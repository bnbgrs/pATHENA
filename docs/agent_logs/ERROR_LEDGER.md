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
- Baseline SHA: `1dc2da1bd38e6147d01d3b1d6833ea1ea6a0e37b`
- Stable read-only parent: `main` at `0d4d621f8a38ddf8eccfa09622bf193687619943`
- Worker branch: `postmerge/errors`
- Worker fast-forwarded NON-FORCE to exact current Develop before this scan because its previous head `39db19165bcf4f7e2d587a368e3f8ef93a5ae7cb` was an ancestor of Develop with no divergence.

## Current error state

- OPEN: none.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001`, `ERR-0002`, `ERR-0003`.
- BLOCKED: none.

## Current scan

- Exact baseline `1dc2da1bd38e6147d01d3b1d6833ea1ea6a0e37b` currently has no commit-status checks and no SHA-bound workflow run returned by the repository connector; no exact-head global PASS is claimed.
- Comparing previous Error head `39db19165bcf4f7e2d587a368e3f8ef93a5ae7cb` to current Develop shows only `docs/agent_handoffs/integrator.md` and `docs/development/ALPHA_BETA_PROGRESS.md` changed. No product, test, packaging, storage, runtime, provider, Windows or Qt file changed in that delta.
- The branch-level Develop workflow history inspected this run contains successful canonical Quality runs on earlier Develop SHAs; no fresh failure signature was evidenced for the current baseline.
- Backend canonical Quality run `33755878184` on `a4768d9b0ea57a1161c93f603a5101c28b555276` completed `failure`: specification validator, Ruff, mypy, Windows path safety, Linux storage regressions and Local install smoke passed; only full pytest failed.
- Diagnostics artifact `9894914799` shows exactly two failures: `tests/unit/test_pathena_window.py::test_reference_body_directly_owns_workspace_and_persistent_inspector` and `tests/unit/test_pathena_window.py::test_reference_inspector_is_persistent_and_composer_action_is_compact`; total result `2 failed, 4488 passed, 3 skipped, 2 warnings`.
- Both failures assert that the Workspace inspector is permanently visible. The failing Backend lineage and current Develop use product blob `src/athena/desktop/pathena_window.py@b683903cc6e6a1a99950bba168e6e314df545ca1`; `UI-GAP-0002` establishes the intended contextual inspector contract.
- Root-cause fix commit `6253577227d427c9bb00707c3e3e578a16c0f9d6` restores the exact canonical-green `tests/unit/test_pathena_window.py` blob `82f492814250536dd003857a4eec2d083e9e13d5` from UI head `ce959e148ddbe8f13952ca56f7d07e7a7ce1addb` rather than weakening coverage.
- Canonical Quality run `33745885426` on exact UI head `ce959e148ddbe8f13952ca56f7d07e7a7ce1addb` completed `success`. This remains observed exact-content verification for the affected product and focused Qt/UI harness blobs.
- Qt deleted-`QProcess` stderr remains a warning signal only because it has not produced a reproducible current-lineage failure; no new ERR-ID is allocated without failure evidence.
- Backend currently owns the independently identified ExternalAccessGateway runtime-boundary hardening work; Error does not duplicate that root cause unless it manifests as a confirmed current-lineage failure.

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
- checked_sha: `1dc2da1bd38e6147d01d3b1d6833ea1ea6a0e37b`
- severity: P1
- area: Qt/Desktop / UI contract harness / contextual Evidence & Activity inspector
- status: `FIXED`
- exact evidence:
  - Canonical Backend Quality run `33755878184` failed only at full pytest with the two stale persistent-inspector assertions; all other canonical jobs/checks passed.
  - Diagnostics artifact `9894914799` records exactly `2 failed, 4488 passed, 3 skipped, 2 warnings`.
  - `docs/ui/VISUAL_GAP_LEDGER.md` defines `UI-GAP-0002`: inspector is context-sensitive rather than permanently visible.
  - Fix commit `6253577227d427c9bb00707c3e3e578a16c0f9d6` restores exact known-green shell-test blob `tests/unit/test_pathena_window.py@82f492814250536dd003857a4eec2d083e9e13d5`, including Workspace-hidden, context/non-Chat-visible, reset-hidden and return-to-Workspace-hidden state transitions.
  - Relevant companion suite remains exact known-green blob `tests/unit/test_pathena_ui_presentation.py@171f209728831feb1ac7bb06172e30aee12973ae`.
  - These exact affected product/test blobs match UI head `ce959e148ddbe8f13952ca56f7d07e7a7ce1addb`, whose canonical Quality run `33745885426` completed `success`.
  - Current Develop differs from the verified Error lineage only in Integrator/Alpha-Beta documentation, so the fixed affected blobs remain unchanged on the current baseline.
- reproducible path before fix:
  1. Construct `PathenaMainWindow` on Workspace with no grounded context.
  2. `_sync_inspector_visibility()` hides the inspector because `navigation.currentRow() == 0` and no context is available.
  3. The stale integrated shell tests asserted permanent visibility and failed.
- primary root cause: integration retained obsolete `test_pathena_window.py` coverage after the verified `UI-GAP-0002` product contract changed to contextual inspector visibility. This is test-harness/contract drift, not a product visibility regression.
- affected files: `tests/unit/test_pathena_window.py`; product reference `src/athena/desktop/pathena_window.py` unchanged.
- fix_commit: `6253577227d427c9bb00707c3e3e578a16c0f9d6`.
- verification executed: canonical Quality run `33745885426` PASS on byte-identical affected product and focused harness blobs; current baseline delta from verified Error lineage is documentation-only. No exact-current-head global Quality PASS is claimed.
- remaining risks: Qt deleted-`QProcess` stderr remains scan-only until reproducible failure evidence appears.
- integrator handoff: already integrated into Develop; preserve the contextual-inspector test contract in future UI changes.

## Historical/stale evidence

Historical pre-consolidation and recovery/platform-parity failures remain stale unless their signature recurs on current `develop/pathena-next`.
