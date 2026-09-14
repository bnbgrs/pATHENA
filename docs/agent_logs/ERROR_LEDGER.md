# pATHENA Error Ledger

Evidence-first ledger for current exact-SHA failures. Historical IDs, old runs and priorities are non-authoritative unless reproduced on a current exact SHA.

## Current source of truth

- `develop/pathena-next@ee8aa791742f7cbdd056532e66a50da14c461c4a`; canonical Quality `34818856565 = SUCCESS`.
- `postmerge/errors@e1b6e00f375fa5ceab143d01ee9c01ab598cd133` before this repair; canonical `34816691363 = FAILURE`, with validator/Ruff/mypy/Linux Storage/Windows release guards/Local Install green and exactly one inherited stale 48px UI pytest failure.
- `postmerge/spec-core@6c7f417a53428f496d7b31e330917d4a53c85189`; canonical `34818641155 = SUCCESS`.
- `postmerge/backend@52eb61de9ecfde4074778a1bab2966e18aab526d`; canonical `34796053576 = SUCCESS`.
- `postmerge/ui@a88eac5f05db4128ae21b7c747e95c16a91191c4`; Visual `34819309682 = FAILURE` only at final visual verdict after eleven captures and route identity pass. Canonical `34819314295` is still running at this ledger update.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## OPEN

### ERR-0064 — P2 — Core Focused changed-file selector crosses ownership boundary

Status: `IN_PROGRESS`

Owner: Error/Harness.

Exact reproduction: Core Focused `34819314380` on `postmerge/ui@a88eac5f05db4128ae21b7c747e95c16a91191c4`. Ruff and focused pytest are clean, but mypy diagnostics contain 61 errors in unrelated UI tests such as `test_pathena_window.py`, `test_system_workspace.py`, `test_pathena_comfyui_shell.py`, and other desktop tests. The focused pytest selector reports no changed Core-owned test files. Root cause is the Ruff/mypy selector in `core-focused-candidate.yml`: it accepts all `tests/unit/*.py`, while the workflow's declared Core ownership and focused pytest selector are limited to claim/knowledge/concept-note/identity-transition/temporal/user-correction test families.

Bounded repair in this Error-worker candidate: keep `src/athena/knowledge/**` and `src/athena/api/knowledge_*.py`, but make Ruff, mypy and Ruff-remediation test selection use the same Core-owned test-family regex already used by focused pytest. No canonical test/type guard is weakened; repository-wide canonical Quality remains unchanged.

Closure requires exact focused success on a candidate exercising the repaired workflow, followed by canonical qualification as applicable.

### ERR-0054 — P2 — Windows visual baseline review incomplete

Status: `OPEN`

Owner: UI / Visual Review.

Current exact Visual `34819309682` on `a88eac5f...` now captures all eleven surfaces, verifies route identity, compares/emits proposal, and uploads artifacts; only `Enforce visual verdict` fails. The current UI handoff still says `PAIRS_VERIFIED_0_OF_11` / `MATCH_0_OF_11`. No Error-worker baseline creation or acceptance. UI must open the eleven exact reference/render pairs and record truthful review states before closure.

## FIXED / HELD CLOSED

### ERR-0063 — P2 — UI capture/route failure

Status: `FIXED`

Exact current UI Visual `34819309682` passes `Capture exactly eleven canonical surfaces with native fonts` and `Verify captured workspace route identity`; the prior route/capture blocker no longer reproduces.

### ERR-0059 — P2 — manifest capture truth

Status: `FIXED`

The exact current UI artifact `pathena-visual-a88eac5f...` contains eleven real captures, `errors=[]`, `status=PASS`, `assigned_reference_count=11`, `captured_reference_count=11`, and `captured_reference_surfaces` equal to the actual capture labels. The manifest therefore proves the bounded fix on an exact current SHA while preserving the fail-closed exact-eleven PASS contract. Do not touch again absent a new exact regression.

- `ERR-0062` — `FIXED`; no current matching Core failure.
- `ERR-0060` — `FIXED`; no current matching Core failure.
- `ERR-0061` — `FIXED`; Core Focused enforces mypy.
- Historical `ERR-0058`, `ERR-0053`, `ERR-0055`, `ERR-0056`, `ERR-0057`, `ERR-0049` remain closed absent new exact reproduction.

## STALE / DEDUPLICATED CASCADES

### Error-worker inherited 48px UI geometry divergence

Status: `STALE`

Canonical `34816691363` on exact `e1b6e00f...` is red only because `test_reference_composer_uses_large_work_surface_and_send_target` observes 48px against the authoritative 44px guard; 5067 tests pass and the manifest-truth regression test passes. Do not reopen the UI defect, weaken the 44px guard or patch UI product code from `postmerge/errors`.

## Persistent release guards

No current exact evidence reopens pypdf packaging, fail-closed Frozen argv, Desktop/Worker executable separation, single Desktop with bounded workers, adaptive 2048-context reserve, Windows lane-lock escalation, duplicate-column, Core-startup or storage-bootstrap failures. Keep guards unchanged.

## Next root cause

1. Qualify this `ERR-0064` harness repair on its exact Error-worker SHA; do not supersede while canonical/focused checks are active.
2. Consume terminal UI canonical result for `a88eac5f...`; open only a newly reproduced exact failure.
3. UI owns `ERR-0054`: perform real 11/11 visual review; no baseline acceptance by Error worker.
4. Keep `ERR-0059` and `ERR-0063` closed absent new exact regression.
5. Keep Spec/Core and Backend closed while exact canonical-green.
