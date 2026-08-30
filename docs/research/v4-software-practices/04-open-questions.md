# Open Questions / Hallucination-Risk Register

These questions are deliberately **not** converted into universal rules.

| ID | Question / temptation | Evidence status | Risk if Koda guesses | Current disposition |
|---|---|---|---|---|
| O001 | Hard cyclomatic/cognitive complexity threshold? | metrics can signal difficulty; no universal threshold found | metric gaming, worse refactors | reviewer signal only unless project policy exists |
| O002 | Reject any interface with one implementation? | unsupported as universal rule | destroys useful API/boundary/test seams | require concrete purpose, not implementation count |
| O003 | “YAGNI” vs legitimate foreseeable extensibility? | both overengineering and modifiability matter | either speculative framework or short-sighted design | require concrete foreseeable requirement/quality attribute |
| O004 | Universal code coverage %? | explicitly unsupported | test theater/brittle tests | preserve project/org threshold; otherwise risk-based |
| O005 | Mutation testing by default? | evidence of value, nontrivial cost | compute/process bloat | selective high-risk/mature suites/existing tool |
| O006 | Fuzz/property testing by default? | useful for certain input/state spaces | meaningless test complexity | trigger from parsers/untrusted structured input/invariants |
| O007 | Load testing by default? | target-driven performance guidance | arbitrary benchmarks | trigger from scale/latency/throughput requirement |
| O008 | Flaky test auto-quarantine? | reliable tests strongly preferred | hides real defects | diagnose; quarantine only with explicit evidence/policy |
| O009 | Universal security baseline? | SSDF high-level; ASVS web-scoped | over/under-security | use threat-surface matrix |
| O010 | Dependency license acceptability? | visibility useful, acceptability org/legal | Koda making legal decision | report; obey supplied policy only |
| O011 | Dependency “health score”? | weak/unstandardized | popularity bias/false certainty | no opaque score in V4 |
| O012 | Docker/devcontainer by default? | reproducibility can help; environment may lack Docker | unusable tooling | only existing/requested/needed+available |
| O013 | How many language adapters in V4? | many native lifecycles identified | giant weak adapter framework | capability resolver + focused evidence-backed adapters |
| O014 | Greenfield stack blueprint? | unsupported by architecture research | “dashboard→stack” vibe coding | prohibit fixed category mapping |
| O015 | Universal DB choice? | workload/topology differs | wrong consistency/concurrency | use explicit storage decision axes |
| O016 | Backup cadence? | recovery need supported; cadence workload-specific | false assurance | derive RPO/RTO/data-loss tolerance when material |
| O017 | Universal migration tool? | ecosystem-specific | duplicate/conflicting migration systems | preserve existing; choose native only if greenfield |
| O018 | Hosted CI mandatory? | unsupported for local/offline apps | makes cloud prerequisite | local quality contract is baseline |
| O019 | Sonar mandatory? | vendor/tool-specific | unnecessary service/threshold | existing/requested/available only |
| O020 | Full observability stack mandatory? | unsupported | logging/telemetry boilerplate | operational-context based |
| O021 | Monorepo affected scope always narrow? | project graph useful, shared changes can widen | missed downstream breakage | use native graph + conservative widening |
| O022 | Koda “better than raw Copilot”? | not tested live | unsupported product claim | future benchmark only |
| O023 | Automatic style/metric rewrites? | consistency useful; noisy diffs harmful | scope explosion | only mission/blocking gate |
| O024 | Ban `Any`/dynamic types? | useful typing supported; ecosystem norms differ | excessive type machinery | prefer useful specificity, preserve policy |
| O025 | Always use latest framework/tool? | no support | churn/version risk | respect existing/explicit constraints |
| O026 | Always split monolith to microservices at size X? | no universal size threshold | distributed complexity | require concrete scale/ownership/deployment/isolation reason |
