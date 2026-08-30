from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from .copilot import sanitize_output
from .models import Mission
from .repository import git
from .workspace import validate_mission_worktree

MAX_DIFF_CONTEXT = 20_000


def changed_paths(repository: Path) -> tuple[str, ...]:
    output = git(
        repository,
        "status",
        "--porcelain=v1",
        "-z",
        "--untracked-files=all",
    ).stdout
    paths: list[str] = []
    entries = output.split("\0")
    index = 0
    while index < len(entries):
        entry = entries[index]
        index += 1
        if not entry:
            continue
        path = entry[3:]
        if entry[:1] in {"R", "C"} and index < len(entries):
            path = entries[index]
            index += 1
        paths.append(path)
    return tuple(sorted(dict.fromkeys(paths)))


def repository_diff(repository: Path) -> str:
    output = git(
        repository,
        "diff",
        "--no-ext-diff",
        "--no-color",
        "HEAD",
        "--",
        check=False,
    ).stdout
    sanitized = sanitize_output(output)
    if len(sanitized) <= MAX_DIFF_CONTEXT:
        return sanitized
    half = MAX_DIFF_CONTEXT // 2
    return f"{sanitized[:half]}\n... diff truncated ...\n{sanitized[-half:]}"


def index_status(repository: Path) -> str:
    return git(repository, "diff", "--cached", "--name-status", "-z").stdout


def worktree_fingerprint(repository: Path, *, exclude_state: bool = False) -> str:
    digest = hashlib.sha256()
    for relative in changed_paths(repository):
        if exclude_state and (relative == ".koda-code" or relative.startswith(".koda-code/")):
            continue
        digest.update(relative.encode(errors="surrogateescape"))
        path = repository / relative
        if path.is_symlink():
            digest.update(f"symlink:{path.readlink()}".encode(errors="surrogateescape"))
        elif path.is_file():
            with path.open("rb") as handle:
                while chunk := handle.read(65_536):
                    digest.update(chunk)
        else:
            digest.update(b"missing-or-directory")
    return digest.hexdigest()


def validation_evidence(mission: Mission) -> str:
    parts = [
        f"{check.name}: {check.outcome} (exit {check.exit_code})\n{sanitize_output(check.output)}"
        for check in mission.checks
    ]
    return sanitize_output("\n\n".join(parts))


def mission_evidence(mission: Mission, repository: Path) -> dict[str, Any]:
    worktree = validate_mission_worktree(mission, repository)
    staged = tuple(item for item in index_status(worktree).split("\0") if item)
    return {
        "mission_id": mission.mission_id,
        "repository": str(repository),
        "worktree": str(worktree),
        "branch": git(worktree, "branch", "--show-current").stdout.strip(),
        "head": git(worktree, "rev-parse", "HEAD").stdout.strip(),
        "changed_paths": list(changed_paths(worktree)),
        "staged_entries": list(staged),
        "fingerprint": worktree_fingerprint(worktree),
        "diff": repository_diff(worktree),
        "stable_checkout_changed_paths": list(changed_paths(repository)),
        "stable_checkout_fingerprint": worktree_fingerprint(repository, exclude_state=True),
        "checks": [record.__dict__ for record in mission.checks],
    }
