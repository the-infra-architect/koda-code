# Iteration 4 — Changes to Earlier Research

This iteration intentionally updates earlier conclusions.

## New V4 dimensions

### Compatibility surface
Added because “maintainability improvement” can create regressions if Koda changes an external contract.

### Release/supply-chain integrity
Split into:
- reproducibility;
- SBOM/component inventory;
- build provenance;
- artifact integrity;
- CI security.

Previously these were too compressed under dependency/security checks.

### Secure defaults
Promoted from generic security to a first-class UX/architecture principle because Koda targets non-experts.

### Memory safety
Added as a conditional greenfield quality attribute for exposed/privileged/low-level code, not a universal language choice.

### Distributed-pattern triggers
Explicit rules now prevent Koda from adding microservices, queues, caches, retries or eventual consistency without the corresponding correctness/operational requirements.

### Data constraints/transactions
Added because application-level validation alone is insufficient for some persistent invariants/concurrent writers.

### Dependency role
Corrected: application locks and library dependency constraints are not the same thing.

## Earlier rules retained

- no universal coverage percentage;
- no universal Sonar requirement;
- no universal database;
- DuckDB preference remains conditional;
- existing project conventions outrank Koda taste;
- hosted CI is optional for local/offline projects;
- AI self-report is never deterministic evidence.

## Research quality note

This iteration adds more hard security/supply-chain guidance, but still does **not** make all of it mandatory. Many controls are only appropriate when the relevant release, distribution, CI, public API, security or distributed-system surface exists.
