# Contributing

1. Start from a concrete user outcome and record acceptance behavior.
2. Inspect the existing project before choosing architecture.
3. Create a focused branch or worktree; never work directly on a protected branch.
4. Implement the smallest coherent change using project conventions.
5. Add meaningful tests and run the deterministic quality gate.
6. Review for correctness, clarity, security, resource use, and proportionality.
7. Deliver through a pull request when a remote workflow exists.

Run before review:

```bash
uv sync --python 3.11 --extra dev --locked
uv run koda check self-check
```

Do not add a dependency, abstraction, service, or framework without explaining which concrete
requirement makes it the least complex responsible choice.

