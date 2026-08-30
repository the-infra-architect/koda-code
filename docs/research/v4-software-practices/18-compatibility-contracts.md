# Iteration 4 — Compatibility / Contract Surfaces

## Why this matters

A change can be internally cleaner and still be bad engineering if it silently breaks consumers.

Koda V4 should recognize **compatibility surfaces**, including:

- public library/package APIs;
- HTTP/RPC APIs;
- CLI command names/options/exit codes/stdout formats used by automation;
- configuration keys/formats;
- plugin/extension interfaces;
- serialized/persisted data formats;
- database schema contracts used by multiple application versions/services;
- events/messages consumed by other systems;
- documented environment variables;
- public error/status contracts;
- generated artifact naming/locations when consumers depend on them.

## Evidence-based rules

### Existing contracts first

Microsoft API guidance explicitly warns against breaking an existing service merely to conform it to newer guidelines. GitHub/Kubernetes both use explicit compatibility/version/deprecation mechanisms.

**Koda implication:** “cleaner according to our latest rules” is not enough reason for a breaking change.

### Define what is public/stable

Semantic Versioning only works when the public API is defined. Projects may use other version schemes or no external contract.

Koda should detect:
- package/library metadata;
- public exports;
- OpenAPI/protobuf/GraphQL/etc schemas;
- documented CLI interfaces;
- versioning/deprecation docs;
- consumer tests/contract tests;
- compatibility tooling already in CI.

Do not invent a public API for an internal module.

### Breaking-change review

When a mission touches a stable compatibility surface, Reviewer should explicitly ask:

1. Does an existing consumer need to change?
2. Is a field/parameter/type/behavior/error/auth requirement being removed or changed?
3. Is a previously optional behavior now required?
4. Does latency/rate/concurrency behavior materially change where consumers rely on it?
5. Is there a version/deprecation/migration path?
6. Can the change be additive/backward-compatible instead?

### Project policy wins

Do not copy:
- GitHub's support window;
- Kubernetes stability tracks;
- Microsoft's exact REST version rules;
- SemVer if the project does not claim SemVer.

Use the project's contract/version policy.

## Candidate V4 capability

`compatibility`

States:
- `not_applicable` — no stable/public contract affected;
- `existing` — repo already has compatibility/version tooling/policy;
- `required` — mission changes a stable/public surface;
- `unknown` — surface appears public but policy/consumers unclear;
- `recommended` — early/pre-1.0/internal API with some external use but low stability guarantee.

This capability should not be a universal build step. It is triggered by the change surface.
