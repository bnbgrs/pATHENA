# pATHENA Error Ledger

Evidence-first ledger for current exact-SHA failures. Historical IDs/runs are non-authoritative unless reproduced on a current exact SHA.

## Current source of truth
- `develop/pathena-next@a5ab9f4ecdd35b899dba9676a8c5574621e64604`; canonical Quality `35358305891 = SUCCESS` on this exact SHA.
- `postmerge/errors@271c0178a63b6225090a8709ba8b0a57cd35383f` before this refresh.
- `postmerge/spec-core@6dddda87919cc5363ccf664863f6b4dca83784ed`; no new current-SHA failure evidence.
- `postmerge/backend@72a3437dc756a42f85e049ecd575706c1a6ca9d1`; Backend Focused `35362708468 = SUCCESS`; canonical Quality `35362708452 = FAILURE`.
- `postmerge/ui@e149515870b773548a164658775159f29de323af`; Develop contains the independently integrated 11-screen regression-baseline bundle, but native review remains `MATCH=0/11`.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## OPEN
### ERR-0054 — P2 — Windows visual baseline review incomplete
Status: `OPEN`
Owner: UI / Visual Review.
Develop `a5ab9f4e...` is canonical Quality green, but its merge evidence explicitly states native review remains `MATCH=0/11`. This is not screenshot-parity closure. Error worker must not create or accept a baseline. UI/Visual Review must truthfully review the eleven original-reference + exact-render pairs.

### ERR-0074 — P1 — Backend canonical Ruff failure
Status: `OPEN`
Owner: Backend.
Exact reproduction: `postmerge/backend@72a3437dc756a42f85e049ecd575706c1a6ca9d1`, canonical Quality `35362708452`, Python 3.12 quality. Canonical diagnostics contain exactly one Ruff failure: fixable `I001` at `tests/unit/test_backup_verify_durable_service.py:1:1`, `Organize imports`, `1 fixable with --fix`. The current file places `pytest` in a separate block before `athena.*`; canonical Ruff still rejects it. Repeated hand-authored import permutations are non-closure evidence. Backend owns this file; Error worker must not mutate it in parallel. Required action remains actual repository-pinned Ruff 0.15.22 `check --fix tests/unit/test_backup_verify_durable_service.py`, complete generated diff, focused Ruff PASS, then exact canonical verify.

### ERR-0075 — P1 — Backend durable-service contract test regression
Status: `OPEN`
Owner: Backend.
Reproduced anew on exact `postmerge/backend@72a3437dc756a42f85e049ecd575706c1a6ca9d1`, canonical Quality `35362708452`: full pytest reports `3 failed, 5328 passed, 17 skipped`. All three failures are in `tests/unit/test_backup_verify_durable_service.py` and fail before exercising the intended contract because `BackupDeepVerifyDurableJobService(repository=repository)` omits required constructor argument `chat`, raising `TypeError: DurableJobService.__init__() missing 1 required positional argument: 'chat'` in each test. The same commit titled `Backend: apply Ruff canonical import grouping` changed 68 lines in this test file (23 additions, 45 deletions), including functional test/API shape, not merely import grouping. Production `BackupDeepVerifyDurableJobService` still inherits the canonical `DurableJobService` constructor and its `create()` contract requires `job_type`, `priority`, `requested_scope`, `pinned_configuration`, and optional `next_run_at_us`; the rewritten tests instead call a different `job_id/payload/metadata` API shape. Do not change production to satisfy this accidental test rewrite. Backend must restore the test to the actual durable-service contract, preserve fail-closed validation, and focused-verify this file before another canonical candidate.

## FIXED / HELD CLOSED
### ERR-0059 — P2 — manifest capture truth
Status: `FIXED`
No new exact-SHA manifest-truth regression is reproduced. Develop `a5ab9f4e...` canonical Quality is SUCCESS. Preserve capture-derived manifest fields, `assigned_reference_count = 11`, and fail-closed exact-eleven PASS semantics. Do not reopen absent a new exact-SHA failure signature.

Historical closed errors remain closed absent new exact reproduction.

## Persistent release guards
On exact Backend `72a3437dc756a42f85e049ecd575706c1a6ca9d1`, Windows path safety, Linux storage regressions, and Local-install smoke are SUCCESS. Windows storage/durable-filesystem/API-boundary/Core-API-ownership/packaged-runtime/adaptive-chat/restart/pypdf guards are SUCCESS. Keep pypdf packaging, fail-closed Frozen argv, Desktop/Worker executable separation, single Desktop with bounded workers, adaptive 2048-context reserve, Windows lane-lock escalation, duplicate-column, Core-startup and storage-bootstrap protections unchanged.

## Next root cause
1. `ERR-0075`: Backend must revert the accidental functional rewrite of `tests/unit/test_backup_verify_durable_service.py` to the real constructor/create contract and focused-verify the durable-service tests. Production API must not be distorted to satisfy the bad test rewrite.
2. In the same bounded file, close `ERR-0074` only by executing pinned Ruff 0.15.22 `check --fix`, consuming the exact generated import transformation, and proving focused Ruff PASS.
3. Require focused pytest + focused Ruff PASS on the same Backend SHA before another canonical candidate.
4. `ERR-0059` remains FIXED; do not touch without new exact reproduction.
5. `ERR-0054` remains UI/Visual-Review-owned and OPEN because native review is still `MATCH=0/11`; Error worker only verifies evidence/closure status.
