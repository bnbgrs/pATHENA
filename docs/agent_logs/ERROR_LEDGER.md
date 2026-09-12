# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA-evidenced failures are active; cascades are deduplicated. `FIXED` requires real verification on the relevant integrated exact SHA. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, assertion/static-check weakening, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop source of truth: `develop/pathena-next@915668a376390d86fb333291f555eb804dfa4358` (`feat(backend): integrate schedule codec and startup identity hardening`).
- Current Develop canonical Quality: `34718446158@915668a376390d86fb333291f555eb804dfa4358 = IN_PROGRESS`; Errors started no competing run.
- Previous Develop `54c990285503e5076d31f46408ef530b9f02de28` canonical `34715466882 = SUCCESS`.
- Error worker entered this run at `postmerge/errors@cbcb9f60981484554d39f614308b32b67f378787`; exact SHA had zero workflow runs before mutation.
- Current workers: Spec/Core `47053f798bae152f676e9ff4be22ca4c6c06a6a8`; Backend `c40be5764e600fe961bc3aeaf39c17f91100e34f`; UI `8b38c1a501789cbfb7c76b1ee1acef999270fa13`.
- Spec/Core exact `47053f798bae152f676e9ff4be22ca4c6c06a6a8`: Core Focused `34716645679 = SUCCESS`; canonical Quality `34716645678 = SUCCESS`.
- Backend exact `c40be5764e600fe961bc3aeaf39c17f91100e34f`: Backend Focused `34717283972 = SUCCESS`; Storage Focused `34717283988 = SUCCESS`; canonical Quality `34717283963 = SUCCESS`.
- UI exact `8b38c1a501789cbfb7c76b1ee1acef999270fa13`: UI Focused `34717682781 = SUCCESS`; canonical Quality `34717682751 = SUCCESS`; Core Focused `34717682759 = FAILURE` with exact diagnostics `2 skipped` because both selected files require missing `PySide6`.
- Current Develop `core-focused-candidate.yml` still selects every changed `tests/unit/test_*.py` for focused pytest while installing only `--extra dev`; `ERR-0046` therefore remains current.
- Integrator confirms current Develop contains bounded Backend startup-identity hardening and its tests; no guard relaxation.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current state

- OPEN: `ERR-0046`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: `ERR-0042`, `ERR-0043`, `ERR-0045`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`, `ERR-0031`, `ERR-0032`, `ERR-0033`, `ERR-0034`, `ERR-0035`, `ERR-0036`, `ERR-0037`, `ERR-0040`, `ERR-0041`, `ERR-0044`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`, `ERR-0038`, `ERR-0039`.
- BLOCKED: none at top level.

## ERR-0046 — Core Focused harness selects UI unit tests without UI runtime

- Severity: P2 CI/harness integration blocker.
- Status: `OPEN`.
- Newest exact reproducer: Core Focused Candidate `34717682759` on `postmerge/ui@8b38c1a501789cbfb7c76b1ee1acef999270fa13`.
- Exact diagnostics: Ruff `All checks passed!`; focused pytest selects only `tests/unit/test_pathena_comfyui_shell.py` and `tests/unit/test_pathena_pallas_full_view.py`; both are skipped at collection because `PySide6` is absent; final outcome gate correctly refuses success.
- Same exact UI SHA is healthy in its owner/canonical lanes: UI Focused `34717682781 = SUCCESS`, canonical `34717682751 = SUCCESS`. This deduplicates the red Core lane away from UI product code.
- Current Develop workflow still performs `git diff ... tests/unit/*.py` followed by `Where-Object { $_ -match '^tests/unit/test_.*\\.py$' }`, despite workflow triggers being Core-specific patterns. Root cause therefore remains current in the harness.
- Safe repair: make focused pytest selection mirror explicit Core ownership patterns (`claim*`, `knowledge*`, `concept_note*`, `identity_transition*`, `temporal*`) or another explicit Core allowlist. Preserve `--diff-filter=ACMR`, tracked-worktree fail-closed remediation, and final outcome enforcement. Never convert skipped-only execution into success.
- Closure requirement: exact candidate proving UI-only changed tests are not spuriously selected, plus a negative control showing a genuine Core failing test still fails, then integrated canonical success.

## ERR-0045 — Backend absent-sidecar test fixture recreates WAL/SHM during read-only preflight

- Severity: P2 Storage test/harness integration blocker.
- Status: `FIXED_PENDING_VERIFY`.
- Owner repair lineage `365df03a040cb9dffddf6f942ae61a2cdb8dc375` is superseded by synchronized Backend exact `c40be5764e600fe961bc3aeaf39c17f91100e34f` with Backend Focused `34717283972 = SUCCESS`, Storage Focused `34717283988 = SUCCESS`, canonical `34717283963 = SUCCESS`.
- Integrator has copied the bounded storage startup-identity test/product delta into Develop `915668a376390d86fb333291f555eb804dfa4358`.
- No Storage/Recovery guard was relaxed.
- Final closure requirement: Develop canonical `34718446158@915668a... = SUCCESS` before `FIXED`.

## ERR-0043 — Backend SQLite startup revalidation accepts foreign sidecar replacement

- Severity: P1 Storage/release integration blocker.
- Status: `FIXED_PENDING_VERIFY`.
- Product repair remains fail-closed: only complete absent-both -> published-both WAL+SHM transition for unchanged primary identity may be accepted, followed by fresh exact-identity confirmation; partial or foreign replacement remains rejected.
- Synchronized Backend exact `c40be5764e600fe961bc3aeaf39c17f91100e34f` is fully green in Backend Focused, Storage Focused and canonical Quality.
- Integrator explicitly incorporated this bounded startup-identity hardening into Develop `915668a376390d86fb333291f555eb804dfa4358`.
- Final closure requirement: Develop canonical `34718446158@915668a... = SUCCESS` before `FIXED`.

## ERR-0042 — Spec/Core Ruff blocker in revision-change slice

- Severity: P1 integration blocker.
- Status: `FIXED_PENDING_VERIFY`.
- Historical exact reproducer: `postmerge/spec-core@9f2052b9c10668ad9eeeb2857dbcbb25145cc832`, one Ruff `I001` in `tests/unit/test_revision_change_explanation.py` while six focused behavior tests passed.
- Owner repair: `postmerge/spec-core@47053f798bae152f676e9ff4be22ca4c6c06a6a8` (`fix(core): normalize revision explanation test import block`).
- Exact owner verification: Core Focused `34716645679 = SUCCESS`; canonical Quality `34716645678 = SUCCESS` on the unchanged SHA.
- No current evidence that this repair is integrated into Develop `915668a...`; therefore not `FIXED` yet.
- Final closure requirement: integrate the verified Spec/Core repair and require canonical success on the resulting exact Develop SHA.

## ERR-0044 — Core Focused harness selects deleted files from PR diff

- Severity: P2 CI/harness integration blocker.
- Status: `FIXED`.
- Repair uses `git diff --diff-filter=ACMR --name-only` and tracked-worktree fail-closed remediation.
- Integrated verification: canonical `34710920451@b8afe9661387c4a1a3d65f539c39ca772f37329c = SUCCESS`.

## ERR-0041 / ERR-0040 / ERR-0035 / ERR-0033

All remain `FIXED` with previously recorded integrated exact-SHA canonical success. Historical closed signatures are not reopened without current exact-SHA reproduction.

## ERR-0039 / ERR-0038

Both remain `STALE`; reopen only with a new current exact-SHA reproduction.

## Persistent release guards

Historical closed/stale clusters remain unchanged. Reopen only with current exact-SHA reproduction. Persistent guards remain binding: Windows `pypdf` packaging; fail-closed Frozen argv; separate Desktop/Worker EXEs; exactly one Desktop with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock `PermissionError` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError`; duplicate-column/Core-startup/storage-bootstrap signatures. Before Beta/release promotion, execute the known-crash regression matrix on the exact candidate SHA. No promotion-ready claim while a known crash signature or removed guard is current.
