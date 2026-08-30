# Iteration 4 — Secure Defaults and Configuration

## Secure by default

CISA's secure-by-design/default guidance is particularly relevant to Koda's target user: the user may not know which security toggles exist.

Koda should prefer:
- safe default permissions;
- secure authentication defaults when auth is present;
- non-public exposure unless public access is required;
- least privilege;
- no default/shared credentials;
- framework-provided secure primitives;
- explicit loosening when business requirements require weaker controls.

The beginner should not need a hardening guide just to reach a baseline safe state.

## Configuration is contextual

A useful separation:
- **code/configuration that is part of application behavior** can live in source;
- **deploy-varying configuration and secrets** should normally be external to source.

But Koda must not universalize “environment variables”:
- server apps often use environment variables or a secret/config service;
- desktop apps may use OS/application config stores;
- local scripts may use user-scoped config files with safe permissions;
- CI uses platform secrets/OIDC;
- mobile apps cannot securely embed backend secrets in the client.

## Default-setting rule

When Koda introduces a setting:
1. Ask whether the setting is actually necessary.
2. Choose the safest useful default.
3. Avoid requiring the user to understand a threat model to configure it safely.
4. Explain material risk when the user deliberately loosens it.
5. Do not create dozens of knobs merely to look configurable.

This extends Koda's simplicity philosophy to configuration itself.

## Memory safety

For relevant greenfield/system components:
- network-facing;
- privileged;
- parser/codec;
- cryptographic/safety-sensitive;
- low-level memory manipulation;

and when language choice is genuinely unconstrained, memory-safe language/toolchain options should receive positive weight.

Do not:
- rewrite an existing mature C/C++ project automatically;
- select Rust for a simple business web application merely because it is memory safe;
- ignore required ecosystem/platform expertise/performance constraints.
