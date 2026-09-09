# pATHENA Backend & Systems Handoff

## Baseline

- Exact Develop reviewed: `develop/pathena-next@8b7d83ba170a121414a26055f0c5df9acf97914e`.
- Pre-run Backend worker: `postmerge/backend@3fbd8c238b8e926c5c175e37805c3033cb90e6b6`.
- Latest exact canonical Quality consumed: `34290849093@3fbd8c238b8e926c5c175e37805c3033cb90e6b6` = FAILURE.
- Diagnostics: pytest `31 failed, 4820 passed, 3 skipped`; Ruff has exactly one I001 in `src/athena/storage/schema.py`; specification-validator, mypy, Linux storage regressions, Windows path safety and Local install smoke passed.
- `main` and `bnbgrs/ATHENA` remain read-only; no force update or history rewrite.

## Current bounded slice — Ruff I001

Exact `ruff.txt` proves the `athena.storage.schema_contract` import block is unsorted because `_user_tables` precedes `DatabaseCompatibilityError`. An earlier repository blob `b5658c38ca061095a951bc85f3a2fbc88b53ee76` is otherwise byte-identical to the current schema file and differs by exactly that import ordering, as confirmed by commit comparison from `69e2a4707bba544af5d2d2ae53daffc1dbf786a3` to the current worker showing `src/athena/storage/schema.py` at `+1/-1` only.

This candidate restores the formatter-required ordering:

- `DatabaseCompatibilityError as DatabaseCompatibilityError`
- `_user_tables as _user_tables`

No schema, migration, verification, persistence, recovery, WAL, network or runtime semantics change.

## Develop synchronization

The same candidate imports current Develop changes byte-identically for:

- `docs/agent_handoffs/integrator.md`
- `src/athena/desktop/pathena_design_tokens.py`
- `tests/unit/test_direct_chat_context_budget.py`
- `tests/unit/test_pathena_design_system.py`
- `tests/unit/test_pathena_design_tokens.py`
- `tests/unit/test_pathena_theme.py`
- `tests/unit/test_pathena_window.py`

## Remaining independent current failures

The exact pytest diagnostics show a separate v41 harness/fixture cluster: stale latest-schema expectations still assert v40/`0040_grounded_response_receipts`, and reconstructed v30-v40 fixtures can retain the v41-only `research_delta_boundaries` table/index, causing `table research_delta_boundaries already exists`. Those failures are not mixed into this Ruff-only candidate.

The three WAL failures in Quality `34290849093` correspond to the predecessor SHA and are addressed by the current worker's exact-class scheduler/guard-text harness commits; their closure still requires this candidate's new exact-SHA Quality evidence.

## Invariants retained

- no production guard, storage validation, migration, recovery or security weakening;
- no Skip/XFail or assertion relaxation;
- no silent Tor→Direct fallback; redirect/auth/HTTPS/compression/response-size fail-closed boundaries unchanged;
- PASSIVE-only automatic WAL maintenance and explicit-idle TRUNCATE unchanged;
- pypdf/frozen argv/two-EXE/bounded worker tree/adaptive 2048-context reserve/Windows lane-lock/startup crash classes remain release guards.

## Verification prerequisite

Run one canonical Quality on the exact candidate. Do not mark Integrator-ready unless Ruff clears and the previously repaired WAL subcluster is verified. The independent v41 fixture/current-expectation cluster remains Backend-owned and must be closed in a later bounded candidate before global readiness.
