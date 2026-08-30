# Context Matrix

This file exists to prevent Koda from applying the same engineering contract to every project.

| Context | Primary engineering concerns | Often appropriate | Often unnecessary unless justified | Evidence/questions needed |
|---|---|---|---|---|
| Tiny one-off/local script | correctness, clarity, safe inputs | simple functions, focused tests for meaningful logic, clear errors | microservices, hosted CI, Sonar, observability stack | shared/maintained? valuable data? scheduled/automated? |
| Local single-user app | correctness, UX, persistence, recovery | embedded storage if workload fits, local validation | distributed cache/queue/orchestration | data value/size, process model, OS, backup need |
| Shared-folder data tool | filesystem semantics, concurrent access, corruption risk | read-only shared data or central writer/service | native read-write DB file directly on SMB/NFS/NAS | how many machines/processes write? what filesystem? |
| Desktop app | install/update UX, local storage, crash recovery | platform packaging, clear logs/errors | service-grade observability/cloud infra by default | OSes, update path, offline use, data-loss impact |
| Small internal web app | auth if needed, concurrent users, deployability, backup | conventional monolith/modular app, server DB for multiwriter | gateway/microservices/cache without concrete need | users, write concurrency, hosting, auth/SSO |
| Public web app | security, accessibility, reliability, performance | ASVS-informed controls, WCAG, dependency/secret/static checks | embedded shared-file DB architecture | exposure, data sensitivity, traffic, recovery/uptime |
| Distributed/high-throughput service | latency, throughput, reliability, idempotency, operability | explicit targets, profiling, bounded retries, metrics/tracing as useful | simplistic “fewest components” rule | concurrency, SLOs, dependency contracts, failure modes |
| Batch/data analytics pipeline | data volume, memory/I/O, reproducibility, data quality | DuckDB/columnar/vectorized tools when suitable, batching/pushdown | row-at-a-time loops, unnecessary service architecture | format/size, locality, concurrency, SLA |
| Library/package | API stability, compatibility, docs, packaging | ecosystem conventions, public API tests/docs | application deployment infrastructure | supported runtimes, semver/release expectations |
| CLI | input validation, exit behavior, portability | CLI integration tests, deterministic diagnostics | UI/UX agent or web security ceremony | OSes, interactive/noninteractive use |
| Existing mature repo | regression risk, consistency, scope | preserve package manager, lockfiles, scripts, style, CI | global tool migrations unrelated to mission | current commands, architecture, policies, debt |
| Legacy repo with weak tests | characterization/safety, incremental improvement | targeted tests near changed behavior | “fix whole repo before feature”, arbitrary global coverage jump | critical behavior, feasible test seams |
| Greenfield repo | architecture fitness, reproducibility, baseline quality | derive stack from outcome/environment; minimal coherent contract | rigid category→stack blueprint | user/deployment/data/scale/security constraints |
| Monorepo | affected scope, dependency graph, CI cost | native workspace graph/affected commands | second custom graph | workspace tool, shared config/lock changes |
| Offline/restricted | installability, local verification | local deterministic checks, approved/existing deps | mandatory cloud CI/Sonar/online scanners | network, registry policy, install permissions |
| Regulated/high-risk | assurance, traceability, evidence | stronger review/testing/security/documentation | heuristic “good enough” defaults | governing standard/risk classification |
| UI-heavy web product | accessibility, UX states, responsiveness | WCAG/native semantics, critical flow/UI tests | visual-only review | users/devices/design system/keyboard needs |

## Interpretation rule

Project category is a **signal**, not an architecture blueprint. Koda still needs the actual repository, environment, user outcome, workload, deployment reality, and explicit constraints.
