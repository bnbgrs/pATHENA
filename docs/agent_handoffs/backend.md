# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline: `develop/pathena-next`
- Baseline SHA: `edae673243cfea9114302bd0b52655a7034b106e`
- Worker branch: `postmerge/backend`
- History-preserving synchronization commit: `374313e9d64bf7cb173df96cce3b5c238cd5afbe`
- `main` remains read-only and was not touched.
- Error worker handoff/ledger checked: `ERR-0001` remains confirmed and Backend-owned; `postmerge/errors` must not mutate the same root cause in parallel.
- Core/UI/Integrator handoffs checked; no active ownership collision in `src/athena/lifecycle/deletion.py`.

## Selected backend slice

Area: durable deletion-ledger runtime boundaries / recovery cursor.

Anchor: `ERR-0001` plus backend audit tasks 290-293. Current `src/athena/lifecycle/deletion.py` still proves the root cause:

- `record_deletion()` executes `entity_type.strip()` before requiring an actual string;
- `deleted_at_us < 0` and `deletion_commit_seq <= 0` accept `bool` because Python booleans are integer subclasses;
- `read_deletion_records()` likewise accepts `after_seq=False` through its relational check.

These are durable mutation/query boundaries and malformed runtime values must fail before SQL/query side effects.

## New focused regression harness

Commit `de7da517f0cc0cd056de3cbe8aed19db44915884` adds `tests/unit/test_deletion_ledger_boundaries.py`.

The new test file uses a no-SQL connection sentinel and asserts that malformed runtime inputs fail with `ValueError` before any `connection.execute()` call:

- non-string `entity_type` values;
- bool/non-int `deleted_at_us` values;
- bool/zero/negative/non-int `deletion_commit_seq` values;
- bool/negative/non-int `after_seq` values.

The tests deliberately preserve valid zero timestamp/cursor and positive commit-sequence semantics. No production guard was weakened or bypassed.

ATHENA Quality Gate run `33728141579` targets exact test-bearing worker SHA `de7da517f0cc0cd056de3cbe8aed19db44915884` and is currently pending. No PASS claim is made.

## Required product contract

Apply exact runtime validation before the first SQL operation:

```python
if type(entity_type) is not str:
    raise ValueError("Deletion entity_type must be a string.")

normalized_type = entity_type.strip()
if not normalized_type:
    raise ValueError("Deletion entity_type must not be empty.")

if type(deleted_at_us) is not int or deleted_at_us < 0:
    raise ValueError("Deletion timestamp must be a non-negative integer.")

if type(deletion_commit_seq) is not int or deletion_commit_seq <= 0:
    raise ValueError("Deletion commit sequence must be a positive integer.")
```

and at the read boundary:

```python
if type(after_seq) is not int or after_seq < 0:
    raise ValueError("Deletion ledger cursor must be a non-negative integer.")
```

Do not alter existing-marker reconciliation, INSERT/readback sequence, restore replay, transaction, ordering, or identity-conflict semantics.

## Verification state

- Exact current-lineage source re-read: CONFIRMED.
- Focused regression test commit: `de7da517f0cc0cd056de3cbe8aed19db44915884`.
- Canonical Quality run: `33728141579` PENDING on the exact test-bearing SHA.
- Product mutation: NOT YET APPLIED; `ERR-0001` remains OPEN/BACKEND_OWNED.
- Existing deletion integration tests remain the required post-fix regression set: payload-free persistence, one-marker/idempotent replay, old-snapshot restore reapplication, watermark publication and ordered cursor reads.

## Failure / recovery impact

The intended product change is fail-before-SQL and side-effect reducing. It does not alter ledger rows, persistence format, ordering, idempotent replay, restore transactions, deletion identity reconciliation, or crash/restart behavior. Explicit bool rejection prevents Python integer-subclass semantics from crossing SQLite durability/cursor boundaries.

## Platform impact

Platform-neutral Python validation. No Windows/Linux storage-format or path-semantics divergence is introduced.

## Integrator handoff

Not product-ready yet. The worker is current with Develop and now has a focused regression harness pinned to the exact root cause. Do not integrate `ERR-0001` until the product guards are applied and the focused tests plus deletion/recovery regressions pass on the exact worker SHA. After integration, `postmerge/errors` should independently re-verify the exact Develop SHA before marking the ledger entry FIXED.

## Coordination

- `postmerge/errors`: do not duplicate `ERR-0001` product mutation; verify after integration.
- `postmerge/spec-core`: Search DTO/adapter work is non-overlapping.
- `postmerge/ui`: UI-GAP work is non-overlapping.
- `develop/pathena-next`: remains the only integration target; `main` remains untouched.

## Next backend slice

Continue `ERR-0001` first. Apply only the exact runtime guards above, run `tests/unit/test_deletion_ledger_boundaries.py`, then the existing deletion-ledger/lifecycle regressions and canonical Quality. Only exact-head verification can make the product commit READY for the Integrator.
