from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any

from .engineering import mission_engineering_is_stale, quality_contract_blockers
from .errors import KodaError
from .evidence import changed_paths, worktree_fingerprint
from .models import AgentName, ExecutionStatus, Mission, Outcome
from .workspace import validate_mission_worktree

BASELINE_AGENTS = {AgentName.ENGINEER, AgentName.TESTER, AgentName.REVIEWER}


def required_agents(mission: Mission) -> set[AgentName]:
    return BASELINE_AGENTS | {assignment.agent for assignment in mission.assignments}


def next_agent(mission: Mission) -> AgentName | None:
    if next_product_question(mission) is not None:
        return None
    if mission.resume_agent is not None:
        return mission.resume_agent
    for assignment in mission.assignments:
        stage = mission.stages.get(assignment.agent.value)
        if stage is None or stage.outcome is not Outcome.PASSED:
            return assignment.agent
    return None


def next_product_question(mission: Mission) -> str | None:
    answered = {item.question for item in mission.answers}
    return next(
        (
            question
            for question in mission.understanding.product_questions
            if question not in answered
        ),
        None,
    )


def ready_to_finish(mission: Mission, repository: Path) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    pending_question = next_product_question(mission)
    if pending_question is not None:
        reasons.append(f"Product clarification is required: {pending_question}")
    worktree: Path | None = None
    try:
        worktree = validate_mission_worktree(mission, repository)
    except KodaError as exc:
        reasons.append(str(exc))
    incomplete = sorted(
        agent.value
        for agent in required_agents(mission)
        if mission.stages.get(agent.value) is None
        or mission.stages[agent.value].outcome is not Outcome.PASSED
    )
    if incomplete:
        reasons.append(f"Required stages are incomplete: {', '.join(incomplete)}")
    if worktree is not None:
        if mission_engineering_is_stale(
            mission,
            worktree,
            changed_paths=changed_paths(worktree),
        ):
            reasons.append(
                "The engineering profile and quality contract are stale for the current worktree."
            )
        else:
            reasons.extend(quality_contract_blockers(mission.quality_contract))
    if not mission.checks or any(check.outcome != "passed" for check in mission.checks):
        reasons.append("The latest deterministic quality gate is not passing.")
    elif worktree is not None and mission.check_fingerprint != worktree_fingerprint(worktree):
        reasons.append("The deterministic quality evidence is stale for the current worktree.")
    return not reasons, reasons


def mission_status(mission: Mission, repository: Path) -> dict[str, Any]:
    ready, blockers = ready_to_finish(mission, repository)
    role = next_agent(mission)
    effective_status = mission.execution_status
    if not ready and effective_status is ExecutionStatus.READY_TO_FINISH:
        effective_status = ExecutionStatus.PENDING
    engineering_stale = any("engineering profile" in blocker for blocker in blockers)
    return {
        "schema_version": mission.schema_version,
        "mission_id": mission.mission_id,
        "request": mission.request,
        "execution_status": effective_status.value,
        "ready_to_finish": ready,
        "readiness_blockers": blockers,
        "next_agent": role.value if role else None,
        "assignments": [assignment.agent.value for assignment in mission.assignments],
        "stages": {
            key: {
                "outcome": stage.outcome.value,
                "note": stage.note,
                "recorded_at": stage.recorded_at,
            }
            for key, stage in mission.stages.items()
        },
        "checks": [record.__dict__ for record in mission.checks],
        "baseline_checks": [record.__dict__ for record in mission.baseline_checks],
        "remediation_count": mission.remediation_count,
        "waiting_question": next_product_question(mission),
        "pending_findings": mission.pending_findings,
        "worktree": mission.worktree,
        "branch": mission.branch,
        "engineering_profile": (
            asdict(mission.engineering_profile) if mission.engineering_profile is not None else None
        ),
        "quality_contract": (
            asdict(mission.quality_contract) if mission.quality_contract is not None else None
        ),
        "engineering_stale": engineering_stale,
    }


def synchronize_ready_status(mission: Mission, repository: Path) -> None:
    ready, _ = ready_to_finish(mission, repository)
    if ready:
        mission.execution_status = ExecutionStatus.READY_TO_FINISH
        mission.resume_agent = None
