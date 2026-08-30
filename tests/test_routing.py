from koda_code.models import AgentName, RequirementUnderstanding
from koda_code.routing import add_debugger, route_agents


def request(signals: tuple[str, ...] = ()) -> RequirementUnderstanding:
    return RequirementUnderstanding("Build it", (), (), signals)


def names(signals: tuple[str, ...] = ()) -> list[AgentName]:
    return [item.agent for item in route_agents(request(signals))]


def test_baseline_route_is_small() -> None:
    assert names() == [AgentName.ENGINEER, AgentName.TESTER, AgentName.REVIEWER]


def test_ui_role_is_conditional() -> None:
    assert names(("user_interface",)) == [
        AgentName.ENGINEER,
        AgentName.UI_UX,
        AgentName.TESTER,
        AgentName.REVIEWER,
    ]


def test_debugger_is_not_added_for_clear_failure() -> None:
    assignments = route_agents(request())
    assert add_debugger(assignments, unclear_failure=False) == assignments


def test_debugger_is_inserted_before_review() -> None:
    assignments = add_debugger(route_agents(request()), unclear_failure=True)
    assert [item.agent for item in assignments] == [
        AgentName.ENGINEER,
        AgentName.TESTER,
        AgentName.DEBUGGER,
        AgentName.REVIEWER,
    ]


def test_debugger_is_not_duplicated() -> None:
    first = add_debugger(route_agents(request()), unclear_failure=True)
    assert add_debugger(first, unclear_failure=True) == first
