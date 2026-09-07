# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA evidenced failures are opened; cascades are deduplicated. `FIXED` requires real verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, weakened assertion, Ruff/mypy/Validator relaxation, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Baseline reviewed: `develop/pathena-next@aed6afdfa23f1ef3d90abe05cbecd790727ed016`.
- Error branch mutation lineage remains `postmerge/errors` only; no force, rebase, history rewrite or main mutation was performed.
- Reviewed current worker heads: Spec/Core `cce6f200059d972958c9c971db2d7ad9d73ce2de`; Backend `607319fa41abdea0e468523f2c653e1fd84cfc82`; UI `1de30b1df309954399a3a47cc485b7517ecf9ce1`; Integrator/Develop `aed6afdfa23f1ef3d90abe05cbecd790727ed016`.
- Required handoff files were reviewed; branch heads and canonical Quality state were independently rechecked.

## Current state

- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015`, `ERR-0016`, `ERR-0017`, `ERR-0018`.
- STALE: `ERR-0014`.
- IN_PROGRESS: `ERR-0019`.
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
- Status: `IN_PROGRESS`.
- Initial evidence: canonical Quality `34095098802@65b66db6b41bbb0c37ca26437b80bd50ccff1810 = failure`; Linux storage, Local install smoke, Windows path safety, Validator, Ruff and mypy PASS; full pytest sole failure.
- Triggering delta: new `test_current_instruction_outranks_conflicting_global_detail_preference` in `tests/unit/test_personal_memory_context_priority.py`.
- Root-cause layer 1 CONFIRMED: harness expected serialized `revision_no` although `_render_context()` canonically emits `context_id`; Spec/Core `a033f07472b7c32f932da37b4659b047d19e0482` corrected the expectation to `context_id: MEM-001` without product mutation.
- Root-cause layer 2 CONFIRMED by subsequent owner correction: the same harness called nonexistent/noncanonical `PersonalMemoryRepository.get()` for state-before/state-after checks; Spec/Core `cce6f200059d972958c9c971db2d7ad9d73ce2de` replaced both calls with the repository's actual `load_current()` contract and changed no product file.
- Exact verification after layer 2: canonical Quality `34105038031@cce6f200059d972958c9c971db2d7ad9d73ce2de = failure`; Linux storage PASS, Local install smoke PASS, Windows path safety PASS, Validator PASS, Ruff PASS, mypy PASS, and full pytest remains the sole failing step. Therefore layers 1 and 2 are real harness defects but remain insufficient to close `ERR-0019`.
- Residual root cause: not finalized. Quality diagnostics artifact `10012806334` exists for exact run `34105038031`, but the available GitHub connector exposes artifact metadata rather than the text payload and rejects the job-log endpoint; local network cloning is unavailable in the automation runtime. No speculative third fix is permitted.
- Files: `tests/unit/test_personal_memory_context_priority.py`; exact residual product/root-cause file remains unknown pending the failing traceback/assertion.
- Fix SHA: none accepted as complete. `a033f074...` and `cce6f200...` are partial harness corrections only; both exact follow-up states remained canonical-red.
- Verification: NO PASS/FIXED claim.
- Risk: do not attribute the residual to Windows, Storage, Ruff, mypy or Validator because all are green on the exact current failing SHA. Do not allocate a duplicate error.
- Integrator handoff: HOLD Spec/Core `cce6f200059d972958c9c971db2d7ad9d73ce2de`; recover the exact remaining pytest traceback/assertion from `34105038031`/job `101687991088`/artifact `10012806334` and finish this same `ERR-0019`.

## Current scan evidence — 2026-09-07 12:xx CEST

- Spec/Core exact `cce6f200059d972958c9c971db2d7ad9d73ce2de`: canonical Quality `34105038031 = failure`; pytest only.
- Backend exact `607319fa41abdea0e468523f2c653e1fd84cfc82`: canonical Quality `34106290925 = in_progress`; no confirmed primary failure yet.
- UI exact `1de30b1df309954399a3a47cc485b7517ecf9ce1`: canonical Quality `34107416188 = in_progress`; no confirmed primary failure yet.
- Develop exact `aed6afdfa23f1ef3d90abe05cbecd790727ed016`: no exact completed pull-request-triggered canonical Quality success established in this scan; no promotion-ready claim.
- `ERR-0004` remains FIXED and is not reopened.

## Persistent Beta/release regression knowledge

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded workers; adaptive 2048-context Chat reserve; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.
