# Iteration 5 — Rule Promotion / Enforcement Matrix

The biggest hallucination risk now is not missing practices; it is turning valid contextual guidance into hard failures.

V4 should classify every engineering rule into one of these enforcement levels.

## Level 1 — Hard invariant

Use only when violating the rule is inherently unsafe/corrupting within the detected surface and Koda can verify it deterministically.

Examples:
- do not claim a check passed when it did not run;
- do not treat malformed provider/tool output as success;
- do not commit detected real secrets;
- do not bypass protected delivery boundaries;
- do not execute model/user-controlled shell text unsafely;
- do not write outside validated worktree/path boundaries;
- do not silently overwrite unrelated user work.

## Level 2 — Existing project/org policy gate

Koda enforces because the project already requires it.

Examples:
- project coverage threshold;
- required compiler/linter settings;
- Sonar quality gate;
- dependency vulnerability severity threshold;
- license allow/deny list;
- supported runtime versions;
- branch/PR policy;
- formatting/lint rules.

Koda must preserve the policy unless the user explicitly changes it.

## Level 3 — Context-required engineering capability

Koda derives requirement from a concrete surface/risk.

Examples:
- accessibility checks for meaningful web interaction;
- compatibility review for a stable public API;
- migration/data-integrity validation for schema changes;
- authorization tests for protected resources;
- idempotency for at-least-once message processing;
- backup/recovery reasoning for valuable durable data;
- integration tests for changed DB/network boundaries.

These are hard for the mission **only after the trigger is established**.

## Level 4 — Strong recommendation

Supported good engineering, but absence should not automatically fail the mission without explicit policy/risk.

Examples:
- adding hosted CI to a local-only project;
- adding mutation testing to mature critical logic;
- adding an SBOM to a small internally distributed tool;
- adding observability beyond clear local errors;
- creating an ADR for a medium architecture decision;
- dependency-update automation where the ecosystem/platform supports it.

## Level 5 — Advisory / reviewer signal

Qualitative judgments that models/tools can surface but should not become deterministic numeric policy.

Examples:
- function feels too long;
- abstraction may be premature;
- naming could be clearer;
- coupling may be excessive;
- code may be more clever than needed;
- a dependency may be unnecessary;
- a service split may be premature.

## Level 6 — Deferred / insufficient evidence

Do not implement as policy.

Examples:
- universal complexity score;
- universal coverage percentage;
- universal database;
- universal framework mapping;
- dependency “health” popularity score;
- universal observability stack;
- Koda superiority over raw coding agents.

## Promotion requirements

To promote a candidate rule upward:
1. source/claim IDs exist;
2. scope matches;
3. trigger is detectable;
4. Koda can verify the condition;
5. counterexample has been considered;
6. project policy precedence is defined;
7. failure message is understandable;
8. false-positive cost is acceptable.

Default uncertain rules **downward**, not upward.
