# Iteration 3 — Greenfield Discovery Model

Koda must be able to select architecture for a new project **without asking a beginner to design the stack**.

## Principle

Only ask facts that materially change the engineering design and cannot be inferred.

Technical users may answer in technical language. Nontechnical users should receive product-language questions.

## Minimum decision axes

| Engineering fact needed | Beginner-facing form if needed | Why it matters |
|---|---|---|
| audience/access | “Who needs to use this: only you, a small team, anyone in the company, or the public?” | deployment/auth/concurrency/security |
| location | “Does it need to work only on this computer, on several company computers, or online?” | local/server/cloud/network topology |
| simultaneous use | “Can several people use or edit it at the same time?” | DB/concurrency/session design |
| durable data value | “If this data disappeared, how serious would that be?” | backup/recovery/persistence |
| sensitivity | “Does it contain private, financial, customer, employee, or other sensitive information?” | threat/security controls |
| scale | “Roughly how many users or how much data do you expect?” | architecture/performance/storage |
| offline/restricted | “Does it need to work without internet, or in an environment where software/services cannot be freely installed?” | dependency/hosting/tool selection |
| target devices/OS | “Where will people use it: browser, Windows/Mac app, phone, command line, other?” | framework/package/UI |
| integrations | “Does it need to connect to any existing systems, files, APIs, or databases?” | boundaries/auth/data flow |
| expert stack constraint | direct technical instruction, if provided | treat as requirement |
| deployment ownership | “Where can this actually run after it is built?” only if not inferable | feasibility/operability |
| availability importance | “If it is unavailable for an hour/day, what happens?” only if material | reliability/HA/ops |

## Progressive questioning rule

Do **not** ask the whole table.

Example:
- A personal offline workout tracker may need no follow-up if local browser/app + local durable data is obvious and low risk.
- A company inventory system used by six people may need one question about simultaneous access / where it runs.
- A public payment workflow needs more explicit security/reliability/data questions.

## Architecture selection record

Before material greenfield architecture, Koda should be able to state internally:

- user outcome;
- explicit constraints;
- deployment topology;
- writer/concurrency topology;
- data sensitivity/value;
- scale/performance expectations;
- important quality attributes;
- available environment/tools;
- chosen architecture;
- why simpler alternatives do not satisfy requirements (if sophisticated);
- why more complex alternatives are unnecessary (if simple).

This is an internal reasoning/evidence record, not a long questionnaire shown to the user.

## Forbidden behavior

- “Dashboard → React + FastAPI + DuckDB.”
- “Web app → Next.js.”
- “Data app → DuckDB.”
- “Team app → Kubernetes.”
- “No Docker detected → ask beginner what Docker is.”
- Installing cloud infrastructure the user cannot access.
