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
- Baseline SHA: `a0e0a2bcf76b0e7f77bb3cd15b8c2ccf79d5c600`
- Worker branch: `postmerge/errors`
- History-preserving NON-FORCE synchronization merge: `ba80f4060ad4aac5ebf77bdcf09e0f23c77cc964`.

## Current error state

- OPEN: none.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0008`.
- BLOCKED: none.

## Current scan

- `ERR-0008` exact owner fix SHA `afa319f0ab1b12edccc4b649d4a1ca36bcd7ac39` now has canonical ATHENA Quality Gate `33854660676 = success`.
- Integrator independently carried the canonical-green Settings product/test blobs onto Develop and records UI-GAP-0008 as integrated without Provider, Security, Storage or network-capability changes.
- Therefore `ERR-0008` is now `FIXED`; no PASS was claimed before the exact run completed.
- Current Backend head `33933c00169ab72786b8b27b8286af6432225e8e` has Quality `33858608297` still in progress: Windows path safety PASS, Linux storage PASS, local-install smoke PASS, validator PASS, Ruff PASS, mypy PASS, pytest still running. No new ERR-ID is allocated without a concrete failing signature.

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

### ERR-0008 — Settings runtime/comprehension harness contract mismatch
- first_seen: 2026-09-04
- severity: P2
- area: Qt/Desktop / Settings / test harness
- status: `FIXED`
- checked_sha: failing UI `5a77a4841dfdda120afaefccb698319d31a7d9e9`; intermediate `f7da16e05aa50da9ca17e5069a8880a84e34432e`; repeated failing `e6cb967c354f55a1cbb4ca1a4bbd2ff26b863b90`; final fix `afa319f0ab1b12edccc4b649d4a1ca36bcd7ac39`.
- evidence: `33845743958` and `33849890354` isolated the stale Settings runtime assertion after platform/static gates passed. Exact final fix Quality `33854660676` completed `success`.
- repro before fix: after installing Settings comprehension/refinement and applying an unavailable provider snapshot while local Core remains `ok`, network scope is truthfully `loopback-only`; accessibility copy says `does not indicate Internet access`, while the stale harness expected `Internet-access state is not inferred`.
- root_cause: first owner correction exposed a second stale harness expectation. Product runtime and accessibility state were consistent; the harness lagged the truthful loopback-only contract.
- files: `tests/unit/test_pathena_settings_runtime.py`; product reference `src/athena/desktop/pathena_settings_comprehension_5100.py`.
- fix_sha: `afa319f0ab1b12edccc4b649d4a1ca36bcd7ac39`.
- verification: canonical ATHENA Quality Gate `33854660676 = success` on exact fix SHA. Integrator records byte-identical verified Settings product/test blobs integrated onto Develop.
- risk: low; the fix retains substantive accessibility/network non-inference coverage via loopback-specific wording plus `pathenaInternetStateInferred is False`.
- integrator_handoff: no remaining ERR-0008 blocker; reject earlier red SHAs as globally green and preserve the verified final blobs.

## Historical/stale evidence

Historical pre-consolidation/recovery/platform-parity failures remain stale unless their exact signature recurs on current `develop/pathena-next`.
