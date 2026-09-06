# pATHENA Error Handoff

## Baseline

- Baseline source: `develop/pathena-next@451b2f39377653b44fb178e58d86705b6026bef8`.
- Worker branch: `postmerge/errors`.
- Pre-run Error head: `0049ca90d1687b1c5ea8722895e1c9f2a1fe9e76`.
- History-preserving NON-FORCE synchronization: `4fc852b66715eb42d402d8cab97d70c67175a394`, with parents prior Error head and exact Develop.
- Current Backend head reviewed: `d6fca835ad432e05aecbdc3c790a55ec2691a11b`.
- Current Spec/Core head reviewed: `a43a471b611c78d24ebb8c67253b855b6a0642f3`.
- Current UI head reviewed: `8cbec3ef97a13caf626450a0111ee3dc50b262cc`.
- `main` and `bnbgrs/ATHENA` remain strictly read-only; no force update, rebase, history rewrite or merge to main was attempted.

## Current error state

- OPEN: `ERR-0017`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: `ERR-0016`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015`.
- STALE: `ERR-0014`.
- BLOCKED: none.

## ERR-0016 — correction exists, canonical closure blocked by independent import failure

Backend product fix `d721846ea9524ab18336ba72eeb082cca7ee0fb8` introduces explicit `_byte_budget_poisoned`; regression commit `44bf215b999e727514fc10ddb88eb8379a5358b6` proves rejected bytes do not advance successful accounting while follow-up body access is blocked before delegate I/O. Current Backend documentation descendant is `d6fca835ad432e05aecbdc3c790a55ec2691a11b`.

Canonical Quality `34022137849@d6fca835ad432e05aecbdc3c790a55ec2691a11b` is red, but not because the poisoning signature recurred. Its primary failure is the independent Personal-Memory import-graph defect now tracked as `ERR-0017`; mypy and pytest abort before ERR-0016 can receive complete canonical verification. Keep `ERR-0016` as `FIXED_PENDING_VERIFY`, preserve the poison fix, and reverify it on an exact descendant after the import graph is repaired.

## ERR-0017 — current Develop has a broken Personal-Memory import graph

Canonical Backend Quality `34022137849@d6fca835ad432e05aecbdc3c790a55ec2691a11b = failure` provides exact diagnostics:

- specification Validator: PASS;
- Ruff: PASS;
- mypy: FAIL at `src/athena/memory/service.py:16` because `athena.memory.models` has no attribute `ModelInferredMemoryProposal`;
- full pytest: collection aborts with 147 errors, all rooted in `ImportError: cannot import name 'ModelInferredMemoryProposal' from 'athena.memory.models'`;
- Linux storage focused storage regressions pass, then API runtime path-boundary regressions fail through the same import graph;
- Windows deterministic locality/storage checks pass, then API runtime path-boundary regressions fail through the same import graph;
- local-install smoke fails the disposable Core/API restart through the same import graph.

This is one primary root cause, not separate Storage/Windows/pytest/local-start defects.

Current `develop/pathena-next@451b2f39377653b44fb178e58d86705b6026bef8` already imports and uses `ModelInferredMemoryProposal` in `src/athena/memory/service.py`, but its `src/athena/memory/models.py` does not define the class. The integration therefore combined reviewed-inference service semantics without its required model dependency.

The active Spec/Core worker already has the compatible missing contract: `postmerge/spec-core@a43a471b611c78d24ebb8c67253b855b6a0642f3` defines `ModelInferredMemoryProposal` with MODEL_INFERRED, confidence, NORMAL-sensitivity, UUID provenance and exact `review_required=True` validation. Exact canonical Spec/Core Quality `34021606032@a43a471b611c78d24ebb8c67253b855b6a0642f3 = success`. Its handoff explicitly states that current Develop already integrates reviewed-inference acceptance while the missing verified provenance-boundary blobs include `src/athena/memory/models.py`.

No duplicate Error-branch product implementation is introduced because a current active worker correction is already exact-green. This run instead finalizes the root cause and binds the verified correction source, satisfying the progress rule without creating colliding product mutations.

## Required integrator action

Compose the bounded compatible `ModelInferredMemoryProposal` dependency from exact-green Spec/Core lineage `a43a471b611c78d24ebb8c67253b855b6a0642f3` onto current Develop. Do not remove the service import or weaken review/provenance validation to make collection pass.

After composition, require on the exact resulting SHA:

- mypy;
- focused Personal-Memory inferred-proposal / review-acceptance / provenance tests;
- disposable local Core/API restart smoke;
- API runtime path-boundary regressions on Linux and Windows;
- full pytest;
- canonical ATHENA Quality completion.

Only then set `ERR-0017` to `FIXED`. The same corrected descendant should also run focused local HTTP poisoning/oversize-accounting coverage so `ERR-0016` can move from `FIXED_PENDING_VERIFY` to `FIXED` if its signature remains absent.

## Other worker evidence

- Spec/Core `a43a471b611c78d24ebb8c67253b855b6a0642f3`: canonical Quality `34021606032 = success`; contains the missing proposal model dependency.
- UI `8cbec3ef97a13caf626450a0111ee3dc50b262cc`: Jobs detail focus candidate remains UI-owned and disjoint.
- Current Develop `451b2f39377653b44fb178e58d86705b6026bef8`: no repository-wide green claim is valid while `ERR-0017` remains present.

## Persistent Beta/release regression knowledge

Retain as release-acceptance knowledge without reopening absent exact-current reproduction:

- Windows missing `pypdf` metadata / `PackageNotFoundError` and supervisor relaunch;
- frozen child argv recursion, preserving fail-closed routing and two-EXE split;
- exactly one Desktop and bounded/non-growing Workers;
- adaptive output reserve at 2048 LM-Studio context;
- Windows lane-lock `_lock_nonblocking` `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`;
- `duplicate column name: source_processing_job_id`;
- `ATHENA Core startup failed`;
- `Failed to start service 'storage-bootstrap'`.

Any recurrence on an exact Beta/release candidate blocks promotion until root cause is closed with real verification.

## Next scan

1. Consume the first exact Develop/integrated candidate containing the compatible Spec/Core proposal-model dependency and close `ERR-0017` only on real evidence.
2. On that same corrected lineage, reverify `ERR-0016` poisoning + oversize-accounting semantics and close only if focused/canonical evidence is green.
3. Immediately after those closures, consume the next real canonical/runtime failure signal; allocate a new stable ID only for a concrete deduplicated primary cause.
