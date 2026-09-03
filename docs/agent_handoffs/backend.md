# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline: `develop/pathena-next`
- Baseline SHA: `7c15b44818e9ac5c3484ee30d4a20d6f0d56087e`
- Worker branch: `postmerge/backend`
- History-preserving synchronization commit: `4b1eb51ade8fa5633f92c781c72acc4922b4feef`
- `main` remains read-only and was not touched.
- Error worker handoff/ledger checked: `ERR-0001` is confirmed on the current lineage, explicitly Backend-owned, and must not be mutated in parallel by `postmerge/errors`.
- Core/UI/Integrator handoffs checked; no active ownership collision in `src/athena/lifecycle/deletion.py`.

## Selected backend slice

Area: durable deletion-ledger runtime boundaries / recovery cursor.

Anchor: `ERR-0001` plus backend audit tasks 290-293. Current `src/athena/lifecycle/deletion.py` still proves the root cause:

- `record_deletion()` executes `entity_type.strip()` before requiring an actual string;
- `deleted_at_us < 0` and `deletion_commit_seq <= 0` accept `bool` because Python booleans are integer subclasses;
- `read_deletion_records()` likewise accepts `after_seq=False` through its relational check.

These are durable mutation/query boundaries and malformed runtime values must fail before SQL/query side effects.

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

Do not alter the existing existing-marker reconciliation, INSERT/readback sequence, restore replay, transaction, ordering, or identity-conflict semantics.

## Focused acceptance tests

1. `entity_type=None` and other non-strings raise `ValueError` before `connection.execute()`.
2. Empty/whitespace-only strings remain rejected before SQL.
3. `deleted_at_us=False` and non-int values fail before SQL; `0` remains valid.
4. `deletion_commit_seq=True`, zero, negative and non-int values fail before SQL; positive exact ints remain valid.
5. `after_seq=False`, negative and non-int values fail before query execution; `0` remains valid.
6. Existing deletion-ledger integration/recovery tests remain green, specifically idempotent one-marker behavior, restore reapplication, watermark publication and ordered cursor reads.

## Verification state

- Exact current-lineage source re-read: CONFIRMED.
- Existing deletion integration tests were reviewed and already exercise payload-free persistence, one-marker reset behavior, old-snapshot restore reapplication and watermark publication.
- Product mutation this run: NOT APPLIED.
- Reason: the available GitHub write primitive replaces complete UTF-8 files; `deletion.py` is a large recovery-sensitive module. Reconstructing/replacing the entire file only to change these few boundary lines would create unnecessary overwrite risk, violating the worker's minimal/non-destructive mutation rule. No unsafe whole-file rewrite was attempted.
- Therefore no PASS/FIXED claim is made and `ERR-0001` remains open/Backend-owned.

## Failure / recovery impact

The intended change is fail-before-SQL and side-effect reducing. It does not alter ledger rows, persistence format, ordering, idempotent replay, restore transactions, deletion identity reconciliation, or crash/restart behavior. Rejecting `bool` prevents Python's integer-subclass semantics from crossing the SQLite durability/cursor boundary.

## Platform impact

Platform-neutral Python validation. No Windows/Linux storage-format divergence is introduced.

## Integrator handoff

Nothing from `ERR-0001` is product-ready yet. The worker is synchronized history-preservingly with current Develop and the exact safe patch/acceptance contract above is now versioned. Do not integrate a deletion-ledger product change until the focused boundary tests and existing deletion/recovery regressions have actually passed. After a Backend fix integrates, `postmerge/errors` should independently re-verify `ERR-0001` on the exact Develop SHA before marking it FIXED.

## Coordination

- `postmerge/errors`: do not duplicate `ERR-0001` product mutation; verify after integration.
- `postmerge/spec-core`: Search DTO/adapter work is non-overlapping.
- `postmerge/ui`: UI-GAP work is non-overlapping.
- `develop/pathena-next`: remains the only integration target; `main` remains untouched.

## Next backend slice

Continue `ERR-0001` first. Use the smallest patch-capable mutation path available to apply only the runtime guards above, add focused fail-before-SQL tests, then execute the deletion-ledger/lifecycle regressions and canonical Quality as applicable. Only after exact-head verification may this slice be handed to the Integrator as READY.
