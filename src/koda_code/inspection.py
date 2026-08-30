from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any

from .discovery import inspect_repository
from .engineering import derive_engineering_profile, resolve_quality_contract
from .identity import VERSION
from .models import RequirementUnderstanding
from .status import mission_status
from .store import MissionStore

MAX_MISSIONS = 20


def project_snapshot(repository: Path, store: MissionStore) -> dict[str, Any]:
    evidence = inspect_repository(repository)
    understanding = RequirementUnderstanding("Inspect this project", (), (), ())
    profile = derive_engineering_profile(evidence, understanding)
    contract = resolve_quality_contract(profile, evidence)
    mission_ids = store.list_ids()
    missions = []
    for mission_id in mission_ids[-MAX_MISSIONS:]:
        status = mission_status(store.load(mission_id), repository)
        missions.append(
            {
                key: value
                for key, value in status.items()
                if key not in {"stages", "checks", "baseline_checks", "pending_findings"}
            }
        )
    return {
        "schema_version": 4,
        "engine_version": VERSION,
        "repository": evidence.__dict__,
        "engineering_profile": asdict(profile),
        "quality_contract": asdict(contract),
        "missions": missions,
        "missions_truncated": len(mission_ids) > MAX_MISSIONS,
    }
