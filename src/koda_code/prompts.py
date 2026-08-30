from __future__ import annotations

from .errors import KodaError
from .models import AgentName, CapabilityState, Mission, Outcome

AGENT_FOCUS = {
    AgentName.ENGINEER: (
        "Implement the requested outcome. Inspect before deciding, honor explicit constraints, "
        "and prefer the least complex solution that remains correct and maintainable."
    ),
    AgentName.TESTER: (
        "Challenge the behavior independently. Cover acceptance behavior, important boundaries, "
        "failure modes, and regressions without testing implementation trivia."
    ),
    AgentName.REVIEWER: (
        "Review correctness, readability, naming, typing, duplication, security, dependencies, "
        "resource use, performance, framework conventions, and over/underengineering."
    ),
    AgentName.UI_UX: (
        "Review the meaningful interface change for task clarity, hierarchy, accessibility, "
        "responsive behavior, empty/error/loading states, and beginner comprehension."
    ),
    AgentName.DEBUGGER: (
        "Diagnose the unclear reproducible failure at the smallest causal boundary. Gather "
        "evidence and report the root cause; do not modify files."
    ),
}

ENGINEERING_PRINCIPLES = """Solve the actual requested outcome and inspect before deciding.
Respect explicit constraints and established project conventions. Use the least complex coherent
solution: every function, class, interface, service, and dependency must earn its place. Prefer
readable code, clear domain names, useful types, secure trust boundaries, actionable errors, and
meaningful behavioral tests. Consider CPU, memory, I/O, algorithms, queries, concurrency, and
resource cleanup in proportion to the workload; measure non-obvious optimizations. Never claim
success without verification."""

RESULT_CONTRACT = """Return exactly one JSON object and no Markdown or surrounding prose:
{"outcome":"pass|changes_required|needs_input|blocked","summary":"concise result",
"findings":["actionable issue"],"question":null,"unclear_failure":false}
Use needs_input with exactly one concise product-language question when a material requirement
cannot be inferred safely. Use changes_required only with actionable findings. Do not report
changed-file lists or claim deterministic checks passed; Koda derives those facts itself."""


def next_assignment(mission: Mission) -> AgentName | None:
    for assignment in mission.assignments:
        stage = mission.stages.get(assignment.agent.value)
        if stage is None or stage.outcome is not Outcome.PASSED:
            return assignment.agent
    return None


def render_agent_packet(mission: Mission, agent: AgentName | None = None) -> str:
    selected = agent or next_assignment(mission)
    if selected is None:
        raise KodaError("All assigned agent stages are complete; run the quality gate.")
    if selected not in {item.agent for item in mission.assignments}:
        raise KodaError(f"Agent is not assigned to this mission: {selected.value}")
    questions = (
        "\n".join(f"- {item}" for item in mission.understanding.product_questions) or "- None"
    )
    engineering_context = _engineering_context(mission, selected)
    return f"""# {selected.value.replace("_", " ").title()} assignment

## Outcome requested

{mission.request}

## Current technical approach

{mission.approach.summary}

## Product questions still requiring care

{questions}

## Your responsibility

{AGENT_FOCUS[selected]}

## Adaptive engineering context

{engineering_context}

Do not claim completion without reporting the exact evidence you produced.
"""


def render_execution_prompt(
    mission: Mission,
    agent: AgentName,
    *,
    repository_diff: str,
    changed_paths: tuple[str, ...],
    validation_evidence: str,
) -> str:
    if agent not in {item.agent for item in mission.assignments}:
        raise KodaError(f"Agent is not assigned to this mission: {agent.value}")
    constraints = ", ".join(mission.understanding.explicit_technical_constraints) or "None"
    conventions = (
        ", ".join((*mission.repository.languages, *mission.repository.frameworks))
        or "No established stack was detected; inspect the project and choose proportionately."
    )
    answers = (
        "\n".join(f"- {item.question}\n  Answer: {item.answer}" for item in mission.answers)
        or "- None"
    )
    findings = "\n".join(f"- {item}" for item in mission.pending_findings) or "- None"
    paths = "\n".join(f"- {item}" for item in changed_paths) or "- None yet"
    role_boundary = _role_boundary(agent)
    role_context = _role_context(
        agent,
        mission=mission,
        repository_diff=repository_diff,
        paths=paths,
        validation_evidence=validation_evidence,
        findings=findings,
    )
    engineering_context = _engineering_context(mission, agent)
    return f"""# Koda {agent.value.replace("_", " ").title()} execution

You are a fresh, independent {agent.value.replace("_", " ")} execution. Work only in the current
mission worktree. Never commit, push, open or merge a pull request, switch branches, reset history,
clean unrelated files, access unrelated paths, or perform delivery. Koda owns Git and delivery.

## Requested outcome

{mission.request}

## Shared engineering constitution

{ENGINEERING_PRINCIPLES}

## Project evidence

Established languages/frameworks: {conventions}
Explicit user constraints: {constraints}
Technical direction: {mission.approach.summary}

Adaptive engineering profile and quality contract:
{engineering_context}

## Resolved product information

{answers}

## Role responsibility

{AGENT_FOCUS[agent]}
{role_boundary}

{role_context}

## Result contract

{RESULT_CONTRACT}
"""


def _role_boundary(agent: AgentName) -> str:
    if agent is AgentName.TESTER:
        return (
            "You may add or improve meaningful tests. Do not rewrite production code to force a "
            "pass; report implementation defects for Engineer repair."
        )
    if agent is AgentName.REVIEWER:
        return "This is read-only review. Do not edit source, tests, configuration, or Git state."
    if agent is AgentName.DEBUGGER:
        return "This is read-only diagnosis. Do not repair or edit files; Engineer applies the fix."
    if agent is AgentName.UI_UX:
        return "Change only the relevant interface surface and preserve the existing design system."
    return "Implement the smallest sound change and add focused tests where appropriate."


def _role_context(
    agent: AgentName,
    *,
    mission: Mission,
    repository_diff: str,
    paths: str,
    validation_evidence: str,
    findings: str,
) -> str:
    if agent is AgentName.ENGINEER:
        return f"""## Repair evidence from prior independent stages

{findings}

Inspect the relevant repository files before implementing. Existing project conventions win unless
the requested outcome genuinely requires a broader decision."""
    if agent is AgentName.TESTER:
        return f"""## Actual repository evidence

Changed paths:
{paths}

Git diff (bounded):
```diff
{repository_diff or "No textual diff is available; inspect the changed paths directly."}
```

Independently derive behavioral, boundary, failure, security, and regression tests from the user
outcome. You have not been given Engineer reasoning or self-justification."""
    if agent is AgentName.REVIEWER:
        return f"""## Actual repository evidence

Changed paths:
{paths}

Git diff (bounded):
```diff
{repository_diff or "No textual diff is available; inspect the changed paths directly."}
```

Deterministic validation evidence:
{validation_evidence or "No passing validation evidence is available."}

Challenge both overengineering and underengineering. Review correctness, security, resource use,
framework conventions, typing, naming, maintainability, and test quality. You have not been given
Engineer reasoning or self-justification."""
    if agent is AgentName.DEBUGGER:
        return f"""## Reproducible failure evidence

{findings}

Deterministic validation evidence:
{validation_evidence or "No additional validation output is available."}

Identify the root cause and what Engineer should change. Do not make the repair."""
    return f"""## Relevant interface evidence

Changed paths:
{paths}

Git diff (bounded):
```diff
{repository_diff or "No textual diff is available; inspect the relevant UI files."}
```

Evaluate only the requested interaction and its relevant states, accessibility, responsiveness,
and consistency with the existing application."""


def _engineering_context(mission: Mission, agent: AgentName) -> str:
    profile = mission.engineering_profile
    contract = mission.quality_contract
    if profile is None or contract is None:
        return "No V4 profile is available; inspect repository evidence and do not infer a pass."
    profile_lines = [
        f"- Mode: {profile.project_mode.value}",
        f"- Important qualities: {', '.join(profile.quality_attributes) or 'none detected'}",
        f"- Deployment: {', '.join(profile.deployment_topology) or 'unknown'}",
    ]
    for label, values in (
        ("Security", profile.security_surfaces),
        ("Compatibility", profile.compatibility_surfaces),
        ("Data", profile.data_concerns),
        ("Distributed", profile.distributed_concerns),
    ):
        if values:
            profile_lines.append(f"- {label}: {', '.join(values)}")
    relevant_names = _relevant_capabilities(agent)
    selected = [
        item
        for item in contract.capabilities
        if item.name in relevant_names and item.state is not CapabilityState.NOT_APPLICABLE
    ]
    capability_lines = [
        f"- {item.name}: {item.state.value}/{item.verification.value} — {item.reason}"
        for item in selected
    ]
    if profile.unresolved_questions:
        profile_lines.append(
            f"- Unresolved material questions: {len(profile.unresolved_questions)}"
        )
    return "\n".join(
        (*profile_lines, "- Relevant capabilities:", *(capability_lines or ["  - None detected."]))
    )


def _relevant_capabilities(agent: AgentName) -> set[str]:
    shared = {"unit_tests", "integration_tests", "compatibility", "documentation"}
    if agent is AgentName.ENGINEER:
        return shared | {
            "type_compile",
            "build_package",
            "static_security",
            "web_security",
            "migration_data_integrity",
            "recovery_backup",
            "authorization",
            "input_validation",
            "secure_defaults",
            "idempotency",
            "cache_consistency",
            "retry_safety",
        }
    if agent is AgentName.TESTER:
        return shared | {
            "e2e_tests",
            "fuzz_property",
            "accessibility",
            "performance_load",
            "web_security",
            "authorization",
            "input_validation",
            "migration_data_integrity",
            "idempotency",
            "retry_safety",
        }
    if agent is AgentName.UI_UX:
        return {"accessibility", "e2e_tests", "secure_defaults", "web_security"}
    if agent is AgentName.DEBUGGER:
        return {item for item in CAPABILITY_NAMES_FOR_DIAGNOSIS}
    return set(CAPABILITY_NAMES_FOR_DIAGNOSIS)


CAPABILITY_NAMES_FOR_DIAGNOSIS = {
    "format",
    "lint",
    "type_compile",
    "unit_tests",
    "integration_tests",
    "e2e_tests",
    "build_package",
    "secret_scan",
    "dependency_analysis",
    "static_security",
    "web_security",
    "accessibility",
    "performance_load",
    "migration_data_integrity",
    "recovery_backup",
    "compatibility",
    "ci_security",
    "dependency_reproducibility",
    "component_inventory",
    "build_provenance",
    "artifact_integrity",
    "authorization",
    "input_validation",
    "secure_defaults",
    "observability",
    "idempotency",
    "cache_consistency",
    "retry_safety",
}
