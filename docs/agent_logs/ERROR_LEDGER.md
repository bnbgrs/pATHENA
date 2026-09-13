# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only current exact-SHA reproduced or verified failures are active; cascades are deduplicated. `FIXED` requires real integrated verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, guard/assertion weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop: `ae6ca984040c36a52c96c3e578cb0fee1e64136f`; canonical Quality `34748637687 = SUCCESS`.
- Error worker before this update: `496cd6ef20965950588a85fcc3263517497d7edf`; exact-SHA workflow count = 0.
- Spec/Core: `60b82913ed64f13a92c52bb52448011ac208dacf`; exact canonical Quality `34749319064` completed successfully, including Python quality, Linux storage, Windows path safety and local-install jobs.
- Backend: `aab04d0c4564a07f9af5c12e6fa496a5e1038ff7`; Storage Focused `34749553305 = SUCCESS`; canonical Quality `34749553299 = SUCCESS`.
- UI: `3dfd310c06f3a6b3e34db0d524bf752269fe8bcc`; UI Focused `34749938754 = SUCCESS`; Core Focused `34749938787 = SUCCESS`; canonical Quality `34749938741 = SUCCESS`.
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
- Last exact reproduction remains `postmerge/ui@541c367547c698489ad548cc791f72dd27d141b4`, 11-Surface Visual Regression `34746342711 = FAILURE` because the committed Windows visual baseline was absent and the workflow failed closed after generating a proposal.
- Current UI HEAD is now `3dfd310c06f3a6b3e34db0d524bf752269fe8bcc`; its current exact run set has UI Focused, Core Focused and canonical all `SUCCESS`.
- No current exact-SHA 11-Surface Visual Regression failure for `3dfd310c...` is present in the consumed evidence. Therefore the older visual failure remains non-authoritative and `STALE`.
- If a current exact-SHA visual run reproduces the fail-closed baseline absence, reopen `ERR-0054` as `OPEN`; do not weaken tolerance, add Skip/XFail, or blindly accept a generated baseline.

## ERR-0053 — UI send-button shell geometry mismatch

- Severity: P2 integration blocker.
- Status: `FIXED_PENDING_VERIFY`.
- Product fix remains on ancestor `541c367547c698489ad548cc791f72dd27d141b4`.
- Current UI successor `3dfd310c06f3a6b3e34db0d524bf752269fe8bcc` is exact green: UI Focused `34749938754 = SUCCESS`, Core Focused `34749938787 = SUCCESS`, canonical `34749938741 = SUCCESS`.
- Owner-side verification is complete. Keep `FIXED_PENDING_VERIFY` until the bounded UI fix is integrated into Develop and that resulting exact Develop SHA is canonical green.

## ERR-0052 — Spec/Core Knowledge Read API Ruff/import blocker

- Severity: P2 integration blocker.
- Status: `FIXED`.
- Owner-side successor was exact green and bounded Knowledge Read integration was verified by Develop canonical `34744264489 = SUCCESS`. Historical Ruff `I001` remains closed absent a new exact-SHA reproduction.

## ERR-0049 — concurrent SQLite writer startup vs fail-closed sidecar identity continuity

- Severity: P1 Storage/Recovery integration blocker.
- Status: `FIXED_PENDING_VERIFY`.
- Current Backend successor is `aab04d0c4564a07f9af5c12e6fa496a5e1038ff7`, synchronized history-preservingly with current Develop.
- Exact Storage Focused `34749553305 = SUCCESS`; exact canonical Quality `34749553299 = SUCCESS`.
- Compare against current Develop `ae6ca984...` is `ahead`; the effective file delta is still bounded to exactly `src/athena/storage/database.py` and `tests/unit/test_storage_database_startup_identity.py`.
- This materially strengthens integration safety: no unrelated Backend product delta is present in the current tree comparison. However the Storage fix is not yet in Develop, so integrated closure is not claimed.
- Promote `ERR-0049` to `FIXED` only after those bounded Storage changes are integrated into Develop and that exact Develop SHA is canonical green. Preserve all fail-closed Storage/Recovery guards.

## Current Develop state

- `develop/pathena-next@ae6ca984040c36a52c96c3e578cb0fee1e64136f` canonical Quality `34748637687 = SUCCESS`.
- The previous in-progress state is closed without a new failure signature. No new Error ID is opened from that candidate.

## Current worker requalification

- Spec/Core `60b82913...` is exact canonical green; no current Core error signature is reproduced.
- Backend `aab04d0c...` is Storage-Focused and canonical green; only `ERR-0049` remains pending integrated verification.
- UI `3dfd310c...` is UI-Focused, Core-Focused and canonical green; only `ERR-0053` remains pending integrated verification. Historical `ERR-0054` remains stale.

## Persistent release guards

Closed historical signatures reopen only on a current exact-SHA reproduction. Current evidence does not reopen pypdf Packaging, fail-closed Frozen argv, Desktop/Worker two-EXE split, bounded worker tree, adaptive 2048-context Chat reserve, Windows lane-lock, duplicate-column/Core-startup/storage-bootstrap, Security, Storage or Recovery guards.

## CI discipline

- No competing canonical run was started by the Error worker.
- `postmerge/errors@496cd6ef20965950588a85fcc3263517497d7edf` had zero workflow runs before mutation.
- No foreign worker product branch was mutated.
- No force push, history rewrite, main mutation, Skip/XFail, guard weakening, visual-tolerance relaxation, or Security/Storage/Recovery relaxation occurred.
