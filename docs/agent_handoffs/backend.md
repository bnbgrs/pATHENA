# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline: `develop/pathena-next@96489c4c493992ff9d8c7efd57557a69aa578e56`.
- Stable read-only branch: `main@0d4d621f8a38ddf8eccfa09622bf193687619943` (unchanged).
- Worker branch: `postmerge/backend`.
- Previous worker head: `eaafbea79e2ae99158b213304eccaf4b29811f94`.
- History-preserving synchronization merge: `0ee051eac32cd6156d464475571ee1b0995999b0` with parents `eaafbea79e2ae99158b213304eccaf4b29811f94` and `96489c4c493992ff9d8c7efd57557a69aa578e56`.

## Synchronization result

The previous direct branch merge was non-mergeable because Backend and Develop had diverged. This run reconciled them without force, rebase or history rewrite by creating an explicit two-parent merge commit on `postmerge/backend`.

The merge tree is based on the exact current Develop tree and preserves only the already verified bounded Backend product delta:

- `src/athena/resources/manager.py`: `ResourceManager.set_mode()` rejects non-`ResourceMode` runtime values before `ensure_local_user()` or any database mutation.
- `tests/unit/test_resource_mode_boundary.py`: focused invalid-runtime and valid-enum coverage.

Develop-side Search provenance/protection work is retained unchanged. No `main` mutation occurred.

## Verification

Canonical ATHENA Quality Gate run `33718973461` targets exact synchronized Backend SHA `0ee051eac32cd6156d464475571ee1b0995999b0`.

Observed during this run:

- Local install smoke: SUCCESS.
- Linux storage regressions: SUCCESS.
- Python 3.12 quality: specification validator SUCCESS, Ruff SUCCESS, mypy SUCCESS; full pytest still in progress at last observation.
- Windows path safety: deterministic locality regressions SUCCESS; remaining storage/path checks still in progress at last observation.

No final global PASS is claimed until the run completes.

## Current owned root cause — ERR-0001 / tasks 290-293

`postmerge/errors` records `ERR-0001` and explicitly assigns product ownership to Backend. Current `src/athena/lifecycle/deletion.py` still has four related durable-boundary gaps:

1. `record_deletion(entity_type=...)` calls `.strip()` before an explicit runtime text-type check.
2. `deleted_at_us` uses a raw relational check, so `bool` is accepted as an integer and malformed types can raise uncontrolled comparison errors.
3. `deletion_commit_seq` has the same exact-int/bool-safe gap.
4. `read_deletion_records(after_seq=...)` has the same cursor gap.

Required contract: fail before SQL/query side effects, require actual non-empty `str` for `entity_type`, exact nonnegative `int` for `deleted_at_us` and `after_seq`, exact positive `int` for `deletion_commit_seq`, explicitly reject `bool`, and preserve existing idempotent deletion-marker replay/conflict semantics.

## Collision avoidance

- Error worker must not patch `src/athena/lifecycle/deletion.py` in parallel; it owns ledger verification, not this product fix.
- Core Search DTO/facade work does not overlap this slice.
- UI work does not overlap this slice.

## Integrator handoff

The ResourceMode delta is now on a current Develop-compatible history-preserving Backend lineage at `0ee051eac32cd6156d464475571ee1b0995999b0`. Integrator may independently review this merge lineage and exact-head Quality result once complete.

No deletion-ledger fix commit is ready yet in this run. The next Backend mutation remains one coherent `ERR-0001` slice with focused tests proving malformed values fail before SQL access, bool rejection, valid boundary acceptance, unchanged idempotent replay behavior and unchanged ordered cursor semantics.

## Next backend slice

1. Resolve `ERR-0001` / tasks 290-293 in `src/athena/lifecycle/deletion.py` plus focused deletion-ledger regressions.
2. Re-run the focused ledger tests and relevant storage/recovery regressions.
3. If green, hand the exact product/test SHA to Integrator and Error worker for independent current-lineage verification.
4. Then continue to the next highest unclaimed Backend/System gap, currently external-gateway input boundaries unless fresher exact-lineage evidence supersedes it.
