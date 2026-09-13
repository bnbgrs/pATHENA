# pATHENA Error Ledger

Evidence-first ledger for current exact-SHA failures. Historical IDs, old runs and old priorities are non-authoritative unless reproduced on the current exact SHA.

## Current source of truth

- `develop/pathena-next@c1847b26941ff83d9b80b2839435a6079dc19dea`; canonical Quality `34766898131 = SUCCESS`.
- `postmerge/spec-core@d2569f97607566e241443622ec1f11370aebb880`; Core Focused `34762195665 = SUCCESS`, canonical `34762195648 = SUCCESS`.
- `postmerge/backend@fa019ac6017ce24ce826f4ae3cfb3b14a418b5c4`; Backend Focused `34768709243 = SUCCESS`, canonical `34768709258 = SUCCESS`.
- `postmerge/ui@4322820fd02e15e30626e42107291360d5f79b18`; UI Focused/Core Focused/canonical remain green from the exact candidate lineage, while 11-Surface Visual Regression `34766501013 = FAILURE` at capture route identity.
- `postmerge/errors` is the only branch mutated by this worker. `main` and `bnbgrs/ATHENA` remain read-only.

## OPEN

### ERR-0058 — P2 — exact Windows visual capture route identity drifts before workspace row 5

Status: `OPEN`

Exact reproduction: `postmerge/ui@4322820fd02e15e30626e42107291360d5f79b18`, 11-Surface Visual Regression `34766501013 = FAILURE`.

Evidence:

- Visual harness Ruff, comparator mypy, comparator tests, shared visual hierarchy token contract and navigation accessibility contract pass before capture.
- Capture fails with: `Workspace route identity drifted before capture: requested row 5, navigation row 1, page index 1.`
- The exact artifact contains workspace PNGs only for rows 0-4; System and Settings are absent. Auxiliary PALLAS, Command Palette, Help and ComfyUI captures still run afterward.
- The same UI SHA is otherwise canonical/focused green, isolating the defect to the visual capture/navigation path.
- UI owns the navigation/product surface. Error worker must not parallel-patch that UI product code while UI owns the slice.

Required closure:

1. UI reproduces the row-5 fallback on an exact successor and isolates the signal/focus/route transition that returns navigation/page to row 1.
2. Apply the smallest UI or capture-sequencing fix without weakening route-identity checks.
3. Exact successor Visual run captures all seven workspace rows and reaches route verification and baseline handling while UI/Core/canonical remain green.

### ERR-0059 — P2 — visual manifest falsely reports full 11-surface capture after partial failure

Status: `OPEN`

Exact reproduction: artifact `pathena-visual-4322820fd02e15e30626e42107291360d5f79b18` from Visual run `34766501013`.

Evidence:

- The uploaded artifact contains exactly nine PNG files: workspace rows 0-4 plus PALLAS, Command Palette, Help and ComfyUI.
- `manifest.json` nevertheless reports `captured_reference_count: 11` and enumerates System and Settings in `captured_reference_surfaces` even though their PNGs were never produced.
- Root cause is harness-owned: `scripts/render_pathena_ui_snapshot.py` writes `captured_reference_count` from the constant `expected_capture_count` and writes a hard-coded eleven-item surface list instead of deriving both fields from `captures`.
- This does not cause the existing gate to pass because top-level manifest status is still `FAIL`; however it makes diagnostic evidence internally false and can mislead downstream review.
- Error worker added `tests/qa/test_visual_capture_manifest_truth.py` in commit `464b85b0365c955bf0670b016b8b7a3baa5eaa58` to require actual-count and actual-label derivation. The current script does not yet satisfy this regression contract, so no FIXED claim is made.

Required closure:

1. Change only the harness manifest construction so `captured_reference_count == len(captures)` and `captured_reference_surfaces` is derived from the actual capture records.
2. Keep `assigned_reference_count = 11` and the top-level PASS condition requiring all eleven captures.
3. Focused regression test must pass; no tolerance, route-identity or visual verdict weakening.

## FIXED_PENDING_VERIFY

None.

## FIXED

- `ERR-0053` — Send-button outer geometry contract; integrated Develop canonical success.
- `ERR-0056` — Core-Focused user-correction selector coverage; integrated and verified.
- `ERR-0057` — Core-Focused workflow regression-test/Ruff repair; integrated and verified.
- `ERR-0055` — user-correction Ruff-only Spec/Core block; verified.
- `ERR-0049` — paired WAL/SHM startup identity replacement; integrated and exact-canonical verified.

## STALE

### ERR-0054 — P2 — missing Windows visual baseline

Status: `STALE`

Current exact UI visual capture fails before baseline comparison. Reopen only if a future exact SHA reaches comparison and reproduces the missing-baseline verdict.

## Persistent release guards

No current canonical lane reproduces pypdf packaging, fail-closed Frozen argv, Desktop/Worker executable separation, single Desktop with bounded workers, adaptive 2048-context reserve, Windows lane-lock escalation, duplicate-column, Core-startup or storage-bootstrap failures.

## Next root cause

1. `ERR-0059` is the current Error-owned/harness-owned actionable slice: fix truthful manifest derivation and focused-verify it.
2. `ERR-0058` remains the highest UI-owned product/capture-route failure; consume UI successor evidence without parallel product mutation.
3. Backend current exact successor is now canonical green; the prior exit-143 interruption is stale infrastructure evidence and requires no product fix.
