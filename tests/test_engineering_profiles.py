from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from koda_code.discovery import inspect_repository
from koda_code.engineering import (
    apply_check_results,
    assess_storage,
    derive_engineering_profile,
    quality_contract_blockers,
    resolve_quality_contract,
)
from koda_code.models import (
    CapabilityState,
    CapabilityVerification,
    CheckRecord,
    EcosystemSupport,
    EnforcementLevel,
    ProjectMode,
    RequirementUnderstanding,
)
from koda_code.quality import run_mission_checks
from koda_code.requirements import understand_request
from koda_code.workflow import begin_mission


def _profile(repository: Path, request: str):  # type: ignore[no-untyped-def]
    evidence = inspect_repository(repository)
    understanding = understand_request(request, evidence)
    profile = derive_engineering_profile(evidence, understanding)
    return evidence, profile, resolve_quality_contract(profile, evidence)


def _capability(contract, name: str):  # type: ignore[no-untyped-def]
    return next(item for item in contract.capabilities if item.name == name)


def test_existing_python_project_preserves_native_quality_policy(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.py").write_text("value = 1\n", encoding="utf-8")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_app.py").write_text(
        "def test_app(): assert True\n", encoding="utf-8"
    )
    (tmp_path / "pyproject.toml").write_text(
        "[project]\nname='sample'\nversion='1'\n[build-system]\nrequires=[]\n"
        "[tool.ruff]\n[tool.mypy]\n[tool.pytest.ini_options]\n",
        encoding="utf-8",
    )
    (tmp_path / "uv.lock").write_text("version = 1\n", encoding="utf-8")
    (tmp_path / "koda-code.toml").write_text(
        "[[quality.checks]]\nname='lint'\nargv=['python','-m','ruff','check','src']\n"
        "[[quality.checks]]\nname='types'\nargv=['python','-m','mypy','src']\n"
        "[[quality.checks]]\nname='tests'\nargv=['python','-m','pytest']\n",
        encoding="utf-8",
    )
    evidence, profile, contract = _profile(tmp_path, "Add a report")

    assert profile.project_mode is ProjectMode.EXISTING
    assert "uv" in evidence.package_managers
    assert "uv.lock" in profile.lockfiles
    assert _capability(contract, "lint").state is CapabilityState.EXISTING
    assert _capability(contract, "type_compile").state is CapabilityState.EXISTING
    assert _capability(contract, "unit_tests").state is CapabilityState.EXISTING
    reproducibility = _capability(contract, "dependency_reproducibility")
    assert reproducibility.state is CapabilityState.EXISTING
    assert reproducibility.mechanisms == ("uv.lock",)
    assert _capability(contract, "component_inventory").state is CapabilityState.NOT_APPLICABLE
    assert all("migrate" not in decision.outcome for decision in profile.decisions)


def test_typescript_web_app_uses_package_scripts_and_requires_accessibility(
    tmp_path: Path,
) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "page.tsx").write_text(
        "export const Page = () => <form />\n", encoding="utf-8"
    )
    (tmp_path / "package.json").write_text(
        '{"packageManager":"pnpm@10","scripts":{"test":"vitest","lint":"eslint .",'
        '"typecheck":"tsc --noEmit","build":"vite build"},'
        '"dependencies":{"react":"1","vite":"1"}}',
        encoding="utf-8",
    )
    (tmp_path / "pnpm-lock.yaml").write_text("lockfileVersion: '9'\n", encoding="utf-8")
    (tmp_path / "tsconfig.json").write_text("{}\n", encoding="utf-8")
    evidence, profile, contract = _profile(tmp_path, "Change the checkout form UI")

    assert evidence.package_managers == ("pnpm",)
    assert {"React", "Vite"} <= set(evidence.frameworks)
    assert _capability(contract, "type_compile").state is CapabilityState.EXISTING
    assert _capability(contract, "build_package").state is CapabilityState.EXISTING
    accessibility = _capability(contract, "accessibility")
    assert accessibility.state is CapabilityState.REQUIRED
    assert accessibility.enforcement is EnforcementLevel.CONTEXT_REQUIRED
    assert "accessibility" in profile.quality_attributes


def test_maven_go_and_monorepo_support_levels_are_explicit(tmp_path: Path) -> None:
    maven = tmp_path / "maven"
    maven.mkdir()
    (maven / "pom.xml").write_text("<project />\n", encoding="utf-8")
    (maven / "App.java").write_text("class App {}\n", encoding="utf-8")
    _, maven_profile, _ = _profile(maven, "Improve the service")
    maven_support = next(item for item in maven_profile.ecosystems if item.name == "Maven/Java")
    assert maven_support.support is EcosystemSupport.NATIVE_LIFECYCLE
    assert any("mvn test" in command for command in maven_support.commands)

    go = tmp_path / "go"
    go.mkdir()
    (go / "go.mod").write_text("module example.invalid/app\n", encoding="utf-8")
    (go / "main.go").write_text("package main\n", encoding="utf-8")
    _, go_profile, _ = _profile(go, "Improve the command")
    assert (
        next(item for item in go_profile.ecosystems if item.name == "Go").support
        is EcosystemSupport.NATIVE_LIFECYCLE
    )

    monorepo = tmp_path / "monorepo"
    monorepo.mkdir()
    (monorepo / "package.json").write_text(
        '{"workspaces":["apps/*"],"devDependencies":{"nx":"1"}}', encoding="utf-8"
    )
    (monorepo / "nx.json").write_text("{}\n", encoding="utf-8")
    _, mono_profile, _ = _profile(monorepo, "Change a shared package")
    assert mono_profile.monorepo_tools == ("JavaScript workspaces", "Nx")
    decision = next(item for item in mono_profile.decisions if item.topic == "monorepo")
    assert decision.outcome == "reuse_native_project_graph"
    assert "R022" in decision.rule_ids


def test_greenfield_questions_are_progressive_and_product_worded(tmp_path: Path) -> None:
    evidence = inspect_repository(tmp_path)
    personal = understand_request("Build a personal offline workout tracker", evidence)
    assert personal.product_questions == ()

    shared = understand_request("Build a company inventory tracking page", evidence)
    assert len(shared.product_questions) == 2
    assert any(
        "Where should the shared information live" in item for item in shared.product_questions
    )
    assert any("several people edit" in item for item in shared.product_questions)
    assert not any(
        "PostgreSQL" in item or "optimistic" in item for item in shared.product_questions
    )


def test_negative_contract_does_not_overengineer_a_tiny_local_script(tmp_path: Path) -> None:
    (tmp_path / "tool.py").write_text("print('ok')\n", encoding="utf-8")
    evidence, profile, contract = _profile(tmp_path, "Improve the local script output")

    assert profile.deployment_topology == ("local_one_user",)
    assert "Docker" not in evidence.frameworks
    assert "Sonar" not in evidence.analysis_tools
    assert _capability(contract, "accessibility").state is CapabilityState.NOT_APPLICABLE
    assert _capability(contract, "migration_data_integrity").state is CapabilityState.NOT_APPLICABLE
    assert _capability(contract, "compatibility").state is CapabilityState.NOT_APPLICABLE
    assert _capability(contract, "idempotency").state is CapabilityState.NOT_APPLICABLE
    assert _capability(contract, "performance_load").state is CapabilityState.NOT_APPLICABLE
    assert _capability(contract, "observability").state is CapabilityState.NOT_APPLICABLE
    assert _capability(contract, "component_inventory").state is CapabilityState.NOT_APPLICABLE
    assert quality_contract_blockers(contract) == []


def test_public_contract_migration_and_distributed_triggers_are_contextual(
    tmp_path: Path,
) -> None:
    (tmp_path / "service.py").write_text("def public(): return 1\n", encoding="utf-8")
    _, api_profile, api_contract = _profile(
        tmp_path,
        "Change an existing public API JSON output and database schema migration",
    )
    assert "api_schema_or_behavior" in api_profile.compatibility_surfaces
    assert _capability(api_contract, "compatibility").state is CapabilityState.REQUIRED
    assert _capability(api_contract, "migration_data_integrity").state is CapabilityState.REQUIRED

    _, distributed_profile, distributed_contract = _profile(
        tmp_path,
        (
            "Use microservices with an at-least-once event queue, Redis cache, and retry "
            "transient remote failures"
        ),
    )
    assert "service_contracts_and_failure_modes" in distributed_profile.distributed_concerns
    assert _capability(distributed_contract, "idempotency").state is CapabilityState.REQUIRED
    assert _capability(distributed_contract, "cache_consistency").state is CapabilityState.REQUIRED
    assert _capability(distributed_contract, "retry_safety").state is CapabilityState.REQUIRED
    assert any(
        item.outcome == "accept_with_semantic_costs" for item in distributed_profile.decisions
    )


@pytest.mark.parametrize(
    ("mission_request", "surface"),
    [
        ("Change the existing CLI flag and JSON output", "cli_contract"),
        ("Rename an existing configuration schema key", "configuration_contract"),
        ("Change the persisted file format", "persisted_format"),
        ("Change the event schema consumed by another service", "event_or_message_schema"),
        (
            "Change a rolling deployment database schema with version overlap",
            "multi_version_database_schema",
        ),
    ],
)
def test_compatibility_surfaces_trigger_only_from_contract_evidence(
    tmp_path: Path, mission_request: str, surface: str
) -> None:
    (tmp_path / "app.py").write_text("value = 1\n", encoding="utf-8")
    _, profile, contract = _profile(tmp_path, mission_request)
    assert surface in profile.compatibility_surfaces
    assert _capability(contract, "compatibility").state is CapabilityState.REQUIRED


def test_data_constraints_and_atomic_writes_trigger_integrity_capability(tmp_path: Path) -> None:
    (tmp_path / "app.py").write_text("value = 1\n", encoding="utf-8")
    _, profile, contract = _profile(
        tmp_path,
        "Add a uniqueness invariant and a multi-step write that must succeed or fail together",
    )
    assert "durable_datastore_constraints" in profile.data_concerns
    assert "transaction_boundary" in profile.data_concerns
    assert _capability(contract, "migration_data_integrity").state is CapabilityState.REQUIRED


def test_distributed_patterns_are_challenged_only_when_evidence_is_missing(
    tmp_path: Path,
) -> None:
    (tmp_path / "app.py").write_text("value = 1\n", encoding="utf-8")
    _, tiny_profile, _ = _profile(tmp_path, "Split this tiny app into microservices and add cache")
    outcomes = {item.outcome for item in tiny_profile.decisions}
    assert "challenge_missing_readiness_evidence" in outcomes
    assert "challenge_missing_workload_evidence" in outcomes

    _, scale_profile, scale_contract = _profile(
        tmp_path,
        (
            "Use microservices for independent deployment and an explicit cache requirement "
            "for high traffic"
        ),
    )
    scale_outcomes = {item.outcome for item in scale_profile.decisions}
    assert "challenge_missing_readiness_evidence" not in scale_outcomes
    assert "challenge_missing_workload_evidence" not in scale_outcomes
    assert _capability(scale_contract, "cache_consistency").state is CapabilityState.REQUIRED

    _, retry_profile, retry_contract = _profile(
        tmp_path,
        "Retry a permanent authentication failure",
    )
    assert any(item.outcome == "reject_permanent_failure_retry" for item in retry_profile.decisions)
    assert _capability(retry_contract, "retry_safety").state is CapabilityState.NOT_APPLICABLE


def test_storage_resolver_guards_network_shares_without_forcing_a_database() -> None:
    rejected = assess_storage(
        requested_store="DuckDB",
        workload="analytical",
        writer_topology="multiple_machines",
        storage_location="SMB",
    )
    assert rejected.suitable is False
    assert "R016" in rejected.rule_ids

    local = assess_storage(
        requested_store="DuckDB",
        workload="analytical",
        writer_topology="one_process",
        storage_location="local",
    )
    assert local.suitable is True

    shared_read_only = assess_storage(
        requested_store="DuckDB",
        workload="analytical",
        writer_topology="multiple_machines",
        storage_location="NFS",
        read_only=True,
    )
    assert shared_read_only.suitable is True

    writers = assess_storage(
        requested_store=None,
        workload="transactional",
        writer_topology="concurrent_clients",
        storage_location="local",
    )
    assert writers.suitable is None
    assert "client/server" in writers.recommendation


def test_unavailable_capability_is_not_converted_to_pass(tmp_path: Path) -> None:
    (tmp_path / "tool.py").write_text("print('ok')\n", encoding="utf-8")
    (tmp_path / "koda-code.toml").write_text(
        "[[quality.checks]]\nname='tests'\nargv=['python','-m','pytest']\n",
        encoding="utf-8",
    )
    _, _, contract = _profile(tmp_path, "Change behavior")
    unavailable = CheckRecord("tests", ["python", "-m", "pytest"], "failed", None, 0, "missing")
    updated = apply_check_results(contract, [unavailable])
    tests = _capability(updated, "unit_tests")
    assert tests.state is CapabilityState.UNAVAILABLE
    assert tests.verification is CapabilityVerification.UNAVAILABLE
    assert quality_contract_blockers(updated)


def test_failed_check_is_attributed_against_isolated_baseline(git_repo: Path) -> None:
    (git_repo / "app.py").write_text("value = 1\n", encoding="utf-8")
    (git_repo / "koda-code.toml").write_text(
        "[[quality.checks]]\nname='tests'\n"
        "argv=['python','-c','from pathlib import Path; "
        'raise SystemExit(0 if Path("app.py").read_text().strip() == "value = 1" else 1)\']\n',
        encoding="utf-8",
    )
    subprocess.run(["git", "add", "app.py", "koda-code.toml"], cwd=git_repo, check=True)
    subprocess.run(["git", "commit", "-m", "Add passing baseline"], cwd=git_repo, check=True)
    mission = begin_mission("Change app behavior", git_repo, prepare_worktree=True)
    worktree = Path(mission.worktree or "")
    (worktree / "app.py").write_text("value = 2\n", encoding="utf-8")

    records = run_mission_checks(mission, git_repo)

    assert records[0].outcome == "failed"
    assert records[0].baseline_outcome == "passed"
    assert records[0].attribution == "introduced"
    assert mission.baseline_checks[0].outcome == "passed"


def test_preexisting_failed_check_is_reported_without_disabling_gate(git_repo: Path) -> None:
    (git_repo / "app.py").write_text("value = 2\n", encoding="utf-8")
    (git_repo / "koda-code.toml").write_text(
        "[[quality.checks]]\nname='tests'\n"
        "argv=['python','-c','from pathlib import Path; "
        'raise SystemExit(0 if Path("app.py").read_text().strip() == "value = 1" else 1)\']\n',
        encoding="utf-8",
    )
    subprocess.run(["git", "add", "app.py", "koda-code.toml"], cwd=git_repo, check=True)
    subprocess.run(["git", "commit", "-m", "Add failing baseline"], cwd=git_repo, check=True)
    mission = begin_mission("Add a separate note", git_repo, prepare_worktree=True)
    worktree = Path(mission.worktree or "")
    (worktree / "note.txt").write_text("changed\n", encoding="utf-8")

    records = run_mission_checks(mission, git_repo)

    assert records[0].outcome == "failed"
    assert records[0].baseline_outcome == "failed"
    assert records[0].attribution == "preexisting"
    assert quality_contract_blockers(mission.quality_contract)


def test_internal_helper_refactor_does_not_invent_public_compatibility(tmp_path: Path) -> None:
    (tmp_path / "internal.py").write_text("def _helper(value): return value\n", encoding="utf-8")
    evidence = inspect_repository(tmp_path)
    understanding = RequirementUnderstanding("Refactor an internal private helper", (), (), ())
    profile = derive_engineering_profile(
        evidence,
        understanding,
        changed_paths=("internal.py",),
    )
    contract = resolve_quality_contract(profile, evidence)
    assert profile.compatibility_surfaces == ()
    assert _capability(contract, "compatibility").state is CapabilityState.NOT_APPLICABLE
    assert not hasattr(profile, "complexity_score")
    assert not hasattr(profile, "coverage_threshold")


def test_unsupported_universal_policy_is_deferred_without_overriding_project_policy(
    tmp_path: Path,
) -> None:
    (tmp_path / "app.py").write_text("value = 1\n", encoding="utf-8")
    _, profile, _ = _profile(
        tmp_path,
        "Apply one universal complexity score to every project",
    )

    decision = next(
        item for item in profile.decisions if item.topic == "unsupported_universal_policy"
    )
    assert decision.outcome == "defer_without_project_evidence"
    assert decision.enforcement is EnforcementLevel.DEFERRED
    assert "R008" in decision.rule_ids
