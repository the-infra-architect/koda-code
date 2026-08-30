from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import time
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .engineering import apply_check_results, resolve_mission_engineering
from .errors import KodaError
from .evidence import changed_paths, index_status, worktree_fingerprint
from .models import CheckRecord, Mission
from .repository import git
from .workspace import validate_mission_worktree

ALLOWED_EXECUTABLES = {
    "python",
    "python3",
    "pytest",
    "ruff",
    "mypy",
    "uv",
    "npm",
    "pnpm",
    "yarn",
    "cargo",
    "go",
    "mvn",
    "./mvnw",
    "gradle",
    "./gradlew",
    "dotnet",
    "bun",
    "make",
}
SAFE_ENV_KEYS = {
    "PATH",
    "SYSTEMROOT",
    "TMPDIR",
    "TMP",
    "TEMP",
    "USERPROFILE",
    "CI",
    "NO_COLOR",
}
SHELL_META = {";", "&&", "||", "|", ">", ">>", "<", "`"}
MAX_OUTPUT = 12_000


@dataclass(frozen=True)
class QualityCheck:
    name: str
    argv: tuple[str, ...]
    timeout_seconds: int = 300


def load_checks(repository: Path) -> list[QualityCheck]:
    path = repository / "koda-code.toml"
    if not path.is_file():
        raise KodaError("No koda-code.toml was found. Add explicit project quality checks first.")
    try:
        data: dict[str, Any] = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise KodaError("koda-code.toml is invalid.") from exc
    raw_checks = data.get("quality", {}).get("checks", [])
    checks: list[QualityCheck] = []
    for item in raw_checks:
        argv = tuple(item.get("argv", []))
        timeout = int(item.get("timeout_seconds", 300))
        checks.append(
            QualityCheck(name=str(item.get("name", "unnamed")), argv=argv, timeout_seconds=timeout)
        )
    if not checks:
        raise KodaError("At least one quality check must be configured.")
    for check in checks:
        validate_check(check)
    return checks


def validate_check(check: QualityCheck) -> None:
    if not check.argv or check.argv[0] not in ALLOWED_EXECUTABLES:
        executable = check.argv[0] if check.argv else "<missing>"
        raise KodaError(f"Quality executable is not allowed: {executable}")
    if check.timeout_seconds < 1 or check.timeout_seconds > 1_800:
        raise KodaError(f"Quality timeout must be between 1 and 1800 seconds: {check.name}")
    if any(
        argument in SHELL_META or "\n" in argument or "\x00" in argument for argument in check.argv
    ):
        raise KodaError(f"Shell syntax is not allowed in quality check: {check.name}")


def run_checks(repository: Path, checks: list[QualityCheck]) -> list[CheckRecord]:
    environment = {key: value for key, value in os.environ.items() if key in SAFE_ENV_KEYS}
    environment.update({"CI": "1", "NO_COLOR": "1", "PYTHONUNBUFFERED": "1"})
    records: list[CheckRecord] = []
    for check in checks:
        argv = list(check.argv)
        if argv[0] in {"python", "python3"}:
            argv[0] = sys.executable
        started = time.monotonic()
        try:
            result = subprocess.run(
                argv,
                cwd=repository,
                env=environment,
                capture_output=True,
                text=True,
                timeout=check.timeout_seconds,
                check=False,
            )
            output = _bounded_output(result.stdout, result.stderr)
            records.append(
                CheckRecord(
                    name=check.name,
                    argv=list(check.argv),
                    outcome="passed" if result.returncode == 0 else "failed",
                    exit_code=result.returncode,
                    duration_seconds=round(time.monotonic() - started, 3),
                    output=output,
                )
            )
        except subprocess.TimeoutExpired as exc:
            records.append(
                CheckRecord(
                    name=check.name,
                    argv=list(check.argv),
                    outcome="timed_out",
                    exit_code=None,
                    duration_seconds=round(time.monotonic() - started, 3),
                    output=_bounded_output(exc.stdout or "", exc.stderr or ""),
                )
            )
            break
        except OSError as exc:
            records.append(
                CheckRecord(
                    name=check.name,
                    argv=list(check.argv),
                    outcome="failed",
                    exit_code=None,
                    duration_seconds=round(time.monotonic() - started, 3),
                    output=f"Quality command could not start: {exc}",
                )
            )
            break
        if records[-1].outcome != "passed":
            break
    return records


def run_mission_checks(mission: Mission, repository: Path) -> list[CheckRecord]:
    execution_root = (
        validate_mission_worktree(mission, repository) if mission.worktree else repository
    )
    resolve_mission_engineering(
        mission,
        execution_root,
        changed_paths=changed_paths(execution_root),
    )
    fingerprint_before = worktree_fingerprint(execution_root)
    head_before = _head(execution_root)
    index_before = index_status(execution_root)
    records = run_checks(execution_root, load_checks(execution_root))
    if mission.worktree and any(record.outcome != "passed" for record in records):
        baseline = _baseline_failed_check(mission, repository, records, execution_root)
        mission.baseline_checks = baseline
    integrity_errors: list[str] = []
    if _head(execution_root) != head_before:
        integrity_errors.append("quality checks changed Git history")
    if index_status(execution_root) != index_before:
        integrity_errors.append("quality checks changed the Git staging area")
    if worktree_fingerprint(execution_root) != fingerprint_before:
        integrity_errors.append("quality checks changed repository files")
    if integrity_errors:
        records.append(
            CheckRecord(
                name="workspace-integrity",
                argv=[],
                outcome="failed",
                exit_code=None,
                duration_seconds=0.0,
                output="; ".join(integrity_errors),
            )
        )
    if mission.quality_contract is not None:
        mission.quality_contract = apply_check_results(mission.quality_contract, records)
    return records


def _baseline_failed_check(
    mission: Mission,
    repository: Path,
    records: list[CheckRecord],
    execution_root: Path,
) -> list[CheckRecord]:
    failed = next((record for record in records if record.outcome != "passed"), None)
    if failed is None or mission.base_commit is None:
        return []
    selected = next(
        (check for check in load_checks(execution_root) if check.name == failed.name),
        None,
    )
    if selected is None:
        failed.attribution = "unknown"
        return []
    with tempfile.TemporaryDirectory(prefix="koda-baseline-") as temporary:
        baseline_root = Path(temporary) / "checkout"
        added = git(
            repository,
            "worktree",
            "add",
            "--detach",
            str(baseline_root),
            mission.base_commit,
            check=False,
        )
        if added.returncode != 0:
            failed.attribution = "unknown"
            return []
        try:
            baseline = run_checks(baseline_root, [selected])
        finally:
            git(
                repository,
                "worktree",
                "remove",
                "--force",
                str(baseline_root),
                check=False,
            )
    if not baseline:
        failed.attribution = "unknown"
        return []
    baseline_outcome = baseline[0].outcome
    failed.baseline_outcome = baseline_outcome
    if baseline[0].exit_code is None:
        failed.attribution = "unknown"
    elif baseline_outcome == "passed":
        failed.attribution = "introduced"
    else:
        failed.attribution = "preexisting"
    return baseline


def _head(repository: Path) -> str:
    return git(repository, "rev-parse", "HEAD", check=False).stdout.strip()


def _bounded_output(stdout: str | bytes, stderr: str | bytes) -> str:
    def text(value: str | bytes) -> str:
        return value.decode(errors="replace") if isinstance(value, bytes) else value

    combined = "\n".join(part.strip() for part in (text(stdout), text(stderr)) if part.strip())
    if len(combined) <= MAX_OUTPUT:
        return combined
    half = MAX_OUTPUT // 2
    return f"{combined[:half]}\n... output truncated ...\n{combined[-half:]}"
