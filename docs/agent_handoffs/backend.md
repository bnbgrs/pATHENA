# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline: `develop/pathena-next@7c4c8bb52d8e6df819d4a5ff44bbf6442b529d23`.
- Worker branch: `postmerge/backend`.
- History-preserving NON-FORCE synchronization commit: `d93e73be642b09d8719ef2ee8f653bffdb4aed5a` with parents previous Backend head and current Develop.
- `main@0d4d621f8a38ddf8eccfa09622bf193687619943` remains strictly read-only and untouched.

## Selected backend slice

Area: durable deletion-ledger runtime boundaries / recovery cursor.

Spec/error anchor: `ERR-0001` plus backend audit tasks 290-293 and the existing deletion/recovery invariants in `src/athena/lifecycle/deletion.py`.

Root cause on the synchronized lineage was:

- `record_deletion()` called `entity_type.strip()` before requiring an actual string;
- `deleted_at_us < 0` and `deletion_commit_seq <= 0` accepted `bool` because `bool` subclasses `int`;
- `read_deletion_records()` likewise accepted boolean cursors.

Malformed runtime values at these durable mutation/query boundaries must fail before SQL.

## Product fix

Commit `780d25d74ce2e310b6a4bc434f547a23163e8b78` applies only the bounded runtime guards:

- exact `str` requirement before `entity_type.strip()`;
- exact `int` plus non-negative requirement for `deleted_at_us`;
- exact `int` plus positive requirement for `deletion_commit_seq`;
- exact `int` plus non-negative requirement for `after_seq`.

Independent commit-diff inspection confirms that only `src/athena/lifecycle/deletion.py` changed and only those validation blocks/messages were modified. Existing-marker reconciliation, INSERT/readback sequencing, restore replay, transaction boundaries, ordering, identity-conflict semantics and persistence format are unchanged.

## Focused regression harness

Existing Backend commit `de7da517f0cc0cd056de3cbe8aed19db44915884` provides `tests/unit/test_deletion_ledger_boundaries.py` with a no-SQL sentinel covering:

- non-string `entity_type`;
- bool/non-int `deleted_at_us`;
- bool/zero/negative/non-int `deletion_commit_seq`;
- bool/negative/non-int `after_seq`.

Valid `deleted_at_us=0`, `after_seq=0`, and positive integer commit-sequence semantics remain required.

## Verification state

- Branch sync with exact current Develop: COMPLETE via `d93e73be642b09d8719ef2ee8f653bffdb4aed5a`.
- Product mutation: COMPLETE at `780d25d74ce2e310b6a4bc434f547a23163e8b78`.
- Product diff review: COMPLETE; only expected validation blocks changed.
- ATHENA Quality Gate run `33744742408` is associated with exact product/test head `780d25d74ce2e310b6a4bc434f547a23163e8b78` and is currently pending. No PASS claim is made yet.
- Focused/deletion/recovery results must be read from that exact run before Integrator readiness is asserted.

## Failure / recovery impact

The fix is fail-before-SQL and side-effect reducing. It does not change ledger rows, schema, ordering, idempotency, restore transactions, deletion identity reconciliation, crash/restart behavior, or recovery semantics. Invalid values now terminate before database access instead of relying on Python subtype/coercion behavior.

## Platform impact

Platform-neutral Python runtime-boundary hardening only. No Windows/Linux path, packaging, storage-format or provider/transport changes.

## Coordination

- `postmerge/errors`: `ERR-0001` remains Backend-owned until exact-head verification and Integrator handoff; Error worker should independently verify after integration.
- `postmerge/spec-core`: normal-Hybrid Search facade/application wiring is non-overlapping.
- `postmerge/ui`: contextual Inspector work is non-overlapping.
- `develop/pathena-next`: integration target only; no Backend self-integration.

## Integrator handoff

`FIXED_PENDING_VERIFY`, not READY yet. Candidate product/test head: `780d25d74ce2e310b6a4bc434f547a23163e8b78`. Integrate only after exact-head Quality/focused deletion and recovery checks complete successfully. If the run fails, diagnose the precise failure before any further product mutation.

## Next backend slice

First consume exact run `33744742408`. If successful, mark ERR-0001 candidate READY for Integrator and immediately select the next highest unclaimed Backend/System gap from current Alpha/Beta/backlog evidence. If failed, root-cause the exact failure and keep the slice Backend-owned until corrected.
