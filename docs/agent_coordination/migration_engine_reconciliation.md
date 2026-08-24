# Migration Engine Reconciliation — FG-013

Verified against `agent/pathena` on 2026-08-23.

## Specification contract

Beta 03 section 3 selects SQLAlchemy 2.x + Alembic plus ATHENA-specific safety logic. Sections 194–209 additionally require versioned Alembic revisions, reviewed migration metadata, SQLite batch migration support, a pre-migration clone, clone-first migration execution, free-space preflight, rollback snapshot retention, reversibility metadata, an exclusive migration lock, and an external migration journal.

## Current implementation

The current runtime uses stdlib `sqlite3`. `SQLiteDatabase.start()` performs the normal read-only preflight and then opens the live database directly before calling `initialize_schema()`.

`initialize_schema()` advances every supported historical `PRAGMA user_version` through an ordered chain of `_migrate_schema_vN_to_vN+1()` functions and verifies the final schema. This gives ATHENA a deterministic internal version chain and substantial schema verification, but the inspected startup path applies upgrades to the live database connection.

The current repository has no `migrations/versions/` Alembic revision tree and `pyproject.toml` contains neither SQLAlchemy nor Alembic. The inspected storage package also has no dedicated clone-migration coordinator, migration free-space preflight, rollback-snapshot retention controller, migration lock/journal implementation, or activation-time file swap matching Beta 03 sections 197–209.

## Reconciliation conclusion

FG-013 is a real architecture/specification divergence, not a cosmetic dependency mismatch. The custom migration chain cannot presently be declared equivalent to the Beta 03 migration contract because several independent safety invariants are absent from the normal startup migration path.

Do not bolt Alembic onto `initialize_schema()` while leaving live in-place startup migration unchanged. The safe next implementation sequence is:

1. Introduce a migration coordinator around the database service that decides whether migration is required before opening the live database for mutation.
2. Implement migration metadata independent of a specific migration library: migration ID, from/to versions, reversibility, clone requirement, estimated space factor, rebuild requirement.
3. Add free-space preflight and an exclusive migration lock.
4. Create the pre-migration clone with SQLite Online Backup API and persist an external migration journal.
5. Run schema migration against the clone, then foreign-key/integrity/schema verification.
6. Durably flush and atomically activate the verified clone while retaining the previous database as rollback candidate.
7. Only after that boundary exists, decide whether Alembic becomes the revision executor or whether the Beta specification is formally amended to retain ATHENA's custom revision executor.

## Ownership decision still required

The backend can implement the safety coordinator independently of Alembic. Choosing between Alembic and the existing custom revision executor changes the normative architecture and packaging contract; that choice should not be silently made by a maintenance bot.

Until that decision is explicit, FG-013 should be BLOCKED at the technology-selection layer while implementation-ready sub-slices for clone migration safety may proceed independently.
