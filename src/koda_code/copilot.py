from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .models import AgentName, AgentResult, AgentResultOutcome

MAX_PROVIDER_OUTPUT = 12_000
MAX_RESULT_TEXT = 2_000
DEFAULT_TIMEOUT_SECONDS = 1_800

SAFE_ENV_KEYS = {
    "HOME",
    "LANG",
    "LC_ALL",
    "PATH",
    "SYSTEMROOT",
    "TEMP",
    "TMP",
    "TMPDIR",
    "USERPROFILE",
}

MUTABLE_ROLES = {AgentName.ENGINEER, AgentName.TESTER, AgentName.UI_UX}
READ_ONLY_ROLES = {AgentName.REVIEWER, AgentName.DEBUGGER}

MUTABLE_SHELL_PERMISSIONS = (
    "shell(python:*)",
    "shell(python3:*)",
    "shell(pytest:*)",
    "shell(ruff:*)",
    "shell(mypy:*)",
    "shell(uv:*)",
    "shell(npm:*)",
    "shell(pnpm:*)",
    "shell(yarn:*)",
    "shell(cargo:*)",
    "shell(go:*)",
    "shell(make)",
    "shell(make:*)",
    "shell(git diff)",
    "shell(git grep)",
    "shell(git log)",
    "shell(git ls-files)",
    "shell(git rev-parse)",
    "shell(git show)",
    "shell(git status)",
)

DELIVERY_DENIALS = (
    "shell(git add)",
    "shell(git branch)",
    "shell(git cherry-pick)",
    "shell(git commit)",
    "shell(git config)",
    "shell(git merge)",
    "shell(git push)",
    "shell(git checkout)",
    "shell(git rebase)",
    "shell(git remote)",
    "shell(git revert)",
    "shell(git switch)",
    "shell(git reset)",
    "shell(git clean)",
    "shell(git tag)",
    "shell(git worktree)",
    "shell(gh)",
)

SECRET_ASSIGNMENT = re.compile(
    r"(?i)\b(api[_-]?key|access[_-]?token|auth[_-]?token|client[_-]?secret|password)"
    r"\b\s*[:=]\s*([^\s,;]+)"
)


@dataclass(frozen=True)
class CopilotCapability:
    executable: str
    version: str
    sandbox_supported: bool
    compatible: bool = True
    diagnostic: str = ""


@dataclass(frozen=True)
class CopilotCall:
    process_outcome: str
    exit_code: int | None
    timed_out: bool
    sandboxed: bool
    diagnostic: str
    result: AgentResult | None


def detect_copilot() -> CopilotCapability | None:
    executable = shutil.which("copilot")
    if executable is None:
        return None
    try:
        version = subprocess.run(
            [executable, "--version"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        help_result = subprocess.run(
            [executable, "help"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if version.returncode != 0 or help_result.returncode != 0:
        return None
    help_text = f"{help_result.stdout}\n{help_result.stderr}"
    required = {
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
    }
    missing = sorted(option for option in required if option not in help_text)
    return CopilotCapability(
        executable=executable,
        version=_bounded(version.stdout or version.stderr).strip(),
        sandbox_supported="--sandbox" in help_text,
        compatible=not missing,
        diagnostic=(
            "Installed GitHub Copilot CLI lacks required options: " + ", ".join(missing)
            if missing
            else ""
        ),
    )


def role_arguments(role: AgentName) -> list[str]:
    shell_tool = "powershell" if os.name == "nt" else "bash"
    if role in MUTABLE_ROLES:
        arguments = [
            f"--available-tools=view,grep,glob,edit,create,apply_patch,{shell_tool}",
            "--allow-tool=" + ",".join(("read", "write", *MUTABLE_SHELL_PERMISSIONS)),
            "--deny-tool=url,memory",
        ]
    elif role in READ_ONLY_ROLES:
        arguments = [
            "--available-tools=view,grep,glob",
            "--allow-tool=read",
            "--deny-tool=write,shell,url,memory",
        ]
    else:  # pragma: no cover - AgentName currently makes this unreachable.
        raise ValueError(f"Unsupported role: {role}")
    arguments.extend(f"--deny-tool={rule}" for rule in DELIVERY_DENIALS)
    return arguments


def copilot_argv(
    capability: CopilotCapability,
    role: AgentName,
    prompt: str,
) -> list[str]:
    argv = [
        capability.executable,
        "-p",
        prompt,
        "-s",
        "--stream=off",
        "--no-ask-user",
        "--no-color",
        "--no-auto-update",
        "--no-remote",
        "--no-remote-export",
        "--disable-builtin-mcps",
        "--excluded-tools=task,web_fetch,web_search,skill",
        *role_arguments(role),
    ]
    if capability.sandbox_supported:
        argv.extend(("--experimental", "--sandbox"))
    return argv


def run_copilot(
    role: AgentName,
    prompt: str,
    worktree: Path,
    capability: CopilotCapability,
    *,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
) -> CopilotCall:
    environment = {key: value for key, value in os.environ.items() if key in SAFE_ENV_KEYS}
    environment.update(
        {
            "CI": "1",
            "NO_COLOR": "1",
            "COPILOT_AUTO_UPDATE": "false",
            "GIT_TERMINAL_PROMPT": "0",
        }
    )
    try:
        completed = subprocess.run(
            copilot_argv(capability, role, prompt),
            cwd=worktree,
            env=environment,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        diagnostic = sanitize_output(_combine(exc.stdout or "", exc.stderr or ""))
        if not diagnostic:
            diagnostic = f"GitHub Copilot CLI timed out after {timeout_seconds} seconds."
        return CopilotCall(
            process_outcome="timed_out",
            exit_code=None,
            timed_out=True,
            sandboxed=capability.sandbox_supported,
            diagnostic=diagnostic,
            result=None,
        )
    except OSError as exc:
        return CopilotCall(
            process_outcome="unavailable",
            exit_code=None,
            timed_out=False,
            sandboxed=capability.sandbox_supported,
            diagnostic=sanitize_output(str(exc)),
            result=None,
        )

    output = sanitize_output(_combine(completed.stdout, completed.stderr))
    if completed.returncode != 0:
        return CopilotCall(
            process_outcome=_failure_kind(output),
            exit_code=completed.returncode,
            timed_out=False,
            sandboxed=capability.sandbox_supported,
            diagnostic=output or "GitHub Copilot CLI exited without diagnostic output.",
            result=None,
        )
    try:
        result = parse_agent_result(completed.stdout.strip())
    except ValueError as exc:
        return CopilotCall(
            process_outcome="invalid_result",
            exit_code=completed.returncode,
            timed_out=False,
            sandboxed=capability.sandbox_supported,
            diagnostic=_bounded(f"{exc}\n{output}"),
            result=None,
        )
    return CopilotCall(
        process_outcome="completed",
        exit_code=completed.returncode,
        timed_out=False,
        sandboxed=capability.sandbox_supported,
        diagnostic="",
        result=result,
    )


def parse_agent_result(output: str) -> AgentResult:
    try:
        raw: Any = json.loads(output)
    except json.JSONDecodeError as exc:
        raise ValueError("Copilot did not return one valid JSON result object.") from exc
    if not isinstance(raw, dict):
        raise ValueError("Copilot result must be a JSON object.")
    allowed = {"outcome", "summary", "findings", "question", "unclear_failure"}
    if set(raw) - allowed:
        raise ValueError("Copilot result contains unsupported fields.")
    try:
        outcome = AgentResultOutcome(raw["outcome"])
    except (KeyError, ValueError, TypeError) as exc:
        raise ValueError("Copilot result has an invalid outcome.") from exc
    summary = raw.get("summary")
    findings = raw.get("findings", [])
    question = raw.get("question")
    unclear = raw.get("unclear_failure", False)
    if not isinstance(summary, str) or not summary.strip() or len(summary) > MAX_RESULT_TEXT:
        raise ValueError("Copilot result requires a concise non-empty summary.")
    if (
        not isinstance(findings, list)
        or len(findings) > 20
        or any(not isinstance(item, str) or not item.strip() for item in findings)
    ):
        raise ValueError("Copilot findings must be a short list of non-empty strings.")
    if any(len(item) > MAX_RESULT_TEXT for item in findings):
        raise ValueError("A Copilot finding exceeded the result size limit.")
    if question is not None and (not isinstance(question, str) or not question.strip()):
        raise ValueError("Copilot question must be null or a non-empty string.")
    if isinstance(question, str) and len(question) > MAX_RESULT_TEXT:
        raise ValueError("Copilot question exceeded the result size limit.")
    if not isinstance(unclear, bool):
        raise ValueError("Copilot unclear_failure must be true or false.")
    if outcome is AgentResultOutcome.NEEDS_INPUT and not question:
        raise ValueError("A needs_input result requires one question.")
    if outcome is not AgentResultOutcome.NEEDS_INPUT and question is not None:
        raise ValueError("Only needs_input may include a question.")
    if outcome is AgentResultOutcome.CHANGES_REQUIRED and not findings:
        raise ValueError("A changes_required result requires actionable findings.")
    return AgentResult(
        outcome=outcome,
        summary=summary.strip(),
        findings=tuple(item.strip() for item in findings),
        question=question.strip() if isinstance(question, str) else None,
        unclear_failure=unclear,
    )


def sanitize_output(output: str) -> str:
    bounded = _bounded(output)
    for key, value in os.environ.items():
        if _sensitive_key(key) and len(value) >= 4:
            bounded = bounded.replace(value, "[REDACTED]")
    return SECRET_ASSIGNMENT.sub(lambda match: f"{match.group(1)}=[REDACTED]", bounded)


def _sensitive_key(key: str) -> bool:
    upper = key.upper()
    return any(marker in upper for marker in ("TOKEN", "SECRET", "PASSWORD", "API_KEY"))


def _failure_kind(output: str) -> str:
    lowered = output.lower()
    if any(term in lowered for term in ("quota", "rate limit", "usage limit")):
        return "quota_limited"
    if any(term in lowered for term in ("not authenticated", "authentication", "log in", "login")):
        return "authentication_failed"
    return "process_failed"


def _combine(stdout: str | bytes, stderr: str | bytes) -> str:
    def text(value: str | bytes) -> str:
        return value.decode(errors="replace") if isinstance(value, bytes) else value

    return "\n".join(part.strip() for part in (text(stdout), text(stderr)) if part.strip())


def _bounded(output: str) -> str:
    if len(output) <= MAX_PROVIDER_OUTPUT:
        return output
    half = MAX_PROVIDER_OUTPUT // 2
    return f"{output[:half]}\n... provider output truncated ...\n{output[-half:]}"
