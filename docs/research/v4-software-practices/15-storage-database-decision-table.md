# Iteration 3 — Storage / Database Decision Table

## Key finding

Database choice must follow workload and deployment topology, not brand preference.

DuckDB remains a strong Koda candidate for embedded analytical workloads, but official DuckDB guidance says to avoid native read-write DB files on NAS/NFS/SMB/Samba. SQLite independently warns about direct multi-client network-filesystem database access. PostgreSQL demonstrates the client/server model for concurrent transactional sessions.

## Decision axes

| Axis | Evidence/choices | Engineering consequence |
|---|---|---|
| workload shape | analytical scans/aggregations vs row-oriented transactions | analytical engine vs transactional OLTP characteristics |
| writer topology | one process, several threads, several processes, several machines | file DB vs coordinated service/client-server |
| write concurrency | rare/serialized vs frequent simultaneous writes | conflict/locking/concurrency requirements |
| storage location | local disk, network share, cloud block disk, object/lake storage | file-locking/durability/performance semantics |
| data value | disposable/cache vs valuable source-of-record | backup/recovery requirements |
| data sensitivity | none/internal/private/regulatory | encryption/access/audit requirements |
| data size | tiny to very large | memory/storage/query design |
| query shape | point lookup/CRUD vs large joins/aggregations | indexes/layout/engine fit |
| availability | can stop vs must remain available | maintenance/HA/migration strategy |
| migration | greenfield vs populated live schema | migration tooling/locks/rollback |
| offline requirement | must run locally/offline vs server reachable | embedded/local advantages |
| existing infrastructure | organization already provides DB/service | reuse may beat introducing another engine |

## Candidate choices

### DuckDB
Strong candidate when:
- analytical/OLAP or file-oriented workload;
- embedded/local execution is valuable;
- writes are compatible with its concurrency model;
- native DB is on appropriate storage, or current DuckLake/remote architecture is explicitly justified.

Avoid as a naive default when:
- many independent machines/processes directly write the same native DB;
- native read-write DB would live on SMB/NFS/NAS;
- workload is primarily many small concurrent transactional writes.

### SQLite
This project prefers DuckDB over SQLite **when both genuinely fit**, but SQLite research is useful as an independent control:
- strong local embedded transactional option in many low-concurrency scenarios;
- still not a safe “shared file DB for many network clients” default;
- one writer at a time per DB file.

Koda should not choose SQLite merely because it is common.

### PostgreSQL / client-server RDBMS
Strong candidate when:
- multiple clients/processes need transactional writes;
- centralized service/database operation is available;
- consistency/concurrency are material;
- project already uses PostgreSQL or organization provides it.

Do not deploy PostgreSQL for a tiny local analytical script merely to look professional.

### Central application with embedded DB
Potentially appropriate when:
- many clients need access but **one server process** can own the embedded DB;
- server serializes/coordinates DB access;
- deployment environment can reliably host that process.

This is materially different from all clients opening the same DB file over a share.

## Shared-folder example

User says:
> “The database/data is in a shared network folder.”

Koda must NOT jump to DuckDB.

It should determine:
- Is the folder only source/input data?
- Is the DB itself meant to be there?
- Is it read-only or read-write?
- How many machines/processes write?
- Can one application/server own all writes?

A valid simple architecture might be:
- app/server on one machine + local DB + shared source files;
- central PostgreSQL if available;
- read-only DuckDB analytics over shared files;
- another existing organization-approved store.

The answer depends on the actual topology.
