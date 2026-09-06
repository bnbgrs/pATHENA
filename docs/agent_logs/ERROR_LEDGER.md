# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

- Stable IDs use `ERR-####`.
- Only reproduced or exact-SHA evidenced failures are opened; cascades are deduplicated under their primary root cause.
- `FIXED` requires real observed verification; unverified corrections remain `FIXED_PENDING_VERIFY`.
- Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`.
- Product defects are fixed in product code; harness defects in the harness. No Skip/XFail, dummy success path, weakened assertion, Ruff/mypy/Validator relaxation, or Security/Storage/Recovery/Windows guard weakening.
- `main` and `bnbgrs/ATHENA` remain read-only.

## Current baseline

- Baseline: `develop/pathena-next@8b6c7a2f44104675570152a5b44fa65979493bc9`.
- Error branch history-preserving NON-FORCE synchronization: `2c8de3800f8ae028f7e8689a24a653a1e5e7cc56` with parents prior Error `f4208cedd9574e6fddcc4cf47dac2694eeab69c8` and current Develop `8b6c7a2f44104675570152a5b44fa65979493bc9`.
- Relevant heads reviewed: Spec/Core `b8858f986ec96e5973d47f8b74d2a120149a2037`; Backend `77ce30acb409881e00f12a9ab78655b81b0cdd1e`; UI `59b2046d5e127664195f7ecf17245c45f70f00ca`; Integrator/Develop `8b6c7a2f44104675570152a5b44fa65979493bc9`.
- `main` and `bnbgrs/ATHENA` were not mutated.

## Current error state

- OPEN: `ERR-0018`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015`, `ERR-0016`, `ERR-0017`.
- STALE: `ERR-0014`.
- BLOCKED: none.

## Entries

### ERR-0001 — Deletion-ledger malformed runtime boundaries
- severity: P2; status: `FIXED`.
- evidence: Backend canonical `33749788522`.
- root_cause: bool-safe runtime validation missing before SQL mutation/cursor boundaries.
- files: `src/athena/lifecycle/deletion.py`, `tests/unit/test_deletion_ledger_boundaries.py`.
- fix_sha: `780d25d74ce2e310b6a4bc434f547a23163e8b78`; harness `2f705d5e0fc1c77dd60612b5aeaa16d9380e46cd`.

### ERR-0002 — Deletion-boundary harness Ruff I001
- severity: P2; status: `FIXED`.
- evidence: `33744816398`; corrected Ruff PASS `33749788522`.
- root_cause: import ordering defect in `tests/unit/test_deletion_ledger_boundaries.py`.
- fix_sha: `2f705d5e0fc1c77dd60612b5aeaa16d9380e46cd`.

### ERR-0003 — Stale permanent-inspector harness contract
- severity: P1; status: `FIXED`.
- evidence: Backend `33755878184`; UI `33745885426` green on affected blobs.
- root_cause: harness contract lagged contextual `Evidence & Activity` behavior.
- fix_sha: `6253577227d427c9bb00707c3e3e578a16c0f9d6`.

### ERR-0004 — Startup/readiness harness canonical Ruff regressions
- severity: P2; status: `FIXED`.
- evidence: `33785726577` B010; `33792012599` I001; exact-head `33804193396 = success`.
- root_cause: bounded startup/readiness test-harness lint defects, not product startup failure.
- files: `tests/unit/test_pathena_startup_experience_2900.py` and related startup harness imports.
- fix_sha: `77e7b4c7d95202e6814226e2b4a2c4a54e3f5c8e`, `a5d9530525bd0b6bf0eae3945c23a6805f6b9669`.

### ERR-0005 — System-tray QApplication ownership typing
- severity: P2; status: `FIXED`; evidence: UI `33822842314`, corrected `33822861477 = success`.
- root_cause: typed `self.app` assignment before runtime `QApplication` narrowing.
- fix_sha: `72e43bc18c28b5c92f6528919abf788f66924ba9`.

### ERR-0006 — Research UUID filter container boundary not runtime-safe
- severity: P2; status: `FIXED`; evidence: Backend `33833499697`, repaired `33838658964 = success`.
- root_cause: missing explicit runtime container/element validation.
- fix_sha: `462fba22637e0083c87df32f987134ce0fb3de00`; integrated equivalent `4b390b4fcc39affc1884f304f460901d07ea622a`.

### ERR-0007 — Missing contradiction-review dependency breaks Core import graph
- severity: P1; status: `FIXED`; evidence: `33838377083`, repaired `33838658964 = success`.
- root_cause: Core integration omitted required contradiction-review dependency.
- fix_sha: `05bca268e2d2fc8e5b0f5ae59c564f2403605540`.

### ERR-0008 — Settings runtime/comprehension harness contract mismatch
- severity: P2; status: `FIXED`; evidence: `33845743958`, `33849890354`, corrected `33854660676 = success`.
- root_cause: harness drift after truthful loopback-only behavior changes.
- fix_sha: `afa319f0ab1b12edccc4b649d4a1ca36bcd7ac39`.

### ERR-0009 — Local HTTP remaining-budget hardening left stale readline harness
- severity: P2; status: `FIXED`; evidence: `33900689788`, Backend `33911612711 = success`.
- root_cause: correct product `remaining + 1` hardening left stale harness expectations.
- fix_sha: Error `67f3f447621c4544a5fb2fe321e76b62347290e0`; Backend `0e966a49cd37d9ee6a4572ac4e35ce3d8018ff8e`.

### ERR-0010 — Direct total-deadline hardening invalidated stream timing harness
- severity: P2; status: `FIXED`; evidence: Backend `33916312429`, recurrences `33933291735`/`33936799048`, corrected `33936396203 = success`, UI `33937005854 = success`.
- root_cause: obsolete timing fixture reintroduced while fail-closed deadline behavior was correct.
- fix_sha: `e62fcc2db49815e7d32579d0dc68a143f8af07b0`.

### ERR-0011 — Unavailable provider leaks fresh accessibility freshness
- severity: P2; status: `FIXED`; evidence: UI `33922277491`, fix `33926653411 = success`.
- root_cause: unavailable provider reused snapshot freshness.
- fix_sha: `9df9d7d46e3c4774aeea5439f91166a2092bd7fb`.

### ERR-0012 — UI synchronization drops unavailable StorageHealth database-path invariant
- severity: P1; status: `FIXED`; evidence: UI `33961422115`, corrected `33966822035 = success`.
- root_cause: UI synchronization retained stale `src/athena/storage/health.py`.
- fix_sha: verified on `77b3f9582d4530dbe081e3c81b8768ad00d3f050`.

### ERR-0013 — UI provider-detail whitespace harness Ruff I001
- severity: P2; status: `FIXED`; evidence: UI `33964058090`, corrected `33966822035 = success`.
- root_cause: non-canonical import block in redundant whitespace harness.
- fix_sha: `77b3f9582d4530dbe081e3c81b8768ad00d3f050`.

### ERR-0014 — Qt Desktop controller test process SIGSEGV
- first_seen: 2026-09-05; severity: P1; status: `STALE`.
- evidence: UI `33975657049` and `33978563758` exited 139; later `33978582156` and `33981877292` succeeded without recurrence.
- root_cause: deterministic product defect unestablished; reopen only on exact signature recurrence.

### ERR-0015 — Negative bounded local-response read harness fabricates overflow byte
- first_seen: 2026-09-06; severity: P2; status: `FIXED`.
- evidence: Backend `34004101347`, `34006604490`; verified `34009044381 = success`.
- root_cause: unbounded fake response fabricated the deliberate overflow-probe byte; product probe was correct.
- fix_sha: `5abee1fb3cf9aa639a2600796036302ef63a773d`.

### ERR-0016 — Local HTTP overflow no longer poisons bounded response
- first_seen: 2026-09-06; severity: P1; status: `FIXED`.
- evidence: Backend `34016515174@c991482a9f49dec50e69779f73e3a0939df5c73b`, `34019237735@a5904fc2078a8dec5eece17dd352436d14453d8f`; corrected Quality `34030367660@54637682087b880622796ee0b618362f7ed802fe = success`.
- root_cause: oversize-before-accounting left `_bytes_read` within budget and removed the implicit poisoned-state marker.
- files: `src/athena/model/adapters/local_http.py`, `tests/unit/test_local_http_response_boundaries.py`, `tests/unit/test_local_http_oversize_accounting.py`.
- fix_sha: `d721846ea9524ab18336ba72eeb082cca7ee0fb8`; regression `44bf215b999e727514fc10ddb88eb8379a5358b6`.
- risks: preserve explicit fail-closed poisoning, `remaining + 1` overflow probe, byte accounting, deadline/type and loopback/proxy/redirect guards.

### ERR-0017 — Integrated Personal Memory service imports missing proposal model
- first_seen: 2026-09-06; severity: P1; status: `FIXED`.
- evidence: Backend `34022137849@d6fca835ad432e05aecbdc3c790a55ec2691a11b`, `34024809050@bc622dcb0554d2449183afe2331669ab15c7c8ef`; corrected Quality `34030367660@54637682087b880622796ee0b618362f7ed802fe = success`.
- root_cause: incomplete bounded Core integration omitted `ModelInferredMemoryProposal`; mypy, pytest collection, Linux/Windows API path and local Core/API restart failures were one cascade.
- files: `src/athena/memory/models.py`, `src/athena/memory/service.py`, `tests/unit/test_personal_memory_inferred_provenance_validation.py`.
- fix_sha: Error `5ff326e39611a3aea5678e2151c300822ad593f9` + `281cedc6010617ce0aa60ea25ec497500225bb17`; Develop equivalent `a7a6301ec580492ee443d2c32e3d65ad624cdcc4` + `dbfcd37e7411447cb6abb4be29731908deff909e`.
- risks: preserve MODEL_INFERRED, confidence, NORMAL sensitivity, real UUID provenance, exact `review_required is True`, and human review control.

### ERR-0018 — Personal Memory context import block violates Ruff I001
- first_seen: 2026-09-06; severity: P2; area: Spec/Core / Personal Memory / Quality source formatting; status: `OPEN`.
- evidence: `34044943935@4ebe23f510a0b36d8f87e027088de54a9809148a = failure`; attempted correction `34048268758@e8f7199f70c56a79403026926430ea56a5177bec = failure`; second attempted correction `34051030897@b8858f986ec96e5973d47f8b74d2a120149a2037 = failure`. All three fail solely at Ruff `I001` on `src/athena/memory/context.py:3:1` while semantic/runtime gates are green.
- exact third verification: Local install/Core-API restart PASS; Windows path safety PASS; Linux storage/API path-boundary PASS; Validator 63/63 PASS; mypy PASS; full pytest `4736 passed, 3 skipped, 2 warnings`; Ruff alone reports `I001 [*] Import block is un-sorted or un-formatted`.
- repro: canonical Quality `34051030897` on exact Spec/Core SHA `b8858f986ec96e5973d47f8b74d2a120149a2037`; canonical diagnostics artifact `canonical-quality-diagnostics-b8858f986ec96e5973d47f8b74d2a120149a2037`.
- root_cause: canonical Ruff/isort normalization of the complete import block remains incorrect. Attempt 1 kept `import uuid` before `from dataclasses import dataclass` but changed the 91-character local import to multiline. Attempt 2 reversed the stdlib order to `from dataclasses import dataclass` before `import uuid` and restored the local import to one line. Both exact forms are rejected. Ruff/isort default semantics place straight imports before from-imports, so the second attempt's stdlib reordering is not a valid canonicalization; however the exact final formatting must be taken from `ruff check --fix`/an exact corrected worker run rather than guessed. This remains a formatting defect, not a semantic Personal Memory defect.
- files: `src/athena/memory/context.py`; focused semantic regression: `tests/unit/test_personal_memory_context.py`.
- fix_sha: none verified. Rejected attempts: `e8f7199f70c56a79403026926430ea56a5177bec`, `b8858f986ec96e5973d47f8b74d2a120149a2037`.
- verification: not fixed. Require exact corrected descendant with Ruff PASS, focused Personal Memory context PASS, full pytest PASS and canonical Quality SUCCESS before changing status.
- risks: import-only correction; preserve `USER PREFERENCE` labeling, active-only projection, duplicate/snapshot identity checks and fail-closed Protected Memory behavior. Do not import the unintegrated Spec/Core feature into Develop/Error merely to satisfy lint.
- integrator_handoff: reject both attempted correction SHAs as READY. Have Spec/Core apply the exact `ruff check --fix` import-block result on its own branch, then verify exact corrected SHA. Error worker must consume that exact evidence before closure.

## Current scan evidence — 2026-09-06

- Spec/Core `b8858f986ec96e5973d47f8b74d2a120149a2037`: Quality `34051030897 = failure`, Ruff-only I001; all other canonical jobs and full pytest green. Continued `ERR-0018`, no new error.
- Backend `77ce30acb409881e00f12a9ab78655b81b0cdd1e`: Quality `34052064954` in progress at scan time; no confirmed independent primary failure yet.
- UI `59b2046d5e127664195f7ecf17245c45f70f00ca`: current head reviewed; no confirmed independent primary failure established in this scan.
- Current Develop `8b6c7a2f44104675570152a5b44fa65979493bc9` contains later integration work but does not contain `src/athena/memory/context.py`; therefore `ERR-0018` is worker-lineage-only at this point and must not be 'fixed' by importing unintegrated feature code onto `postmerge/errors`.
- Current Develop has no exact completed canonical Quality verified in this run; no promotion-ready claim.

## Persistent Beta/release regression knowledge

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded workers; adaptive 2048-context Chat reserve; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.
