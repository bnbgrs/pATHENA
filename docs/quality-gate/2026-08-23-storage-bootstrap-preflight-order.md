# Quality Gate Incident — Storage bootstrap mutates runtime state before database preflight

Date: 2026-08-23

## Status

- Priority: P1 startup-safety / integration ordering
- Ownership: BACKEND
- Quality status: BLOCKED on Backend owner
- Product mutation by Quality: none
- Execution status: static contract violation confirmed; targeted runtime regression not yet present

## Observed HEAD

Revalidated on `agent/pathena` at HEAD `825e8fc6f092e1f4d7bce4a0840fa42f293783e9`.

Affected component:

- `src/athena/storage/bootstrap.py`
- `StorageBootstrapService.start()`
- BE-033 / FG-013 / FG-015 startup integration

## Primary defect

The Backend coordination contract states that safe storage bootstrap ordering is:

`read-only preflight/planning -> RuntimeLayout -> EmergencyReserve -> clone migration when needed -> DatabaseService`

The current implementation performs:

```python
self.layout.start()
self._ensure_migration_root()

preflight = inspect_database_read_only(self.paths.database_path)
plan = plan_database_migration(preflight)
```

`RuntimeLayoutService.start()` is not read-only. It creates required directories and creates/fsyncs/deletes write probes. `_ensure_migration_root()` can also create the migration directory durably. Therefore a corrupt, foreign, unsupported, or otherwise recovery-required active database is not inspected until after filesystem mutation has already occurred.

This weakens the intended fail-before-mutation startup boundary and directly contradicts the ordering documented in `docs/agent_coordination/backend_queue.md` for BE-033.

## Why this matters

The purpose of the read-only preflight is to classify the existing active database before normal startup mutates local state. Creating runtime directories and write probes first means a failed preflight no longer guarantees that startup made no filesystem changes.

The current storage-bootstrap tests verify reserve-before-database ordering and emergency/recovery blocking, but they do not assert that database preflight happens before RuntimeLayout mutation or that a preflight failure leaves previously absent runtime directories untouched.

## Recommended Backend fix

Establish a genuinely read-only first phase before `RuntimeLayoutService.start()` whenever the active database path can be inspected without creating directories:

1. run `inspect_database_read_only(database_path)` first;
2. derive `plan_database_migration(preflight)` before runtime layout mutation;
3. only then create/validate RuntimeLayout and migration root;
4. perform recovery assessment once the migration root can be safely addressed, without weakening the no-write-before-preflight invariant;
5. add a regression proving that a preflight-rejected existing database does not create runtime directories, migration directories, or write-probe artifacts.

If missing-parent semantics require a small read-only path classification before preflight, encode that explicitly rather than calling the mutating layout service first.

## Required verification

- targeted `tests/unit/test_storage_bootstrap.py` with explicit call-order/no-mutation assertions;
- storage preflight tests;
- Ruff/mypy for bootstrap/storage tests;
- full keep-going Linux gate;
- local install smoke after integration.
