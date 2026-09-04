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
- Baseline SHA: `da34f14284cd61eb0e23b4dc2ac1d7757b2b2e5a`
- Worker branch: `postmerge/errors`
- History-preserving NON-FORCE synchronization merge: `20154f0a7db41c68d7e1b71c2a86c2a6732dd15a`.

## Current error state

- OPEN: none.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: `ERR-0008`.
- FIXED: `ERR-0001` through `ERR-0007`.
- BLOCKED: none.

## Current scan

- UI Quality `33845676401` on `5a77a4841dfdda120afaefccb698319d31a7d9e9` completed `failure` with Windows path safety, Linux storage, local-install smoke, validator, Ruff and mypy PASS; only full pytest and canonical enforcement failed.
- UI owner correction `f7da16e05aa50da9ca17e5069a8880a84e34432e` changes only `tests/unit/test_pathena_settings_runtime.py`, installing `apply_ui_refinements_5001_5100(window)` before asserting the `pathenaSettingsComprehensionController` state.
- Exact corrected Quality `33845743958` is still in progress; therefore no canonical PASS/FIXED claim is made.

## Entries

### ERR-0001 — Deletion-ledger malformed runtime boundaries
- severity: P2
- status: `FIXED`
- evidence: canonical Backend `33749788522`.
- root_cause: bool-safe/runtime validation missing before SQL mutation/cursor boundaries.
- fix_sha: `780d25d74ce2e310b6a4bc434f547a23163e8b78` plus harness `2f705d5e0fc1c77dd60612b5aeaa16d9380e46cd`.

### ERR-0002 — Deletion-boundary harness Ruff I001
- severity: P2
- status: `FIXED`
- evidence: Ruff failure `33744816398`; Ruff PASS `33749788522`.
- root_cause: import ordering/formatting in `tests/unit/test_deletion_ledger_boundaries.py`.
- fix_sha: `2f705d5e0fc1c77dd60612b5aeaa16d9380e46cd`.

### ERR-0003 — Stale permanent-inspector harness contract
- severity: P1
- status: `FIXED`
- evidence: Backend `33755878184`; canonical UI `33745885426` passed byte-identical relevant product/harness blobs.
- root_cause: test contract lagged contextual `Evidence & Activity` inspector behavior.
- fix_sha: `6253577227d427c9bb00707c3e3e578a16c0f9d6`.

### ERR-0004 — Startup/readiness harness canonical Ruff regressions
- severity: P2
- status: `FIXED`
- evidence: `33785726577` B010; `33792012599` I001; exact-head `33804193396` SUCCESS.
- root_cause: bounded startup/readiness test-harness lint defects.
- fix_sha: `77e7b4c7d95202e6814226e2b4a2c4a54e3f5c8e`, `a5d9530525bd0b6bf0eae3945c23a6805f6b9669`.

### ERR-0005 — System-tray QApplication ownership typing
- severity: P2
- status: `FIXED`
- evidence: UI `33822842314` mypy failure; corrected `33822861477` SUCCESS.
- root_cause: typed `self.app` assignment occurred before runtime `QApplication` narrowing.
- fix_sha: `72e43bc18c28b5c92f6528919abf788f66924ba9`.

### ERR-0006 — Research UUID filter container boundary is not runtime-safe
- severity: P2
- status: `FIXED`
- evidence: Backend `33833499697`; repaired-lineage `33838658964` SUCCESS.
- root_cause: static `Sequence[uuid.UUID]` annotation was trusted at runtime without explicit container validation.
- fix_sha: `462fba22637e0083c87df32f987134ce0fb3de00`; integrated equivalent `4b390b4fcc39affc1884f304f460901d07ea622a`.

### ERR-0007 — Missing contradiction-review dependency breaks integrated Core import graph
- severity: P1
- status: `FIXED`
- evidence: post-integration `33838377083`; repaired-lineage `33838658964` SUCCESS.
- root_cause: Core integration carried `acceptance_service.py` without required `contradiction_review_gate.py`.
- fix_sha: `05bca268e2d2fc8e5b0f5ae59c564f2403605540`.

### ERR-0008 — Settings runtime harness asserts comprehension state before installing comprehension layer
- first_seen: 2026-09-04
- severity: P2
- area: Qt/Desktop / Settings / test harness
- status: `FIXED_PENDING_VERIFY`
- checked_sha: failing UI `5a77a4841dfdda120afaefccb698319d31a7d9e9`; owner correction `f7da16e05aa50da9ca17e5069a8880a84e34432e`.
- evidence: canonical UI Quality `33845676401` failed only `Quality — pytest` plus canonical enforcement; Windows path safety, Linux storage, local-install smoke, validator, Ruff and mypy all passed.
- repro: `tests/unit/test_pathena_settings_runtime.py::test_runtime_panel_never_turns_stale_or_missing_provider_into_ready` obtains `pathenaSettingsComprehensionController` immediately after `install_settings_runtime(...)`, although that controller belongs to the separately installed `apply_ui_refinements_5001_5100(...)` layer.
- root_cause: harness setup ordering omitted installation of the Settings comprehension layer before asserting its controller state; this is a harness defect, not a product runtime regression.
- files: `tests/unit/test_pathena_settings_runtime.py`; product code unchanged by owner fix.
- fix_sha: `f7da16e05aa50da9ca17e5069a8880a84e34432e`.
- verification: exact corrected canonical Quality `33845743958` is `in_progress`; no FIXED claim until full pytest and canonical enforcement complete successfully.
- risk: low; correction changes test setup only and does not weaken assertions or guards.
- integrator_handoff: reject failing SHA `5a77a4841dfdda120afaefccb698319d31a7d9e9`; retain corrected candidate `f7da16e05aa50da9ca17e5069a8880a84e34432e` pending exact-head canonical completion.

## Historical/stale evidence

Historical pre-consolidation/recovery/platform-parity failures remain stale unless their exact signature recurs on current `develop/pathena-next`.
