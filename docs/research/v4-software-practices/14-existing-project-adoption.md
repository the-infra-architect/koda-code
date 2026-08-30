# Iteration 3 — Existing-Project Adoption Rules

## Core principle

For an existing repository, **discovery precedes prescription**.

Koda should assume the repository's deliberate conventions are part of the requirements unless evidence shows they are broken, unsafe, unavailable, obsolete in a material way, or the user explicitly requests migration.

## Evidence precedence

1. Explicit user mission constraints.
2. Repository-local Koda/Copilot/contribution/architecture policy.
3. Build/package/test configuration.
4. Wrapper scripts and task definitions.
5. Lockfiles/version manager/toolchain files.
6. Existing CI and deployment config.
7. Framework/language conventional lifecycle.
8. Locally installed tools.
9. Koda recommendation.

## Adoption inventory

Koda should detect, bounded to relevant scope:

- languages and framework markers;
- package managers and lockfiles;
- monorepo/workspace config;
- formatter/linter/type/compiler settings;
- test frameworks and existing suites;
- build/package scripts;
- security scanning already configured;
- CI workflows;
- Sonar/static analysis;
- database/migration mechanism;
- deployment/container/IaC files;
- project instructions/contribution docs;
- runtime/version files;
- generated-code/vendor directories that should not be hand-edited.

## Preserve by default

- package manager;
- lockfile strategy;
- formatter/style;
- lint/type policy;
- test framework;
- migration framework;
- framework architecture;
- CI provider;
- established module boundaries;
- supported language/runtime versions.

## Legitimate reasons to change an existing mechanism

- user explicitly requested migration;
- current mechanism cannot satisfy the requested feature;
- deterministic evidence shows it is broken;
- security/compatibility requirement makes it unacceptable;
- upstream/tool support has ended and creates a material project problem;
- current environment cannot run it and migration is the approved solution.

## Do not conflate debt with mission scope

If Koda finds unrelated debt:
- record/report it if relevant;
- do not expand the feature into a repository cleanup unless it blocks correctness/security/delivery;
- prefer changed-code improvement rather than demanding all legacy debt be repaired first.

## Command trust

Use the repository's own scripts/wrappers when available. A `package.json` script or Maven/Gradle wrapper can encode project-specific configuration that a guessed raw command misses.

## Broken-tool behavior

If the existing quality command is failing before Koda's change:
1. establish baseline where safe;
2. distinguish pre-existing failure from Koda-caused failure;
3. do not claim Koda introduced it;
4. do not automatically disable the gate;
5. escalate/repair only when mission scope or user instruction justifies it.
