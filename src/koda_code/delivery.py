from __future__ import annotations

import shutil
from pathlib import Path

from .errors import KodaError
from .evidence import worktree_fingerprint
from .models import AgentName, Mission, Outcome
from .repository import ensure_inside, git
from .security import scan_paths
from .workspace import refuse_protected_branch

REQUIRED_STAGES = {AgentName.ENGINEER, AgentName.TESTER, AgentName.REVIEWER}


def finish_mission(
    mission: Mission,
    repository: Path,
    paths: list[str],
    message: str,
    *,
    push: bool = False,
    pull_request: bool = False,
) -> str:
    refuse_protected_branch(repository)
    required = REQUIRED_STAGES | {
        assignment.agent
        for assignment in mission.assignments
        if assignment.agent is AgentName.UI_UX
    }
    incomplete = [
        agent.value
        for agent in sorted(required, key=lambda item: item.value)
        if mission.stages.get(agent.value) is None
        or mission.stages[agent.value].outcome is not Outcome.PASSED
    ]
    if incomplete:
        raise KodaError(f"Required stages are incomplete: {', '.join(incomplete)}")
    if not mission.checks or any(check.outcome != "passed" for check in mission.checks):
        raise KodaError("The latest quality gate must be complete and passing.")
    if not mission.check_fingerprint or mission.check_fingerprint != worktree_fingerprint(
        repository
    ):
        raise KodaError("The latest quality evidence is stale for the current repository state.")
    if not paths:
        raise KodaError("Name the files to include; broad automatic staging is not allowed.")
    if not message.strip():
        raise KodaError("A clear commit message is required.")
    pre_staged = git(repository, "diff", "--cached", "--name-only", "-z").stdout.split("\0")
    if any(pre_staged):
        raise KodaError("Unrelated files are already staged; review and clear them first.")
    selected = [ensure_inside(repository, repository / item) for item in paths]
    missing = [str(path.relative_to(repository)) for path in selected if not path.exists()]
    if missing:
        raise KodaError(f"Selected paths do not exist: {', '.join(missing)}")
    findings = scan_paths(repository, selected)
    if findings:
        raise KodaError("Secret scan blocked delivery: " + "; ".join(findings))
    git(repository, "add", "--", *(str(path.relative_to(repository)) for path in selected))
    git(repository, "commit", "-m", message.strip())
    commit = git(repository, "rev-parse", "HEAD").stdout.strip()
    if push or pull_request:
        git(repository, "push", "-u", "origin", "HEAD")
    if pull_request:
        if shutil.which("gh") is None:
            raise KodaError("GitHub CLI is required to open a pull request.")
        branch = git(repository, "branch", "--show-current").stdout.strip()
        _run_gh(repository, "pr", "create", "--fill", "--head", branch)
    mission.delivered_commit = commit
    return commit


def _run_gh(repository: Path, *args: str) -> None:
    import os
    import subprocess

    environment = {
        key: value
        for key, value in os.environ.items()
        if key
        in {"PATH", "SYSTEMROOT", "TMPDIR", "TMP", "TEMP", "USERPROFILE", "GH_HOST", "GH_TOKEN"}
    }
    result = subprocess.run(
        ["gh", *args],
        cwd=repository,
        env=environment,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    if result.returncode != 0:
        raise KodaError((result.stderr or result.stdout).strip() or "Pull request creation failed.")
