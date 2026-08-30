from __future__ import annotations

import hashlib
import re
from pathlib import Path

from .approach import choose_approach
from .discovery import inspect_repository
from .engineering import derive_engineering_profile, resolve_quality_contract
from .models import Mission, utc_now
from .repository import git
from .requirements import understand_request
from .routing import route_agents
from .store import MissionStore
from .workspace import create_mission_worktree


def mission_identifier(request: str, repository: Path) -> str:
    slug = "-".join(re.findall(r"[a-z0-9]+", request.lower())[:4]) or "software-change"
    digest = hashlib.sha256(f"{repository.resolve()}\0{request}".encode()).hexdigest()[:8]
    return f"{slug}-{digest}"[:72].rstrip("-")


def begin_mission(request: str, repository: Path, *, prepare_worktree: bool = False) -> Mission:
    evidence = inspect_repository(repository)
    understanding = understand_request(request, evidence)
    approach = choose_approach(understanding, evidence)
    profile = derive_engineering_profile(evidence, understanding)
    contract = resolve_quality_contract(profile, evidence)
    mission = Mission(
        mission_id=mission_identifier(request, Path(evidence.root)),
        request=understanding.requested_outcome,
        created_at=utc_now(),
        repository=evidence,
        understanding=understanding,
        approach=approach,
        assignments=route_agents(understanding),
        engineering_profile=profile,
        quality_contract=contract,
        engineering_fingerprint=profile.fingerprint,
        base_commit=git(Path(evidence.root), "rev-parse", "HEAD", check=False).stdout.strip()
        or None,
    )
    if prepare_worktree:
        worktree, branch = create_mission_worktree(Path(evidence.root), mission.mission_id, request)
        mission.worktree = str(worktree)
        mission.branch = branch
    MissionStore(Path(evidence.root)).save(mission)
    return mission
