# pATHENA Error Hunter Handoff

## Current exact state

- Develop: `c1847b26941ff83d9b80b2839435a6079dc19dea`; canonical Quality `34766898131 = SUCCESS`.
- Spec/Core: `d2569f97607566e241443622ec1f11370aebb880`; Core Focused `34762195665 = SUCCESS`, canonical `34762195648 = SUCCESS`.
- Backend: `fa019ac6017ce24ce826f4ae3cfb3b14a418b5c4`; Backend Focused `34768709243 = SUCCESS`, canonical `34768709258 = SUCCESS`. The older exit-143 canonical interruption is stale infrastructure evidence.
- UI: `4322820fd02e15e30626e42107291360d5f79b18`; exact 11-Surface Visual run `34766501013 = FAILURE` at workspace row 5 route identity.
- `main` and `bnbgrs/ATHENA` remain read-only. Error-worker mutations remain confined to `postmerge/errors`.

## ITERATION-1 — Develop/backend terminal outcomes consumed

Develop canonical `34766898131` completed `SUCCESS`. Backend synchronized to exact successor `fa019ac6017ce24ce826f4ae3cfb3b14a418b5c4` and both Backend Focused `34768709243` and canonical `34768709258` completed `SUCCESS`.

No Backend product Error ID is opened. The previous runner shutdown/exit-143 event is not a current exact-SHA product failure.

## ITERATION-2 — ERR-0058 exact artifact inspected

Status: `OPEN`

Exact UI artifact from Visual run `34766501013` was downloaded and inspected. The route failure is real and occurs before System workspace capture:

`Workspace route identity drifted before capture: requested row 5, navigation row 1, page index 1.`

Actual workspace files exist only for Chat, Knowledge, Research, Jobs and Files. System and Settings workspace PNGs are absent. PALLAS, Command Palette, Help and ComfyUI later capture because their timers continue independently.

UI owns the navigation/product slice. Do not parallel-change `pathena_layout_refinement_2200.py` or other UI route code from Error worker while UI owns it. Required UI successor must preserve the route-identity guard and make rows 5 and 6 remain selected through capture.

## ITERATION-3 — ERR-0059 opened: manifest evidence is internally false

Status: `OPEN`

The same artifact exposes an independent harness-owned root cause. Only nine PNG captures exist, but `manifest.json` reports `captured_reference_count: 11` and lists all eleven assigned surfaces as captured.

Exact harness cause in `scripts/render_pathena_ui_snapshot.py`:

- `captured_reference_count` is assigned from constant `expected_capture_count` rather than `len(captures)`;
- `captured_reference_surfaces` is a hard-coded eleven-item list rather than actual capture records.

This does not weaken the current gate because top-level status is `FAIL`, but the evidence is untruthful and can mislead review. Error worker added regression contract `tests/qa/test_visual_capture_manifest_truth.py` in commit `464b85b0365c955bf0670b016b8b7a3baa5eaa58` requiring actual count and actual labels.

The script itself still needs the bounded harness change before `ERR-0059` can move to `FIXED_PENDING_VERIFY`:

- use `"captured_reference_surfaces": [capture["label"] for capture in captures]`;
- use `"captured_reference_count": len(captures)`;
- retain `assigned_reference_count = 11`;
- retain the existing PASS condition requiring all eleven captures;
- do not weaken route identity, baseline handling, comparator tolerances, Skip/XFail or any release guard.

## ITERATION-4 — ERR-0054 remains stale

Status: `STALE`

The current visual run fails before baseline comparison, so the historical missing-baseline root cause is not currently reproduced. Reopen only on a future exact SHA that reaches comparison and reproduces that verdict.

## Persistent release guards

No current exact canonical evidence reopens pypdf packaging, Frozen argv, Desktop/Worker split, single Desktop/bounded workers, adaptive 2048-context reserve, Windows lane-lock escalation, duplicate-column, Core-startup or storage-bootstrap failures.

## Next root cause

1. Finish `ERR-0059` with the two-field harness correction and run its focused regression contract.
2. Consume the next exact UI successor for `ERR-0058`; if UI fixes route row 5/6, close the Error-side parallel path immediately.
3. After those, scan fresh exact-SHA canonical failures only; do not resurrect historical IDs without current reproduction.
