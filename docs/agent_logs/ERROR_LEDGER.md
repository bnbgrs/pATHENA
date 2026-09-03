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
- Baseline SHA: `a728668f046bf0d8b66724bb8004a1767bd5589f`
- Stable read-only parent: `main` at `0d4d621f8a38ddf8eccfa09622bf193687619943`
- Worker branch: `postmerge/errors`
- Worker synchronized history-preservingly and NON-FORCE with current Develop in merge `71a9fa36281ad60de650bd393b447e77fbe76e73`; prior Error head `bd88a8bd3d101d5f1be0dff8675049169109854a` and current Develop were retained as parents.

## Current error state

- OPEN: none.
- IN_PROGRESS: `ERR-0004`.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001`, `ERR-0002`, `ERR-0003`.
- BLOCKED: none.

## Current scan

- Current Develop `a728668f046bf0d8b66724bb8004a1767bd5589f` contains the verified Core normal-Hybrid and Backend ExternalAccessGateway integrations plus progress documentation. No new Develop product/test defect is evidenced by those integrated worker slices at this observation point.
- `ERR-0004` original canonical failure is exactly diagnosed as Ruff `B010` at `tests/unit/test_pathena_startup_experience_2900.py:61`: constant-name `setattr(window, "_core_transport_ready", False)`.
- UI correction `77e7b4c7d95202e6814226e2b4a2c4a54e3f5c8e` removed that B010 site using a test-only `_DisconnectedStartupWindow` contract.
- UI run `33792012599` then exposed Ruff `I001` on the startup harness. UI correction `ecbf44ddd0fb8c7428d4cca090834eca284b997e` reformatted the first `PySide6.QtWidgets` import block only; no product semantics, assertions, lint rules, storage/security/recovery invariants or accessibility behavior were changed.
- Current UI exact head is `d581a88dfb916f2ffb3e358d16d92d502139ce42`, with canonical Quality run `33797732276`. Exact-head evidence already shows Linux storage PASS, Windows path safety PASS, local-install smoke PASS, specification validator PASS, mypy PASS, but Ruff FAIL again; full pytest is still running. Therefore `ERR-0004` remains `IN_PROGRESS` and UI-GAP-0004 is not Integrator-ready.
- The exact current Ruff rule/message from `33797732276` is not yet retrievable because diagnostics upload follows completion of the still-running pytest step. No new `ERR-0005` is allocated until that exact diagnostic is available and deduplicated.
- Static inspection confirms `tests/unit/test_pathena_startup_experience_2900.py` now has a multiline `PySide6.QtWidgets` import plus the existing multi-name `athena.desktop.pathena_startup_experience_2900` import block. This confines current investigation to import-block formatting/order or another exact Ruff signature in the UI lineage, but no rule is asserted without the uploaded diagnostics.
- Qt deleted-`QProcess` stderr remains warning-only because no current-lineage failing path was reproduced.

## Entries

### ERR-0001 — Deletion-ledger mutation/cursor boundaries accept malformed runtime types

- first_seen: 2026-09-03
- last_seen: 2026-09-03
- checked_sha: `58dbd4d80bc61c4cc8e9cd6d61adaa5b311ea4c3`
- severity: P2
- area: Storage / Persistence / Deletion Ledger / Recovery boundary
- status: `FIXED`
- exact evidence: product fix `780d25d74ce2e310b6a4bc434f547a23163e8b78` integrated; canonical Backend run `33749788522` passed all 22 deletion-boundary tests plus validator, Ruff, mypy, Windows path safety, Linux storage and local-install smoke.
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
- checked_sha: `f76911dfef6530041d62fb6c2e0ddec242d64231`
- severity: P1
- area: Qt/Desktop / UI contract harness / contextual Evidence & Activity inspector
- status: `FIXED`
- exact evidence: canonical Backend Quality run `33755878184` failed only at full pytest with stale persistent-inspector assertions; fix commit `6253577227d427c9bb00707c3e3e578a16c0f9d6` restored the verified contextual-inspector harness contract; exact affected product/test blobs match UI head `ce959e148ddbe8f13952ca56f7d07e7a7ce1addb`, whose canonical Quality run `33745885426` succeeded.
- reproducible path before fix: construct `PathenaMainWindow` on Workspace without grounded context; `_sync_inspector_visibility()` correctly hides inspector; obsolete tests asserted permanent visibility.
- primary root cause: test-harness/contract drift after UI-GAP-0002 changed the inspector to contextual visibility.
- affected files: `tests/unit/test_pathena_window.py`; product reference `src/athena/desktop/pathena_window.py` unchanged.
- fix_commit: `6253577227d427c9bb00707c3e3e578a16c0f9d6`.
- verification executed: canonical Quality run `33745885426` PASS on byte-identical affected product and focused harness blobs.
- remaining risks: Qt deleted-`QProcess` stderr remains scan-only until reproducible failure evidence appears.
- integrator handoff: already integrated into Develop; preserve contextual-inspector behavior.

### ERR-0004 — UI startup/readiness harness fails canonical Ruff

- first_seen: 2026-09-03
- last_seen: 2026-09-03
- checked_sha: `d581a88dfb916f2ffb3e358d16d92d502139ce42`
- severity: P2
- area: Quality / Python lint / Qt startup-readiness test harness
- status: `IN_PROGRESS`
- exact evidence:
  - Canonical Quality `33785726577` on `b76115748aed53e3502a71eef10a41b11f97f8ae`: Ruff-only quality failure; Windows path safety, Linux storage, local-install smoke, validator, mypy and full pytest passed. Uploaded diagnostics identified `B010` at startup harness line 61.
  - UI B010 correction `77e7b4c7d95202e6814226e2b4a2c4a54e3f5c8e` removes constant-name `setattr` with a test-only disconnected-window type.
  - Next exact UI run `33792012599` exposed Ruff `I001`; correction `ecbf44ddd0fb8c7428d4cca090834eca284b997e` changed only the first PySide6 import from a single line to a multiline import.
  - Current exact UI head `d581a88dfb916f2ffb3e358d16d92d502139ce42` / run `33797732276`: Linux storage PASS, Windows path safety PASS, local-install smoke PASS, validator PASS, mypy PASS, Ruff FAIL again; pytest still in progress at the checked state.
- reproducible path: canonical Ruff on exact UI head `d581a88dfb916f2ffb3e358d16d92d502139ce42` reproduces a lint failure after both prior corrections.
- primary root cause: original B010 is verified corrected. I001 was the next exact known signature. The latest exact Ruff signature is pending diagnostics upload; current evidence shows the I001 correction was insufficient but does not justify claiming the exact rule/message yet.
- affected files: `tests/unit/test_pathena_startup_experience_2900.py` remains the active Python harness file; no production/runtime defect is implicated by current evidence.
- fix_commit: B010 correction `77e7b4c7d95202e6814226e2b4a2c4a54e3f5c8e`; attempted I001 correction `ecbf44ddd0fb8c7428d4cca090834eca284b997e`; no verified final fix yet.
- verification executed: exact-head canonical run `33797732276` already confirms platform/storage/install/validator/mypy green and Ruff still FAIL; pytest/diagnostics upload pending.
- remaining risks: consume exact diagnostics immediately after upload; deduplicate current rule under ERR-0004 unless it is demonstrably independent. UI owns the active harness file while the exact-head run is in progress.
- integrator handoff: keep UI-GAP-0004 rejected. Do not integrate `d581a88d...`. After run completion, use exact diagnostics to make one minimal import/harness correction and require exact-head Ruff + focused startup/offline tests before acceptance.

## Historical/stale evidence

Historical pre-consolidation and recovery/platform-parity failures remain stale unless their signature recurs on current `develop/pathena-next`.
