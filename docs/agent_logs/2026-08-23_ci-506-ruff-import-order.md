# CI #506 — Ruff import-order failure in Windows safety tests

- Timestamp: 2026-08-23 00:20 Europe/Berlin
- Repository: `bnbgrs/pATHENA`
- Branch: `agent/pathena`
- Failing pATHENA HEAD: `b7a99563f701d8b8fd9ee2cdb825f167df1b5755`
- Fix HEAD after code changes: `2a7830ddae55bb549190732e92fcffe4c02f77e8`
- GitHub Actions run: `32601758870` / run number `506`
- Job: `97100982776` — `Python 3.12 quality`
- Failed step: `Run ATHENA quality gate`
- Classification: `CODE/TEST-LINT`
- Status: `FIXED_PENDING_CI`

## Affected files

- `tests/unit/test_windows_settings_script_safety.py`
- `tests/unit/test_windows_uv_probe_safety.py`

## Reproduction / failing check

```text
uv run --locked --extra dev --extra desktop python scripts/quality.py
```

The specification validator passed `63/63`. The gate then failed in Ruff before mypy or pytest could run.

## Relevant error excerpt

```text
I001 [*] Import block is un-sorted or un-formatted
 --> tests/unit/test_windows_settings_script_safety.py:1:1

I001 [*] Import block is un-sorted or un-formatted
 --> tests/unit/test_windows_uv_probe_safety.py:1:1

Found 2 errors.
[*] 2 fixable with the `--fix` option.

[FAIL] Ruff returned 1.
```

## Root cause

Both new Windows safety tests carried an unnecessary `from __future__ import annotations` import. These files do not require postponed annotation evaluation under the project's Python 3.12-only runtime. Removing the unused future import leaves a single standard-library import and eliminates the Ruff isort/I001 failure without changing test behavior.

## Fix

- Removed the unnecessary future import from both affected tests.
- No production behavior changed.
- `bnbgrs/ATHENA` was not modified.

Commits:

- `38385ff6414331a44baa80206a99e89e31c1cd34` — settings safety test
- `2a7830ddae55bb549190732e92fcffe4c02f77e8` — uv probe safety test

## Verification evidence

Observed before fix:

- Spec validator: `PASS`, `63/63`
- Ruff: `FAIL`, exactly two `I001` findings above
- mypy: not reached due fail-fast gate
- pytest: not reached due fail-fast gate

Observed after fix:

- Repository edits completed successfully.
- New CI result not yet observed at the time this log was created.

## Next action

Inspect the workflow run triggered by fix HEAD `2a7830ddae55bb549190732e92fcffe4c02f77e8` (or a later current head). If Ruff passes, continue through mypy/pytest and update this log to `FIXED` with the observed gate evidence. If another gate failure appears, create a separate durable error log for that distinct failure before continuing.
