# Database Connection Pool Exhausted

## Symptoms
Requests hang then fail with errors like `connection to database "orders" failed: Read
timed out`, `too many connections`, or `QueuePool limit of size N overflow reached`.
Latency spikes and the app throws 500s while the database CPU may look fine.

## Likely causes
The app's connection pool is too small for the traffic, connections are leaked (not
returned to the pool), a slow query holds connections open too long, or the database's
own `max_connections` is set below what all app replicas together request.

## Fix steps
1. Check current connections on Postgres:
   `SELECT count(*) FROM pg_stat_activity;` and compare against `SHOW max_connections;`.
2. Look for long-running or idle-in-transaction sessions in `pg_stat_activity` and
   terminate a stuck one with `SELECT pg_terminate_backend(<pid>);` if needed.
3. Fix the slow query behind the held connections (add an index / reduce the work).
4. Right-size the pool: total app pool size across all replicas must stay under the
   database `max_connections` (leave headroom for admin connections).
5. Consider a pooler like PgBouncer in front of Postgres for many short-lived clients.

## Verify
`pg_stat_activity` count sits well under `max_connections`, latency returns to baseline,
and the `Read timed out` / `too many connections` errors stop.
