# Development

## Setup

```bash
uv sync --python 3.11 --extra dev --locked
uv run koda --help
cd .vscode/koda-tools && npm ci && npm run check
```

## A complete local mission

```bash
uv run koda begin "Make configuration errors easier to understand" --repo .
uv run koda guide <mission-id> --repo .
uv run koda record <mission-id> --repo . \
  --agent engineer --outcome passed --note "Implemented with focused tests."
uv run koda record <mission-id> --repo . \
  --agent tester --outcome passed --note "Boundary and regression checks pass."
uv run koda record <mission-id> --repo . \
  --agent reviewer --outcome passed --note "Correct and proportionate."
uv run koda check <mission-id> --repo .
```

Use `--prepare-worktree` on `begin` for isolated mutable work. Use `finish` only from that contained
branch after every assigned role and quality check passes.

For the primary runtime, package and install the development VSIX, open this repository in VS Code,
and select **Koda** in GitHub Copilot Chat:

```bash
npm --prefix .vscode/koda-tools run package
code --install-extension .vscode/koda-tools/dist/koda-code-vscode.vsix
```

The extension resolves `koda.enginePath`, workspace `.venv/bin/koda`, PATH `koda`, then the local
development environment. It never installs or downloads the engine. For optional V2 autonomous CLI
execution, install and authenticate GitHub Copilot CLI, then run:

```bash
uv run koda begin "Improve configuration errors" --repo . --prepare-worktree
uv run koda run <mission-id> --repo .
```

The deterministic Python and extension suites use fake provider/engine processes and do not require
Copilot credits or live model calls.
Manual `guide`/`record` remains the fallback when Copilot is unavailable.

## Code conventions

- Keep domain policy pure where possible and side effects at explicit boundaries.
- Use dataclasses for mission data and functions for stateless decisions.
- Raise `KodaError` for actionable workflow failures.
- Keep command execution argv-only and bounded.
- Add a regression test with every bug fix.
