# Iteration 5 — Research Audit

## Audit objective

Attempt to falsify or weaken the strongest candidate V4 rules before implementation.

## Rules downgraded from universal hard gates

- coverage percentage;
- Sonar presence/threshold;
- SBOM/provenance for all projects;
- dependency vulnerability severity threshold;
- license acceptability;
- exact dependency pinning style;
- mutation/fuzz/load testing;
- memory-safe language requirement;
- microservices avoidance;
- hosted CI;
- observability stack;
- Docker/containerization;
- complexity/function-size limits.

## Rules strengthened

### Compatibility awareness
A code-quality refactor can be harmful if it breaks a stable consumer contract. Compatibility is now a first-class project/change surface.

### Secure defaults
Because Koda explicitly targets non-experts, safe defaults are more important than documentation telling users how to harden the output later.

### CI as privileged code
Generated workflow files can create injection/credential/supply-chain risk and deserve security validation as code.

### Data integrity
Persistent invariants, transaction boundaries and migration overlap are real correctness concerns, not merely database style.

### Distributed semantic cost
Queues, caches, retries and microservices bring correctness obligations—not just deployment complexity.

### Capability `unavailable`
Koda must distinguish inability to verify from success. This applies to security scanners, hosted services, model execution and ecosystem tools.

## Strongest remaining hallucination risks

1. Treating a source's example tool as mandatory.
2. Promoting project/vendor numeric defaults into Koda constants.
3. Overfitting to Python/TypeScript because Koda itself uses them.
4. Asking beginners technical questions that repository/environment discovery could answer.
5. Treating “modern architecture” as a quality attribute.
6. Treating a scanner finding as automatically exploitable—or automatically ignorable.
7. Treating application and library dependency policy as identical.
8. Applying distributed-system resilience patterns to non-distributed software.
9. Rewriting existing architecture to satisfy Koda style rather than mission requirements.
10. Hiding verification gaps behind agent confidence.

## Research conclusion

The evidence base is now broad enough that the next phase can safely be a **V4 design synthesis**, not more indiscriminate source collection.

Further research should become targeted: when the V4 design encounters a concrete unresolved decision, research that decision specifically rather than continuing to enlarge a generic best-practices corpus.
