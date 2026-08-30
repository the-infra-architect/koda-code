# Iteration 3 — V4 Scope Synthesis

## What V4 should become

V4 should make Koda competent across **real software-development situations** by adding a small evidence-based project/quality capability layer.

It should NOT become:
- a giant universal software factory;
- a rigid blueprint catalog;
- an enterprise architecture framework;
- a package-manager migration system;
- a universal database recommender with one favorite;
- a policy engine full of arbitrary numeric thresholds.

## Candidate V4 primitives

The research supports a small set of concepts:

### 1. Project engineering profile
Evidence-derived facts:
- languages/frameworks;
- greenfield vs existing;
- deployment/access topology;
- data/storage/concurrency;
- important quality attributes;
- environment restrictions;
- existing quality/toolchain capabilities;
- security surfaces;
- monorepo/workspace structure.

### 2. Quality capability contract
A technology-neutral set of capabilities:
- format;
- lint/static correctness;
- type/compile;
- unit;
- integration;
- E2E;
- build/package;
- secret/dependency/static security;
- accessibility;
- performance/load;
- migration/data integrity;
- recovery;
- docs;
- CI mirror.

Each gets a state: existing / required / recommended / unavailable / not-applicable / unknown.

### 3. Ecosystem resolver
Use repository evidence to map capabilities to **existing/native** commands. Avoid new adapter abstractions beyond what is necessary for clear, tested support.

### 4. Greenfield requirements translator
Ask product-language questions only when the missing fact changes architecture materially.

### 5. Existing-project adoption guard
Preserve package manager, lockfiles, scripts, architecture, test framework, migration system, CI and style unless there is a concrete reason to change them.

### 6. Storage/topology reasoning
Use workload/writer/storage/recovery axes; encode the network-share correction.

### 7. Threat-surface resolver
Choose security capabilities based on actual attack surface and data sensitivity.

## V4 acceptance philosophy

V4 should be tested deterministically without live model claims:
- detector fixtures across representative ecosystems;
- profile/resolver decisions;
- preservation of existing toolchains;
- greenfield question minimization;
- storage/shared-network edge cases;
- threat-surface selection;
- local-only/offline cases;
- monorepo affected-scope integration;
- unsupported/unavailable tool behavior;
- no universal thresholds/blueprints.

## Deferred beyond V4

- live model quality benchmark;
- Koda vs raw Copilot comparison;
- generalized provider framework;
- autonomous cloud provisioning;
- broad package publishing/distribution;
- dependency “reputation” scoring;
- legal/license acceptance decisions;
- universal architecture ranking score.

## Research status

Iterations 1–3 provide enough evidence to write a **separate V4 design/superprompt** next.

The V4 prompt should cite/use the claim IDs and decision tables in this pack, and should preserve uncertainty where this research deliberately does not establish a universal rule.


## Iteration 4 scope additions

### 8. Compatibility surface resolver
Detect whether changed code affects stable/public API, library, CLI, config, persisted format, event/message or multi-version schema contracts. Require compatibility review only when applicable.

### 9. Release / supply-chain profile
Separate:
- reproducible dependency/build state;
- component inventory/SBOM;
- build provenance/attestation;
- artifact integrity/signing;
- CI security.
Activate these based on distribution, risk and policy.

### 10. Secure-default resolver
For user-facing software, default to safe permissions/exposure/authentication/configuration where the product surface supports it. Do not require beginners to know the hardening steps.

### 11. Distributed-pattern justification
Microservices, messaging, caching, retries and eventual consistency require explicit triggers plus the corresponding correctness/operational semantics.

### 12. Data-integrity profile
For persistent/concurrent data, identify:
- invariant enforcement;
- transaction boundaries;
- writer topology;
- migration compatibility;
- recovery needs.

## Updated V4 boundary

V4 can change earlier Koda behavior if the evidence here shows it was too rigid or unsafe. Backward compatibility of **Koda's own public surface** should still be reviewed deliberately rather than changed accidentally.

V4 remains deterministic/research-driven and still makes no live-model quality claims.
