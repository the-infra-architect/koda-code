from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from koda_code.answers import record_answer
from koda_code.cli import main
from koda_code.errors import KodaError
from koda_code.evidence import mission_evidence, worktree_fingerprint
from koda_code.models import AgentName, ExecutionStatus, Mission, Outcome
from koda_code.policy import MAX_REMEDIATION_ROUNDS
from koda_code.progress import record_verified_progress
from koda_code.quality import run_mission_checks
from koda_code.status import mission_status
from koda_code.store import MissionStore
from koda_code.workflow import begin_mission


def _git(repository: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repository, check=True, capture_output=True)


def _mission(git_repo: Path, *, quality: str = '["python", "--version"]') -> Mission:
    (git_repo / "koda-code.toml").write_text(
        f'[[quality.checks]]\nname="contract"\nargv={quality}\ntimeout_seconds=10\n',
        encoding="utf-8",
    )
    _git(git_repo, "add", "koda-code.toml")
    _git(git_repo, "commit", "-m", "Add quality contract")
    return begin_mission("Improve project error handling", git_repo, prepare_worktree=True)


def test_cli_project_status_and_evidence_are_json_contracts(git_repo: Path, capsys: object) -> None:
    mission = _mission(git_repo)
    capsys.readouterr()  # type: ignore[attr-defined]

    assert main(["project", "--repo", str(git_repo), "--json"]) == 0
    project = json.loads(capsys.readouterr().out)  # type: ignore[attr-defined]
    assert project["engine_version"] == "0.4.0"
    assert project["schema_version"] == 4
    assert project["engineering_profile"]["project_mode"] == "existing"
    states = {item["state"] for item in project["quality_contract"]["capabilities"]}
    assert {"existing", "not_applicable", "recommended"} <= states
    assert project["repository"]["root"] == str(git_repo)
    assert project["missions"][0]["mission_id"] == mission.mission_id

    assert main(["status", mission.mission_id, "--repo", str(git_repo), "--json"]) == 0
    status = json.loads(capsys.readouterr().out)  # type: ignore[attr-defined]
    assert status["next_agent"] == "engineer"
    assert status["ready_to_finish"] is False
    assert status["engineering_stale"] is False

    assert main(["evidence", mission.mission_id, "--repo", str(git_repo), "--json"]) == 0
    evidence = json.loads(capsys.readouterr().out)  # type: ignore[attr-defined]
    assert evidence["branch"] == mission.branch
    assert len(evidence["fingerprint"]) == 64


def test_product_questions_must_be_answered_before_roles_advance(
    git_repo: Path, capsys: object
) -> None:
    (git_repo / "koda-code.toml").write_text(
        '[[quality.checks]]\nname="contract"\nargv=["python", "--version"]\n',
        encoding="utf-8",
    )
    _git(git_repo, "add", "koda-code.toml")
    _git(git_repo, "commit", "-m", "Add quality contract")
    mission = begin_mission("Build an inventory page", git_repo, prepare_worktree=True)
    status = mission_status(mission, git_repo)
    assert status["waiting_question"]
    assert status["next_agent"] is None

    assert (
        main(
            [
                "answer",
                mission.mission_id,
                "--repo",
                str(git_repo),
                "--answer",
                "Keep it local on this computer.",
                "--json",
            ]
        )
        == 0
    )
    answered = json.loads(capsys.readouterr().out)  # type: ignore[attr-defined]
    assert answered["waiting_question"]
    assert answered["next_agent"] is None
    assert (
        main(
            [
                "answer",
                mission.mission_id,
                "--repo",
                str(git_repo),
                "--answer",
                "Only the person using this computer needs it.",
                "--json",
            ]
        )
        == 0
    )
    complete = json.loads(capsys.readouterr().out)  # type: ignore[attr-defined]
    assert complete["waiting_question"] is None
    assert complete["next_agent"] == "engineer"

    loaded = MissionStore(git_repo).load(mission.mission_id)
    with pytest.raises(KodaError, match="no pending"):
        record_answer(loaded, git_repo, MissionStore(git_repo), "extra")


def test_product_answers_reject_empty_and_oversized_values(git_repo: Path) -> None:
    mission = begin_mission("Build inventory", git_repo)
    store = MissionStore(git_repo)
    with pytest.raises(KodaError, match="empty"):
        record_answer(mission, git_repo, store, "   ")
    with pytest.raises(KodaError, match="exceeds"):
        record_answer(mission, git_repo, store, "x" * 4001)


def test_verified_progress_requires_git_and_quality_evidence(git_repo: Path) -> None:
    mission = _mission(git_repo)
    store = MissionStore(git_repo)
    worktree = Path(mission.worktree or "")

    assert (
        main(
            [
                "record",
                mission.mission_id,
                "--repo",
                str(git_repo),
                "--agent",
                "engineer",
                "--outcome",
                "passed",
                "--note",
                "No actual change",
                "--verified-evidence",
                "--json",
            ]
        )
        == 2
    )

    (worktree / "app.py").write_text("value = 1\n", encoding="utf-8")
    mission = store.load(mission.mission_id)
    record_verified_progress(
        mission,
        git_repo,
        store,
        agent=AgentName.ENGINEER,
        outcome=Outcome.PASSED,
        note="Implemented app behavior.",
        evidence_fingerprint=None,
        unclear_failure=False,
    )
    assert mission_status(mission, git_repo)["next_agent"] == "tester"

    mission.checks = run_mission_checks(mission, git_repo)
    mission.check_fingerprint = worktree_fingerprint(worktree)
    store.save(mission)
    record_verified_progress(
        mission,
        git_repo,
        store,
        agent=AgentName.TESTER,
        outcome=Outcome.PASSED,
        note="Quality contract passed.",
        evidence_fingerprint=None,
        unclear_failure=False,
    )
    fingerprint = str(mission_evidence(mission, git_repo)["fingerprint"])
    record_verified_progress(
        mission,
        git_repo,
        store,
        agent=AgentName.REVIEWER,
        outcome=Outcome.PASSED,
        note="No blocking findings.",
        evidence_fingerprint=fingerprint,
        unclear_failure=False,
    )
    assert mission.execution_status is ExecutionStatus.READY_TO_FINISH
    assert mission_status(mission, git_repo)["ready_to_finish"] is True


def test_changed_files_make_passing_check_evidence_stale(git_repo: Path) -> None:
    mission = _mission(git_repo)
    store = MissionStore(git_repo)
    worktree = Path(mission.worktree or "")
    (worktree / "app.py").write_text("value = 1\n", encoding="utf-8")
    record_verified_progress(
        mission,
        git_repo,
        store,
        agent=AgentName.ENGINEER,
        outcome=Outcome.PASSED,
        note="Implementation exists.",
        evidence_fingerprint=None,
        unclear_failure=False,
    )
    mission.checks = run_mission_checks(mission, git_repo)
    mission.check_fingerprint = worktree_fingerprint(worktree)
    store.save(mission)
    (worktree / "app.py").write_text("value = 2\n", encoding="utf-8")

    with pytest.raises(KodaError, match="check evidence is stale"):
        record_verified_progress(
            mission,
            git_repo,
            store,
            agent=AgentName.TESTER,
            outcome=Outcome.PASSED,
            note="Checks passed before a later edit.",
            evidence_fingerprint=None,
            unclear_failure=False,
        )
    assert mission_status(mission, git_repo)["ready_to_finish"] is False


def test_read_only_role_cannot_record_stale_evidence(git_repo: Path) -> None:
    mission = _mission(git_repo)
    store = MissionStore(git_repo)
    worktree = Path(mission.worktree or "")
    (worktree / "app.py").write_text("value = 1\n", encoding="utf-8")
    record_verified_progress(
        mission,
        git_repo,
        store,
        agent=AgentName.ENGINEER,
        outcome=Outcome.PASSED,
        note="Implementation exists.",
        evidence_fingerprint=None,
        unclear_failure=False,
    )
    mission.checks = run_mission_checks(mission, git_repo)
    mission.check_fingerprint = worktree_fingerprint(worktree)
    store.save(mission)
    record_verified_progress(
        mission,
        git_repo,
        store,
        agent=AgentName.TESTER,
        outcome=Outcome.PASSED,
        note="Checks passed.",
        evidence_fingerprint=None,
        unclear_failure=False,
    )
    fingerprint = str(mission_evidence(mission, git_repo)["fingerprint"])
    (worktree / "app.py").write_text("value = 2\n", encoding="utf-8")

    result = main(
        [
            "record",
            mission.mission_id,
            "--repo",
            str(git_repo),
            "--agent",
            "reviewer",
            "--outcome",
            "needs_work",
            "--note",
            "Repository changed during review.",
            "--verified-evidence",
            "--evidence-fingerprint",
            fingerprint,
        ]
    )
    assert result == 2
    assert "reviewer" not in store.load(mission.mission_id).stages


def test_verified_findings_route_debugger_and_enforce_remediation_budget(git_repo: Path) -> None:
    mission = _mission(git_repo)
    store = MissionStore(git_repo)
    worktree = Path(mission.worktree or "")
    (worktree / "app.py").write_text("value = 1\n", encoding="utf-8")
    record_verified_progress(
        mission,
        git_repo,
        store,
        agent=AgentName.ENGINEER,
        outcome=Outcome.PASSED,
        note="Implementation exists.",
        evidence_fingerprint=None,
        unclear_failure=False,
    )
    record_verified_progress(
        mission,
        git_repo,
        store,
        agent=AgentName.TESTER,
        outcome=Outcome.NEEDS_WORK,
        note="Reproducible failure with unclear cause.",
        evidence_fingerprint=None,
        unclear_failure=True,
    )
    assert mission.remediation_count == 1
    assert mission.resume_agent is AgentName.DEBUGGER
    assert AgentName.DEBUGGER in {assignment.agent for assignment in mission.assignments}

    fingerprint = str(mission_evidence(mission, git_repo)["fingerprint"])
    record_verified_progress(
        mission,
        git_repo,
        store,
        agent=AgentName.DEBUGGER,
        outcome=Outcome.PASSED,
        note="State leaks between calls.",
        evidence_fingerprint=fingerprint,
        unclear_failure=False,
    )
    assert mission.resume_agent is AgentName.ENGINEER
    assert mission.pending_findings == ["State leaks between calls."]

    with (worktree / "app.py").open("a", encoding="utf-8") as handle:
        handle.write("# repaired\n")
    record_verified_progress(
        mission,
        git_repo,
        store,
        agent=AgentName.ENGINEER,
        outcome=Outcome.PASSED,
        note="Repaired the diagnosed state leak.",
        evidence_fingerprint=None,
        unclear_failure=False,
    )

    mission.remediation_count = MAX_REMEDIATION_ROUNDS
    store.save(mission)
    record_verified_progress(
        mission,
        git_repo,
        store,
        agent=AgentName.TESTER,
        outcome=Outcome.NEEDS_WORK,
        note="Still failing after repair.",
        evidence_fingerprint=None,
        unclear_failure=False,
    )
    assert mission.execution_status is ExecutionStatus.BLOCKED


def test_verified_engineer_block_preserves_resume_role(git_repo: Path) -> None:
    mission = _mission(git_repo)
    store = MissionStore(git_repo)
    record_verified_progress(
        mission,
        git_repo,
        store,
        agent=AgentName.ENGINEER,
        outcome=Outcome.BLOCKED,
        note="A required local service is unavailable.",
        evidence_fingerprint=None,
        unclear_failure=False,
    )
    assert mission.execution_status is ExecutionStatus.BLOCKED
    assert mission.resume_agent is AgentName.ENGINEER


def test_quality_gate_rejects_checks_that_modify_the_worktree(git_repo: Path) -> None:
    mission = _mission(
        git_repo,
        quality=(
            '["python", "-c", "from pathlib import Path; '
            'Path(\\"generated.txt\\").write_text(\\"x\\")"]'
        ),
    )
    records = run_mission_checks(mission, git_repo)
    assert records[-1].name == "workspace-integrity"
    assert records[-1].outcome == "failed"
    assert "changed repository files" in records[-1].output
