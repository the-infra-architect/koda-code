from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path

from .answers import record_answer
from .delivery import finish_mission
from .errors import KodaError
from .evidence import mission_evidence, worktree_fingerprint
from .execution import RunReport, run_mission
from .identity import COMMAND_NAME, PRODUCT_NAME, VERSION
from .inspection import project_snapshot
from .models import AgentName, ExecutionStatus, Mission, Outcome, StageRecord
from .progress import record_verified_progress
from .prompts import render_agent_packet
from .quality import run_mission_checks
from .repository import repository_root
from .routing import add_debugger
from .status import mission_status, synchronize_ready_status
from .store import MissionStore, render_brief
from .workflow import begin_mission
from .workspace import validate_mission_worktree


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(
        prog=COMMAND_NAME,
        description="Turn a software request into a proportionate, verifiable engineering mission.",
    )
    root.add_argument("--version", action="version", version=f"{PRODUCT_NAME} {VERSION}")
    commands = root.add_subparsers(dest="command", required=True)

    begin = commands.add_parser(
        "begin", help="Understand a request and begin an engineering mission."
    )
    begin.add_argument("request")
    begin.add_argument("--repo", type=Path, default=Path.cwd())
    begin.add_argument("--prepare-worktree", action="store_true")
    begin.add_argument("--json", action="store_true")

    project = commands.add_parser(
        "project", help="Inspect the project and its local Koda missions."
    )
    project.add_argument("--repo", type=Path, default=Path.cwd())
    project.add_argument("--json", action="store_true")

    guide = commands.add_parser(
        "guide", help="Show the next assigned engineering role and its brief."
    )
    guide.add_argument("mission_id")
    guide.add_argument("--repo", type=Path, default=Path.cwd())
    guide.add_argument("--agent", choices=[item.value for item in AgentName])

    record = commands.add_parser("record", help="Record verified progress for an assigned role.")
    record.add_argument("mission_id")
    record.add_argument("--repo", type=Path, default=Path.cwd())
    record.add_argument("--agent", required=True, choices=[item.value for item in AgentName])
    record.add_argument("--outcome", required=True, choices=[item.value for item in Outcome])
    record.add_argument("--note", required=True)
    record.add_argument("--unclear-failure", action="store_true")
    record.add_argument("--verified-evidence", action="store_true")
    record.add_argument("--evidence-fingerprint")
    record.add_argument("--json", action="store_true")

    check = commands.add_parser(
        "check", help="Run the project's explicit deterministic quality gate."
    )
    check.add_argument("mission_id")
    check.add_argument("--repo", type=Path, default=Path.cwd())
    check.add_argument("--json", action="store_true")

    status = commands.add_parser("status", help="Show authoritative mission progress.")
    status.add_argument("mission_id")
    status.add_argument("--repo", type=Path, default=Path.cwd())
    status.add_argument("--json", action="store_true")

    evidence = commands.add_parser("evidence", help="Show bounded Git evidence for a mission.")
    evidence.add_argument("mission_id")
    evidence.add_argument("--repo", type=Path, default=Path.cwd())
    evidence.add_argument("--json", action="store_true")

    answer = commands.add_parser("answer", help="Record the next product clarification.")
    answer.add_argument("mission_id")
    answer.add_argument("--repo", type=Path, default=Path.cwd())
    answer.add_argument("--answer", required=True)
    answer.add_argument("--json", action="store_true")

    run = commands.add_parser(
        "run", help="Execute the mission autonomously with GitHub Copilot CLI."
    )
    run.add_argument("mission_id")
    run.add_argument("--repo", type=Path, default=Path.cwd())
    run.add_argument("--answer", help="Answer the one product question Koda is waiting on.")
    run.add_argument("--json", action="store_true")
    run.add_argument("--verbose", action="store_true")

    build = commands.add_parser(
        "build", help="Create an isolated mission and execute it with GitHub Copilot CLI."
    )
    build.add_argument("request")
    build.add_argument("--repo", type=Path, default=Path.cwd())
    build.add_argument("--answer", help="Answer the first product question when already known.")
    build.add_argument("--json", action="store_true")
    build.add_argument("--verbose", action="store_true")

    missions = commands.add_parser("missions", help="List local engineering missions.")
    missions.add_argument("--repo", type=Path, default=Path.cwd())

    finish = commands.add_parser(
        "finish", help="Commit verified work and optionally open a pull request."
    )
    finish.add_argument("mission_id")
    finish.add_argument("--repo", type=Path, default=Path.cwd())
    finish.add_argument("--path", action="append", default=[])
    finish.add_argument("--message", required=True)
    finish.add_argument("--push", action="store_true")
    finish.add_argument("--pull-request", action="store_true")
    return root


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        return _dispatch(args)
    except KodaError as exc:
        print(f"Cannot continue: {exc}")
        return 2


def _dispatch(args: argparse.Namespace) -> int:
    repository = repository_root(args.repo)
    store = MissionStore(repository)
    if args.command == "begin":
        mission = begin_mission(args.request, repository, prepare_worktree=args.prepare_worktree)
        print(json.dumps(mission.to_dict(), indent=2) if args.json else render_brief(mission))
        return 0
    if args.command == "project":
        payload = project_snapshot(repository, store)
        print(json.dumps(payload, indent=2) if args.json else _readable_project(payload))
        return 0
    if args.command == "build":
        mission = begin_mission(args.request, repository, prepare_worktree=True)
        if not args.json:
            print(f"Koda is building: {mission.request}")
            print(f"✓ Isolated change created: {mission.mission_id}")
        report = run_mission(
            mission,
            repository,
            store,
            answer=args.answer,
            progress=None if args.json else _print_progress,
        )
        _print_run_report(report, mission, json_output=args.json, verbose=args.verbose)
        return 0 if report.status is ExecutionStatus.READY_TO_FINISH else 1
    if args.command == "missions":
        ids = store.list_ids()
        print("\n".join(ids) if ids else "No engineering missions yet.")
        return 0

    mission = store.load(args.mission_id)
    if args.command == "guide":
        selected = AgentName(args.agent) if args.agent else None
        print(render_agent_packet(mission, selected))
        return 0
    if args.command == "record":
        agent = AgentName(args.agent)
        if agent not in {item.agent for item in mission.assignments}:
            raise KodaError(f"Agent is not assigned to this mission: {agent.value}")
        outcome = Outcome(args.outcome)
        if args.verified_evidence:
            record_verified_progress(
                mission,
                repository,
                store,
                agent=agent,
                outcome=outcome,
                note=args.note,
                evidence_fingerprint=args.evidence_fingerprint,
                unclear_failure=args.unclear_failure,
            )
            payload = mission_status(mission, repository)
            print(
                json.dumps(payload, indent=2)
                if args.json
                else f"Recorded {agent.value}: {outcome.value}"
            )
            return 0
        mission.stages[agent.value] = StageRecord(outcome=outcome, note=args.note.strip())
        if outcome is not Outcome.PASSED and args.unclear_failure:
            mission.assignments = add_debugger(mission.assignments, unclear_failure=True)
        store.save(mission)
        if args.json:
            print(json.dumps(mission_status(mission, repository), indent=2))
        else:
            print(f"Recorded {agent.value}: {outcome.value}")
        return 0
    if args.command == "check":
        mission.checks = run_mission_checks(mission, repository)
        execution_root = (
            validate_mission_worktree(mission, repository) if mission.worktree else repository
        )
        mission.check_fingerprint = worktree_fingerprint(execution_root)
        mission.execution_status = ExecutionStatus.PENDING
        synchronize_ready_status(mission, repository)
        store.save(mission)
        if args.json:
            print(json.dumps([record.__dict__ for record in mission.checks], indent=2))
        else:
            for record in mission.checks:
                print(f"{record.name}: {record.outcome} ({record.duration_seconds:.3f}s)")
        return (
            0 if mission.checks and all(item.outcome == "passed" for item in mission.checks) else 1
        )
    if args.command == "status":
        payload = mission_status(mission, repository)
        print(json.dumps(payload, indent=2) if args.json else _readable_status(payload))
        return 0
    if args.command == "evidence":
        payload = mission_evidence(mission, repository)
        print(json.dumps(payload, indent=2) if args.json else _readable_evidence(payload))
        return 0
    if args.command == "answer":
        record_answer(mission, repository, store, args.answer)
        payload = mission_status(mission, repository)
        print(json.dumps(payload, indent=2) if args.json else _readable_status(payload))
        return 0
    if args.command == "run":
        report = run_mission(
            mission,
            repository,
            store,
            answer=args.answer,
            progress=None if args.json else _print_progress,
        )
        _print_run_report(report, mission, json_output=args.json, verbose=args.verbose)
        return 0 if report.status is ExecutionStatus.READY_TO_FINISH else 1
    if args.command == "finish":
        execution_root = (
            validate_mission_worktree(mission, repository) if mission.worktree else repository
        )
        commit = finish_mission(
            mission,
            execution_root,
            args.path,
            args.message,
            push=args.push or args.pull_request,
            pull_request=args.pull_request,
        )
        store.save(mission)
        print(f"Delivered commit {commit}")
        return 0
    raise KodaError(f"Unknown command: {args.command}")


def _readable_project(payload: dict[str, object]) -> str:
    repository = payload["repository"]
    missions = payload["missions"]
    assert isinstance(repository, dict)
    assert isinstance(missions, list)
    return f"Project: {repository['root']}\nMissions: {len(missions)}"


def _readable_status(payload: dict[str, object]) -> str:
    return (
        f"Mission: {payload['mission_id']}\n"
        f"Status: {payload['execution_status']}\n"
        f"Next agent: {payload['next_agent'] or 'none'}\n"
        f"Ready to finish: {'yes' if payload['ready_to_finish'] else 'no'}"
    )


def _readable_evidence(payload: dict[str, object]) -> str:
    changed = payload["changed_paths"]
    assert isinstance(changed, list)
    return (
        f"Branch: {payload['branch']}\n"
        f"Changed paths: {', '.join(str(item) for item in changed) or 'none'}\n"
        f"Fingerprint: {payload['fingerprint']}"
    )


def _print_progress(event: str, role: AgentName | None) -> None:
    label = role.value.replace("_", " ").title() if role else "mission"
    if event == "starting":
        print(f"→ {label} is working...")
    elif event == "passed":
        print(f"✓ {label} complete")
    elif event == "validation_failed":
        print("→ Deterministic checks found a problem; Engineer is repairing it...")
    elif event == "remediating":
        print(f"→ Findings require another {label} pass...")


def _print_run_report(
    report: RunReport,
    mission: Mission,
    *,
    json_output: bool,
    verbose: bool,
) -> None:
    if json_output:
        payload = report.to_dict()
        payload["mission_id"] = mission.mission_id
        print(json.dumps(payload, indent=2))
        return
    print(report.message)
    if report.status is ExecutionStatus.WAITING_FOR_INPUT:
        print("Rerun with --answer after deciding this product behavior.")
    elif report.status is ExecutionStatus.BLOCKED:
        print("The isolated worktree was preserved. No commit, push, or pull request was made.")
    if verbose:
        print(f"Worktree: {report.worktree}")
        print(f"Copilot calls this run: {report.calls}")
        if report.sandboxed is not None:
            print(f"Local Copilot sandbox: {'enabled' if report.sandboxed else 'unsupported'}")


if __name__ == "__main__":
    raise SystemExit(main())
