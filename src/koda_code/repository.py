from __future__ import annotations

import os
import subprocess
from pathlib import Path

from .errors import KodaError

SAFE_GIT_ENV = {
    "PATH",
    "SYSTEMROOT",
    "TMPDIR",
    "TMP",
    "TEMP",
    "USERPROFILE",
    "GIT_CONFIG_NOSYSTEM",
}


def repository_root(path: Path) -> Path:
    candidate = path.expanduser().resolve()
    if not candidate.is_dir():
        raise KodaError(f"Project folder does not exist: {candidate}")
    result = git(candidate, "rev-parse", "--show-toplevel", check=False)
    if result.returncode == 0:
        return Path(result.stdout.strip()).resolve()
    return candidate


def ensure_inside(root: Path, candidate: Path) -> Path:
    resolved = candidate.expanduser().resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError as exc:
        raise KodaError(f"Path must stay inside the project: {candidate}") from exc
    return resolved


def git(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    env = {key: value for key, value in os.environ.items() if key in SAFE_GIT_ENV}
    env.update({"GIT_TERMINAL_PROMPT": "0", "LC_ALL": "C", "LANG": "C"})
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    if check and result.returncode != 0:
        message = (result.stderr or result.stdout).strip()
        raise KodaError(message or f"Git command failed: {' '.join(args)}")
    return result
