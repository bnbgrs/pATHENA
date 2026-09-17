# pATHENA Error Ledger

Evidence-first ledger for current exact-SHA failures. Historical IDs/runs are non-authoritative unless reproduced on a current exact SHA.

## Current source of truth
- `develop/pathena-next@03157f15246c8acb0f51a30631bf45c4d2a72416`.
- `postmerge/errors@2f56bd541174c8f4d8956c9918ced683b07da6fa` before this refresh.
- `postmerge/spec-core@6dddda87919cc5363ccf664863f6b4dca83784ed`; no new current-SHA failure evidence.
- `postmerge/backend@8f23bf80d09cc0add2bb20f92af9525aaa42689f`; Backend Focused `35221156644 = SUCCESS`; canonical Quality `35221156651 = FAILURE`.
- `postmerge/ui@e149515870b773548a164658775159f29de323af`; no current Error-worker closure evidence.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## OPEN
### ERR-0054 — P2 — Windows visual baseline review incomplete
Status: `OPEN`
Owner: UI / Visual Review.
No Error-worker closure evidence. Error worker must not create or accept a baseline. Closure requires truthful review of all eleven original-reference + exact-render pairs.

### ERR-0074 — P1 — Backend canonical Ruff failure
Status: `OPEN`
Owner: Backend.
Exact reproduction: `postmerge/backend@8f23bf80d09cc0add2bb20f92af9525aaa42689f`, canonical Quality `35221156651`, Python 3.12 quality. Ruff reports exactly one `I001 [*] Import block is un-sorted or un-formatted` at `tests/unit/test_backup_verify_durable_service.py:1:1`; the current block has `pytest` in its own blank-separated section before wrapped `athena.*` imports. Do not reopen unrelated runtime code. Apply the complete pinned Ruff fixer output, not another manual partial permutation.

### ERR-0075 — P1 — Backend durable-service contract regression
Status: `OPEN`
Owner: Backend.
Reopened only because it is newly reproduced on exact `8f23bf80d09cc0add2bb20f92af9525aaa42689f`: canonical pytest has 3 failures, all in `tests/unit/test_backup_verify_durable_service.py`, with `TypeError: BackupDeepVerifyDurableJobService.create() got an unexpected keyword argument 'actor_id'`. The current production `create()` contract accepts `job_type`, `priority`, `requested_scope`, `pinned_configuration`, `next_run_at_us` and derives actor identity via `chat.ensure_local_user()`, while the test still calls the historical `actor_id/payload/version` API. This is a test/product-contract drift cluster, not three independent failures. Resolve against the current canonical service contract without weakening validation or persistence assertions; focused durable-service pytest must pass before canonical.

## FIXED / HELD CLOSED
### ERR-0059 — P2 — manifest capture truth
Status: `FIXED`
On exact Backend `8f23bf80...`, `tests/qa/test_visual_capture_manifest_truth.py` passes in canonical pytest before the unrelated durable-service failures. Preserve capture-derived manifest fields, `assigned_reference_count = 11`, and fail-closed exact-eleven PASS semantics.

- `ERR-0072` — `FIXED`; no current reproduction.
- `ERR-0073` — `FIXED`; no current reproduction.
- `ERR-0070` — `FIXED`.
- `ERR-0071` — `FIXED`.
- `ERR-0063` — `FIXED`.
- `ERR-0064` — `FIXED`.
- `ERR-0065` — `STALE`.
- `ERR-0066` — `FIXED`.
- `ERR-0062` — `FIXED`.
- `ERR-0060` — `FIXED`.
- `ERR-0061` — `FIXED`.
Historical closed errors remain closed absent new exact reproduction.

## Persistent release guards
On exact Backend `8f23bf80d09cc0add2bb20f92af9525aaa42689f`, Linux storage regressions, Local-install smoke, and Windows path/storage/durable-filesystem/API-boundary/ownership/packaged-runtime/adaptive-chat/restart/pypdf guards are SUCCESS. Keep pypdf packaging, fail-closed Frozen argv, Desktop/Worker executable separation, single Desktop with bounded workers, adaptive 2048-context reserve, Windows lane-lock escalation, duplicate-column, Core-startup and storage-bootstrap protections unchanged.

## Next root cause
1. ERR-0075 is newly current and higher-impact than treating Ruff alone: align `test_backup_verify_durable_service.py` with the actual current `BackupDeepVerifyDurableJobService.create()` contract while retaining fail-closed invalid snapshot/pipeline assertions and persistence truth.
2. In the same bounded file, consume the complete Ruff 0.15.22 fixer output for ERR-0074 rather than another manual import permutation.
3. Focused durable-service pytest and focused Ruff must both pass before a new canonical candidate.
4. Close ERR-0074/ERR-0075 only on terminal exact-SHA canonical success for their respective steps.
5. Keep ERR-0059 and all current release guards closed; ERR-0054 remains UI/Visual-Review-owned.
