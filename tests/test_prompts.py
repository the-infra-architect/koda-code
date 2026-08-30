import pytest

from koda_code.errors import KodaError
from koda_code.models import (
    AgentAssignment,
    AgentName,
    Mission,
    Outcome,
    RepositoryEvidence,
    RequirementUnderstanding,
    StageRecord,
    TechnicalApproach,
)
from koda_code.prompts import next_assignment, render_agent_packet


def mission() -> Mission:
    return Mission(
        "m-1",
        "Build an inventory page",
        "now",
        RepositoryEvidence("/p", True, (), (), False, False, False, (), 0),
        RequirementUnderstanding(
            "Build an inventory page", (), ("Who uses it?",), ("user_interface",)
        ),
        TechnicalApproach("Resolve product needs first.", (), (), (), (), ()),
        [
            AgentAssignment(AgentName.ENGINEER, "Implement"),
            AgentAssignment(AgentName.TESTER, "Test"),
        ],
    )


def test_next_assignment_advances_after_pass() -> None:
    item = mission()
    assert next_assignment(item) is AgentName.ENGINEER
    item.stages["engineer"] = StageRecord(Outcome.PASSED, "done")
    assert next_assignment(item) is AgentName.TESTER


def test_packet_contains_mission_evidence() -> None:
    packet = render_agent_packet(mission())
    assert "Build an inventory page" in packet
    assert "Who uses it?" in packet
    assert "least complex" in packet


def test_unassigned_agent_is_rejected() -> None:
    with pytest.raises(KodaError, match="not assigned"):
        render_agent_packet(mission(), AgentName.DEBUGGER)


def test_complete_route_has_no_next_assignment() -> None:
    item = mission()
    item.stages = {
        "engineer": StageRecord(Outcome.PASSED, "done"),
        "tester": StageRecord(Outcome.PASSED, "done"),
    }
    assert next_assignment(item) is None
    with pytest.raises(KodaError, match="quality gate"):
        render_agent_packet(item)
