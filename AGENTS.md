# Agent Guide

## Start here

Read `README.md`, `ARCHITECTURE.md`, the relevant mission brief under `.koda-code/`, and only
the files needed for the task. Inspect before editing and state assumptions when evidence is missing.

## Engineering contract

- Solve the requested user outcome, not an imagined platform.
- Honor explicit technical constraints unless a concrete conflict is documented.
- Prefer project conventions and the least complex correct implementation.
- Use plain functions, dataclasses, classes, interfaces, frameworks, and services only when each has
  a concrete reason.
- Treat security, failure behavior, performance, CPU, memory, I/O, and dependency cost as normal
  engineering considerations.
- Add meaningful tests and report exact validation evidence.

## Git containment

Never push directly to `main`, `master`, `trunk`, or `production`. Use a focused feature, fix, or
refactor branch, preferably in an isolated worktree for concurrent mutable work. Use pull requests
where a hosted remote exists. Never force push as part of the normal workflow.

## Quality gate

Before merge, run `uv run koda check <mission-id>` or every equivalent command in
`koda-code.toml`. Do not claim completion while a deterministic check fails.

## Engine maintenance

After a major milestone or unusually large debugging context, recommend compacting the conversation.
After the same test failure repeats more than three times, stop guessing, preserve the evidence, and
request focused review.

