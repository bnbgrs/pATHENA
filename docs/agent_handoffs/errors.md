# pATHENA Error Handoff

## Baseline

- Develop: `b4cba3d5cba31213e789cb2cbbc91f651e465e71`; canonical Quality `34731514082 = IN_PROGRESS`.
- Workers: Spec/Core `78d51621cbdfa3282cd236b5d0c7f5984abedcae`; Backend `a709c229d6994c159490c2c1eaf3f2549f12cf56`; UI `031f291bbbb215e6319bb30e7aed92768e6aac18`.
- Error worker entered at `4d56cdbde52af238917568948daf86bd7c112930`; no workflow runs existed before mutation or after the Ledger commit.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- OPEN: `ERR-0049`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: `ERR-0047`, `ERR-0048`.
- Prior closures remain closed absent current exact-SHA reproduction.

## ITERATION-1 — ERR-0049 owner candidate is green but not safe to close

`ERR-0049 = OPEN / P1`.

Backend successor `a709c229d6994c159490c2c1eaf3f2549f12cf56` is exact-green:

- Backend Focused `34730587835 = SUCCESS`;
- Storage Focused `34730587918 = SUCCESS`;
- canonical Quality `34730587873 = SUCCESS`.

The race repair adds a `complete_rotation` acceptance path to `_revalidate_existing_identity()`. It is true whenever the primary DB identity is unchanged, WAL+SHM are complete before and after, and both sidecar object identities changed.

That resolves the observed concurrent writer race but does not prove fail-closed continuity. The predicate cannot distinguish a legitimate SQLite pair rotation from simultaneous foreign replacement of both existing sidecars. The current regression suite has single-sidecar foreign replacement plus publication/withdrawal coverage, but no paired foreign WAL+SHM replacement case.

Do not integrate this Storage mutation yet. First require a focused test that replaces both accepted WAL and SHM objects and still expects `DatabaseStartupIdentityChangedError`. The eventual repair must preserve both that rejection and the process-separated legitimate writer startup.

## ITERATION-2 — ERR-0047 stronger owner closure evidence

`ERR-0047 = FIXED_PENDING_VERIFY / P2`.

The old nonexistent `JobPriority.HIGH` failure remains absent on the current Backend successor. `a709c229...` is now fully canonical-green, so the bounded schedule-startup fix itself is owner-verified.

Final closure still needs Develop integration and exact integrated canonical success. Because the same Backend head also contains the unresolved `ERR-0049` Storage mutation, prefer bounded integration of the schedule-startup slice rather than wholesale Backend promotion while `ERR-0049` is OPEN.

## ITERATION-3 — ERR-0048 integrated, final canonical still running

`ERR-0048 = FIXED_PENDING_VERIFY / P2`.

Spec/Core `78d51621cbdfa3282cd236b5d0c7f5984abedcae` is exact-green: Core Focused `34730134596 = SUCCESS`; canonical `34730134589 = SUCCESS`.

Develop `b4cba3d5cba31213e789cb2cbbc91f651e465e71` now contains the bounded Knowledge revision-history API/test and revision-change wording repair from that lineage. Integrated Quality `34731514082` is still `IN_PROGRESS`; close only if that exact run completes `SUCCESS`.

## ITERATION-4 — current UI/cascade classification

UI `031f291bbbb215e6319bb30e7aed92768e6aac18` is exact-green in all relevant lanes: UI Focused `34731122725 = SUCCESS`, Core Focused `34731122738 = SUCCESS`, canonical `34731122731 = SUCCESS`. No current UI error cluster is evidenced, and the previously closed Core-Focused ownership defect stays closed.

## ITERATION-5 — current release-guard classification

No persistent historical release-guard signature is reopened by current exact evidence. Backend's exact canonical is green, but its `ERR-0049` candidate still fails the stricter static fail-closed acceptance criterion above; canonical success alone does not authorize relaxing a binding Storage/Recovery guard.

## CI discipline

- No competing canonical run was started.
- `postmerge/errors` had zero workflow runs before mutation and after the Ledger commit.
- No product code or foreign worker branch was mutated.
- No force push, history rewrite, main mutation, Skip/XFail or guard relaxation occurred.

## Integrator handoff

- `ERR-0049 = OPEN / P1`: Backend `a709c229d6994c159490c2c1eaf3f2549f12cf56` is exact-green, but its `complete_rotation` predicate accepts any paired complete→complete WAL+SHM identity replacement. Hold the Storage mutation until paired foreign-sidecar rejection is explicitly regression-tested and preserved.
- `ERR-0047 = FIXED_PENDING_VERIFY / P2`: bounded schedule-startup fix is owner-canonical-green on `a709c229...`; integrate independently from unresolved Storage if safely separable.
- `ERR-0048 = FIXED_PENDING_VERIFY / P2`: integrated at Develop `b4cba3d5...`; canonical `34731514082` is still running.

## NEXT_ROOT_CAUSE

1. Consume the next Backend successor for `ERR-0049`. Required proof: process-separated race passes and simultaneous foreign WAL+SHM replacement still fails closed.
2. Consume `34731514082@b4cba3d5...`; on SUCCESS close `ERR-0048`.
3. Close `ERR-0047` only after its bounded schedule-startup change is integrated and exact Develop canonical is green.
4. Inspect any new exact failure immediately; do not recycle stale historical IDs without current reproduction.
