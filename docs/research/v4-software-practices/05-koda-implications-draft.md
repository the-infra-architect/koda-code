# Provisional Koda Implications

This is **not** the V4 implementation specification. It translates supported claims into design directions that still require conditional rules.

1. **Quality-attribute profile before architecture** — Koda should identify what matters for this project rather than minimizing components blindly. (`C001`–`C003`)
2. **Existing project first** — package manager, lockfiles, scripts, framework, CI, migration system, conventions and project instructions are evidence. (`C023`, `C038`, `C045`)
3. **Adaptive quality contract** — resolve capabilities such as format/lint/type/test/build/security rather than install one canonical toolchain. (`C039`)
4. **Greenfield is different from adoption** — greenfield chooses; adoption preserves and scopes. (`C043`)
5. **Risk-based testing** — select test layers from behavior/risk; coverage is evidence, not the goal. (`C010`–`C014`)
6. **Threat-surface security** — select controls from exposure/input/data/dependencies rather than run every security technique everywhere. (`C015`–`C019`)
7. **Agent evidence is never completion evidence** — deterministic repository state wins. (`C020`)
8. **Performance is ordinary engineering, not optimization theater** — catch obvious bad algorithms/query patterns, measure before complex optimization. (`C026`)
9. **Retries are conditional** — transient, bounded, idempotency-aware only. (`C027`)
10. **Observability is proportional** — operational software gets the signals it needs, tiny local tools do not receive a mandatory telemetry stack. (`C028`)
11. **Storage choice is topology-aware** — data value, writer topology, transactionality, workload, filesystem, recovery and migration all matter. (`C029`–`C034`)
12. **Shared network folder != embedded shared-write DB** — direct read-write DuckDB/SQLite files over SMB/NFS/NAS are unsafe defaults. (`C032`, `C033`)
13. **Git worktrees are isolation, not branch ideology** — Koda can use them while keeping changes short-lived. (`C006`, `C025`)
14. **Delivery readiness != deployment** — local deterministic verification remains valid without cloud CI. (`C021`, `C042`)
15. **Monorepo native graph wins** — reuse Nx/Turbo/workspace mechanisms instead of building a second graph. (`C035`)
16. **Accessibility is engineering** — meaningful web UI work includes standards-based behavior, not only visual polish. (`C036`)
17. **Beginner questions are translated requirements discovery** — ask only material unknowns in product language; let experts be technical. (`C037`)
18. **Sonar is optional/policy-driven** — preserve it when present, do not force its defaults universally. (`C041`)
