# Independent FG-018 Backup Quiet-Hour Handoff

## Baseline and ownership

- Exact baseline: `develop/pathena-next@0b7f428f8679db9391c00b4b9638d85550332c43`.
- Independent branch: `independent/fg018-backup-quiet-hour-20260904`.
- Scope: Beta 21 / historical `FG-018` only — make the existing daily backup quiet hour bootstrap-configurable.
- `main`, `develop/pathena-next`, `postmerge/backend`, `postmerge/spec-core`, `postmerge/ui`, and `postmerge/errors` were not mutated.
- Deliberately untouched integration hotspot: `src/athena/core/application.py`.

## Product change

Product commit: `05ae3b357fc2bd3d4285a1a4789a47ec0527fbe7`.

`src/athena/jobs/backup.py` now supports bootstrap configuration through:

`ATHENA_BACKUP_QUIET_HOUR_UTC`

Contract:

- unset environment preserves the prior `03:00 UTC` default;
- accepted configured values are decimal hours `0..23`;
- malformed, signed, whitespace-padded, non-decimal, or out-of-range values fail closed during worker construction;
- an explicit `quiet_hour_utc=` constructor value overrides the environment and retains the existing exact-int/bool-rejecting validation;
- the resolved hour is still pinned into each scheduled backup job configuration;
- UTC semantics remain unchanged; this slice does not invent local-time or DST behavior.

No backup creation, catch-up, overlap prevention, target locking, idempotency, lease, retry, retention, restore, verification, storage, network, security, or UI semantics were changed.

## Focused regressions

Test file: `tests/unit/test_backup_quiet_hour_configuration.py`.

Final test-file commit in this handoff lineage: `a273ab241449e9d1a3ce47296a1510d51fe1cba1`.

Coverage locks:

- legacy default remains 03 UTC when configuration is absent;
- environment configuration is consumed when the constructor omits the hour;
- explicit constructor configuration wins over environment configuration;
- invalid environment values fail closed;
- explicit boolean values remain rejected.

## Collision guidance

This branch is intentionally disjoint from the active worker scopes observed when it was created:

- Core worker: Research/source-coverage/ResearchResult composition;
- Backend worker: ExternalAccessGateway and local-model HTTP response-size boundaries;
- UI worker: Settings runtime/accessibility freshness;
- Error worker: current-lineage failure scanning.

Integrator should review/cherry-pick only the bounded product/test state after executable Quality evidence is green. Do not merge this branch automatically and do not infer broader Beta 21 completion from this slice.

## Validation state

At handoff-document creation, no canonical Quality PASS is claimed for this branch. A draft validation PR should target `develop/pathena-next`; pending, cancelled, action-required, or failed runs are not PASS evidence.
