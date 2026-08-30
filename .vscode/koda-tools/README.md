# Koda-Code repo-local VS Code runtime

This repo-local runtime contributes the `Koda` manager, its five hidden specialists, and seven
language-model tools. It never calls a model itself. It invokes the trusted Koda 0.4+ Python engine
with argv arrays and schema-versioned JSON output, while VS Code supplies the model and native
subagents.

Koda V4 preserves `unknown`, `unavailable`, and `not_applicable` engineering capability states and
re-resolves stale engineering evidence through the deterministic check tool. The manager is the
only user-visible Koda agent; bundled specialists are available only for explicit delegation.

Open the repository in VS Code, install this extension, select **Koda**, and describe the software
outcome. For development, `npm run check` validates the runtime and `npm run package` creates a VSIX
under `dist/`.
