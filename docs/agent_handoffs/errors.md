# Error worker handoff

## Exact source of truth

- Develop: `3a8120805e41d0fe9d283fc948d6e52b327a8e58`; canonical Quality `34893392725 = SUCCESS`.
- Error worker before this run: `44930e07f8cb422a13da9b4036c6187aa4a770eb`; no queued/in-progress Error-worker workflow exists on that exact lineage.
- Spec/Core: `95a60521bb06cb883e14bdc5803181b224f53f64`; Core Focused `34898273973 = FAILURE`; canonical `34898274002 = FAILURE`.
- Backend: `13ccd56eb7c4451e0b5b06532e98a67ec989c774`; Backend Focused `34899421459 = SUCCESS`; canonical `34899421431 = SUCCESS`.
- UI: `e149515870b773548a164658775159f29de323af`; exact Visual `34888542153 = FAILURE`, with exact-eleven capture, route identity, compare/proposal and artifact upload all `SUCCESS`; only final `Enforce visual verdict` is `FAILURE`.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## ITERATION-1 — current worker qualification

Develop remains exact canonical green. Backend advanced and is again exact focused + canonical green. UI has no new canonical/focused current-SHA assertion evidence. Spec/Core advanced to a new exact SHA and is the only newly red technical worker.

## ITERATION-2 — ERR-0070 isolated

Status: `OPEN`

Owner: Spec/Core.

Canonical `34898274002` on exact `95a60521...` has Windows release guards, Linux storage, Local install/pypdf, specification validator, Ruff and mypy green. Full pytest is the only canonical failure and reports exactly `2 failed, 5257 passed, 17 skipped`.

Both failures are in `tests/unit/test_core_focused_candidate_workflow.py`. Commit `95a60521...` intentionally expands `.github/workflows/core-focused-candidate.yml` to include `src/athena/api/research.py` and `tests/unit/test_api_research.py`, but the workflow contract still asserts the old selector strings/counts. This is stale harness-contract evidence, not a product failure.

Required owner action: update the focused-workflow contract to prove the intended Research-expanded selector exactly; do not broaden ownership, weaken the selector, or relax any gate.

## ITERATION-3 — ERR-0071 isolated

Status: `OPEN`

Owner: Spec/Core.

Core Focused `34898273973` on the same SHA has Ruff `SUCCESS` and focused pytest `SUCCESS` (`2 passed`), while mypy is `FAILURE`. Exact uploaded diagnostics contain only two mypy errors in `tests/unit/test_api_research.py`: both are `import-untyped`, for `athena.api.research` and `athena.jobs.models`. The final enforcement step is red only because mypy is red.

Required owner action: preserve Research coverage while correcting the focused mypy target/package-resolution boundary. Do not use `ignore_missing_imports`, blanket error-code suppression, Skip/XFail, or any gate weakening.

## ITERATION-4 — cascade deduplication

The red Core Focused workflow conclusion is not a third error: its final enforcement failure is a cascade of `ERR-0071`. The canonical red workflow is also not a generic aggregate error: exact pytest diagnostics isolate `ERR-0070`.

Historical `ERR-0065` stays stale rather than reopening as a generic enforcement signature. Historical `ERR-0064` stays fixed: the current Research selector expansion is intentionally Core-owned and is not the prior cross-ownership defect.

## ITERATION-5 — current UI and manifest truth

`ERR-0059 = FIXED`: current exact UI Visual evidence still proves exactly eleven native captures plus successful workspace route identity. Capture-derived manifest truth, `assigned_reference_count = 11`, and the fail-closed exact-eleven PASS contract remain unchanged.

`ERR-0054 = OPEN / UI-Visual-Review-owned`: the current exact UI Visual job passes technical capture/comparator/route/artifact stages and fails only at `Enforce visual verdict`. Current UI handoff remains `PAIRS_VERIFIED_0_OF_11`, `MATCH_0_OF_11`, Visual readiness `NO`. Error worker must not create or accept a baseline.

`ERR-0067/0068/0069 = IN_PROGRESS`: they were reproduced on the prior UI parent, not on current exact UI SHA `e1495158...`; do not infer them from the visual-verdict failure.

## Persistent release guards

Current Spec/Core red state does not reproduce packaging, Frozen argv, two-EXE, bounded-worker, adaptive-2048, lane-lock, duplicate-column, Core-startup or storage-bootstrap signatures. Canonical Windows release guards and pypdf install checks are green on `95a60521...`. Preserve all guards unchanged.

## Next root cause

1. Consume the next Spec/Core successor. `ERR-0070` closes only when the expanded workflow contract is exact and canonical pytest is green on that successor.
2. `ERR-0071` closes only when exact Core Focused mypy, Ruff and focused pytest are all green without suppression, and canonical is also green on the same successor.
3. Keep Develop and Backend closed while current exact evidence stays green.
4. Consume any new current-SHA UI canonical/focused evidence and reclassify `ERR-0067/0068/0069` independently from direct assertions only.
5. Keep `ERR-0054` strictly UI/Visual-Review-owned and `ERR-0059` closed absent a new exact regression.
