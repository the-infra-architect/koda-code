from __future__ import annotations

import re
from pathlib import Path

from .errors import KodaError
from .models import Mission
from .repository import git

PROTECTED_BRANCHES = {"main", "master", "trunk", "production"}


def branch_slug(request: str, mission_id: str) -> str:
    words = re.findall(r"[a-z0-9]+", request.lower())[:5]
    topic = "-".join(words) or "change"
    return f"feature/{mission_id}-{topic}"[:90].rstrip("-")


def create_mission_worktree(repository: Path, mission_id: str, request: str) -> tuple[Path, str]:
    if git(repository, "rev-parse", "--is-inside-work-tree", check=False).returncode != 0:
        raise KodaError("Create a Git repository before requesting an isolated worktree.")
    dirty = _non_state_changes(repository)
    if dirty:
        raise KodaError(
            "The stable project checkout has uncommitted changes. Commit, stash, or remove them "
            f"before beginning a mission: {', '.join(dirty)}"
        )
    branch = branch_slug(request, mission_id)
    parent = repository.parent / f"{repository.name}-worktrees"
    destination = parent / mission_id
    if destination.exists():
        raise KodaError(f"Worktree destination already exists: {destination}")
    existing = git(repository, "branch", "--list", branch).stdout.strip()
    if existing:
        raise KodaError(f"Branch already exists: {branch}")
    parent.mkdir(parents=True, exist_ok=True)
    git(repository, "worktree", "add", "-b", branch, str(destination))
    return destination.resolve(), branch


def current_branch(repository: Path) -> str:
    return git(repository, "branch", "--show-current").stdout.strip()


def refuse_protected_branch(repository: Path) -> str:
    branch = current_branch(repository)
    if not branch:
        raise KodaError("Delivery requires a named Git branch.")
    if branch in PROTECTED_BRANCHES:
        raise KodaError(f"Delivery is blocked on protected branch: {branch}")
    return branch


def validate_mission_worktree(mission: Mission, repository: Path) -> Path:
    canonical = repository.resolve()
    recorded_root = Path(mission.repository.root).resolve()
    if canonical != recorded_root:
        raise KodaError(f"Mission belongs to a different project: {recorded_root}")
    if not mission.worktree or not mission.branch:
        raise KodaError(
            "Automatic execution requires an isolated worktree. Begin again with "
            "--prepare-worktree."
        )
    worktree = Path(mission.worktree).resolve()
    if not worktree.is_dir() or worktree == canonical:
        raise KodaError(
            "The mission worktree is missing or is not isolated from the main checkout."
        )
    expected_parent = canonical.parent / f"{canonical.name}-worktrees"
    if worktree.parent != expected_parent.resolve():
        raise KodaError(f"The mission worktree is outside Koda's expected location: {worktree}")
    if mission.branch in PROTECTED_BRANCHES:
        raise KodaError(f"Execution is blocked on protected branch: {mission.branch}")
    if current_branch(worktree) != mission.branch:
        raise KodaError("The mission worktree no longer has its recorded branch checked out.")
    if _common_git_directory(canonical) != _common_git_directory(worktree):
        raise KodaError("The mission worktree is not attached to the recorded repository.")
    listed = git(canonical, "worktree", "list", "--porcelain").stdout.splitlines()
    if f"worktree {worktree}" not in listed:
        raise KodaError("Git no longer recognizes the recorded mission worktree.")
    return worktree


def _common_git_directory(repository: Path) -> Path:
    raw = git(repository, "rev-parse", "--git-common-dir").stdout.strip()
    path = Path(raw)
    return (path if path.is_absolute() else repository / path).resolve()


def _non_state_changes(repository: Path) -> tuple[str, ...]:
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
        if path != ".koda-code" and not path.startswith(".koda-code/"):
            paths.append(path)
    return tuple(sorted(dict.fromkeys(paths)))
