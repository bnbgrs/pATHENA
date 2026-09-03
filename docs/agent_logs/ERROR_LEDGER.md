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
- Baseline SHA: `58dbd4d80bc61c4cc8e9cd6d61adaa5b311ea4c3`
- Stable read-only parent: `main` at `0d4d621f8a38ddf8eccfa09622bf193687619943`
- Worker branch: `postmerge/errors`
- Exact current Develop has no associated workflow run or commit-status result, so no synthetic whole-Develop Quality PASS is claimed.

## Current error state

- OPEN: none confirmed on the current baseline.
- IN_PROGRESS: none.
- FIXED: `ERR-0001`, `ERR-0002`.
- BLOCKED: none.

## Current scan

- Integrator fast-forwarded the verified Backend lineage containing deletion-ledger fix `780d25d74ce2e310b6a4bc434f547a23163e8b78` and Ruff-only test correction `2f705d5e0fc1c77dd60612b5aeaa16d9380e46cd` into Develop, then integrated the independent UI/PALLAS lifecycle repair.
- On current Develop, `src/athena/lifecycle/deletion.py` has blob `b37897f385e216508314d9cbdc44610d569df331`, identical to current Backend; `tests/unit/test_deletion_ledger_boundaries.py` has blob `1c5ff46c623f9bb57fca2bd7613e1efee9ea3aec`, also identical to current Backend.
- Canonical Backend run `33749788522` exercised this exact deletion product/test content: all 22 deletion-boundary tests passed; specification validator, Ruff, mypy, Windows path safety, Linux storage regressions and Local install smoke passed. Its sole full-pytest failure was independently diagnosed as UI/PALLAS `MessageActionTabOrderController.document`, not deletion/storage.
- The UI-owned PALLAS defect was subsequently fixed and exact UI head `76cb122dbe7b58b0fa49bbcb36de2bd732922d4d` passed canonical Quality run `33751403354`; the bounded fix was then integrated into Develop.
- Backend head `a4768d9b0ea57a1161c93f603a5101c28b555276` currently has canonical run `33755878184` still in progress; pending/in-progress evidence is not treated as PASS or FAIL.
- No new current-lineage error signature is evidenced in this run.

## Entries

### ERR-0001 — Deletion-ledger mutation/cursor boundaries accept malformed runtime types

- first_seen: 2026-09-03
- last_seen: 2026-09-03
- checked_sha: `58dbd4d80bc61c4cc8e9cd6d61adaa5b311ea4c3`
- severity: P2
- area: Storage / Persistence / Deletion Ledger / Recovery boundary
- status: `FIXED`
- exact evidence:
  - Product fix `780d25d74ce2e310b6a4bc434f547a23163e8b78` is integrated into current Develop.
  - Current Develop deletion product blob `b37897f385e216508314d9cbdc44610d569df331` is identical to the verified Backend blob.
  - Current Develop boundary-test blob `1c5ff46c623f9bb57fca2bd7613e1efee9ea3aec` is identical to the verified Backend blob.
  - Canonical Backend run `33749788522` passed all 22 deletion-boundary tests plus validator, Ruff, mypy, Windows path safety, Linux storage and local-install smoke on this exact product/test content.
  - That run's only full-pytest failure was independently identified as UI/PALLAS and later fixed/verifiably green on UI canonical run `33751403354` before bounded integration into Develop.
- reproducible path before fix:
  1. Malformed `entity_type` could reach `.strip()` before intended boundary validation.
  2. Bool values could cross integer timestamp/commit-sequence/cursor boundaries because `bool` is an `int` subclass.
- primary root cause: durable deletion-ledger APIs relied on annotations/relational comparisons instead of explicit bool-safe runtime validation before SQL access.
- affected files: `src/athena/lifecycle/deletion.py`; `tests/unit/test_deletion_ledger_boundaries.py`.
- fix_commit: `780d25d74ce2e310b6a4bc434f547a23163e8b78`; harness correction `2f705d5e0fc1c77dd60612b5aeaa16d9380e46cd`.
- verification executed: 22 focused boundary tests PASS in canonical Backend run `33749788522`; validator/Ruff/mypy/Windows/Linux-storage/local-install checks PASS; current-Develop product and test blobs independently compared and confirmed identical to the verified lineage; unrelated UI-only pytest failure separately fixed and canonical-green before integration.
- remaining risks: no exact whole-Develop Quality run exists yet for `58dbd4d...`; this does not reopen ERR-0001 absent recurrence, but the next scan must consume any new current-Develop/worker Quality evidence.
- integrator handoff: no further ERR-0001 fix integration required; keep closed unless the same runtime-boundary signature recurs on a newer checked SHA.

### ERR-0002 — Backend deletion-boundary test import block failed canonical Ruff I001

- first_seen: 2026-09-03
- last_seen: 2026-09-03
- checked_sha: `58dbd4d80bc61c4cc8e9cd6d61adaa5b311ea4c3`
- severity: P2
- area: Quality / Python lint / Storage boundary test harness
- status: `FIXED`
- exact evidence:
  - Previous canonical run `33744816398` failed `Quality — Ruff` because `tests/unit/test_deletion_ledger_boundaries.py` had Ruff `I001` for an unformatted import block.
  - Correction `2f705d5e0fc1c77dd60612b5aeaa16d9380e46cd` changes import formatting only; assertions and product semantics are unchanged.
  - Corrected canonical run `33749788522` reports Ruff PASS.
  - Current Develop test blob `1c5ff46c623f9bb57fca2bd7613e1efee9ea3aec` is identical to the corrected verified Backend blob.
- reproducible path: canonical Ruff on the previous Backend lineage reproduced I001; corrected lineage passes canonical Ruff.
- primary root cause: import ordering/formatting defect in `tests/unit/test_deletion_ledger_boundaries.py`.
- affected files: `tests/unit/test_deletion_ledger_boundaries.py` only.
- fix_commit: `2f705d5e0fc1c77dd60612b5aeaa16d9380e46cd`.
- verification executed: canonical Ruff PASS in run `33749788522`; current Develop contains the identical corrected test blob.
- remaining risks: none for this signature.
- integrator handoff: no action required unless Ruff I001 recurs on a newer checked SHA.

## Historical/stale evidence

Historical pre-consolidation and recovery/platform-parity failures remain stale unless their signature recurs on current `develop/pathena-next`.
