from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from koda_code.copilot import (
    CopilotCapability,
    copilot_argv,
    detect_copilot,
    parse_agent_result,
    role_arguments,
    run_copilot,
    sanitize_output,
)
from koda_code.models import AgentName, AgentResultOutcome


def capability(*, sandbox: bool = True) -> CopilotCapability:
    return CopilotCapability("/bin/copilot", "1.0.0", sandbox)


def test_parses_small_result_contract() -> None:
    result = parse_agent_result(
        json.dumps(
            {
                "outcome": "changes_required",
                "summary": "A boundary is missing.",
                "findings": ["Handle an empty query."],
                "question": None,
                "unclear_failure": False,
            }
        )
    )
    assert result.outcome is AgentResultOutcome.CHANGES_REQUIRED
    assert result.findings == ("Handle an empty query.",)


@pytest.mark.parametrize(
    "payload",
    [
        "not json",
        "[]",
        '{"outcome":"pass","summary":"ok","findings":[],"question":null,"passed":true}',
        '{"outcome":"unknown","summary":"ok"}',
        '{"outcome":"changes_required","summary":"ok","findings":[]}',
        '{"outcome":"needs_input","summary":"waiting","question":null}',
    ],
)
def test_rejects_malformed_or_self_authorizing_results(payload: str) -> None:
    with pytest.raises(ValueError):
        parse_agent_result(payload)


def test_permission_arguments_never_use_permissive_modes() -> None:
    engineer = copilot_argv(capability(), AgentName.ENGINEER, "prompt")
    reviewer = copilot_argv(capability(), AgentName.REVIEWER, "prompt")
    joined = " ".join((*engineer, *reviewer))
    assert "--allow-all" not in joined
    assert "--yolo" not in joined
    assert "--allow-all-paths" not in joined
    assert "--sandbox" in engineer
    assert any(item.startswith("--allow-tool=read,write,") for item in engineer)
    assert any("shell(python:*)" in item for item in engineer)
    assert all(item != "--allow-tool=shell" for item in engineer)
    assert "--deny-tool=write,shell,url,memory" in reviewer
    assert all("--allow-tool=write" not in item for item in role_arguments(AgentName.REVIEWER))
    assert "--disable-builtin-mcps" in engineer
    assert "--deny-tool=shell(git push)" in engineer
    assert "--deny-tool=shell(git commit)" in engineer


def test_unsupported_sandbox_is_reported_and_flag_omitted() -> None:
    item = capability(sandbox=False)
    assert "--sandbox" not in copilot_argv(item, AgentName.TESTER, "prompt")


def test_runner_uses_argv_worktree_timeout_and_sanitized_environment(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    observed: dict[str, object] = {}
    payload = json.dumps({"outcome": "pass", "summary": "Done", "findings": [], "question": None})

    def fake_run(argv: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        observed["argv"] = argv
        observed.update(kwargs)
        return subprocess.CompletedProcess(argv, 0, payload, "")

    monkeypatch.setenv("GH_TOKEN", "should-not-reach-agent")
    monkeypatch.setattr(subprocess, "run", fake_run)
    result = run_copilot(AgentName.ENGINEER, "Do work", tmp_path, capability())
    assert result.result and result.result.outcome is AgentResultOutcome.PASS
    assert observed["cwd"] == tmp_path
    assert observed["timeout"] == 1_800
    assert observed["stdin"] is subprocess.DEVNULL
    assert "shell" not in observed
    assert "GH_TOKEN" not in observed["env"]  # type: ignore[operator]
    assert isinstance(observed["argv"], list)


def test_runner_records_timeout(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    def expire(*args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
        raise subprocess.TimeoutExpired(["copilot"], 3, output="partial")

    monkeypatch.setattr(subprocess, "run", expire)
    result = run_copilot(AgentName.TESTER, "Test", tmp_path, capability(), timeout_seconds=3)
    assert result.process_outcome == "timed_out"
    assert result.timed_out


def test_runner_classifies_authentication_failure(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    def fail(argv: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(argv, 1, "", "Not authenticated; run /login")

    monkeypatch.setattr(subprocess, "run", fail)
    result = run_copilot(AgentName.REVIEWER, "Review", tmp_path, capability())
    assert result.process_outcome == "authentication_failed"


def test_detects_missing_executable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("shutil.which", lambda name: None)
    assert detect_copilot() is None


def test_detects_current_compatible_cli_and_sandbox(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("shutil.which", lambda name: "/bin/copilot")
    options = " ".join(
        (
            "-p",
            "--allow-tool",
            "--available-tools",
            "--deny-tool",
            "--disable-builtin-mcps",
            "--excluded-tools",
            "--no-auto-update",
            "--no-color",
            "--no-ask-user",
            "--no-remote",
            "--no-remote-export",
            "--silent",
            "--stream",
            "--sandbox",
        )
    )

    def fake_run(argv: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        output = "1.2.3" if "--version" in argv else options
        return subprocess.CompletedProcess(argv, 0, output, "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    result = detect_copilot()
    assert result == CopilotCapability("/bin/copilot", "1.2.3", True)


def test_detects_incompatible_cli_without_assuming_missing_flags(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("shutil.which", lambda name: "/bin/copilot")

    def fake_run(argv: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(argv, 0, "old version", "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    result = detect_copilot()
    assert result is not None
    assert not result.compatible
    assert "--allow-tool" in result.diagnostic


def test_detect_returns_none_when_inspection_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("shutil.which", lambda name: "/bin/copilot")

    def fail(*args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
        raise OSError("cannot execute")

    monkeypatch.setattr(subprocess, "run", fail)
    assert detect_copilot() is None


def test_runner_marks_invalid_success_output(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    def invalid(argv: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(argv, 0, "not json", "")

    monkeypatch.setattr(subprocess, "run", invalid)
    result = run_copilot(AgentName.ENGINEER, "Work", tmp_path, capability())
    assert result.process_outcome == "invalid_result"
    assert result.result is None


def test_runner_handles_executable_disappearing(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    def missing(*args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
        raise OSError("gone")

    monkeypatch.setattr(subprocess, "run", missing)
    result = run_copilot(AgentName.ENGINEER, "Work", tmp_path, capability())
    assert result.process_outcome == "unavailable"


def test_redacts_environment_values_and_assignments(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SERVICE_TOKEN", "very-secret-token")
    fake_assignment = "password" + "=another-secret"
    output = sanitize_output(f"very-secret-token {fake_assignment}")
    assert "very-secret-token" not in output
    assert "another-secret" not in output
    assert output.count("[REDACTED]") == 2
