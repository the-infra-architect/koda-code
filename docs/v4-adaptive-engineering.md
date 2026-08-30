# V4 adaptive engineering

Koda-Code V4 derives a bounded engineering profile from repository evidence, the requested change,
explicit constraints, recorded product answers, and changed paths. It then resolves a
technology-neutral quality capability contract. This layer guides Koda and its existing five hidden
specialists; it does not choose a stack from a project category and does not add specialist agents.

The permanent research snapshot lives in
`docs/research/v4-software-practices/`. No research correction was needed during implementation.
Non-obvious behavior below follows the pack's claim (`C…`) and conditional-rule (`R…`) identifiers.

## Engineering profile

The profile records only decision-relevant evidence:

- existing versus greenfield mode;
- detected ecosystems and honest support level;
- package managers, lockfiles, native lifecycle commands, monorepo and migration tools;
- deployment/access topology and important quality attributes;
- security, compatibility, data/storage, supply-chain, and distributed-system surfaces;
- environment restrictions, changed surfaces, unresolved questions, and concise decisions.

Existing projects preserve repository instructions, scripts, wrappers, package/lock strategy,
test/type/style policy, migration mechanism, CI provider, and architecture by default (`C038`,
`C039`, `C045`, `R001`). Greenfield work asks only material facts that cannot be inferred, one at a
time through the existing mission question flow and in product language (`C037`, `C043`, `R024`,
`R025`). Architecture follows the least complex design that satisfies the detected qualities and
constraints, not minimum component count (`C001`–`C003`, `R002`–`R004`).

## Ecosystem support

`native_lifecycle` means Koda detects the native configured lifecycle or repository scripts; it does
not promise generated architecture expertise. `detection_only` means Koda can identify a surface
and route/review it without claiming full execution support.

| Ecosystem | V4 support |
|---|---|
| Python | native lifecycle from project/Koda configuration; preserves uv/Poetry/PDM/lock evidence |
| JavaScript/TypeScript | native package scripts and npm/pnpm/Yarn/Bun lock evidence |
| Maven/Java | native wrapper/lifecycle command resolution |
| Gradle/JVM | native wrapper/check/test resolution |
| .NET | native build/test detection |
| Rust/Cargo | native fmt/clippy/test detection |
| Go | native vet/test and module/workspace detection |
| Nx/Turborepo/workspaces | native graph/affected mechanism reuse; no second graph (`C035`, `R022`) |
| GitHub Actions and Sonar | detection/review only; existing policy is preserved (`C041`, `C052`) |
| Containers, IaC, migrations, data tools | bounded surface detection; no generated blueprint claim |

Configured `koda-code.toml` argv checks remain the only authoritative executable quality gate. A
detected command is evidence of an existing mechanism, not permission to execute an arbitrary
repository script (`C044`).

## Quality contract

Capabilities are technology-neutral: format, lint, type/compile, unit, integration, E2E,
build/package, secret/dependency/static/web security, fuzz/property, accessibility,
performance/load, migration/data integrity, recovery, compatibility, documentation, CI mirror/CI
security, dependency reproducibility, component inventory, provenance, artifact integrity,
authorization, input validation, secure defaults, observability, idempotency, cache consistency,
and retry safety.

Each capability has one resolution state:

- `existing` — repository evidence provides a mechanism;
- `required` — a concrete change surface creates an obligation;
- `recommended` — valuable, but not a universal mission gate;
- `unavailable` — relevant verification could not run; never a pass;
- `not_applicable` — its trigger is absent; never a pass;
- `unknown` — material evidence is unresolved; never a pass.

Verification is separate: `not_run`, `passed`, `failed`, `unavailable`, or `not_applicable`.
Configured check failures and unavailable required mechanisms block readiness. Specialist stages and
the deterministic repository gate remain authoritative together; an agent's prose never converts a
gap into success (`C020`, `C071`, `R026`). Profile/contract fingerprints exclude local mission-state
noise and become stale when decision-relevant repository/change evidence changes. Running `check`
re-resolves the profile before verification.

The enforcement level explains why a result matters:

1. hard invariant — deterministic containment, real-secret, unsafe-shell, malformed-output, and
   honest-verification boundaries;
2. existing project policy — repository coverage/type/lint/Sonar/vulnerability/license/delivery
   policy;
3. context-required — accessibility, compatibility, migration, authorization, integration,
   recovery, idempotency, and similar capabilities after a trigger exists;
4. recommendation — useful additions whose absence does not automatically fail;
5. reviewer signal — qualitative maintainability/proportionality judgment;
6. deferred — unsupported universal scores, thresholds, stacks, databases, or superiority claims.

This implements the promotion matrix rather than a configurable policy language. No universal
coverage percentage, function size, complexity score, vulnerability severity, license conclusion,
database, Docker, Sonar, hosted-CI, or observability-stack rule was added (`C008`, `C010`, `C013`,
`C039`, `C070`, `R008`, `R019`, `R021`, `R028`).

## Risk and domain resolution

Testing follows behavior and risk: focused unit tests for logic/invariants, integration tests at
DB/filesystem/network/framework/process boundaries, E2E for changed critical journeys, and
fuzz/property/performance checks only with their concrete triggers (`C010`–`C014`, `R007`, `R008`,
`R011`). Existing coverage thresholds remain Level 2 project policy.

Security follows detected exposure, identity/access, untrusted input/files, queries, process
execution, secrets, dependencies, sensitive data, tenancy, network/browser/plugin, and CI surfaces
(`C015`–`C019`, `C056`, `C059`, `C068`, `R009`). Secure defaults are a user-facing requirement,
not a request for a large settings surface. The GitHub Actions inspector checks declared
least-privilege permissions, contributor-controlled expression interpolation into executable text,
obvious secret printing, third-party action reference policy, and OIDC only when compatible cloud
authentication exists (`C024`, `C052`, `C053`, `C067`, `R020`). It makes no support claim for other
CI providers.

Storage decisions use workload, writer topology, concurrency, locality, value, sensitivity,
availability, migration, and existing infrastructure. Local single-process analytics can make
DuckDB suitable. A native read-write DuckDB file on SMB/NFS/NAS is rejected as a default; read-only
shared analytical input is distinct. Multiple transactional writers produce a coordinated
ownership/client-server requirement signal without automatically choosing PostgreSQL (`C029`–
`C034`, `R014`–`R017`). Persistent changes separately trigger datastore-invariant, transaction,
migration-overlap, and recovery reasoning (`C061`, `C062`, `C066`).

Compatibility is triggered only by evidence of stable public library/API/CLI/config/persisted/event/
multi-version DB/plugin contracts. Internal helper refactors do not invent a public gate. Existing
version/deprecation policy wins; SemVer is not imposed (`C046`–`C049`).

Dependency reproducibility, SBOM/component inventory, build provenance, artifact integrity, and CI
security remain distinct and are resolved from artifact role, distribution, risk, and policy
(`C050`–`C055`). Vulnerability triage distinguishes new blocking, new review, pre-existing,
evidenced-not-affected, fixed, unknown, and tool-unavailable states. `not_affected` requires evidence;
severity and license gates require project/user policy (`C069`–`C072`).

Queues/events trigger duplicate delivery, ordering, idempotency, poison-message, schema, eventual-
consistency, and dual-write reasoning. Caches trigger freshness/invalidation/capacity semantics.
Retries are transient-only and bounded. Explicit microservices are respected while carrying their
contract/failure/operational costs; arbitrary service splits are reviewer signals (`C027`,
`C063`–`C065`, `R011`–`R013`, `R025`).

## Baselines and compatibility

When a mission check fails in an isolated worktree, Koda can run that failed argv check at the
recorded base commit in a temporary detached worktree. Results are marked `introduced`,
`preexisting`, or `unknown`; unrelated legacy debt is not silently disabled or falsely attributed.
The temporary checkout is removed after the comparison.

Mission JSON schema version 4 adds optional profile, contract, base-commit, fingerprint, and
baseline records. The loader still accepts V3 state with schema version 3 defaults. CLI command
names and the seven VS Code tools are unchanged. `project` and `status` were enriched atomically;
the extension continues to validate inputs, bound output, avoid shells, handle cancellation, and
pass structured capability states through unchanged.

## Deliberate V1–V3 changes

- Repository discovery now records native ecosystem/tooling evidence instead of only languages,
  broad frameworks, tests, CI, UI, and database-name hints.
- Binary check success is supplemented by explicit capability resolution/verification states;
  unavailable, unknown, and not-applicable are no longer representable as implied success.
- Product answers now re-resolve architecture-relevant profile evidence.
- Failed checks can distinguish introduced from pre-existing baseline failures.
- Specialist prompts receive concise role-relevant profile/contract context, while Koda remains the
  only visible manager and the specialist list is unchanged.
- Public JSON is versioned as schema 4 while retaining V3 mission loading.

## Known limitations

- Detection is bounded and marker/script based; it does not prove framework semantics or discover
  every custom task runner.
- GitHub Actions is the only CI provider with V4-specific static security inspection.
- Capability verification is strongest for commands in `koda-code.toml`; qualitative requirements
  still rely on bounded specialist review plus deterministic repository evidence.
- Baseline commands may be unavailable in the clean detached checkout when a project depends on
  machine-local generated environments; Koda reports `unknown` rather than guessing.
- V4 does not benchmark live model quality, provision infrastructure, publish artifacts, make legal
  license decisions, or rank dependency popularity/health.

V5 should use real Koda mission telemetry to refine detection precision, determine which additional
ecosystems deserve tested execution adapters, and evaluate model-assisted outcomes separately. It
should not be implemented until those concrete gaps have evidence.
