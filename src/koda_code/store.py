from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from .errors import KodaError
from .identity import STATE_DIRECTORY
from .models import Mission


class MissionStore:
    def __init__(self, repository: Path) -> None:
        self.repository = repository.resolve()
        self.root = self.repository / STATE_DIRECTORY / "missions"

    def save(self, mission: Mission) -> Path:
        folder = self._mission_folder(mission.mission_id)
        folder.mkdir(parents=True, exist_ok=True)
        self._refuse_symlink(folder)
        destination = folder / "mission.json"
        self._atomic_write(
            destination, json.dumps(mission.to_dict(), indent=2, sort_keys=True) + "\n"
        )
        self._atomic_write(folder / "brief.md", render_brief(mission))
        return destination

    def load(self, mission_id: str) -> Mission:
        path = self._mission_folder(mission_id) / "mission.json"
        self._refuse_symlink(path.parent)
        if not path.is_file() or path.is_symlink():
            raise KodaError(f"Mission not found: {mission_id}")
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise KodaError(f"Mission state is unreadable: {mission_id}") from exc
        return Mission.from_dict(data)

    def list_ids(self) -> list[str]:
        if not self.root.exists():
            return []
        self._refuse_symlink(self.root)
        return sorted(
            path.name
            for path in self.root.iterdir()
            if path.is_dir() and not path.is_symlink() and (path / "mission.json").is_file()
        )

    def _mission_folder(self, mission_id: str) -> Path:
        if not mission_id or any(
            character not in "abcdefghijklmnopqrstuvwxyz0123456789-" for character in mission_id
        ):
            raise KodaError(
                "Mission identifiers may contain lowercase letters, numbers, and hyphens."
            )
        return self.root / mission_id

    @staticmethod
    def _refuse_symlink(path: Path) -> None:
        current = path
        while current.exists():
            if current.is_symlink():
                raise KodaError(f"Refusing symlinked state path: {current}")
            if current.parent == current:
                break
            current = current.parent

    @staticmethod
    def _atomic_write(path: Path, content: str) -> None:
        if path.exists() and path.is_symlink():
            raise KodaError(f"Refusing symlinked state file: {path}")
        descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                handle.write(content)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)


def render_brief(mission: Mission) -> str:
    questions = (
        "\n".join(f"- {item}" for item in mission.understanding.product_questions) or "- None."
    )
    agents = "\n".join(f"- {item.agent.value}: {item.reason}" for item in mission.assignments)
    reasons = "\n".join(f"- {item}" for item in mission.approach.reasons)
    profile = mission.engineering_profile
    contract = mission.quality_contract
    profile_summary = (
        f"- Mode: {profile.project_mode.value}\n"
        f"- Important qualities: {', '.join(profile.quality_attributes)}\n"
        f"- Security surfaces: {', '.join(profile.security_surfaces) or 'none detected'}\n"
        f"- Compatibility surfaces: {', '.join(profile.compatibility_surfaces) or 'none detected'}"
        if profile is not None
        else "- Not resolved."
    )
    capability_summary = (
        "\n".join(
            f"- {item.name}: {item.state.value}"
            for item in contract.capabilities
            if item.state.value not in {"not_applicable"}
        )
        if contract is not None
        else "- Not resolved."
    )
    return f"""# Engineering Mission: {mission.mission_id}

## Requested outcome

{mission.request}

## Product questions

{questions}

## Proportionate approach

{mission.approach.summary}

{reasons}

## Engineering profile

{profile_summary}

## Adaptive quality contract

{capability_summary}

## Agent route

{agents}
"""
