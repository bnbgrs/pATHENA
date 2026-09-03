# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline: `develop/pathena-next`
- Baseline SHA: `5eb99f4cc3baed1f4eef23a54d686d109a7da21c`
- Worker branch: `postmerge/backend`
- History-preserving synchronization commit: `a1723c6cdc9e5b161db5d8df688f1772e55d29cc`
- `main` remains read-only and was not touched.
- ERR-0001 remains Backend-owned; `postmerge/errors` must not mutate the same root cause in parallel.
- Core/Search changes integrated on Develop are disjoint from the deletion-ledger files; synchronization preserved both histories without force.

## Selected backend slice

Area: durable deletion-ledger runtime boundaries / recovery cursor.

Anchor: `ERR-0001` plus backend audit tasks 290-293. Current `src/athena/lifecycle/deletion.py` still proves the root cause:

- `record_deletion()` executes `entity_type.strip()` before requiring an actual string;
- `deleted_at_us < 0` and `deletion_commit_seq <= 0` accept `bool` because Python booleans are integer subclasses;
- `read_deletion_records()` likewise accepts `after_seq=False` through its relational check.

These are durable mutation/query boundaries and malformed runtime values must fail before SQL/query side effects.

## Focused regression harness

Commit `de7da517f0cc0cd056de3cbe8aed19db44915884` adds `tests/unit/test_deletion_ledger_boundaries.py`.

The test uses a no-SQL connection sentinel and asserts that malformed runtime inputs fail with `ValueError` before any `connection.execute()` call:

- non-string `entity_type` values;
- bool/non-int `deleted_at_us` values;
- bool/zero/negative/non-int `deletion_commit_seq` values;
- bool/negative/non-int `after_seq` values.

The harness preserves valid zero timestamp/cursor and positive commit-sequence semantics. No production guard is weakened or bypassed.

Canonical Quality run `33728141579` for exact test-bearing SHA `de7da517f0cc0cd056de3cbe8aed19db44915884` completed with conclusion `cancelled`; it is therefore not PASS evidence.

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

## Mutation status

Product mutation is still intentionally not applied in this run. The available repository write primitive replaces a complete UTF-8 file; `src/athena/lifecycle/deletion.py` is a large recovery-sensitive module. Although the exact blob and relevant call chain were re-read, a whole-file reconstruction solely to alter these guards creates unnecessary overwrite risk. The worker therefore records the exact surgical patch contract rather than risking loss of unrelated recovery logic.

## Verification state

- Exact current-lineage source re-read: CONFIRMED.
- Focused regression test commit: `de7da517f0cc0cd056de3cbe8aed19db44915884`.
- Canonical Quality run: `33728141579` = COMPLETED/CANCELLED, not PASS.
- Product mutation: NOT YET APPLIED; `ERR-0001` remains OPEN/BACKEND_OWNED.
- Existing deletion integration tests remain required post-fix regressions: payload-free persistence, one-marker/idempotent replay, old-snapshot restore reapplication, watermark publication and ordered cursor reads.

## Failure / recovery impact

The intended product change is fail-before-SQL and side-effect reducing. It does not alter ledger rows, persistence format, ordering, idempotent replay, restore transactions, deletion identity reconciliation, or crash/restart behavior. Explicit bool rejection prevents Python integer-subclass semantics from crossing SQLite durability/cursor boundaries.

## Platform impact

Platform-neutral Python validation. No Windows/Linux storage-format or path-semantics divergence is introduced.

## Integrator handoff

Not product-ready yet. Backend is synchronized with current Develop and retains the focused regression harness. Do not integrate ERR-0001 until the exact product guards are applied and the focused tests plus deletion/recovery regressions pass on the same worker SHA. After integration, `postmerge/errors` should independently re-verify the exact Develop SHA before marking the ledger entry FIXED.

## Coordination

- `postmerge/errors`: do not duplicate ERR-0001 product mutation; verify after integration.
- `postmerge/spec-core`: Search DTO/adapter and facade wiring remain non-overlapping.
- `postmerge/ui`: UI-GAP work remains non-overlapping.
- `develop/pathena-next`: remains the only integration target; `main` remains untouched.

## Next backend slice

Continue ERR-0001 first. Use a safe surgical mutation route for the exact runtime guards, run `tests/unit/test_deletion_ledger_boundaries.py`, then the existing deletion-ledger/lifecycle regressions and canonical Quality. Only exact-head verification can make the product commit READY for the Integrator.
