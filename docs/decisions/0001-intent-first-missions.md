# ADR 0001: Intent-first engineering missions

Status: accepted for V1

## Context

The target user may describe a software outcome without knowing framework, database, deployment, or
Git vocabulary. A command collection centered on repository maintenance would expose the wrong
abstraction and encourage technical questions before product understanding.

## Decision

The core record is an engineering mission containing the requested outcome, bounded project
evidence, product-language questions, explicit technical constraints, a proportionate approach,
role assignments, stage evidence, quality results, and optional delivery state.

The default route is Engineer, Tester, and Reviewer. UI/UX is evidence-triggered; Debugger is
failure-triggered. Git, worktrees, checks, and pull requests remain supporting boundaries.

## Consequences

The beginner-facing path starts with desired behavior. Expert constraints remain visible. The system
can defer architecture when product facts are missing without pretending a universal stack is safe.
V1 does not implement a provider or autonomous executor; compatible coding assistants consume the
mission and role contracts.

