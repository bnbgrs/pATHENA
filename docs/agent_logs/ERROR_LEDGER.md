# pATHENA Error Ledger

Evidence-first ledger for current exact-SHA failures. Historical IDs, old runs and old priorities are non-authoritative unless reproduced on the current exact SHA.

## Current source of truth

- `develop/pathena-next@72ab7085f40afa74c0334b698dffc3462665d366`; canonical Quality `34779068839` is currently `IN_PROGRESS`. Specification validator, Ruff, mypy, Linux Storage, Windows release guards and Local Install/pypdf are green; full pytest is still running.
- `postmerge/errors@7d8cab5a231353b9ca2ba3e47ad22a91f2afea9f`; exact canonical Quality `34778491220 = FAILURE`, but `tests/qa/test_visual_capture_manifest_truth.py` passes on this exact SHA. The only failing pytest is the inherited historical Send-button 48-vs-44 geometry assertion; Windows, Linux Storage and Local Install/pypdf jobs are green.
- `postmerge/spec-core@97bb3c13d6c6a1911b631f0b9d511d0c10c5cc71`; Core Focused `34777239256 = SUCCESS`, canonical Quality `34777239238 = SUCCESS`.
- `postmerge/backend@7516c67e1c19fded96239639aa2182c65b236b69`; Backend Focused `34774634769 = SUCCESS`, canonical Quality `34774634757 = SUCCESS`.
- `postmerge/ui@b3066df5be557047c59331476ea1de4e79045e67`; UI Focused and canonical Quality are green; 11-Surface Visual `34770817654 = FAILURE` only at final visual verdict after successful capture, route verification and comparison/proposal stage.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## OPEN

### ERR-0054 — P2 — missing reviewed Windows visual baseline

Status: `OPEN`

Owner: UI/Visual Review. Error worker is evidence-only for this cluster.

Exact reproduction: `postmerge/ui@b3066df5be557047c59331476ea1de4e79045e67`, 11-Surface Visual Regression `34770817654 = FAILURE`.

Evidence:

- Native capture of all eleven canonical surfaces succeeds.
- Workspace route identity verification succeeds.
- Baseline compare/proposal and artifact upload succeed.
- Only `Enforce visual verdict` fails because no reviewed committed Windows baseline exists.
- UI Focused and canonical Quality are green on the same exact SHA.
- No current handoff proves that all eleven authoritative reference/render pairs have since been manually reviewed and approved.

Required closure:

1. UI/Visual owner reviews all eleven exact reference/render pairs.
2. Commit a reviewed Windows baseline only after visual approval.
3. Re-run exact-SHA Visual Regression and require final verdict success.
4. Never auto-accept the generated proposal, relax comparator tolerances, or bypass verdict enforcement.

## FIXED

### ERR-0059 — P2 — visual manifest falsely reported full capture after partial failure

Status: `FIXED`

Verification exact SHA: `postmerge/errors@7d8cab5a231353b9ca2ba3e47ad22a91f2afea9f`, canonical Quality run `34778491220`.

Root cause and fix:

- `captured_reference_surfaces` is derived from `[capture["label"] for capture in captures]`.
- `captured_reference_count` is `len(captures)`.
- `assigned_reference_count = 11` remains unchanged.
- PASS remains fail-closed: `not errors and len(captures) == expected_capture_count`.
- The post-capture mismatch/error guard remains unchanged.
- No route, baseline, comparator, Test, Security, Storage or Recovery contract was weakened.

Exact verification:

- `tests/qa/test_visual_capture_manifest_truth.py` passes inside canonical pytest on exact SHA `7d8cab5...`.
- Specification validator, Ruff and mypy also pass.
- Windows path/release guards, Linux Storage regressions and Local Install/pypdf all pass.
- The overall canonical run is red only because `tests/unit/test_pathena_window.py::test_reference_composer_uses_large_work_surface_and_send_target` sees inherited 48px geometry on this old Error-worker baseline. That failure is not a manifest failure and must not reopen `ERR-0059`.
- Current Develop source retains the authoritative 44px `composer_action_size`, so the Error-worker 48px failure is a stale-branch cascade, not a new current Develop reproduction of the historical geometry root cause.

Closure rule: do not touch `ERR-0059` again unless a new exact-SHA manifest-truth regression reproduces.

Also fixed and retained: `ERR-0058`, `ERR-0053`, `ERR-0055`, `ERR-0056`, `ERR-0057`, `ERR-0049`.

## STALE / DEDUPLICATED CASCADES

### Historical Send-button 48px failure on Error worker

Status: `STALE`

`postmerge/errors@7d8cab5...` is highly diverged from current Develop and its canonical run reproduces the old 48px Send target. This does not reopen `ERR-0053`: current Develop carries the 44px token and its current canonical candidate is the authority. No Error-worker product patch is permitted for this stale inherited UI state.

## Persistent release guards

No current exact evidence reopens pypdf packaging, fail-closed Frozen argv, Desktop/Worker executable separation, single Desktop with bounded workers, adaptive 2048-context reserve, Windows lane-lock escalation, duplicate-column, Core-startup or storage-bootstrap failures.

## Next root cause

1. `ERR-0059` is closed; do not revisit without a new exact-SHA regression.
2. `ERR-0054` remains UI/Visual-review-owned; inspect closure evidence only and never create/accept a baseline in parallel.
3. Consume terminal canonical `34779068839` on Develop. If it succeeds, keep Develop green; if it fails, diagnose only the new exact-SHA failure signature.
4. Spec/Core and Backend are exact-canonical green and are not diagnosis targets.
5. If no fresh Error-owned exact-SHA failure appears, do not manufacture work from historical red runs.
