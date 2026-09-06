# pATHENA Feature Integrator Handoff

## Current branch state

- `main` remains strict read-only at `0d4d621f8a38ddf8eccfa09622bf193687619943`.
- Develop before this run: `ff780f2edf367320340771ffc3176d9fc1724c5c`.
- Integration target: `develop/pathena-next` only.
- Worker heads reviewed: errors `0017b4d83481ba46e020d12492eb5c1d0a5fca7a`; spec-core `daf618982b068557919b58a3e0e6935c9cf41afe`; backend `7b37f0629d3a137301ef04284524a8dfd78c36d3`; ui `f09406daab9440ee77a06e907add84280b3ae936`.
- `main` and `bnbgrs/ATHENA` were untouched.

## Integrated this run — Disk-pressure canonical reserve-release size truth

READY Backend lineage independently reviewed:

- product `ef7dbde6e660d095272e14febcbbd1fc4cfa4370`;
- focused regression `415691b0cac741f461ed41bcecbbe08bd9011330`;
- exact green Backend descendant `02707d295e31e8d321ba6f2ed1bd6f50197eeb81`;
- canonical Quality `33999117392 = success`.

The worker descendant contains additional later Backend hardening, so it was not transplanted wholesale. The bounded reviewed product patch was applied semantically to exact current Develop `src/athena/storage/disk_pressure.py`, adding only the canonical reserve-size upper bound after the existing volume/threshold guards. The focused regression was added to `tests/unit/test_disk_pressure_result_boundaries.py`. This preserves already-integrated UI/Core/Error state and excludes newer unrelated Backend changes.

Integration commits: product `c6cdc28f2236f9124535da1f76af9e639827ce85`; focused test `86364de2041b6a170e32d952ed005faa6e156da7`.

## Contract now covered

`DiskPressureCheckResult.released_reserve_bytes` fails closed when telemetry exceeds `emergency_reserve_size_bytes(before_release.total_bytes)`, even if the value remains below total volume size. Existing threshold consistency, EMERGENCY-only positive release, zero-release identity, reserve provisioning, read-only safe mode, noncritical-write gating, SQLite/WAL, recovery, fsync, transport, security, audit and provenance behavior are unchanged.

## Validation state

- Exact worker canonical Quality `33999117392` is green on the verified Backend lineage.
- Focused worker regression explicitly covers a 2 GiB claimed release on a 100 GiB volume whose canonical reserve is 1 GiB.
- Exact-current-Develop repository-wide green is not claimed: this connector run cannot execute local pytest/Quality and no workflow run is yet associated with integration commit `86364de2041b6a170e32d952ed005faa6e156da7`.
- `ALPHA_BETA_PROGRESS.md` was read; connector retrieval is truncated, so no whole-file rewrite was attempted and no tracker state was fabricated or truncated.

## Other current inputs

- Core head `daf618982b068557919b58a3e0e6935c9cf41afe` has memory-scope-priority work pending canonical Quality and is not READY for this run.
- Backend local-provider HTTP error-body total-deadline hardening product `eaa0c891d794529708917461b600ebe4584ae2a2` plus focused test `18710d1441206c8282f7c7dacae15f8116365c17` remains canonical-pending and was not integrated.
- UI head `f09406daab9440ee77a06e907add84280b3ae936` continues visual/focus work; no UI slice was selected under the single-bounded-slice rule.
- Error worker head `0017b4d83481ba46e020d12492eb5c1d0a5fca7a` still has no current exact-SHA blocker; historical `ERR-0014` remains stale unless reproduced exactly.
- Eleven UI screens remain implemented pending visual review; pixel-level `MATCH` remains unclaimed.

## Runtime/release guards retained

Known Windows pypdf packaging, fail-closed frozen argv routing, bounded process-tree, adaptive 2048-context DirectChat budgeting, lane-lock/scheduler packaged-worker crash cluster and storage-startup signatures remain explicit Beta/release regression requirements. This Storage slice does not alter their owning code or reopen them without exact-SHA reproduction.

## Next integration order

1. Prefer any newer exact-green bounded Core composition successor.
2. Otherwise independently review the next READY Backend/UI slice against exact current Develop; do not absorb canonical-pending local-provider deadline hardening.
3. Obtain exact-current-Develop Quality before any repository-wide green or promotion-ready claim.
4. Before Beta/release readiness, explicitly regress known Windows packaging/process-tree/startup/chat-context/lane-lock crash classes.

## Rules retained

- No direct work on `main`; no main promotion.
- No force-push, history rewrite or auto-merge.
- No Skip/XFail, weaker assertions, Security/Storage/Windows/Recovery/validator relaxation, fake success or fabricated provenance.
