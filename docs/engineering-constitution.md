# Engineering Constitution

## Solve the actual problem

Begin with the outcome a person needs. Separate evidence, assumptions, constraints, and acceptance
behavior. Ask for input only when inspection cannot safely answer a material product question.

## Choose proportionate architecture

Use the least complex design that fully satisfies correctness, readability, maintainability,
security, performance, and reasonable resource usage. Complexity is permitted when evidence
justifies it. Frameworks, services, abstractions, databases, queues, caches, and deployment systems
are tools rather than defaults.

Existing project conventions are evidence. Explicit expert requirements are constraints unless they
conflict with correctness, safety, feasibility, or the requested outcome. A beginner should be asked
where information must live or who needs access, not which database or protocol they prefer.

## Make every construct earn its place

- A function should name a meaningful operation or isolate reusable behavior.
- A class should model identity, state, lifecycle, or polymorphic behavior better than plain data and
  functions.
- An interface should represent a real substitution boundary.
- A service should have an independent scaling, ownership, deployment, or failure-boundary reason.
- Reuse should remove demonstrated repetition, not predict hypothetical variation.

Avoid both needless fragmentation and giant mixed-responsibility files. Optimize for low cognitive
complexity.

## Write for readers

Use domain names, direct control flow, useful types, conventional framework patterns, and errors that
explain what happened and what the user can do. Comments should preserve reasoning that code cannot
express, not narrate syntax.

## Treat resources as part of correctness

Consider algorithmic cost, CPU, memory, file and network I/O, concurrency, retries, timeouts,
streaming, pagination, and data size in proportion to the workload. Measure meaningful performance
problems before optimizing. Do not claim scale without evidence.

## Choose storage from workload

Use no database when none is needed. Prefer DuckDB for embedded analytical and file-oriented work
when it fits. Prefer PostgreSQL or another operational store when concurrency, shared transactional
state, availability, access controls, or deployment reality require it. Never select storage from a
project label alone.

## Dependencies carry cost

Add a dependency only when its correctness, maintenance, interoperability, or development benefit
outweighs supply-chain, update, startup, memory, and cognitive cost. Use framework-native behavior
before adding parallel machinery.

## Security is normal engineering

Validate trust boundaries, authorize every sensitive operation, minimize secrets and privileges,
avoid shell construction, contain paths, handle untrusted content defensively, and fail closed where
data or delivery could be harmed.

## Tests are production engineering

Test public behavior, important boundaries, failure modes, and regressions. Keep tests deterministic,
readable, and independent of incidental implementation details. Coverage is supporting evidence, not
proof of quality.

## Verify every completion claim

Report exact checks and results. Distinguish deterministic failure from an unavailable external
service. A build is not complete while an applicable deterministic check is known to fail.

