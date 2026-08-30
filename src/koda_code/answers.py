from __future__ import annotations

from pathlib import Path

from .copilot import sanitize_output
from .engineering import resolve_mission_engineering
from .errors import KodaError
from .evidence import changed_paths
from .models import ExecutionStatus, Mission, MissionAnswer
from .status import next_product_question
from .store import MissionStore

MAX_ANSWER_LENGTH = 4000


def record_answer(
    mission: Mission,
    repository: Path,
    store: MissionStore,
    answer: str,
) -> None:
    if Path(mission.repository.root).resolve() != repository.resolve():
        raise KodaError("Mission belongs to a different project.")
    question = next_product_question(mission)
    if question is None:
        raise KodaError("There is no pending product question to answer.")
    cleaned = sanitize_output(" ".join(answer.split()))
    if not cleaned:
        raise KodaError("The supplied answer is empty.")
    if len(cleaned) > MAX_ANSWER_LENGTH:
        raise KodaError(f"The supplied answer exceeds {MAX_ANSWER_LENGTH} characters.")
    mission.answers.append(MissionAnswer(question, cleaned))
    mission.waiting_question = next_product_question(mission)
    mission.execution_status = (
        ExecutionStatus.WAITING_FOR_INPUT
        if mission.waiting_question is not None
        else ExecutionStatus.PENDING
    )
    execution_root = Path(mission.worktree) if mission.worktree else repository
    resolve_mission_engineering(
        mission,
        execution_root,
        changed_paths=changed_paths(execution_root),
    )
    store.save(mission)
