# pATHENA Error Ledger

Evidence-first ledger for current exact-SHA failures. Historical IDs/runs are non-authoritative unless reproduced on a current exact SHA.

## Current source of truth
- `develop/pathena-next@03157f15246c8acb0f51a30631bf45c4d2a72416`.
- `postmerge/errors@32cbc4dcb5e037bd4638e42edfefcf951db614a0` before this refresh.
- `postmerge/spec-core@6dddda87919cc5363ccf664863f6b4dca83784ed`; no new current-SHA failure evidence.
- `postmerge/backend@ab3736bbdc73de3b07eb7062fa819273ee676bc2`; Backend Focused `35233727773 = SUCCESS`; canonical Quality `35233727718 = FAILURE`.
- `postmerge/ui@e149515870b773548a164658775159f29de323af`; no Error-worker closure evidence.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## OPEN
### ERR-0054 — P2 — Windows visual baseline review incomplete
Status: `OPEN`
Owner: UI / Visual Review.
No Error-worker closure evidence. UI handoff still states `PAIRS_VERIFIED_0_OF_11` / visual readiness NO for its current evidence lineage. Error worker must not create or accept a baseline. Closure requires truthful review of all eleven original-reference + exact-render pairs.

### ERR-0074 — P1 — Backend canonical Ruff failure
Status: `OPEN`
Owner: Backend.
Exact reproduction: `postmerge/backend@ab3736bbdc73de3b07eb7062fa819273ee676bc2`, canonical Quality `35233727718`, Python 3.12 quality. Specification validator, mypy and full pytest are SUCCESS; Ruff alone fails with exactly one `I001 [*] Import block is un-sorted or un-formatted` at `tests/unit/test_backup_verify_durable_service.py:1:1`. Exact diagnostics artifact `canonical-quality-diagnostics-ab3736bbdc73de3b07eb7062fa819273ee676bc2` confirms the entire lines 1-15 import block is fixable with `--fix`. Current source has `pytest` in a blank-separated section before the wrapped `athena.*` imports. Do not reopen runtime code or manually permute imports further: run the pinned Ruff 0.15.22 fixer on this exact file and consume its complete diff, then focused Ruff before another canonical candidate.

## FIXED / HELD CLOSED
### ERR-0075 — P1 — Backend durable-service contract regression
Status: `FIXED`
On exact Backend `ab3736bbdc73de3b07eb7062fa819273ee676bc2`, Backend Focused is SUCCESS and canonical full pytest is SUCCESS (`5331 passed, 17 skipped`); `tests/unit/test_backup_verify_durable_service.py` contributes three passing tests. The prior `actor_id/payload/version` contract drift is no longer reproduced. Keep closed absent a new exact-SHA reproduction.

### ERR-0059 — P2 — manifest capture truth
Status: `FIXED`
On exact Backend `ab3736bbdc73de3b07eb7062fa819273ee676bc2`, `tests/qa/test_visual_capture_manifest_truth.py` passes in canonical pytest. Preserve capture-derived manifest fields, `assigned_reference_count = 11`, and fail-closed exact-eleven PASS semantics.

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
On exact Backend `ab3736bbdc73de3b07eb7062fa819273ee676bc2`, Linux storage regressions, Local-install smoke, and Windows path/storage/durable-filesystem/API-boundary/ownership/packaged-runtime/adaptive-chat/restart/pypdf guards are SUCCESS. Keep pypdf packaging, fail-closed Frozen argv, Desktop/Worker executable separation, single Desktop with bounded workers, adaptive 2048-context reserve, Windows lane-lock escalation, duplicate-column, Core-startup and storage-bootstrap protections unchanged.

## Next root cause
1. ERR-0074 is the only current Backend Python-quality failure cluster on exact `ab3736bb...`.
2. Backend must execute the pinned Ruff 0.15.22 `check --fix` on `tests/unit/test_backup_verify_durable_service.py` and consume the complete generated import-block transformation rather than another manual partial permutation.
3. Focused Ruff and focused durable-service pytest must both pass before a new canonical candidate.
4. Close ERR-0074 only on terminal exact-SHA canonical Ruff success.
5. Keep ERR-0075, ERR-0059 and all current release guards closed; ERR-0054 remains UI/Visual-Review-owned.
