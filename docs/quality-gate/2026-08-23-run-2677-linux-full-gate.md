# Quality Gate Incident — Run #2677 Linux full keep-going gate

Date: 2026-08-23

## Run / job

- Workflow run: `#2677` / `32662756936`
- Job: `Python 3.12 quality` / `97251316701`
- Checked-out PR merge commit: `3af1d647736ccae70a6db0e1c61626f5cecb5768`
- PR head for that run: `e09650b2e76043e1c1cf5c2eb60ba913762a9f10`
- Runner: Ubuntu 24.04, Python 3.12.14

## Gate summary

- Specification validator: **PASS — 63/63**
- Ruff: **FAIL — 14 errors**
- mypy: **FAIL — 24 errors in 15 files**
- pytest: **FAIL — native process crash / exit -11 after reaching 66% of 3897 collected tests**
- Keep-going behavior: **VERIFIED** — mypy executed after Ruff failed, and pytest executed after both Ruff and mypy failed.

This run replaces #2097 as the latest fully decoded Linux execution baseline for the tested head.

## Ruff classification

The 14 Ruff errors were mostly UI-owned imports/lint issues plus one Quality-owned import-order issue in `tests/unit/test_quality_workflow_contract.py`.

Quality-owned issue:

- `tests/unit/test_quality_workflow_contract.py:1` — I001 import block
- fixed by Quality commit `66ae047e7b917b568915ef2612a6622e47f30c62` by removing the unnecessary future import.

Representative UI-owned issues included multiple I001 errors, one B009 constant `getattr`, one F401 unused `QListWidget`, and an F841 unused local in a UI test. Quality did not mutate UI code/tests.

## mypy classification

24 errors were reported across 15 files. Confirmed Backend-owned groups include:

- `src/athena/research/models.py` — 2 errors
- `src/athena/model/registry.py` — 3 errors
- `src/athena/storage/migration_recovery.py` — 1 unreachable statement
- `src/athena/research/idempotency.py` — 3 unreachable errors
- `src/athena/retrieval/semantic.py` — 2 errors
- `src/athena/chat/grounded_context_package.py` — 1 missing `model_revision` argument

The historical #2097 research-models/idempotency/semantic failures are therefore still executed failures on #2677, not merely stale static suspicions.

Remaining mypy failures shown in the log are UI-owned desktop modules. Quality did not modify those modules.

## pytest execution

The keep-going runner collected 3897 tests and continued through 66% before a fatal native crash. Numerous tests had already reported ordinary failures before the crash, so their details require targeted reruns because pytest never reached its normal failure summary.

Useful executed migration/storage evidence before the crash:

- `tests/unit/test_disk_pressure.py`: PASS on this run head
- `tests/unit/test_migration_activation.py`: PASS
- `tests/unit/test_migration_clone.py`: PASS on Linux
- `tests/unit/test_migration_coordinator.py`: PASS
- `tests/unit/test_migration_executor.py`: at least one FAIL
- `tests/unit/test_migration_journal.py`: PASS
- `tests/unit/test_migration_lock.py`: PASS
- `tests/unit/test_migration_plan.py`: PASS
- `tests/unit/test_migration_recovery.py`: PASS
- `tests/unit/test_migration_safety.py`: PASS
- `tests/unit/test_emergency_reserve.py`: at least one FAIL, consistent with the separately decoded stale message expectation seen on Windows

## Primary fatal pytest termination

The process ended with `Fatal Python error: Segmentation fault`, exit `-11`, while executing:

`tests/unit/test_pathena_command_palette_presentation.py::test_command_palette_uses_quiet_product_copy_without_losing_commands`

Native-stack top:

```text
src/athena/desktop/ascii_panel.py:253 in _bind_pallas_target
src/athena/desktop/ascii_panel.py:166 in set_context
src/athena/desktop/window.py:2660 in _select_page
src/athena/desktop/pathena_window.py:566 in _select_page
src/athena/desktop/window.py:369 in __init__
src/athena/desktop/pathena_window.py:79 in __init__
```

A dedicated incident log tracks this UI-owned P0 separately.

## Timeout evidence

The full quality step ran from approximately 19:55:29 to 20:03:02 UTC (~7m33s), but pytest terminated at 66% due to SIGSEGV. Therefore this run does **not** prove that the current 10-minute timeout has sufficient headroom for a fully completing suite.

## Status

- Keep-going diagnostic coverage: VERIFIED.
- Linux gate: FAIL.
- Quality-owned Ruff issue: FIXED, re-verification pending.
- Backend mypy failures: BLOCKED on Backend owners.
- UI Ruff/mypy failures: BLOCKED on UI owner.
- pytest fatal crash: BLOCKED on UI owner; dedicated incident created.
- Full pytest failure inventory: incomplete because native crash prevented final summary; targeted reruns required.
