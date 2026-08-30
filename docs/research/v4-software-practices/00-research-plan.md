# Research Plan

Snapshot: 2026-08-29

## Objective

Research the engineering practices Koda-Code V4 should understand when creating or modifying real software across different environments, without hard-coding a universal stack or “best-practice checklist.”

## Method

1. Prefer primary or authoritative sources: standards, official tool/ecosystem docs, NIST, OWASP, DORA, SEI, W3C, and major engineering guides.
2. Separate:
   - source fact;
   - engineering claim;
   - context/caveat;
   - Koda implication;
   - candidate rule.
3. Preserve source scope. Tool/vendor documentation is authoritative about that tool, not universal necessity.
4. Tag confidence:
   - **A** — standard/spec/government/primary tool behavior;
   - **B** — strong practitioner/research-backed guidance;
   - **C** — context-dependent synthesis/inference;
   - **D** — weak heuristic/insufficient evidence;
   - **Rejected** — contradicted, obsolete, too broad, or unsupported.
5. Record contexts where a rule would be wrong.
6. Any number/threshold must come from:
   - project/org policy;
   - explicit user requirement;
   - measured workload;
   - governing standard;
   not Koda folklore.
7. Existing project conventions outrank Koda preferences unless broken, unsafe, unavailable, or explicitly being migrated.
8. AI/model output remains untrusted input; repository state and deterministic checks are authoritative.
9. Do not write V4 until the main decisions are expressible as conditional tables.

## Domains researched

- quality attributes and architecture tradeoffs
- maintainability/readability/naming/typing
- abstraction and reuse
- testing strategy and coverage
- security and threat modeling
- AI-generated-code verification
- dependency/supply-chain/reproducibility
- performance/resources/retries
- observability/error handling
- persistent data, backup, migrations, concurrency
- Git/worktrees/CI/CD
- static analysis/Sonar
- accessibility/UI
- beginner/expert requirements discovery
- greenfield vs existing-project adoption
- ecosystem/tool detection
- monorepos
- local/offline/restricted environments
