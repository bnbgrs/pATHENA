# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

- Stable IDs use `ERR-####`.
- Only failures reproduced or evidenced on the stated SHA are opened.
- Historical failures are not carried forward unless their signature recurs on the current baseline.
- Cascades are deduplicated under their primary root cause.
- `FIXED` requires observed verification; unverified fixes remain `FIXED_PENDING_VERIFY`.
- Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`.

## Current baseline

- Baseline branch: `develop/pathena-next`
- Baseline SHA: `3347f766651a9b6e2a03235eca4add7905ad4527`
- Stable read-only parent: `main` at `0d4d621f8a38ddf8eccfa09622bf193687619943`
- Worker branch: `postmerge/errors`
- Worker was fast-forward synchronized NON-FORCE to exact current Develop before mutation.

## Current error state

- OPEN: none.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: `ERR-0003`.
- FIXED: `ERR-0001`, `ERR-0002`.
- BLOCKED: none.

## Current scan

- Backend canonical Quality run `33755878184` on `a4768d9b0ea57a1161c93f603a5101c28b555276` completed `failure`: specification validator, Ruff, mypy, Windows path safety, Linux storage regressions and Local install smoke passed; only full pytest failed.
- Downloaded canonical diagnostics artifact `9894914799` shows exactly two failures: `tests/unit/test_pathena_window.py::test_reference_body_directly_owns_workspace_and_persistent_inspector` and `tests/unit/test_pathena_window.py::test_reference_inspector_is_persistent_and_composer_action_is_compact`; total result `2 failed, 4488 passed, 3 skipped, 2 warnings`.
- Both failures assert that the Workspace inspector is permanently visible. The failing Backend lineage and current Develop contain identical `src/athena/desktop/pathena_window.py` blob `b683903cc6e6a1a99950bba168e6e314df545ca1` and identical stale `tests/unit/test_pathena_window.py` blob `950f868e2e396bab5711bda147a124458c69cc34`, so this signature applies to current Develop rather than being historical-only.
- `UI-GAP-0002` is authoritative product evidence that the inspector is intentionally context-sensitive. Product commit `177bef4dcdb4956f1df75bfcce9ee10c7a4bd1e2` and test-contract commit `1685221150c724deceb5d150a4d2dcff2bdd867b` were canonical green on exact UI head `ce959e148ddbe8f13952ca56f7d07e7a7ce1addb` in run `33745885426`; the Visual Gap Ledger marks the contextual inspector contract `FIXED` and integrated.
- Error-worker harness correction `ebcf0dc2a305e946aabd0309c95316d29a1ebd91` updates only the two stale shell assertions/names to the already verified contextual contract and adds an explicit non-Workspace visibility assertion. No product code or guard was changed.
- Local focused execution could not be performed because the execution container could not resolve `github.com`; no PASS claim is made for `ebcf0dc...`. `ERR-0003` therefore remains `FIXED_PENDING_VERIFY`.

## Entries

### ERR-0001 — Deletion-ledger mutation/cursor boundaries accept malformed runtime types

- first_seen: 2026-09-03
- last_seen: 2026-09-03
- checked_sha: `58dbd4d80bc61c4cc8e9cd6d61adaa5b311ea4c3`
- severity: P2
- area: Storage / Persistence / Deletion Ledger / Recovery boundary
- status: `FIXED`
- exact evidence:
  - Product fix `780d25d74ce2e310b6a4bc434f547a23163e8b78` is integrated into Develop.
  - Canonical Backend run `33749788522` passed all 22 deletion-boundary tests plus validator, Ruff, mypy, Windows path safety, Linux storage and local-install smoke on the exact integrated product/test content.
  - That run's only full-pytest failure was independently identified as UI/PALLAS and later fixed/verifiably green before bounded integration.
- reproducible path before fix: malformed entity/runtime integer boundaries could cross validation before SQL because Python `bool` is an `int` subclass and annotations did not enforce runtime types.
- primary root cause: deletion-ledger APIs lacked explicit bool-safe fail-before-SQL runtime validation.
- affected files: `src/athena/lifecycle/deletion.py`; `tests/unit/test_deletion_ledger_boundaries.py`.
- fix_commit: `780d25d74ce2e310b6a4bc434f547a23163e8b78`; harness correction `2f705d5e0fc1c77dd60612b5aeaa16d9380e46cd`.
- verification executed: 22 focused boundary tests PASS inside canonical Backend run `33749788522`; validator/Ruff/mypy/Windows/Linux-storage/local-install PASS.
- remaining risks: none for this signature absent recurrence.
- integrator handoff: no action required.

### ERR-0002 — Backend deletion-boundary test import block failed canonical Ruff I001

- first_seen: 2026-09-03
- last_seen: 2026-09-03
- checked_sha: `58dbd4d80bc61c4cc8e9cd6d61adaa5b311ea4c3`
- severity: P2
- area: Quality / Python lint / Storage boundary test harness
- status: `FIXED`
- exact evidence: canonical Ruff failure in `33744816398`, import-format-only correction `2f705d5e0fc1c77dd60612b5aeaa16d9380e46cd`, canonical Ruff PASS in `33749788522`.
- reproducible path: canonical Ruff on the previous Backend lineage reproduced I001.
- primary root cause: import ordering/formatting defect in `tests/unit/test_deletion_ledger_boundaries.py`.
- affected files: `tests/unit/test_deletion_ledger_boundaries.py` only.
- fix_commit: `2f705d5e0fc1c77dd60612b5aeaa16d9380e46cd`.
- verification executed: canonical Ruff PASS in run `33749788522`.
- remaining risks: none for this signature.
- integrator handoff: no action required.

### ERR-0003 — Shell tests retain obsolete permanently-visible inspector contract

- first_seen: 2026-09-03
- last_seen: 2026-09-03
- checked_sha: `3347f766651a9b6e2a03235eca4add7905ad4527`
- severity: P1
- area: Qt/Desktop / UI contract harness / contextual Evidence & Activity inspector
- status: `FIXED_PENDING_VERIFY`
- exact evidence:
  - Canonical Backend Quality run `33755878184` on `a4768d9b0ea57a1161c93f603a5101c28b555276` completed failure only at `Quality — pytest`; all other canonical jobs/checks passed.
  - Diagnostics artifact `9894914799` records exactly two failures in `tests/unit/test_pathena_window.py`: `test_reference_body_directly_owns_workspace_and_persistent_inspector` at line 97 and `test_reference_inspector_is_persistent_and_composer_action_is_compact` at line 136, both `assert not inspector.isHidden()` while the inspector is hidden on an ungrounded Workspace.
  - Full pytest summary: `2 failed, 4488 passed, 3 skipped, 2 warnings`.
  - Current Develop has the exact same product blob `b683903cc6e6a1a99950bba168e6e314df545ca1` and stale test blob `950f868e2e396bab5711bda147a124458c69cc34` as the failing lineage, establishing current-baseline applicability.
  - `docs/ui/VISUAL_GAP_LEDGER.md` defines `UI-GAP-0002`: inspector must be context-sensitive, not permanently visible; its corrected UI lineage passed canonical Quality run `33745885426`.
- reproducible path:
  1. Construct `PathenaMainWindow` on Workspace with no grounded context.
  2. `_sync_inspector_visibility()` evaluates `navigation.currentRow() == 0` and no visible context button, so the inspector is intentionally hidden.
  3. Two stale shell tests still assert permanent visibility and fail.
- primary root cause: integration retained old `test_pathena_window.py` assertions after the verified `UI-GAP-0002` product contract changed to contextual inspector visibility. This is test-harness/contract drift, not a product visibility regression.
- affected files: `tests/unit/test_pathena_window.py` only for this correction; product reference is `src/athena/desktop/pathena_window.py` but remains unchanged.
- fix_commit: `ebcf0dc2a305e946aabd0309c95316d29a1ebd91`.
- verification executed: pre-fix failure reproduced by canonical diagnostics on an exact product+test blob pair identical to current Develop; corrected assertions have not yet had an executable focused/canonical run because the local container cannot resolve GitHub and no Error-branch workflow run exists yet.
- remaining risks: exact corrected-head focused/canonical verification still required. The stderr also contains Qt lifecycle noise involving deleted `QProcess` objects, but it did not create an additional pytest failure in this run; do not allocate another ERR-ID without a reproducible failing signature.
- integrator handoff: do not integrate as `FIXED` yet. Verify `tests/unit/test_pathena_window.py` plus `tests/unit/test_pathena_ui_presentation.py`; if green, run the smallest relevant Qt regression set and promote ERR-0003 to `FIXED` before integration.

## Historical/stale evidence

Historical pre-consolidation and recovery/platform-parity failures remain stale unless their signature recurs on current `develop/pathena-next`.
