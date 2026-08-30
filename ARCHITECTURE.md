# Architecture

## Product boundary

Koda-Code is an intent-to-delivery workflow. Repository discovery, Git worktrees, quality
commands, and pull requests are supporting mechanisms. The product abstraction is an engineering
mission created from a requested user outcome.

## Components

- `requirements.py` translates the request into capability signals, explicit technical constraints,
  and questions phrased in product language.
- `discovery.py` gathers bounded, non-executing evidence from the target project.
- `engineering.py` derives V4 engineering profiles, technology-neutral quality contracts,
  enforcement levels, storage topology decisions, stale fingerprints, and verification semantics.
- `ci_security.py` performs bounded GitHub Actions-specific privileged-code checks, while
  `vulnerabilities.py` preserves vulnerability evidence and explicit license-policy decisions.
- `approach.py` uses that evidence to recommend a proportionate direction and records which
  complexity is justified, avoided, or deferred.
- `routing.py` assigns Engineer, Tester, and Reviewer, adding UI/UX only for meaningful interface
  work and Debugger only after an unclear failure.
- `workflow.py` creates the mission and optionally prepares an isolated Git worktree.
- `prompts.py` creates role-specific packets tied to the mission rather than generic specialist work.
- `evidence.py`, `status.py`, `progress.py`, and `answers.py` expose the same bounded evidence and
  verified-transition policies to every runtime.
- `.vscode/koda-tools/` is the repo-local VS Code runtime. It bundles the manager and specialists,
  resolves a trusted local Koda executable, invokes JSON CLI commands without a shell, and
  contributes language-model tools to VS Code.
- `copilot.py` implements the single GitHub Copilot CLI process boundary: capability detection,
  role permissions, bounded subprocess execution, result parsing, and output redaction.
- `execution.py` runs fresh role processes sequentially, verifies Git evidence, routes bounded
  remediation, persists resumable attempts, and stops at ready-to-finish.
- `quality.py` runs explicit no-shell project checks with bounded output and timeouts, re-resolves
  V4 evidence after material changes, and attributes failures against an isolated base-commit
  checkout when possible.
- `delivery.py` requires completed roles, a passing quality gate, exact staging, secret scanning, and
  a non-protected branch before committing or optionally opening a pull request.
- `store.py` atomically persists local mission briefs and evidence under a gitignored directory.

These modules are boundaries around different policies, not a service framework. Koda runs in one
process, uses the standard library at runtime, and has no queue, server, provider registry, or
database. V3 uses VS Code's model and native subagent runtime; the older direct Copilot CLI path
remains isolated in `copilot.py` and `execution.py`.

V4 adds plain dataclasses, enums, and pure resolver functions rather than a generic policy engine.
Research traceability and the precise support boundary are documented in
[docs/v4-adaptive-engineering.md](docs/v4-adaptive-engineering.md).

## VS Code boundary

The repository custom agent is the only user-visible manager. It may invoke exactly Engineer,
UI UX, Tester, Reviewer, and Debugger through VS Code's native `agent` tool. Specialist agents are
hidden from the picker and cannot be selected implicitly. The extension registers seven tools:
project, begin, answer, status, evidence, record, and check. It does not provide a chat participant,
model provider, MCP server, shell tool, custom UI, or duplicate workflow engine.

All model-originated input is schema-checked and validated again at runtime. Workspace selection is
canonicalized against open folders, subprocesses use argv with `shell: false`, output and time are
bounded, cancellation terminates the child, and one mutating invocation per workspace is allowed.
The Python engine still owns repository discovery, worktree containment, state transitions,
adaptive profiles/contracts, remediation limits, check execution, and ready-to-finish eligibility.

## Autonomous execution boundary

Each mutable invocation runs with `cwd` set to the mission's recorded sibling worktree. Koda checks
the repository relationship, expected worktree location, branch, HEAD, staging area, and stable
checkout before accepting a result. Engineer, UI/UX, and Tester may edit; Reviewer and Debugger are
read-only. Each receives fresh role-specific context rather than a shared conversation.

Copilot output is advisory until a small JSON result is parsed and repository evidence agrees.
Changed paths come from Git, and configured quality checks remain authoritative. At most two
Engineer remediation rounds may be caused by test, UI, review, or deterministic-check findings.
Delivery remains outside this state machine and is available only through `finish`.

## Technical decisions

The system prefers existing project conventions over category-to-stack mappings. When no reliable
stack evidence exists, it defers irreversible framework and storage choices until the relevant
product questions are answered. An explicit expert constraint is preserved unless there is a
concrete conflict.

See [docs/decisions/0001-intent-first-missions.md](docs/decisions/0001-intent-first-missions.md).
