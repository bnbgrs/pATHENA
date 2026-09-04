# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

- Stable IDs use `ERR-####`.
- Only reproduced or exact-SHA evidenced failures are opened.
- Cascades are deduplicated under the primary root cause.
- `FIXED` requires observed verification; unverified corrections remain `FIXED_PENDING_VERIFY`.
- Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`.
- `main` and `bnbgrs/ATHENA` remain read-only.

## Current baseline

- Baseline branch: `develop/pathena-next`
- Baseline SHA: `5522e73c6f314b1dfac77fa5cfdb8e8d6f667704`
- Stable read-only parent: `main@0d4d621f8a38ddf8eccfa09622bf193687619943`
- Worker branch: `postmerge/errors`
- History-preserving NON-FORCE synchronization merge: `0fea7636ed7e2c2fac8a95851c836fe037b27767`.

## Current error state

- OPEN: none.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: `ERR-0006`, `ERR-0007`.
- FIXED: `ERR-0001`, `ERR-0002`, `ERR-0003`, `ERR-0004`, `ERR-0005`.
- BLOCKED: none.

## Current scan

- Research UUID correction `462fba22637e0083c87df32f987134ce0fb3de00` is now integrated on Develop as equivalent reviewed blobs in `4b390b4fcc39affc1884f304f460901d07ea622a`. Focused verifier `33833496929` is green; exact combined canonical verification remains pending, so `ERR-0006` is not yet `FIXED`.
- Post-integration canonical validation `33838377083` exposed a distinct integration defect: `src/athena/knowledge/acceptance_service.py` imported `athena.knowledge.contradiction_review_gate`, but the dependency module was absent from Develop. This produced `ModuleNotFoundError` and a 131-error pytest collection cascade, with mypy/local-install/API-runtime regressions failing from the same missing dependency.
- The missing dependency was restored from exact previously canonical-green Core blob `95866345cfa5fd2727bdb01c60ec4b2a60660707` into Develop commit `05bca268e2d2fc8e5b0f5ae59c564f2403605540`. No unrelated product/test/guard change was bundled.
- Canonical validation `33838658964` on the repaired product lineage is in progress. Local install smoke, Windows path safety, Linux storage, specification validator, Ruff and mypy are already PASS; full pytest/canonical enforcement remain pending. Therefore `ERR-0007` is `FIXED_PENDING_VERIFY`.

## Entries

### ERR-0001 — Deletion-ledger malformed runtime boundaries
- first_seen: 2026-09-03
- severity: P2
- area: Storage / Persistence / Recovery boundary
- status: `FIXED`
- evidence: canonical Backend `33749788522`.
- root_cause: bool-safe/runtime validation missing before SQL mutation/cursor boundaries.
- files: `src/athena/lifecycle/deletion.py`; `tests/unit/test_deletion_ledger_boundaries.py`.
- fix_sha: `780d25d74ce2e310b6a4bc434f547a23163e8b78` plus harness `2f705d5e0fc1c77dd60612b5aeaa16d9380e46cd`.
- verification: focused boundary tests, validator, Ruff, mypy, Windows/Linux-storage/local-install PASS.
- risk: none absent recurrence.
- integrator_handoff: cleared.

### ERR-0002 — Deletion-boundary harness Ruff I001
- first_seen: 2026-09-03
- severity: P2
- area: Quality / Python lint
- status: `FIXED`
- evidence: Ruff failure `33744816398`; Ruff PASS `33749788522`.
- root_cause: import ordering/formatting in `tests/unit/test_deletion_ledger_boundaries.py`.
- files: `tests/unit/test_deletion_ledger_boundaries.py`.
- fix_sha: `2f705d5e0fc1c77dd60612b5aeaa16d9380e46cd`.
- verification: canonical Ruff PASS.
- risk: none absent recurrence.
- integrator_handoff: cleared.

### ERR-0003 — Stale permanent-inspector harness contract
- first_seen: 2026-09-03
- severity: P1
- area: Qt/Desktop / UI contract harness
- status: `FIXED`
- evidence: Backend `33755878184` failed two stale inspector assertions; canonical UI `33745885426` passed byte-identical relevant product/harness blobs.
- root_cause: test contract lagged contextual `Evidence & Activity` inspector behavior.
- files: `tests/unit/test_pathena_window.py`; product reference `src/athena/desktop/pathena_window.py` unchanged.
- fix_sha: `6253577227d427c9bb00707c3e3e578a16c0f9d6`.
- verification: canonical exact-content PASS.
- risk: none absent recurrence.
- integrator_handoff: cleared.

### ERR-0004 — Startup/readiness harness canonical Ruff regressions
- first_seen: 2026-09-03
- severity: P2
- area: Qt/Desktop / startup-readiness harness / Ruff
- status: `FIXED`
- evidence: `33785726577` exposed B010; `33792012599` exposed residual I001; exact-head `33804193396` completed SUCCESS.
- root_cause: bounded test-harness lint defects, not runtime behavior.
- files: `tests/unit/test_pathena_startup_experience_2900.py`.
- fix_sha: B010 `77e7b4c7d95202e6814226e2b4a2c4a54e3f5c8e`; I001 `a5d9530525bd0b6bf0eae3945c23a6805f6b9669`.
- verification: Windows path safety, Linux storage, local-install, validator, Ruff, mypy, full pytest, canonical enforcement PASS.
- risk: none absent recurrence.
- integrator_handoff: cleared.

### ERR-0005 — System-tray QApplication ownership typing
- first_seen: 2026-09-04
- severity: P2
- area: Qt/Desktop / system tray / mypy
- status: `FIXED`
- evidence: canonical UI `33822842314` failed mypy only; corrected exact-head `33822861477` completed SUCCESS.
- root_cause: typed `self.app` assignment occurred before runtime `QApplication` narrowing.
- files: `src/athena/desktop/pathena_system_tray.py`.
- fix_sha: `72e43bc18c28b5c92f6528919abf788f66924ba9`.
- verification: all canonical stages PASS.
- risk: none absent recurrence.
- integrator_handoff: cleared.

### ERR-0006 — Research UUID filter container boundary is not runtime-safe
- first_seen: 2026-09-04
- severity: P2
- area: Research / Jobs / runtime validation / API boundary
- status: `FIXED_PENDING_VERIFY`
- evidence: Backend canonical `33833499697` on `24775cd9b6dd621a1cde188a376a3926c3c062b2` failed API runtime boundary/local-install/mypy/pytest; focused verifier `33833496929` passed.
- repro: scalar text-like or non-Sequence values could cross `_stable_uuids()` normalization instead of failing closed.
- root_cause: static `Sequence[uuid.UUID]` annotation was trusted at runtime without explicit container validation.
- files: `src/athena/research/service.py`; `tests/unit/test_research_stable_strings_boundaries.py`.
- fix_sha: owner fix `462fba22637e0083c87df32f987134ce0fb3de00`; equivalent integrated blobs `4b390b4fcc39affc1884f304f460901d07ea622a`.
- verification: focused pytest/Ruff/mypy/diff-check PASS; combined canonical run `33838658964` still pending final pytest/enforcement.
- risk: do not claim global green until exact combined verification completes.
- integrator_handoff: retain integrated bounded slice; close only after canonical PASS.

### ERR-0007 — Missing contradiction-review dependency breaks integrated Core import graph
- first_seen: 2026-09-04
- severity: P1
- area: Core / Knowledge / application composition / integration dependency
- status: `FIXED_PENDING_VERIFY`
- checked_sha: pre-repair integrated lineage validated by run `33838377083`; repair lineage `05bca268e2d2fc8e5b0f5ae59c564f2403605540`.
- evidence: post-integration Quality `33838377083` produced `ModuleNotFoundError: No module named 'athena.knowledge.contradiction_review_gate'`; pytest collection cascaded to 131 errors, with mypy, local-install and API-runtime checks failing from the same absent module.
- repro: import `athena.knowledge.acceptance_service` on the defective integrated lineage; its direct import of `athena.knowledge.contradiction_review_gate` cannot resolve.
- root_cause: earlier Core integration carried `acceptance_service.py` without its required contradiction-review module dependency. This is an integration omission, not a Research UUID regression.
- files: missing `src/athena/knowledge/contradiction_review_gate.py`; importer `src/athena/knowledge/acceptance_service.py` unchanged by repair.
- fix_sha: `05bca268e2d2fc8e5b0f5ae59c564f2403605540`, restoring exact blob `95866345cfa5fd2727bdb01c60ec4b2a60660707` from canonical-green Core head `a20dbe70824d5fc07bdd1d981e3acf431554877a` / Quality `33826094843`.
- verification: current combined run `33838658964` has Local install smoke, Windows path safety, Linux storage, validator, Ruff and mypy PASS; full pytest and canonical enforcement are still pending.
- risk: no `FIXED` claim until `33838658964` completes successfully.
- integrator_handoff: repair is already on Develop; retain it and treat ERR-0007 as blocker only if final combined validation fails.

## Historical/stale evidence

Historical pre-consolidation/recovery/platform-parity failures remain stale unless their exact signature recurs on current `develop/pathena-next`.
