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
- Baseline SHA: `f886a63ea190cb8d8df202bfd6528a6ef22df317`
- Worker branch: `postmerge/errors`
- History-preserving NON-FORCE synchronization merge: `46dc6edfb1ce410be81520b426d26a3e66422c9c`.

## Current error state

- OPEN: none.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: `ERR-0008`.
- FIXED: `ERR-0001` through `ERR-0007`.
- BLOCKED: none.

## Current scan

- UI owner commit `afa319f0ab1b12edccc4b649d4a1ca36bcd7ac39` applies the exact bounded `ERR-0008` harness correction in `tests/unit/test_pathena_settings_runtime.py`: the stale generic accessibility substring is replaced with the existing truthful loopback-specific phrase `does not indicate Internet access`, and the test additionally asserts `pathenaInternetStateInferred is False`.
- The correction does not change product runtime behavior, remove the accessibility assertion, weaken network-scope semantics, or add a dummy success path.
- Canonical Quality run `33854660676` is bound to exact UI SHA `afa319f0ab1b12edccc4b649d4a1ca36bcd7ac39`.
- Observed completed jobs/stages so far: Windows path safety PASS, Linux storage PASS, local-install smoke PASS, specification validator PASS, Ruff PASS, mypy PASS. Full pytest remains IN_PROGRESS; canonical enforcement remains pending.
- Therefore `ERR-0008` advances from `IN_PROGRESS` to `FIXED_PENDING_VERIFY`, not `FIXED`.
- No new concrete primary failure signature is evidenced on the current scanned lineages.

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
- status: `FIXED_PENDING_VERIFY`
- checked_sha: original failing UI `5a77a4841dfdda120afaefccb698319d31a7d9e9`; first owner correction `f7da16e05aa50da9ca17e5069a8880a84e34432e`; repeated failing UI `e6cb967c354f55a1cbb4ca1a4bbd2ff26b863b90`; current correction `afa319f0ab1b12edccc4b649d4a1ca36bcd7ac39`.
- evidence: UI Quality `33845743958` and `33849890354` fail only full pytest/canonical enforcement after validator, Ruff, mypy and platform gates pass. Canonical diagnostic from `33845743958` identifies the single stale assertion at `tests/unit/test_pathena_settings_runtime.py:215`. Current exact-fix Quality `33854660676` has Windows path safety, Linux storage, local-install smoke, validator, Ruff and mypy PASS; pytest remains in progress.
- repro: after `apply_ui_refinements_5001_5100(window)`, apply an unavailable model-provider snapshot while local Core remains `ok`, then call `comprehension.sync()`. `runtime.network_value.property("pathenaNetworkScope")` remains truthfully `loopback-only`, so the controller emits `Local loopback connection only; this status does not indicate Internet access.` The stale harness required `Internet-access state is not inferred`.
- root_cause: the first UI correction fixed the missing comprehension-controller installation, exposing a second stale harness expectation. The test expected generic non-loopback accessibility wording even though the real state remained `loopback-only`; product runtime and accessibility implementation were internally consistent.
- files: `tests/unit/test_pathena_settings_runtime.py`; relevant implementation evidence `src/athena/desktop/pathena_settings_comprehension_5100.py`.
- fix_sha: `afa319f0ab1b12edccc4b649d4a1ca36bcd7ac39`.
- verification: PARTIAL ONLY. Exact-fix Quality `33854660676`: Windows path safety PASS; Linux storage PASS; local-install smoke PASS; validator PASS; Ruff PASS; mypy PASS; full pytest IN_PROGRESS; canonical enforcement pending. Do not mark FIXED until the run completes successfully.
- risk: low and harness-only; substantive accessibility/network non-inference coverage is retained by checking both the loopback-specific wording and `pathenaInternetStateInferred is False`.
- integrator_handoff: reject earlier red SHAs as globally green; retain current correction candidate `afa319f0ab1b12edccc4b649d4a1ca36bcd7ac39` but do not integrate/close until exact Quality `33854660676` completes PASS.

## Historical/stale evidence

Historical pre-consolidation/recovery/platform-parity failures remain stale unless their exact signature recurs on current `develop/pathena-next`.
