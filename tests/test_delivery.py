from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from koda_code.delivery import finish_mission
from koda_code.errors import KodaError
from koda_code.evidence import worktree_fingerprint
from koda_code.models import (
    AgentAssignment,
    AgentName,
    CheckRecord,
    Mission,
    Outcome,
    RepositoryEvidence,
    RequirementUnderstanding,
    StageRecord,
    TechnicalApproach,
)


def ready_mission(repository: Path) -> Mission:
    item = Mission(
        "m-1",
        "Change behavior",
        "now",
        RepositoryEvidence("/p", True, (), (), True, True, False, (), 1),
        RequirementUnderstanding("Change behavior", (), (), ()),
        TechnicalApproach("Small change", (), (), (), (), ()),
        [
            AgentAssignment(AgentName.ENGINEER, "Implement"),
            AgentAssignment(AgentName.TESTER, "Test"),
            AgentAssignment(AgentName.REVIEWER, "Review"),
        ],
    )
    item.stages = {
        name.value: StageRecord(Outcome.PASSED, "verified")
        for name in (AgentName.ENGINEER, AgentName.TESTER, AgentName.REVIEWER)
    }
    item.checks = [CheckRecord("tests", ["python", "-m", "pytest"], "passed", 0, 1.0, "ok")]
    item.check_fingerprint = worktree_fingerprint(repository)
    return item


def feature_branch(repository: Path) -> None:
    subprocess.run(
        ["git", "checkout", "-b", "feature/test"], cwd=repository, check=True, capture_output=True
    )


def test_commits_only_named_paths(git_repo: Path) -> None:
    feature_branch(git_repo)
    selected = git_repo / "selected.txt"
    unrelated = git_repo / "unrelated.txt"
    selected.write_text("selected\n", encoding="utf-8")
    unrelated.write_text("unrelated\n", encoding="utf-8")
    commit = finish_mission(
        ready_mission(git_repo), git_repo, ["selected.txt"], "Add selected file"
    )
    assert len(commit) == 40
    status = subprocess.run(
        ["git", "status", "--short"], cwd=git_repo, text=True, capture_output=True, check=True
    ).stdout
    assert "unrelated.txt" in status
    assert "selected.txt" not in status


def test_rejects_incomplete_stages(git_repo: Path) -> None:
    feature_branch(git_repo)
    item = ready_mission(git_repo)
    del item.stages["reviewer"]
    with pytest.raises(KodaError, match="incomplete"):
        finish_mission(item, git_repo, ["README.md"], "Message")


def test_rejects_failed_quality(git_repo: Path) -> None:
    feature_branch(git_repo)
    item = ready_mission(git_repo)
    item.checks[0].outcome = "failed"
    with pytest.raises(KodaError, match="quality gate"):
        finish_mission(item, git_repo, ["README.md"], "Message")


def test_rejects_unrelated_pre_staged_file(git_repo: Path) -> None:
    feature_branch(git_repo)
    (git_repo / "other.txt").write_text("other", encoding="utf-8")
    subprocess.run(["git", "add", "other.txt"], cwd=git_repo, check=True)
    with pytest.raises(KodaError, match="already staged"):
        finish_mission(ready_mission(git_repo), git_repo, ["README.md"], "Message")


def test_rejects_secret(git_repo: Path) -> None:
    feature_branch(git_repo)
    secret = git_repo / "settings.py"
    field = "pass" + "word"
    value = "not-safe-" + "secret"
    secret.write_text(f'{field} = "{value}"\n', encoding="utf-8")
    with pytest.raises(KodaError, match="Secret scan"):
        finish_mission(ready_mission(git_repo), git_repo, ["settings.py"], "Message")


def test_rejects_stale_quality_fingerprint(git_repo: Path) -> None:
    feature_branch(git_repo)
    item = ready_mission(git_repo)
    (git_repo / "README.md").write_text("# Changed after checks\n", encoding="utf-8")
    with pytest.raises(KodaError, match="evidence is stale"):
        finish_mission(item, git_repo, ["README.md"], "Message")
