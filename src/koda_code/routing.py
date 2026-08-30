from __future__ import annotations

from .models import AgentAssignment, AgentName, RequirementUnderstanding


def route_agents(understanding: RequirementUnderstanding) -> list[AgentAssignment]:
    assignments = [
        AgentAssignment(
            AgentName.ENGINEER, "Understand the outcome and implement the smallest sound change."
        ),
    ]
    if "user_interface" in understanding.capability_signals:
        assignments.append(
            AgentAssignment(
                AgentName.UI_UX, "The request contains a meaningful user-interface change."
            )
        )
    assignments.append(
        AgentAssignment(
            AgentName.TESTER, "Challenge behavior and important boundaries independently."
        )
    )
    assignments.append(
        AgentAssignment(
            AgentName.REVIEWER,
            "Review correctness, clarity, proportionality, and operational risk.",
        )
    )
    return assignments


def add_debugger(
    assignments: list[AgentAssignment], *, unclear_failure: bool
) -> list[AgentAssignment]:
    if not unclear_failure or any(item.agent is AgentName.DEBUGGER for item in assignments):
        return assignments
    updated = list(assignments)
    reviewer_index = next(
        (index for index, item in enumerate(updated) if item.agent is AgentName.REVIEWER),
        len(updated),
    )
    updated.insert(
        reviewer_index,
        AgentAssignment(AgentName.DEBUGGER, "A reproducible failure has no clear root cause yet."),
    )
    return updated
