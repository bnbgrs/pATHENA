# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

- Stable IDs use `ERR-####`.
- Only reproduced or exact-SHA evidenced failures are opened.
- Cascades are deduplicated under the primary root cause.
- `FIXED` requires real observed verification; unverified corrections remain `FIXED_PENDING_VERIFY`.
- Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`.
- Product defects are fixed in product code; harness defects are fixed in the harness.
- No Skip/XFail, dummy success path, weakened assertions, Ruff/mypy/Validator relaxation, or Security/Storage/Recovery/Windows guard weakening.
- `main` and `bnbgrs/ATHENA` remain read-only.

## Current baseline

- Baseline: `develop/pathena-next@86ab95c9bd31e52a8d65fd3b37f7c27556a6f3b9`.
- Error branch pre-sync head: `b8e050c9756299a70e8f5d4df0139ef54a5f08a0`.
- History-preserving NON-FORCE synchronization: `28017c9cfb1c39623dd860dcaf30ac099fdd0ada`, parents prior Error head + exact Develop, using exact Develop tree before Error-owned mutation.
- Relevant Backend head: `bc622dcb0554d2449183afe2331669ab15c7c8ef`.
- Relevant Spec/Core head: `96c8f17d99017060238da27b51f6e59b77b9eafc`.
- Relevant UI head: `6558031bb31e5e35f5c8639bf4f5c8591f7fa250`.
- No force update, rebase, history rewrite, ATHENA mutation, or merge to `main` occurred.

## Current error state

- OPEN: none.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: `ERR-0016`, `ERR-0017`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015`.
- STALE: `ERR-0014`.
- BLOCKED: none.

## Entries

### ERR-0001 — Deletion-ledger malformed runtime boundaries
- severity: P2
- status: `FIXED`
- evidence: canonical Backend `33749788522`.
- root_cause: bool-safe runtime validation missing before SQL mutation/cursor boundaries.
- files: `src/athena/lifecycle/deletion.py`, `tests/unit/test_deletion_ledger_boundaries.py`.
- fix_sha: `780d25d74ce2e310b6a4bc434f547a23163e8b78`; harness `2f705d5e0fc1c77dd60612b5aeaa16d9380e46cd`.

### ERR-0002 — Deletion-boundary harness Ruff I001
- severity: P2
- status: `FIXED`
- evidence: Ruff failure `33744816398`; Ruff PASS `33749788522`.
- root_cause: import ordering defect in `tests/unit/test_deletion_ledger_boundaries.py`.
- fix_sha: `2f705d5e0fc1c77dd60612b5aeaa16d9380e46cd`.

### ERR-0003 — Stale permanent-inspector harness contract
- severity: P1
- status: `FIXED`
- evidence: Backend `33755878184`; UI `33745885426` green on affected blobs.
- root_cause: test contract lagged contextual `Evidence & Activity` behavior.
- fix_sha: `6253577227d427c9bb00707c3e3e578a16c0f9d6`.

### ERR-0004 — Startup/readiness harness canonical Ruff regressions
- severity: P2
- status: `FIXED`
- evidence: `33785726577` B010; `33792012599` I001; exact-head `33804193396 = success`.
- root_cause: bounded startup/readiness test-harness lint defects, not product startup failure.
- files: `tests/unit/test_pathena_startup_experience_2900.py` and related startup harness imports.
- fix_sha: `77e7b4c7d95202e6814226e2b4a2c4a54e3f5c8e`, `a5d9530525bd0b6bf0eae3945c23a6805f6b9669`.

### ERR-0005 — System-tray QApplication ownership typing
- severity: P2
- status: `FIXED`
- evidence: UI `33822842314`; corrected `33822861477 = success`.
- root_cause: typed `self.app` assignment before runtime `QApplication` narrowing.
- fix_sha: `72e43bc18c28b5c92f6528919abf788f66924ba9`.

### ERR-0006 — Research UUID filter container boundary not runtime-safe
- severity: P2
- status: `FIXED`
- evidence: Backend `33833499697`; repaired `33838658964 = success`.
- root_cause: missing explicit runtime container/element validation.
- fix_sha: `462fba22637e0083c87df32f987134ce0fb3de00`; integrated equivalent `4b390b4fcc39affc1884f304f460901d07ea622a`.

### ERR-0007 — Missing contradiction-review dependency breaks Core import graph
- severity: P1
- status: `FIXED`
- evidence: `33838377083`; repaired `33838658964 = success`.
- root_cause: Core integration omitted required contradiction-review dependency.
- fix_sha: `05bca268e2d2fc8e5b0f5ae59c564f2403605540`.

### ERR-0008 — Settings runtime/comprehension harness contract mismatch
- severity: P2
- status: `FIXED`
- evidence: `33845743958`, `33849890354`; fix Quality `33854660676 = success`.
- root_cause: harness drift after truthful loopback-only behavior changes.
- fix_sha: `afa319f0ab1b12edccc4b649d4a1ca36bcd7ac39`.

### ERR-0009 — Local HTTP remaining-budget hardening left stale readline harness
- severity: P2
- status: `FIXED`
- evidence: `33900689788`; Backend `33911612711 = success`.
- root_cause: correct product `remaining + 1` hardening left stale harness expectations.
- fix_sha: Error `67f3f447621c4544a5fb2fe321e76b62347290e0`; Backend `0e966a49cd37d9ee6a4572ac4e35ce3d8018ff8e`.

### ERR-0010 — Direct total-deadline hardening invalidated stream timing harness
- severity: P2
- status: `FIXED`
- evidence: Backend `33916312429`, recurrences `33933291735`/`33936799048`; corrected Backend `33936396203 = success`, UI `33937005854 = success`.
- root_cause: obsolete timing fixture reintroduced while fail-closed deadline behavior was correct.
- fix_sha: `e62fcc2db49815e7d32579d0dc68a143f8af07b0`.

### ERR-0011 — Unavailable provider leaks fresh accessibility freshness
- severity: P2
- status: `FIXED`
- evidence: UI `33922277491`; fix `33926653411 = success`.
- root_cause: unavailable provider reused snapshot freshness.
- fix_sha: `9df9d7d46e3c4774aeea5439f91166a2092bd7fb`.

### ERR-0012 — UI synchronization drops unavailable StorageHealth database-path invariant
- severity: P1
- status: `FIXED`
- evidence: UI `33961422115`; corrected `33966822035 = success`.
- root_cause: UI synchronization retained stale `src/athena/storage/health.py`.
- fix_sha: verified on `77b3f9582d4530dbe081e3c81b8768ad00d3f050`.

### ERR-0013 — UI provider-detail whitespace harness Ruff I001
- severity: P2
- status: `FIXED`
- evidence: UI `33964058090`; corrected `33966822035 = success`.
- root_cause: non-canonical import block in redundant whitespace harness.
- fix_sha: `77b3f9582d4530dbe081e3c81b8768ad00d3f050`.

### ERR-0014 — Qt Desktop controller test process SIGSEGV
- first_seen: 2026-09-05
- severity: P1
- status: `STALE`
- evidence: UI `33975657049` and `33978563758` exited 139; later `33978582156` and `33981877292` succeeded without recurrence.
- root_cause: deterministic product defect unestablished; reopen only on exact signature recurrence.

### ERR-0015 — Negative bounded local-response read harness fabricates overflow byte
- first_seen: 2026-09-06
- severity: P2
- status: `FIXED`
- evidence: Backend `34004101347`, `34006604490`; verified `34009044381 = success`.
- root_cause: unbounded fake response fabricated the deliberate overflow-probe byte; product probe was correct.
- fix_sha: `5abee1fb3cf9aa639a2600796036302ef63a773d`.

### ERR-0016 — Local HTTP overflow no longer poisons bounded response
- first_seen: 2026-09-06
- severity: P1
- area: Backend / Provider-Transport / local HTTP product safety
- status: `FIXED_PENDING_VERIFY`
- evidence: Backend `34016515174@c991482a9f49dec50e69779f73e3a0939df5c73b` and `34019237735@a5904fc2078a8dec5eece17dd352436d14453d8f` reproduced exactly two poisoning failures.
- root_cause: oversize-before-accounting left `_bytes_read` within budget and removed the implicit poisoned-state marker.
- files: `src/athena/model/adapters/local_http.py`, `tests/unit/test_local_http_response_boundaries.py`, `tests/unit/test_local_http_oversize_accounting.py`.
- fix_sha: product `d721846ea9524ab18336ba72eeb082cca7ee0fb8`; regression `44bf215b999e727514fc10ddb88eb8379a5358b6`.
- verification: independent `ERR-0017` import failure prevented complete canonical closure; reverify poisoning/oversize semantics after import graph repair.

### ERR-0017 — Integrated Personal Memory service imports missing proposal model
- first_seen: 2026-09-06
- severity: P1
- area: Core / Personal Memory / Integration / Startup import graph
- status: `FIXED_PENDING_VERIFY`
- evidence: Backend `34022137849@d6fca835ad432e05aecbdc3c790a55ec2691a11b` and current Backend `34024809050@bc622dcb0554d2449183afe2331669ab15c7c8ef` fail through the same missing-symbol import graph. Current Develop `86ab95c9bd31e52a8d65fd3b37f7c27556a6f3b9` still imports `ModelInferredMemoryProposal` from `src/athena/memory/service.py` while `src/athena/memory/models.py` lacks it.
- root_cause: incomplete bounded Core integration: reviewed-inference service semantics landed without the required proposal-model dependency. mypy failure, pytest collection errors, Linux/Windows API runtime path-boundary failures and local Core/API restart failure are cascades under this single root cause.
- files: `src/athena/memory/models.py`, `src/athena/memory/service.py`, `tests/unit/test_personal_memory_inferred_provenance_validation.py`.
- worker_evidence: Spec/Core `96c8f17d99017060238da27b51f6e59b77b9eafc` contains the compatible model and focused provenance regression; canonical Quality `34024071953 = success`. Earlier exact-green source `a43a471b611c78d24ebb8c67253b855b6a0642f3`, Quality `34021606032 = success`.
- fix_sha: Error product `5ff326e39611a3aea5678e2151c300822ad593f9`; regression `281cedc6010617ce0aa60ea25ec497500225bb17`.
- correction: add only `ModelInferredMemoryProposal` with MODEL_INFERRED, confidence, NORMAL-sensitivity, real UUID provenance, and exact `review_required is True` validation; no service bypass or guard weakening.
- verification_required: focused inferred-proposal/review/provenance tests, Ruff, mypy, local Core/API restart, Linux/Windows API path-boundary, full pytest and exact canonical Quality on the corrected Error SHA. Only then mark `FIXED`.

## Persistent Beta/release regression matrix

Retain without automatically reopening unless reproduced on an exact current candidate:

- Windows `pypdf` metadata / `PackageNotFoundError` plus supervisor relaunch behavior.
- Fail-closed frozen child argv and two-EXE Desktop/Worker split.
- Exactly one Desktop process and bounded/non-growing Worker population.
- Adaptive Chat output reserve for 2048-token LM-Studio contexts.
- Windows lane-lock cluster: `_lock_nonblocking` `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`.
- `duplicate column name: source_processing_job_id`.
- `ATHENA Core startup failed`.
- `Failed to start service 'storage-bootstrap'`.

Any recurrence on an exact Beta/release candidate blocks promotion until root cause is closed with real verification.
