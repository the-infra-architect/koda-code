# Koda-Code

Koda-Code is an intent-first AI-assisted coding workflow. It
helps turn a plain-language software outcome into an evidence-based engineering mission, routes only
the roles that add value, and requires deterministic proof before delivery.

V4 adds an evidence-backed engineering profile and adaptive quality capability contract. Koda now
distinguishes greenfield selection from existing-project adoption; resolves security,
compatibility, data, supply-chain, distributed-system, and test obligations from actual surfaces;
and reports unknown or unavailable verification honestly instead of applying a universal checklist.

The user can be a beginner or an expert. Beginners describe what people need to accomplish; the
system inspects the project and asks only product-language questions it cannot answer safely.
Technical users can provide explicit architecture constraints, which are honored unless they
conflict with correctness, safety, feasibility, or the requested outcome.

The governing principle is:

> Use the least complex solution that fully satisfies the actual requirements while preserving
> correctness, readability, maintainability, security, performance, and reasonable resource use.

Complexity is permitted. Unjustified complexity is not.

## What Koda does

The primary V4 experience preserves the **Koda** custom agent in VS Code's GitHub Copilot Chat.
Koda uses native VS Code subagents for focused engineering roles and a small extension tool surface
for authoritative mission state, Git evidence, and deterministic checks:

```text
User outcome
  → evidence and product questions
  → proportionate technical approach
  → isolated implementation
  → targeted agent collaboration
  → deterministic quality gate
  → guarded commit, push, and pull request
```

Open the project in VS Code, install the runtime from `.vscode/koda-tools`, select **Koda** in
Copilot Chat, and describe the outcome. Koda coordinates Engineer, optional UI/UX, Tester, Reviewer,
and Debugger sequentially. It stops at `VERIFIED / READY TO FINISH`; it never commits or pushes.

The Python CLI remains the authoritative engine and a useful manual interface:

```bash
koda begin "Build an inventory tracking page" --repo /path/to/project
koda project --repo /path/to/project --json
koda status <mission-id> --repo /path/to/project --json
koda evidence <mission-id> --repo /path/to/project --json
koda answer <mission-id> --repo /path/to/project --answer "Keep this local."
koda guide <mission-id> --repo /path/to/project
koda record <mission-id> --repo /path/to/project \
  --agent engineer --outcome passed --note "Implemented and verified the inventory flow."
koda check <mission-id> --repo /path/to/project
koda finish <mission-id> --repo /path/to/project \
  --path src/inventory.py --path tests/test_inventory.py --message "Add inventory tracking"
```

Add `--prepare-worktree` to `begin` when the target is already a Git repository and isolated mutable
work should start immediately.

The optional V2 compatibility path can still execute a mission through GitHub Copilot CLI:

```bash
koda begin "Add customer search" --repo /path/to/project --prepare-worktree
koda run <mission-id> --repo /path/to/project
```

For a beginner-facing one-command start:

```bash
koda build "Add customer search" --repo /path/to/project
```

`run` and `build` stop at `VERIFIED / READY TO FINISH`. They never commit, push, or open a pull
request. Use the guarded `finish` command separately after reviewing the isolated change. If Koda
needs a material product decision, it asks one question and resumes with
`koda run <mission-id> --answer "..."`.

## Install for development

Requirements: Python 3.11+, Git, and `uv`. The primary experience also requires VS Code, GitHub
Copilot Chat, Node.js 24+ for extension development, and the local Koda extension. Copilot CLI is
required only for the optional `koda run` / `koda build` compatibility path.

```bash
uv sync --python 3.11 --extra dev --locked
uv run koda --help
uv run koda begin "Improve the error message" --repo .
cd .vscode/koda-tools && npm ci && npm run check && npm run package
```

There are no third-party runtime dependencies. Development tools are locked in `uv.lock`.

## Important boundaries

- VS Code and GitHub Copilot Chat provide the primary model and native-subagent runtime. The
  extension never calls a model, downloads Koda, or requires Copilot CLI.
- The optional V2 `run` / `build` commands use GitHub Copilot CLI. Their absence does not affect the
  VS Code manager or manual engine commands.
- Agent files are focused engineering contracts for use by a compatible coding assistant.
- Runtime role prompts are bundled in `.vscode/koda-tools/`; `.github/agents/` contains synchronized
  workspace-discovery mirrors.
- Project checks are explicit argv arrays. They never run through a shell.
- Push and pull-request creation are opt-in.
- Local mission state is gitignored and remains with the project.
- A database is not used because Koda has no workload that needs one. Embedded analytics may use
  DuckDB later only when real analytical or file-processing requirements justify it.

Read [ARCHITECTURE.md](ARCHITECTURE.md),
[docs/v4-adaptive-engineering.md](docs/v4-adaptive-engineering.md),
[docs/vscode-extension.md](docs/vscode-extension.md),
[docs/autonomous-execution.md](docs/autonomous-execution.md), [docs/agents.md](docs/agents.md), and
[docs/development.md](docs/development.md) before extending the workflow.
