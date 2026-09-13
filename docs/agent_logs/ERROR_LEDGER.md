# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only current exact-SHA reproduced or verified failures are active; cascades are deduplicated. `FIXED` requires real integrated verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, guard/assertion weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop: `ae6ca984040c36a52c96c3e578cb0fee1e64136f` (`feat(core): integrate truthful stale knowledge policy`); canonical Quality `34748637687 = IN_PROGRESS`.
- Error worker before this update: `0e90f96d3819a37a5143e2d9c58495eace67c586`; exact-SHA workflow count = 0.
- Spec/Core: `12a2c2a4ac14c14a28f3bcfda9429d4db7a61830`; Core Focused `34745747874 = SUCCESS`, canonical `34745747939 = SUCCESS`.
- Backend: `2182382b8aa4a2c37cbf698c51b9de8f7c148287`; Storage Focused `34746286422 = SUCCESS`, canonical `34746286425 = SUCCESS`.
- UI: `402d80180d29a4a9ddf1d678bc9f75c808bbbb16`; UI Focused `34748439827 = SUCCESS`, Core Focused `34748439840 = SUCCESS`, canonical `34748439735 = IN_PROGRESS`.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current state

- OPEN: none.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: `ERR-0049`, `ERR-0053`.
- FIXED: prior closures plus `ERR-0047`, `ERR-0050`, `ERR-0051`, `ERR-0052`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`, `ERR-0038`, `ERR-0039`, `ERR-0054`.
- BLOCKED: none.

## ERR-0054 — historical visual-baseline absence on superseded UI SHA

- Severity: P2 visual-evidence / integration blocker when reproduced.
- Status: `STALE`.
- Last exact reproduction: `postmerge/ui@541c367547c698489ad548cc791f72dd27d141b4`, 11-Surface Visual Regression `34746342711 = FAILURE` because the committed Windows visual baseline was absent and the workflow failed closed after generating a proposal.
- Current UI HEAD is `402d80180d29a4a9ddf1d678bc9f75c808bbbb16`. The current exact-SHA run set contains UI Focused, Core Focused and canonical Quality; no 11-Surface Visual Regression run for this exact SHA is present in the current evidence.
- Per exact-SHA source-of-truth policy, the older `541c367...` visual failure is not authoritative for the current UI HEAD. Do not keep it `OPEN` merely from historical evidence.
- If a current exact-SHA visual run reproduces the same fail-closed baseline absence, reopen `ERR-0054` as `OPEN` and preserve the prior policy: no tolerance weakening, no Skip/XFail, no blind baseline acceptance.

## ERR-0053 — UI send-button shell geometry mismatch

- Severity: P2 integration blocker.
- Status: `FIXED_PENDING_VERIFY`.
- Product fix remains on ancestor `541c367547c698489ad548cc791f72dd27d141b4`, deriving the foundation send-button content box from the shell action-size token while accounting for the border.
- Current UI HEAD `402d80180d29a4a9ddf1d678bc9f75c808bbbb16` is two test-only commits ahead of the fix; compare evidence shows only `tests/unit/test_pathena_shared_components.py` and `tests/unit/test_pathena_window.py` changed after `541c367...`.
- Current exact same-SHA UI Focused `34748439827 = SUCCESS`; Core Focused `34748439840 = SUCCESS`; canonical `34748439735 = IN_PROGRESS`.
- Keep `FIXED_PENDING_VERIFY` until current exact UI canonical succeeds and later integrated Develop verification is green.

## ERR-0052 — Spec/Core Knowledge Read API Ruff/import blocker

- Severity: P2 integration blocker.
- Status: `FIXED`.
- Owner-side successor was exact green and bounded Knowledge Read integration was verified by Develop canonical `34744264489 = SUCCESS`. Historical Ruff `I001` remains closed absent a new exact-SHA reproduction.

## ERR-0049 — concurrent SQLite writer startup vs fail-closed sidecar identity continuity

- Severity: P1 Storage/Recovery integration blocker.
- Status: `FIXED_PENDING_VERIFY`.
- Backend fix `2182382b8aa4a2c37cbf698c51b9de8f7c148287` rejects direct complete WAL+SHM identity replacement during the bound startup window while preserving allowed publication/withdrawal transitions.
- Exact Storage Focused `34746286422 = SUCCESS`.
- Exact canonical Quality `34746286425 = SUCCESS`. This closes owner-side canonical verification; the paired-sidecar fix is not yet integrated into current Develop.
- Compare evidence between Backend candidate and current Develop is `diverged` with merge-base `8c2dda7794ef4949844feb30d265d34248aa4660`; therefore no claim of integrated closure is permitted yet.
- Promote `ERR-0049` to `FIXED` only after the bounded Storage slice is integrated into Develop and that exact Develop SHA is canonical green. Do not weaken Storage/Recovery guards during integration.

## Current Develop candidate

- `develop/pathena-next@ae6ca984040c36a52c96c3e578cb0fee1e64136f` integrates only the truthful stale-Knowledge policy from the exact-green Core candidate.
- canonical Quality `34748637687` is currently in progress. Do not start a competing canonical run or mutate Develop from the Error worker.
- No current exact-SHA failure has been observed yet, so no new Error ID is opened.

## Persistent release guards

Closed historical signatures reopen only on a current exact-SHA reproduction. No current evidence reopens pypdf Packaging, fail-closed Frozen argv, Desktop/Worker two-EXE split, bounded worker tree, adaptive 2048-context Chat reserve, Windows lane-lock, duplicate-column/Core-startup/storage-bootstrap, Security, Storage or Recovery guards.

## CI discipline

- No competing canonical run was started by the Error worker.
- `postmerge/errors@0e90f96d3819a37a5143e2d9c58495eace67c586` had zero workflow runs before mutation.
- No foreign worker product branch was mutated.
- No force push, history rewrite, main mutation, Skip/XFail, guard weakening, visual-tolerance relaxation, or Security/Storage/Recovery relaxation occurred.
