# Technology / Project Signal Matrix

This is a **detection matrix**, not a blueprint catalog.

| Ecosystem | Strong signals | Existing commands/config Koda should inspect first | Reproducibility signals | Important note |
|---|---|---|---|---|
| Python | `pyproject.toml`, setup/pytest/type/lint config | configured scripts/tools, uv/tox/nox/etc if present | uv/poetry/pdm/pylock/requirements lock state | do not migrate package manager to standardize |
| JS/TS | `package.json`, `tsconfig*.json`, framework config | package scripts (`test`, `lint`, `build`, `typecheck`) | npm/pnpm/yarn/bun lockfile | scripts are stronger evidence than guessed commands |
| Maven/Java | `pom.xml`, `mvnw` | Maven lifecycle; wrapper | dependency/plugin/reproducible build config | prefer wrapper if present |
| Gradle/JVM | `build.gradle*`, `settings.gradle*`, `gradlew` | `check`, `test`, project tasks | wrapper/locking if configured | custom test suites/tasks are common |
| .NET | `*.sln`, `*.csproj`, `global.json`, `Directory.Build.*` | `dotnet build/test` or repo scripts | SDK/package lock/central mgmt if present | respect solution boundaries |
| Rust | `Cargo.toml`, `Cargo.lock` | `cargo test`, configured fmt/clippy | Cargo lock policy | lint allowances can be intentional |
| Go | `go.mod`, `go.sum`, `go.work` | `go test`, `go vet`, repo scripts | module state | `go.work` may indicate multiple modules |
| Nx monorepo | `nx.json`, project configs | native targets / `nx affected` | workspace package lock | reuse graph; shared changes may widen |
| Turborepo/workspaces | `turbo.json`, workspace config | existing turbo/package scripts | workspace lock | do not invent another task graph |
| GitHub CI | `.github/workflows/*` | workflow-defined commands + local equivalents | action refs + package locks | service/plan capabilities vary |
| Sonar | sonar property/config/workflow | existing configured gate | external service config | preserve if present; optional otherwise |
| Containers | Docker/Compose/devcontainer files | existing build/run | image pin/policy | presence ≠ every component must be containerized |
| DB migrations | Alembic/Flyway/Liquibase/ORM migrations | existing migration command | versioned migrations | never create parallel migration system casually |
| Web UI | React/Next/Vue/Svelte/etc | framework package scripts | package lock | accessibility/interaction checks relevant |
| Data/analytics | DuckDB/Polars/Pandas/Spark/dbt/Parquet configs | project-native data/tests | env lock + data/schema contracts | data size/query shape/storage matter |
| IaC | Terraform/Pulumi/Bicep/CloudFormation/K8s | existing validate/plan/lint | provider/module pins | do not add IaC if deployment is local-only |

## Detection precedence

1. Explicit user constraints.
2. Repository-local instructions/policy.
3. Existing package/build/test/CI scripts.
4. Lockfiles/version-manager/wrapper files.
5. Framework/ecosystem conventions.
6. Installed local capabilities.
7. Koda recommendation only after the above.

A marker tells Koda **what exists**, not automatically **what should be added or expanded**.
