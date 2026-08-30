from __future__ import annotations

from dataclasses import dataclass

from .errors import KodaError
from .models import (
    VulnerabilityFinding,
    VulnerabilityState,
    VulnerabilityTriage,
)


@dataclass(frozen=True)
class LicenseAssessment:
    license_name: str
    state: str
    blocking: bool
    reason: str


def triage_vulnerability(
    finding: VulnerabilityFinding,
    *,
    blocking_severities: frozenset[str] | None = None,
) -> VulnerabilityTriage:
    requested = finding.requested_state
    if requested is VulnerabilityState.NOT_AFFECTED_EVIDENCED:
        if not finding.applicability_evidence:
            raise KodaError(
                "A vulnerability cannot be marked not affected without trustworthy evidence."
            )
        return VulnerabilityTriage(
            finding,
            VulnerabilityState.NOT_AFFECTED_EVIDENCED,
            False,
            "Trustworthy applicability evidence supports non-impact for this product context.",
        )
    if requested is VulnerabilityState.TOOL_UNAVAILABLE:
        return VulnerabilityTriage(
            finding,
            VulnerabilityState.TOOL_UNAVAILABLE,
            False,
            "The vulnerability capability could not run; this is an explicit verification "
            "gap, not a pass.",
        )
    if requested is VulnerabilityState.FIXED:
        return VulnerabilityTriage(
            finding,
            VulnerabilityState.FIXED,
            False,
            "Deterministic dependency evidence records the finding as fixed.",
        )
    if finding.introduced is False:
        return VulnerabilityTriage(
            finding,
            VulnerabilityState.PREEXISTING,
            False,
            "The finding predates this mission and is reported without false attribution.",
        )
    if finding.introduced is True:
        severity = (finding.severity or "unknown").lower()
        policy_blocks = blocking_severities is not None and severity in {
            item.lower() for item in blocking_severities
        }
        if policy_blocks:
            return VulnerabilityTriage(
                finding,
                VulnerabilityState.NEW_BLOCKING,
                True,
                "The newly introduced finding violates the project's explicit severity policy.",
            )
        remediation = (
            f" A fixed version is reported: {finding.fixed_version}."
            if finding.fixed_version
            else ""
        )
        return VulnerabilityTriage(
            finding,
            VulnerabilityState.NEW_REQUIRES_REVIEW,
            False,
            "The mission introduced a finding that requires contextual review; no universal "
            "severity threshold was invented." + remediation,
        )
    return VulnerabilityTriage(
        finding,
        VulnerabilityState.UNKNOWN,
        False,
        "There is insufficient baseline or applicability evidence to classify the finding.",
    )


def assess_license(
    license_name: str,
    *,
    allowed: frozenset[str] | None = None,
    denied: frozenset[str] | None = None,
) -> LicenseAssessment:
    normalized = license_name.casefold()
    if denied is not None and normalized in {item.casefold() for item in denied}:
        return LicenseAssessment(
            license_name,
            "denied_by_policy",
            True,
            "The project or organization explicitly denies this license.",
        )
    if allowed is not None:
        if normalized in {item.casefold() for item in allowed}:
            return LicenseAssessment(
                license_name,
                "allowed_by_policy",
                False,
                "The project or organization explicitly allows this license.",
            )
        return LicenseAssessment(
            license_name,
            "not_listed_by_policy",
            True,
            "The project supplied an allow-list and this license is not listed.",
        )
    return LicenseAssessment(
        license_name,
        "report_only",
        False,
        "No license policy was supplied; Koda reports metadata without making a legal conclusion.",
    )
