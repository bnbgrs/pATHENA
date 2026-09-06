# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA evidenced failures are opened; cascades are deduplicated. `FIXED` requires real verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, weakened assertion, Ruff/mypy/Validator relaxation, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Baseline: `develop/pathena-next@2bc57c4c84a0ed13ca9adbbc61f8fd00fc87fb8f`.
- Error NON-FORCE sync: `a00978919ca870fdfc6029cfc925cdaa68c15cd7`, parents prior Error `410bdc595d3f4c370541b0701386cfe4b4b880ce` + Develop `2bc57c4c84a0ed13ca9adbbc61f8fd00fc87fb8f`.
- Reviewed heads: Spec/Core `942d19f46a91af6672bb7639c1fca4cadf378ac7`; Backend `80bd67a2a0ad9b1b013635597f6cdaeca0f05cba`; UI `38a28f61af16d0b12500b4056b586ba934a2ba1a`; Integrator/Develop `2bc57c4c84a0ed13ca9adbbc61f8fd00fc87fb8f`.

## Current state

- OPEN: `ERR-0018`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015`, `ERR-0016`, `ERR-0017`.
- STALE: `ERR-0014`.
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

- first_seen: 2026-09-06; severity: P2; area: Spec/Core / Personal Memory / Quality formatting; status: `OPEN`.
- evidence: `34044943935@4ebe23f510a0b36d8f87e027088de54a9809148a = failure`; `34048268758@e8f7199f70c56a79403026926430ea56a5177bec = failure`; `34051030897@b8858f986ec96e5973d47f8b74d2a120149a2037 = failure`; `34054516742@942d19f46a91af6672bb7639c1fca4cadf378ac7 = failure`.
- exact current diagnostic: Ruff `I001 [*] Import block is un-sorted or un-formatted` at `src/athena/memory/context.py:3:1`.
- exact fourth verification on `942d19f...`: Local install/Core-API restart PASS; Windows path safety PASS; Linux storage/API path-boundary PASS; Validator 63/63 PASS; mypy PASS; full pytest `4736 passed, 3 skipped, 2 warnings`; Ruff alone FAIL.
- root_cause: three of four meaningful import forms are exact-run rejected: (A) `import uuid` before dataclasses + multiline local models import (`e8f7199f...`); (B) dataclasses before `import uuid` + single-line local import (`b8858f98...`); (C) dataclasses before `import uuid` + multiline local import (`942d19f4...`). The only remaining canonical candidate is `import uuid` before `from dataclasses import dataclass` plus single-line `from athena.memory.models import MemoryScopeKind, MemorySensitivity, PersonalMemorySnapshot`. Root cause and corrective shape are now bounded/finalized. This is formatting-only; semantic Personal Memory tests remain green.
- files: `src/athena/memory/context.py`; focused regression `tests/unit/test_personal_memory_context.py`.
- fix_sha: none verified; rejected `e8f7199f70c56a79403026926430ea56a5177bec`, `b8858f986ec96e5973d47f8b74d2a120149a2037`, `942d19f46a91af6672bb7639c1fca4cadf378ac7`.
- verification requirement: corrected descendant must have Ruff PASS, focused Personal Memory context PASS, full pytest PASS and canonical Quality SUCCESS before `FIXED`.
- risks: preserve `USER PREFERENCE`, active-only projection, duplicate/snapshot identity checks and fail-closed Protected Memory behavior. Develop/Error do not currently contain this unintegrated feature and must not import it as a lint workaround.
- integrator_handoff: reject all three attempted correction SHAs. Spec/Core should apply only the remaining import layout and rerun exact verification.

## Current scan evidence — 2026-09-06

- Spec/Core `942d19f46a91af6672bb7639c1fca4cadf378ac7`: Quality `34054516742 = failure`, Ruff-only I001; all semantic/runtime jobs and full pytest green.
- Backend `80bd67a2a0ad9b1b013635597f6cdaeca0f05cba`: Quality `34055313570` in progress; no confirmed independent primary failure at scan.
- UI `38a28f61af16d0b12500b4056b586ba934a2ba1a`: Quality `34056114998` pending; no confirmed independent primary failure at scan.
- Develop `2bc57c4c84a0ed13ca9adbbc61f8fd00fc87fb8f` has no exact completed canonical Quality verified this run; no promotion-ready claim.

## Persistent Beta/release regression knowledge

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded workers; adaptive 2048-context Chat reserve; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.
