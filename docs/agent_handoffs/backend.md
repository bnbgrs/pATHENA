# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline: `develop/pathena-next`
- Baseline SHA: `280066cc5450f172693e2ee913bd269b6755f7bb`
- Worker branch: `postmerge/backend`
- History-preserving synchronization commit: `100bfbf458e0bd4a90c6f8b100823e698bcd79e4`
- `main` remains strictly read-only and was not touched.
- Synchronization was NON-FORCE. Develop-only changes to `docs/agent_handoffs/integrator.md` and `docs/development/ALPHA_BETA_PROGRESS.md` were preserved; Backend-only `docs/agent_handoffs/backend.md` and `tests/unit/test_deletion_ledger_boundaries.py` were preserved.

## Selected backend slice

Area: durable deletion-ledger runtime boundaries / recovery cursor.

Anchor: `ERR-0001` plus backend audit tasks 290-293.

Current `src/athena/lifecycle/deletion.py` still proves the root cause:

- `record_deletion()` calls `entity_type.strip()` before requiring an actual string;
- `deleted_at_us < 0` and `deletion_commit_seq <= 0` accept `bool` because `bool` subclasses `int`;
- `read_deletion_records()` likewise accepts `after_seq=False`.

Malformed runtime values at these durable mutation/query boundaries must fail before SQL.

## Focused regression harness

Commit `de7da517f0cc0cd056de3cbe8aed19db44915884` adds `tests/unit/test_deletion_ledger_boundaries.py` with a no-SQL sentinel and covers:

- non-string `entity_type`;
- bool/non-int `deleted_at_us`;
- bool/zero/negative/non-int `deletion_commit_seq`;
- bool/negative/non-int `after_seq`.

Valid `deleted_at_us=0`, `after_seq=0`, and positive integer commit sequence semantics remain required.

Canonical Quality run `33728141579` for the focused-test lineage completed `cancelled`; it is not PASS evidence.

## Required product contract

Before any SQL operation in `record_deletion()`:

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

Before SQL in `read_deletion_records()`:

```python
if type(after_seq) is not int or after_seq < 0:
    raise ValueError("Deletion ledger cursor must be a non-negative integer.")
```

Do not alter existing-marker reconciliation, INSERT/readback sequencing, restore replay, transaction boundaries, ordering, identity-conflict semantics, or persistence format.

## Mutation status

`ERR-0001` remains OPEN/BACKEND_OWNED; no production guard was changed in this run.

The previous tooling blocker is materially reduced: the GitHub connector now exposes the complete exact `deletion.py` blob (`446ebd69c3fbc286bad66c5076cec2e6a36250f8`) in addition to line-range reads. Therefore the next run can construct a byte-for-byte-preserving replacement with only the two validation blocks changed instead of reconstructing from truncated reads.

## Verification state

- Current Develop baseline traced: CONFIRMED.
- Worker synchronized with Develop: CONFIRMED via `100bfbf458e0bd4a90c6f8b100823e698bcd79e4`.
- Root cause on synchronized lineage: CONFIRMED.
- Focused regression harness retained: CONFIRMED.
- Product fix: NOT YET APPLIED.
- Canonical Quality: no PASS claim for ERR-0001.

Required post-fix regressions remain payload-free persistence, idempotent marker reconciliation, deletion restore replay, watermark publication, ordered cursor reads, crash/restart-sensitive lifecycle behavior, and the focused fail-before-SQL boundary harness.

## Failure / recovery impact

The intended fix is fail-before-SQL and side-effect reducing. It must not change ledger rows, schema, ordering, idempotency, restore transactions, deletion identity reconciliation, crash/restart behavior, or recovery semantics.

## Platform impact

Platform-neutral Python runtime-boundary hardening. No Windows/Linux path or storage-format divergence.

## Coordination

- `postmerge/errors`: `ERR-0001` remains Backend-owned; do not mutate the same root cause in parallel. Independently verify after integration.
- `postmerge/spec-core`: current Search facade/application work is non-overlapping.
- `postmerge/ui`: current UI-GAP work is non-overlapping.
- `develop/pathena-next`: only integration target; `main` remains untouched.

## Integrator handoff

NOT READY. Do not integrate the ERR-0001 slice yet. The Backend worker is synchronized with Develop and the reproducing test is preserved, but a product fix and exact-head verification are still required.

## Next backend slice

Apply the exact runtime guards to the complete verified `deletion.py` blob, then execute the focused boundary harness plus deletion/lifecycle recovery regressions. If those pass, run canonical Quality on the same product/test worker lineage and hand the exact SHA to the Integrator.
