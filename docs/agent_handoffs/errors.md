# Error worker handoff

## Exact source of truth

- Develop: `ee8aa791742f7cbdd056532e66a50da14c461c4a`; canonical `34818856565 = SUCCESS`.
- Error worker: harness repair ancestor `158d62e9a1eb9ddaf3e0b5ff3112e75e4ec9d6cb`; no exact workflow had started on it at this refresh.
- Spec/Core: `6c7f417a53428f496d7b31e330917d4a53c85189`; canonical `34818641155 = SUCCESS`.
- Backend: `52eb61de9ecfde4074778a1bab2966e18aab526d`; canonical `34796053576 = SUCCESS`.
- UI: `a88eac5f05db4128ae21b7c747e95c16a91191c4`; Visual `34819309682 = FAILURE` only at final verdict after 11-capture and route-identity success. Canonical `34819314295 = FAILURE` only in full pytest; release/storage/install/validator/Ruff/mypy lanes are green.

## ERR-0064 — IN_PROGRESS — Core Focused selector contamination

Core Focused `34819314380` on current UI produces 61 mypy errors from unrelated desktop/UI tests while focused pytest selects no Core-owned test files. The Error-worker repair aligns Ruff, mypy and Ruff-remediation with the existing Core-owned test-family selector, without changing repository-wide canonical Quality or product/test contracts.

## Current UI canonical regressions — OPEN / UI-owned

Exact canonical `34819314295` reports three candidate-specific UI failures: design-system bounded-scale tuple `(15, 11, 30)` vs `(15, 12, 42)`, readiness placeholder `Ask anything…` vs required `pATHENA reconnecting`, and converged composer height `118` vs `94`. These are not Error-owned and are not patched from `postmerge/errors`; UI must root-cause/split them on its successor.

## ERR-0063 — FIXED

Current UI Visual `34819309682` captures all eleven canonical surfaces and passes workspace route identity. The previous capture/route blocker is closed on the exact current UI SHA.

## ERR-0059 — FIXED

The exact current UI visual artifact was opened. Its manifest reports the eleven actual capture labels, `captured_reference_count=11`, `assigned_reference_count=11`, no errors and `status=PASS`. This verifies the capture-derived manifest fix and preserves the exact-eleven fail-closed PASS contract.

## ERR-0054 — OPEN — UI/Visual Review

Technical capture is complete again, so review is no longer blocked. The current UI handoff remains `PAIRS_VERIFIED_0_OF_11` / `MATCH_0_OF_11`; Error worker must not create or accept a baseline. UI must open and assess all eleven exact reference/render pairs and obtain final visual-verdict success.

## Green / held clusters

- Spec/Core and Backend remain exact canonical-green; do not reopen without a new matching signature.
- Develop is canonical-green on current exact SHA.
- Persistent pypdf/Frozen-argv/two-EXE/bounded-worker/adaptive-2048/lane-lock/duplicate-column/Core-startup/storage-bootstrap guards remain unchanged.
- Error-worker 48px Send geometry remains `STALE`, not a new product root cause.

## Next root cause

1. Consume exact CI for `ERR-0064` and do not supersede its candidate while checks run.
2. UI consumes and repairs/splits the three exact canonical pytest regressions; Error worker remains evidence-only for that product slice.
3. Keep `ERR-0059` and `ERR-0063` closed.
4. `ERR-0054` remains strictly UI/Visual-Review-owned until truthful 11/11 review evidence exists.
