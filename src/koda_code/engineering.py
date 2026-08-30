from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, replace
from pathlib import Path

from .ci_security import inspect_github_actions
from .models import (
    CapabilityState,
    CapabilityVerification,
    CheckRecord,
    EcosystemProfile,
    EcosystemSupport,
    EnforcementLevel,
    EngineeringDecision,
    EngineeringProfile,
    Mission,
    MissionAnswer,
    ProjectMode,
    QualityCapability,
    QualityContract,
    RepositoryEvidence,
    RequirementUnderstanding,
)

CAPABILITY_VOCABULARY = (
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
    "fuzz_property",
    "accessibility",
    "performance_load",
    "migration_data_integrity",
    "recovery_backup",
    "compatibility",
    "documentation",
    "ci_mirror",
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
)


@dataclass(frozen=True)
class StorageAssessment:
    requested_store: str | None
    suitable: bool | None
    recommendation: str
    concerns: tuple[str, ...]
    claim_ids: tuple[str, ...]
    rule_ids: tuple[str, ...]


def derive_engineering_profile(
    evidence: RepositoryEvidence,
    understanding: RequirementUnderstanding,
    *,
    changed_paths: tuple[str, ...] = (),
    answers: tuple[MissionAnswer, ...] = (),
) -> EngineeringProfile:
    answer_text = " ".join(answer.answer for answer in answers)
    request = f"{understanding.requested_outcome} {answer_text}".lower()
    paths = tuple(path.lower() for path in changed_paths)
    signals = set(understanding.capability_signals)
    constraints = {item.lower() for item in understanding.explicit_technical_constraints}
    mode = _project_mode(evidence, request)
    topology = _deployment_topology(request, signals)
    changes = _change_surfaces(request, paths, signals)
    security = _security_surfaces(evidence, request, changes)
    compatibility = _compatibility_surfaces(evidence, request, changes)
    supply_chain = _supply_chain_surfaces(evidence, changes)
    data = _data_concerns(evidence, request, changes)
    distributed = _distributed_concerns(request, constraints)
    ci_report = inspect_github_actions(Path(evidence.root))
    ci_findings = tuple(
        f"{item.code}:{item.enforcement.value}:{item.path}" for item in ci_report.findings
    )
    quality = _quality_attributes(
        evidence,
        topology,
        security,
        compatibility,
        data,
        distributed,
        changes,
    )
    answered = {answer.question for answer in answers}
    unresolved = tuple(
        question for question in understanding.product_questions if question not in answered
    )
    decisions = _engineering_decisions(
        mode,
        evidence,
        request,
        constraints,
        security,
        compatibility,
        data,
        distributed,
    )
    ecosystems = _ecosystems(evidence)
    fingerprint = _profile_fingerprint(
        evidence,
        understanding,
        changed_paths,
        answers,
    )
    return EngineeringProfile(
        project_mode=mode,
        ecosystems=ecosystems,
        deployment_topology=topology,
        quality_attributes=quality,
        package_managers=evidence.package_managers,
        lockfiles=evidence.lockfiles,
        monorepo_tools=evidence.monorepo_tools,
        migration_tools=evidence.migration_tools,
        security_surfaces=security,
        compatibility_surfaces=compatibility,
        supply_chain_surfaces=supply_chain,
        data_concerns=data,
        distributed_concerns=distributed,
        ci_security_findings=ci_findings,
        environment_constraints=evidence.environment_constraints,
        change_surfaces=changes,
        decisions=decisions,
        unresolved_questions=unresolved,
        fingerprint=fingerprint,
    )


def resolve_mission_engineering(
    mission: Mission,
    repository: Path,
    *,
    changed_paths: tuple[str, ...] = (),
) -> None:
    from .discovery import inspect_repository

    current = inspect_repository(repository)
    profile = derive_engineering_profile(
        current,
        mission.understanding,
        changed_paths=changed_paths,
        answers=tuple(mission.answers),
    )
    mission.engineering_profile = profile
    mission.quality_contract = resolve_quality_contract(profile, current)
    mission.engineering_fingerprint = profile.fingerprint


def mission_engineering_is_stale(
    mission: Mission,
    repository: Path,
    *,
    changed_paths: tuple[str, ...] = (),
) -> bool:
    from .discovery import inspect_repository

    if mission.engineering_profile is None or mission.engineering_fingerprint is None:
        return True
    current = inspect_repository(repository)
    profile = derive_engineering_profile(
        current,
        mission.understanding,
        changed_paths=changed_paths,
        answers=tuple(mission.answers),
    )
    return profile.fingerprint != mission.engineering_fingerprint


def resolve_quality_contract(
    profile: EngineeringProfile,
    evidence: RepositoryEvidence,
) -> QualityContract:
    mechanisms = _mechanisms(evidence)
    changes = set(profile.change_surfaces)
    security = set(profile.security_surfaces)
    compatibility = set(profile.compatibility_surfaces)
    data = set(profile.data_concerns)
    distributed = set(profile.distributed_concerns)
    supply = set(profile.supply_chain_surfaces)
    public_web = "public_web_or_api" in security
    meaningful_ui = "web_ui" in changes
    persistent_change = (
        "persistent_data" in changes
        or "schema_migration" in changes
        or bool(data & {"durable_datastore_constraints", "transaction_boundary"})
    )
    capabilities: list[QualityCapability] = []

    def add(
        name: str,
        *,
        applicable: bool,
        required: bool = False,
        recommended: bool = False,
        unknown: bool = False,
        reason: str,
        enforcement: EnforcementLevel = EnforcementLevel.CONTEXT_REQUIRED,
        claims: tuple[str, ...] = (),
        rules: tuple[str, ...] = (),
    ) -> None:
        found = mechanisms.get(name, ())
        if not applicable:
            state = CapabilityState.NOT_APPLICABLE
            verification = CapabilityVerification.NOT_APPLICABLE
        elif found:
            state = CapabilityState.EXISTING
            verification = CapabilityVerification.NOT_RUN
        elif unknown:
            state = CapabilityState.UNKNOWN
            verification = CapabilityVerification.NOT_RUN
        elif required:
            state = CapabilityState.REQUIRED
            verification = CapabilityVerification.NOT_RUN
        elif recommended:
            state = CapabilityState.RECOMMENDED
            verification = CapabilityVerification.NOT_RUN
        else:
            state = CapabilityState.RECOMMENDED
            verification = CapabilityVerification.NOT_RUN
        capabilities.append(
            QualityCapability(
                name=name,
                state=state,
                enforcement=enforcement,
                reason=reason,
                mechanisms=found,
                evidence=tuple(sorted(_capability_evidence(name, profile))),
                claim_ids=claims,
                rule_ids=rules,
                verification=verification,
            )
        )

    existing_project = profile.project_mode is ProjectMode.EXISTING
    add(
        "format",
        applicable=bool(mechanisms.get("format")),
        recommended=existing_project,
        reason="Preserve an existing formatter; do not install one only for ceremony.",
        enforcement=EnforcementLevel.PROJECT_POLICY
        if mechanisms.get("format")
        else EnforcementLevel.RECOMMENDATION,
        claims=("C007", "C038"),
        rules=("R001",),
    )
    add(
        "lint",
        applicable=bool(mechanisms.get("lint")),
        recommended=existing_project,
        reason="Use existing static-correctness policy when the repository provides it.",
        enforcement=EnforcementLevel.PROJECT_POLICY
        if mechanisms.get("lint")
        else EnforcementLevel.RECOMMENDATION,
        claims=("C038", "C039"),
        rules=("R001",),
    )
    typed = bool(
        {"TypeScript", "Java", "Kotlin", "C#", "Rust", "Go"} & set(_profile_languages(profile))
    )
    add(
        "type_compile",
        applicable=typed or bool(mechanisms.get("type_compile")),
        required=typed,
        reason=(
            "Compile or type-check through the existing native lifecycle without a global "
            "policy migration."
        ),
        enforcement=EnforcementLevel.PROJECT_POLICY
        if mechanisms.get("type_compile")
        else EnforcementLevel.CONTEXT_REQUIRED,
        claims=("C040",),
        rules=("R006",),
    )
    behavior_change = bool(changes - {"documentation"})
    add(
        "unit_tests",
        applicable=behavior_change or bool(mechanisms.get("unit_tests")),
        required=behavior_change,
        reason="Changed behavior needs the fastest meaningful tests for its logic and invariants.",
        claims=("C010", "C011"),
        rules=("R007", "R008"),
    )
    boundary_change = bool(
        changes
        & {
            "persistent_data",
            "schema_migration",
            "network",
            "filesystem",
            "process_execution",
            "api",
        }
    )
    add(
        "integration_tests",
        applicable=boundary_change or bool(mechanisms.get("integration_tests")),
        required=boundary_change,
        reason=(
            "A changed DB, filesystem, network, framework, or process boundary needs "
            "integration evidence."
        ),
        claims=("C011",),
        rules=("R007",),
    )
    critical_journey = meaningful_ui and bool(
        changes & {"authentication", "payment", "critical_journey"}
    )
    add(
        "e2e_tests",
        applicable=meaningful_ui or bool(mechanisms.get("e2e_tests")),
        required=critical_journey,
        recommended=meaningful_ui,
        reason=(
            "E2E evidence is focused on changed critical user journeys, not required for "
            "every repository."
        ),
        claims=("C010", "C011"),
        rules=("R007",),
    )
    distributable = bool(supply & {"published_package", "container_or_release_artifact"})
    add(
        "build_package",
        applicable=distributable or bool(mechanisms.get("build_package")),
        required=distributable,
        reason="Build/package verification follows the artifact role and native lifecycle.",
        claims=("C023", "C055"),
        rules=("R001",),
    )
    add(
        "secret_scan",
        applicable=True,
        recommended=True,
        reason=(
            "Source and configuration can carry credentials; detected real secrets remain "
            "a hard delivery invariant."
        ),
        enforcement=EnforcementLevel.HARD_INVARIANT
        if mechanisms.get("secret_scan")
        else EnforcementLevel.RECOMMENDATION,
        claims=("C018",),
        rules=("R009", "R026"),
    )
    dependency_change = "dependencies" in changes
    add(
        "dependency_analysis",
        applicable=dependency_change or bool(mechanisms.get("dependency_analysis")),
        required=dependency_change,
        reason=(
            "Analyze dependency changes in their runtime/dev/build role and preserve project "
            "policy."
        ),
        claims=("C019", "C069", "C070"),
        rules=("R010",),
    )
    static_security = bool(
        security
        & {
            "public_web_or_api",
            "untrusted_input",
            "file_access",
            "sql_queries",
            "process_execution",
            "plugins_or_deserialization",
        }
    )
    add(
        "static_security",
        applicable=static_security or bool(mechanisms.get("static_security")),
        required=static_security and bool(mechanisms.get("static_security")),
        recommended=static_security,
        reason=(
            "Static security analysis is selected from supported threat surfaces and "
            "available tooling."
        ),
        claims=("C016", "C025", "C071"),
        rules=("R009",),
    )
    add(
        "web_security",
        applicable=public_web,
        required=public_web,
        reason=(
            "Exposed web/API behavior needs testable access, validation, and session controls "
            "where applicable."
        ),
        claims=("C016", "C017"),
        rules=("R009",),
    )
    parser_surface = (
        bool(changes & {"parser", "protocol"}) or "untrusted_structured_input" in security
    )
    add(
        "fuzz_property",
        applicable=parser_surface or bool(mechanisms.get("fuzz_property")),
        recommended=parser_surface,
        reason=(
            "Fuzz/property testing is selective for parsers, protocols, and rich invariant spaces."
        ),
        enforcement=EnforcementLevel.RECOMMENDATION,
        claims=("C010", "C016"),
    )
    add(
        "accessibility",
        applicable=meaningful_ui,
        required=meaningful_ui,
        reason=(
            "Meaningful web interaction requires keyboard, semantic, focus, label, and state "
            "review."
        ),
        claims=("C036",),
        rules=("R023",),
    )
    performance = "performance" in changes
    add(
        "performance_load",
        applicable=performance or bool(mechanisms.get("performance_load")),
        required=performance,
        reason=(
            "Performance validation requires an explicit target, scale signal, or observed "
            "regression."
        ),
        claims=("C026",),
        rules=("R011",),
    )
    add(
        "migration_data_integrity",
        applicable=persistent_change,
        required=persistent_change,
        reason=(
            "Schema/data changes require existing migration, invariant, transaction, and "
            "overlap reasoning."
        ),
        claims=("C030", "C061", "C062", "C066"),
        rules=("R015",),
    )
    valuable_data = "valuable_durable_data" in data
    recovery_unknown = "persistent_data" in data and bool(profile.unresolved_questions)
    add(
        "recovery_backup",
        applicable=valuable_data or recovery_unknown,
        required=valuable_data,
        unknown=recovery_unknown and not valuable_data,
        reason="Recovery follows durable-data value and acceptable loss, not database branding.",
        claims=("C029",),
        rules=("R014",),
    )
    add(
        "compatibility",
        applicable=bool(compatibility),
        required=bool(compatibility),
        reason=(
            "Stable/public API, CLI, config, persisted, message, or multi-version schema "
            "changes need consumer-impact review."
        ),
        claims=("C046", "C047", "C048", "C049"),
    )
    docs = bool(changes & {"public_contract", "setup", "architecture", "documentation"})
    add(
        "documentation",
        applicable=docs,
        required=docs,
        reason=(
            "Update the smallest useful documentation when public/setup/architecture "
            "behavior changes."
        ),
        claims=("C009",),
        rules=("R027",),
    )
    add(
        "ci_mirror",
        applicable=evidence.has_ci or bool(mechanisms.get("ci_mirror")),
        required=evidence.has_ci and "ci_workflow" in changes,
        recommended=not evidence.has_ci,
        reason=(
            "Hosted CI mirrors important local checks when present; local verification "
            "remains valid without it."
        ),
        enforcement=EnforcementLevel.PROJECT_POLICY
        if evidence.has_ci
        else EnforcementLevel.RECOMMENDATION,
        claims=("C021", "C042"),
        rules=("R019", "R028"),
    )
    add(
        "ci_security",
        applicable="github_actions" in supply,
        required="ci_workflow" in changes,
        recommended="github_actions" in supply,
        reason=(
            "GitHub Actions is privileged code: validate permissions, secrets, action "
            "references, and untrusted interpolation."
        ),
        claims=("C052", "C053", "C067"),
        rules=("R020",),
    )
    reproducibility = bool(evidence.lockfiles)
    add(
        "dependency_reproducibility",
        applicable=reproducibility or bool(evidence.package_managers),
        required=dependency_change and not reproducibility,
        recommended=not reproducibility and bool(evidence.package_managers),
        reason=(
            "Preserve ecosystem- and artifact-role-specific resolution state; a lockfile is "
            "not an SBOM."
        ),
        claims=("C023", "C050", "C054", "C055"),
        rules=("R001", "R010"),
    )
    inventory_candidate = distributable and (dependency_change or "release_artifact" in changes)
    add(
        "component_inventory",
        applicable=inventory_candidate,
        recommended=inventory_candidate,
        reason=(
            "An SBOM is a distinct, risk/distribution-driven inventory capability, not a "
            "universal local gate."
        ),
        enforcement=EnforcementLevel.RECOMMENDATION,
        claims=("C050", "C051"),
    )
    add(
        "build_provenance",
        applicable=distributable and "release_artifact" in changes,
        recommended=distributable and "release_artifact" in changes,
        reason=(
            "Provenance describes how a distributed artifact was built and is separate from "
            "inventory."
        ),
        enforcement=EnforcementLevel.RECOMMENDATION,
        claims=("C050", "C051"),
    )
    add(
        "artifact_integrity",
        applicable=distributable and "release_artifact" in changes,
        recommended=distributable and "release_artifact" in changes,
        reason=(
            "Signing/integrity is resolved independently for distributed artifacts and "
            "project policy."
        ),
        enforcement=EnforcementLevel.RECOMMENDATION,
        claims=("C050", "C051"),
    )
    authz = "authorization" in security
    add(
        "authorization",
        applicable=authz,
        required=authz,
        reason=(
            "Protected resources require authorization-boundary behavior, not authentication alone."
        ),
        claims=("C015", "C016"),
        rules=("R009",),
    )
    untrusted = bool(
        security
        & {
            "untrusted_input",
            "untrusted_structured_input",
            "file_access",
            "sql_queries",
            "process_execution",
        }
    )
    add(
        "input_validation",
        applicable=untrusted,
        required=untrusted,
        reason=(
            "Validate untrusted syntax and business semantics at the trusted boundary with "
            "safe framework APIs."
        ),
        claims=("C059", "C068"),
        rules=("R009",),
    )
    user_facing = meaningful_ui or public_web
    add(
        "secure_defaults",
        applicable=user_facing,
        required=user_facing,
        reason=(
            "User-facing systems should default to safe exposure, credentials, permissions, "
            "and framework primitives."
        ),
        claims=("C056", "C068"),
    )
    operational = bool(profile.deployment_topology) and not set(profile.deployment_topology) <= {
        "local_one_user",
        "offline_or_restricted",
    }
    add(
        "observability",
        applicable=operational,
        recommended=operational,
        reason=(
            "Operational signals are proportional to a long-running/public/distributed lifecycle."
        ),
        enforcement=EnforcementLevel.RECOMMENDATION,
        claims=("C028",),
        rules=("R013",),
    )
    messaging = "duplicate_delivery_and_ordering" in distributed
    add(
        "idempotency",
        applicable=messaging,
        required=messaging,
        reason=(
            "At-least-once/event delivery requires explicit duplicate-safe processing and "
            "ordering semantics."
        ),
        claims=("C063",),
        rules=("R012",),
    )
    caching = "cache_freshness_and_invalidation" in distributed
    add(
        "cache_consistency",
        applicable=caching,
        required=caching,
        reason=(
            "A cache requires evidence for freshness, invalidation, capacity, and "
            "local/shared semantics."
        ),
        claims=("C065",),
        rules=("R011",),
    )
    retries = "bounded_transient_retries" in distributed
    add(
        "retry_safety",
        applicable=retries,
        required=retries,
        reason="Retries are bounded, transient-only, timeout-aware, and duplicate-safe.",
        claims=("C027", "C063"),
        rules=("R012",),
    )
    assert tuple(item.name for item in capabilities) == CAPABILITY_VOCABULARY
    return QualityContract(tuple(capabilities), profile.fingerprint)


def apply_check_results(
    contract: QualityContract,
    checks: list[CheckRecord],
) -> QualityContract:
    updated: list[QualityCapability] = []
    for capability in contract.capabilities:
        matching = [record for record in checks if _check_capability(record) == capability.name]
        if not matching:
            updated.append(capability)
            continue
        if any(record.exit_code is None and record.outcome == "failed" for record in matching):
            verification = CapabilityVerification.UNAVAILABLE
            state = CapabilityState.UNAVAILABLE if _is_blocking(capability) else capability.state
        elif any(record.outcome != "passed" for record in matching):
            verification = CapabilityVerification.FAILED
            state = capability.state
        else:
            verification = CapabilityVerification.PASSED
            state = capability.state
        updated.append(replace(capability, state=state, verification=verification))
    return QualityContract(tuple(updated), contract.resolved_fingerprint)


def quality_contract_blockers(contract: QualityContract | None) -> list[str]:
    if contract is None:
        return ["The adaptive quality contract has not been resolved."]
    blockers: list[str] = []
    for capability in contract.capabilities:
        if capability.state is CapabilityState.UNKNOWN and _is_blocking(capability):
            blockers.append(f"Material quality capability remains unknown: {capability.name}")
        elif capability.state is CapabilityState.UNAVAILABLE and _is_blocking(capability):
            blockers.append(f"Required quality capability is unavailable: {capability.name}")
        elif capability.verification is CapabilityVerification.FAILED:
            blockers.append(f"Quality capability failed verification: {capability.name}")
        elif capability.verification is CapabilityVerification.UNAVAILABLE and _is_blocking(
            capability
        ):
            blockers.append(f"Quality capability could not be verified: {capability.name}")
    return blockers


def assess_storage(
    *,
    requested_store: str | None,
    workload: str,
    writer_topology: str,
    storage_location: str,
    read_only: bool = False,
    valuable_data: bool = False,
) -> StorageAssessment:
    store = requested_store.lower() if requested_store else None
    network_share = storage_location.lower() in {"smb", "nfs", "nas", "samba", "network_share"}
    multiple_writers = writer_topology.lower() in {
        "multiple_processes",
        "multiple_machines",
        "concurrent_clients",
    }
    concerns: list[str] = []
    if valuable_data:
        concerns.append("recovery_requirements")
    if store == "duckdb" and network_share and not read_only:
        return StorageAssessment(
            requested_store,
            False,
            (
                "Do not default a native read-write DuckDB database to SMB/NFS/NAS; use local "
                "ownership, a central writer/service, or an organization-supported store."
            ),
            tuple((*concerns, "network_filesystem_write_safety")),
            ("C031", "C032", "C033"),
            ("R016", "R017"),
        )
    if (
        store == "duckdb"
        and workload.lower() in {"analytical", "olap", "file_analytics"}
        and not multiple_writers
    ):
        return StorageAssessment(
            requested_store,
            True,
            (
                "DuckDB is a suitable candidate for this embedded analytical topology; "
                "verify current concurrency and storage semantics."
            ),
            tuple(concerns),
            ("C031", "C032"),
            ("R016",),
        )
    if network_share and read_only and workload.lower() in {"analytical", "olap", "file_analytics"}:
        return StorageAssessment(
            requested_store,
            True if store == "duckdb" else None,
            (
                "Shared read-only analytical input can be suitable; keep the native writable "
                "database on supported storage."
            ),
            tuple(concerns),
            ("C031", "C032"),
            ("R016",),
        )
    if multiple_writers:
        return StorageAssessment(
            requested_store,
            False if store in {"duckdb", "sqlite"} else None,
            (
                "Use safe coordinated ownership or a client/server transactional store "
                "supported by the project; no database brand is selected universally."
            ),
            tuple((*concerns, "concurrent_transactional_writers")),
            ("C033", "C034"),
            ("R017",),
        )
    return StorageAssessment(
        requested_store,
        None,
        (
            "Resolve storage from workload, writer topology, locality, data value, "
            "sensitivity, availability, migration, and existing infrastructure."
        ),
        tuple(concerns),
        ("C029", "C030", "C031", "C034"),
        ("R014", "R015", "R016", "R017"),
    )


def _project_mode(evidence: RepositoryEvidence, request: str) -> ProjectMode:
    existing_verbs = ("fix ", "improve ", "update ", "change ", "refactor ", "migrate ", "repair ")
    substantive_markers = set(evidence.project_markers)
    if evidence.implementation_files or substantive_markers or request.startswith(existing_verbs):
        return ProjectMode.EXISTING
    return ProjectMode.GREENFIELD


def _deployment_topology(request: str, signals: set[str]) -> tuple[str, ...]:
    values: set[str] = set()
    if _has(request, "offline", "air-gapped", "restricted"):
        values.add("offline_or_restricted")
    if _has(request, "public", "anyone online", "internet-facing"):
        values.add("public_service")
    elif _has(request, "company", "team", "internal", "shared") or "shared_or_deployed" in signals:
        values.add("internal_team_service")
    else:
        values.add("local_one_user")
    if _has(request, "microservice", "distributed", "high throughput", "high traffic"):
        values.add("distributed_or_high_throughput")
    return tuple(sorted(values))


def _change_surfaces(request: str, paths: tuple[str, ...], signals: set[str]) -> tuple[str, ...]:
    surfaces: set[str] = set()
    if "user_interface" in signals or any(
        path.endswith((".tsx", ".jsx", ".html", ".css")) for path in paths
    ):
        surfaces.add("web_ui")
    if "persistent_data" in signals:
        surfaces.add("persistent_data")
    if "identity_or_access" in signals:
        surfaces.update(("authentication", "authorization"))
    if _has(request, "api", "endpoint", "rest", "graphql", "openapi"):
        surfaces.add("api")
    if _has(request, "migration", "schema", "database column", "database table") or any(
        "migration" in path for path in paths
    ):
        surfaces.update(("schema_migration", "persistent_data"))
    if _has(request, "dependency", "package", "library") or any(
        path.endswith(("lock", "lock.json", "lock.yaml", "go.sum")) for path in paths
    ):
        surfaces.add("dependencies")
    if _has(request, "publish", "release artifact", "release package", "container image"):
        surfaces.add("release_artifact")
    if _has(request, "performance", "latency", "throughput", "large data", "high traffic"):
        surfaces.add("performance")
    if _has(request, "parser", "parse", "codec"):
        surfaces.add("parser")
    if _has(request, "protocol"):
        surfaces.add("protocol")
    if _has(request, "file", "upload", "filesystem"):
        surfaces.add("filesystem")
    if _has(request, "subprocess", "command execution", "shell"):
        surfaces.add("process_execution")
    if _has(request, "network", "remote service", "http client"):
        surfaces.add("network")
    if _has(request, "payment"):
        surfaces.update(("payment", "critical_journey"))
    if any(path.startswith(".github/workflows/") for path in paths):
        surfaces.add("ci_workflow")
    if any(path.endswith(("readme.md", ".md")) for path in paths):
        surfaces.add("documentation")
    if _has(request, "public api", "public library", "published package", "cli flag", "config key"):
        surfaces.add("public_contract")
    return tuple(sorted(surfaces))


def _security_surfaces(
    evidence: RepositoryEvidence, request: str, changes: tuple[str, ...]
) -> tuple[str, ...]:
    surfaces: set[str] = set()
    change_set = set(changes)
    if _has(request, "public", "internet-facing") and (
        "api" in change_set or evidence.has_user_interface
    ):
        surfaces.add("public_web_or_api")
    if "authentication" in change_set:
        surfaces.add("authentication")
    if "authorization" in change_set:
        surfaces.add("authorization")
    if _has(request, "input", "form", "upload", "parser", "csv", "json"):
        surfaces.add("untrusted_input")
    if "parser" in change_set or "protocol" in change_set:
        surfaces.add("untrusted_structured_input")
    if "filesystem" in change_set:
        surfaces.add("file_access")
    if _has(request, "sql", "query"):
        surfaces.add("sql_queries")
    if "process_execution" in change_set:
        surfaces.add("process_execution")
    if _has(request, "secret", "token", "password", "credential"):
        surfaces.add("secrets")
    if evidence.package_managers:
        surfaces.add("dependencies")
    if _has(request, "private", "medical", "health", "financial", "customer", "employee"):
        surfaces.add("sensitive_persistent_data")
    if _has(request, "multi-tenant", "several users", "many users"):
        surfaces.add("multi_tenant_or_shared_users")
    if "network" in change_set or "api" in change_set:
        surfaces.add("network_clients")
    if evidence.has_user_interface or "web_ui" in change_set:
        surfaces.add("browser_ui")
    if _has(request, "plugin", "extension", "deserialize"):
        surfaces.add("plugins_or_deserialization")
    if evidence.has_ci:
        surfaces.add("ci_cd")
    return tuple(sorted(surfaces))


def _compatibility_surfaces(
    evidence: RepositoryEvidence, request: str, changes: tuple[str, ...]
) -> tuple[str, ...]:
    surfaces: set[str] = set()
    change_set = set(changes)
    if "public_contract" in change_set or _has(
        request, "public export", "public library", "published package"
    ):
        surfaces.add("public_library_exports")
    if "api" in change_set and _has(request, "existing", "change", "update", "remove", "rename"):
        surfaces.add("api_schema_or_behavior")
    if _has(request, "cli", "command", "flag", "exit code", "json output"):
        surfaces.add("cli_contract")
    if _has(request, "config key", "configuration schema", "rename config"):
        surfaces.add("configuration_contract")
    if _has(request, "file format", "serialized", "persisted format"):
        surfaces.add("persisted_format")
    if _has(request, "event schema", "message schema", "queue message"):
        surfaces.add("event_or_message_schema")
    if "schema_migration" in change_set and _has(request, "rolling", "zero downtime", "overlap"):
        surfaces.add("multi_version_database_schema")
    if _has(request, "plugin api", "extension contract"):
        surfaces.add("plugin_or_extension_contract")
    if "python_package" in evidence.release_signals and "public_contract" in change_set:
        surfaces.add("public_library_exports")
    return tuple(sorted(surfaces))


def _supply_chain_surfaces(
    evidence: RepositoryEvidence, changes: tuple[str, ...]
) -> tuple[str, ...]:
    surfaces: set[str] = set()
    if evidence.lockfiles:
        surfaces.add("reproducible_dependency_state")
    if "python_package" in evidence.release_signals:
        surfaces.add("published_package")
    if set(evidence.release_signals) & {"container", "release_workflow"}:
        surfaces.add("container_or_release_artifact")
    if "GitHub Actions" in evidence.ci_providers:
        surfaces.add("github_actions")
    if "dependencies" in changes:
        surfaces.add("dependency_change")
    return tuple(sorted(surfaces))


def _data_concerns(
    evidence: RepositoryEvidence, request: str, changes: tuple[str, ...]
) -> tuple[str, ...]:
    concerns: set[str] = set()
    if evidence.data_signals or "persistent_data" in changes:
        concerns.add("persistent_data")
    if _has(
        request, "source of record", "business critical", "serious business problem", "cannot lose"
    ):
        concerns.add("valuable_durable_data")
    if _has(request, "cache", "disposable", "temporary"):
        concerns.add("disposable_data")
    if _has(request, "analytics", "analytical", "report", "aggregation", "olap", "parquet"):
        concerns.add("analytical_workload")
    if _has(request, "transaction", "inventory", "orders", "edit record", "crud"):
        concerns.add("transactional_workload")
    if _has(request, "several people", "multiple writers", "concurrent writers", "many users"):
        concerns.add("multiple_concurrent_writers")
    if _has(request, "smb", "nfs", "nas", "samba", "network share", "shared folder"):
        concerns.add("network_shared_storage")
    if "schema_migration" in changes:
        concerns.add("migration_required")
    if _has(request, "private", "medical", "financial", "customer", "employee"):
        concerns.add("sensitive_data")
    if _has(request, "unique", "uniqueness", "non-null", "foreign key", "reference invariant"):
        concerns.add("durable_datastore_constraints")
    if _has(request, "atomic write", "multi-step write", "succeed or fail together"):
        concerns.add("transaction_boundary")
    return tuple(sorted(concerns))


def _distributed_concerns(request: str, constraints: set[str]) -> tuple[str, ...]:
    concerns: set[str] = set()
    if _has(request, "microservice"):
        concerns.update(("service_contracts_and_failure_modes", "distributed_observability"))
        if not _has(
            request,
            "independent deployment",
            "independent scaling",
            "team ownership",
            "isolation",
            "high traffic",
            "high throughput",
        ):
            concerns.add("microservices_without_readiness_evidence")
    if (
        _has(request, "queue", "event bus", "kafka", "rabbitmq", "sqs", "at-least-once")
        or "kafka" in constraints
    ):
        concerns.update(
            ("duplicate_delivery_and_ordering", "eventual_consistency", "poison_message_handling")
        )
    if _has(request, "cache", "redis") or "redis" in constraints:
        concerns.add("cache_freshness_and_invalidation")
        if not _has(
            request,
            "latency",
            "throughput",
            "high scale",
            "high traffic",
            "repeated expensive",
            "explicit cache requirement",
        ):
            concerns.add("cache_without_workload_evidence")
    if _has(request, "retry", "transient remote failure"):
        if _has(request, "authentication failure", "validation failure", "configuration error"):
            concerns.add("reject_retry_for_permanent_failure")
        else:
            concerns.add("bounded_transient_retries")
    if _has(request, "transactional outbox", "dual write"):
        concerns.add("transaction_to_event_atomicity")
    return tuple(sorted(concerns))


def _quality_attributes(
    evidence: RepositoryEvidence,
    topology: tuple[str, ...],
    security: tuple[str, ...],
    compatibility: tuple[str, ...],
    data: tuple[str, ...],
    distributed: tuple[str, ...],
    changes: tuple[str, ...],
) -> tuple[str, ...]:
    attributes = {"correctness", "maintainability", "operational_simplicity"}
    if security:
        attributes.add("security")
    if evidence.has_user_interface or "web_ui" in changes:
        attributes.update(("accessibility", "usability"))
    if compatibility:
        attributes.add("compatibility")
    if "performance" in changes or "distributed_or_high_throughput" in topology:
        attributes.add("performance")
    if distributed or "public_service" in topology:
        attributes.add("reliability")
    if "valuable_durable_data" in data:
        attributes.add("recoverability")
    if "offline_or_restricted" in topology:
        attributes.add("portability")
    return tuple(sorted(attributes))


def _engineering_decisions(
    mode: ProjectMode,
    evidence: RepositoryEvidence,
    request: str,
    constraints: set[str],
    security: tuple[str, ...],
    compatibility: tuple[str, ...],
    data: tuple[str, ...],
    distributed: tuple[str, ...],
) -> tuple[EngineeringDecision, ...]:
    decisions = [
        EngineeringDecision(
            "architecture",
            "least_complex_satisfying_profile",
            (
                "Complexity is justified by detected qualities and constraints; component "
                "count is not a quality score."
            ),
            EnforcementLevel.REVIEWER_SIGNAL,
            ("C001", "C002", "C003"),
            ("R002", "R003", "R004"),
        )
    ]
    if _has(
        request,
        "universal complexity score",
        "universal coverage threshold",
        "one database for every project",
        "one framework for every project",
    ):
        decisions.append(
            EngineeringDecision(
                "unsupported_universal_policy",
                "defer_without_project_evidence",
                (
                    "A context-free numeric or technology mandate is not supported; an explicit "
                    "project or organization policy remains authoritative when present."
                ),
                EnforcementLevel.DEFERRED,
                ("C008", "C013", "C039"),
                ("R008", "R021"),
            )
        )
    if mode is ProjectMode.EXISTING:
        decisions.append(
            EngineeringDecision(
                "existing_project_adoption",
                "preserve_native_toolchain",
                (
                    "Repository instructions, scripts, wrappers, lockfiles, and existing "
                    "policy outrank Koda preference."
                ),
                EnforcementLevel.PROJECT_POLICY,
                ("C038", "C039", "C045"),
                ("R001",),
            )
        )
    if constraints:
        decisions.append(
            EngineeringDecision(
                "expert_constraints",
                "honor_unless_concrete_conflict",
                (
                    "Explicit technical direction is a requirement unless unsafe, "
                    "contradictory, unavailable, or impossible."
                ),
                EnforcementLevel.CONTEXT_REQUIRED,
                ("C037",),
                ("R025",),
            )
        )
    if evidence.monorepo_tools:
        decisions.append(
            EngineeringDecision(
                "monorepo",
                "reuse_native_project_graph",
                (
                    "Use existing affected/project tooling and widen for shared configuration "
                    "when necessary."
                ),
                EnforcementLevel.PROJECT_POLICY,
                ("C035",),
                ("R022",),
            )
        )
    if security:
        decisions.append(
            EngineeringDecision(
                "security",
                "threat_surface_driven",
                (
                    "Security techniques follow actual exposure, inputs, data, dependencies, "
                    "and privileges."
                ),
                EnforcementLevel.CONTEXT_REQUIRED,
                ("C015", "C016", "C056", "C068"),
                ("R009",),
            )
        )
    if compatibility:
        decisions.append(
            EngineeringDecision(
                "compatibility",
                "explicit_consumer_impact_review",
                "A cleaner implementation is not sufficient reason to break stable consumers.",
                EnforcementLevel.CONTEXT_REQUIRED,
                ("C046", "C047", "C048", "C049"),
            )
        )
    if "network_shared_storage" in data:
        decisions.append(
            EngineeringDecision(
                "storage",
                "reject_shared_native_read_write_file_database_default",
                (
                    "Writer topology and filesystem semantics must be resolved before "
                    "choosing DuckDB/SQLite or a central service/store."
                ),
                EnforcementLevel.CONTEXT_REQUIRED,
                ("C031", "C032", "C033", "C034"),
                ("R016", "R017"),
            )
        )
    if distributed:
        decisions.append(
            EngineeringDecision(
                "distributed_systems",
                "accept_with_semantic_costs",
                (
                    "Queues, caches, retries, and service boundaries carry consistency, "
                    "idempotency, contract, and operational obligations."
                ),
                EnforcementLevel.CONTEXT_REQUIRED,
                ("C027", "C063", "C064", "C065"),
                ("R011", "R012", "R013"),
            )
        )
    if "microservices_without_readiness_evidence" in distributed:
        decisions.append(
            EngineeringDecision(
                "microservices",
                "challenge_missing_readiness_evidence",
                (
                    "Respect an explicit architecture requirement, while asking for the "
                    "deployment, scale, isolation, or ownership benefit that justifies it."
                ),
                EnforcementLevel.REVIEWER_SIGNAL,
                ("C064",),
            )
        )
    if "cache_without_workload_evidence" in distributed:
        decisions.append(
            EngineeringDecision(
                "cache",
                "challenge_missing_workload_evidence",
                "Do not add cache complexity without a concrete repeated-cost or latency need.",
                EnforcementLevel.REVIEWER_SIGNAL,
                ("C026", "C065"),
                ("R011",),
            )
        )
    if "reject_retry_for_permanent_failure" in distributed:
        decisions.append(
            EngineeringDecision(
                "retries",
                "reject_permanent_failure_retry",
                "Authentication, validation, and configuration failures are not transient.",
                EnforcementLevel.CONTEXT_REQUIRED,
                ("C027",),
                ("R012",),
            )
        )
    if "no_hosted_git_remote_detected" in evidence.environment_constraints:
        decisions.append(
            EngineeringDecision(
                "delivery_environment",
                "local_deterministic_verification_is_valid",
                "No hosted remote or CI service is required for a strong local contract.",
                EnforcementLevel.RECOMMENDATION,
                ("C021", "C042"),
                ("R028",),
            )
        )
    return tuple(decisions)


def _ecosystems(evidence: RepositoryEvidence) -> tuple[EcosystemProfile, ...]:
    profiles: list[EcosystemProfile] = []
    markers = set(evidence.project_markers)
    commands = evidence.lifecycle_commands

    def add(
        name: str, detected: bool, marker_names: tuple[str, ...], prefixes: tuple[str, ...]
    ) -> None:
        if not detected:
            return
        native = tuple(item for item in commands if any(prefix in item for prefix in prefixes))
        profiles.append(
            EcosystemProfile(
                name,
                EcosystemSupport.NATIVE_LIFECYCLE if native else EcosystemSupport.DETECTION_ONLY,
                tuple(item for item in marker_names if item in markers),
                native,
            )
        )

    languages = set(evidence.languages)
    add(
        "Python",
        "Python" in languages or "pyproject.toml" in markers,
        ("pyproject.toml", "setup.py", "setup.cfg"),
        ("python ", "pytest", "ruff", "mypy", "uv "),
    )
    add(
        "JavaScript/TypeScript",
        bool(languages & {"JavaScript", "TypeScript"}) or "package.json" in markers,
        ("package.json",),
        ("npm ", "pnpm ", "yarn ", "bun "),
    )
    add("Maven/Java", "pom.xml" in markers, ("pom.xml",), ("mvn",))
    add(
        "Gradle/JVM",
        bool(markers & {"build.gradle", "build.gradle.kts"}),
        ("build.gradle", "build.gradle.kts"),
        ("gradle",),
    )
    add(".NET", "C#" in languages, (), ("dotnet",))
    add("Rust/Cargo", "cargo.toml" in markers, ("cargo.toml",), ("cargo ",))
    add("Go", "go.mod" in markers or "go.work" in markers, ("go.mod", "go.work"), ("go ",))
    for tool in evidence.monorepo_tools:
        profiles.append(
            EcosystemProfile(
                tool, EcosystemSupport.NATIVE_LIFECYCLE, (), ("reuse native graph/affected tasks",)
            )
        )
    if evidence.has_ci:
        profiles.append(
            EcosystemProfile(
                "GitHub Actions", EcosystemSupport.DETECTION_ONLY, (".github/workflows",), ()
            )
        )
    if "Sonar" in evidence.analysis_tools:
        profiles.append(
            EcosystemProfile(
                "Sonar", EcosystemSupport.DETECTION_ONLY, ("sonar-project.properties",), ()
            )
        )
    return tuple(profiles)


def _mechanisms(evidence: RepositoryEvidence) -> dict[str, tuple[str, ...]]:
    grouped: dict[str, list[str]] = {}
    for item in evidence.lifecycle_commands:
        capability, separator, command = item.partition(":")
        if separator and capability in CAPABILITY_VOCABULARY:
            grouped.setdefault(capability, []).append(command)
    if evidence.lockfiles:
        grouped["dependency_reproducibility"] = list(evidence.lockfiles)
    return {key: tuple(sorted(values)) for key, values in grouped.items()}


def _capability_evidence(name: str, profile: EngineeringProfile) -> set[str]:
    evidence: set[str] = set()
    if name in {"accessibility", "e2e_tests"} and "web_ui" in profile.change_surfaces:
        evidence.add("change:web_ui")
    if name in {"migration_data_integrity", "recovery_backup"}:
        evidence.update(f"data:{item}" for item in profile.data_concerns)
    if name in {"compatibility"}:
        evidence.update(f"contract:{item}" for item in profile.compatibility_surfaces)
    if name in {
        "static_security",
        "web_security",
        "authorization",
        "input_validation",
        "secure_defaults",
    }:
        evidence.update(f"security:{item}" for item in profile.security_surfaces)
    if name in {
        "ci_security",
        "component_inventory",
        "build_provenance",
        "artifact_integrity",
        "dependency_reproducibility",
    }:
        evidence.update(f"supply_chain:{item}" for item in profile.supply_chain_surfaces)
    if name in {"idempotency", "cache_consistency", "retry_safety", "observability"}:
        evidence.update(f"distributed:{item}" for item in profile.distributed_concerns)
    return evidence


def _check_capability(record: CheckRecord) -> str:
    joined = f"{record.name} {' '.join(record.argv)}".lower()
    mapping = (
        ("format", "format"),
        ("lint", "lint"),
        ("mypy", "type_compile"),
        ("type", "type_compile"),
        ("pytest", "unit_tests"),
        ("test", "unit_tests"),
        ("bandit", "static_security"),
        ("secret", "secret_scan"),
        ("audit", "dependency_analysis"),
        ("package", "build_package"),
        ("build", "build_package"),
    )
    return next((capability for marker, capability in mapping if marker in joined), "ci_mirror")


def _is_blocking(capability: QualityCapability) -> bool:
    return capability.enforcement in {
        EnforcementLevel.HARD_INVARIANT,
        EnforcementLevel.PROJECT_POLICY,
        EnforcementLevel.CONTEXT_REQUIRED,
    }


def _profile_languages(profile: EngineeringProfile) -> tuple[str, ...]:
    names = {item.name for item in profile.ecosystems}
    languages: set[str] = set()
    if "Python" in names:
        languages.add("Python")
    if "JavaScript/TypeScript" in names:
        languages.add("TypeScript")
    if "Maven/Java" in names or "Gradle/JVM" in names:
        languages.add("Java")
    if ".NET" in names:
        languages.add("C#")
    if "Rust/Cargo" in names:
        languages.add("Rust")
    if "Go" in names:
        languages.add("Go")
    return tuple(languages)


def _profile_fingerprint(
    evidence: RepositoryEvidence,
    understanding: RequirementUnderstanding,
    changed_paths: tuple[str, ...],
    answers: tuple[MissionAnswer, ...],
) -> str:
    payload = {
        "repository": {
            key: getattr(evidence, key)
            for key in (
                "languages",
                "frameworks",
                "has_tests",
                "has_ci",
                "has_user_interface",
                "data_signals",
                "implementation_files",
                "project_markers",
                "package_managers",
                "lockfiles",
                "lifecycle_commands",
                "monorepo_tools",
                "migration_tools",
                "analysis_tools",
                "ci_providers",
                "release_signals",
                "environment_constraints",
            )
        },
        "request": understanding.requested_outcome,
        "constraints": understanding.explicit_technical_constraints,
        "signals": understanding.capability_signals,
        "changed_paths": changed_paths,
        "answers": [(item.question, item.answer) for item in answers],
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


def _has(value: str, *phrases: str) -> bool:
    return any(phrase in value for phrase in phrases)
