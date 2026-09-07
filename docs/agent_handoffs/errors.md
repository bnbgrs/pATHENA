# pATHENA Error Handoff

## Baseline

- Current baseline reviewed: `develop/pathena-next@0a19ab7fbd8944fbe38768dcba1d6c3710bfd656`.
- Error branch mutation lineage: `postmerge/errors` only. History-preserving NON-FORCE synchronization merge: `1f085d098b0bb4ee33848b821da51e28a3cca6fc`.
- Current worker heads reviewed: Spec/Core `a033f07472b7c32f932da37b4659b047d19e0482`; Backend `afd4fce6d4005a88bc3a4bdd3233531e041ffcbb`; UI `4a4efbe417809fe8cc5d7f1ecb3aa4f4861f63d7`; Integrator/Develop `0a19ab7fbd8944fbe38768dcba1d6c3710bfd656`.
- `spec-core.md`, `backend.md`, `ui.md`, and `integrator.md` were reviewed before this scan; worker heads and canonical workflow states were independently rechecked.

## Current state

- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015`, `ERR-0016`, `ERR-0017`, `ERR-0018`.
- STALE: `ERR-0014`.
- IN_PROGRESS: `ERR-0019`.
- OPEN: none.

## Canonical evidence consumed this run

- Initial Spec/Core `34095098802@65b66db6b41bbb0c37ca26437b80bd50ccff1810 = failure`; full pytest alone failed while Linux storage, Local install smoke, Windows path safety, Validator, Ruff and mypy passed.
- The initial delta added only `test_current_instruction_outranks_conflicting_global_detail_preference`.
- Spec/Core then made a harness-only correction at `a033f07472b7c32f932da37b4659b047d19e0482`: the expected serialized preference changed from `revision_no` to canonical `context_id: MEM-001`. This confirms one concrete root-cause layer: expectation drift in the new harness, not a product mutation.
- Exact follow-up canonical Quality `34099534536@a033f07472b7c32f932da37b4659b047d19e0482 = failure`; Local install, Linux storage, Windows path safety, Validator, Ruff and mypy all PASS; full pytest remains the sole failing step. Therefore the harness correction is only partial and `ERR-0019` remains active.
- The available connector still does not expose the remaining pytest traceback/log payload. Do not infer whether the residual failure is another assertion mismatch or a product defect.
- Backend `34100925468@afd4fce6d4005a88bc3a4bdd3233531e041ffcbb = in_progress`; no concrete primary failure confirmed.
- UI `34102329189@4a4efbe417809fe8cc5d7f1ecb3aa4f4861f63d7 = pending`; no concrete primary failure confirmed.
- Current Develop `0a19ab7fbd8944fbe38768dcba1d6c3710bfd656` has no exact completed canonical success established in this scan; no promotion-ready claim.
- No current Quality/Runtime evidence reproduces retained Windows packaging/process-tree/chat-context/lane-lock/storage-bootstrap crash signatures, so none is reopened.

## ERR-0019 integrator handoff

- HOLD Spec/Core `a033f07472b7c32f932da37b4659b047d19e0482`; it is canonical-red.
- Treat `a033f07472b7c32f932da37b4659b047d19e0482` only as a partial harness correction: it fixes the known `revision_no`/`context_id` serializer expectation mismatch but does not verify the new precedence test.
- Recover the exact residual pytest diagnostic from Quality run `34099534536`, Python quality job `101670548332`, or its diagnostics artifact/log payload and finish `ERR-0019` without allocating a duplicate.
- If the residual traceback proves expectation drift, change only the harness. If it proves actual behavior violates current-message-over-durable-preference precedence, fix the smallest product scope.
- Do not touch Windows path safety, Storage, Security, Provider/Transport, Recovery, Ruff/mypy/Validator configuration, or use Skip/XFail/dummy success paths.
- `ERR-0004` remains closed.

## Persistent Beta/release regression knowledge

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded workers; adaptive 2048-context Chat reserve; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

## Next scan

1. Consume the exact residual pytest diagnostic for `34099534536@a033f07472b7c32f932da37b4659b047d19e0482` and finalize `ERR-0019` root cause; do not repeat the already-confirmed serializer-expectation layer.
2. Consume Backend `34100925468` and UI `34102329189` completion and allocate/reopen only on a concrete deduplicated primary failure.
3. Consume the next exact current Develop/Runtime signal for `0a19ab7fbd8944fbe38768dcba1d6c3710bfd656` or its successor.
4. Keep known Windows/runtime crash classes in the Beta/release regression matrix without reopening absent exact-current reproduction.
