# Iteration 3 — Quality Contract Resolver

## Goal

Koda should not ask “Which tools should every repo have?” It should ask:

> Which **quality capabilities** are required for this project/change, which are already available, and what is the smallest appropriate way to satisfy missing required capabilities?

## Resolution states

For each capability:

- `required` — failing/absent would make this mission unsafe or incomplete.
- `recommended` — valuable but not a hard blocker absent explicit project policy.
- `existing` — project already provides a trustworthy mechanism; use it.
- `unavailable` — relevant but cannot run in this environment; report honestly.
- `not_applicable` — risk/surface is not present.
- `unknown` — insufficient evidence; resolve before material architecture/delivery if important.

## Capability vocabulary

| Capability | Strong triggers | Existing evidence to prefer | When it may be N/A / recommendation only |
|---|---|---|---|
| format | repo already enforces formatting; generated code must match style | existing formatter/config/script | tiny repo without formatter: readability may be reviewed without introducing one |
| lint/static correctness | language/project supports meaningful static checks | existing lint script/config/compiler warnings | do not add a linter solely for ceremony when no suitable project tool exists |
| type/compile | compiled/static-typed language or existing type policy | compiler/typecheck script/config | dynamic project without type-checking policy: useful local types can still be improved |
| unit tests | changed pure/domain behavior with meaningful branches/invariants | existing unit suite/framework | trivial declarative/config-only change may not need new unit tests |
| integration tests | behavior crosses DB/filesystem/network/framework boundary | existing integration suite | pure isolated logic |
| E2E/critical journey | user-facing critical workflow changes | existing browser/system suite | backend/internal refactor with no user journey |
| build/package | distributable/compiled/packageable app/library | native project build/package lifecycle | interpreted one-off script may have no package artifact |
| secret scan | source/config can carry credentials | existing secret scanner / platform | still inspect changed files even if full tool unavailable |
| dependency analysis | dependency manifest/lock changes or third-party code added | existing platform/scanner/audit | no dependency change: may be baseline CI only |
| static security | exposed/untrusted/security-sensitive code and supported analyzer | CodeQL/Semgrep/Bandit/etc already configured | unsupported language/tool can mean `unavailable`, not fake pass |
| web security | exposed web app/API | ASVS-informed existing scanner/tests | CLI/local computation |
| fuzz/property | parser, untrusted structured input, protocol/state invariants | existing fuzz/property tooling | ordinary CRUD or low-risk deterministic logic |
| accessibility | meaningful web UI/interactions | existing a11y tests/linter/browser tooling | backend/CLI/no UI |
| performance/load | explicit latency/throughput/scale or observed regression | existing benchmarks/profiler/load tests | ordinary change with no performance risk |
| migration/data integrity | schema/data transformation/persistence change | existing migration tool + DB checks | no persistent data change |
| recovery/backup | valuable durable data newly introduced/materially changed | existing backup/recovery process | disposable/cache data |
| docs | public API/setup/architecture/operation behavior changed | existing docs structure | internal self-evident refactor may need none |
| CI mirror | hosted CI available/requested | existing CI workflow | local/offline can use local deterministic contract |

## Resolver algorithm

1. Detect repo/project context.
2. Detect existing quality mechanisms and authoritative scripts.
3. Determine change surfaces and risks.
4. Mark each capability state.
5. Use existing mechanisms first.
6. For a `required` missing capability:
   - prefer ecosystem-native/minimal addition;
   - ensure tooling is available/authorized;
   - if unavailable, report blocker/limitation rather than claim pass.
7. For `recommended` missing capability:
   - do not install infrastructure automatically unless value clearly outweighs cost or user requests it.
8. Never convert a vendor default into a universal numeric gate.
9. Preserve explicit project/org policies even when stricter than Koda defaults.
10. Recompute affected capabilities when the diff changes materially.

## Examples

### Existing Next.js app changes a form
Likely:
- existing lint/type/build: `existing/required`;
- unit/integration: depends on current architecture;
- E2E: recommended/required if critical flow;
- accessibility: required/recommended based on interaction;
- migration: N/A unless data schema changes;
- load testing: N/A absent scale requirement.

### Local Python CSV converter
Likely:
- format/lint: use existing if present;
- focused behavior tests: required for nontrivial transformation;
- package/build: only if distributed as package;
- web security/accessibility: N/A;
- hosted CI: optional;
- performance: inspect memory/data size, benchmark only if material.

### Public authenticated web app
Likely:
- unit/integration/build: required according to architecture;
- security/static/secret/dependency: strongly applicable;
- auth/access-control security requirements: required;
- accessibility for UI: applicable;
- E2E critical auth/user journeys: strongly applicable;
- observability/recovery: depends on operational/data requirements.
