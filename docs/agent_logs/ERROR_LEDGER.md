# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only current exact-SHA reproduced or verified failures are active; cascades are deduplicated. `FIXED` requires real integrated verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, guard/assertion weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop: `8c2dda7794ef4949844feb30d265d34248aa4660` (`feat(core): integrate knowledge read API`). canonical Quality `34744264489 = SUCCESS`.
- Error worker before this update: `61aa174d46d57a73546f9cbc9f785a39e763dd2f`; zero workflow runs exist on `postmerge/errors`.
- Spec/Core: `12a2c2a4ac14c14a28f3bcfda9429d4db7a61830`; Core Focused `34745747874 = SUCCESS`, canonical `34745747939 = SUCCESS`.
- Backend: `2182382b8aa4a2c37cbf698c51b9de8f7c148287`; Storage Focused `34746286422 = SUCCESS`, canonical `34746286425 = PENDING`.
- UI: `541c367547c698489ad548cc791f72dd27d141b4`; UI Focused `34746344232 = SUCCESS`, Core Focused `34746344239 = SUCCESS`, canonical `34746344225 = PENDING`; 11-Surface Visual Regression `34746342711 = FAILURE` for fail-closed baseline absence.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current state

- OPEN: `ERR-0054`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: `ERR-0049`, `ERR-0053`.
- FIXED: prior closures plus `ERR-0047`, `ERR-0050`, `ERR-0051`, `ERR-0052`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`, `ERR-0038`, `ERR-0039`.
- BLOCKED: none.

## ERR-0054 — exact UI visual gate has no committed Windows baseline

- Severity: P2 visual-evidence / integration blocker.
- Status: `OPEN`.
- Exact reproducer: `postmerge/ui@541c367547c698489ad548cc791f72dd27d141b4`, 11-Surface Visual Regression `34746342711 = FAILURE`.
- The visual job successfully resolves and proves the exact SHA, installs the locked desktop environment, passes Ruff, mypy, comparator contract tests, shared hierarchy-token contract and navigation accessibility contract, captures all eleven surfaces, verifies route identity and uploads the artifact. Only `Enforce visual verdict` fails.
- Workflow contract explains the failure: if `tests/qa/visual-baseline-windows.json` is absent, it generates `artifacts/visual-baseline-proposal.json` and deliberately throws `Committed visual baseline is absent; proposal uploaded for review.` The final gate then fails closed. This is not evidence of a deterministic UI-product assertion regression.
- Exact artifact `pathena-visual-541c367547c698489ad548cc791f72dd27d141b4` reports `manifest.status = PASS`, captured 11/11 assigned surfaces, and no capture errors.
- Do not silence this by adding Skip/XFail, weakening tolerance, changing `continue-on-error` semantics, or blindly committing the generated baseline proposal. A committed baseline is promotion evidence and requires the UI worker's prescribed visual review against the authoritative references before acceptance.
- Ownership: UI / visual-evidence harness. Error worker documents and hands off; no parallel UI mutation.

## ERR-0053 — UI send-button shell geometry mismatch

- Severity: P2 integration blocker.
- Status: `FIXED_PENDING_VERIFY`.
- Former exact failure was resolved by UI fix `541c367547c698489ad548cc791f72dd27d141b4`, deriving the foundation send-button content box from the 48px shell action-size token while accounting for the existing 1px border.
- Exact same-SHA UI Focused `34746344232 = SUCCESS` with changed UI tests/navigation contract green; Core Focused `34746344239 = SUCCESS`.
- canonical `34746344225` remains pending. Do not mutate or supersede this UI candidate until that run finishes.
- The separate visual-baseline absence is tracked as `ERR-0054`; it does not reopen the send-button product root cause.

## ERR-0052 — Spec/Core Knowledge Read API Ruff/import blocker

- Severity: P2 integration blocker.
- Status: `FIXED`.
- Owner-side successor `bd5b0497a8c220e2a3a238f974109d060d7256e5` was exact green, and the bounded Knowledge Read API slice was integrated into Develop `8c2dda7794ef4949844feb30d265d34248aa4660`.
- Integrated canonical Quality `34744264489 = SUCCESS`. The historical Ruff `I001` is therefore closed and must not be reopened without a new exact-SHA reproduction.

## ERR-0049 — concurrent SQLite writer startup vs fail-closed sidecar identity continuity

- Severity: P1 Storage/Recovery integration blocker.
- Status: `FIXED_PENDING_VERIFY`.
- Backend fix `2182382b8aa4a2c37cbf698c51b9de8f7c148287` rejects direct complete WAL+SHM identity replacement during the bound startup window while preserving complete publication and withdrawal transitions.
- Exact same-SHA Storage Focused `34746286422 = SUCCESS`; changed Storage Ruff and mypy are green; focused Storage pytest reports `34 passed`, including the paired foreign WAL+SHM replacement case.
- canonical Quality `34746286425` remains pending. Do not mutate or supersede this Backend candidate until that exact run finishes.
- Promote to `FIXED` only on exact worker canonical SUCCESS and later integrated Develop verification; any new failure must be classified from its exact job evidence rather than by weakening Storage/Recovery guards.

## Persistent release guards

Closed historical signatures reopen only on a current exact-SHA reproduction. Current Develop `8c2dda...` is canonical green. No current evidence reopens pypdf Packaging, fail-closed Frozen argv, Desktop/Worker two-EXE split, bounded worker tree, adaptive 2048-context Chat reserve, Windows lane-lock, duplicate-column/Core-startup/storage-bootstrap, Security, Storage or Recovery guards.

## CI discipline

- No competing canonical run was started by the Error worker.
- `postmerge/errors` had zero workflow runs before mutation.
- No foreign worker product branch was mutated.
- No force push, history rewrite, main mutation, Skip/XFail, guard weakening, or Security/Storage/Recovery relaxation occurred.
