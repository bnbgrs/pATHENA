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
- Baseline SHA: `eaab89bb4d7b08839517c40b622480bb1dc309f0`
- Stable read-only parent: `main` at `0d4d621f8a38ddf8eccfa09622bf193687619943`
- Worker branch: `postmerge/errors`
- Error worker synchronized history-preservingly and NON-FORCE with current Develop via merge commit `e01971082f9f04331f1305b097af2e5a23580603`.

## Current error state

- OPEN: none assigned to error-worker product mutation.
- IN_PROGRESS: none.
- FIXED: `ERR-0002` Ruff I001 regression is now verified fixed on the corrected Backend lineage.
- BLOCKED: `ERR-0001` remains Backend-owned pending completion of corrected-lineage verification and integration.

## Current scan

- Exact current Develop `eaab89bb4d7b08839517c40b622480bb1dc309f0` has no associated workflow run or commit statuses, so no exact-Develop Quality PASS is claimed.
- Backend worker head `1cfd18c69014390380bb960b86c8e1b81a5067ac` contains ERR-0001 product fix `780d25d74ce2e310b6a4bc434f547a23163e8b78` plus Ruff harness correction `2f705d5e0fc1c77dd60612b5aeaa16d9380e46cd`.
- Canonical Backend Quality run `33749788522` on exact head `1cfd18c69014390380bb960b86c8e1b81a5067ac` currently shows specification validator PASS, Ruff PASS, mypy PASS, Windows path safety PASS, Linux storage regressions PASS and Local install smoke PASS; full pytest remains in progress.
- Therefore the prior ERR-0002 hypothesis against direct `type(...)` comparisons is retired. The confirmed root cause was Ruff `I001` in the import block of `tests/unit/test_deletion_ledger_boundaries.py`, fixed by `2f705d5e0fc1c77dd60612b5aeaa16d9380e46cd` and verified by canonical Ruff PASS on the corrected exact head.

## Entries

### ERR-0001 — Deletion-ledger mutation/cursor boundaries accept malformed runtime types

- first_seen: 2026-09-03
- last_seen: 2026-09-03
- checked_sha: `eaab89bb4d7b08839517c40b622480bb1dc309f0` baseline; candidate verified on Backend head `1cfd18c69014390380bb960b86c8e1b81a5067ac`
- severity: P2
- area: Storage / Persistence / Deletion Ledger / Recovery boundary
- status: `BLOCKED`
- exact evidence:
  - Current Develop does not yet contain Backend product fix `780d25d74ce2e310b6a4bc434f547a23163e8b78`.
  - The Backend candidate adds fail-before-SQL runtime type/range guards for deletion-ledger mutation and cursor boundaries.
  - Corrected-lineage canonical run `33749788522` has already passed specification validator, Ruff, mypy, Windows path safety, Linux storage regressions and Local install smoke; pytest remains in progress.
- reproducible path:
  1. On baseline without the candidate fix, malformed `entity_type` can reach `.strip()` before intended boundary validation.
  2. Bool values can cross integer timestamp/commit-sequence/cursor boundaries because `bool` is an `int` subclass.
- primary root cause: durable deletion-ledger APIs relied on annotations/relational comparisons instead of explicit bool-safe runtime validation before SQL access.
- affected files: `src/athena/lifecycle/deletion.py`; `tests/unit/test_deletion_ledger_boundaries.py`; existing deletion-ledger/lifecycle recovery regressions.
- fix_commit: Backend candidate `780d25d74ce2e310b6a4bc434f547a23163e8b78`, not integrated.
- verification executed: candidate diff and Backend handoff reviewed; corrected exact-head canonical run `33749788522` inspected through current job state.
- remaining risks: full pytest on corrected Backend head has not completed; candidate is not integrated into current Develop; independent post-integration re-verification remains required.
- integrator handoff: wait for corrected-lineage pytest/run completion, then integrate only if no Backend-owned regression appears; after integration Error worker independently re-verifies before `FIXED`.
- blocked reason: active ownership collision avoidance with `postmerge/backend`.

### ERR-0002 — Backend deletion-boundary test import block failed canonical Ruff I001

- first_seen: 2026-09-03
- last_seen: 2026-09-03
- checked_sha: `1cfd18c69014390380bb960b86c8e1b81a5067ac`
- severity: P2
- area: Quality / Python lint / Storage boundary test harness
- status: `FIXED`
- exact evidence:
  - Previous canonical run `33744816398` failed `Quality — Ruff` because `tests/unit/test_deletion_ledger_boundaries.py` had Ruff `I001` for an unformatted import block.
  - Backend correction `2f705d5e0fc1c77dd60612b5aeaa16d9380e46cd` changes import formatting only; assertions and product semantics are unchanged.
  - Corrected exact-head canonical run `33749788522` reports `Quality — Ruff` = SUCCESS on Backend head `1cfd18c69014390380bb960b86c8e1b81a5067ac`.
- reproducible path: canonical Ruff on the previous Backend lineage reproduced I001; the same canonical Ruff step now passes on the corrected exact head.
- primary root cause: import ordering/formatting defect in `tests/unit/test_deletion_ledger_boundaries.py`; not the product `type(...)` runtime guards.
- affected files: `tests/unit/test_deletion_ledger_boundaries.py` only.
- fix_commit: `2f705d5e0fc1c77dd60612b5aeaa16d9380e46cd`.
- verification executed: canonical `Quality — Ruff` PASS in run `33749788522` on exact corrected Backend head.
- remaining risks: none for ERR-0002 itself; full workflow completion is still relevant to ERR-0001/integration readiness but not required to establish that the Ruff signature is fixed.
- integrator handoff: ERR-0002 no longer blocks integration by itself; use the corrected Backend lineage and wait for remaining ERR-0001 verification.

## Historical/stale evidence

Historical pre-consolidation and recovery/platform-parity failures remain stale unless their signature recurs on current `develop/pathena-next`.
