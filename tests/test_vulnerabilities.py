import pytest

from koda_code.errors import KodaError
from koda_code.models import VulnerabilityFinding, VulnerabilityState
from koda_code.vulnerabilities import assess_license, triage_vulnerability


def finding(**overrides: object) -> VulnerabilityFinding:
    values: dict[str, object] = {
        "identifier": "CVE-EXAMPLE",
        "component": "example",
        "version": "1.0",
        "severity": "high",
    }
    values.update(overrides)
    return VulnerabilityFinding(**values)  # type: ignore[arg-type]


def test_new_finding_uses_explicit_threshold_or_requires_review() -> None:
    review = triage_vulnerability(
        finding(introduced=True, fixed_version="1.1"),
    )
    assert review.state is VulnerabilityState.NEW_REQUIRES_REVIEW
    assert not review.blocking
    assert "1.1" in review.reason

    blocked = triage_vulnerability(
        finding(introduced=True),
        blocking_severities=frozenset({"high", "critical"}),
    )
    assert blocked.state is VulnerabilityState.NEW_BLOCKING
    assert blocked.blocking


def test_preexisting_fixed_unknown_and_tool_unavailable_are_distinct() -> None:
    assert triage_vulnerability(finding(introduced=False)).state is VulnerabilityState.PREEXISTING
    assert triage_vulnerability(finding()).state is VulnerabilityState.UNKNOWN
    fixed = triage_vulnerability(finding(requested_state=VulnerabilityState.FIXED))
    assert fixed.state is VulnerabilityState.FIXED
    unavailable = triage_vulnerability(finding(requested_state=VulnerabilityState.TOOL_UNAVAILABLE))
    assert unavailable.state is VulnerabilityState.TOOL_UNAVAILABLE
    assert "not a pass" in unavailable.reason


def test_not_affected_requires_evidence() -> None:
    with pytest.raises(KodaError, match="without trustworthy evidence"):
        triage_vulnerability(finding(requested_state=VulnerabilityState.NOT_AFFECTED_EVIDENCED))
    evidenced = triage_vulnerability(
        finding(
            requested_state=VulnerabilityState.NOT_AFFECTED_EVIDENCED,
            applicability_evidence="Vendor VEX statement for this product version.",
        )
    )
    assert evidenced.state is VulnerabilityState.NOT_AFFECTED_EVIDENCED


def test_license_policy_is_explicit_and_no_policy_is_report_only() -> None:
    assert assess_license("MIT").state == "report_only"
    assert not assess_license("MIT").blocking
    assert assess_license("MIT", allowed=frozenset({"MIT"})).state == "allowed_by_policy"
    denied = assess_license("GPL-3.0", denied=frozenset({"GPL-3.0"}))
    assert denied.state == "denied_by_policy"
    assert denied.blocking
