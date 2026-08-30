from __future__ import annotations

import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest

from koda_code.copilot import CopilotCall, CopilotCapability
from koda_code.execution import MAX_REMEDIATION_ROUNDS, run_mission
from koda_code.models import (
    AgentName,
    AgentResult,
    AgentResultOutcome,
    ExecutionStatus,
    Mission,
    MissionAnswer,
)
from koda_code.store import MissionStore
from koda_code.workflow import begin_mission

Runner = Callable[[AgentName, str, Path, CopilotCapability], CopilotCall]


def _git(repository: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repository, check=True, capture_output=True)


def _mission(
    git_repo: Path,
    request: str = "Improve project error handling",
    *,
    resolve_questions: bool = True,
    passing_quality: bool = True,
) -> Mission:
    quality_argv = (
        '["python", "--version"]' if passing_quality else '["python", "-c", "raise SystemExit(1)"]'
    )
    (git_repo / "koda-code.toml").write_text(
        f'[[quality.checks]]\nname="python"\nargv={quality_argv}\ntimeout_seconds=10\n',
        encoding="utf-8",
    )
    _git(git_repo, "add", "koda-code.toml")
    _git(git_repo, "commit", "-m", "Add quality contract")
    mission = begin_mission(request, git_repo, prepare_worktree=True)
    if resolve_questions:
        mission.answers = [
            MissionAnswer(question, "Use the existing local project behavior.")
            for question in mission.understanding.product_questions
        ]
        MissionStore(git_repo).save(mission)
    return mission


def _call(
    outcome: AgentResultOutcome = AgentResultOutcome.PASS,
    *,
    summary: str = "Role passed.",
    findings: tuple[str, ...] = (),
    question: str | None = None,
    unclear: bool = False,
) -> CopilotCall:
    return CopilotCall(
        "completed",
        0,
        False,
        True,
        "",
        AgentResult(outcome, summary, findings, question, unclear),
    )


def _failure(kind: str = "process_failed") -> CopilotCall:
    return CopilotCall(kind, 1, False, True, "provider failed", None)


def _passing_runner(roles: list[AgentName]) -> Runner:
    def run(
        role: AgentName, prompt: str, worktree: Path, capability: CopilotCapability
    ) -> CopilotCall:
        roles.append(role)
        if role is AgentName.ENGINEER:
            (worktree / "app.py").write_text(
                "def value() -> int:\n    return 1\n", encoding="utf-8"
            )
        return _call()

    return run


def _run(git_repo: Path, mission: Mission, runner: Runner) -> object:
    return run_mission(
        mission,
        git_repo,
        MissionStore(git_repo),
        runner=runner,
        capability=CopilotCapability("fake", "1", True),
    )


def test_happy_path_isolated_and_ready_without_delivery(git_repo: Path) -> None:
    mission = _mission(git_repo)
    roles: list[AgentName] = []
    report = _run(git_repo, mission, _passing_runner(roles))
    assert report.status is ExecutionStatus.READY_TO_FINISH  # type: ignore[attr-defined]
    assert roles == [AgentName.ENGINEER, AgentName.TESTER, AgentName.REVIEWER]
    assert not (git_repo / "app.py").exists()
    assert (Path(mission.worktree or "") / "app.py").is_file()
    assert mission.delivered_commit is None
    assert mission.checks and all(item.outcome == "passed" for item in mission.checks)
    assert (
        "app.py"
        not in subprocess.run(
            ["git", "status", "--short"], cwd=git_repo, text=True, capture_output=True, check=True
        ).stdout
    )


def test_prompt_does_not_expose_canonical_or_unrelated_paths(git_repo: Path) -> None:
    mission = _mission(git_repo)
    prompts: list[str] = []

    def runner(
        role: AgentName, prompt: str, worktree: Path, capability: CopilotCapability
    ) -> CopilotCall:
        prompts.append(prompt)
        if role is AgentName.ENGINEER:
            (worktree / "app.py").write_text("value = 1\n", encoding="utf-8")
        return _call()

    _run(git_repo, mission, runner)
    assert prompts
    assert all(str(git_repo) not in prompt for prompt in prompts)
    assert all(str(git_repo.parent / "unrelated") not in prompt for prompt in prompts)


def test_ui_role_is_conditional_and_precedes_testing(git_repo: Path) -> None:
    mission = _mission(git_repo, "Improve the settings page layout")
    roles: list[AgentName] = []
    report = _run(git_repo, mission, _passing_runner(roles))
    assert report.status is ExecutionStatus.READY_TO_FINISH  # type: ignore[attr-defined]
    assert roles == [
        AgentName.ENGINEER,
        AgentName.UI_UX,
        AgentName.TESTER,
        AgentName.REVIEWER,
    ]


def test_tester_findings_trigger_engineer_repair_and_retest(git_repo: Path) -> None:
    mission = _mission(git_repo)
    roles: list[AgentName] = []
    tester_calls = 0

    def runner(
        role: AgentName, prompt: str, worktree: Path, capability: CopilotCapability
    ) -> CopilotCall:
        nonlocal tester_calls
        roles.append(role)
        if role is AgentName.ENGINEER:
            with (worktree / "app.py").open("a", encoding="utf-8") as handle:
                handle.write("# implementation\n")
        if role is AgentName.TESTER:
            tester_calls += 1
            if tester_calls == 1:
                return _call(
                    AgentResultOutcome.CHANGES_REQUIRED,
                    findings=("Empty input is not handled.",),
                )
        return _call()

    report = _run(git_repo, mission, runner)
    assert report.status is ExecutionStatus.READY_TO_FINISH  # type: ignore[attr-defined]
    assert roles == [
        AgentName.ENGINEER,
        AgentName.TESTER,
        AgentName.ENGINEER,
        AgentName.TESTER,
        AgentName.REVIEWER,
    ]
    assert mission.remediation_count == 1


def test_unclear_failure_routes_debugger_before_engineer_repair(git_repo: Path) -> None:
    mission = _mission(git_repo)
    roles: list[AgentName] = []
    tester_calls = 0

    def runner(
        role: AgentName, prompt: str, worktree: Path, capability: CopilotCapability
    ) -> CopilotCall:
        nonlocal tester_calls
        roles.append(role)
        if role is AgentName.ENGINEER:
            with (worktree / "app.py").open("a", encoding="utf-8") as handle:
                handle.write("# implementation\n")
        if role is AgentName.TESTER:
            tester_calls += 1
            if tester_calls == 1:
                return _call(
                    AgentResultOutcome.CHANGES_REQUIRED,
                    findings=("Intermittent failure has no clear cause.",),
                    unclear=True,
                )
        if role is AgentName.DEBUGGER:
            return _call(findings=("State leaks between calls.",), summary="Root cause isolated.")
        return _call()

    report = _run(git_repo, mission, runner)
    assert report.status is ExecutionStatus.READY_TO_FINISH  # type: ignore[attr-defined]
    assert roles == [
        AgentName.ENGINEER,
        AgentName.TESTER,
        AgentName.DEBUGGER,
        AgentName.ENGINEER,
        AgentName.TESTER,
        AgentName.REVIEWER,
    ]


def test_remediation_budget_stops_infinite_loop(git_repo: Path) -> None:
    mission = _mission(git_repo)

    def runner(
        role: AgentName, prompt: str, worktree: Path, capability: CopilotCapability
    ) -> CopilotCall:
        if role is AgentName.ENGINEER:
            with (worktree / "app.py").open("a", encoding="utf-8") as handle:
                handle.write("# attempt\n")
            return _call()
        if role is AgentName.TESTER:
            return _call(
                AgentResultOutcome.CHANGES_REQUIRED,
                findings=("Behavior remains incorrect.",),
            )
        return _call()

    report = _run(git_repo, mission, runner)
    assert report.status is ExecutionStatus.BLOCKED  # type: ignore[attr-defined]
    assert mission.remediation_count == MAX_REMEDIATION_ROUNDS
    assert "2 remediation rounds" in report.message  # type: ignore[attr-defined]


def test_validation_failure_after_agent_pass_is_authoritative(git_repo: Path) -> None:
    mission = _mission(git_repo, passing_quality=False)
    roles: list[AgentName] = []
    report = _run(git_repo, mission, _passing_runner(roles))
    assert report.status is ExecutionStatus.BLOCKED  # type: ignore[attr-defined]
    assert mission.remediation_count == MAX_REMEDIATION_ROUNDS
    assert AgentName.REVIEWER not in roles
    assert mission.checks and mission.checks[0].outcome == "failed"


def test_provider_failure_resumes_at_failed_reviewer(git_repo: Path) -> None:
    mission = _mission(git_repo)
    first_roles: list[AgentName] = []

    def first(
        role: AgentName, prompt: str, worktree: Path, capability: CopilotCapability
    ) -> CopilotCall:
        first_roles.append(role)
        if role is AgentName.ENGINEER:
            (worktree / "app.py").write_text("value = 1\n", encoding="utf-8")
        return _failure("quota_limited") if role is AgentName.REVIEWER else _call()

    first_report = _run(git_repo, mission, first)
    assert first_report.status is ExecutionStatus.BLOCKED  # type: ignore[attr-defined]
    assert mission.resume_agent is AgentName.REVIEWER
    second_roles: list[AgentName] = []
    second_report = _run(git_repo, mission, _passing_runner(second_roles))
    assert second_report.status is ExecutionStatus.READY_TO_FINISH  # type: ignore[attr-defined]
    assert second_roles == [AgentName.REVIEWER]


def test_source_change_after_tester_pass_invalidates_downstream_evidence(git_repo: Path) -> None:
    mission = _mission(git_repo)

    def first(
        role: AgentName, prompt: str, worktree: Path, capability: CopilotCapability
    ) -> CopilotCall:
        if role is AgentName.ENGINEER:
            (worktree / "app.py").write_text("value = 1\n", encoding="utf-8")
        return _failure("quota_limited") if role is AgentName.REVIEWER else _call()

    first_report = _run(git_repo, mission, first)
    assert first_report.status is ExecutionStatus.BLOCKED  # type: ignore[attr-defined]
    (Path(mission.worktree or "") / "app.py").write_text("value = 2\n", encoding="utf-8")
    resumed_roles: list[AgentName] = []
    second_report = _run(git_repo, mission, _passing_runner(resumed_roles))
    assert second_report.status is ExecutionStatus.READY_TO_FINISH  # type: ignore[attr-defined]
    assert resumed_roles == [AgentName.TESTER, AgentName.REVIEWER]


def test_malformed_result_does_not_advance_stage(git_repo: Path) -> None:
    mission = _mission(git_repo)
    report = _run(git_repo, mission, lambda *args: _failure("invalid_result"))
    assert report.status is ExecutionStatus.BLOCKED  # type: ignore[attr-defined]
    assert "engineer" not in mission.stages
    assert mission.executions[-1].process_outcome == "invalid_result"


def test_structured_output_is_redacted_before_persistence(git_repo: Path) -> None:
    mission = _mission(git_repo)
    fake_assignment = "password" + "=not-safe-secret"

    def runner(
        role: AgentName, prompt: str, worktree: Path, capability: CopilotCapability
    ) -> CopilotCall:
        if role is AgentName.ENGINEER:
            (worktree / "app.py").write_text("value = 1\n", encoding="utf-8")
        return _call(summary=f"Handled {fake_assignment}")

    _run(git_repo, mission, runner)
    loaded = MissionStore(git_repo).load(mission.mission_id)
    assert all("not-safe-secret" not in item.summary for item in loaded.executions)
    assert all("[REDACTED]" in item.summary for item in loaded.executions)


def test_read_only_reviewer_modification_is_rejected(git_repo: Path) -> None:
    mission = _mission(git_repo)

    def runner(
        role: AgentName, prompt: str, worktree: Path, capability: CopilotCapability
    ) -> CopilotCall:
        if role is AgentName.ENGINEER:
            (worktree / "app.py").write_text("value = 1\n", encoding="utf-8")
        if role is AgentName.REVIEWER:
            (worktree / "app.py").write_text("value = 2\n", encoding="utf-8")
        return _call()

    report = _run(git_repo, mission, runner)
    assert report.status is ExecutionStatus.BLOCKED  # type: ignore[attr-defined]
    assert "read-only reviewer changed" in report.message  # type: ignore[attr-defined]
    assert "reviewer" not in mission.stages


def test_git_history_change_is_rejected(git_repo: Path) -> None:
    mission = _mission(git_repo)

    def runner(
        role: AgentName, prompt: str, worktree: Path, capability: CopilotCapability
    ) -> CopilotCall:
        if role is AgentName.ENGINEER:
            (worktree / "app.py").write_text("value = 1\n", encoding="utf-8")
            _git(worktree, "add", "app.py")
            _git(worktree, "commit", "-m", "Agent must not commit")
        return _call()

    report = _run(git_repo, mission, runner)
    assert report.status is ExecutionStatus.BLOCKED  # type: ignore[attr-defined]
    assert "Git history" in report.message  # type: ignore[attr-defined]
    assert "engineer" not in mission.stages


def test_git_staging_change_is_rejected(git_repo: Path) -> None:
    mission = _mission(git_repo)

    def runner(
        role: AgentName, prompt: str, worktree: Path, capability: CopilotCapability
    ) -> CopilotCall:
        if role is AgentName.ENGINEER:
            (worktree / "app.py").write_text("value = 1\n", encoding="utf-8")
            _git(worktree, "add", "app.py")
        return _call()

    report = _run(git_repo, mission, runner)
    assert report.status is ExecutionStatus.BLOCKED  # type: ignore[attr-defined]
    assert "staging area" in report.message  # type: ignore[attr-defined]
    assert "engineer" not in mission.stages


def test_change_to_stable_checkout_is_rejected(git_repo: Path) -> None:
    mission = _mission(git_repo)

    def runner(
        role: AgentName, prompt: str, worktree: Path, capability: CopilotCapability
    ) -> CopilotCall:
        if role is AgentName.ENGINEER:
            (worktree / "app.py").write_text("value = 1\n", encoding="utf-8")
            (git_repo / "README.md").write_text("# Changed outside worktree\n", encoding="utf-8")
        return _call()

    report = _run(git_repo, mission, runner)
    assert report.status is ExecutionStatus.BLOCKED  # type: ignore[attr-defined]
    assert "stable project checkout" in report.message  # type: ignore[attr-defined]


def test_product_questions_pause_before_provider_and_resume(git_repo: Path) -> None:
    mission = _mission(git_repo, "Build an inventory page", resolve_questions=False)
    roles: list[AgentName] = []
    runner = _passing_runner(roles)
    first = _run(git_repo, mission, runner)
    assert first.status is ExecutionStatus.WAITING_FOR_INPUT  # type: ignore[attr-defined]
    assert roles == []
    second = run_mission(
        mission,
        git_repo,
        MissionStore(git_repo),
        answer="Only on this computer",
        runner=runner,
        capability=CopilotCapability("fake", "1", True),
    )
    assert second.status is ExecutionStatus.WAITING_FOR_INPUT
    final = run_mission(
        mission,
        git_repo,
        MissionStore(git_repo),
        answer="Only me",
        runner=runner,
        capability=CopilotCapability("fake", "1", True),
    )
    assert final.status is ExecutionStatus.READY_TO_FINISH
    loaded = MissionStore(git_repo).load(mission.mission_id)
    assert len(loaded.answers) == 2


def test_missing_copilot_does_not_start_or_advance(
    monkeypatch: pytest.MonkeyPatch, git_repo: Path
) -> None:
    mission = _mission(git_repo)
    monkeypatch.setattr("koda_code.execution.detect_copilot", lambda: None)
    report = run_mission(mission, git_repo, MissionStore(git_repo))
    assert report.status is ExecutionStatus.BLOCKED
    assert report.calls == 0
    assert mission.stages == {}
    assert not (Path(mission.worktree or "") / "app.py").exists()
