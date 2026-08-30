# Candidate Conditional Rules

Format: **trigger/evidence → action → do not**.

| ID | Trigger / evidence | Candidate Koda action | Do NOT |
|---|---|---|---|
| R001 | Existing repo has build/package/test config | Use existing package manager, lockfile, scripts/lifecycle/style first | migrate because Koda prefers another tool |
| R002 | New project/material architecture change | derive relevant quality attributes/constraints | minimize components blindly |
| R003 | Multiple solutions satisfy requirements | choose lower operational/cognitive complexity | reject sophisticated solution when requirements justify it |
| R004 | New abstraction/interface/factory/service | require concrete boundary/reuse/state/lifecycle/change benefit | reject solely because it currently has one implementation |
| R005 | Changed identifiers | follow project/ecosystem naming; prefer domain meaning | impose a Koda naming dialect |
| R006 | Typed codebase | use specific useful types in touched code | force global strictness migration without reason |
| R007 | Behavior changes | add fastest meaningful tests; integration at boundaries; E2E critical journeys | maximize count or demand every test layer |
| R008 | Coverage exists | inspect risky uncovered changed behavior; preserve existing threshold | invent 80/85/90/100% universal threshold |
| R009 | Threat surface identified | select relevant security checks | apply all web security controls to non-web software |
| R010 | New dependency proposed | check existing capability, manifest/lock impact, vulnerability/deployment feasibility | add a package for trivial built-in capability |
| R011 | Plausible performance issue | fix obvious inefficiency; measure before complex optimization | add cache/queue/concurrency on speculation |
| R012 | Remote transient failure | use bounded retry/backoff/timeout/idempotency-aware mechanism | retry permanent errors/infinite loops |
| R013 | Long-running/service operational context | add proportional actionable observability | add full telemetry stack to every project |
| R014 | Valuable durable data | determine backup/recovery need | treat DB choice as only API/schema choice |
| R015 | Existing populated DB changes | use existing migration mechanism; assess locks/data/rollback | drop/recreate live data casually |
| R016 | Embedded analytical/local workload | prefer DuckDB when writer/storage semantics fit | put native read-write DB on SMB/NFS/NAS by default |
| R017 | Multiple machines/processes write shared data | prefer safe central/client-server write coordination | assume shared file == concurrent database |
| R018 | Koda mission branch | keep isolated/scoped/short-lived | create long-lived environment branches by default |
| R019 | Hosted CI exists/requested | mirror deterministic local contract in CI | require cloud CI for local/offline app |
| R020 | Generating GitHub workflow with third-party actions | use project/security policy and immutable references where appropriate | casually use floating refs |
| R021 | Sonar exists/requested/available | preserve configured gate and changed-code focus | force Sonar or vendor thresholds everywhere |
| R022 | Monorepo with native graph | use existing affected/project graph | build a competing graph |
| R023 | Meaningful web UI change | apply accessibility/interaction checks | treat UI/UX as visual preference only |
| R024 | Material fact cannot be inferred for beginner | ask one concise product-language question | ask infrastructure jargon/which-agent questions |
| R025 | Expert explicitly specifies stack/architecture | treat as requirement unless unsafe/impossible/conflicting | override merely because Koda prefers simpler tech |
| R026 | Agent reports done/pass | verify via Git/filesystem/configured checks | advance from self-report |
| R027 | Public/setup/architecture behavior changes | update smallest useful docs | generate stale boilerplate |
| R028 | No hosting/remote CI | keep deterministic local quality contract | declare project unengineered because cloud unavailable |
