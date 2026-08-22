# CI #506 / #512 — Ruff import-block formatting failure in Windows safety tests

- First observed: 2026-08-23 00:20 Europe/Berlin
- Reclassified: 2026-08-23 00:26 Europe/Berlin
- Verified fixed: 2026-08-23 00:45 Europe/Berlin
- Repository: `bnbgrs/pATHENA`
- Branch: `agent/pathena`
- First failing pATHENA HEAD: `b7a99563f701d8b8fd9ee2cdb825f167df1b5755`
- First attempted fix HEAD: `36b298f116e3b4475b0105313783dc7d51455f02`
- Corrected code HEAD: `411e5a2c29cc101c4775ceac3322fbe7cfe00b51`
- Verification HEAD: `fa98b6aa8cafc2f169dbf01c91b9af3e318c59c1`
- GitHub Actions runs: `32601758870` / #506, `32602260319` / #512, `32602427831` / #518
- Jobs: `97100982776`, `97102238068`, `97102644559` — `Python 3.12 quality`
- Gate step: `Run ATHENA quality gate`
- Classification: `CODE/TEST-LINT`
- Status: `FIXED`

## Affected files

- `tests/unit/test_windows_settings_script_safety.py`
- `tests/unit/test_windows_uv_probe_safety.py`

## Reproduction / failing check

```text
uv run --locked --extra dev --extra desktop python scripts/quality.py
```

In CI #506 and #512 the specification validator passed `63/63`, then Ruff failed before mypy or pytest could run.

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

## Root cause and reclassification

The first diagnosis was incomplete. The original files combined a future import and a standard-library import without the group separation Ruff expects. The first attempted fix removed the unnecessary future imports but left **two blank lines** between the remaining import block and the module constants. CI #512 reproduced the same `I001` findings, proving that attempt did not satisfy Ruff's import-block formatter.

The corrected form keeps the single `from pathlib import Path` import and exactly one blank line before the module constants. This is a formatting-only change; the tests' behavior is unchanged.

## Fix history

First attempted fix — **did not resolve CI**:

- `38385ff6414331a44baa80206a99e89e31c1cd34` — removed future import from settings safety test
- `2a7830ddae55bb549190732e92fcffe4c02f77e8` — removed future import from uv-probe safety test
- `36b298f116e3b4475b0105313783dc7d51455f02` — log-bearing HEAD tested by CI #512

Corrected fix:

- `6f2a283022032a825793d0b36b73b6ed5711a801` — normalized blank-line spacing after settings safety import block
- `411e5a2c29cc101c4775ceac3322fbe7cfe00b51` — normalized blank-line spacing after uv-probe safety import block

No production behavior changed. `bnbgrs/ATHENA` was not modified.

## Verification evidence

Observed on CI #506:

- Specification validator: `PASS`, `63/63`
- Ruff: `FAIL`, two `I001` findings
- mypy: not reached due fail-fast gate
- pytest: not reached due fail-fast gate

Observed on CI #512 after the first attempted fix:

- Specification validator: `PASS`, `63/63`
- Ruff: `FAIL`, the same two `I001` findings
- mypy: not reached due fail-fast gate
- pytest: not reached due fail-fast gate

Observed on CI #518 (`32602427831`) for pATHENA HEAD `fa98b6aa8cafc2f169dbf01c91b9af3e318c59c1`:

```text
TOTAL 63/63 PASS
All checks passed!
Success: no issues found in 234 source files
============================= test session starts ==============================
collected 1453 items
```

This proves both Ruff and mypy passed and pytest started. The overall workflow was later cancelled during pytest at approximately 83% after multiple separate test failures had already been observed. Those pytest regressions are not part of this lint defect and are tracked separately.

## Next action

No further action for this Ruff defect. Preserve the Windows safety tests and continue resolving the separately logged pytest regressions from CI #518.
