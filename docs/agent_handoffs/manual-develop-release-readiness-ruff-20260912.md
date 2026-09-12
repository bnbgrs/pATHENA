# Develop Release Readiness Ruff Repair Handoff

## Baseline and reproduction

- Develop baseline: `develop/pathena-next@146fb7280dbfe30f2bec129aec8ee77f015ce040`.
- Canonical Quality run `34697870543` on that exact Develop SHA completed `FAILURE`.
- The failure is bounded to Ruff `I001` in exactly two files:
  - `src/athena/release_readiness.py`
  - `tests/unit/test_release_readiness.py`
- The same inherited failure reproduced on `postmerge/spec-core@a35a67f1afe2789d8a568fa3484ef5fe29f46de9` in canonical run `34698818608`; Spec/Core Focused `34698818610` was green and canonical mypy, pytest, Windows, Linux storage and local install all passed.
- Exact canonical pytest on that Spec/Core reproduction: `4989 passed, 17 skipped`.

## Root cause

Ruff 0.15.22 requires the release-readiness import blocks to be normalized. No product behavior, assertion, release guard, storage guard, security guard or Windows behavior is implicated.

## Repair

This branch ports only the already-Ruff-green formatting used by current Backend candidate `postmerge/backend@6fcfdf8a71abcabad7e3b4a661ad35ee1f6603f8`:

- remove one extra blank line after `from dataclasses import dataclass` before `_REQUIRED_GUARDS`;
- collapse the project import in `tests/unit/test_release_readiness.py` to Ruff's single-line form.

No other Backend work is consumed. In particular `schedule_recovery.py` and its tests are intentionally excluded.

Repair commits:
- `69118c6224f5202775af056dcc31295a8d6e82ff`
- `5bd1c9531d4103b30822a2c84520fc0cc017a9a8`

## Bot coordination

- Do not reimplement this import-format fix independently.
- Do not merge Backend Schedule Recovery merely to obtain this Ruff repair.
- Spec/Core should treat its current canonical Ruff failure as inherited from Develop, not as a defect in the provenance-explanation slice.
- Backend may continue its own bounded work; its current head already demonstrates Ruff success for these exact file blobs.
- UI does not own these paths.
- Errors should record this as a current Develop baseline Ruff cluster and close it only after the repaired exact Develop SHA passes canonical Quality after integration.

## Promotion rule

Require canonical Quality on the exact repair PR head. After merge into Develop, require canonical Quality on the resulting Develop SHA before declaring the cluster FIXED. No Skip, XFail, `noqa`, lint-rule weakening, assertion weakening or guard weakening is permitted.
