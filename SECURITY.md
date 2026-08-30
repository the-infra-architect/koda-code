# Security

## Supported versions

V1 is pre-release. Security fixes are applied to the latest `0.1.x` revision.

## Report a vulnerability

Report vulnerabilities privately to the repository owner. Do not disclose exploitable details in a
public issue.

## Deterministic safeguards

- Project discovery reads bounded filenames and metadata; it does not import or execute target code.
- Quality commands are argv arrays with an executable allowlist, sanitized environment, timeout, and
  bounded output. Shell syntax is rejected.
- Git commands use argv execution with prompts disabled.
- State writes are atomic and refuse symlinked state paths.
- Worktree branches and paths are derived conservatively and protected branches cannot deliver.
- Delivery stages only named paths, rejects unrelated pre-staged changes, and scans selected files
  for secret-like names and assignments.
- Push and pull-request creation require explicit flags.

These checks reduce common mistakes; they do not make arbitrary project code safe to execute. Only
run configured checks in a project you are authorized to execute.

