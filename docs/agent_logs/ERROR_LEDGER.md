# pATHENA Error Ledger

Evidence-first ledger for current exact-SHA failures. Historical IDs, old runs and old priorities are non-authoritative unless reproduced on the current exact SHA.

## Current source of truth

- `develop/pathena-next@c1847b26941ff83d9b80b2839435a6079dc19dea`; canonical Quality `34766898131` is still `IN_PROGRESS`. Specification validation, Ruff, mypy, Linux Storage, Local Install/pypdf and Windows release guards are green; only the long pytest lane remains active.
- `postmerge/spec-core@d2569f97607566e241443622ec1f11370aebb880`; Core Focused `34762195665 = SUCCESS`, canonical `34762195648 = SUCCESS`.
- `postmerge/backend@b7a1358caa1c5ae97066ea8075fcde4285b47882`; Backend Focused `34765672180 = SUCCESS`, canonical `34765672205 = FAILURE` only because the hosted runner received a shutdown signal at 92% of the full suite and exited 143. The isolated desktop-controller suite passed 6/6, the new schedule-timezone tests passed, Ruff/mypy passed, Linux Storage passed, Windows release guards passed, and Local Install/pypdf passed. This is infrastructure interruption evidence, not a reproduced product/test failure; no new Error ID is opened.
- `postmerge/ui@4322820fd02e15e30626e42107291360d5f79b18`; UI Focused `34766506253 = SUCCESS`, Core Focused `34766506246 = SUCCESS`, canonical `34766506348 = SUCCESS`. 11-Surface Visual Regression `34766501013 = FAILURE` for the independent capture-route defect described as `ERR-0058` below.
- `postmerge/errors` is the only branch mutated by this worker. `main` and `bnbgrs/ATHENA` remain read-only.

## OPEN

### ERR-0058 — P2 — exact Windows visual capture route identity drifts before workspace row 5

Status: `OPEN`

Exact reproduction: `postmerge/ui@4322820fd02e15e30626e42107291360d5f79b18`, 11-Surface Visual Regression `34766501013 = FAILURE`.

Evidence:

- Visual harness Ruff, comparator mypy, comparator contract tests, shared visual hierarchy token contract, and primary navigation accessibility contract all pass.
- Capture fails before baseline comparison with: `Workspace route identity drifted before capture: requested row 5, navigation row 1, page index 1.`
- The manifest still records assigned reference count 11 and captured reference count 11, but marks the run `FAIL`; the subsequent route-identity and baseline-comparison steps are skipped because capture exits non-zero.
- The same exact UI SHA has canonical Quality `SUCCESS`, UI Focused `SUCCESS`, Core Focused `SUCCESS`, Linux Storage `SUCCESS`, Windows release guards `SUCCESS`, and Local Install/pypdf `SUCCESS`. This isolates the defect to the native visual capture/navigation path rather than a broad product/runtime cascade.
- Current UI commit `4322820...` changes top-navigation keyboard traversal (`_link_top_navigation_tab_order`) and its acceptance test. This is UI-owned evidence; Error worker must not patch the same UI product path in parallel while UI owns the slice.

Required closure:

1. UI worker reproduces the route drift on an exact successor and identifies whether top-navigation focus traversal or capture route-selection sequencing causes row 5 to fall back to navigation row 1/page 1.
2. Minimal UI/harness fix; no weakening of route identity checks and no skipped capture.
3. Exact successor 11-Surface Visual Regression reaches route-identity verification and baseline stage successfully; normal UI/Core/canonical gates remain green.

## FIXED_PENDING_VERIFY

None currently.

## FIXED

### ERR-0053 — P2 — Send-button outer geometry contract

Status: `FIXED`

Develop repair `1c20496e5e91c800050a9586dce7a903f9d86a6c` restored `SHELL.composer_action_size` to the verified 44 px outer target without weakening the test. Canonical Quality `34764344711 = SUCCESS`; closure is integrated and exact-SHA verified.

### ERR-0056 — P2 — Core-Focused user-correction selector coverage

Status: `FIXED`

Integrated selector/trigger coverage and restored regression contracts were exact-canonical verified on Develop.

### ERR-0057 — P2 — Core-Focused workflow regression-test replacement / Ruff failure

Status: `FIXED`

The Error-owned restoration was integrated and exact-canonical verified; historical Ruff cascades on stale worker SHAs are non-authoritative.

### ERR-0055 — P2 — user-correction Ruff-only Spec/Core block

Status: `FIXED`

Owner-side and integrated exact-SHA verification succeeded.

### ERR-0049 — P1 — paired WAL/SHM startup identity replacement

Status: `FIXED`

Bounded storage fix is integrated and exact-canonical verified on Develop; no current exact-SHA regression exists in canonical storage/release guards.

## STALE

### ERR-0054 — P2 — missing Windows visual baseline

Status: `STALE`

The historical failure was a fail-closed missing-baseline verdict. The current exact UI run `34766501013` never reaches baseline comparison; it fails earlier in capture with the distinct route-identity defect `ERR-0058`. Therefore the old baseline root cause is not currently reproduced and must not remain OPEN.

## Persistent release guards

No current canonical lane reproduces pypdf packaging, fail-closed Frozen argv, Desktop/Worker executable separation, single Desktop with bounded workers, adaptive 2048-context reserve, Windows lane-lock escalation, duplicate-column, Core-startup, or storage-bootstrap failures. A transient `DatabaseStartupIdentityChangedError` appears during the current visual capture bootstrap, but the same exact SHA passes Windows storage/release guards, Linux Storage, Local Install and canonical Quality; it does not determine the current run failure and is not promoted to a separate error without a failing exact guard or repeatable product outcome.

## Next root cause

1. `ERR-0058` — UI/visual route identity drift is the highest current independently reproduced error.
2. Consume terminal Develop `34766898131`; do not create or duplicate a canonical run while it remains active.
3. Backend `34765672205` requires a clean exact-SHA canonical rerun by the owning workflow/integrator after the hosted-runner shutdown; do not patch product code for exit 143 evidence alone.
