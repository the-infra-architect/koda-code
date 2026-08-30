from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from koda_code.errors import KodaError
from koda_code.quality import QualityCheck, load_checks, run_checks, validate_check


def test_loads_explicit_checks(tmp_path: Path) -> None:
    (tmp_path / "koda-code.toml").write_text(
        '[[quality.checks]]\nname="tests"\nargv=["python", "-m", "pytest"]\ntimeout_seconds=30\n',
        encoding="utf-8",
    )
    assert load_checks(tmp_path) == [QualityCheck("tests", ("python", "-m", "pytest"), 30)]


def test_missing_configuration_fails_closed(tmp_path: Path) -> None:
    with pytest.raises(KodaError, match=r"No koda-code\.toml"):
        load_checks(tmp_path)


@pytest.mark.parametrize(
    "check",
    [
        QualityCheck("empty", ()),
        QualityCheck("shell", ("sh", "-c", "echo bad")),
        QualityCheck("meta", ("python", ";", "bad")),
        QualityCheck("timeout", ("python", "-V"), 0),
    ],
)
def test_rejects_unsafe_check(check: QualityCheck) -> None:
    with pytest.raises(KodaError):
        validate_check(check)


@pytest.mark.parametrize(
    "executable",
    ("mvn", "./mvnw", "gradle", "./gradlew", "dotnet", "bun", "cargo", "go"),
)
def test_accepts_detected_native_lifecycle_executables(executable: str) -> None:
    validate_check(QualityCheck("native", (executable, "test")))


def test_runs_check_without_shell(tmp_path: Path) -> None:
    records = run_checks(tmp_path, [QualityCheck("version", ("python", "--version"), 10)])
    assert records[0].outcome == "passed"
    assert records[0].exit_code == 0


def test_stops_after_failure(tmp_path: Path) -> None:
    records = run_checks(
        tmp_path,
        [
            QualityCheck("fail", ("python", "-c", "raise SystemExit(3)"), 10),
            QualityCheck("never", ("python", "--version"), 10),
        ],
    )
    assert len(records) == 1
    assert records[0].outcome == "failed"
    assert records[0].exit_code == 3


def test_records_timeout(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    def expire(*args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
        raise subprocess.TimeoutExpired(["python"], 1, output="partial")

    monkeypatch.setattr(subprocess, "run", expire)
    records = run_checks(tmp_path, [QualityCheck("slow", ("python", "--version"), 1)])
    assert records[0].outcome == "timed_out"
    assert records[0].exit_code is None


def test_records_unavailable_quality_command(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    def unavailable(*args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
        raise FileNotFoundError("tool missing")

    monkeypatch.setattr(subprocess, "run", unavailable)
    records = run_checks(tmp_path, [QualityCheck("missing", ("npm", "test"), 10)])
    assert records[0].outcome == "failed"
    assert records[0].exit_code is None
    assert "could not start" in records[0].output


def test_bounds_output(tmp_path: Path) -> None:
    records = run_checks(
        tmp_path,
        [QualityCheck("large", ("python", "-c", "print('x' * 20000)"), 10)],
    )
    assert "output truncated" in records[0].output
    assert len(records[0].output) < 13_000
