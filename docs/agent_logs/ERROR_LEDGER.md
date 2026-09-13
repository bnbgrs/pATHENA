# pATHENA Error Ledger

Evidence-first ledger for current exact-SHA failures. Historical IDs, old runs and old priorities are non-authoritative unless reproduced on the current exact SHA.

## Current source of truth

- `develop/pathena-next@ba6bc224cc152c144d13ca21730dad6620610abe`; canonical Quality `34781654173 = SUCCESS`. Specification validator, Ruff, mypy, full pytest, Linux Storage regressions, Windows release guards and Local Install/pypdf are green.
- `postmerge/errors@20b489a739b64e276affa2cf2d6490ee4183b614`; latest exact canonical Quality `34779840281 = FAILURE` only on the stale inherited 48-vs-44 Send-button geometry of this diverged worker baseline. The verified manifest-truth fix is not the failure and is now integrated on current Develop.
- `postmerge/spec-core@b35033657b2809febb491235bb284b6219975cb2`; Core Focused `34780613663 = SUCCESS`, canonical Quality `34780613667 = FAILURE` only in mypy. Full pytest is green (`5109 passed, 17 skipped`), as are Ruff, Linux Storage, Windows release guards and Local Install/pypdf.
- `postmerge/backend@82321f9acb6e542b11afa6b0b64568818f2432d1`; canonical Quality `34780789750 = SUCCESS`.
- `postmerge/ui@de4efa5d3814948d47d83484c4a27ac0c2daf64c`; Core Focused `34779940800 = SUCCESS`, UI Focused `34779940824 = SUCCESS`, canonical Quality is green on the same exact SHA. Current UI handoff still reports `PAIRS_VERIFIED_0_OF_11` and visual integration readiness `NO`.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## OPEN

### ERR-0060 — P2 — Spec/Core merge-split planner mypy tuple inference

Status: `OPEN`

Owner: Spec/Core. Error worker is evidence-only for this cluster and must not parallel-edit the product file while the owner branch holds the slice.

Exact reproduction: `postmerge/spec-core@b35033657b2809febb491235bb284b6219975cb2`, canonical Quality `34780613667 = FAILURE`.

Root cause:

- `src/athena/knowledge/merge_split_policy.py:77` fails mypy with `Incompatible types in assignment`.
- The variable `superseded` is inferred from the one-element branch as `tuple[UUID]` and later receives `(left, right)`, whose inferred type is `tuple[UUID, UUID]`.
- Runtime behavior is not failing: the dedicated merge/split tests pass and canonical pytest completes with `5109 passed, 17 skipped`.
- Ruff, Specification Validator, Linux Storage, Windows release guards and Local Install/pypdf are green on the same exact SHA. This is not a Storage, Packaging, Recovery or Runtime cascade.

Bounded owner fix:

1. Give `superseded` an explicit variable-length UUID tuple type before the branch, e.g. `tuple[UUID, ...]`, without changing planner semantics.
2. Run the smallest merge/split policy regression set plus mypy.
3. Require an exact-SHA Core Focused success and canonical Quality success on the Spec/Core successor before marking `FIXED`.

### ERR-0054 — P2 — Windows visual baseline review incomplete

Status: `OPEN`

Owner: UI/Visual Review. Error worker is evidence-only for this cluster.

Current exact state:

- `postmerge/ui@de4efa5d3814948d47d83484c4a27ac0c2daf64c` is Core-Focused, UI-Focused and canonical green.
- The current UI handoff still states `PAIRS_VERIFIED_0_OF_11`, visual readiness `NO`, and integrator readiness `NO` for reference/render matching.
- No current handoff proves that all eleven authoritative reference/render pairs have been reviewed and approved.
- The older visual-verdict failures belong to older SHAs and are not themselves authoritative for this current SHA.

Required closure:

1. UI/Visual owner produces exact current-candidate render evidence for all eleven assigned surfaces.
2. Review all eleven exact reference/render pairs.
3. Commit a Windows baseline only after visual approval.
4. Re-run exact-SHA 11-Surface Visual Regression and require final verdict success.
5. Never auto-accept a generated proposal, relax comparator tolerances, bypass route identity, weaken capture truth, or bypass verdict enforcement.

## FIXED

### ERR-0059 — P2 — visual manifest falsely reported full capture after partial failure

Status: `FIXED`

Verified first on the Error worker and now integrated on current Develop.

Current Develop evidence:

- `develop/pathena-next@ba6bc224cc152c144d13ca21730dad6620610abe` changes `captured_reference_surfaces` to `[capture["label"] for capture in captures]`.
- `captured_reference_count` is `len(captures)`.
- `assigned_reference_count = 11` remains unchanged.
- The existing fail-closed capture/verdict contract remains intact.
- canonical Quality `34781654173 = SUCCESS`, including Ruff, mypy, full pytest, Linux Storage, Windows release guards and Local Install/pypdf.

Closure rule: do not touch `ERR-0059` again unless a new exact-SHA manifest-truth regression reproduces.

Also fixed and retained: `ERR-0058`, `ERR-0053`, `ERR-0055`, `ERR-0056`, `ERR-0057`, `ERR-0049`.

## STALE / DEDUPLICATED CASCADES

### Historical Send-button 48px failure on Error worker

Status: `STALE`

`postmerge/errors@20b489a...` remains highly diverged and canonical `34779840281` is red on the inherited historical 48px Send target. Current Develop is canonical green and retains the authoritative 44px geometry. This does not reopen `ERR-0053`, and no Error-worker UI patch is permitted for this stale inherited state.

## Persistent release guards

No current exact evidence reopens pypdf packaging, fail-closed Frozen argv, Desktop/Worker executable separation, single Desktop with bounded workers, adaptive 2048-context reserve, Windows lane-lock escalation, duplicate-column, Core-startup or storage-bootstrap failures. Current Develop is green across the relevant Windows, Linux Storage and Local Install lanes.

## Next root cause

1. `ERR-0060` is the highest current exact-SHA failure. It is Spec/Core-owned: consume the owner fix and exact successor evidence; do not parallel-edit its product code on `postmerge/errors`.
2. `ERR-0054` remains UI/Visual-review-owned. The current handoff is still `PAIRS_VERIFIED_0_OF_11`; do not create or accept a baseline in parallel.
3. `ERR-0059` is closed and integrated; do not revisit without a new exact-SHA manifest regression.
4. Develop, Backend and current UI canonical clusters are green and are not diagnosis targets.
5. If no new Error-owned exact-SHA failure appears, do not manufacture work from historical red runs.
