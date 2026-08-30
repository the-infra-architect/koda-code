from __future__ import annotations

from pathlib import Path

from .copilot import sanitize_output
from .errors import KodaError
from .evidence import mission_evidence
from .models import AgentName, ExecutionStatus, Mission, Outcome, StageRecord
from .policy import MAX_REMEDIATION_ROUNDS
from .routing import add_debugger
from .status import next_agent, next_product_question, synchronize_ready_status
from .store import MissionStore

READ_ONLY_AGENTS = {AgentName.REVIEWER, AgentName.DEBUGGER}


def record_verified_progress(
    mission: Mission,
    repository: Path,
    store: MissionStore,
    *,
    agent: AgentName,
    outcome: Outcome,
    note: str,
    evidence_fingerprint: str | None,
    unclear_failure: bool,
) -> None:
    assigned = {item.agent for item in mission.assignments}
    if agent not in assigned:
        raise KodaError(f"Agent is not assigned to this mission: {agent.value}")
    expected = next_agent(mission)
    failed_check_finding = (
        agent is AgentName.TESTER
        and outcome is not Outcome.PASSED
        and bool(mission.checks)
        and any(check.outcome != "passed" for check in mission.checks)
    )
    if agent is not expected and not failed_check_finding:
        label = expected.value if expected else "none"
        raise KodaError(f"Expected next agent is {label}, not {agent.value}.")
    cleaned_note = sanitize_output(" ".join(note.split()))
    if not cleaned_note:
        raise KodaError("A non-empty evidence note is required.")
    if question := next_product_question(mission):
        raise KodaError(f"Answer the pending product question before advancing roles: {question}")
    evidence = mission_evidence(mission, repository)
    if evidence["staged_entries"]:
        raise KodaError("The mission worktree contains staged changes.")
    if agent in READ_ONLY_AGENTS:
        if not evidence_fingerprint:
            raise KodaError(f"The read-only {agent.value} requires a prior evidence fingerprint.")
        if evidence_fingerprint != evidence["fingerprint"]:
            raise KodaError(f"The read-only {agent.value} changed repository files.")

    if outcome is Outcome.PASSED:
        _validate_pass(mission, agent, evidence)
        mission.stages[agent.value] = StageRecord(outcome, cleaned_note)
        mission.execution_status = ExecutionStatus.PENDING
        mission.resume_agent = None
        if agent is AgentName.ENGINEER:
            mission.pending_findings = []
        elif agent is AgentName.DEBUGGER:
            mission.pending_findings = [cleaned_note]
            mission.resume_agent = AgentName.ENGINEER
        else:
            mission.resume_agent = next_agent(mission)
        synchronize_ready_status(mission, repository)
        store.save(mission)
        return

    mission.stages[agent.value] = StageRecord(outcome, cleaned_note)
    if outcome is Outcome.BLOCKED or agent is AgentName.ENGINEER:
        mission.execution_status = ExecutionStatus.BLOCKED
        mission.resume_agent = agent
        store.save(mission)
        return
    if agent is AgentName.DEBUGGER:
        mission.pending_findings = [cleaned_note]
        mission.resume_agent = AgentName.DEBUGGER
        mission.execution_status = ExecutionStatus.BLOCKED
        store.save(mission)
        return
    if mission.remediation_count >= MAX_REMEDIATION_ROUNDS:
        mission.pending_findings = [cleaned_note]
        mission.execution_status = ExecutionStatus.BLOCKED
        mission.resume_agent = agent
        store.save(mission)
        return
    mission.remediation_count += 1
    mission.pending_findings = [cleaned_note]
    mission.checks = []
    mission.check_fingerprint = None
    for assignment in mission.assignments:
        if assignment.agent is not AgentName.DEBUGGER:
            mission.stages.pop(assignment.agent.value, None)
    if agent is AgentName.TESTER and unclear_failure:
        mission.assignments = add_debugger(mission.assignments, unclear_failure=True)
        mission.resume_agent = AgentName.DEBUGGER
    else:
        mission.resume_agent = AgentName.ENGINEER
    mission.execution_status = ExecutionStatus.PENDING
    store.save(mission)


def _validate_pass(mission: Mission, agent: AgentName, evidence: dict[str, object]) -> None:
    if agent in {AgentName.ENGINEER, AgentName.UI_UX} and not evidence["changed_paths"]:
        raise KodaError(f"{agent.value} cannot pass because Git contains no mission changes.")
    if agent in {AgentName.TESTER, AgentName.REVIEWER} and (
        not mission.checks or any(check.outcome != "passed" for check in mission.checks)
    ):
        raise KodaError(f"{agent.value} cannot pass until deterministic checks pass.")
    if agent in {AgentName.TESTER, AgentName.REVIEWER} and (
        not mission.check_fingerprint or mission.check_fingerprint != evidence["fingerprint"]
    ):
        raise KodaError(f"{agent.value} cannot pass because deterministic check evidence is stale.")
