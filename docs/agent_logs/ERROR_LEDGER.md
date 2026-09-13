# pATHENA Error Ledger

Evidence-first ledger for current exact-SHA failures. Historical IDs, old runs and old priorities are non-authoritative unless reproduced on the current exact SHA.

## Current source of truth

- `develop/pathena-next@a9aaf5f414b7a030598d1735244bcbf6407e6bcb`; canonical Quality `34772777276 = IN_PROGRESS`.
- `postmerge/errors@cf8203ba11c205825363a57a424db8f3a9db2f42`; only Error-worker branch mutated in this run.
- `postmerge/spec-core@7a04a10a6f20b7a780a2f6d2db1d15f7608c08b0`; canonical Quality `34771164034 = SUCCESS`.
- `postmerge/backend@fa019ac6017ce24ce826f4ae3cfb3b14a418b5c4`; latest exact canonical remains `34768709258 = SUCCESS`.
- `postmerge/ui@b3066df5be557047c59331476ea1de4e79045e67`; UI Focused `34770820473 = SUCCESS`, Core Focused `34770820365 = SUCCESS`, canonical Quality `34770820352 = SUCCESS`, 11-Surface Visual `34770817654 = FAILURE` only at final visual verdict after successful capture, route verification and comparison/proposal stage.
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
- UI Focused, Core Focused and canonical Quality are all green on the same exact SHA; no product/runtime cascade is implicated.

Required closure:

1. Review the exact eleven native renderings against the authoritative references.
2. Commit a reviewed Windows baseline only after visual approval.
3. Re-run exact-SHA Visual Regression and require final verdict success.
4. Do not auto-accept the generated proposal, relax comparator tolerances, or bypass visual verdict enforcement.

### ERR-0059 — P2 — visual manifest can falsely report full capture after partial failure

Status: `OPEN`

Current reproduction: both `postmerge/errors` and current `postmerge/ui@b3066df5be557047c59331476ea1de4e79045e67` still construct `captured_reference_count` from `expected_capture_count` and hard-code the complete surface list instead of deriving coverage from actual `captures`.

Evidence:

- The previous partial-capture artifact proved the diagnostic failure mode: fewer PNGs can exist while manifest coverage claims all eleven.
- The current UI harness still contains the same two constant-derived manifest fields.
- Error worker strengthened `tests/qa/test_visual_capture_manifest_truth.py` in `cf8203ba11c205825363a57a424db8f3a9db2f42` to require actual derivation and explicitly reject both stale constant forms.
- The product/harness implementation itself is not yet changed, so no FIXED claim is made.

Required closure:

1. Set `captured_reference_surfaces` from actual capture labels.
2. Set `captured_reference_count = len(captures)`.
3. Keep `assigned_reference_count = 11` and the existing fail-closed PASS condition requiring all eleven captures.
4. Focused regression must pass without weakening route identity, baseline handling, comparator tolerances, Skip/XFail or release guards.

## FIXED_PENDING_VERIFY

None.

## FIXED

### ERR-0058 — P2 — workspace route identity drift before System capture

Status: `FIXED`

Exact verification: `postmerge/ui@b3066df5be557047c59331476ea1de4e79045e67`, Visual run `34770817654`.

- `Capture exactly eleven canonical surfaces with native fonts = SUCCESS`.
- `Verify captured workspace route identity = SUCCESS`.
- The run progresses through baseline handling and artifact upload; therefore the historical row-5 fallback no longer reproduces on the current exact SHA.
- UI Focused, Core Focused and canonical Quality are green on the same exact SHA.

Also fixed and retained: `ERR-0053`, `ERR-0055`, `ERR-0056`, `ERR-0057`, `ERR-0049`.

## STALE

None among the currently tracked visual errors. `ERR-0054` is reopened by current exact-SHA evidence.

## Persistent release guards

No current exact canonical evidence reopens pypdf packaging, fail-closed Frozen argv, Desktop/Worker executable separation, single Desktop with bounded workers, adaptive 2048-context reserve, Windows lane-lock escalation, duplicate-column, Core-startup or storage-bootstrap failures.

## Next root cause

1. `ERR-0059` remains the directly Error-owned actionable harness slice; implementation still needs the bounded two-field truthfulness correction.
2. `ERR-0054` is current but review-owned: consume the exact eleven-surface artifact and produce a reviewed baseline only if the renderings genuinely match requirements.
3. Consume Develop canonical `34772777276` when terminal; do not infer failure while it is still in progress.
