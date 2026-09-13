# pATHENA Error Handoff

## Baseline

- Develop: `8c2dda7794ef4944feb30d265d34248aa4660`; canonical Quality `34744264489 = SUCCESS`.
- Spec/Core: `12a2c2a4ac14c14a28f3bcfda9429d4db7a61830`; Core Focused `34745747874 = SUCCESS`; canonical `34745747939 = SUCCESS`.
- Backend: `2182382b8aa4a2c37cbf698c51b9de8f7c148287`; Storage Focused `34746286422 = SUCCESS`; canonical `34746286425 = PENDING`.
- UI: `541c367547c698489ad548cc791f72dd27d141b4`; UI Focused `34746344232 = SUCCESS`; Core Focused `34746344239 = SUCCESS`; canonical `34746344225 = PENDING`; 11-Surface Visual Regression `34746342711 = FAILURE`.
- `main` and `bnbgrs/ATHENA` remain untouched.

## Current error state

- OPEN: `ERR-0054`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: `ERR-0049`, `ERR-0053`.
- FIXED: prior closures plus `ERR-0047`, `ERR-0050`, `ERR-0051`, `ERR-0052`.
- BLOCKED: none.

## ERR-0054 — OPEN / visual baseline evidence gap

Current exact UI SHA `541c367547c698489ad548cc791f72dd27d141b4` fails 11-Surface Visual Regression `34746342711` only at `Enforce visual verdict`.

Everything before the verdict is green: exact SHA proof, locked desktop install, visual-harness Ruff, comparator mypy, comparator tests, shared hierarchy-token contract, navigation accessibility contract, eleven-surface capture, route-identity verification, comparison/proposal generation and artifact upload. The exact artifact manifest reports PASS with 11/11 assigned surfaces captured and no capture errors.

The workflow itself explains the failure. When `tests/qa/visual-baseline-windows.json` is absent it deliberately generates `artifacts/visual-baseline-proposal.json`, throws `Committed visual baseline is absent; proposal uploaded for review.`, and the final verdict step fails closed.

This must not be repaired by weakening the gate or blindly committing the generated proposal. A baseline is evidence, not a convenience fixture. UI owns visual review against the authoritative references; only after that review may a reviewed baseline be committed through the UI path.

## ERR-0052 — FIXED

Develop `8c2dda7794ef4949844feb30d265d34248aa4660` completed canonical Quality `34744264489 = SUCCESS`. The integrated Knowledge Read API / prior Ruff blocker is closed.

## ERR-0049 — FIXED_PENDING_VERIFY / P1

Backend fix `2182382b8aa4a2c37cbf698c51b9de8f7c148287` now fails closed on direct complete WAL+SHM replacement during the bound startup window while preserving legitimate complete publication/withdrawal transitions.

Exact same-SHA evidence: Storage Focused `34746286422 = SUCCESS`, changed Storage Ruff = SUCCESS, Storage mypy = SUCCESS, focused Storage pytest = `34 passed`, including the paired foreign WAL+SHM replacement regression.

Canonical Quality `34746286425` remains queued/pending. Do not touch or supersede the Backend candidate until it resolves. Promote only from exact canonical evidence; if it fails, classify the exact failing job before any further code change.

## ERR-0053 — FIXED_PENDING_VERIFY / P2

UI fix `541c367547c698489ad548cc791f72dd27d141b4` aligns the send-button foundation content-box geometry with the 48px shell action token while preserving the square invariant.

Exact same-SHA UI Focused `34746344232 = SUCCESS` and Core Focused `34746344239 = SUCCESS`. canonical Quality `34746344225` remains queued/pending. The separate fail-closed missing-baseline condition is `ERR-0054` and does not reopen this product fix.

## CI discipline

- No competing canonical run was started.
- No Backend/UI/Spec-Core product branch was mutated by Error worker.
- `postmerge/errors` had zero workflow runs before mutation.
- No force push, history rewrite, main mutation, Skip/XFail, guard weakening, visual-tolerance relaxation, or Security/Storage/Recovery relaxation occurred.

## Integrator / worker handoff

- `ERR-0049`: consume canonical `34746286425`; if SUCCESS keep repaired state pending integrated Develop verification; if failure classify only exact job evidence.
- `ERR-0053`: consume canonical `34746344225`; if SUCCESS keep repaired state pending integrated Develop verification; if failure classify only exact job evidence.
- `ERR-0054`: UI must review the exact 11-surface artifact against authoritative references and produce a reviewed committed Windows baseline without loosening comparator policy. Error worker must not auto-accept the generated proposal.

## NEXT_ROOT_CAUSE

Highest actionable root cause is `ERR-0054` as a visual-evidence gate gap, but ownership is UI and a safe Error-worker product mutation is not justified. While Backend/UI canonicals are pending, inspect new exact-SHA failures only; do not churn already-green focused fixes.
