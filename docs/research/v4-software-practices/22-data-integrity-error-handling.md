# Iteration 4 — Data Integrity, Error Handling, and Logging

## Data integrity layers

Koda should distinguish:

### Input validation
Is incoming data syntactically and semantically acceptable?

### Domain/business validation
Does the operation make sense in the business/domain state?

### Persistent constraints
Should the datastore itself prevent impossible states?

For relational stores, examples include:
- NOT NULL;
- UNIQUE;
- primary keys;
- foreign keys;
- check/exclusion constraints when appropriate.

Application-only checks can race or be bypassed by other writers/tools. Datastore constraints can make invariants durable when the store supports them.

Do not duplicate complex business workflows into constraints merely because constraints exist.

## Transactions

Use a transaction when a set of persistent changes must commit or roll back as one integrity unit.

Avoid:
- partial multi-step state changes;
- giant transactions containing unrelated work;
- network calls held inside DB transactions without a concrete reason;
- assuming distributed services share one transaction.

## Error handling

Good error behavior has two audiences:

### User/client
- understandable;
- does not leak internal stack traces/secrets;
- tells the user what they can do when appropriate.

### Maintainer/operator
- enough technical evidence to diagnose;
- structured/contextual where useful;
- correlated with request/job/operation when operational context needs it.

Do not swallow errors merely to keep the UI clean.

## Logging

Logs should be:
- useful;
- bounded;
- sensitive-data aware;
- protected appropriately;
- proportional to operational need.

Avoid logging:
- passwords/tokens/keys;
- raw sensitive records without purpose;
- connection strings/credentials;
- huge payloads by default.

Do not add a logging framework to a tiny script if clear stderr/errors are enough.

## Untrusted input

Validate at a trusted boundary.

Prefer:
- framework/schema validators;
- type/range/length checks;
- semantic/domain checks;
- parameterized database operations.

Avoid:
- fragile ad-hoc denylist filters;
- trusting client-side validation for security;
- passing untrusted values into shell/SQL/template contexts without safe APIs.
