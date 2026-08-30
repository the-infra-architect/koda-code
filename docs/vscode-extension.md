# VS Code Manager and Extension

## User flow

Install the VSIX from `.vscode/koda-tools/dist`, open one or more project folders in VS Code, select
**Koda** in GitHub Copilot Chat, and describe the desired outcome. Koda inspects or resumes local
mission state, asks unresolved product-language questions one at a time, then coordinates native
Engineer, optional UI UX, Tester, Reviewer, and exceptional Debugger subagents sequentially.

Koda reports ready-to-finish only when the Python engine confirms every required role and the latest
deterministic checks. It does not stage, commit, push, or open a pull request.

## Tool contract

The repo-local runtime contributes Koda, its five hidden specialists, and seven language-model
tools: project inspection, begin, answer, status, Git evidence, verified result recording, and
deterministic checks. Read-only tools inspect local state. Begin, answer, record, and check show
meaningful confirmation messages. Tool inputs use JSON schemas and receive a second runtime
validation pass.

V4 keeps this tool surface unchanged. Project and status results now include a schema-versioned
engineering profile, adaptive capability states and verification, and stale-evidence status. The
extension passes these bounded results to Koda without translating `unknown`, `unavailable`, or
`not_applicable` into success.

`record` cannot arbitrarily pass a stage. The engine requires an assigned role, an isolated mission
worktree, an unchanged staging area, actual Git changes for mutable implementation roles, passing
checks for Tester and Reviewer, and a matching pre-role fingerprint for read-only Reviewer and
Debugger. Findings can cause at most two remediation rounds.

## Engine resolution and failure behavior

For each selected workspace, the extension resolves the first trusted option:

1. configured `koda.enginePath`;
2. workspace `.venv/bin/koda` (or the Windows equivalent);
3. `koda` on PATH;
4. the repository's existing `.venv` Python module when developing Koda itself.

Every candidate must identify as Koda-Code 0.4 or newer. The extension never installs dependencies
or downloads an executable. It launches argv arrays with no shell, a canonical workspace `cwd`, a
small environment allowlist, a configurable bounded timeout, a 256 KiB output limit, and VS Code
cancellation. Missing, incompatible, failed, timed-out, cancelled, malformed, and oversized engine
results return structured errors to the manager.

Multi-root workspaces require explicit repository selection. Nested repositories are allowed when
their canonical path remains inside an open folder; symlink escapes are rejected. Concurrent
mutating calls for the same workspace are rejected while the first call is running. Persistent
mission JSON remains authoritative across extension-host restarts.

## Development dependencies

The extension has no runtime npm dependencies. TypeScript and the VS Code/Node type packages provide
strict compilation, ESLint plus `typescript-eslint` provide static linting, and `@vscode/vsce`
performs deterministic VSIX packaging. Tests use Node's built-in test runner, so no test framework
dependency is needed.
