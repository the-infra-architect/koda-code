from pathlib import Path

from koda_code.workflow import begin_mission, mission_identifier


def test_identifier_is_deterministic_and_request_specific(tmp_path: Path) -> None:
    first = mission_identifier("Build inventory", tmp_path)
    assert first == mission_identifier("Build inventory", tmp_path)
    assert first != mission_identifier("Build reports", tmp_path)
    assert first.startswith("build-inventory-")


def test_begin_creates_mission_and_brief(git_repo: Path) -> None:
    mission = begin_mission("Build an inventory tracking page", git_repo)
    folder = git_repo / ".koda-code" / "missions" / mission.mission_id
    assert (folder / "mission.json").is_file()
    assert (folder / "brief.md").is_file()
    assert mission.assignments[0].agent.value == "engineer"
    assert any(item.agent.value == "ui_ux" for item in mission.assignments)


def test_begin_can_prepare_worktree(git_repo: Path) -> None:
    mission = begin_mission("Improve error handling", git_repo, prepare_worktree=True)
    assert mission.branch and mission.branch.startswith("feature/")
    assert mission.worktree and Path(mission.worktree).is_dir()
