# Autonomous Execution

This document describes the optional V2 Copilot CLI compatibility path. V3's primary runtime is the
Koda custom agent in VS Code; see [vscode-extension.md](vscode-extension.md). The two paths share the
same Python mission, worktree, evidence, remediation, quality, and delivery policies.

`koda run <mission-id> --repo /path/to/project` executes an existing prepared mission. `koda build
"<outcome>" --repo /path/to/project` is a thin `begin --prepare-worktree` plus `run` wrapper.

## Copilot requirement

This optional execution path requires GitHub Copilot CLI to be installed and authenticated. Koda
inspects `copilot --version` and `copilot help` before relying on the installed command. An absent
or incompatible executable blocks only `run`/`build`; `begin`, `guide`, `record`, `check`,
`missions`, and `finish` retain their manual behavior.

Koda invokes `copilot -p` with an argv array, an explicit worktree `cwd`, a sanitized environment, a
30-minute role timeout, bounded output, no remote session/export, no built-in GitHub MCP server, and
no transcript sharing. It never uses `--allow-all`, `--allow-all-paths`, or `--yolo`.

When the installed CLI advertises its experimental per-session `--sandbox` option, Koda enables it
without changing permanent Copilot settings. When unavailable, Koda reports reduced isolation and
continues with explicit role permissions plus its own worktree/Git checks.

## Role flow and isolation

The normal route is Engineer, optional UI/UX, Tester, deterministic validation, then Reviewer. Every
role is a new Copilot process:

- Engineer receives the outcome, constraints, project evidence, constitution, resolved answers,
  and repair findings when applicable.
- UI/UX receives the requested interaction, changed UI evidence, and existing conventions.
- Tester receives the outcome and actual diff/changed paths, but not Engineer reasoning.
- Reviewer receives the outcome, actual diff, and deterministic validation, but not Engineer
  reasoning. Its tools are read-only.
- Debugger is read-only and appears only for a reproducible failure whose cause Tester marks unclear.
  It returns diagnosis to a subsequent Engineer repair.

Mutable roles may read/write the worktree and run explicitly approved common local toolchain and
read-only Git commands. They do not receive blanket shell approval. All roles are denied commit,
staging, push, branch/config/history changes, `gh`, URL, memory, and built-in GitHub MCP access. Koda
rejects a changed HEAD or staging area. Reviewer and Debugger results are also rejected if file
evidence changes.

## Evidence, remediation, and resume

Every role must return one validated JSON object with `pass`, `changes_required`, `needs_input`, or
`blocked`. Koda does not trust claims about changed files or tests: it derives changed paths and diff
from Git and runs `koda-code.toml` checks itself.

Tester, UI/UX, Reviewer, or deterministic-check findings route back to Engineer. The repaired change
then passes through the applicable downstream roles and validation again. A mission receives at most
two remediation rounds. Remaining failures stop with evidence in the isolated worktree.

Attempts are atomically saved before Copilot launches. A failed process, timeout, malformed result,
quota failure, or interruption does not pass the stage. Running the same `koda run` command resumes
at the incomplete role. Accepted repository fingerprints prevent stale evidence: if files change
between runs, Koda reruns the affected downstream UI, test, validation, and review stages. A material
ambiguity pauses with one product-language question; answer it with `--answer` and rerun.

## Delivery boundary

Successful execution ends at `VERIFIED / READY TO FINISH`. Agents cannot commit, push, create a pull
request, or mark deterministic checks passed. After review, use `koda finish` with exact paths and a
commit message. Existing secret scanning, protected-branch checks, explicit staging, and optional
push/pull-request flags remain in force.
