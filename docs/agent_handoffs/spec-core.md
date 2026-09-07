# pATHENA Alpha/Beta Core Handoff

## Current baseline

- Current shared baseline reviewed: `develop/pathena-next@15f4a439d15d4bb1414e7b54afee7a25ced36e61`.
- Worker branch: `postmerge/spec-core` only.
- Exact verified predecessor before the current Reset slice: `6b164470eae5352e6d5c0a84ac32a8f80ac002bc`.
- Exact canonical ATHENA Quality for that predecessor: `34116431458 = success`.
- `main` and `bnbgrs/ATHENA` remain untouched/read-only; no force update or history rewrite is allowed.

## Verified Core contracts

Normal Hybrid Search remains exact-green on the verified Core lineage: one-time `attach_normal_search`, capability `search.normal.hybrid` only after attachment, exact `query/model_id/limit/entity_type` delegation, canonical `hybrid_search_result_response()` mapping, unchanged `SemanticRetrievalUnavailableError` propagation, and application identity `app.api._normal_search is app.hybrid_retrieval`. No Archive/Protected expansion or synthetic provenance is introduced.

Personal Memory Beta acceptance through §47 remains exact-green on the verified lineage. Covered contracts include domain routing, explicit save, inference provenance/review gating, sensitive/protected fail-closed behavior, project-over-global scope priority, and current-turn instruction precedence over conflicting durable preference without mutating durable memory.

## Current bounded slice — Beta §50 Reset Test

Correction: the normative `docs/beta/06_Personal_Memory.md` defines §48 as Delete Test, §49 as Protected Lock Test and §50 as Reset Test. The previous handoff incorrectly described §50 as a provenance trace. That description is superseded; Core must not invent a `USED_MEMORY` edge as part of Personal-Memory §50.

The existing product path already exposes `PersonalMemoryService.reset() -> PersonalMemoryRepository.reset_all()`. It marks active/inactive Personal-Memory entities deleted in one reset commit and records deletion markers, while the existing generic test already checks Knowledge and Sources counts.

Acceptance commit `e6b6a5b1fe42ac612beb10e641a770be3e120b60` adds a dedicated §50 isolation regression proving the real reset path deletes the two Personal-Memory entries while preserving the archived standard Chat, promoted Knowledge snapshot and captured Source exactly. No fake Project implementation or synthetic provenance was added. A repository-wide search did not establish a current `ProjectRepository` contract, so the normative “Projects unchanged” clause remains a concrete product-domain dependency rather than being simulated in Core.

Exact canonical ATHENA Quality `34121459780` is in progress for `e6b6a5b1fe42ac612beb10e641a770be3e120b60` at this handoff update. Do not claim §50 READY until an exact completed success exists on a descendant carrying the unchanged acceptance test.

## Ownership boundaries

§48 Delete/Restore remains coupled to the existing lifecycle/storage deletion-marker path. Deep physical deletion, restore target registration and storage cleanup remain Backend/lifecycle-owned; Core must not duplicate that subsystem.

§49 Protected Lock requires the actual Protected-Content/index/UI-metadata contract. Core must not persist protected plaintext or synthesize an unlocked representation to satisfy the test.

For §50, Core owns the Personal-Memory reset composition/acceptance surface only. Knowledge, Raw Archive/Chat and Sources must remain unchanged. Project preservation can only be proven once a real Project persistence contract exists in the current runtime tree.

## Coordination state

- Error handoff reviewed at current Develop baseline: OPEN none, IN_PROGRESS none, BLOCKED none; ERR-0019 is FIXED and exact Core predecessor `6b164470eae5352e6d5c0a84ac32a8f80ac002bc` is canonical-green.
- Backend handoff reviewed; WAL/runtime work is disjoint from this Reset acceptance slice.
- UI handoff reviewed; Settings/accessibility presentation work is disjoint from this Reset acceptance slice.
- Integrator handoff reviewed at `develop/pathena-next@15f4a439d15d4bb1414e7b54afee7a25ced36e61`; current Core Reset work is not Integrator-ready until its exact canonical Quality succeeds.

## Next Core action

1. Consume exact Quality `34121459780` for `e6b6a5b1fe42ac612beb10e641a770be3e120b60` or the exact descendant carrying this handoff only.
2. If green, hand the exact verified Reset SHA to Integrator and then take the highest remaining bounded Core-owned Alpha/Beta P0/P1/P2 gap.
3. If red, repair only the exact primary failure; do not weaken assertions, add Skip/XFail, or relax persistence/provenance/security invariants.
4. Do not claim the Project portion of §50 covered until an actual Project persistence contract exists and can be proven unchanged.

## Release regression obligations

Before Beta/release promotion retain explicit regression coverage for pypdf frozen packaging metadata and fail-closed child argv/two-EXE routing, bounded desktop/worker process tree, 2048-context adaptive output reserve, Windows lane-lock PermissionError/SchedulerLaneOwnershipError/packaged-worker OSError cluster, duplicate-column startup migration, ATHENA Core startup failure, and storage-bootstrap failure. Historical signatures are OPEN only when reproduced on an exact candidate SHA.
