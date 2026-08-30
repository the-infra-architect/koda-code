from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .models import EnforcementLevel

MAX_WORKFLOW_BYTES = 262_144
ACTION_REFERENCE = re.compile(r"\buses:\s*([^\s@]+/[^\s@]+)@([^\s#]+)")
FULL_SHA = re.compile(r"[0-9a-fA-F]{40}")
UNTRUSTED_EXPRESSIONS = (
    "github.event.pull_request.title",
    "github.event.pull_request.body",
    "github.event.issue.title",
    "github.event.issue.body",
    "github.head_ref",
    "github.ref_name",
)


@dataclass(frozen=True)
class CiSecurityFinding:
    code: str
    path: str
    enforcement: EnforcementLevel
    message: str
    claim_ids: tuple[str, ...] = ("C052", "C067")


@dataclass(frozen=True)
class GithubActionsReport:
    workflows: tuple[str, ...]
    least_privilege_declared: bool
    findings: tuple[CiSecurityFinding, ...]


def inspect_github_actions(
    repository: Path,
    *,
    immutable_third_party_actions_required: bool = False,
) -> GithubActionsReport:
    root = repository / ".github" / "workflows"
    if not root.is_dir():
        return GithubActionsReport((), False, ())
    workflows: list[str] = []
    findings: list[CiSecurityFinding] = []
    least_privilege = True
    for path in sorted((*root.glob("*.yml"), *root.glob("*.yaml"))):
        relative = path.relative_to(repository).as_posix()
        workflows.append(relative)
        if path.stat().st_size > MAX_WORKFLOW_BYTES:
            findings.append(
                CiSecurityFinding(
                    "workflow_too_large",
                    relative,
                    EnforcementLevel.REVIEWER_SIGNAL,
                    "Workflow exceeds bounded static inspection; inspect it through "
                    "project-native policy.",
                )
            )
            least_privilege = False
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            findings.append(
                CiSecurityFinding(
                    "workflow_unreadable",
                    relative,
                    EnforcementLevel.CONTEXT_REQUIRED,
                    "Workflow could not be read; CI security is unavailable rather than passed.",
                )
            )
            least_privilege = False
            continue
        if not _declares_least_privilege(content):
            least_privilege = False
            findings.append(
                CiSecurityFinding(
                    "permissions_not_least_privilege",
                    relative,
                    EnforcementLevel.CONTEXT_REQUIRED,
                    "Declare the smallest workflow/job token permissions needed by this workflow.",
                )
            )
        for expression in _unsafe_run_expressions(content):
            findings.append(
                CiSecurityFinding(
                    "untrusted_expression_in_run",
                    relative,
                    EnforcementLevel.HARD_INVARIANT,
                    f"Contributor-controlled {expression} is interpolated into executable "
                    "workflow text.",
                )
            )
        for owner_repo, reference in ACTION_REFERENCE.findall(content):
            if owner_repo.startswith("./") or owner_repo.startswith("docker://"):
                continue
            if owner_repo.startswith("actions/"):
                continue
            if not FULL_SHA.fullmatch(reference):
                findings.append(
                    CiSecurityFinding(
                        "mutable_third_party_action_reference",
                        relative,
                        (
                            EnforcementLevel.PROJECT_POLICY
                            if immutable_third_party_actions_required
                            else EnforcementLevel.RECOMMENDATION
                        ),
                        f"Third-party action {owner_repo}@{reference} is not pinned to an "
                        "immutable full SHA; follow project update policy.",
                    )
                )
        if re.search(
            r"(?im)^\s*(?:-\s*)?run:.*\b(?:echo|print|printf)\b.*secrets\.",
            content,
        ):
            findings.append(
                CiSecurityFinding(
                    "secret_in_executable_output",
                    relative,
                    EnforcementLevel.HARD_INVARIANT,
                    "A workflow appears to print a secret from executable text.",
                )
            )
        id_token = bool(re.search(r"(?im)^\s*id-token:\s*write\s*$", content))
        cloud_auth = bool(
            re.search(
                r"(?i)(aws-actions/configure-aws-credentials|azure/login|google-github-actions/auth)",
                content,
            )
        )
        if id_token and not cloud_auth:
            findings.append(
                CiSecurityFinding(
                    "oidc_without_cloud_auth",
                    relative,
                    EnforcementLevel.REVIEWER_SIGNAL,
                    "OIDC token permission is present without a detected compatible cloud "
                    "authentication need.",
                    ("C053",),
                )
            )
        if cloud_auth and not id_token and "secrets." in content:
            findings.append(
                CiSecurityFinding(
                    "long_lived_cloud_credentials",
                    relative,
                    EnforcementLevel.RECOMMENDATION,
                    "Detected cloud authentication uses stored secrets; prefer OIDC only if "
                    "the existing provider supports it.",
                    ("C053",),
                )
            )
    return GithubActionsReport(tuple(workflows), least_privilege, tuple(findings))


def _declares_least_privilege(content: str) -> bool:
    if re.search(r"(?im)^\s*permissions:\s*(?:write-all|read-all)\s*$", content):
        return False
    return bool(re.search(r"(?im)^permissions:\s*(?:\n|$)", content))


def _unsafe_run_expressions(content: str) -> tuple[str, ...]:
    found: set[str] = set()
    lines = content.splitlines()
    run_indent: int | None = None
    for line in lines:
        stripped = line.lstrip()
        indent = len(line) - len(stripped)
        if re.match(r"(?:-\s*)?run:\s*", stripped):
            run_indent = indent
            executable = stripped
        elif run_indent is not None and (not stripped or indent > run_indent):
            executable = stripped
        else:
            run_indent = None
            executable = ""
        if not executable:
            continue
        for expression in UNTRUSTED_EXPRESSIONS:
            if expression in executable and "${{" in executable:
                found.add(expression)
    return tuple(sorted(found))
