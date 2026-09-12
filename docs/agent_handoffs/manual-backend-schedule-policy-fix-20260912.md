# Backend missed-run policy canonical-test repair — 2026-09-12

## Exact lineage

- Backend source candidate: `postmerge/backend@f99f352050cbbcda889cd2a528d95c415992f3ec`.
- Isolated repair branch: `manual/backend-schedule-policy-fix-20260912`.
- Product repair commit: `9b242c9fdbeac8b0523a391f9b9a84d1086641a9`.
- The active `postmerge/backend` ref was not mutated.

## Failure evidence

Backend canonical Quality run `34675706788@f99f352050cbbcda889cd2a528d95c415992f3ec` completed with:

- specification validator: SUCCESS;
- Ruff: SUCCESS;
- mypy: SUCCESS;
- Windows path safety: SUCCESS;
- Linux storage regressions: SUCCESS;
- Local install smoke: SUCCESS;
- full pytest: FAILURE with exactly 7 failures in `tests/unit/test_schedule_policy.py` and `4896 passed, 3 skipped`.

Every failure traces to `_canonical_occurrences()`:

```python
zip(occurrences, occurrences[1:], strict=True)
```

The two iterables are intentionally different lengths because the code wants adjacent pairs. `strict=True` therefore raises `ValueError: zip() argument 2 is shorter than argument 1` for any non-empty occurrence tuple before the missed-run policy can execute.

The broken commit was itself named `fix(jobs): satisfy strict zip lint in missed-run policy`, so this is a concrete example where a lint-only correction changed runtime semantics.

## Repair

Use `itertools.pairwise(occurrences)` for the strictly-increasing validation:

```python
if any(left >= right for left, right in pairwise(occurrences)):
    raise ValueError(...)
```

This directly expresses the intended adjacent-pair operation, avoids the Ruff B905 `zip(..., strict=...)` concern entirely, and preserves the existing fail-closed ordering/uniqueness check.

No test expectations, policy semantics, scheduler persistence, job state or Storage behavior are changed.

## Existing regression coverage

The canonical failure already provides adequate semantic coverage. `tests/unit/test_schedule_policy.py` checks:

- SKIP drops due missed occurrences;
- RUN_ONCE materializes only the latest due occurrence;
- BACKFILL_ALL preserves due order and excludes future occurrences;
- BACKFILL_BOUNDED materializes only the oldest bounded set;
- duplicate/out-of-order occurrences fail closed;
- timestamp validation rejects booleans/negative values;
- bounded policy validates `max_backfill`;
- non-bounded policies reject stray `max_backfill`;
- empty/future-only occurrence sets create no work.

Do not weaken these tests to accommodate the broken `strict=True` implementation.

## Bot coordination rules

1. Do not repeat `strict=True` on `zip(occurrences, occurrences[1:])`; those iterables are intentionally unequal length.
2. Prefer `pairwise()` for adjacent-order validation so lint and semantics agree structurally.
3. Do not mutate `postmerge/backend` directly from this repair lane. Backend can consume this bounded one-file fix after exact CI evidence.
4. The canonical Errors worker should register this as a current exact-SHA failure if its next ledger refresh still sees `f99f3520...` or an equivalent reproducer. Do not invent an `ERR-####` ID in this handoff.
5. This schedule-policy failure is independent of `ERR-0035 / BE-052`; do not mix the code paths or closure evidence.
6. No Skip/XFail, assertion weakening, test deletion or force-push.
7. If Backend advances before consumption, compare `src/athena/jobs/schedule_policy.py` first. Reapply the semantic `pairwise()` fix only if the broken `strict=True` form remains.

## Required verification

Before Backend consumes this fix:

- Ruff SUCCESS;
- mypy SUCCESS;
- `tests/unit/test_schedule_policy.py` SUCCESS;
- Backend Focused SUCCESS if triggered;
- canonical full pytest SUCCESS on an exact unchanged candidate SHA or, at minimum, no remaining `test_schedule_policy.py` failures plus classification of any unrelated red test.
