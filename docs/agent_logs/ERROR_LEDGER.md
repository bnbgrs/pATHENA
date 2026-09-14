# pATHENA Error Ledger

Evidence-first ledger for current exact-SHA failures. Historical IDs, old runs and old priorities are non-authoritative unless reproduced on the current exact SHA.

## Current source of truth

- `develop/pathena-next@e818ade900545e788c72cbd24bb6761880470148`; canonical Quality `34794066456 = IN_PROGRESS`. Specification validator, Ruff, mypy, Linux Storage, Windows release guards and Local Install/pypdf are green; full pytest is still running.
- `postmerge/errors@e8247f46fd2bc685fae10d5bfbd2efceb5a19904`; exact canonical Quality `34788816387 = FAILURE` on attempt 3. Specification validator, Ruff, mypy, Linux Storage, Windows release guards and Local Install/pypdf pass. Full pytest is `1 failed, 5067 passed, 17 skipped`; the sole failure is inherited 48px Send-button geometry versus the authoritative 44px test contract. `tests/qa/test_visual_capture_manifest_truth.py` passes on the same exact SHA.
- `postmerge/spec-core@52b4e322041547e9039a0f3026f6747583605914`; Core Focused `34789228532 = SUCCESS` and canonical Quality `34789228473 = SUCCESS`.
- `postmerge/backend@e4e1244e8482ac7d78e557ded5f91252cccc0347`; no new matching current failure evidence; retain last exact canonical-green qualification and do not reopen absent a new current signature.
- `postmerge/ui@9c03ce6bb2c4cb9913cf0dafcaa2336fdb6dd82c`; exact 11-Surface Visual `34794418240 = FAILURE`. Harness Ruff, comparator mypy/tests, hierarchy/accessibility contracts, all eleven native captures, route identity, compare/proposal and artifact upload pass; only final visual verdict fails.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## OPEN

### ERR-0054 — P2 — Windows visual baseline review incomplete

Status: `OPEN`

Owner: UI/Visual Review. Error worker is evidence-only for this cluster.

Exact current reproduction: `postmerge/ui@9c03ce6bb2c4cb9913cf0dafcaa2336fdb6dd82c`, 11-Surface Visual `34794418240 = FAILURE`. The run proves all eleven native surfaces can be captured and route identity is stable; failure occurs only at `Enforce visual verdict` after compare/proposal and artifact upload succeed.

Current UI handoff remains fail-closed and does not establish eleven reviewed authoritative reference/render pairs. No baseline may be created or accepted by the Error worker.

Required closure: UI/Visual Review must open and review all eleven authoritative reference/render pairs for the exact candidate, approve only a reviewed baseline, and then produce an exact-SHA 11-Surface Visual final verdict success. Never relax comparator tolerances, route identity, capture truth, manifest truth or verdict enforcement.

## FIXED

### ERR-0062 — P2 — Core Merge/Split negative-runtime tests violated focused mypy contract

Status: `FIXED`

Spec/Core successor `52b4e322041547e9039a0f3026f6747583605914` moves the narrow `arg-type` accommodations onto the intentionally invalid argument expressions without changing negative-runtime assertions or planner semantics. Exact Core Focused `34789228532 = SUCCESS` and exact canonical Quality `34789228473 = SUCCESS`. The prior test-typing signature is not current and must not be reopened absent a new exact-SHA reproduction.

### ERR-0060 — P2 — Spec/Core merge-split planner mypy tuple inference

Status: `FIXED`

Retained closed. The current Spec/Core successor is focused- and canonical-green.

### ERR-0061 — P2 — Core Focused omitted mypy and could report false-green candidates

Status: `FIXED`

Retained closed. Current Core Focused qualification executes and enforces mypy.

### ERR-0059 — P2 — visual manifest falsely reported full capture after partial failure

Status: `FIXED`

Retained closed. Exact Error-worker canonical attempt 3 executes `tests/qa/test_visual_capture_manifest_truth.py` successfully. Do not revisit unless a new exact-SHA manifest-truth regression reproduces.

Also fixed and retained: `ERR-0058`, `ERR-0053`, `ERR-0055`, `ERR-0056`, `ERR-0057`, `ERR-0049`.

## STALE / DEDUPLICATED CASCADES

### Error-worker inherited 48px Send-button geometry

Status: `STALE`

Exact current Error-worker canonical `34788816387` attempt 3 reproduces only `tests/unit/test_pathena_window.py::test_reference_composer_uses_large_work_surface_and_send_target`: runtime Send-button width is 48 while the test correctly requires 44. The same run has `5067 passed`, and all release/storage/install lanes are green.

This does not reopen `ERR-0053`: the Error branch is materially behind the current integration target in UI history, while the authoritative product contract remains 44px. It is branch-divergence evidence, not a new Error-owned UI root cause. Do not weaken the 44px test and do not parallel-edit UI product code on `postmerge/errors`. A future history-preserving Error-branch synchronization may remove the stale divergence only after the chosen Develop exact SHA is terminal canonical-green.

## Persistent release guards

No current exact evidence reopens pypdf packaging, fail-closed Frozen argv, Desktop/Worker executable separation, single Desktop with bounded workers, adaptive 2048-context reserve, Windows lane-lock escalation, duplicate-column, Core-startup or storage-bootstrap failures. On current Develop candidate `e818ade...`, Windows release guards, Linux Storage and Local Install/pypdf are already green while canonical full pytest remains in progress.

## Next root cause

1. Consume terminal canonical result for `develop/pathena-next@e818ade900545e788c72cbd24bb6761880470148`; do not create a competing Develop run or mutate Develop.
2. `ERR-0054` remains UI/Visual-review-owned; do not create or accept a baseline in parallel.
3. Do not reopen `ERR-0062`, `ERR-0059`, `ERR-0060` or `ERR-0061` absent a new exact-SHA matching regression.
4. The Error-worker 48px failure is `STALE` branch divergence. Do not weaken the 44px guard or patch UI product code here.
5. Scan for a new current Error-/Harness-owned failure only after excluding ownership-held and canonical-green clusters.