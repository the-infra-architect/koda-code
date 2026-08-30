from pathlib import Path

import pytest

from koda_code.errors import KodaError
from koda_code.models import (
    AgentAssignment,
    AgentName,
    ExecutionAttempt,
    ExecutionStatus,
    Mission,
    MissionAnswer,
    RepositoryEvidence,
    RequirementUnderstanding,
    TechnicalApproach,
)
from koda_code.store import MissionStore


def mission(identifier: str = "build-inventory-a1b2c3d4") -> Mission:
    return Mission(
        mission_id=identifier,
        request="Build inventory",
        created_at="2026-08-29T00:00:00+00:00",
        repository=RepositoryEvidence("/p", True, ("Python",), (), True, False, False, (), 4),
        understanding=RequirementUnderstanding("Build inventory", (), (), ("persistent_data",)),
        approach=TechnicalApproach("Extend it", ("Evidence",), (), (), ("No queue",), ()),
        assignments=[AgentAssignment(AgentName.ENGINEER, "Implement")],
    )


def test_round_trip_and_brief(tmp_path: Path) -> None:
    store = MissionStore(tmp_path)
    path = store.save(mission())
    assert path.is_file()
    assert (path.parent / "brief.md").is_file()
    assert store.load("build-inventory-a1b2c3d4").to_dict() == mission().to_dict()


def test_round_trip_preserves_autonomous_execution_state(tmp_path: Path) -> None:
    item = mission()
    item.execution_status = ExecutionStatus.WAITING_FOR_INPUT
    item.waiting_question = "Who uses it?"
    item.answers = [MissionAnswer("Where is it used?", "Locally", "now")]
    item.executions = [
        ExecutionAttempt(AgentName.ENGINEER, 1, "then", "process_failed", diagnostic="failed")
    ]
    item.remediation_count = 1
    item.pending_findings = ["Handle empty input."]
    item.resume_agent = AgentName.ENGINEER
    store = MissionStore(tmp_path)
    store.save(item)
    assert store.load(item.mission_id).to_dict() == item.to_dict()


def test_v3_state_loads_with_backward_compatible_v4_defaults(tmp_path: Path) -> None:
    item = mission()
    data = item.to_dict()
    for key in (
        "engineering_profile",
        "quality_contract",
        "engineering_fingerprint",
        "base_commit",
        "baseline_checks",
        "schema_version",
    ):
        data.pop(key)
    loaded = Mission.from_dict(data)
    assert loaded.schema_version == 3
    assert loaded.engineering_profile is None
    assert loaded.quality_contract is None


def test_lists_missions_in_order(tmp_path: Path) -> None:
    store = MissionStore(tmp_path)
    store.save(mission("z-last"))
    store.save(mission("a-first"))
    assert store.list_ids() == ["a-first", "z-last"]


@pytest.mark.parametrize("identifier", ["", "UPPER", "../escape", "space here", "under_score"])
def test_rejects_unsafe_identifiers(tmp_path: Path, identifier: str) -> None:
    with pytest.raises(KodaError):
        MissionStore(tmp_path).save(mission(identifier))


def test_rejects_symlinked_state(tmp_path: Path) -> None:
    target = tmp_path / "target"
    target.mkdir()
    (tmp_path / ".koda-code").symlink_to(target, target_is_directory=True)
    with pytest.raises(KodaError, match="symlinked"):
        MissionStore(tmp_path).save(mission())


def test_missing_mission_is_actionable(tmp_path: Path) -> None:
    with pytest.raises(KodaError, match="Mission not found"):
        MissionStore(tmp_path).load("missing")
