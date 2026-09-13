# pATHENA Error Ledger

Evidence-first ledger for current exact-SHA failures. Historical IDs, old runs and old priorities are non-authoritative unless reproduced on the current exact SHA.

## Current source of truth

- `develop/pathena-next@a9aaf5f414b7a030598d1735244bcbf6407e6bcb`; canonical Quality `34772777276 = SUCCESS` (a second exact-SHA Quality run `34774341613` is also `SUCCESS`).
- `postmerge/errors@ed1ea5c9aadcb06f1b71e5ae9eec2173080a7e72`; Error-owned `ERR-0059` implementation candidate. No workflow run exists on this exact SHA.
- `postmerge/spec-core@af5283d7a6c6c5f1e256af1b2f07678ab52cd87b`; canonical Quality `34774353839 = SUCCESS`.
- `postmerge/backend@7516c67e1c19fded96239639aa2182c65b236b69`; Backend Focused `34774634769 = SUCCESS`, canonical Quality `34774634757 = SUCCESS`.
- `postmerge/ui@b3066df5be557047c59331476ea1de4e79045e67`; UI Focused `34770820473 = SUCCESS`, Core Focused and canonical Quality are green; 11-Surface Visual `34770817654 = FAILURE` only at final visual verdict after successful capture, route verification and comparison/proposal stage.
- `main` and `bnbgrs/ATHENA` remain read-only.

## OPEN

### ERR-0054 — P2 — missing reviewed Windows visual baseline

Status: `OPEN`

Exact reproduction: `postmerge/ui@b3066df5be557047c59331476ea1de4e79045e67`, 11-Surface Visual Regression `34770817654 = FAILURE`.

Evidence:

- Native capture of all eleven canonical surfaces succeeds.
- Workspace route identity verification succeeds.
- Baseline compare/proposal step succeeds.
- Artifact upload succeeds.
- Only `Enforce visual verdict` fails.
- `tests/qa/visual-baseline-windows.json` does not exist on the exact UI SHA, so no committed reviewed Windows baseline is available.
- UI Focused, Core Focused and canonical Quality are green on the same exact SHA; no product/runtime cascade is implicated.

Required closure:

1. UI/Visual owner must review the exact eleven native renderings against the authoritative references.
2. Commit a reviewed Windows baseline only after visual approval.
3. Re-run exact-SHA Visual Regression and require final verdict success.
4. Do not auto-accept the generated proposal, relax comparator tolerances, or bypass visual verdict enforcement.

## FIXED_PENDING_VERIFY

### ERR-0059 — P2 — visual manifest can falsely report full capture after partial failure

Status: `FIXED_PENDING_VERIFY`

Implementation candidate: `postmerge/errors@ed1ea5c9aadcb06f1b71e5ae9eec2173080a7e72`.

Root cause:

- The harness previously wrote `captured_reference_count` from the constant `expected_capture_count` and hard-coded all eleven surface labels.
- A partial-capture artifact could therefore contain fewer real PNGs while the manifest still claimed full capture coverage.

Fix:

- `captured_reference_surfaces` is now derived from `[capture["label"] for capture in captures]`.
- `captured_reference_count` is now `len(captures)`.
- `assigned_reference_count = 11` is unchanged.
- The fail-closed PASS condition remains `not errors and len(captures) == expected_capture_count`.
- No route, baseline, comparator, guard, test, Security, Storage or Recovery contract was weakened.

Verification evidence:

- Commit `ed1ea5c9aadcb06f1b71e5ae9eec2173080a7e72` changes only the two target manifest fields.
- Exact source inspection confirms the two actual-capture derivations and unchanged 11-capture PASS/assigned-reference guards.
- Existing regression contract `tests/qa/test_visual_capture_manifest_truth.py` requires both new expressions and rejects both stale constant forms.
- There is no open PR or workflow runner for `postmerge/errors`; exact executed focused/canonical evidence is therefore still absent. Do not promote to `FIXED` until the focused regression is executed on this candidate or its bounded integrated successor.

Required closure:

1. Execute `tests/qa/test_visual_capture_manifest_truth.py` on the exact candidate or bounded integrated successor.
2. Require success without weakening the regression assertions.
3. If integrated into another branch, require that branch's exact-SHA relevant regression/canonical evidence before final `FIXED`.

## FIXED

### ERR-0058 — P2 — workspace route identity drift before System capture

Status: `FIXED`

Exact verification: `postmerge/ui@b3066df5be557047c59331476ea1de4e79045e67`, Visual run `34770817654`.

- Native eleven-surface capture succeeds.
- Workspace route identity verification succeeds.
- The run progresses through baseline handling and artifact upload; therefore the historical row-5 fallback no longer reproduces on the current exact SHA.
- UI Focused, Core Focused and canonical Quality are green on the same exact SHA.

Also fixed and retained: `ERR-0053`, `ERR-0055`, `ERR-0056`, `ERR-0057`, `ERR-0049`.

## STALE

None among the currently tracked visual errors.

## Persistent release guards

No current exact canonical evidence reopens pypdf packaging, fail-closed Frozen argv, Desktop/Worker executable separation, single Desktop with bounded workers, adaptive 2048-context reserve, Windows lane-lock escalation, duplicate-column, Core-startup or storage-bootstrap failures.

## Next root cause

1. Verify `ERR-0059` with a real focused execution on the exact candidate or bounded integrated successor; do not touch its implementation again unless a new exact-SHA regression appears.
2. `ERR-0054` remains UI/Visual-review-owned; Error worker should inspect only closure evidence and must not create/accept a baseline in parallel.
3. Current Develop, Spec/Core, Backend and UI canonical lines are green; do not reopen them without a new exact-SHA failure signature.
4. If no new Error-owned exact-SHA failure appears, remain available for fresh failure evidence rather than inventing a new root cause.
