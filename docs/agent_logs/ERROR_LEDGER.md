# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only current exact-SHA reproduced or verified failures are active; cascades are deduplicated. `FIXED` requires real integrated verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, guard/assertion weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop: `e2a0ead528d24f48d79c16fa4e93c43c5f589d8a`; canonical Quality `34734032423 = FAILURE`.
- Error worker entered this run at `fe507864e1f02c418d1120e68bbc4b23a39244ec`; zero workflow runs existed on that exact SHA before mutation.
- Workers: Spec/Core `78d51621cbdfa3282cd236b5d0c7f5984abedcae`; Backend `ff9988a4b8db84593552a26266213d5ec871ef62`; UI `704ccd243ba2edb4f71e27d402d83b91724c0b30`.
- Spec/Core exact: Core Focused `34730134596 = SUCCESS`; canonical `34730134589 = SUCCESS`.
- Backend exact: Backend Focused `34733130191 = SUCCESS`; Storage Focused `34733130198 = SUCCESS`; canonical `34733130192 = FAILURE` in the full Python quality pytest step while Linux Storage, Windows release guards and Local Install remain green.
- UI exact: Core Focused `34733651263 = SUCCESS`; canonical `34733651287 = SUCCESS`.
- Develop exact: specification validator, Ruff, mypy, Linux Storage, Windows release guards and Local Install are green; only the full Python quality pytest step fails in `34734032423`.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current state

- OPEN: `ERR-0049`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: `ERR-0047`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030` through `ERR-0037`, `ERR-0040` through `ERR-0046`, `ERR-0048`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`, `ERR-0038`, `ERR-0039`.
- BLOCKED: none.

## ERR-0049 — concurrent SQLite writer startup vs fail-closed sidecar identity continuity

- Severity: P1 Storage/Recovery integration blocker.
- Status: `OPEN`.
- Earlier exact reproducer: canonical `34728206821@postmerge/backend:185662aafe7ab539fafd698e021635debfcc2a60 = FAILURE`; sole Full-Pytest failure was the process-separated deletion reliability case where the second legitimate process failed storage bootstrap with `DatabaseStartupIdentityChangedError`.
- The later candidate introduced a `complete_rotation` acceptance path for complete WAL+SHM -> complete WAL+SHM identity changes with unchanged primary DB identity. That removed the observed legitimate race but broadened accepted identity transitions.
- Current Backend head `ff9988a4b8db84593552a26266213d5ec871ef62` remains unsuitable for broad promotion: Backend Focused `34733130191 = SUCCESS`, Storage Focused `34733130198 = SUCCESS`, but canonical `34733130192 = FAILURE`.
- Current exact test inventory still has no regression that simultaneously replaces both already-present WAL and SHM with foreign objects and expects fail-closed rejection. It covers single-member replacement, partial publication, complete publication and complete withdrawal only.
- Therefore the binding guard gap remains current independently of the present canonical failure: no evidence proves that arbitrary paired foreign WAL+SHM replacement is rejected once `complete_rotation` is accepted.
- Required next evidence: add a focused paired foreign WAL+SHM replacement regression that must raise `DatabaseStartupIdentityChangedError`; preserve the process-separated legitimate writer race, single-sidecar replacement, partial publication/withdrawal and complete publication/withdrawal tests. Do not accept arbitrary complete->complete replacement based only on both sidecar identities changing.
- Ownership remains Backend/Storage. Error worker must not parallel-edit this product guard while Backend owns the slice.

## ERR-0048 — Spec/Core knowledge-history Ruff/import blocker

- Severity: P2 integration blocker.
- Status: `FIXED`.
- Spec/Core exact `78d51621cbdfa3282cd236b5d0c7f5984abedcae` is owner-green: Core Focused `34730134596 = SUCCESS`, canonical `34730134589 = SUCCESS`.
- The bounded Knowledge revision-history/revision-change repair was integrated into Develop `b4cba3d5cba31213e789cb2cbbc91f651e465e71`.
- Exact integrated canonical Quality `34731514082@b4cba3d5cba31213e789cb2cbbc91f651e465e71 = SUCCESS`. The historical Ruff/import blocker is therefore closed and must not be reopened without a new current exact-SHA reproduction.

## ERR-0047 — Backend schedule-startup test used nonexistent JobPriority.HIGH

- Severity: P2 test/integration blocker.
- Status: `FIXED_PENDING_VERIFY`.
- Owner repair replaced the nonexistent `JobPriority.HIGH` contract with the real `JobPriority.TIME_CRITICAL` value and was owner-canonical-green on Backend `a709c229d6994c159490c2c1eaf3f2549f12cf56`.
- Integrator imported only the bounded two-file schedule-startup slice into current Develop `e2a0ead528d24f48d79c16fa4e93c43c5f589d8a`; the separate `database.py` `ERR-0049` mutation was intentionally excluded.
- Current Develop source contains `JobPriority.TIME_CRITICAL` consistently in the schedule-startup policy test, so the old syntactic contract defect is absent.
- Exact integrated canonical `34734032423` is nevertheless `FAILURE` in full pytest. Because the available exact job evidence does not expose the failing test name, do not claim integrated `FIXED` yet and do not attribute the current failure back to `ERR-0047` without diagnostics.
- Next evidence: consume the canonical diagnostics or a successor exact-SHA run. Close only when integrated exact evidence proves the old schedule-startup failure does not reproduce.

## Current unclassified canonical failure

Develop `e2a0ead528d24f48d79c16fa4e93c43c5f589d8a` has canonical `34734032423 = FAILURE` solely in `Quality — pytest`; specification validator, Ruff, mypy, Linux Storage, Windows release guards and Local Install all pass. The diagnostics artifact exists for this exact SHA, but the current connector path exposes artifact metadata rather than the contained pytest text. No new ERR ID is opened until the exact failing test/root cause is available; guessing from the integration delta is prohibited.

## Persistent release guards

Closed/stale historical signatures reopen only on current exact-SHA reproduction. Binding guards remain: Windows pypdf packaging; fail-closed Frozen argv; separate Desktop/Worker EXEs; exactly one Desktop with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock `PermissionError` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError`; duplicate-column/Core-startup/storage-bootstrap signatures. Current exact Develop and Backend Windows release-guard jobs are green; `ERR-0049` remains open because paired foreign-sidecar fail-closed coverage is still absent.
