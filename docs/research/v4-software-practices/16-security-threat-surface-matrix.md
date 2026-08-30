# Iteration 3 — Security Threat-Surface Matrix

Koda should select security verification from **what the software can do / what can reach it**, not from a universal scanner checklist.

| Surface | Signals | Relevant engineering/verification | Usually not implied |
|---|---|---|---|
| public web/API | routes/endpoints/listeners/public deployment | auth/access control, input validation, session/security headers as applicable, ASVS-informed checks, static/web testing | fuzz every internal function |
| authentication | login/token/SSO/roles | credential/session/token handling, brute-force/rate controls as relevant, authorization tests | custom auth if framework/provider solves it |
| authorization | roles/permissions/resource ownership | deny-by-default where architecture warrants, object/function access tests | assuming authentication == authorization |
| untrusted structured input | JSON/XML/CSV/uploads/parsers | schema/bounds validation, parser safety, fuzz/property testing candidate | heavy web scanner if no web surface |
| file access/uploads | user-controlled paths/files | path traversal, size/type limits, storage isolation, safe extraction | unrestricted filesystem permissions |
| SQL/query construction | user-derived query values | parameterization/query safety, DB permission scope | executing model/user-generated SQL as trusted |
| command/process execution | subprocess/CLI wrappers | argv/no-shell where practical, allowlists, path/env control | passing user/model strings to shell |
| secrets/credentials | API keys/tokens/password config | no source/log leakage, least privilege, secure configuration | inventing enterprise vault if environment lacks one |
| dependencies | manifest/lock changes | vulnerability/component review, reproducibility, provenance where available | opaque popularity-based “health” score |
| persistent sensitive data | customer/employee/financial/private data | access control, encryption policy where required, backup/recovery, logging hygiene | arbitrary encryption layer without key management plan |
| multi-tenant/shared users | different users/organizations | tenant isolation, authorization boundaries, concurrency/integrity | treating local single-user assumptions as safe |
| network clients | outbound/inbound remote dependencies | TLS/cert validation as platform requires, timeouts, bounded retries, SSRF/URL controls where relevant | retrying all failures |
| browser UI | interactive public/internal web UI | XSS/CSRF/content/security framework controls where applicable, accessibility | backend-only security scanner as full assurance |
| deserialization/plugins/extensions | loading external code/data | safe formats, trust boundaries, signature/provenance/sandbox where appropriate | arbitrary dynamic code execution |
| CI/CD | workflows/actions/secrets/deploy permissions | least privilege, pinned third-party actions/policy, secret handling, protected deployment | hosted CI if project is intentionally local/offline |
| AI/tool execution | model can edit/execute tools | narrow tool scopes, deterministic validation, prompt/tool input validation | trusting agent “pass” statements |

## Security severity is contextual

The same issue can differ dramatically:
- unsafe local test fixture vs public request handler;
- hard-coded fake test token vs production credential;
- local-only read path vs multi-tenant file access.

Koda should use:
- exposure;
- privilege;
- data sensitivity;
- exploitability;
- impact;
- existing project/org policy

to decide blocker vs recommendation.

## Hard invariants suitable for Koda

Some rules are strong enough to be near-universal when the surface exists:
- do not commit real secrets;
- do not trust model/user-controlled paths/commands without validation;
- do not treat authentication as authorization;
- do not claim scanner/test success that did not run;
- do not waive deterministic failures because an agent says code is safe.

Other controls remain surface-dependent.
