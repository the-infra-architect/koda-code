from __future__ import annotations

from collections.abc import Callable
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .copilot import (
    CopilotCall,
    CopilotCapability,
    detect_copilot,
    run_copilot,
    sanitize_output,
)
from .errors import KodaError
from .evidence import (
    changed_paths as _changed_paths,
)
from .evidence import (
    index_status as _index_status,
)
from .evidence import (
    repository_diff as _repository_diff,
)
from .evidence import (
    validation_evidence as _validation_evidence,
)
from .evidence import (
    worktree_fingerprint as _worktree_fingerprint,
)
from .models import (
    AgentName,
    AgentResultOutcome,
    ExecutionAttempt,
    ExecutionStatus,
    Mission,
    MissionAnswer,
    Outcome,
    StageRecord,
    utc_now,
)
from .policy import MAX_REMEDIATION_ROUNDS
from .prompts import render_execution_prompt
from .quality import load_checks, run_checks
from .repository import git
from .routing import add_debugger
from .store import MissionStore
from .workspace import validate_mission_worktree

MAX_AUTONOMOUS_STEPS = 20

Progress = Callable[[str, AgentName | None], None]
Runner = Callable[[AgentName, str, Path, CopilotCapability], CopilotCall]


@dataclass(frozen=True)
class RunReport:
    status: ExecutionStatus
    message: str
    role: AgentName | None
    calls: int
    worktree: str
    sandboxed: bool | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def run_mission(
    mission: Mission,
    repository: Path,
    store: MissionStore,
    *,
    answer: str | None = None,
    runner: Runner = run_copilot,
    capability: CopilotCapability | None = None,
    progress: Progress | None = None,
) -> RunReport:
    worktree = validate_mission_worktree(mission, repository)
    if _invalidate_stale_evidence(mission, worktree):
        store.save(mission)
    if mission.execution_status is ExecutionStatus.READY_TO_FINISH:
        return _report(mission, "Mission is already verified and ready to finish.", None, 0, None)

    waiting = mission.waiting_question or _next_product_question(mission)
    if waiting:
        if answer is None:
            mission.waiting_question = waiting
            mission.execution_status = ExecutionStatus.WAITING_FOR_INPUT
            store.save(mission)
            return _report(mission, waiting, mission.resume_agent, 0, None)
        cleaned = sanitize_output(" ".join(answer.split()))
        if not cleaned:
            raise KodaError("The supplied answer is empty.")
        mission.answers.append(MissionAnswer(waiting, cleaned))
        mission.waiting_question = None
        store.save(mission)
        next_question = _next_product_question(mission)
        if next_question:
            mission.waiting_question = next_question
            mission.execution_status = ExecutionStatus.WAITING_FOR_INPUT
            store.save(mission)
            return _report(mission, next_question, mission.resume_agent, 0, None)
    elif answer is not None:
        raise KodaError("There is no pending product question to answer.")

    selected_capability = capability or detect_copilot()
    if selected_capability is None:
        mission.execution_status = ExecutionStatus.BLOCKED
        store.save(mission)
        return _report(
            mission,
            "Koda prepared the engineering mission, but automatic coding could not start because "
            "GitHub Copilot CLI is not available in this environment. Your project was not "
            "modified.",
            mission.resume_agent or _next_role(mission),
            0,
            None,
        )
    if not selected_capability.compatible:
        mission.execution_status = ExecutionStatus.BLOCKED
        store.save(mission)
        return _report(
            mission,
            selected_capability.diagnostic
            or "The installed GitHub Copilot CLI is incompatible with Koda's safe execution mode.",
            mission.resume_agent or _next_role(mission),
            0,
            selected_capability.sandbox_supported,
        )

    mission.execution_status = ExecutionStatus.RUNNING
    store.save(mission)
    calls = 0
    for _ in range(MAX_AUTONOMOUS_STEPS):
        role = mission.resume_agent or _next_role(mission)
        if role is None:
            if not mission.checks or any(check.outcome != "passed" for check in mission.checks):
                return _blocked(
                    mission,
                    store,
                    "All roles passed, but the deterministic quality gate is not passing.",
                    None,
                    calls,
                    selected_capability.sandbox_supported,
                )
            mission.execution_status = ExecutionStatus.READY_TO_FINISH
            mission.waiting_question = None
            mission.resume_agent = None
            store.save(mission)
            isolation_note = (
                ""
                if selected_capability.sandbox_supported
                else " Local Copilot sandboxing is unsupported; explicit role permissions and "
                "worktree containment were used instead."
            )
            return _report(
                mission,
                "VERIFIED / READY TO FINISH. Koda has not committed, pushed, or opened a pull "
                f"request.{isolation_note}",
                None,
                calls,
                selected_capability.sandbox_supported,
            )

        validate_mission_worktree(mission, repository)
        canonical_before = _worktree_fingerprint(repository, exclude_state=True)
        worktree_before = _worktree_fingerprint(worktree)
        head_before = git(worktree, "rev-parse", "HEAD").stdout.strip()
        index_before = _index_status(worktree)
        if index_before:
            return _blocked(
                mission,
                store,
                "The mission worktree contains staged changes. Koda will not launch an agent "
                "with pre-staged files.",
                role,
                calls,
                selected_capability.sandbox_supported,
            )
        changed_before = _changed_paths(worktree)
        prompt = render_execution_prompt(
            mission,
            role,
            repository_diff=_repository_diff(worktree),
            changed_paths=changed_before,
            validation_evidence=_validation_evidence(mission),
        )
        attempt = ExecutionAttempt(
            role=role,
            attempt=1 + sum(item.role is role for item in mission.executions),
            started_at=utc_now(),
            process_outcome="running",
            sandboxed=selected_capability.sandbox_supported,
        )
        mission.executions.append(attempt)
        mission.resume_agent = role
        store.save(mission)
        if progress:
            progress("starting", role)

        call = runner(role, prompt, worktree, selected_capability)
        calls += 1
        attempt.finished_at = utc_now()
        attempt.process_outcome = call.process_outcome
        attempt.exit_code = call.exit_code
        attempt.timed_out = call.timed_out
        attempt.sandboxed = call.sandboxed
        attempt.diagnostic = sanitize_output(call.diagnostic)
        attempt.changed_paths = list(_changed_paths(worktree))
        attempt.repository_fingerprint = _worktree_fingerprint(worktree)

        containment_error = _containment_error(
            mission,
            repository,
            worktree,
            role,
            canonical_before=canonical_before,
            worktree_before=worktree_before,
            head_before=head_before,
            index_before=index_before,
        )
        if containment_error:
            attempt.process_outcome = "containment_failed"
            attempt.diagnostic = containment_error
            return _blocked(
                mission,
                store,
                containment_error,
                role,
                calls,
                call.sandboxed,
            )
        if call.result is None:
            return _blocked(
                mission,
                store,
                _provider_failure_message(call),
                role,
                calls,
                call.sandboxed,
            )

        result = call.result
        summary = sanitize_output(result.summary)
        findings = tuple(sanitize_output(item) for item in result.findings)
        question = sanitize_output(result.question) if result.question else None
        attempt.summary = summary
        attempt.findings = list(findings)
        attempt.question = question
        if result.outcome is AgentResultOutcome.NEEDS_INPUT:
            mission.waiting_question = question
            mission.execution_status = ExecutionStatus.WAITING_FOR_INPUT
            store.save(mission)
            return _report(
                mission,
                question or summary,
                role,
                calls,
                call.sandboxed,
            )
        if result.outcome is AgentResultOutcome.BLOCKED:
            mission.stages[role.value] = StageRecord(Outcome.BLOCKED, summary)
            return _blocked(mission, store, summary, role, calls, call.sandboxed)
        if result.outcome is AgentResultOutcome.CHANGES_REQUIRED:
            if role is AgentName.ENGINEER:
                mission.stages[role.value] = StageRecord(Outcome.NEEDS_WORK, summary)
                return _blocked(mission, store, summary, role, calls, call.sandboxed)
            if not _schedule_remediation(mission, findings):
                return _blocked(
                    mission,
                    store,
                    _remediation_exhausted_message(mission),
                    role,
                    calls,
                    call.sandboxed,
                )
            mission.stages[role.value] = StageRecord(Outcome.NEEDS_WORK, summary)
            if role is AgentName.TESTER and result.unclear_failure:
                mission.assignments = add_debugger(mission.assignments, unclear_failure=True)
                mission.resume_agent = AgentName.DEBUGGER
            else:
                mission.resume_agent = AgentName.ENGINEER
            store.save(mission)
            if progress:
                progress("remediating", mission.resume_agent)
            continue

        if role is AgentName.ENGINEER and not attempt.changed_paths:
            attempt.process_outcome = "invalid_result"
            attempt.diagnostic = "Engineer reported pass, but Git contains no mission changes."
            return _blocked(
                mission,
                store,
                attempt.diagnostic,
                role,
                calls,
                call.sandboxed,
            )

        mission.stages[role.value] = StageRecord(Outcome.PASSED, summary)
        mission.resume_agent = None
        if role is AgentName.ENGINEER:
            mission.pending_findings = []
        if role is AgentName.DEBUGGER:
            mission.pending_findings = list(findings) or [summary]
            mission.resume_agent = AgentName.ENGINEER
        if role is AgentName.TESTER:
            try:
                mission.checks = run_checks(worktree, load_checks(worktree))
                mission.check_fingerprint = _worktree_fingerprint(worktree)
            except KodaError as exc:
                return _blocked(mission, store, str(exc), role, calls, call.sandboxed)
            if not mission.checks or any(check.outcome != "passed" for check in mission.checks):
                failure = _validation_evidence(mission)
                if not _schedule_remediation(mission, (failure,)):
                    return _blocked(
                        mission,
                        store,
                        _remediation_exhausted_message(mission),
                        role,
                        calls,
                        call.sandboxed,
                    )
                mission.resume_agent = AgentName.ENGINEER
                store.save(mission)
                if progress:
                    progress("validation_failed", AgentName.ENGINEER)
                continue
        store.save(mission)
        if progress:
            progress("passed", role)

    return _blocked(
        mission,
        store,
        "Koda stopped after reaching the autonomous step safety limit.",
        mission.resume_agent,
        calls,
        selected_capability.sandbox_supported,
    )


def _next_product_question(mission: Mission) -> str | None:
    answered = {item.question for item in mission.answers}
    return next(
        (
            question
            for question in mission.understanding.product_questions
            if question not in answered
        ),
        None,
    )


def _next_role(mission: Mission) -> AgentName | None:
    for assignment in mission.assignments:
        stage = mission.stages.get(assignment.agent.value)
        if stage is None or stage.outcome is not Outcome.PASSED:
            return assignment.agent
    return None


def _invalidate_stale_evidence(mission: Mission, worktree: Path) -> bool:
    mutable = {AgentName.ENGINEER, AgentName.UI_UX, AgentName.TESTER}
    latest_accepted: ExecutionAttempt | None = None
    for assignment in reversed(mission.assignments):
        stage = mission.stages.get(assignment.agent.value)
        if assignment.agent not in mutable or stage is None or stage.outcome is not Outcome.PASSED:
            continue
        latest_accepted = next(
            (
                attempt
                for attempt in reversed(mission.executions)
                if attempt.role is assignment.agent
                and attempt.process_outcome == "completed"
                and attempt.repository_fingerprint
            ),
            None,
        )
        if latest_accepted:
            break
    if latest_accepted is None:
        return False
    if latest_accepted.repository_fingerprint == _worktree_fingerprint(worktree):
        return False
    for assignment in mission.assignments:
        if assignment.agent not in {AgentName.ENGINEER, AgentName.DEBUGGER}:
            mission.stages.pop(assignment.agent.value, None)
    mission.checks = []
    mission.check_fingerprint = None
    mission.resume_agent = None
    mission.execution_status = ExecutionStatus.PENDING
    return True


def _schedule_remediation(mission: Mission, findings: tuple[str, ...]) -> bool:
    if mission.remediation_count >= MAX_REMEDIATION_ROUNDS:
        mission.pending_findings = list(findings)
        return False
    mission.remediation_count += 1
    mission.pending_findings = [sanitize_output(item) for item in findings]
    mission.checks = []
    mission.check_fingerprint = None
    for assignment in mission.assignments:
        if assignment.agent is not AgentName.DEBUGGER:
            mission.stages.pop(assignment.agent.value, None)
    return True


def _containment_error(
    mission: Mission,
    repository: Path,
    worktree: Path,
    role: AgentName,
    *,
    canonical_before: str,
    worktree_before: str,
    head_before: str,
    index_before: str,
) -> str | None:
    try:
        validate_mission_worktree(mission, repository)
    except KodaError as exc:
        return str(exc)
    if _worktree_fingerprint(repository, exclude_state=True) != canonical_before:
        return "Copilot changed the stable project checkout; Koda refused to advance the mission."
    head_after = git(worktree, "rev-parse", "HEAD").stdout.strip()
    if head_after != head_before:
        return "Copilot changed Git history; Koda refused to advance the mission."
    if _index_status(worktree) != index_before:
        return "Copilot changed the Git staging area; Koda refused to advance the mission."
    if (
        role in {AgentName.REVIEWER, AgentName.DEBUGGER}
        and _worktree_fingerprint(worktree) != worktree_before
    ):
        return f"The read-only {role.value} changed repository files; Koda refused the result."
    return None


def _provider_failure_message(call: CopilotCall) -> str:
    lead = {
        "authentication_failed": "GitHub Copilot CLI is not authenticated.",
        "quota_limited": "GitHub Copilot quota or usage limits stopped this role.",
        "timed_out": "GitHub Copilot CLI timed out.",
        "invalid_result": "GitHub Copilot returned an invalid structured result.",
        "unavailable": "GitHub Copilot CLI became unavailable.",
    }.get(call.process_outcome, "GitHub Copilot CLI could not complete this role.")
    return f"{lead} {call.diagnostic}".strip()


def _remediation_exhausted_message(mission: Mission) -> str:
    details = "; ".join(mission.pending_findings) or "The mission still has unresolved findings."
    return (
        f"Koda stopped after {MAX_REMEDIATION_ROUNDS} remediation rounds. "
        f"Remaining evidence: {details}"
    )


def _blocked(
    mission: Mission,
    store: MissionStore,
    message: str,
    role: AgentName | None,
    calls: int,
    sandboxed: bool | None,
) -> RunReport:
    mission.execution_status = ExecutionStatus.BLOCKED
    store.save(mission)
    return _report(mission, sanitize_output(message), role, calls, sandboxed)


def _report(
    mission: Mission,
    message: str,
    role: AgentName | None,
    calls: int,
    sandboxed: bool | None,
) -> RunReport:
    return RunReport(
        status=mission.execution_status,
        message=message,
        role=role,
        calls=calls,
        worktree=mission.worktree or "",
        sandboxed=sandboxed,
    )
