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
- Baseline SHA: `dd4b623cc7bbc5b5a24c4427382f0b98ff50ad02`
- Stable read-only parent: `main` at `0d4d621f8a38ddf8eccfa09622bf193687619943`
- Worker branch: `postmerge/errors`
- Worker synchronized history-preservingly and NON-FORCE with current Develop in merge `7afa39e6fd3bf519e32259b26398b6bed884a28c`; prior Error head `757827e2e5b7ed08dd2367645f94ee32f3063781` and current Develop were retained as parents.

## Current error state

- OPEN: `ERR-0004`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001`, `ERR-0002`, `ERR-0003`.
- BLOCKED: none.

## Current scan

- Current Develop SHA `dd4b623cc7bbc5b5a24c4427382f0b98ff50ad02` is an Integrator documentation commit over the prior product lineage; no new Develop product/test defect was evidenced this run.
- UI descendant `b76115748aed53e3502a71eef10a41b11f97f8ae` has canonical Quality run `33785726577` completed `failure`: Windows path safety PASS, Linux storage PASS, local-install smoke PASS, specification validator PASS, mypy PASS, full pytest PASS, Ruff FAIL.
- The UI delta adds a constant-name `setattr(window, "_core_transport_ready", False)` in `tests/unit/test_pathena_startup_experience_2900.py`; project Ruff config selects the full `B` family. This is the strongest isolated root-cause hypothesis for `ERR-0004`, but the exact Ruff annotation text was not retrievable through the repository connector, so the rule code is not asserted as verified.
- Qt deleted-`QProcess` stderr remains warning-only because no current-lineage failing path was reproduced.
- Backend owns ExternalAccessGateway runtime-boundary hardening; Core owns normal-Hybrid Search composition; UI owns UI-GAP-0004 product work. Error does not duplicate those product scopes.

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
- exact evidence: canonical Backend Quality run `33755878184` failed only at full pytest with the stale persistent-inspector assertions; fix commit `6253577227d427c9bb00707c3e3e578a16c0f9d6` restored the verified contextual-inspector harness contract; exact affected product/test blobs match UI head `ce959e148ddbe8f13952ca56f7d07e7a7ce1addb`, whose canonical Quality run `33745885426` succeeded.
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
- checked_sha: `b76115748aed53e3502a71eef10a41b11f97f8ae`
- severity: P2
- area: Quality / Python lint / Qt startup-readiness test harness
- status: `OPEN`
- exact evidence:
  - Canonical Quality run `33785726577` on UI descendant `b76115748aed53e3502a71eef10a41b11f97f8ae` completed `failure`.
  - In that run: Windows path safety PASS, Linux storage regressions PASS, local-install smoke PASS; Python-3.12 specification validator PASS, Ruff FAIL, mypy PASS, full pytest PASS.
  - Changed startup test `tests/unit/test_pathena_startup_experience_2900.py` contains `setattr(window, "_core_transport_ready", False)` with a constant attribute name.
  - `pyproject.toml` selects Ruff `B` rules in addition to E/F/I.
- reproducible path: run canonical Ruff on UI SHA `b76115748aed53e3502a71eef10a41b11f97f8ae`; the canonical job reproduces the failure before full pytest, while pytest itself remains green.
- primary root cause or hypothesis: likely a lint-only harness defect introduced by the constant-name `setattr` in the new startup-readiness test. Exact Ruff rule/annotation is pending retrieval or a local Ruff reproduction; do not treat the hypothesized rule code as verified yet.
- affected files: `tests/unit/test_pathena_startup_experience_2900.py`; no product file is currently implicated by the evidence.
- status: `OPEN`
- fix_commit: none.
- verification executed: canonical run `33785726577` confirms Ruff FAIL and all listed non-Ruff checks PASS; no fix verification yet.
- remaining risks: exact Ruff diagnostic text unavailable from current connector surface; avoid changing production code or weakening Ruff. UI currently owns this active test file, so Error will not create a competing mutation.
- integrator handoff: reject UI candidate until UI applies the minimal harness correction and reruns Ruff plus the focused startup/offline tests; Error can take over only if UI releases ownership or the defect persists independently.

## Historical/stale evidence

Historical pre-consolidation and recovery/platform-parity failures remain stale unless their signature recurs on current `develop/pathena-next`.
