# Error worker handoff

## Exact source of truth
- Develop: `03157f15246c8acb0f51a30631bf45c4d2a72416`.
- Error worker: `9a5618aac9547525c74fd26eef6a885b0f7b6bac` after ledger refresh, before this handoff update.
- Spec/Core: `6dddda87919cc5363ccf664863f6b4dca83784ed`; no new current-SHA failure evidence.
- Backend: `073cb77eebd7cdc3b5bd43e7d4463cf147f24c1e`; Backend Focused `35162492712 = SUCCESS`; canonical `35162492838 = FAILURE`.
- UI: `e149515870b773548a164658775159f29de323af`; no new Error-worker closure evidence.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## ITERATION-1 — Backend successor consumed
Backend advanced from `ff4e4c79...` to `073cb77e...` with `Backend: fix Ruff first-party import grouping`. The bounded commit changes only the import grouping in `tests/unit/test_backup_verify_durable_service.py`.

## ITERATION-2 — exact diagnostics extracted
Canonical `35162492838` is terminal FAILURE. Downloaded diagnostics prove exactly one Ruff failure: `I001 Import block is un-sorted or un-formatted` at `tests/unit/test_backup_verify_durable_service.py:1:1`, explicitly fixable with `--fix`. Specification Validator, mypy and full pytest are SUCCESS.

## ITERATION-3 — cascade deduplicated
ERR-0074 remains `OPEN` and is the sole current Backend Python-quality root cause. ERR-0075 remains `FIXED`: canonical full pytest is green and the durable-service tests pass. No historical Backend failure is reopened.

## ITERATION-4 — release guards held closed
Linux storage, Local-install smoke and Windows path/storage/durable-filesystem/API-boundary/ownership/packaged-runtime/adaptive-chat/restart/pypdf guards are SUCCESS on exact `073cb77e...`. Do not reopen or relax them.

## ITERATION-5 — visual/manifest ownership preserved
ERR-0059 = `FIXED`; preserve capture-derived fields, `assigned_reference_count = 11`, and exact-eleven fail-closed PASS semantics. ERR-0054 = `OPEN` / UI-Visual-Review-owned; Error worker must not create or accept a baseline.

## Next root cause
1. Backend owns ERR-0074. Stop manual import-group guesses: run the pinned Ruff `--fix` against the exact file and preserve the generated diff, then focused Ruff + durable-service pytest before one canonical candidate.
2. Close ERR-0074 only on terminal exact-SHA canonical Ruff success.
3. Keep ERR-0075 and all currently green release guards closed absent new exact signatures.