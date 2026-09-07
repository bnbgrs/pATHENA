# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA evidenced failures are opened; cascades are deduplicated. `FIXED` requires real verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, weakened assertion, Ruff/mypy/Validator relaxation, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Baseline reviewed: `develop/pathena-next@ef2e991d33539bb267b6744e878ac2ad24cd7266`.
- Error branch mutation lineage remains on `postmerge/errors`; no main mutation, force-push or history rewrite.
- Reviewed heads: Spec/Core `65b66db6b41bbb0c37ca26437b80bd50ccff1810`; Backend `2feb8be5988793e84f7d7d1c36a99aa8f4cb220f`; UI `27051b50f6e1eebb969232d10459bcf83d77210c`; Integrator/Develop `ef2e991d33539bb267b6744e878ac2ad24cd7266`.
- `spec-core.md`, `backend.md`, `ui.md`, and `integrator.md` were reviewed before this scan; exact worker branch heads and canonical Quality state were independently rechecked.

## Current state

- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015`, `ERR-0016`, `ERR-0017`, `ERR-0018`.
- STALE: `ERR-0014`.
- BLOCKED: `ERR-0019`.
- OPEN: none.

## Historical verified entries

- `ERR-0001` P2 FIXED — deletion-ledger malformed runtime boundaries; Backend `33749788522`; fix `780d25d74ce2e310b6a4bc434f547a23163e8b78`, harness `2f705d5e0fc1c77dd60612b5aeaa16d9380e46cd`.
- `ERR-0002` P2 FIXED — deletion-boundary Ruff I001; corrected `33749788522`; fix `2f705d5e0fc1c77dd60612b5aeaa16d9380e46cd`.
- `ERR-0003` P1 FIXED — stale permanent-inspector harness contract; Backend `33755878184`, UI `33745885426`; fix `6253577227d427c9bb00707c3e3e578a16c0f9d6`.
- `ERR-0004` P2 FIXED — startup/readiness harness Ruff B010/I001; `33785726577`, `33792012599`, exact green `33804193396`; fixes `77e7b4c7d95202e6814226e2b4a2c4a54e3f5c8e`, `a5d9530525bd0b6bf0eae3945c23a6805f6b9669`.
- `ERR-0005` P2 FIXED — system-tray QApplication ownership typing; UI `33822861477 = success`; fix `72e43bc18c28b5c92f6528919abf788f66924ba9`.
- `ERR-0006` P2 FIXED — research UUID filter runtime container validation; Backend `33838658964 = success`; fix `462fba22637e0083c87df32f987134ce0fb3de00`.
- `ERR-0007` P1 FIXED — missing contradiction-review dependency; `33838658964 = success`; fix `05bca268e2d2fc8e5b0f5ae59c564f2403605540`.
- `ERR-0008` P2 FIXED — settings runtime/comprehension harness drift; `33854660676 = success`; fix `afa319f0ab1b12edccc4b649d4a1ca36bcd7ac39`.
- `ERR-0009` P2 FIXED — local HTTP remaining-budget stale readline harness; Backend `33911612711 = success`; Error fix `67f3f447621c4544a5fb2fe321e76b62347290e0`.
- `ERR-0010` P2 FIXED — total-deadline hardening timing harness drift; corrected `33936396203 = success`; fix `e62fcc2db49815e7d32579d0dc68a143f8af07b0`.
- `ERR-0011` P2 FIXED — unavailable provider accessibility freshness leak; UI `33926653411 = success`; fix `9df9d7d46e3c4774aeea5439f91166a2092bd7fb`.
- `ERR-0012` P1 FIXED — UI synchronization dropped StorageHealth database-path invariant; UI `33966822035 = success`; verified SHA `77b3f9582d4530dbe081e3c81b8768ad00d3f050`.
- `ERR-0013` P2 FIXED — UI provider-detail Ruff I001; UI `33966822035 = success`; fix `77b3f9582d4530dbe081e3c81b8768ad00d3f050`.
- `ERR-0014` P1 STALE — Qt Desktop controller SIGSEGV in `33975657049`/`33978563758`; later `33978582156`/`33981877292` succeeded; reopen only on exact recurrence.
- `ERR-0015` P2 FIXED — fake bounded-response harness fabricated overflow byte; Backend `34009044381 = success`; fix `5abee1fb3cf9aa639a2600796036302ef63a773d`.
- `ERR-0016` P1 FIXED — local HTTP overflow poisoning regression; corrected Quality `34030367660@54637682087b880622796ee0b618362f7ed802fe = success`; fix `d721846ea9524ab18336ba72eeb082cca7ee0fb8`, regression `44bf215b999e727514fc10ddb88eb8379a5358b6`.
- `ERR-0017` P1 FIXED — integrated Personal Memory service omitted `ModelInferredMemoryProposal`; corrected Quality `34030367660@54637682087b880622796ee0b618362f7ed802fe = success`; Error fixes `5ff326e39611a3aea5678e2151c300822ad593f9` + `281cedc6010617ce0aa60ea25ec497500225bb17`.
- `ERR-0018` P2 FIXED — Personal Memory context Ruff I001; pinned Ruff fixer commit `61194be6eddf6fa7fe37c9c62690244a29414acd`; exact canonical success `34060875144@5714f3c7724cb82ccd75a7e852c668bfe78c6d5d`, later `34063688754@12e2e98d10c3fc11821ffa8f5edead80806da009 = success`.

## ERR-0019 — Spec/Core canonical pytest failure

- Severity: P2.
- Status: `BLOCKED` pending exact failing-test diagnostic extraction.
- Evidence: canonical ATHENA Quality Gate `34095098802` on exact Spec/Core SHA `65b66db6b41bbb0c37ca26437b80bd50ccff1810` completed `failure`; Linux storage, Local install smoke, Windows path safety, specification validator, Ruff and mypy all PASS; `Quality — pytest` is the sole failing canonical step.
- Triggering worker delta: commit `65b66db6b41bbb0c37ca26437b80bd50ccff1810` adds `test_current_instruction_outranks_conflicting_global_detail_preference` in `tests/unit/test_personal_memory_context_priority.py` and asserts the current-message-overrides-durable-preference policy without mutating durable memory.
- Root cause: not yet finalized. The canonical diagnostics artifact exists (`canonical-quality-diagnostics-65b66db6b41bbb0c37ca26437b80bd50ccff1810`, artifact `10008929300`), but the available GitHub connector exposes artifact metadata while not exposing the contained pytest traceback/log payload; no speculative test/product fix is permitted without the exact assertion/traceback.
- Files: `tests/unit/test_personal_memory_context_priority.py`; exact product root-cause file unknown until traceback is recovered.
- Fix SHA: none.
- Verification: no PASS/FIXED claim.
- Risk: do not attribute this to Windows, Storage, Ruff, mypy or Validator; those canonical jobs are green on the same SHA.
- Integrator handoff: hold Spec/Core `65b66db6b41bbb0c37ca26437b80bd50ccff1810`; retrieve exact pytest diagnostic from run `34095098802`/artifact `10008929300`, then either correct the harness if expectation drift is proven or product code if behavior violates the current-message precedence contract.

## Current scan evidence — 2026-09-07 10:00 CEST

- Spec/Core exact `65b66db6b41bbb0c37ca26437b80bd50ccff1810`: canonical Quality `34095098802 = failure`; sole canonical failing step is full pytest. `ERR-0019` allocated and blocked on traceback extraction rather than guessed.
- Backend exact `2feb8be5988793e84f7d7d1c36a99aa8f4cb220f`: canonical Quality `34095824663 = in_progress`; no confirmed primary failure yet.
- UI exact `27051b50f6e1eebb969232d10459bcf83d77210c`: canonical Quality `34097034775 = pending`; no jobs/diagnostic failure established yet.
- Develop exact `ef2e991d33539bb267b6744e878ac2ad24cd7266`: no exact pull-request-triggered canonical Quality run is currently associated with this SHA; no promotion-ready claim.
- `ERR-0004` remains FIXED and is not reopened; the current concrete signal is `ERR-0019`.

## Persistent Beta/release regression knowledge

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded workers; adaptive 2048-context Chat reserve; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.
