# Domain Findings — Iterations 1–3

## Architecture and simplicity

The research rejects a one-dimensional “simplicity score.” Software quality has multiple attributes and architecture is about tradeoffs. Koda should seek the **least complex design that satisfies the project's important qualities**, not the fewest files/services/classes.

This allows both:
- a tiny local tool with a tiny architecture;
- a distributed system using Kafka/Redis/Kubernetes when throughput, isolation, scaling, reliability, ownership, or deployment requirements justify them.

## Readability / maintainability / abstractions

Strong practitioner and SEI evidence supports clarity, descriptive naming, consistency, maintainability, coupling/cohesion awareness, and challenging unnecessary complexity.

No strong evidence supports universal rules like:
- function ≤ N lines;
- class ≤ N methods;
- one-implementation interface = wrong;
- every duplicate line must be abstracted;
- complexity score > X = automatic refactor.

Those should remain reviewer signals unless the project already has a policy.

## Typing

Useful specificity is valuable, but a global strictness change can be a migration. Koda should improve touched code where useful without imposing a new type-system religion on an existing codebase.

## Testing

The strongest research result is that **test adequacy is contextual**. Use fast/reliable tests, integration tests at meaningful boundaries, E2E for critical journeys, and nonfunctional tests when the relevant risk exists. Coverage reveals gaps; it does not prove quality.

Mutation, fuzz, property, load, accessibility and migration tests are conditional tools, not ceremonial defaults.

## Security

NIST/OWASP support integrated secure development and multiple verification techniques. The correct V4 move is a threat-surface model:
- exposed web/API;
- auth/authorization;
- untrusted input/files;
- secrets;
- dependencies;
- persistence/data sensitivity;
- command/file/network capability.

Controls should follow actual surfaces.

## AI-generated code

The evidence supports Koda's existing trust model: agent output is a proposal. Git, filesystem state, deterministic tests, static analysis and explicit quality checks are evidence. Never infer “pass” from prose.

## Dependencies / reproducibility

Different ecosystems achieve reproducibility differently. Existing package manager, wrapper, lockfile and scripts are stronger evidence than Koda's preference. V4 should model capabilities, not tools.

## Performance / resources

Koda should catch obvious engineering problems—N+1 access, repeated scans, huge materialization, needless copies, blocking misuse, leaks, pathological complexity—while requiring realistic measurement before introducing complex caches, queues, concurrency or low-level optimizations.

## Reliability

AI often adds retries as “robustness.” Research says retries belong around likely transient failures only, should be bounded, and must respect timeout/idempotency/backoff semantics. Nested retry layers can be harmful.

## Observability

Production services may need structured logs, health, metrics and traces. A local script may need only clear errors. “Add OpenTelemetry” is not a universal best practice.

## Persistent data

Database engineering includes:
- writer topology;
- transactionality;
- read/write pattern;
- storage location;
- consistency/concurrency;
- backup/recovery;
- migration/downtime.

This is more important than brand preference.

## DuckDB correction

DuckDB remains an excellent choice for embedded analytical/OLAP workloads. But its own current docs warn against native read-write databases on NAS/NFS/SMB/Samba, and its concurrency model is workload/process sensitive.

Therefore:
**“shared company folder → DuckDB” is not a valid default.**

## Git / CI / delivery

Short-lived focused change sets and automated feedback are well supported. Koda's worktree isolation is compatible with that. Local-only projects can still have strong deterministic validation. Hosted CI is a capability, not a prerequisite.

## Sonar / static analysis

Sonar's “new code” focus generalizes well to incremental quality improvement. Its numeric built-in thresholds do not.

## Monorepos

Koda should consume the monorepo's existing graph/task model before considering any new graph. A shared config/lockfile change can legitimately broaden the impacted set.

## UI / accessibility

UI/UX quality is not “looks nice.” Meaningful web UI work should consider keyboard behavior, native semantics, loading/error/empty states, responsiveness and applicable WCAG criteria.

## Beginner / expert UX

Koda should infer what it can first, then ask only material unknowns in user language. Expert users should be able to state exact technologies/architecture directly and have those treated as requirements unless contradictory/unsafe/impossible.

## Greenfield vs adoption

A greenfield project needs architecture selection and baseline quality setup. An existing project needs preservation, discovery and scoped change. These are distinct decision modes, but neither requires rigid blueprints.
