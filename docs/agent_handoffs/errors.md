# Error worker handoff

## Exact source of truth

- Develop: `ee8aa791742f7cbdd056532e66a50da14c461c4a`; canonical `34818856565 = SUCCESS`.
- Error worker before this repair: `e1b6e00f375fa5ceab143d01ee9c01ab598cd133`; canonical `34816691363 = FAILURE` only on inherited stale 48px UI geometry; release/storage/type/validator lanes are green.
- Spec/Core: `6c7f417a53428f496d7b31e330917d4a53c85189`; canonical `34818641155 = SUCCESS`.
- Backend: `52eb61de9ecfde4074778a1bab2966e18aab526d`; canonical `34796053576 = SUCCESS`.
- UI: `a88eac5f05db4128ae21b7c747e95c16a91191c4`; Visual `34819309682 = FAILURE` only at final verdict after 11-capture and route-identity success. Canonical is still running at handoff update.

## ERR-0064 — IN_PROGRESS — Core Focused selector contamination

Core Focused `34819314380` on the current UI SHA produces 61 mypy errors exclusively from unrelated desktop/UI tests while focused pytest selects no Core-owned test files. The harness root cause is the broad `tests/unit/.*` Ruff/mypy selection. This Error-worker candidate aligns Ruff, mypy and Ruff-remediation with the existing Core-owned test-family selector used by focused pytest, without changing repository-wide canonical Quality or any product/test contract.

## ERR-0063 — FIXED

Current UI Visual `34819309682` captures all eleven canonical surfaces and passes workspace route identity. The previous capture/route blocker is closed on the exact current UI SHA.

## ERR-0059 — FIXED

The current exact UI visual artifact was opened. Its manifest reports the eleven actual capture labels, `captured_reference_count=11`, `assigned_reference_count=11`, no errors and `status=PASS`. This verifies the capture-derived manifest fix and preserves the exact-eleven fail-closed PASS contract.

## ERR-0054 — OPEN — UI/Visual Review

Technical capture is complete again, so review is no longer blocked. The current UI handoff remains `PAIRS_VERIFIED_0_OF_11` / `MATCH_0_OF_11`; Error worker must not create or accept a baseline. UI must open and assess all eleven exact reference/render pairs and obtain final visual-verdict success.

## Green / held clusters

- Spec/Core and Backend remain exact canonical-green; do not reopen without a new matching signature.
- Develop is canonical-green on the current exact SHA.
- Persistent pypdf/Frozen-argv/two-EXE/bounded-worker/adaptive-2048/lane-lock/duplicate-column/Core-startup/storage-bootstrap guards remain unchanged.
- Error-worker 48px Send geometry remains `STALE` and is not a product root cause for this worker.

## Next root cause

1. Consume exact CI for the `ERR-0064` harness candidate and do not supersede it while checks run.
2. Consume current UI canonical terminal result and classify only exact new signatures.
3. Keep `ERR-0059` and `ERR-0063` closed.
4. `ERR-0054` remains strictly UI/Visual-Review-owned until truthful 11/11 review evidence exists.
