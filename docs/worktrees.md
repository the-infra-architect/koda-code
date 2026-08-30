# Git and Worktrees

`begin --prepare-worktree` creates a mission-specific `feature/...` branch in a sibling worktree
folder. It refuses a non-Git project, an existing destination, or an existing branch.

Worktrees isolate concurrent mutable work; they are not substitutes for test, deployment, or
production environments. Stable branches remain protected and delivery occurs through a focused
commit and, when configured, a pull request.

`run` validates the recorded repository relationship, sibling location, branch, HEAD, and Git
staging area before accepting role evidence. Every mutable Copilot process uses the mission
worktree as its working directory. Reviewer and Debugger are read-only, and Koda rejects their
result if the worktree changes.

`finish` stages only paths named by the operator. It refuses protected branches, incomplete role
evidence, failed or missing checks, unrelated pre-staged changes, missing files, suspected secrets,
and blank commit messages. Push and pull-request creation require explicit flags.
