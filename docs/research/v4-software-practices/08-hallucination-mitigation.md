# Hallucination-Mitigation Protocol

“Best practices” are unusually vulnerable to hallucination because advice is often copied across ecosystems, stripped of scope, converted from vendor defaults into universal law, or remembered after tools changed.

## Required trace

Every non-obvious deterministic Koda policy should be traceable as:

`source → claim → context/caveat → Koda implication → conditional rule`

If a link is missing, the rule is not ready.

## Promotion checklist

Before turning research into a hard V4 behavior:

1. **Scope** — Is the source about all software, web apps, distributed systems, one language, or one tool?
2. **Authority** — Standard/spec/official mechanics vs practitioner guide vs research vs vendor marketing.
3. **Date/version** — Is behavior version-sensitive?
4. **Counterexample** — Name at least one valid situation where this rule would be wrong.
5. **Existing policy** — Does the repo/org intentionally use another valid policy?
6. **Feasibility** — Is the tool/service installed, authorized, network-accessible and supported?
7. **Cost** — Runtime, CI, dependency, operational and cognitive cost.
8. **Evidence ownership** — Can Koda verify the outcome deterministically?
9. **Threshold provenance** — Any number must come from explicit policy/requirement/measurement/standard.
10. **Hard gate vs recommendation** — Context-dependent claims should usually warn/recommend rather than fail closed.
11. **Tool-name substitution check** — Is Koda requiring a *capability* or unnecessarily requiring one vendor/tool?
12. **AI confirmation check** — Never use a model's confidence as evidence for its own work.

## Source-bias rules

- Vendor/tool docs: authoritative for mechanics, not universal necessity.
- Cloud architecture guides: relevant to distributed/cloud workloads, not proof that local apps need cloud patterns.
- Company engineering guides: strong practitioner evidence, but company context remains.
- Empirical AI studies: useful for risk direction, not stable defect-rate constants.
- Standards: often high level; context is still needed to map them to concrete action.

## Examples

### Bad
“Good projects require 85% coverage.”

### Research-safe
“Coverage is a risk signal. Preserve explicit project policy. Otherwise test changed critical behavior based on risk; do not invent a universal percentage.”

### Bad
“Use DuckDB because the data is on a company shared drive.”

### Research-safe
“DuckDB is strong for embedded analytical workloads, but native read-write DB files on SMB/NFS/NAS are specifically discouraged. Determine writer topology and storage location first.”

### Bad
“Microservices are overengineering.”

### Research-safe
“Microservices add distributed operational complexity. Use them when concrete scale, independent deployment, isolation, ownership or reliability requirements justify that cost.”

### Bad
“Every API call needs retries.”

### Research-safe
“Retry only likely transient failures, with bounded attempts and appropriate timeout/idempotency/backoff semantics.”

## V4 design evidence

Recommended: check this research pack into the Koda-Code repository (for example under `docs/research/v4-software-practices/`). Where V4 introduces a non-obvious policy, reference the applicable claim/rule IDs in design documentation so future agents can distinguish deliberate evidence-backed behavior from model preference.


## Iteration 4 additions

Before promoting a rule, also ask:

13. **Compatibility check** — Does this “cleanup” change a public API, CLI, config key/schema, persisted format, event/message, error contract or other consumer-visible behavior?
14. **Supply-chain layer check** — Are we talking about dependency reproducibility, SBOM inventory, build provenance, signing/integrity or CI security? Do not substitute one for another.
15. **Artifact-role check** — Is this an end application, published library, CI/build dependency, container, or distributable binary? Dependency/release policy differs.
16. **Secure-default check** — Are we requiring a beginner/customer to discover a setting that Koda could safely default?
17. **Distributed-complexity check** — Did introducing a cache/queue/service/retry/eventual consistency also introduce the required consistency/idempotency/observability/failure semantics?
18. **Data-integrity check** — Is an invariant being enforced only in application code even though concurrent writers or external access make a datastore constraint/transaction materially safer?


## Iteration 5 additions

19. **Enforcement-level check** — Is this a hard invariant, existing project policy, context-required capability, strong recommendation, reviewer signal, or unsupported rule?
20. **Scanner semantics check** — Does a vulnerability finding establish affected component, exploitability, or merely inventory correlation? Preserve uncertainty.
21. **Unavailable-vs-pass check** — Could a missing tool/service be incorrectly represented as a green check?
22. **Legal-policy check** — Is Koda about to make a license/risk-acceptance decision that belongs to an organization/user?
