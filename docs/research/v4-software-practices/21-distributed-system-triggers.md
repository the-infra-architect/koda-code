# Iteration 4 — Distributed-System Pattern Triggers

Koda should not mistake distributed-system patterns for generic “robust software” practices.

## Microservices

Benefits can include:
- independent deployment;
- independent scaling;
- fault/domain isolation;
- team/service ownership.

Costs include:
- network failure modes;
- distributed consistency;
- deployment/observability burden;
- interservice contracts;
- more complex testing/debugging;
- operational governance.

### Trigger rule
Use microservices when concrete project/team/deployment/scale/isolation requirements justify those costs.

Do not split a small app merely because services look professional.

## Messaging / events

Once a queue/event bus is introduced, Koda must reason about:
- delivery semantics;
- duplicate messages;
- ordering;
- idempotency;
- poison/dead-letter handling;
- schema/event compatibility;
- eventual consistency;
- transaction-to-event atomicity.

If none of those requirements are useful to the problem, a direct synchronous call may be simpler and safer.

## Transactional outbox

Relevant when:
- a durable DB change must reliably result in an event/message;
- database and broker cannot participate in one atomic transaction;
- losing the event or publishing without the DB change is unacceptable.

Not relevant to ordinary non-event CRUD.

## Caching

A cache is a second representation of data.

Before adding one, Koda should have evidence about:
- repeated expensive reads;
- required latency/throughput;
- expected hit rate;
- acceptable staleness;
- invalidation strategy;
- memory/size policy;
- local vs shared cache consistency;
- sensitive-data implications.

Do not add Redis/cache “for performance” with no bottleneck/access evidence.

## Retries

Retries need:
- likely transient failure;
- bounded attempts;
- timeout;
- backoff/jitter when applicable;
- idempotency or duplicate-safety;
- no harmful layered retry multiplication.

## Eventual consistency

If Koda introduces an eventually consistent architecture, it must identify which user-visible/business invariants tolerate stale/partial state.

“Eventually consistent” is not shorthand for “scalable.”
