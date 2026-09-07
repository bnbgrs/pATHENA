# pATHENA Error Handoff

## Baseline

- Current baseline reviewed: `develop/pathena-next@ef2e991d33539bb267b6744e878ac2ad24cd7266`.
- Error branch mutation lineage: `postmerge/errors` only. No force-push, rebase, history rewrite, or main mutation.
- Current worker heads reviewed: Spec/Core `65b66db6b41bbb0c37ca26437b80bd50ccff1810`; Backend `2feb8be5988793e84f7d7d1c36a99aa8f4cb220f`; UI `27051b50f6e1eebb969232d10459bcf83d77210c`; Integrator/Develop `ef2e991d33539bb267b6744e878ac2ad24cd7266`.
- `spec-core.md`, `backend.md`, `ui.md`, and `integrator.md` were reviewed before this scan; worker heads and current canonical workflow states were independently rechecked.

## Current state

- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015`, `ERR-0016`, `ERR-0017`, `ERR-0018`.
- STALE: `ERR-0014`.
- BLOCKED: `ERR-0019`.
- OPEN: none.

## Canonical evidence consumed this run

- Spec/Core `34095098802@65b66db6b41bbb0c37ca26437b80bd50ccff1810 = failure`; Linux storage PASS, Local install smoke PASS, Windows path safety PASS, Validator PASS, Ruff PASS, mypy PASS; full pytest is the sole failing canonical step.
- Exact worker delta `65b66db6b41bbb0c37ca26437b80bd50ccff1810` adds `test_current_instruction_outranks_conflicting_global_detail_preference` in `tests/unit/test_personal_memory_context_priority.py`.
- Canonical diagnostics artifact `10008929300` exists, but the current connector exposes artifact metadata without the contained pytest traceback. Therefore `ERR-0019` is `BLOCKED` on exact traceback extraction rather than assigned a speculative root cause or fix.
- Backend `34095824663@2feb8be5988793e84f7d7d1c36a99aa8f4cb220f = in_progress`; no concrete primary failure confirmed.
- UI `34097034775@27051b50f6e1eebb969232d10459bcf83d77210c = pending`; no concrete primary failure confirmed.
- Current Develop `ef2e991d33539bb267b6744e878ac2ad24cd7266` has no exact pull-request-triggered canonical Quality run associated with the SHA in this scan; no promotion-ready claim.
- No current Quality/Runtime evidence reproduces any retained Windows packaging/process-tree/chat-context/lane-lock/storage-bootstrap crash signature, so none is reopened.

## ERR-0019 integrator handoff

- HOLD Spec/Core `65b66db6b41bbb0c37ca26437b80bd50ccff1810`; it is not exact canonical green.
- Retrieve the exact pytest diagnostic from Quality run `34095098802`, Python quality job `101656899801`, or diagnostics artifact `10008929300`.
- If the traceback proves expectation drift in the new memory-precedence test, fix only the harness. If it proves product behavior violates current-message-over-durable-preference precedence, apply the minimal product fix in the owning worker scope.
- Do not touch Windows path safety, Storage, Security, Provider/Transport, Recovery, Ruff/mypy/Validator configuration, or use Skip/XFail/dummy success paths.
- `ERR-0004` remains closed and must not be reopened from this unrelated pytest-only signal.

## Persistent Beta/release regression knowledge

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded workers; adaptive 2048-context Chat reserve; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

## Next scan

1. Recover and consume the exact `34095098802` pytest traceback and finalize `ERR-0019` root cause; do not repeat the blocked hypothesis once exact diagnostic becomes available.
2. Consume Backend `34095824663` and UI `34097034775` completion and allocate/reopen only on a concrete deduplicated primary failure.
3. Consume the next exact current Develop/Runtime signal for `ef2e991d33539bb267b6744e878ac2ad24cd7266` or its successor.
4. Keep known Windows/runtime crash classes in the Beta/release regression matrix without reopening absent exact-current reproduction.
