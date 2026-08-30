import subprocess
from pathlib import Path

import pytest

from koda_code.errors import KodaError
from koda_code.workflow import begin_mission
from koda_code.workspace import (
    branch_slug,
    create_mission_worktree,
    current_branch,
    refuse_protected_branch,
    validate_mission_worktree,
)


def test_branch_slug_is_focused_and_bounded() -> None:
    result = branch_slug("Build a useful inventory tracking page today", "mission-123")
    assert result == "feature/mission-123-build-a-useful-inventory-tracking"
    assert len(result) <= 90


def test_creates_sibling_worktree(git_repo: Path) -> None:
    path, branch = create_mission_worktree(git_repo, "mission-123", "Add inventory")
    assert path.parent == git_repo.parent / f"{git_repo.name}-worktrees"
    assert path.is_dir()
    assert current_branch(path) == branch


def test_refuses_worktree_for_non_git_folder(tmp_path: Path) -> None:
    with pytest.raises(KodaError, match="Create a Git repository"):
        create_mission_worktree(tmp_path, "mission-123", "Add inventory")


def test_refuses_existing_worktree(git_repo: Path) -> None:
    create_mission_worktree(git_repo, "mission-123", "Add inventory")
    with pytest.raises(KodaError, match="already exists"):
        create_mission_worktree(git_repo, "mission-123", "Add inventory")


def test_refuses_dirty_stable_checkout(git_repo: Path) -> None:
    (git_repo / "README.md").write_text("# Dirty\n", encoding="utf-8")
    with pytest.raises(KodaError, match="uncommitted changes"):
        create_mission_worktree(git_repo, "mission-123", "Add inventory")


def test_refuses_protected_branch(git_repo: Path) -> None:
    with pytest.raises(KodaError, match="protected branch"):
        refuse_protected_branch(git_repo)


def test_validates_recorded_mission_worktree(git_repo: Path) -> None:
    mission = begin_mission("Improve project error handling", git_repo, prepare_worktree=True)
    assert validate_mission_worktree(mission, git_repo) == Path(mission.worktree or "")


def test_refuses_tampered_worktree_location(git_repo: Path) -> None:
    mission = begin_mission("Improve project error handling", git_repo, prepare_worktree=True)
    mission.worktree = str(git_repo)
    with pytest.raises(KodaError, match="not isolated"):
        validate_mission_worktree(mission, git_repo)


def test_refuses_detached_or_protected_recorded_branch(git_repo: Path) -> None:
    mission = begin_mission("Improve project error handling", git_repo, prepare_worktree=True)
    worktree = Path(mission.worktree or "")
    subprocess.run(["git", "checkout", "--detach"], cwd=worktree, check=True, capture_output=True)
    with pytest.raises(KodaError, match="recorded branch"):
        validate_mission_worktree(mission, git_repo)
    mission.branch = "main"
    with pytest.raises(KodaError, match="protected branch"):
        validate_mission_worktree(mission, git_repo)


def test_refuses_missing_or_symlinked_worktree(git_repo: Path, tmp_path: Path) -> None:
    mission = begin_mission("Improve project error handling", git_repo, prepare_worktree=True)
    mission.worktree = str(tmp_path / "missing")
    with pytest.raises(KodaError, match="missing"):
        validate_mission_worktree(mission, git_repo)
    outside = tmp_path / "outside"
    outside.mkdir()
    link = tmp_path / "link"
    link.symlink_to(outside, target_is_directory=True)
    mission.worktree = str(link)
    with pytest.raises(KodaError, match="expected location"):
        validate_mission_worktree(mission, git_repo)
