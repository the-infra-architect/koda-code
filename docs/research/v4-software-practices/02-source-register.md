# Source Register

Research snapshot: **2026-08-29**

Authority is scoped. Tool/vendor docs describe mechanics; they do not automatically establish universal necessity.

## S001 — ISO/IEC 25010:2023 — Systems and software Quality Requirements and Evaluation (SQuaRE): Product quality model
- URL: https://www.iso.org/standard/78176.html
- Authority: International standard
- Scope: Software product quality model
- Used for: Treat software quality as multidimensional rather than a single simplicity/quality score.
- Caveat: Public abstract supports model-level claims; full normative text is not reproduced here.

## S002 — SEI — Reasoning About Software Quality Attributes
- URL: https://www.sei.cmu.edu/library/reasoning-about-software-quality-attributes/
- Authority: SEI / architecture research
- Scope: Architecture and quality attributes
- Used for: Architecture decisions should be reasoned about through concrete quality-attribute scenarios.
- Caveat: Foundational architecture guidance; implementation mechanisms still depend on project context.

## S003 — SEI — Architecture Tradeoff Analysis Method
- URL: https://www.sei.cmu.edu/library/the-architecture-tradeoff-analysis-method/
- Authority: SEI / architecture research
- Scope: Architecture tradeoffs
- Used for: Quality attributes can conflict; architecture involves explicit tradeoffs.
- Caveat: Koda should borrow the reasoning principle, not reproduce enterprise ATAM ceremony.

## S004 — SEI — Maintainability
- URL: https://www.sei.cmu.edu/library/maintainability/
- Authority: SEI / architecture research
- Scope: Maintainability as a quality attribute
- Used for: Maintainability should be considered as a requirement/architectural concern.
- Caveat: Architecture-level guidance.

## S005 — SEI — Modifiability Tactics
- URL: https://www.sei.cmu.edu/library/modifiability-tactics/
- Authority: SEI / architecture research
- Scope: Coupling, cohesion, modifiability tactics
- Used for: Supports reasoning about change cost and structural boundaries.
- Caveat: Do not automatically apply every tactic or turn them into mandatory patterns.

## S006 — Google Engineering Practices — What to look for in a code review
- URL: https://google.github.io/eng-practices/review/reviewer/looking-for.html
- Authority: Major practitioner engineering guide
- Scope: Code review
- Used for: Review design, functionality, complexity, tests, naming, comments/documentation, and maintainability.
- Caveat: Google-specific process details are not universal.

## S007 — Google Engineering Practices — The standard of code review
- URL: https://google.github.io/eng-practices/review/reviewer/standard.html
- Authority: Major practitioner engineering guide
- Scope: Code review acceptance
- Used for: Improve code health rather than block all progress until theoretical perfection.
- Caveat: Risk-critical systems may have higher required acceptance standards.

## S008 — Google Engineering Practices — Small CLs
- URL: https://google.github.io/eng-practices/review/developer/small-cls.html
- Authority: Major practitioner engineering guide
- Scope: Change size/reviewability
- Used for: Small, focused, self-contained changes improve reviewability and integration.
- Caveat: There is no universal line-count threshold; some coherent changes are necessarily large.

## S009 — Google Go Style Guide — Style principles
- URL: https://google.github.io/styleguide/go/guide.html
- Authority: Major practitioner/ecosystem guide
- Scope: Clarity, simplicity, maintainability, consistency
- Used for: Code should be optimized for readers; abstractions should map to the problem and justify their cost.
- Caveat: Examples are Go-specific; project conventions win.

## S010 — Google TypeScript Style Guide
- URL: https://google.github.io/styleguide/tsguide.html
- Authority: Major practitioner/ecosystem guide
- Scope: Naming and TypeScript style
- Used for: Descriptive names and meaningful interface naming.
- Caveat: Google-specific conventions are not universal.

## S011 — Google Documentation Best Practices
- URL: https://google.github.io/styleguide/docguide/best_practices.html
- Authority: Major practitioner guide
- Scope: Documentation
- Used for: Prefer minimum viable, accurate documentation and update it with code.
- Caveat: Regulated/public API contexts may require more extensive documentation.

## S012 — DORA — Test automation
- URL: https://dora.dev/capabilities/test-automation/
- Authority: Research-backed practitioner guidance
- Scope: Testing and delivery feedback
- Used for: Fast, reliable automated feedback is valuable; manual exploratory/usability testing still has a role.
- Caveat: Not every recommendation on the page should become a universal Koda mandate.

## S013 — Google Testing Blog — How Much Testing is Enough?
- URL: https://testing.googleblog.com/2021/06/how-much-testing-is-enough.html
- Authority: Major practitioner testing guidance
- Scope: Risk/context-sensitive test strategy
- Used for: Testing depth depends on software purpose/audience; integration and critical-user-flow testing matter.
- Caveat: Heuristics are practitioner guidance rather than formal standard.

## S014 — Google Testing Blog — Code Coverage Best Practices
- URL: https://testing.googleblog.com/2020/08/code-coverage-best-practices.html
- Authority: Major practitioner testing guidance
- Scope: Coverage
- Used for: Coverage is a gap/risk signal rather than a universal quality score.
- Caveat: Do not promote Google-specific numeric heuristics into universal gates.

## S015 — Microsoft .NET — Unit testing best practices
- URL: https://learn.microsoft.com/en-us/dotnet/core/testing/unit-testing-best-practices
- Authority: Ecosystem/vendor guidance
- Scope: Unit testing
- Used for: Good unit tests are fast/repeatable/isolated; high coverage alone does not establish quality.
- Caveat: .NET examples; general principles are broader.

## S016 — Google Research / ICSE — Long Term Effects of Mutation Testing
- URL: https://research.google/pubs/long-term-effects-of-mutation-testing/
- Authority: Peer-reviewed empirical research
- Scope: Mutation testing
- Used for: Mutation testing can reveal meaningful test gaps and correlate with real faults.
- Caveat: Cost/process overhead makes it selective rather than universal.

## S017 — NIST SP 800-218 — Secure Software Development Framework (SSDF) 1.1
- URL: https://csrc.nist.gov/pubs/sp/800/218/final
- Authority: US government standard/guidance
- Scope: Secure SDLC
- Used for: Security practices should be integrated into software development rather than bolted on later.
- Caveat: High-level framework; implementation is context-dependent.

## S018 — NIST IR 8397 — Guidelines on Minimum Standards for Developer Verification of Software
- URL: https://csrc.nist.gov/pubs/ir/8397/final
- Authority: US government guidance
- Scope: Software verification/security testing
- Used for: Threat modeling, automated tests, static scanning, secret detection, built-in protections, black-box/structural/historical tests, fuzzing, web scanning when applicable, and dependency review.
- Caveat: The document itself says it does not cover the totality of verification; techniques still require applicability judgment.

## S019 — OWASP Application Security Verification Standard (ASVS) 5.0.0
- URL: https://owasp.org/www-project-application-security-verification-standard/
- Authority: Industry security standard
- Scope: Web application/service security
- Used for: Provides testable web security requirements.
- Caveat: Web-focused; do not apply wholesale to local scripts/desktop-only software.

## S020 — OWASP Threat Modeling Cheat Sheet
- URL: https://cheatsheetseries.owasp.org/cheatsheets/Threat_Modeling_Cheat_Sheet.html
- Authority: Industry security guidance
- Scope: Threat modeling
- Used for: Structured process: model system, identify what can go wrong, choose mitigations, validate.
- Caveat: Depth should be proportional to exposure and risk.

## S021 — OWASP Secrets Management Cheat Sheet
- URL: https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html
- Authority: Industry security guidance
- Scope: Secrets
- Used for: Keep secrets out of source/logs and manage lifecycle/privilege appropriately.
- Caveat: Exact mechanism depends on environment/infrastructure.

## S022 — OWASP Software Component Verification Standard (SCVS)
- URL: https://scvs.owasp.org/
- Authority: Industry supply-chain standard
- Scope: Software supply-chain assurance
- Used for: Component inventory, package management, analysis, provenance, and risk-based maturity.
- Caveat: Risk-acceptance criteria are organizational/business decisions; Koda must not invent legal/risk policy.

## S023 — NIST NCCoE DevSecOps — Role of AI in software development
- URL: https://pages.nist.gov/nccoe-devsecops/introduction.html
- Authority: US government guidance/project
- Scope: AI-generated software in DevSecOps
- Used for: AI-generated content should be monitored/validated and supported by verifiable processes.
- Caveat: Project guidance evolves; use SSDF as the stable baseline.

## S024 — Fu et al. — Security Weaknesses of Copilot-Generated Code in GitHub Projects
- URL: https://arxiv.org/abs/2310.02059
- Authority: Empirical preprint/research
- Scope: Security of AI-generated code
- Used for: Supports independent verification of AI-generated code.
- Caveat: Model/tool/time/dataset-specific percentages must not be generalized.

## S025 — DORA — Trunk-based development
- URL: https://dora.dev/capabilities/trunk-based-development/
- Authority: Research-backed practitioner guidance
- Scope: Branch/integration practice
- Used for: Short-lived branches and frequent integration reduce integration burden.
- Caveat: Koda can still use feature worktrees; isolation does not require long-lived branches.

## S026 — DORA — Continuous delivery
- URL: https://dora.dev/capabilities/continuous-delivery/
- Authority: Research-backed practitioner guidance
- Scope: Delivery
- Used for: Keep software releasable; continuous delivery is distinct from automatic deployment.
- Caveat: Local/offline software may have no hosted deployment pipeline.

## S027 — DORA — Version control
- URL: https://dora.dev/capabilities/version-control/
- Authority: Research-backed practitioner guidance
- Scope: Versioned engineering artifacts
- Used for: Version application, tests, build/deploy/config/migrations and relevant AI prompts/agent config.
- Caveat: Large binary artifacts may belong in artifact/blob storage rather than Git.

## S028 — DORA — Code maintainability
- URL: https://dora.dev/capabilities/code-maintainability/
- Authority: Research-backed practitioner guidance
- Scope: Dependency/build traceability
- Used for: Traceable dependencies and reproducible builds/installations support maintainability.
- Caveat: Does not prescribe one package manager or lock strategy.

## S029 — Git — git-worktree documentation
- URL: https://git-scm.com/docs/git-worktree
- Authority: Primary tool documentation
- Scope: Git worktrees
- Used for: Authoritative behavior for linked worktrees and lifecycle.
- Caveat: Worktrees are a Koda isolation mechanism, not a universal team branching policy.

## S030 — GitHub Actions — Secure use reference
- URL: https://docs.github.com/en/actions/reference/security/secure-use
- Authority: Primary platform documentation
- Scope: GitHub Actions security
- Used for: Full commit SHA is GitHub's immutable reference for third-party actions; secure workflow configuration.
- Caveat: GitHub-specific; update automation/policy may be needed.

## S031 — GitHub — Dependency review
- URL: https://docs.github.com/en/code-security/concepts/supply-chain-security/dependency-review
- Authority: Primary platform documentation
- Scope: Dependency changes
- Used for: Can surface dependency vulnerabilities/licenses when platform capability is available.
- Caveat: Availability depends on repository type/plan/settings.

## S032 — GitHub — CodeQL code scanning
- URL: https://docs.github.com/en/code-security/concepts/code-scanning/codeql/codeql-code-scanning
- Authority: Primary platform documentation
- Scope: Static security analysis
- Used for: CodeQL supports a defined language set and can identify vulnerabilities/errors.
- Caveat: Unsupported languages/frameworks require different tooling; platform/plan constraints apply.

## S033 — SonarQube — About new code
- URL: https://docs.sonarsource.com/sonarqube-cloud/standards/about-new-code
- Authority: Primary vendor documentation
- Scope: Changed/new-code quality
- Used for: Supports focusing quality improvement on changed/new code.
- Caveat: Sonar-specific methodology.

## S034 — SonarQube — Quality gates
- URL: https://docs.sonarsource.com/sonarqube-server/2026.1/quality-standards-administration/managing-quality-gates/introduction-to-quality-gates
- Authority: Primary vendor documentation
- Scope: Quality gates
- Used for: Quality gates are customizable and may differ across projects.
- Caveat: Built-in numeric defaults are vendor defaults, not universal engineering laws.

## S035 — Microsoft Engineering Playbook — Observability recommended practices
- URL: https://microsoft.github.io/code-with-engineering-playbook/observability/best-practices/
- Authority: Major practitioner guidance
- Scope: Observability
- Used for: Collect actionable failure/dependency/latency signals, start small, avoid sensitive logging.
- Caveat: Service-oriented; not every script/local app needs logs+metrics+traces.

## S036 — Azure Well-Architected — Performance Efficiency principles
- URL: https://learn.microsoft.com/en-us/azure/well-architected/performance-efficiency/principles
- Authority: Major vendor architecture guidance
- Scope: Performance engineering
- Used for: Use realistic performance targets, measurement, iterative optimization, and efficient resource use.
- Caveat: Cloud-oriented source; general measurement principle is broader.

## S037 — Azure Architecture Center — Transient fault handling
- URL: https://learn.microsoft.com/en-us/azure/architecture/best-practices/transient-faults
- Authority: Major vendor architecture guidance
- Scope: Retries/reliability
- Used for: Retry only likely transient faults; use bounded attempts, timeouts, backoff/jitter, and idempotency awareness.
- Caveat: Remote/distributed dependency context; not a reason to add retry frameworks to local computation.

## S038 — DuckDB — Why DuckDB
- URL: https://www.duckdb.org/why_duckdb
- Authority: Primary project documentation
- Scope: DuckDB workload/architecture
- Used for: DuckDB targets analytical/OLAP workloads and embedded simplicity; explicitly says no DB is one-size-fits-all.
- Caveat: Project source is authoritative about DuckDB, not other databases.

## S039 — DuckDB — Concurrency
- URL: https://duckdb.org/docs/current/connect/concurrency
- Authority: Primary project documentation
- Scope: DuckDB concurrent access
- Used for: Documents process/write concurrency, optimistic conflicts, and current DuckLake/Quack options.
- Caveat: DuckDB is evolving rapidly; version/capability must be checked.

## S040 — DuckDB — Environment / network-attached disks
- URL: https://duckdb.org/docs/current/guides/performance/environment
- Authority: Primary project documentation
- Scope: DuckDB storage environment
- Used for: Warns against native read-write DuckDB on NAS/NFS/SMB/Samba; read-only network storage differs.
- Caveat: Cloud block disks and lakehouse formats have different semantics.

## S041 — DuckDB — Tuning Workloads
- URL: https://duckdb.org/docs/current/guides/performance/how_to_tune_workloads
- Authority: Primary project documentation
- Scope: DuckDB performance/resource behavior
- Used for: Analytical workload focus, profiling, memory caveats, remote I/O, connection reuse.
- Caveat: DuckDB-specific optimizations should not become universal DB rules.

## S042 — SQLite — Appropriate Uses For SQLite
- URL: https://www.sqlite.org/whentouse.html
- Authority: Primary project documentation
- Scope: Embedded vs client/server database selection
- Used for: Client/server is preferable for many concurrent writers/direct network clients; embedded DB is strong for local low-write-concurrency use.
- Caveat: This research does not make SQLite Koda's default; it provides useful workload decision axes.

## S043 — SQLite — SQLite Over a Network, Caveats and Considerations
- URL: https://www.sqlite.org/useovernet.html
- Authority: Primary project documentation
- Scope: Network filesystem database risk
- Used for: Network filesystem locking/sync can be unreliable and may corrupt databases.
- Caveat: Filesystem implementation matters; client/server architecture avoids direct DB file sharing.

## S044 — PostgreSQL 18 — Concurrency Control
- URL: https://www.postgresql.org/docs/18/mvcc.html
- Authority: Primary project documentation
- Scope: Multi-session transactional concurrency
- Used for: PostgreSQL provides MVCC/locking/isolation for multiple concurrent sessions.
- Caveat: PostgreSQL is an example of client/server transactional architecture, not a universal database default.

## S045 — PostgreSQL 18 — Backup and Restore
- URL: https://www.postgresql.org/docs/current/backup.html
- Authority: Primary project documentation
- Scope: Persistent-data recovery
- Used for: Different backup approaches carry tradeoffs; durable valuable data needs recovery planning.
- Caveat: Mechanisms are PostgreSQL-specific.

## S046 — PostgreSQL 18 — ALTER TABLE
- URL: https://www.postgresql.org/docs/current/sql-altertable.html
- Authority: Primary project documentation
- Scope: Schema migration locking
- Used for: Schema changes may acquire strong locks; migration risk depends on operation/workload.
- Caveat: Exact behavior is PostgreSQL-specific.

## S047 — Python Packaging — pyproject.toml specification
- URL: https://packaging.python.org/en/latest/specifications/pyproject-toml/
- Authority: Primary ecosystem specification
- Scope: Python project/build/tool metadata
- Used for: Canonical signal for Python build/project/tool configuration.
- Caveat: Legacy and tool-specific project layouts still exist.

## S048 — Python Packaging — pylock.toml specification
- URL: https://packaging.python.org/en/latest/specifications/pylock-toml/
- Authority: Primary ecosystem specification
- Scope: Python reproducible environments
- Used for: Standards-based lock-file semantics.
- Caveat: Python currently has multiple lock mechanisms; Koda must preserve existing tool choice.

## S049 — npm — package-lock.json
- URL: https://docs.npmjs.com/files/package-lock.json/
- Authority: Primary ecosystem documentation
- Scope: JavaScript dependency locking
- Used for: Exact dependency tree/reproducible npm installs and source-controlled lock state.
- Caveat: pnpm/yarn/bun use different lock formats.

## S050 — Maven — Build Lifecycle
- URL: https://maven.apache.org/guides/introduction/introduction-to-the-lifecycle.html
- Authority: Primary ecosystem documentation
- Scope: Maven build/test lifecycle
- Used for: Use configured native lifecycle before inventing bespoke commands.
- Caveat: Project plugins may extend/change behavior.

## S051 — Maven — Reproducible Builds
- URL: https://maven.apache.org/guides/mini/guide-reproducible-builds.html
- Authority: Primary ecosystem documentation
- Scope: Build reproducibility
- Used for: Reproducible artifacts are a deliberate build property and can be verified.
- Caveat: Bit-for-bit reproducibility may need plugin/environment work.

## S052 — TypeScript — strict TSConfig option
- URL: https://www.typescriptlang.org/tsconfig/strict
- Authority: Primary ecosystem documentation
- Scope: TypeScript type strictness
- Used for: Strict mode gives stronger type-checking guarantees.
- Caveat: Enabling it in an existing project can be a migration; preserve project policy.

## S053 — Rust Cargo — cargo test
- URL: https://doc.rust-lang.org/cargo/commands/cargo-test.html
- Authority: Primary ecosystem documentation
- Scope: Rust testing lifecycle
- Used for: Use native project test lifecycle.
- Caveat: Projects may define extra checks.

## S054 — Rust Clippy — Usage
- URL: https://doc.rust-lang.org/stable/clippy/usage.html
- Authority: Primary ecosystem documentation
- Scope: Rust linting
- Used for: Clippy provides configurable lint levels; allowances can be deliberate.
- Caveat: Do not turn all optional lints into hard failures.

## S055 — Go — Modules Reference
- URL: https://go.dev/ref/mod
- Authority: Primary ecosystem documentation
- Scope: Go module/dependency configuration
- Used for: Detect module/workspace state and use native lifecycle.
- Caveat: Multi-module workspaces require `go.work` awareness.

## S056 — .NET CLI — dotnet test
- URL: https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-test
- Authority: Primary ecosystem documentation
- Scope: .NET testing lifecycle
- Used for: Use native solution/project test lifecycle.
- Caveat: Runner/config differ across SDK/project.

## S057 — Gradle — Testing in Java/JVM projects
- URL: https://docs.gradle.org/current/userguide/java_testing.html
- Authority: Primary ecosystem documentation
- Scope: Gradle/JVM testing lifecycle
- Used for: Use existing test/check lifecycle and configured suites.
- Caveat: Builds can define custom tasks/suites.

## S058 — Nx — Affected tasks
- URL: https://nx.dev/docs/features/ci-features/affected
- Authority: Primary tool documentation
- Scope: Monorepo/project graph
- Used for: Reuse existing affected/project-graph tooling to scope checks.
- Caveat: Shared lock/config changes may broaden impact.

## S059 — W3C — Web Content Accessibility Guidelines (WCAG) 2.2
- URL: https://www.w3.org/TR/WCAG22/
- Authority: Web standard
- Scope: Web accessibility
- Used for: Testable accessibility criteria for web UI.
- Caveat: Applicable primarily to web content; legal obligations vary.

## S060 — W3C — Using ARIA
- URL: https://www.w3.org/TR/using-aria/
- Authority: Web standard/guidance
- Scope: Accessible semantics/interactions
- Used for: Prefer native HTML semantics and preserve keyboard interaction.
- Caveat: Custom widgets may legitimately require ARIA.

## S061 — GOV.UK Service Manual — Start by learning user needs
- URL: https://www.gov.uk/service-manual/user-research/start-by-learning-user-needs
- Authority: Government service-design guidance
- Scope: Outcome/user-language discovery
- Used for: Focus on the user's problem/outcome and use language they recognize.
- Caveat: Government-service context; principles should later be tested with Koda users.

## S062 — GOV.UK Service Manual — Designing good questions
- URL: https://www.gov.uk/service-manual/design/designing-good-questions
- Authority: Government service-design guidance
- Scope: Question design
- Used for: Ask only needed information and use understandable language.
- Caveat: Service-form context; use the principle, not form-specific UI.

## S063 — Semantic Versioning 2.0.0
- URL: https://semver.org/
- Authority: Published versioning specification
- Scope: Public API versioning
- Used for: If a project declares SemVer, incompatible public API changes map to major releases and compatible additions/fixes to minor/patch semantics.
- Caveat: SemVer applies only when the project defines a public API and chooses SemVer; Koda must not force it on every project.

## S064 — Microsoft REST API Guidelines
- URL: https://github.com/microsoft/api-guidelines
- Authority: Major practitioner API guidance
- Scope: Existing/new REST APIs and compatibility
- Used for: Existing services should not receive breaking changes merely to comply with newer guidelines; breaking API changes require explicit versioning policy.
- Caveat: Microsoft conventions are not a universal REST standard; the compatibility principle generalizes better than exact version mechanics.

## S065 — GitHub REST API — Breaking changes
- URL: https://docs.github.com/en/rest/about-the-rest-api/breaking-changes
- Authority: Primary platform API documentation
- Scope: API compatibility/versioning
- Used for: Concrete examples of breaking vs additive changes and explicit supported-version migration.
- Caveat: GitHub-specific API contract; exact support windows are not universal.

## S066 — Kubernetes Deprecation Policy
- URL: https://kubernetes.io/docs/reference/using-api/deprecation-policy/
- Authority: Primary project policy
- Scope: API stability/deprecation
- Used for: Stable APIs require explicit compatibility/deprecation discipline and versioned removal.
- Caveat: Kubernetes timelines/tracks are project-specific, not Koda defaults.

## S067 — SLSA v1.2 — Build requirements
- URL: https://slsa.dev/spec/v1.2/build-requirements
- Authority: Industry supply-chain specification
- Scope: Build provenance and isolation
- Used for: Build provenance identifies artifact outputs and how they were produced; stronger levels add integrity guarantees.
- Caveat: Intended for produced/distributed artifacts and supply-chain assurance; not every local script needs SLSA provenance.

## S068 — CycloneDX Specification Overview
- URL: https://cyclonedx.org/specification/overview/
- Authority: OWASP/Ecma standard
- Scope: Software/system bill of materials
- Used for: Machine-readable representation of components, dependencies, services and related software supply-chain information.
- Caveat: An SBOM describes inventory/transparency; it is not itself build provenance or proof that components are safe.

## S069 — GitHub — Artifact attestations
- URL: https://docs.github.com/en/actions/concepts/security/artifact-attestations
- Authority: Primary platform documentation
- Scope: Build artifact provenance/integrity
- Used for: Signed attestations can establish where/how GitHub-built artifacts were produced.
- Caveat: Availability differs by GitHub plan/repository visibility; not a universal requirement.

## S070 — OpenSSF Scorecard — Checks documentation
- URL: https://github.com/ossf/scorecard/blob/main/docs/checks.md
- Authority: OpenSSF security project
- Scope: Repository/supply-chain security checks
- Used for: Pinning, token permissions, update tools and vulnerability checks have distinct tradeoffs; least-privilege CI tokens matter.
- Caveat: Scorecard scoring is a tool heuristic, not a universal Koda quality score.

## S071 — GitHub — OpenID Connect reference
- URL: https://docs.github.com/en/actions/reference/security/oidc
- Authority: Primary platform documentation
- Scope: CI cloud authentication
- Used for: OIDC enables workflows to obtain short-lived tokens rather than relying solely on stored long-lived cloud credentials.
- Caveat: Only relevant when GitHub Actions authenticates to compatible external services.

## S072 — GitHub Actions — Secure use reference
- URL: https://docs.github.com/en/actions/reference/security/secure-use
- Authority: Primary platform documentation
- Scope: Workflow security
- Used for: Least privilege, secrets handling, third-party action risk, and safe handling of untrusted values in workflows.
- Caveat: GitHub Actions-specific.

## S073 — GitHub Actions — Script injections
- URL: https://docs.github.com/en/actions/concepts/security/script-injections
- Authority: Primary platform documentation
- Scope: Untrusted workflow input
- Used for: Repository/PR metadata can be attacker-controlled and must not be interpolated directly into executable scripts.
- Caveat: GitHub Actions-specific manifestation of a general untrusted-input principle.

## S074 — OWASP CI/CD Security Cheat Sheet
- URL: https://cheatsheetseries.owasp.org/cheatsheets/CI_CD_Security_Cheat_Sheet.html
- Authority: Industry security guidance
- Scope: CI/CD attack surface
- Used for: CI/CD is privileged infrastructure; least privilege, pipeline integrity, secret hygiene, dependency-chain and poisoned-pipeline risks matter.
- Caveat: Exact mitigations depend on the CI platform and threat model.

## S075 — CISA et al. — Shifting the Balance of Cybersecurity Risk: Secure by Design and Default
- URL: https://www.cisa.gov/sites/default/files/2023-06/principles_approaches_for_security-by-design-default_508c.pdf
- Authority: Multi-government secure-by-design guidance
- Scope: Secure defaults and customer burden
- Used for: Secure configuration should be the default and security complexity should not be pushed onto customers.
- Caveat: Product-manufacturer guidance; exact controls depend on product surface.

## S076 — CISA — Eliminating Buffer Overflow Vulnerabilities
- URL: https://www.cisa.gov/sites/default/files/2025-02/secure-by-design-alert-eliminating-buffer-overflow-vulnerabilities-508c.pdf
- Authority: US government secure-by-design guidance
- Scope: Memory safety
- Used for: Where feasible, memory-safe languages and safer toolchains reduce entire classes of memory-safety defects, especially in new/high-risk code.
- Caveat: Does not justify rewriting every existing C/C++ codebase or choosing a low-level memory-safe language for unrelated application work.

## S077 — CISA/FBI — Product Security Bad Practices update
- URL: https://www.cisa.gov/news-events/alerts/2025/01/17/cisa-and-fbi-release-updated-guidance-product-security-bad-practices
- Authority: US government secure-by-design guidance
- Scope: Product security
- Used for: Prioritize secure design, reduce known defect classes, and avoid shifting security burden to customers.
- Caveat: Originally aimed at products supporting critical infrastructure; broader applicability should remain risk-proportional.

## S078 — The Twelve-Factor App — Config
- URL: https://www.12factor.net/config
- Authority: Influential practitioner methodology
- Scope: Deploy-varying service configuration
- Used for: Separates deploy-varying configuration/credentials from source code.
- Caveat: Environment variables are not a universal mechanism for desktop/local/embedded software; use the separation principle, not dogma.

## S079 — OWASP Input Validation Cheat Sheet
- URL: https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html
- Authority: Industry security guidance
- Scope: Untrusted input
- Used for: Validate untrusted data early, syntactically and semantically; prefer trusted/server-side enforcement and framework validators.
- Caveat: Allowlisting is strongest for structured/fixed inputs; free-form text requires more nuanced validation.

## S080 — OWASP Logging Cheat Sheet
- URL: https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html
- Authority: Industry security guidance
- Scope: Application logging
- Used for: Logs should avoid secrets/sensitive data, remain useful, and be protected from tampering/abuse.
- Caveat: Logging volume/content is operationally and legally context-dependent.

## S081 — OWASP Database Security Cheat Sheet
- URL: https://cheatsheetseries.owasp.org/cheatsheets/Database_Security_Cheat_Sheet.html
- Authority: Industry security guidance
- Scope: Database credentials/permissions/configuration
- Used for: Database identities should use least privilege; credentials must not be hard-coded; backup/security configuration matters.
- Caveat: Specific permission granularity and storage mechanisms differ by database/environment.

## S082 — PostgreSQL — Transactions
- URL: https://www.postgresql.org/docs/19/tutorial-transactions.html
- Authority: Primary project documentation
- Scope: Transactional atomicity
- Used for: Multi-step changes can be committed or rolled back as a unit.
- Caveat: PostgreSQL mechanics are specific; transactional concepts generalize to capable stores.

## S083 — PostgreSQL — Constraints
- URL: https://www.postgresql.org/docs/17/ddl-constraints.html
- Authority: Primary project documentation
- Scope: Data integrity constraints
- Used for: NOT NULL, UNIQUE, PK, FK and CHECK-like constraints can enforce invariants at the datastore boundary.
- Caveat: Exact constraint features/performance differ by database.

## S084 — Azure Architecture Center — Asynchronous Messaging Options
- URL: https://learn.microsoft.com/en-us/azure/architecture/guide/technology-choices/messaging
- Authority: Major vendor architecture guidance
- Scope: Message delivery/idempotency
- Used for: Duplicate delivery is a real distributed-system concern; consumers often need idempotent handling.
- Caveat: Only relevant when asynchronous messaging/at-least-once delivery exists.

## S085 — Azure Architecture Center — Microservices Assessment and Readiness
- URL: https://learn.microsoft.com/en-us/azure/architecture/guide/technology-choices/microservices-assessment
- Authority: Major vendor architecture guidance
- Scope: Microservices readiness/tradeoffs
- Used for: Microservices require business, organizational, infrastructure, deployment, testing and operational readiness; gaps should be prioritized by impact.
- Caveat: Azure/cloud perspective; use the readiness/tradeoff principle rather than Azure-specific platform choices.

## S086 — Azure Architecture Center — Microservices architecture style
- URL: https://learn.microsoft.com/azure/architecture/guide/architecture-styles/microservices
- Authority: Major vendor architecture guidance
- Scope: Microservices tradeoffs
- Used for: Microservices increase system-wide complexity, distributed consistency/testing/communication and governance burden.
- Caveat: Does not mean monoliths are always preferable.

## S087 — Azure Architecture Center — Cache-Aside Pattern
- URL: https://learn.microsoft.com/en-us/azure/architecture/patterns/cache-aside
- Authority: Major vendor architecture guidance
- Scope: Caching tradeoffs
- Used for: Caching introduces expiration, consistency, invalidation, capacity and multi-instance behavior that must be justified by access patterns.
- Caveat: Azure examples are implementation-specific; caching tradeoffs generalize.

## S088 — Microsoft Research — Principles of Eventual Consistency
- URL: https://www.microsoft.com/en-us/research/publication/principles-of-eventual-consistency/
- Authority: Research publication
- Scope: Distributed consistency
- Used for: Eventual consistency is a deliberate semantic tradeoff, not a free scalability feature.
- Caveat: Formal distributed-systems context; most simple applications should avoid introducing such complexity without need.

## S089 — Cargo Book — Cargo.toml vs Cargo.lock
- URL: https://doc.rust-lang.org/cargo/guide/cargo-toml-vs-cargo-lock.html
- Authority: Primary ecosystem documentation
- Scope: Dependency manifest vs resolved lock state
- Used for: Manifest constraints and exact resolved lock state serve different purposes.
- Caveat: Rust-specific; other ecosystems differ.

## S090 — Cargo Book — FAQ: Cargo.lock in version control
- URL: https://doc.rust-lang.org/cargo/faq.html
- Authority: Primary ecosystem documentation
- Scope: Application/library dependency locking
- Used for: Lockfile needs differ by package role; deterministic end products and reusable libraries have different dependency-resolution concerns.
- Caveat: Rust-specific evidence supporting a broader 'preserve ecosystem semantics' rule.

## S091 — Python Packaging — Dependency specifiers
- URL: https://packaging.python.org/en/latest/specifications/dependency-specifiers/
- Authority: Primary ecosystem specification
- Scope: Dependency requirements
- Used for: Python package dependencies may intentionally express version ranges, markers, extras or exact artifacts rather than one universal pin style.
- Caveat: Does not by itself prescribe application lock strategy.

## S092 — OpenSSF Scorecard — Beginner checks
- URL: https://github.com/ossf/scorecard/blob/main/docs/beginner-checks.md
- Authority: OpenSSF security project
- Scope: Dependency/update/workflow security
- Used for: Pinned dependencies should be paired with a process/tool for updates; token permissions should be least-privilege.
- Caveat: OpenSSF scoring/remediation is guidance, not a universal project score.

## S093 — CISA — Secure by Demand Guide
- URL: https://www.cisa.gov/sites/default/files/2024-08/SecureByDemandGuide_080624_508c.pdf
- Authority: US government secure-by-design guidance
- Scope: Software product security evidence
- Used for: SBOMs and vulnerability-class elimination are useful product/security evidence; secure building blocks reduce user/developer burden.
- Caveat: Procurement/product guidance; not every internal tool needs a formal SBOM.

## S094 — Azure Architecture Center — Retry Pattern
- URL: https://learn.microsoft.com/en-us/azure/architecture/patterns/retry
- Authority: Major vendor architecture guidance
- Scope: Retry/idempotency
- Used for: Retries need exception classification, bounded policy and idempotency awareness.
- Caveat: Remote/transient failures only.

## S095 — AWS Prescriptive Guidance — Transactional outbox pattern
- URL: https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html
- Authority: Major vendor architecture guidance
- Scope: Atomic DB + event workflows
- Used for: When a database update must reliably result in an event, naive dual writes can fail; transactional outbox and idempotent consumers are one applicable pattern.
- Caveat: Only applies to event-driven dual-write problems; do not add an outbox to ordinary CRUD apps.

## S096 — GitHub Actions — Script injection security
- URL: https://docs.github.com/en/actions/concepts/security/script-injections
- Authority: Primary platform documentation
- Scope: Workflow generated code safety
- Used for: Untrusted PR/issue/branch metadata can become command injection when interpolated into generated scripts.
- Caveat: GitHub Actions-specific implementation.

## S097 — Liquibase — Expand-Contract Pattern
- URL: https://www.liquibase.com/technical-glossary/expand-contract-pattern
- Authority: Primary database-migration tool guidance
- Scope: Backward-compatible schema evolution
- Used for: For rolling/zero-downtime systems, breaking schema changes can be decomposed into additive/migrate/remove phases.
- Caveat: Vendor pattern guidance; only necessary when old/new application versions overlap or downtime must be avoided.

## S098 — CycloneDX — Vulnerability Exploitability eXchange (VEX)
- URL: https://www.cyclonedx.org/capabilities/vex/
- Authority: OWASP/Ecma supply-chain standard capability
- Scope: Vulnerability applicability/exploitability context
- Used for: Distinguishes a vulnerable component finding from whether the specific product context is actually affected/exploitable.
- Caveat: VEX statements require trustworthy evidence; Koda must not manufacture 'not affected' claims.

## S099 — OpenVEX Specification
- URL: https://github.com/openvex/spec
- Authority: Community specification aligned to CISA VEX requirements
- Scope: Machine-readable vulnerability impact status
- Used for: Shows vulnerability status is product-contextual and can represent fixed/not-affected/investigating states.
- Caveat: OpenVEX is a draft/community format; do not require it universally.

## S100 — GitHub — Configure dependency review action
- URL: https://docs.github.com/en/code-security/how-tos/secure-your-supply-chain/manage-your-dependency-security/configure-dependency-review-action
- Authority: Primary platform documentation
- Scope: Dependency vulnerability/license policy
- Used for: Dependency review thresholds are configurable by vulnerability severity/scope and can enforce organization-specific license policy.
- Caveat: GitHub-specific and license acceptability is policy/legal context, not Koda judgment.
