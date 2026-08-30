# Agent System

Koda uses five coding-product roles. It does not invoke all five for every mission.

The VS Code custom agent named **Koda** is the only user-visible manager. The canonical bundled
definitions live under `.vscode/koda-tools/agents/` and are mirrored under `.github/agents/` for
workspace discovery. Koda calls these specialists through VS Code's native subagent tool, one at a
time, and records results only through the Python engine's verified evidence contract. Specialists
are hidden with `user-invocable: false` and cannot be selected implicitly. Koda's exact allowlist is
Engineer, UI UX, Tester, Reviewer, and Debugger.

## Engineer

Always assigned. Understands the requested outcome, inspects the project and environment, honors
explicit constraints, chooses a proportionate approach, implements it, and reports evidence.

## UI/UX

Assigned after Engineer only when the request meaningfully changes a page, screen, form, dashboard,
or other user interface. It may make focused interface improvements before independent testing.

## Tester

Always assigned after implementation. Independently challenges acceptance behavior, boundaries,
failure cases, and regression risk. It does not merely echo the implementation.

## Reviewer

Always assigned after testing and any relevant interface review. Reviews correctness, readability,
naming, useful typing, duplication, security, resource use, performance, dependencies, framework
conventions, test quality, overengineering, and underengineering.

## Debugger

Not assigned initially. It is inserted only after a failed stage is recorded with an unclear root
cause. In autonomous mode it is read-only: it isolates and explains the root cause, then Engineer
performs the repair and adds regression evidence.

`koda guide <mission-id>` renders a role packet from the same mission evidence and
technical approach. Agent completion is recorded explicitly; text output is never assumed to be
proof of execution.

In the primary V4 flow, Koda launches each role as a native VS Code subagent. Tester and Reviewer
receive actual bounded Git evidence but never Engineer's private reasoning. The optional V2
`koda run <mission-id>` compatibility path still launches fresh GitHub Copilot CLI processes. See
[vscode-extension.md](vscode-extension.md) and [autonomous-execution.md](autonomous-execution.md).
