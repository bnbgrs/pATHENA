# pATHENA Error Handoff

## Baseline

- Baseline: `develop/pathena-next@2bc57c4c84a0ed13ca9adbbc61f8fd00fc87fb8f`.
- Error branch history-preserving NON-FORCE sync: `a00978919ca870fdfc6029cfc925cdaa68c15cd7`, parents prior Error `410bdc595d3f4c370541b0701386cfe4b4b880ce` plus current Develop.
- Worker heads reviewed: Spec/Core `942d19f46a91af6672bb7639c1fca4cadf378ac7`; Backend `80bd67a2a0ad9b1b013635597f6cdaeca0f05cba`; UI `38a28f61af16d0b12500b4056b586ba934a2ba1a`; Integrator/Develop `2bc57c4c84a0ed13ca9adbbc61f8fd00fc87fb8f`.
- `spec-core.md`, `backend.md`, `ui.md`, `integrator.md`, worker heads and canonical Quality evidence were reviewed. `main` and `bnbgrs/ATHENA` remained read-only.

## Current state

- OPEN: `ERR-0018`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015`, `ERR-0016`, `ERR-0017`.
- STALE: `ERR-0014`.
- BLOCKED: none.

## ERR-0018 — fourth exact verification and final root-cause narrowing

Spec/Core head `942d19f46a91af6672bb7639c1fca4cadf378ac7` was concretely verified with canonical Quality `34054516742 = failure`. The run completed with exactly one primary gate failure: Ruff `I001 [*] Import block is un-sorted or un-formatted` at `src/athena/memory/context.py:3:1`.

Everything else is green on that exact SHA: Local install/Core-API restart PASS; Windows path safety PASS; Linux storage/API path-boundary PASS; Validator 63/63 PASS; mypy PASS; full pytest `4736 passed, 3 skipped, 2 warnings`.

The exact import forms now rejected by canonical Quality are:

1. `e8f7199f70c56a79403026926430ea56a5177bec`: `import uuid` before `from dataclasses import dataclass`, local `athena.memory.models` import multiline.
2. `b8858f986ec96e5973d47f8b74d2a120149a2037`: `from dataclasses import dataclass` before `import uuid`, local models import single-line.
3. `942d19f46a91af6672bb7639c1fca4cadf378ac7`: `from dataclasses import dataclass` before `import uuid`, local models import multiline.

That exhausts three of the four meaningful combinations. The only remaining canonical candidate is therefore `import uuid` before `from dataclasses import dataclass` with the `athena.memory.models` import kept single-line. This is now the finalized bounded root cause/corrective shape, not another open-ended hypothesis.

Current Develop still does not contain `src/athena/memory/context.py`; Error must not import the unintegrated Spec/Core feature onto `postmerge/errors`. The product mutation remains Spec/Core-owned. The next Spec/Core correction should change only the import block to the remaining form and then run Ruff plus focused Personal Memory context tests and canonical Quality.

## Other evidence

- Backend `postmerge/backend@80bd67a2a0ad9b1b013635597f6cdaeca0f05cba`: Quality `34055313570` was in progress at scan time; no confirmed independent primary failure.
- UI `postmerge/ui@38a28f61af16d0b12500b4056b586ba934a2ba1a`: Quality `34056114998` was pending at scan time; no confirmed independent primary failure.
- Current Develop `2bc57c4c84a0ed13ca9adbbc61f8fd00fc87fb8f` has no exact completed canonical Quality verified this run and is not promotion-ready by Error criteria.

## Integrator handoff

- Reject Spec/Core `e8f7199f70c56a79403026926430ea56a5177bec`, `b8858f986ec96e5973d47f8b74d2a120149a2037`, and `942d19f46a91af6672bb7639c1fca4cadf378ac7` as ready.
- Next Spec/Core correction: keep `import uuid` before `from dataclasses import dataclass` and keep `from athena.memory.models import MemoryScopeKind, MemorySensitivity, PersonalMemorySnapshot` single-line. No semantic changes.
- Require exact corrected SHA: Ruff PASS, focused `tests/unit/test_personal_memory_context.py` PASS, full pytest PASS and canonical Quality SUCCESS before `ERR-0018` becomes FIXED.
- Do not weaken Ruff or import the unintegrated feature into Develop/Error as a workaround.
- Preserve Provider/Transport byte-budget/deadline/poisoning, Personal-Memory provenance/review, Windows path safety, Storage, Security and Recovery guards.

## Persistent Beta/release regression knowledge

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded workers; adaptive 2048-context Chat reserve; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

## Next scan

1. Verify the next Spec/Core descendant after `942d19f46a91af6672bb7639c1fca4cadf378ac7`; close `ERR-0018` only on exact Ruff + focused + full canonical evidence.
2. Consume Backend Quality `34055313570` and UI Quality `34056114998` to completion.
3. Inspect the next exact current Develop/worker canonical or runtime signal and deduplicate against the ledger/crash matrix.
