# Quality Gate #1087 — Ruff I001 in UI refinement 200

## Scope

Repository: `bnbgrs/pATHENA`

Branch: `agent/pathena`

Initial failing workflow run: `32633840858` (`ATHENA Quality Gate` run #1087)

Initial observed head: `5c1b4d28ced231d7ed88efc1be0571d2fef134db`

Follow-up workflow run: `32634118715` (`ATHENA Quality Gate` run #1099)

## Failure

The specification validator completed with `63/63 PASS`. The gate then stopped in Ruff before mypy and pytest.

Run #1087 reported exactly two `I001` failures:

- `src/athena/desktop/pathena_ui_refinement_200.py:7:1` — import block not in Ruff's canonical formatted form.
- `tests/unit/test_pathena_ui_refinement_200.py:1:1` — import block not in Ruff's canonical formatted form.

Run #1099 proved that the test-side correction was successful and narrowed the remaining failure to the production module only:

- `src/athena/desktop/pathena_ui_refinement_200.py:7:1` — single remaining `I001`.

No production behavior failure was reported by either run.

## Root cause

The newly added second UI-refinement pass and its inventory test had not been normalized through the repository's pinned Ruff configuration (`ruff==0.15.22`, `I` rules enabled).

The test imported two module members directly; replacing this with one module import produced the canonical block and was confirmed by run #1099.

The production failure was not caused by the identity or order of the sole `PySide6` import. Run #1099 showed that it persisted even after removing the unnecessary future import. The actual formatting defect was the import-to-module-constant boundary: two blank lines separated the sole import from `UI_REFINEMENT_TASKS_101_200`. Ruff's import organizer expects one blank line when the next top-level statement is a module assignment rather than a class/function definition.

## Fix

- Import the refinement module once in `test_pathena_ui_refinement_200.py` and reference its inventory/guidance through that module.
- Remove the unnecessary future import from `pathena_ui_refinement_200.py`.
- Normalize the production import-to-constant boundary to one blank line.
- No feature behavior, persistence contract, scheduler behavior, API behavior, or `bnbgrs/ATHENA` content is changed.

Fix commits:

- `051f032309717e231eb7faadfccce752465e9e3d` — normalize the UI refinement 200 test import.
- `fcef5e5009cd090feb3901c5768d6cb7fcc0e99f` — simplify the production import block; follow-up #1099 showed spacing still needed correction.
- `94f09bf02d973eab0e845a0fe6dd502e15769b8b` — normalize import-to-constant spacing, addressing the remaining #1099 I001.

## Verification

- Run #1087: specification validator `63/63 PASS`; Ruff failed with two I001 diagnostics.
- Run #1099: specification validator `63/63 PASS`; test-side I001 gone; exactly one production I001 remained.
- The next branch-triggered Quality Gate after `94f09bf02d973eab0e845a0fe6dd502e15769b8b` is the authoritative verification of the final spacing correction and will expose the next independent gate failure, if any.
