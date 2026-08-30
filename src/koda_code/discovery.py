from __future__ import annotations

import json
import tomllib
from collections import Counter
from pathlib import Path
from typing import Any

from .models import RepositoryEvidence
from .repository import git, repository_root

SKIP_DIRECTORIES = {
    ".git",
    ".venv",
    "node_modules",
    "dist",
    "build",
    "coverage",
    "__pycache__",
}
LANGUAGE_SUFFIXES = {
    ".py": "Python",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".go": "Go",
    ".rs": "Rust",
    ".java": "Java",
    ".kt": "Kotlin",
    ".rb": "Ruby",
    ".php": "PHP",
    ".cs": "C#",
    ".swift": "Swift",
}
FRAMEWORK_MARKERS = {
    "next.config.js": "Next.js",
    "next.config.mjs": "Next.js",
    "next.config.ts": "Next.js",
    "manage.py": "Django",
    "vite.config.ts": "Vite",
    "vite.config.js": "Vite",
    "angular.json": "Angular",
    "cargo.toml": "Cargo",
    "go.mod": "Go modules",
}
PROJECT_MARKERS = {
    "pyproject.toml",
    "setup.py",
    "setup.cfg",
    "package.json",
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    "settings.gradle",
    "settings.gradle.kts",
    "cargo.toml",
    "go.mod",
    "go.work",
    "global.json",
    "nx.json",
    "turbo.json",
    "koda-code.toml",
}
LOCKFILES = {
    "uv.lock": "uv",
    "poetry.lock": "Poetry",
    "pdm.lock": "PDM",
    "pylock.toml": "Python lock",
    "requirements.lock": "Python requirements lock",
    "package-lock.json": "npm",
    "npm-shrinkwrap.json": "npm",
    "pnpm-lock.yaml": "pnpm",
    "yarn.lock": "Yarn",
    "bun.lock": "Bun",
    "bun.lockb": "Bun",
    "cargo.lock": "Cargo",
    "go.sum": "Go modules",
    "packages.lock.json": ".NET",
}
DATA_MARKERS = {
    "duckdb": "DuckDB",
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "sqlite": "SQLite",
    "prisma": "Prisma",
    "parquet": "Parquet",
    "dbt_project.yml": "dbt",
}
SCRIPT_CAPABILITIES = {
    "format": "format",
    "lint": "lint",
    "typecheck": "type_compile",
    "type-check": "type_compile",
    "test": "unit_tests",
    "test:unit": "unit_tests",
    "test:integration": "integration_tests",
    "test:e2e": "e2e_tests",
    "build": "build_package",
    "check": "ci_mirror",
}
MAX_CONFIG_BYTES = 262_144


def inspect_repository(path: Path, *, max_files: int = 5_000) -> RepositoryEvidence:
    root = repository_root(path)
    counts: Counter[str] = Counter()
    names: set[str] = set()
    paths: list[str] = []
    inspected = 0
    implementation_files = 0

    for candidate in root.rglob("*"):
        relative_parts = candidate.relative_to(root).parts
        if any(part in SKIP_DIRECTORIES for part in relative_parts):
            continue
        if not candidate.is_file():
            continue
        inspected += 1
        name = candidate.name.lower()
        names.add(name)
        relative = candidate.relative_to(root).as_posix().lower()
        paths.append(relative)
        language = LANGUAGE_SUFFIXES.get(candidate.suffix.lower())
        if language:
            counts[language] += 1
            implementation_files += 1
        if inspected >= max_files:
            break

    frameworks = {value for marker, value in FRAMEWORK_MARKERS.items() if marker in names}
    package_managers = {manager for lock, manager in LOCKFILES.items() if lock in names}
    lockfiles = {name for name in names if name in LOCKFILES}
    project_markers = {name for name in names if name in PROJECT_MARKERS}
    lifecycle_commands: set[str] = set()
    monorepo_tools: set[str] = set()
    migration_tools: set[str] = set()
    analysis_tools: set[str] = set()
    release_signals: set[str] = set()

    package_data = _read_json(root / "package.json")
    if package_data:
        _inspect_package_json(
            package_data,
            package_managers,
            frameworks,
            lifecycle_commands,
            monorepo_tools,
        )
    pyproject = _read_toml(root / "pyproject.toml")
    if pyproject:
        _inspect_pyproject(pyproject, package_managers, analysis_tools, release_signals)
    _inspect_native_lifecycles(root, names, lifecycle_commands, package_managers)
    _inspect_koda_contract(root, lifecycle_commands, analysis_tools)

    lowered_names = "\n".join(paths)
    data_signals = {label for marker, label in DATA_MARKERS.items() if marker in lowered_names}
    if "nx.json" in names:
        monorepo_tools.add("Nx")
    if "turbo.json" in names:
        monorepo_tools.add("Turborepo")
    if any(name in names for name in ("pnpm-workspace.yaml", "lerna.json")):
        monorepo_tools.add("JavaScript workspaces")
    if isinstance(package_data.get("workspaces"), (list, dict)):
        monorepo_tools.add("JavaScript workspaces")

    if "alembic.ini" in names or "alembic/" in lowered_names:
        migration_tools.add("Alembic")
    if "prisma/" in lowered_names:
        migration_tools.add("Prisma")
    if "flyway" in lowered_names:
        migration_tools.add("Flyway")
    if "liquibase" in lowered_names:
        migration_tools.add("Liquibase")
    if "/migrations/" in f"/{lowered_names}" or lowered_names.startswith("migrations/"):
        migration_tools.add("Repository migrations")

    has_ui = any(
        part in lowered_names
        for part in ("src/app/", "src/pages/", "templates/", ".tsx", ".jsx", ".html")
    )
    ci_providers = (
        ("GitHub Actions",) if any(part.startswith(".github/workflows/") for part in paths) else ()
    )
    if "sonar-project.properties" in names or "sonar" in lowered_names:
        analysis_tools.add("Sonar")
    if any(name.startswith("dockerfile") for name in names):
        release_signals.add("container")
    if any(path.startswith(("terraform/", "infra/", "deploy/")) for path in paths):
        release_signals.add("infrastructure_as_code")
    if any(path.startswith(".github/workflows/") and "release" in path for path in paths):
        release_signals.add("release_workflow")

    notes: list[str] = []
    if inspected >= max_files:
        notes.append(f"Inspection stopped after {max_files} files to remain bounded.")
    if not counts:
        notes.append("No established implementation language was detected.")
    remote = git(root, "remote", check=False).stdout.strip()
    environment_constraints = () if remote else ("no_hosted_git_remote_detected",)

    return RepositoryEvidence(
        root=str(root),
        is_git_repository=git(root, "rev-parse", "--is-inside-work-tree", check=False).returncode
        == 0,
        languages=tuple(name for name, _ in counts.most_common()),
        frameworks=tuple(sorted(frameworks)),
        has_tests=any("test" in part.split("/")[-1].lower() for part in paths),
        has_ci=bool(ci_providers),
        has_user_interface=has_ui,
        data_signals=tuple(sorted(data_signals)),
        inspected_files=inspected,
        notes=tuple(notes),
        implementation_files=implementation_files,
        project_markers=tuple(sorted(project_markers)),
        package_managers=tuple(sorted(package_managers)),
        lockfiles=tuple(sorted(lockfiles)),
        lifecycle_commands=tuple(sorted(lifecycle_commands)),
        monorepo_tools=tuple(sorted(monorepo_tools)),
        migration_tools=tuple(sorted(migration_tools)),
        analysis_tools=tuple(sorted(analysis_tools)),
        ci_providers=ci_providers,
        release_signals=tuple(sorted(release_signals)),
        environment_constraints=environment_constraints,
    )


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file() or path.stat().st_size > MAX_CONFIG_BYTES:
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _read_toml(path: Path) -> dict[str, Any]:
    if not path.is_file() or path.stat().st_size > MAX_CONFIG_BYTES:
        return {}
    try:
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError):
        return {}


def _inspect_package_json(
    data: dict[str, Any],
    package_managers: set[str],
    frameworks: set[str],
    lifecycle_commands: set[str],
    monorepo_tools: set[str],
) -> None:
    manager = data.get("packageManager")
    if isinstance(manager, str) and manager:
        package_managers.add(manager.split("@", 1)[0])
    dependencies: dict[str, Any] = {}
    for key in ("dependencies", "devDependencies", "peerDependencies"):
        value = data.get(key)
        if isinstance(value, dict):
            dependencies.update(value)
    framework_packages = {
        "next": "Next.js",
        "react": "React",
        "vue": "Vue",
        "svelte": "Svelte",
        "@angular/core": "Angular",
        "vite": "Vite",
    }
    frameworks.update(
        label for package, label in framework_packages.items() if package in dependencies
    )
    if "nx" in dependencies or "@nx/workspace" in dependencies:
        monorepo_tools.add("Nx")
    if "turbo" in dependencies:
        monorepo_tools.add("Turborepo")
    scripts = data.get("scripts")
    if not isinstance(scripts, dict):
        return
    command = _javascript_command(package_managers)
    for script_name in scripts:
        capability = SCRIPT_CAPABILITIES.get(str(script_name).lower())
        if capability:
            lifecycle_commands.add(f"{capability}:{command} run {script_name}")


def _javascript_command(package_managers: set[str]) -> str:
    for candidate in ("pnpm", "Yarn", "Bun", "npm"):
        if candidate in package_managers:
            return candidate.lower()
    return "npm"


def _inspect_pyproject(
    data: dict[str, Any],
    package_managers: set[str],
    analysis_tools: set[str],
    release_signals: set[str],
) -> None:
    tools = data.get("tool")
    if isinstance(tools, dict):
        for key, label in (("ruff", "Ruff"), ("mypy", "mypy"), ("pytest", "pytest")):
            if key in tools:
                analysis_tools.add(label)
        for key, label in (("uv", "uv"), ("poetry", "Poetry"), ("pdm", "PDM")):
            if key in tools:
                package_managers.add(label)
    if isinstance(data.get("project"), dict) and isinstance(data.get("build-system"), dict):
        release_signals.add("python_package")


def _inspect_native_lifecycles(
    root: Path,
    names: set[str],
    commands: set[str],
    package_managers: set[str],
) -> None:
    if "pom.xml" in names:
        package_managers.add("Maven")
        executable = "./mvnw" if (root / "mvnw").is_file() else "mvn"
        commands.add(f"unit_tests:{executable} test")
        commands.add(f"build_package:{executable} verify")
    if any(name in names for name in ("build.gradle", "build.gradle.kts")):
        package_managers.add("Gradle")
        executable = "./gradlew" if (root / "gradlew").is_file() else "gradle"
        commands.add(f"unit_tests:{executable} test")
        commands.add(f"ci_mirror:{executable} check")
    if "cargo.toml" in names:
        package_managers.add("Cargo")
        commands.update(("format:cargo fmt --check", "lint:cargo clippy", "unit_tests:cargo test"))
    if "go.mod" in names:
        package_managers.add("Go modules")
        commands.update(("lint:go vet ./...", "unit_tests:go test ./..."))
    if any(name.endswith((".sln", ".csproj")) for name in names):
        package_managers.add(".NET")
        commands.update(("type_compile:dotnet build", "unit_tests:dotnet test"))


def _inspect_koda_contract(
    root: Path, lifecycle_commands: set[str], analysis_tools: set[str]
) -> None:
    data = _read_toml(root / "koda-code.toml")
    quality = data.get("quality")
    if not isinstance(quality, dict):
        return
    checks = quality.get("checks")
    if not isinstance(checks, list):
        return
    for item in checks:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name", "quality")).lower()
        argv = item.get("argv")
        if not isinstance(argv, list) or not all(isinstance(arg, str) for arg in argv):
            continue
        capability = _capability_for_check(name, argv)
        lifecycle_commands.add(f"{capability}:{' '.join(argv)}")
        if capability in {"lint", "type_compile", "static_security", "dependency_analysis"}:
            analysis_tools.add(name)


def _capability_for_check(name: str, argv: list[str]) -> str:
    joined = " ".join(argv).lower()
    checks = (
        ("format", "format"),
        ("lint", "lint"),
        ("mypy", "type_compile"),
        ("type", "type_compile"),
        ("pytest", "unit_tests"),
        ("test", "unit_tests"),
        ("build", "build_package"),
        ("bandit", "static_security"),
        ("secret", "secret_scan"),
        ("audit", "dependency_analysis"),
        ("package", "build_package"),
    )
    for marker, capability in checks:
        if marker in name or marker in joined:
            return capability
    return "ci_mirror"
