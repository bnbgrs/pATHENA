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

- Baseline: `develop/pathena-next@abfe054654ae69994ad22d5a1079aeae42fba09f`.
- Error branch was history-preservingly NON-FORCE synchronized through merge `8ebc23b3138469d9633303023513dadc735b67ed` from prior Error head `79a3aa4eaedf53b81d3d3499d5102ae58d6dbb5a` plus current Develop.
- Relevant Backend head: `4f09ad222547f279e27fb3d34285feb82f6a8f71`.
- Relevant Spec/Core head: `e8f7199f70c56a79403026926430ea56a5177bec`.
- Relevant UI head: `c9762d1b65dd6c9db1c30ae9cba9510f83ab942f`.
- No ATHENA mutation or merge to `main` occurred.

## Current error state

- OPEN: `ERR-0018`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015`, `ERR-0016`, `ERR-0017`.
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
- status: `FIXED`
- evidence: Backend `34016515174@c991482a9f49dec50e69779f73e3a0939df5c73b` and `34019237735@a5904fc2078a8dec5eece17dd352436d14453d8f` reproduced exactly two poisoning failures; corrected-lineage canonical Quality `34030367660@54637682087b880622796ee0b618362f7ed802fe = success`.
- root_cause: oversize-before-accounting left `_bytes_read` within budget and removed the implicit poisoned-state marker.
- files: `src/athena/model/adapters/local_http.py`, `tests/unit/test_local_http_response_boundaries.py`, `tests/unit/test_local_http_oversize_accounting.py`.
- fix_sha: product `d721846ea9524ab18336ba72eeb082cca7ee0fb8`; regression `44bf215b999e727514fc10ddb88eb8379a5358b6`; consolidated corrected-lineage Local HTTP blob verified at `54637682087b880622796ee0b618362f7ed802fe`.
- verification: Quality `34030367660` passes Validator, Ruff, mypy, full pytest, local Core/API restart smoke, Linux storage + API runtime path boundaries, and Windows locality/storage + API runtime path boundaries on the corrected lineage. Full pytest includes the poisoning/oversize regressions and the signature is absent.
- risks: preserve explicit fail-closed poisoning, `remaining + 1` overflow probe, byte-budget accounting, type/deadline and loopback/proxy/redirect guards.
- integrator_handoff: closed; do not weaken or reimplement the verified boundary semantics.

### ERR-0017 — Integrated Personal Memory service imports missing proposal model
- first_seen: 2026-09-06
- severity: P1
- area: Core / Personal Memory / Integration / Startup import graph
- status: `FIXED`
- evidence: Backend `34022137849@d6fca835ad432e05aecbdc3c790a55ec2691a11b` and `34024809050@bc622dcb0554d2449183afe2331669ab15c7c8ef` reproduced the missing-symbol import cascade; corrected-lineage canonical Quality `34030367660@54637682087b880622796ee0b618362f7ed802fe = success` after the bounded model dependency was integrated.
- root_cause: incomplete bounded Core integration: reviewed-inference service semantics landed without the required `ModelInferredMemoryProposal` dependency. mypy failure, pytest collection errors, Linux/Windows API runtime path-boundary failures and local Core/API restart failure were cascades under this single root cause.
- files: `src/athena/memory/models.py`, `src/athena/memory/service.py`, `tests/unit/test_personal_memory_inferred_provenance_validation.py`.
- worker_evidence: exact-green Spec/Core sources provided the compatible model and focused provenance regression; Develop integrated equivalent product/test commits `a7a6301ec580492ee443d2c32e3d65ad624cdcc4` and `dbfcd37e7411447cb6abb4be29731908deff909e`.
- fix_sha: Error product `5ff326e39611a3aea5678e2151c300822ad593f9`; regression `281cedc6010617ce0aa60ea25ec497500225bb17`; Develop equivalent `a7a6301ec580492ee443d2c32e3d65ad624cdcc4` + `dbfcd37e7411447cb6abb4be29731908deff909e`.
- verification: canonical Quality `34030367660` on corrected descendant `54637682087b880622796ee0b618362f7ed802fe` passes Validator, Ruff, mypy, full pytest, disposable Core/API restart smoke, Linux API runtime path boundary and Windows API runtime path boundary; the import/startup cascade is absent.
- risks: preserve MODEL_INFERRED, confidence, NORMAL sensitivity, real UUID provenance, exact `review_required is True`, and human review control.
- integrator_handoff: closed; do not reapply the structural fix. Current Develop still requires its own exact-SHA Quality before any promotion-ready claim.

### ERR-0018 — Personal Memory context import block violates Ruff I001
- first_seen: 2026-09-06
- severity: P2
- area: Spec/Core / Personal Memory / Quality source formatting
- status: `OPEN`
- evidence: initial exact Spec/Core `34044943935@4ebe23f510a0b36d8f87e027088de54a9809148a = failure` reported `I001 Import block is un-sorted or un-formatted` at `src/athena/memory/context.py:3:1`; first correction `e8f7199f70c56a79403026926430ea56a5177bec` then failed exact canonical Quality `34048268758` again solely at Ruff while Validator, mypy, full pytest, local install/Core-API restart, Linux storage/API path-boundary and Windows path safety all passed.
- repro: canonical Quality on both exact SHAs; the semantic/runtime suite remains green and Ruff alone rejects the import block.
- root_cause: first correction changed only the 91-character `athena.memory.models` import from a valid-width single line to a parenthesized multiline form and left stdlib order as `import uuid` before `from dataclasses import dataclass`. With repository Ruff `line-length=100` and `I` enabled, the remaining root cause is canonical isort ordering/formatting of this import block, specifically `dataclasses` before `uuid` and the local import remaining single-line, subject to exact Ruff verification.
- files: `src/athena/memory/context.py`.
- fix_sha: first attempted correction `e8f7199f70c56a79403026926430ea56a5177bec` is rejected by Quality `34048268758`; no verified fix SHA yet.
- verification: not fixed; require exact corrected descendant with Ruff PASS, focused `tests/unit/test_personal_memory_context.py` PASS, full pytest PASS, and canonical Quality success.
- risks: import-only correction; preserve `USER PREFERENCE` labeling, active-only projection, duplicate/snapshot identity checks, and fail-closed Protected Memory behavior.
- integrator_handoff: reject both `4ebe23f510a0b36d8f87e027088de54a9809148a` and `e8f7199f70c56a79403026926430ea56a5177bec` as READY. Do not repeat the multiline-only mutation; correct canonical ordering/format only and rerun exact Quality.

## Current scan evidence — 2026-09-06

- Spec/Core `postmerge/spec-core@e8f7199f70c56a79403026926430ea56a5177bec`, canonical Quality `34048268758 = failure`: local install smoke PASS, Linux storage/API path-boundary PASS, Windows path safety PASS, Validator PASS, mypy PASS, full pytest PASS; Ruff alone FAIL. This is continued `ERR-0018`, not a new error.
- Backend `postmerge/backend@4f09ad222547f279e27fb3d34285feb82f6a8f71`, canonical Quality `34048748410` is in progress; no independent confirmed primary failure was established from completed evidence inspected this run.
- UI `postmerge/ui@c9762d1b65dd6c9db1c30ae9cba9510f83ab942f`; no independent confirmed primary failure was established in this scan.
- Current Develop `abfe054654ae69994ad22d5a1079aeae42fba09f` has no exact completed canonical Quality verified in this scan and is not promotion-ready by Error criteria.

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
