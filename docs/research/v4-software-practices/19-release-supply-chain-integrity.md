# Iteration 4 — Release and Supply-Chain Integrity

## Separate capabilities

Koda must not conflate:

### Reproducible dependency resolution
Can another environment resolve/build the intended dependency graph consistently?

Examples:
- lockfiles;
- ecosystem checksums;
- build wrappers/toolchain pins.

### SBOM
What components/dependencies/services are inside or associated with the software?

Examples:
- CycloneDX;
- SPDX (not yet researched in this pack).

### Build provenance / artifact attestation
Where/how/by what builder was a produced artifact built?

Examples:
- SLSA provenance;
- GitHub artifact attestations.

### Artifact signing / integrity verification
Can a consumer verify an artifact/release came from the expected signing/provenance process?

These are related but different.

## V4 applicability model

### Local script / local-only internal source
Usually:
- reproducible environment may be useful;
- formal SBOM/provenance/signing usually `not_applicable` or `recommended`, not mandatory.

### Published library/package
Potentially:
- reproducible build;
- dependency transparency;
- compatibility/versioning;
- SBOM/provenance if ecosystem/org/security policy justifies it.

### Distributed binary/container/release
Stronger candidate:
- artifact digest;
- provenance/attestation;
- SBOM;
- signing/integrity verification;
- release versioning.

### Regulated/high-risk/enterprise software
May be `required` by policy/regulation.

## CI security

Generating a CI pipeline creates privileged executable code.

For GitHub Actions, Koda should inspect:
- `permissions:` least privilege;
- third-party action pinning/update process;
- secret exposure;
- OIDC vs long-lived cloud credentials when supported;
- untrusted contributor-controlled values interpolated into `run:`/scripts;
- fork/PR execution and secret boundaries;
- release/attestation permissions.

Do not treat “CI exists” as automatically secure.

## Pinning nuance

Pinning helps reproducibility/integrity but can freeze vulnerable versions.

Koda should distinguish:
- resolved application/end-product dependency graph;
- published library dependency constraints;
- CI/build action/image dependencies;
- update automation/process.

No universal `== everything forever` policy.

## Candidate V4 capabilities

- `dependency_reproducibility`
- `component_inventory`
- `build_provenance`
- `artifact_integrity`
- `ci_security`

Each independently resolved by project role/risk/distribution.
