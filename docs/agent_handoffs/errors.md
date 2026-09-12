# pATHENA Error Handoff

## Baseline

- Develop source of truth: `develop/pathena-next@d8236b74e69d1eedfdd2b05a52ed767520246671`.
- Error worker entered this run at `postmerge/errors@983a57ca2005ad231a8896fc24e77cfd48b971a7`.
- Current workers: Spec/Core `008345141aac276f9723b536a70497e2dec74b20`; Backend `e4aacf8004e08fddacb41cebe687453a759444cf`; UI `2e39818797e9c13ab20ac929f5377ae9888181df`.
- Develop canonical Quality `34692305368@d8236b74e69d1eedfdd2b05a52ed767520246671 = IN_PROGRESS` at observation time; latest completed Develop canonical is `34689663093@8d34591f08ab1f1a42dbb032963769968aefab2e = SUCCESS`.
- Backend exact `e4aacf8004e08fddacb41cebe687453a759444cf`: Backend Focused `34691379970 = SUCCESS`; canonical `34691380019 = FAILURE`, isolated to full pytest while all other canonical lanes pass.
- Spec/Core exact `008345141aac276f9723b536a70497e2dec74b20`: Core Focused `34688220222 = SUCCESS`; canonical `34688220225 = SUCCESS`.
- UI exact `2e39818797e9c13ab20ac929f5377ae9888181df`: current Integrator handoff treats this as a synchronization head with no bounded promoted product slice from that head.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- OPEN: `ERR-0040`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED includes `ERR-0033` and `ERR-0035`.
- STALE includes historical `ERR-0038` and `ERR-0039`.
- BLOCKED: none.

## Hard progress this run — ERR-0040 root cause identified from exact canonical diagnostics

### ERR-0040 — scheduled-materialization test fixture violates canonical SQLite journal-mode invariant

Status: `OPEN / P1`.

Current exact reproducer is `postmerge/backend@e4aacf8004e08fddacb41cebe687453a759444cf`.

Exact canonical Quality `34691380019` is `FAILURE`; Backend Focused `34691379970` is `SUCCESS`. Canonical Specification Validator, Ruff, mypy, Windows Path Safety, Linux Storage Regressions and Local Install all pass. Only full pytest fails.

The exact diagnostics artifact `canonical-quality-diagnostics-e4aacf8004e08fddacb41cebe687453a759444cf` was consumed. It reports `4955 passed, 17 skipped, 5 errors`; every error is a setup error in `tests/unit/test_scheduled_materialization.py`:

- `test_same_occurrence_materializes_once_across_retry`
- `test_distinct_occurrences_materialize_distinct_jobs`
- `test_materialization_requires_existing_write_transaction`
- `test_disabled_schedule_fails_closed_without_row`
- `test_existing_foreign_binding_fails_closed`

All five fail before scheduled-materialization behavior executes. The fixture creates `sqlite3.connect(":memory:", autocommit=True)` and invokes the canonical `athena.storage.schema.initialize_schema()`. During v37->v38 migration, physical cleanup intentionally accepts only journal modes `wal` or `delete`. SQLite `:memory:` reports journal mode `memory`, so initialization correctly fails closed with `DatabaseCompatibilityError: ATHENA physical cleanup encountered unsupported SQLite journal mode 'memory'`.

The current one-line Backend correction from `athena.storage.schema_evolution.initialize_schema` to `athena.storage.schema.initialize_schema` therefore exposed the actual incompatibility rather than closing it.

### Ownership and minimal repair

This is now a precisely diagnosed Backend harness root cause, not evidence that the Storage physical-cleanup guard is wrong. Backend owns `test_scheduled_materialization.py`; Errors must not parallel-edit that active slice.

Minimal owner fix: replace the in-memory fixture with a temporary file-backed SQLite database initialized through the canonical schema path so the existing `wal`/`delete` migration contract remains intact. Do **not** broaden production schema acceptance to journal mode `memory`, bypass physical cleanup, mock away the guard, delete tests, or use Skip/XFail.

Verification order required for closure:

1. reproduce the five setup errors on the exact Backend lineage;
2. apply the file-backed fixture repair;
3. run those five named tests first;
4. run the smallest scheduled-materialization regression set;
5. obtain exact Backend canonical Quality `SUCCESS`;
6. after integration, obtain relevant exact-Develop verification before `FIXED`.

### Other clusters

`ERR-0035 = FIXED / P1`; integrated closure remains `34680853488@8c885669ce3a3d718588d0327828341684c88c71 = SUCCESS`.

`ERR-0033 = FIXED / P1`; integrated closure remains `34666307002@ca87e42c8820c47db7d6626feb17698560cd3b49 = SUCCESS`.

`ERR-0038` and `ERR-0039` remain `STALE`; reopen only with current exact-SHA reproduction.

## CI discipline

- `postmerge/errors@983a57ca2005ad231a8896fc24e77cfd48b971a7` had zero workflow runs before the ledger mutation.
- After ledger commit `e4494eecfdc0d7af707932d7bdf822e46d34644d`, the Error branch again had zero workflow runs before this handoff mutation.
- No canonical Quality run was started by Errors.
- No mutation was made to Develop, Backend, Spec/Core, UI, `main`, or `bnbgrs/ATHENA`.

## Integrator handoff

- Develop: `d8236b74e69d1eedfdd2b05a52ed767520246671`; canonical `34692305368 = IN_PROGRESS`. Do not treat the current Develop SHA as qualified until that run completes.
- `ERR-0040 = OPEN / P1`: Backend exact `e4aacf8004e08fddacb41cebe687453a759444cf`; Backend Focused `34691379970 = SUCCESS`; canonical `34691380019 = FAILURE`.
- Exact root cause is now known: `test_scheduled_materialization.py` uses an in-memory SQLite fixture that cannot satisfy the canonical v37->v38 physical-cleanup journal-mode invariant. All five canonical errors are fixture setup failures with journal mode `memory`.
- Required Backend repair is a file-backed canonical-schema fixture, followed by the five named tests, scheduled-materialization regression set and exact canonical success. Storage migration guards must remain unchanged.
- Spec/Core: `008345141aac276f9723b536a70497e2dec74b20`; focused and canonical both `SUCCESS`.
- UI: `2e39818797e9c13ab20ac929f5377ae9888181df`; no Error-owned UI mutation or promotion claim.
- Preserve pypdf packaging, Frozen argv, two-EXE topology, bounded workers, adaptive 2048-context reserve, Windows lane-lock mapping, duplicate-column/Core-startup/storage-bootstrap guards and all Storage/Recovery/Security fail-closed invariants.
