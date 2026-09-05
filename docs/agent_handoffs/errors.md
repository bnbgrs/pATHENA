# pATHENA Error Handoff

## Baseline

- Baseline source: `develop/pathena-next`
- Baseline SHA observed this run: `7710c7aaa82b4fe4725238cbe8f84d5be9ed3017`
- Worker branch: `postmerge/errors`
- Error branch pre-run head: `6ccac5e5add098e4981f7d95d5fc912ca776259f`.
- Error branch remains history-diverged from current Develop; no force ref update, rebase or history rewrite was attempted.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## Current error state

- OPEN: none.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: `ERR-0012`.
- FIXED: `ERR-0001` through `ERR-0011`.
- BLOCKED: none.

## Fresh evidence

- Backend `2d5b22801d5889c374ae1a75bd9880e3070e21c4` completed canonical Quality `33960721888 = success`.
- UI `9f24999c62b309e25ac512a110ef18011225a4cc` completed canonical Quality `33961422115 = failure`.
- Exact failing canonical node: `tests/unit/test_storage_health.py::test_storage_health_snapshot_requires_path_for_unavailable_state` -> `Failed: DID NOT RAISE ValueError`; full pytest `1 failed, 4650 passed, 3 skipped, 2 warnings`.
- All other exposed jobs in the failed UI run were green: Windows path safety, Linux storage, local install smoke, specification validator, Ruff and mypy.
- Root cause is cross-owner synchronization drift: relative to Develop merge parent `c887b2beb4b0f919fdd4f86d3db245c16c2094f4`, failing UI tree `9f24999c...` deleted exactly the two-line unavailable `database_path is None` guard from `src/athena/storage/health.py` while retaining the test that requires the invariant.
- Current UI head `cef280487dd12b6fe88d4a3f021ec9b1b2aea0d5` again contains the missing-path rejection. Canonical Quality `33964058090` is still `in_progress`; this is correction evidence but not PASS evidence.
- Current Develop `7710c7aaa82b4fe4725238cbe8f84d5be9ed3017` preserves the missing-path guard and later StorageHealth NUL-detail hardening.

## Collision avoidance

- Do not mutate UI or Storage product code from Error while UI already carries the correction and exact canonical verification is running.
- Do not weaken `test_storage_health_snapshot_requires_path_for_unavailable_state`; it correctly detected product-tree drift.
- Preserve direct total-deadline, cumulative byte-budget, delegated body-handle/file-descriptor restrictions, loopback-only/proxy-free transport, Security, Storage and Recovery guards.
- No skip/XFail, assertion weakening, dummy success, force-push, history rewrite or merge to main.

## Integrator handoff

- `ERR-0001` through `ERR-0011` remain error-cleared on recorded exact evidence.
- New `ERR-0012` is `FIXED_PENDING_VERIFY`.
- Reject UI `9f24999c62b309e25ac512a110ef18011225a4cc` / Quality `33961422115` as READY: it is exact canonical red due to the StorageHealth unavailable-path regression.
- Current UI `cef280487dd12b6fe88d4a3f021ec9b1b2aea0d5` contains the correction, but do not mark READY or `ERR-0012` FIXED until exact Quality `33964058090` completes successfully.
- Current Develop still requires exact-head canonical Quality before any repository-wide global-green claim.

## Next scan

1. Consume UI `33964058090` on exact head `cef280487dd12b6fe88d4a3f021ec9b1b2aea0d5` when complete.
2. If successful, verify the unavailable-path guard remains byte/semantically present and close `ERR-0012` as `FIXED`; if red, extract the new exact primary diagnostic and deduplicate before allocating another ID.
3. Continue Packaging, Provider/Transport, Research/Jobs, Persistence/Recovery, Qt/Desktop, Security, Windows path safety, Linux storage and local install/start scanning for real current-lineage failures.
