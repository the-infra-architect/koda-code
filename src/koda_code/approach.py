from __future__ import annotations

from .models import RepositoryEvidence, RequirementUnderstanding, TechnicalApproach


def choose_approach(
    understanding: RequirementUnderstanding, evidence: RepositoryEvidence
) -> TechnicalApproach:
    reasons: list[str] = []
    drivers: list[str] = []
    avoided: list[str] = []
    deferred: list[str] = []

    if evidence.languages or evidence.frameworks:
        established = ", ".join((*evidence.languages[:2], *evidence.frameworks[:2]))
        summary = (
            f"Extend the existing project conventions ({established}) with the smallest "
            "coherent change."
        )
        reasons.append("An existing codebase is stronger evidence than a generic preferred stack.")
    elif understanding.explicit_technical_constraints:
        requested = ", ".join(understanding.explicit_technical_constraints)
        summary = (
            f"Start a focused implementation that honors the requested technology: {requested}."
        )
        reasons.append(
            "The user supplied explicit technical direction and no concrete conflict was found."
        )
    elif understanding.product_questions:
        summary = "Resolve the product questions before selecting irreversible infrastructure."
        reasons.append("Deployment, data, or access needs affect the responsible technical choice.")
        deferred.append("Framework and storage selection until the product questions are answered.")
    else:
        summary = (
            "Use one deployable component and the standard library or a small established "
            "framework."
        )
        reasons.append("No requirement currently justifies distributed infrastructure.")

    signals = set(understanding.capability_signals)
    if "sensitive_data" in signals:
        drivers.append(
            "Sensitive information requires explicit access and threat-boundary decisions."
        )
    if "scale_or_concurrency" in signals:
        drivers.append("Stated scale or concurrency requires measurement and capacity evidence.")
    if "persistent_data" in signals:
        drivers.append(
            "Persistence requires ownership, consistency, backup, and lifecycle decisions."
        )
    if "user_interface" in signals:
        drivers.append("A meaningful interface requires usability and accessibility review.")

    avoided.extend(
        (
            "No microservices without independent scaling, ownership, or "
            "failure-boundary evidence.",
            "No cache, queue, container platform, or database chosen by category alone.",
            "No interface or abstraction without a concrete substitution or repetition boundary.",
        )
    )
    if understanding.product_questions:
        deferred.append(
            "Acceptance details represented by the unanswered product-language questions."
        )

    return TechnicalApproach(
        summary=summary,
        reasons=tuple(reasons),
        constraints_honored=understanding.explicit_technical_constraints,
        complexity_drivers=tuple(drivers),
        complexity_avoided=tuple(avoided),
        decisions_deferred=tuple(dict.fromkeys(deferred)),
    )
