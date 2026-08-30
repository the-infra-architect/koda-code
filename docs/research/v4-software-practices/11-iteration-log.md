# Research Iteration Log

## Iteration 1 — Core engineering practice

Covered:
- code review and complexity;
- test strategy;
- secure SDLC;
- small changes / continuous delivery;
- observability;
- GitHub security capabilities;
- Sonar/new-code philosophy.

Major conclusion:
**Koda needs adaptive practices, not a fixed “best-practice” checklist.**

## Iteration 2 — Context, ecosystems, resources, data, UX, AI

Covered:
- quality attributes and architecture tradeoffs;
- readability/naming/abstractions/typing;
- dependency reproducibility across ecosystems;
- performance/resource measurement;
- bounded transient fault handling;
- persistent data/backup/migration;
- DuckDB concurrency/network-filesystem constraints;
- monorepo affected-graph reuse;
- WCAG/ARIA;
- beginner question design;
- independent verification of AI output.

Major corrections:
1. “Simplest” means least complexity **subject to important quality attributes**, not fewest components.
2. Shared network folder is **not** evidence for a native read-write DuckDB database.
3. Coverage and Sonar thresholds are policies/defaults, not universal truth.
4. Hosted CI is optional; local deterministic verification can be strong.
5. Existing project tooling normally outranks Koda preferences.

## Iteration 3 — Decision tables

Formalized:
- quality-contract capability resolver;
- greenfield minimum-information model;
- existing-project adoption precedence;
- storage/database decision axes;
- security threat-surface matrix;
- final V4 scope boundary.

Major conclusion:
V4 can now be designed around **capability resolution + conditional engineering profiles**, without hard-coded project blueprints.

## Next step

Do a separate **V4 design synthesis** from this research pack before implementation. The V4 superprompt should reference the research/rule IDs and should not add unsupported universal practices.


## Iteration 4 — Compatibility, supply chain, secure defaults, distributed systems

Covered:
- public API / CLI / config / data-contract compatibility;
- Semantic Versioning as opt-in project policy rather than universal rule;
- SBOM vs reproducibility vs build provenance/attestation;
- CI least privilege, OIDC, script-injection and poisoned-pipeline risk;
- dependency pinning + update-process tradeoff;
- application vs library dependency-resolution semantics;
- secure-by-default behavior for nontechnical users;
- memory-safety language preference for relevant greenfield/high-risk components;
- configuration/secrets separation without universal environment-variable dogma;
- input validation, logging and DB least privilege;
- relational constraints and transaction boundaries;
- microservices/messaging/cache/retry/eventual-consistency triggers;
- rolling schema compatibility / expand-contract conditions.

Major corrections:
1. Koda needs a **compatibility** capability for public/stable surfaces.
2. Supply-chain assurance must be split into distinct capabilities; a lockfile is not an SBOM and an SBOM is not provenance.
3. “Pin everything” is not universal; application and library roles differ.
4. Secure defaults are part of beginner UX, not just security review.
5. Distributed-system patterns must carry their semantic/operational costs; Koda must not add them as generic robustness.


## Iteration 5 — Enforcement audit / vulnerability triage

Covered:
- VEX/exploitability context;
- configurable dependency-review severity/license policy;
- distinction between unavailable verification and passing verification;
- hard-invariant vs project-policy vs context-required vs recommendation vs reviewer-signal rules.

Major conclusion:
The research should now stop growing horizontally. V4 design should use a **promotion matrix** so context-dependent good practices do not accidentally become hard universal gates.
