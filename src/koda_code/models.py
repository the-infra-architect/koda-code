from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


class AgentName(StrEnum):
    ENGINEER = "engineer"
    TESTER = "tester"
    REVIEWER = "reviewer"
    UI_UX = "ui_ux"
    DEBUGGER = "debugger"


class Outcome(StrEnum):
    PASSED = "passed"
    NEEDS_WORK = "needs_work"
    BLOCKED = "blocked"


class AgentResultOutcome(StrEnum):
    PASS = "pass"
    CHANGES_REQUIRED = "changes_required"
    NEEDS_INPUT = "needs_input"
    BLOCKED = "blocked"


class ExecutionStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    WAITING_FOR_INPUT = "waiting_for_input"
    BLOCKED = "blocked"
    READY_TO_FINISH = "ready_to_finish"


class ProjectMode(StrEnum):
    EXISTING = "existing"
    GREENFIELD = "greenfield"


class CapabilityState(StrEnum):
    EXISTING = "existing"
    REQUIRED = "required"
    RECOMMENDED = "recommended"
    UNAVAILABLE = "unavailable"
    NOT_APPLICABLE = "not_applicable"
    UNKNOWN = "unknown"


class CapabilityVerification(StrEnum):
    NOT_RUN = "not_run"
    PASSED = "passed"
    FAILED = "failed"
    UNAVAILABLE = "unavailable"
    NOT_APPLICABLE = "not_applicable"


class EnforcementLevel(StrEnum):
    HARD_INVARIANT = "hard_invariant"
    PROJECT_POLICY = "project_policy"
    CONTEXT_REQUIRED = "context_required"
    RECOMMENDATION = "recommendation"
    REVIEWER_SIGNAL = "reviewer_signal"
    DEFERRED = "deferred"


class EcosystemSupport(StrEnum):
    NATIVE_LIFECYCLE = "native_lifecycle"
    DETECTION_ONLY = "detection_only"


class VulnerabilityState(StrEnum):
    NEW_BLOCKING = "new_blocking"
    NEW_REQUIRES_REVIEW = "new_requires_review"
    PREEXISTING = "preexisting"
    NOT_AFFECTED_EVIDENCED = "not_affected_evidenced"
    FIXED = "fixed"
    UNKNOWN = "unknown"
    TOOL_UNAVAILABLE = "tool_unavailable"


@dataclass(frozen=True)
class EcosystemProfile:
    name: str
    support: EcosystemSupport
    markers: tuple[str, ...] = ()
    commands: tuple[str, ...] = ()


@dataclass(frozen=True)
class EngineeringDecision:
    topic: str
    outcome: str
    rationale: str
    enforcement: EnforcementLevel
    claim_ids: tuple[str, ...] = ()
    rule_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class EngineeringProfile:
    project_mode: ProjectMode
    ecosystems: tuple[EcosystemProfile, ...]
    deployment_topology: tuple[str, ...]
    quality_attributes: tuple[str, ...]
    package_managers: tuple[str, ...]
    lockfiles: tuple[str, ...]
    monorepo_tools: tuple[str, ...]
    migration_tools: tuple[str, ...]
    security_surfaces: tuple[str, ...]
    compatibility_surfaces: tuple[str, ...]
    supply_chain_surfaces: tuple[str, ...]
    data_concerns: tuple[str, ...]
    distributed_concerns: tuple[str, ...]
    ci_security_findings: tuple[str, ...]
    environment_constraints: tuple[str, ...]
    change_surfaces: tuple[str, ...]
    decisions: tuple[EngineeringDecision, ...]
    unresolved_questions: tuple[str, ...]
    fingerprint: str


@dataclass(frozen=True)
class QualityCapability:
    name: str
    state: CapabilityState
    enforcement: EnforcementLevel
    reason: str
    mechanisms: tuple[str, ...] = ()
    evidence: tuple[str, ...] = ()
    claim_ids: tuple[str, ...] = ()
    rule_ids: tuple[str, ...] = ()
    verification: CapabilityVerification = CapabilityVerification.NOT_RUN


@dataclass(frozen=True)
class QualityContract:
    capabilities: tuple[QualityCapability, ...]
    resolved_fingerprint: str


@dataclass(frozen=True)
class VulnerabilityFinding:
    identifier: str
    component: str
    version: str
    direct: bool | None = None
    dependency_scope: str = "unknown"
    severity: str | None = None
    fixed_version: str | None = None
    introduced: bool | None = None
    applicability_evidence: str | None = None
    requested_state: VulnerabilityState | None = None


@dataclass(frozen=True)
class VulnerabilityTriage:
    finding: VulnerabilityFinding
    state: VulnerabilityState
    blocking: bool
    reason: str


@dataclass(frozen=True)
class RepositoryEvidence:
    root: str
    is_git_repository: bool
    languages: tuple[str, ...]
    frameworks: tuple[str, ...]
    has_tests: bool
    has_ci: bool
    has_user_interface: bool
    data_signals: tuple[str, ...]
    inspected_files: int
    notes: tuple[str, ...] = ()
    implementation_files: int = 0
    project_markers: tuple[str, ...] = ()
    package_managers: tuple[str, ...] = ()
    lockfiles: tuple[str, ...] = ()
    lifecycle_commands: tuple[str, ...] = ()
    monorepo_tools: tuple[str, ...] = ()
    migration_tools: tuple[str, ...] = ()
    analysis_tools: tuple[str, ...] = ()
    ci_providers: tuple[str, ...] = ()
    release_signals: tuple[str, ...] = ()
    environment_constraints: tuple[str, ...] = ()


@dataclass(frozen=True)
class RequirementUnderstanding:
    requested_outcome: str
    explicit_technical_constraints: tuple[str, ...]
    product_questions: tuple[str, ...]
    capability_signals: tuple[str, ...]


@dataclass(frozen=True)
class TechnicalApproach:
    summary: str
    reasons: tuple[str, ...]
    constraints_honored: tuple[str, ...]
    complexity_drivers: tuple[str, ...]
    complexity_avoided: tuple[str, ...]
    decisions_deferred: tuple[str, ...]


@dataclass(frozen=True)
class AgentAssignment:
    agent: AgentName
    reason: str


@dataclass
class StageRecord:
    outcome: Outcome
    note: str
    recorded_at: str = field(default_factory=utc_now)


@dataclass
class CheckRecord:
    name: str
    argv: list[str]
    outcome: str
    exit_code: int | None
    duration_seconds: float
    output: str
    baseline_outcome: str | None = None
    attribution: str = "current"


@dataclass(frozen=True)
class AgentResult:
    outcome: AgentResultOutcome
    summary: str
    findings: tuple[str, ...] = ()
    question: str | None = None
    unclear_failure: bool = False


@dataclass
class ExecutionAttempt:
    role: AgentName
    attempt: int
    started_at: str
    process_outcome: str
    finished_at: str | None = None
    exit_code: int | None = None
    timed_out: bool = False
    sandboxed: bool = False
    summary: str = ""
    findings: list[str] = field(default_factory=list)
    question: str | None = None
    diagnostic: str = ""
    changed_paths: list[str] = field(default_factory=list)
    repository_fingerprint: str = ""


@dataclass(frozen=True)
class MissionAnswer:
    question: str
    answer: str
    recorded_at: str = field(default_factory=utc_now)


@dataclass
class Mission:
    mission_id: str
    request: str
    created_at: str
    repository: RepositoryEvidence
    understanding: RequirementUnderstanding
    approach: TechnicalApproach
    assignments: list[AgentAssignment]
    stages: dict[str, StageRecord] = field(default_factory=dict)
    checks: list[CheckRecord] = field(default_factory=list)
    check_fingerprint: str | None = None
    worktree: str | None = None
    branch: str | None = None
    delivered_commit: str | None = None
    executions: list[ExecutionAttempt] = field(default_factory=list)
    remediation_count: int = 0
    execution_status: ExecutionStatus = ExecutionStatus.PENDING
    waiting_question: str | None = None
    answers: list[MissionAnswer] = field(default_factory=list)
    pending_findings: list[str] = field(default_factory=list)
    resume_agent: AgentName | None = None
    engineering_profile: EngineeringProfile | None = None
    quality_contract: QualityContract | None = None
    engineering_fingerprint: str | None = None
    base_commit: str | None = None
    baseline_checks: list[CheckRecord] = field(default_factory=list)
    schema_version: int = 4

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Mission:
        repo = RepositoryEvidence(
            **{
                **data["repository"],
                "languages": tuple(data["repository"]["languages"]),
                "frameworks": tuple(data["repository"]["frameworks"]),
                "data_signals": tuple(data["repository"]["data_signals"]),
                "notes": tuple(data["repository"].get("notes", [])),
                "project_markers": tuple(data["repository"].get("project_markers", [])),
                "package_managers": tuple(data["repository"].get("package_managers", [])),
                "lockfiles": tuple(data["repository"].get("lockfiles", [])),
                "lifecycle_commands": tuple(data["repository"].get("lifecycle_commands", [])),
                "monorepo_tools": tuple(data["repository"].get("monorepo_tools", [])),
                "migration_tools": tuple(data["repository"].get("migration_tools", [])),
                "analysis_tools": tuple(data["repository"].get("analysis_tools", [])),
                "ci_providers": tuple(data["repository"].get("ci_providers", [])),
                "release_signals": tuple(data["repository"].get("release_signals", [])),
                "environment_constraints": tuple(
                    data["repository"].get("environment_constraints", [])
                ),
            }
        )
        understanding = RequirementUnderstanding(
            **{
                **data["understanding"],
                "explicit_technical_constraints": tuple(
                    data["understanding"]["explicit_technical_constraints"]
                ),
                "product_questions": tuple(data["understanding"]["product_questions"]),
                "capability_signals": tuple(data["understanding"]["capability_signals"]),
            }
        )
        approach = TechnicalApproach(
            **{
                **data["approach"],
                "reasons": tuple(data["approach"]["reasons"]),
                "constraints_honored": tuple(data["approach"]["constraints_honored"]),
                "complexity_drivers": tuple(data["approach"]["complexity_drivers"]),
                "complexity_avoided": tuple(data["approach"]["complexity_avoided"]),
                "decisions_deferred": tuple(data["approach"]["decisions_deferred"]),
            }
        )
        assignments = [
            AgentAssignment(agent=AgentName(item["agent"]), reason=item["reason"])
            for item in data["assignments"]
        ]
        stages = {
            key: StageRecord(
                outcome=Outcome(value["outcome"]),
                note=value["note"],
                recorded_at=value["recorded_at"],
            )
            for key, value in data.get("stages", {}).items()
        }
        checks = [CheckRecord(**item) for item in data.get("checks", [])]
        baseline_checks = [CheckRecord(**item) for item in data.get("baseline_checks", [])]
        engineering_profile = _engineering_profile_from_dict(data.get("engineering_profile"))
        quality_contract = _quality_contract_from_dict(data.get("quality_contract"))
        executions = [
            ExecutionAttempt(
                **{
                    **item,
                    "role": AgentName(item["role"]),
                }
            )
            for item in data.get("executions", [])
        ]
        answers = [MissionAnswer(**item) for item in data.get("answers", [])]
        return cls(
            mission_id=data["mission_id"],
            request=data["request"],
            created_at=data["created_at"],
            repository=repo,
            understanding=understanding,
            approach=approach,
            assignments=assignments,
            stages=stages,
            checks=checks,
            check_fingerprint=data.get("check_fingerprint"),
            worktree=data.get("worktree"),
            branch=data.get("branch"),
            delivered_commit=data.get("delivered_commit"),
            executions=executions,
            remediation_count=int(data.get("remediation_count", 0)),
            execution_status=ExecutionStatus(data.get("execution_status", "pending")),
            waiting_question=data.get("waiting_question"),
            answers=answers,
            pending_findings=list(data.get("pending_findings", [])),
            resume_agent=(
                AgentName(data["resume_agent"]) if data.get("resume_agent") is not None else None
            ),
            engineering_profile=engineering_profile,
            quality_contract=quality_contract,
            engineering_fingerprint=data.get("engineering_fingerprint"),
            base_commit=data.get("base_commit"),
            baseline_checks=baseline_checks,
            schema_version=int(data.get("schema_version", 3)),
        )


def _engineering_profile_from_dict(data: Any) -> EngineeringProfile | None:
    if not isinstance(data, dict):
        return None
    ecosystems = tuple(
        EcosystemProfile(
            name=str(item["name"]),
            support=EcosystemSupport(item["support"]),
            markers=tuple(item.get("markers", [])),
            commands=tuple(item.get("commands", [])),
        )
        for item in data.get("ecosystems", [])
    )
    decisions = tuple(
        EngineeringDecision(
            topic=str(item["topic"]),
            outcome=str(item["outcome"]),
            rationale=str(item["rationale"]),
            enforcement=EnforcementLevel(item["enforcement"]),
            claim_ids=tuple(item.get("claim_ids", [])),
            rule_ids=tuple(item.get("rule_ids", [])),
        )
        for item in data.get("decisions", [])
    )
    tuple_fields = {
        key: tuple(data.get(key, []))
        for key in (
            "deployment_topology",
            "quality_attributes",
            "package_managers",
            "lockfiles",
            "monorepo_tools",
            "migration_tools",
            "security_surfaces",
            "compatibility_surfaces",
            "supply_chain_surfaces",
            "data_concerns",
            "distributed_concerns",
            "ci_security_findings",
            "environment_constraints",
            "change_surfaces",
            "unresolved_questions",
        )
    }
    return EngineeringProfile(
        project_mode=ProjectMode(data["project_mode"]),
        ecosystems=ecosystems,
        decisions=decisions,
        fingerprint=str(data["fingerprint"]),
        **tuple_fields,
    )


def _quality_contract_from_dict(data: Any) -> QualityContract | None:
    if not isinstance(data, dict):
        return None
    capabilities = tuple(
        QualityCapability(
            name=str(item["name"]),
            state=CapabilityState(item["state"]),
            enforcement=EnforcementLevel(item["enforcement"]),
            reason=str(item["reason"]),
            mechanisms=tuple(item.get("mechanisms", [])),
            evidence=tuple(item.get("evidence", [])),
            claim_ids=tuple(item.get("claim_ids", [])),
            rule_ids=tuple(item.get("rule_ids", [])),
            verification=CapabilityVerification(item.get("verification", "not_run")),
        )
        for item in data.get("capabilities", [])
    )
    return QualityContract(capabilities, str(data["resolved_fingerprint"]))
