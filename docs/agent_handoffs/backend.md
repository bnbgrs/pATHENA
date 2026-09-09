# Backend & Systems Handoff

Generated: 2026-09-10
Branch: `postmerge/backend`

## Current baseline

- Develop source-of-truth consumed: `develop/pathena-next@16336f99ebe7e294c352eb215bfb6c5543db1c64`.
- Exact Develop canonical Quality: `34415180744` — FAILURE only at Ruff; specification validator, mypy, full pytest, Windows path safety, Linux storage regressions, and local-install smoke passed.
- Exact Ruff diagnostic: `I001 Import block is un-sorted or un-formatted` at `tests/unit/test_chat_context_reserve_contract.py:1:1`.
- Exact behavioral evidence on the same SHA: `tests/unit/test_chat_context_reserve_contract.py` passed and full pytest completed `4826 passed, 3 skipped`.
- Previous Backend HEAD: `844d65a85ecb611d5060bf311c6346c810d2247e`; its earlier canonical Quality remains failed and is not READY evidence.

## Bounded root-cause closure candidate

The current Develop red exact-SHA root cause is harness-only Ruff formatting in the newly added adaptive-2048 reserve contract. The candidate synchronizes the six current Develop commits history-preservingly and changes only that new test's import-block spacing from two blank lines after the sole import to Ruff's canonical single blank separator before module constants. Assertions and product behavior are unchanged.

No production code was altered for the failure. Current Develop's disjoint Research/Jobs and release-contract files are synchronized byte-identically from the source-of-truth tree.

## Verification

- Before mutation, no `postmerge/backend` canonical Quality run was queued or in progress; latest worker Quality `34378587885` was completed FAILURE.
- Focused behavioral evidence precedes this candidate through exact Develop Quality `34415180744`: the target test itself passed.
- Exact Ruff failure is assertion/file bound from the decoded canonical job log and reports only I001 in the target file.
- Local checkout remains unavailable because the execution environment cannot resolve `github.com`; no fabricated local Ruff PASS is claimed.
- Candidate requires a new exact-SHA canonical Quality result before any READY handoff.

## Preserved invariants

- No product guard, test assertion, Security, Storage, Recovery, WAL, migration, TOR/network, packaging, worker-tree, context-reserve, Windows lane-lock, duplicate-column, Core-startup, or storage-bootstrap invariant was weakened.
- No Skip/XFail, force push, history rewrite, or main mutation.
- `bnbgrs/ATHENA` and `main` remain read-only.

## Integrator prerequisites

HOLD until canonical Quality completes successfully on the exact final Backend candidate SHA. Do not treat the historical Backend v41 fixture work as globally READY while known worker red root causes remain. The older archive-replication v41 fixture drift remains a separate root-cause cluster and was not modified in this slice.

## Next Backend action

At the next run, consume the exact-SHA candidate Quality first. If Ruff is green, close only this current-lineage I001 cluster; then re-evaluate current Develop and choose the highest remaining exact-SHA Backend/System root cause without duplicating integrated work.
