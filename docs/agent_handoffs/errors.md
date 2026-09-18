# Error worker handoff

## Exact source of truth
- Develop: `03157f15246c8acb0f51a30631bf45c4d2a72416`.
- Error worker: ledger refresh `01170b94326b61fd71673befef53584e5d9fe2db` before this handoff update.
- Spec/Core: `6dddda87919cc5363ccf664863f6b4dca83784ed`; no new current-SHA failure evidence.
- Backend: `71e551364c5355e8d030b0964c39d9ed53e502bb`; Backend Focused `35324506141 = SUCCESS`; canonical `35324506070 = FAILURE`.
- UI: `e149515870b773548a164658775159f29de323af`; current handoff still has `PAIRS_VERIFIED_0_OF_11` / `MATCH_0_OF_11`.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## ITERATION-1 — Backend successor consumed
Backend advanced to `71e551...` (`Backend: restore durable verify contract regression`). The bounded test file now again expects `{"pipeline_version":"backup-deep-verify-v1"}` and uses `"wrong"` as the deliberately invalid pipeline version.

## ITERATION-2 — ERR-0075 exact closure
Canonical `35324506070` full pytest is SUCCESS: `5331 passed, 17 skipped, 2 warnings`. This closes the newly reproduced durable-service contract regression on exact `71e551...`. `ERR-0075 = FIXED`; do not reopen without a new exact-SHA reproduction.

## ITERATION-3 — ERR-0074 remains exact and isolated
Canonical Python quality has Specification Validator SUCCESS, mypy SUCCESS and pytest SUCCESS; Ruff alone fails. Exact diagnostics contain one fixable `I001` at `tests/unit/test_backup_verify_durable_service.py:1:1` and explicitly say `help: Organize imports` / `1 fixable with --fix`. The current block is `from __future__`, `from unittest.mock import Mock`, straight `import athena...`, `import pytest`, then `from athena...`. No further hand-authored import permutations count as closure evidence.

## ITERATION-4 — release guards held
Windows Path Safety, Linux Storage and Local-install are SUCCESS on exact `71e551...`. Windows storage/durable-filesystem/API-boundary/Core-ownership/packaged-runtime/adaptive-chat/restart/pypdf guards remain green. `ERR-0059 = FIXED`; no new manifest-truth failure signature exists and canonical full pytest is green.

## ITERATION-5 — visual ownership held
`ERR-0054 = OPEN`, UI/Visual-Review-owned. UI remains `e1495158...`; its handoff explicitly reports zero of eleven pairs verified for the candidate. Error worker neither creates nor accepts a baseline.

## Next root cause
1. Backend: `ERR-0074` only — execute repository-pinned Ruff 0.15.22 `check --fix tests/unit/test_backup_verify_durable_service.py` on exact source and consume the complete generated transformation.
2. Require focused Ruff PASS before another canonical candidate; do not submit another hand-authored import permutation.
3. Close `ERR-0074` only from terminal exact-SHA canonical Ruff success.
4. Keep `ERR-0075`, `ERR-0059` and all current release guards closed unless a new exact-SHA failure reproduces them.
5. Error worker consumes the next Backend successor immediately, then moves to the next independent current failure cluster.