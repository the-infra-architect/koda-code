import json
from pathlib import Path

import pytest

import koda_code.cli as cli
from koda_code.cli import main
from koda_code.execution import RunReport
from koda_code.models import ExecutionStatus


def test_begin_and_list_missions(git_repo: Path, capsys: object) -> None:
    assert main(["begin", "Build an inventory page", "--repo", str(git_repo)]) == 0
    identifier = next((git_repo / ".koda-code" / "missions").iterdir()).name
    assert main(["missions", "--repo", str(git_repo)]) == 0
    assert identifier in capsys.readouterr().out  # type: ignore[attr-defined]


def test_guide_and_record(git_repo: Path, capsys: object) -> None:
    main(["begin", "Improve errors", "--repo", str(git_repo)])
    identifier = next((git_repo / ".koda-code" / "missions").iterdir()).name
    assert main(["guide", identifier, "--repo", str(git_repo)]) == 0
    assert "Engineer assignment" in capsys.readouterr().out  # type: ignore[attr-defined]
    assert (
        main(
            [
                "record",
                identifier,
                "--repo",
                str(git_repo),
                "--agent",
                "engineer",
                "--outcome",
                "passed",
                "--note",
                "Implemented and tested",
            ]
        )
        == 0
    )


def test_unknown_mission_returns_actionable_exit(git_repo: Path, capsys: object) -> None:
    assert main(["guide", "missing", "--repo", str(git_repo)]) == 2
    assert "Cannot continue" in capsys.readouterr().out  # type: ignore[attr-defined]


def test_run_reports_missing_copilot_without_advancing(
    monkeypatch: pytest.MonkeyPatch, git_repo: Path, capsys: object
) -> None:
    main(
        [
            "begin",
            "Improve project error handling",
            "--repo",
            str(git_repo),
            "--prepare-worktree",
        ]
    )
    capsys.readouterr()  # type: ignore[attr-defined]
    identifier = next((git_repo / ".koda-code" / "missions").iterdir()).name
    monkeypatch.setattr("koda_code.execution.detect_copilot", lambda: None)
    assert main(["run", identifier, "--repo", str(git_repo)]) == 1
    output = capsys.readouterr().out  # type: ignore[attr-defined]
    assert "automatic coding could not start" in output
    assert "No commit, push, or pull request" in output


def test_build_is_thin_begin_prepare_and_run_wrapper(
    monkeypatch: pytest.MonkeyPatch, git_repo: Path, capsys: object
) -> None:
    observed: dict[str, object] = {}

    def fake_run(*args: object, **kwargs: object) -> RunReport:
        mission = args[0]
        observed["worktree"] = mission.worktree  # type: ignore[attr-defined]
        return RunReport(
            ExecutionStatus.READY_TO_FINISH,
            "VERIFIED / READY TO FINISH",
            None,
            3,
            mission.worktree,  # type: ignore[attr-defined]
            True,
        )

    monkeypatch.setattr(cli, "run_mission", fake_run)
    assert main(["build", "Improve project error handling", "--repo", str(git_repo), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)  # type: ignore[attr-defined]
    assert payload["status"] == "ready_to_finish"
    assert observed["worktree"]
    assert Path(str(observed["worktree"])).is_dir()
