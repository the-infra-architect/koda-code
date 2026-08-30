from __future__ import annotations

import re

from .models import RepositoryEvidence, RequirementUnderstanding

TECHNOLOGIES = (
    "React",
    "Next.js",
    "FastAPI",
    "Django",
    "Flask",
    "PostgreSQL",
    "DuckDB",
    "SQLite",
    "Redis",
    "Kafka",
    "Docker",
    "Kubernetes",
    "GraphQL",
    "REST",
    "TypeScript",
    "Python",
    "Go",
    "Rust",
    ".NET",
    "Maven",
    "Gradle",
    "Nx",
    "Turborepo",
    "Microservices",
)


def understand_request(request: str, evidence: RepositoryEvidence) -> RequirementUnderstanding:
    normalized = " ".join(request.split())
    lowered = normalized.lower()
    explicit = tuple(
        technology
        for technology in TECHNOLOGIES
        if re.search(rf"\b{re.escape(technology.lower())}\b", lowered)
    )
    signals: list[str] = []
    questions: list[str] = []

    if any(word in lowered for word in ("page", "screen", "dashboard", "form", "website", "ui")):
        signals.append("user_interface")
    if any(word in lowered for word in ("data", "inventory", "record", "save", "track", "report")):
        signals.append("persistent_data")
    if any(word in lowered for word in ("login", "account", "role", "permission", "private")):
        signals.append("identity_or_access")
    if any(word in lowered for word in ("payment", "medical", "health", "financial", "secret")):
        signals.append("sensitive_data")
    if any(word in lowered for word in ("many users", "high traffic", "concurrent", "real-time")):
        signals.append("scale_or_concurrency")
    if any(word in lowered for word in ("deploy", "online", "public", "share", "company")):
        signals.append("shared_or_deployed")
    if any(word in lowered for word in ("api", "endpoint", "library", "package", "cli")):
        signals.append("compatibility_surface")
    if any(word in lowered for word in ("migration", "schema", "database column")):
        signals.append("data_migration")
    if any(word in lowered for word in ("queue", "event bus", "kafka", "at-least-once")):
        signals.append("messaging")
    if any(word in lowered for word in ("cache", "redis")):
        signals.append("caching")
    if any(word in lowered for word in ("smb", "nfs", "nas", "shared folder")):
        signals.append("network_shared_storage")

    local_usage_is_explicit = any(
        phrase in lowered
        for phrase in ("offline", "personal", "only on this computer", "local-only")
    )
    if "persistent_data" in signals and not evidence.data_signals and not local_usage_is_explicit:
        questions.append(
            "Where should the shared information live: only on this computer, on a company "
            "server/shared location, or online?"
        )
    if "identity_or_access" in signals:
        questions.append(
            "Who should be able to use this, and should different people be allowed to do "
            "different things?"
        )
    if (
        "persistent_data" in signals
        and "shared_or_deployed" in signals
        and not evidence.data_signals
    ):
        questions.append("Can several people edit this information at the same time?")
    if "sensitive_data" in signals:
        questions.append(
            "What information would be especially harmful if the wrong person could see or "
            "change it?"
        )
    if (
        "shared_or_deployed" not in signals
        and not evidence.frameworks
        and "user_interface" in signals
        and not local_usage_is_explicit
    ):
        questions.append(
            "Who needs to use this and where: just you on this computer, people on a shared "
            "network, or anyone online?"
        )
    if len(normalized.split()) < 4:
        questions.append("What should someone be able to accomplish when this is finished?")

    return RequirementUnderstanding(
        requested_outcome=normalized,
        explicit_technical_constraints=explicit,
        product_questions=tuple(dict.fromkeys(questions)),
        capability_signals=tuple(signals),
    )
