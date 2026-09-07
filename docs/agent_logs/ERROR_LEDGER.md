# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA evidenced failures are opened; cascades are deduplicated. `FIXED` requires real verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, weakened assertion, Ruff/mypy/Validator relaxation, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Baseline reviewed: `develop/pathena-next@30dd27c97e948e59994e8cfbe01b1c77ce6c917b`.
- Error branch mutation lineage remains `postmerge/errors` only.
- Previous Error head: `3e726c52fa9a509c6b5d88789272cff43d9bfc81`.
- History-preserving NON-FORCE synchronization merge: `1dc57faec1206889066b8a9bfb91ffc64a91bfb5`, parents `3e726c52fa9a509c6b5d88789272cff43d9bfc81` and `30dd27c97e948e59994e8cfbe01b1c77ce6c917b`.
- Reviewed worker heads: Spec/Core `c6b4fdba485a1de249a93e99883fca4085b9fc48`; Backend `a4696e2647c485465a82764b081562a5b34c6b08`; UI `fd0780d23b081fddb8a236971c74f4cb3c565899`; Integrator/Develop `30dd27c97e948e59994e8cfbe01b1c77ce6c917b`.
- Required `spec-core.md`, `backend.md`, `ui.md`, `integrator.md`, relevant worker branch heads and current canonical workflow state were reviewed before mutation.

## Current state

- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015`, `ERR-0016`, `ERR-0017`, `ERR-0018`, `ERR-0019`.
- STALE: `ERR-0014`.
- IN_PROGRESS: none.
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
- `ERR-0018` P2 FIXED — Personal Memory context Ruff I001; Ruff fixer `61194be6eddf6fa7fe37c9c62690244a29414acd`; exact canonical success `34060875144@5714f3c7724cb82ccd75a7e852c668bfe78c6d5d`, later `34063688754@12e2e98d10c3fc11821ffa8f5edead80806da009 = success`.
- `ERR-0019` P2 FIXED — Personal Memory precedence harness drift across canonical serializer key, repository read API and persisted revision identity; complete fix `c7cd4d9b1e0889a00b4599dfe76738442378b17b`; exact canonical Quality `34110957854 = success` with Windows path safety, Linux storage, local install, Validator, Ruff, mypy and full pytest PASS.

## Current scan evidence — 2026-09-07 20:03 CEST

- Spec/Core head `c6b4fdba485a1de249a93e99883fca4085b9fc48`: prior exact canonical Quality `34127196867 = success`; no current error signal.
- Backend Develop-compatible WAL lane-hook application `caf72c43cd84b208429f99982a8a0c291f61b67b`: exact canonical Quality `34147793827 = success`.
- Backend current documentation descendant `a4696e2647c485465a82764b081562a5b34c6b08`: canonical Quality `34147831223` is in progress. Linux storage, local install, Windows path safety, Validator, Ruff and mypy are completed PASS; full pytest is still running. No confirmed primary failure.
- UI predecessor `7fe5d44e4271dcbec6c0bfba92e0a01a0671b69f`: exact canonical Quality `34144645412 = success`; UI-GAP-0066 was subsequently integrated on Develop.
- UI current `fd0780d23b081fddb8a236971c74f4cb3c565899`, carrying the UI-GAP-0067 accessibility candidate: canonical Quality `34148642145` is in progress. Linux storage, local install, Windows path safety, Validator, Ruff and mypy are completed PASS; full pytest is still running. No confirmed primary failure.
- Develop exact `30dd27c97e948e59994e8cfbe01b1c77ce6c917b`: no pull-request-triggered workflow run is associated with this exact SHA in the current scan; no promotion-ready claim.
- No current Quality/Runtime evidence reproduces retained Windows packaging/process-tree/chat-context/lane-lock/storage-bootstrap crash signatures; none is reopened.
- `ERR-0004` remains FIXED; the historical startup/readiness Ruff signature did not recur in current exact worker evidence.

## Persistent Beta/release regression knowledge

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

Before Beta/release promotion, explicitly execute the known-crash regression matrix on the exact candidate SHA. No promotion-ready claim is allowed while a known crash signature is reproducible on that candidate.
