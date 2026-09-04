# Independent FG-018 Backup Quiet-Hour Handoff

## Baseline and ownership

- Original exact baseline: `develop/pathena-next@0b7f428f8679db9391c00b4b9638d85550332c43`.
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

## Collision and synchronization evidence

This branch was intentionally disjoint from the active worker scopes observed when it was created:

- Core worker: Research/source-coverage/ResearchResult composition;
- Backend worker: ExternalAccessGateway and local-model HTTP response-size boundaries;
- UI worker: Settings runtime/accessibility freshness;
- Error worker: current-lineage failure scanning.

While this slice was being prepared, Develop advanced from `0b7f428f8679db9391c00b4b9638d85550332c43` to `2520224ebe3143368b3e5f13c091479d5e7b8d35`. The intervening Develop delta touched only Research composition/tests and shared progress/integrator documentation; it did not touch `src/athena/jobs/backup.py` or this focused test path.

The independent branch was then synchronized without force-push using merge commit `173bc6b462377a3fdab3d6cd489fa054768f7e47`, with the independent handoff lineage and exact Develop `2520224ebe3143368b3e5f13c091479d5e7b8d35` as parents. PR #66 became mergeable after that synchronization.

Integrator should review/cherry-pick only the bounded product/test state after executable Quality evidence is green. Do not merge this branch automatically and do not infer broader Beta 21 completion from this slice.

## Validation state

- Draft validation PR: `#66` — `Backend: make daily backup quiet hour configurable`.
- Exact synchronized validation head before this documentation refresh: `173bc6b462377a3fdab3d6cd489fa054768f7e47`.
- ATHENA Quality Gate run `33898237340` was `pending` when this documentation refresh was written; no PASS is claimed from it.
- This documentation commit advances the PR head again without changing product/test blobs, so Integrator must consume the canonical Quality result for the final exact PR head (or a verified descendant containing these blobs unchanged).
- Pending, cancelled, action-required, in-progress, or failed runs are not PASS evidence.
