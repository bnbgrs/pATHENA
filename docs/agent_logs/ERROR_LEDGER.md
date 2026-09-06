# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA evidenced failures are opened; cascades are deduplicated. `FIXED` requires real verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, weakened assertion, Ruff/mypy/Validator relaxation, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Baseline reviewed: `develop/pathena-next@8941f823d896e85b58c7f566b45bef04bbfdb84d`.
- Error branch mutation lineage remains on `postmerge/errors`; no `main` mutation, force-push or history rewrite.
- Reviewed heads: Spec/Core `5714f3c7724cb82ccd75a7e852c668bfe78c6d5d`; Backend `74df90dc3b189d397c7a9f18afd0929a25e372bc`; UI `4be3a9c897313f63f8c49ddc6eb9ecfea9186ded`; Integrator/Develop `8941f823d896e85b58c7f566b45bef04bbfdb84d`.

## Current state

- FIXED_PENDING_VERIFY: `ERR-0018`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015`, `ERR-0016`, `ERR-0017`.
- STALE: `ERR-0014`.
- OPEN: none.
- BLOCKED: none.

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

## ERR-0018 — Personal Memory context import block violates Ruff I001

- first_seen: 2026-09-06; severity: P2; area: Spec/Core / Personal Memory / Quality formatting; status: `FIXED_PENDING_VERIFY`.
- failing evidence: `34044943935@4ebe23f510a0b36d8f87e027088de54a9809148a`, `34048268758@e8f7199f70c56a79403026926430ea56a5177bec`, `34051030897@b8858f986ec96e5973d47f8b74d2a120149a2037`, `34054516742@942d19f46a91af6672bb7639c1fca4cadf378ac7`, `34057610329@528ed7d3d7d80470a0fa78458ff2babd59bff20e`; each failed solely Ruff `I001 [*] Import block is un-sorted or un-formatted` at `src/athena/memory/context.py:3:1` while semantic/runtime gates were green.
- corrective evidence: pinned repository Ruff fixer produced commit `61194be6eddf6fa7fe37c9c62690244a29414acd` (`Fix Personal Memory imports with pinned Ruff`). Its only product-file change removes one extra blank line between the `athena.memory.models` import and `PERSONAL_MEMORY_CONTEXT_LABEL`; it does not reorder imports or alter behavior. Cleanup head `5714f3c7724cb82ccd75a7e852c668bfe78c6d5d` removes the temporary one-shot fixer workflow and retains the fixer output.
- root_cause: an extra blank line after the third-party/local import block made the complete import section non-canonical under repository-pinned Ruff `0.15.22`; prior manual ordering/wrapping hypotheses were false. No Personal Memory semantic/runtime defect is evidenced.
- current verification: canonical Quality `34060875144@5714f3c7724cb82ccd75a7e852c668bfe78c6d5d` is in progress. Completed exact-SHA evidence: Windows path safety PASS; Linux storage/API path-boundary PASS; Local install/Core-API restart PASS; Validator PASS; Ruff PASS; mypy PASS. Full pytest is still running, so `FIXED` is not yet permitted.
- files: `src/athena/memory/context.py`; focused regression `tests/unit/test_personal_memory_context.py`.
- fix_sha: `61194be6eddf6fa7fe37c9c62690244a29414acd`; exact candidate verification SHA: `5714f3c7724cb82ccd75a7e852c668bfe78c6d5d`.
- verification requirement: canonical Quality `34060875144` must complete successfully with full pytest PASS on exact SHA `5714f3c...`; only then move to `FIXED`.
- risks: preserve `USER PREFERENCE`, active-only projection, duplicate/snapshot identity checks and fail-closed Protected Memory behavior. Temporary fixer workflow was removed; no permanent CI write path remains.
- integrator_handoff: hold Spec/Core `5714f3c...` pending completion of exact canonical Quality. Ruff root cause is concretely fixed; do not re-edit import ordering/wrapping unless new exact contradictory evidence appears.

## Current scan evidence — 2026-09-07

- Spec/Core `5714f3c7724cb82ccd75a7e852c668bfe78c6d5d`: Quality `34060875144` in progress; Ruff/Validator/mypy/Windows/Linux/local-install completed PASS; full pytest running.
- Backend `74df90dc3b189d397c7a9f18afd0929a25e372bc`: Quality `34061317620` in progress; no confirmed independent primary failure at scan.
- UI `4be3a9c897313f63f8c49ddc6eb9ecfea9186ded`: Quality `34061905305` in progress; no confirmed independent primary failure at scan.
- Develop `8941f823d896e85b58c7f566b45bef04bbfdb84d`: current baseline reviewed; no exact completed canonical Quality verified by Error this run; no promotion-ready claim.

## Persistent Beta/release regression knowledge

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded workers; adaptive 2048-context Chat reserve; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.
