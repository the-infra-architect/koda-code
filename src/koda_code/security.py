from __future__ import annotations

import re
from pathlib import Path

from .repository import git

SENSITIVE_NAME = re.compile(
    r"(^|/)(\.env($|\.)|.*\.(pem|key|p12|pfx)|id_(rsa|ed25519)|credentials\.json)$",
    re.IGNORECASE,
)
SECRET_ASSIGNMENT = re.compile(
    r"(?i)\b(api[_-]?key|access[_-]?token|auth[_-]?token|client[_-]?secret|password)\b\s*[:=]\s*[\"']?([^\s\"']+)"
)
PLACEHOLDERS = {"", "changeme", "example", "placeholder", "your-token-here", "<redacted>"}
MAX_SCAN_BYTES = 1_000_000


def scan_paths(repository: Path, paths: list[Path]) -> list[str]:
    findings: list[str] = []
    for path in paths:
        relative = path.relative_to(repository).as_posix()
        if SENSITIVE_NAME.search(relative):
            findings.append(f"Sensitive filename: {relative}")
            continue
        if not path.is_file() or path.is_symlink() or path.stat().st_size > MAX_SCAN_BYTES:
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for match in SECRET_ASSIGNMENT.finditer(content):
            value = match.group(2).strip().lower()
            if value not in PLACEHOLDERS and len(value) >= 8:
                findings.append(f"Possible secret assignment in {relative}")
                break
    return findings


def tracked_paths(repository: Path) -> list[Path]:
    result = git(repository, "ls-files", "-z")
    return [repository / item for item in result.stdout.split("\0") if item]


def main() -> int:
    repository = Path.cwd().resolve()
    findings = scan_paths(repository, tracked_paths(repository))
    if findings:
        print("\n".join(findings))
        return 1
    print("Secret scan passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
