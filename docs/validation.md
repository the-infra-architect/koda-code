# Validation

`koda-code.toml` is the explicit quality contract for this repository. The `check` command
parses each argv array, rejects unapproved executables and shell syntax, sanitizes the environment,
applies a timeout, bounds captured output, and stops after a failure.

The repository gate covers Python formatting, linting, strict typing, tests with branch coverage,
package build, static security analysis, tracked-file secret scanning, dependency vulnerability
auditing, plus extension compilation, linting, deterministic unit tests, and VSIX packaging.

Neither VS Code subagent output nor V2 autonomous role results can waive this gate. Koda runs the
target worktree's explicit checks after Tester and requires the latest records to pass before
Reviewer approval can become ready-to-finish. Provider tests are deterministic and simulate
success, malformed JSON, process failure, timeout, authentication/quota errors, worktree
containment, role permissions, remediation, resume, output redaction, and validation failure.

External hosted checks must be reported separately from deterministic local results. An unavailable
hosted service does not erase a local failure and is not evidence that the hosted check passed.

V4 resolves a technology-neutral quality capability contract before checks run and re-resolves it
after material worktree changes. Capability resolution (`existing`, `required`, `recommended`,
`unavailable`, `not_applicable`, `unknown`) is separate from verification (`not_run`, `passed`,
`failed`, `unavailable`, `not_applicable`). Unknown, unavailable, and not-applicable never become
green checks. Existing numeric thresholds such as this repository's coverage gate remain project
policy; Koda introduces no universal threshold.

When an isolated mission check fails, Koda attempts the same argv check at the recorded base commit
inside a temporary detached worktree. The check is attributed as introduced, pre-existing, or
unknown without mutating the stable checkout.
