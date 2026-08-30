# Iteration 4 — Dependency Resolution Nuance

## Why this needed a correction

“Pin all dependencies exactly” sounds safe but is not universally correct.

Different artifacts play different roles:

### End applications / deployed binaries
Usually want a reproducible resolved dependency graph.

Examples:
- lockfiles;
- package-manager resolution snapshots;
- checksums.

### Published libraries
Often declare compatibility ranges/minimum versions so downstream applications can resolve a coherent graph.

The library's development environment may still have a lockfile/testing resolution, but its consumers do not necessarily use that exact graph.

### CI/build dependencies
Actions, images, scripts and plugins execute with high privilege, so immutable references/integrity verification deserve stronger consideration.

## Koda rule

Before editing dependency versions, determine:
1. ecosystem;
2. package/application/library role;
3. existing lock/resolution semantics;
4. whether this is runtime/build/dev/test dependency;
5. current project/org policy;
6. vulnerability/security evidence;
7. update mechanism.

## Pin + update are paired concerns

OpenSSF guidance highlights the tradeoff:
- immutable pins reduce unexpected supply-chain change;
- stale pins can preserve vulnerabilities.

Therefore Koda should not:
- exact-pin every reusable library dependency;
- delete lockfiles to “allow updates”;
- update all dependencies during an unrelated feature;
- pin and then remove the project's update mechanism.

Dependency changes should remain scoped and evidence-driven.
