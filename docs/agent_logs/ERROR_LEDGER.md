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

- Baseline branch: `develop/pathena-next`.
- Baseline SHA observed this run: `451b2f39377653b44fb178e58d86705b6026bef8`.
- Error branch pre-run head: `0049ca90d1687b1c5ea8722895e1c9f2a1fe9e76`.
- History-preserving NON-FORCE synchronization: `4fc852b66715eb42d402d8cab97d70c67175a394`, with parents prior Error head and exact Develop; tree equals exact Develop before Error-owned documentation mutation.
- Relevant Backend head: `d6fca835ad432e05aecbdc3c790a55ec2691a11b`.
- Relevant Spec/Core head: `a43a471b611c78d24ebb8c67253b855b6a0642f3`.
- Relevant UI head: `8cbec3ef97a13caf626450a0111ee3dc50b262cc`.
- No force update, rebase, history rewrite or merge to `main` was attempted.

## Current error state

- OPEN: `ERR-0017`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: `ERR-0016`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015`.
- STALE: `ERR-0014`.
- BLOCKED: none.

## Entries

### ERR-0001 — Deletion-ledger malformed runtime boundaries
- severity: P2
- status: `FIXED`
- evidence: canonical Backend `33749788522`.
- root_cause: bool-safe runtime validation was missing before SQL mutation/cursor boundaries.
- files: `src/athena/lifecycle/deletion.py`, `tests/unit/test_deletion_ledger_boundaries.py`.
- fix_sha: `780d25d74ce2e310b6a4bc434f547a23163e8b78`; harness `2f705d5e0fc1c77dd60612b5aeaa16d9380e46cd`.

### ERR-0002 — Deletion-boundary harness Ruff I001
- severity: P2
- status: `FIXED`
- evidence: Ruff failure `33744816398`; Ruff PASS `33749788522`.
- root_cause: import ordering/formatting in `tests/unit/test_deletion_ledger_boundaries.py`.
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
- evidence: `33785726577` exact B010 diagnostic; `33792012599` I001; exact-head `33804193396 = success`.
- root_cause: bounded startup/readiness test-harness lint defects, not product startup failure.
- files: `tests/unit/test_pathena_startup_experience_2900.py` and related startup harness imports.
- fix_sha: `77e7b4c7d95202e6814226e2b4a2c4a54e3f5c8e`, `a5d9530525bd0b6bf0eae3945c23a6805f6b9669`.

### ERR-0005 — System-tray QApplication ownership typing
- severity: P2
- status: `FIXED`
- evidence: UI `33822842314` mypy failure; corrected `33822861477 = success`.
- root_cause: typed `self.app` assignment occurred before runtime `QApplication` narrowing.
- fix_sha: `72e43bc18c28b5c92f6528919abf788f66924ba9`.

### ERR-0006 — Research UUID filter container boundary is not runtime-safe
- severity: P2
- status: `FIXED`
- evidence: Backend `33833499697`; repaired lineage `33838658964 = success`.
- root_cause: missing explicit runtime container/element validation.
- fix_sha: `462fba22637e0083c87df32f987134ce0fb3de00`; integrated equivalent `4b390b4fcc39affc1884f304f460901d07ea622a`.

### ERR-0007 — Missing contradiction-review dependency breaks integrated Core import graph
- severity: P1
- status: `FIXED`
- evidence: post-integration `33838377083`; repaired lineage `33838658964 = success`.
- root_cause: Core integration omitted required contradiction-review dependency file.
- fix_sha: `05bca268e2d2fc8e5b0f5ae59c564f2403605540`.

### ERR-0008 — Settings runtime/comprehension harness contract mismatch
- severity: P2
- status: `FIXED`
- evidence: `33845743958`, `33849890354`; exact fix Quality `33854660676 = success`.
- root_cause: harness contract drift after truthful loopback-only behavior changes.
- files: `tests/unit/test_pathena_settings_runtime.py`.
- fix_sha: `afa319f0ab1b12edccc4b649d4a1ca36bcd7ac39`.

### ERR-0009 — Local HTTP remaining-budget hardening leaves stale readline-size harness expectations
- severity: P2
- status: `FIXED`
- evidence: failing Quality `33900689788`; exact Backend Quality `33911612711 = success`.
- root_cause: correct product `remaining + 1` hardening left stale harness expectations.
- fix_sha: Error `67f3f447621c4544a5fb2fe321e76b62347290e0`; Backend `0e966a49cd37d9ee6a4572ac4e35ce3d8018ff8e`.

### ERR-0010 — Direct total-deadline hardening invalidates stream timing harness
- severity: P2
- status: `FIXED`
- evidence: Backend `33916312429`; recurrent `33933291735` and UI `33936799048`; corrected Backend `33936396203 = success`, UI `33937005854 = success`.
- root_cause: obsolete timing fixture was reintroduced while product fail-closed deadline behavior was correct.
- fix_sha: Backend `e62fcc2db49815e7d32579d0dc68a143f8af07b0`.

### ERR-0011 — Unavailable provider leaks fresh accessibility freshness
- severity: P2
- status: `FIXED`
- evidence: failing UI `33922277491`; exact fix-head UI Quality `33926653411 = success`.
- root_cause: provider/detail metadata reused snapshot freshness while provider was unavailable.
- fix_sha: `9df9d7d46e3c4774aeea5439f91166a2092bd7fb`.

### ERR-0012 — UI synchronization drops unavailable StorageHealth database-path invariant
- severity: P1
- status: `FIXED`
- evidence: failing UI `33961422115@9f24999c62b309e25ac512a110ef18011225a4cc`; corrected `33966822035@77b3f9582d4530dbe081e3c81b8768ad00d3f050 = success`.
- root_cause: UI synchronization retained stale `src/athena/storage/health.py`.
- fix_sha: correction present by `cef280487dd12b6fe88d4a3f021ec9b1b2aea0d5`, verified on `77b3f9582d4530dbe081e3c81b8768ad00d3f050`.

### ERR-0013 — UI provider-detail whitespace harness Ruff I001
- severity: P2
- status: `FIXED`
- evidence: failing UI `33964058090@cef280487dd12b6fe88d4a3f021ec9b1b2aea0d5`; corrected `33966822035@77b3f9582d4530dbe081e3c81b8768ad00d3f050 = success`.
- root_cause: non-canonical import block in redundant whitespace harness.
- fix_sha: `77b3f9582d4530dbe081e3c81b8768ad00d3f050`.

### ERR-0014 — Qt Desktop controller test process SIGSEGV
- first_seen: 2026-09-05
- severity: P1
- status: `STALE`
- evidence: UI `33975657049@97b051612ca1199907a47d7e3f6938e3f1f8ca37` and `33978563758@8adcc65f394c556b2783b5da070a52c9afc27d0d` exited `139`; later exact successors `33978582156@fb98e47fde410137b971a303678d4e63f66e1d6d = success` and `33981877292@074c7b9a4ccf9271a91dd1e56784601f749ac020 = success` did not reproduce it.
- root_cause: deterministic product defect unestablished; reopen only on exact signature recurrence.

### ERR-0015 — Negative bounded local-response read harness fabricates overflow byte
- first_seen: 2026-09-06
- severity: P2
- status: `FIXED`
- evidence: Backend `34004101347@e4ddf651db85c1abe1c42e8b3f65a7b77fd08eba` and `34006604490@aed7296fd0ca173daaca41da1f2f64e575b8c5b4`; verified descendant `34009044381@a9a267ec790ea4dd1c9cfc79d07fc1665f664e30 = success`.
- root_cause: unbounded fake response fabricated the deliberate overflow-probe byte; product probe was correct.
- fix_sha: Backend `5abee1fb3cf9aa639a2600796036302ef63a773d`.

### ERR-0016 — Local HTTP overflow no longer poisons the bounded response
- first_seen: 2026-09-06
- severity: P1
- area: Backend / Provider-Transport / local HTTP product safety
- status: `FIXED_PENDING_VERIFY`
- evidence: Backend `34016515174@c991482a9f49dec50e69779f73e3a0939df5c73b` and `34019237735@a5904fc2078a8dec5eece17dd352436d14453d8f` reproduced exactly two poisoning failures.
- root_cause: oversize-before-accounting left `_bytes_read` within budget and removed the implicit poisoned-state marker.
- files: `src/athena/model/adapters/local_http.py`, `tests/unit/test_local_http_response_boundaries.py`, `tests/unit/test_local_http_oversize_accounting.py`.
- fix_sha: Backend product `d721846ea9524ab18336ba72eeb082cca7ee0fb8`; regression `44bf215b999e727514fc10ddb88eb8379a5358b6`; documentation descendant `d6fca835ad432e05aecbdc3c790a55ec2691a11b`.
- correction: explicit `_byte_budget_poisoned` state; rejected bytes are not counted as successful consumption; follow-up `read()`/`readline()` fails before delegate access.
- verification: canonical run `34022137849@d6fca835ad432e05aecbdc3c790a55ec2691a11b` is not valid closure evidence because an independent Core import-graph failure aborts mypy/pytest and path-boundary/local-start checks before complete verification. Keep `FIXED_PENDING_VERIFY` until an exact corrected descendant completes required focused and canonical verification.
- integrator_handoff: preserve the poison fix; do not interpret run `34022137849` as an ERR-0016 recurrence because its primary diagnostic is `ERR-0017`.

### ERR-0017 — Integrated Personal Memory service imports a missing proposal model
- first_seen: 2026-09-06
- severity: P1
- area: Core / Personal Memory / Integration / Startup import graph
- status: `OPEN`
- evidence: canonical Backend Quality `34022137849@d6fca835ad432e05aecbdc3c790a55ec2691a11b = failure`. Ruff and specification Validator pass, but mypy reports `src/athena/memory/service.py:16: error: Module "athena.memory.models" has no attribute "ModelInferredMemoryProposal" [attr-defined]`. Full pytest collects only 3733 items and aborts with 147 import errors rooted in `ImportError: cannot import name 'ModelInferredMemoryProposal' from 'athena.memory.models'`. Linux storage and Windows path-safety jobs both fail their API runtime path-boundary step; local-install smoke fails its disposable Core/API restart smoke through the same import graph.
- repro: current `develop/pathena-next@451b2f39377653b44fb178e58d86705b6026bef8` has `src/athena/memory/service.py` importing and using `ModelInferredMemoryProposal`, while current Develop `src/athena/memory/models.py` does not define it.
- root_cause: incomplete bounded Core integration. Reviewed-inference service/repository semantics were integrated onto Develop without the required proposal model dependency. This is one primary missing-symbol defect; the mypy failure, 147 pytest collection errors, API path-boundary failures and local-start failure are cascades and must not receive separate ERR IDs.
- active_worker_correction: `postmerge/spec-core@a43a471b611c78d24ebb8c67253b855b6a0642f3` contains the missing `ModelInferredMemoryProposal` definition in `src/athena/memory/models.py`. Exact Spec/Core canonical Quality `34021606032@a43a471b611c78d24ebb8c67253b855b6a0642f3 = success`. The Spec/Core handoff explicitly states current Develop already integrates the reviewed-inference acceptance while the still-missing verified provenance-boundary blobs include `src/athena/memory/models.py`.
- files: `src/athena/memory/service.py`, `src/athena/memory/models.py`; affected startup/import consumers across Core/API/Chat/Research/Jobs are cascade-only.
- fix_sha: none on Develop/Error branch; verified worker correction exists on Spec/Core head `a43a471b611c78d24ebb8c67253b855b6a0642f3`.
- verification_required: integrate a bounded compatible `ModelInferredMemoryProposal` definition from the exact-green Spec/Core lineage, then run mypy, Personal-Memory proposal/review/provenance focused tests, local Core/API restart smoke, API runtime path-boundary tests, full pytest and exact canonical Quality on the resulting SHA.
- risks: do not delete the service import or bypass review-gated inferred-memory semantics merely to restore collection; do not fabricate provenance or loosen UUID/review-required validation.
- integrator_handoff: current Develop is not promotion-ready. Treat `a43a471b611c78d24ebb8c67253b855b6a0642f3` / Quality `34021606032 = success` as the verified active-worker source for the missing model contract; compose only the compatible bounded dependency and verify exact resulting Develop.

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

Any exact-candidate recurrence blocks Beta/release promotion until closed with real verification.
