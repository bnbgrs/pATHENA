# pATHENA Alpha/Beta Core Handoff

## Current baseline

- Current shared baseline reviewed: `develop/pathena-next@200648457ba647173376109d09f94725730ee659`.
- Worker branch: `postmerge/spec-core` only.
- Current verified worker predecessor: `57e133507ab4b8edc78d4af8467f2320dce0e906`.
- Exact canonical ATHENA Quality for that predecessor: `34121540987 = success`.
- The verified predecessor carries the unchanged Beta §50 Reset acceptance introduced at `e6b6a5b1fe42ac612beb10e641a770be3e120b60`.
- `main` and `bnbgrs/ATHENA` remain untouched/read-only; no force update or history rewrite is allowed.

## Verified Core contracts

Normal Hybrid Search remains exact-green on the verified Core lineage: one-time `attach_normal_search`, capability `search.normal.hybrid` only after attachment, exact `query/model_id/limit/entity_type` delegation, canonical `hybrid_search_result_response()` mapping, unchanged `SemanticRetrievalUnavailableError` propagation, and application identity `app.api._normal_search is app.hybrid_retrieval`. No Archive/Protected expansion or synthetic provenance is introduced.

Personal Memory Beta acceptance through §47 remains exact-green on the verified lineage. Covered contracts include domain routing, explicit save, inference provenance/review gating, sensitive/protected fail-closed inference, project-over-global scope priority, and current-turn instruction precedence over conflicting durable preference without mutating durable memory.

Beta §50 Reset isolation is now verified by exact canonical Quality on the current worker predecessor. The real reset path deletes Personal Memory while preserving archived standard Chat, Knowledge and Sources; deleted Personal-Memory revisions remain inspectable only through the explicit deleted-state path. The normative Projects-unchanged clause remains unproven because no real Project persistence/repository contract has been established in the current runtime tree; Core must not fake one.

## Current bounded slice — Beta §49 Protected Lock boundary

Normative §49 requires protected personal information to remain inaccessible to indexing and AI suggestions without a passphrase, with the index locked.

Current Core evidence establishes a strict fail-closed plaintext boundary but not the complete unlock/index contract:

- `PersonalMemoryRepository.create()` and `.revise()` call `_require_unprotected_payload()` before any write.
- `_require_unprotected_payload()` raises `PersonalMemoryProtectionError` for `MemorySensitivity.PROTECTED` and explicitly routes ownership to the Protected Content path instead of plaintext Personal-Memory storage.
- `PersonalMemoryService.context_candidates()` reads only canonical Personal-Memory rows and documents that Protected entries cannot exist in the v1 plaintext repository; it performs no silent unlock.
- Existing real regression `test_protected_memory_fails_closed_until_protected_content_path_exists` proves a protected explicit-memory write creates zero `personal_memory_entries`.
- The Core Personal-Memory service/repository exposes no passphrase/unlock handle, no Protected Content materialization API, no FTS/HNSW attachment, and no AI-suggestion index adapter that could be safely exercised for a full §49 proof.

Therefore full §49 cannot be honestly marked covered from the Core worker alone. Adding a fake protected row, fake index, synthetic unlock flag or mock passphrase would weaken the security contract. The required next integration contract is: a real Protected Content unlock/token boundary plus the concrete index/suggestion attachment point must be exposed to Core composition; then §49 can assert locked-without-passphrase across those real surfaces while retaining the existing plaintext refusal.

This is a concrete cross-component dependency, not a request to weaken assertions. Until that contract exists, Core preserves fail-closed behavior and must not expand protected content into Normal Search, Archive, PALLAS, FTS/HNSW or AI suggestions.

## Ownership boundaries

§48 Delete/Restore remains coupled to the existing lifecycle/storage deletion-marker path. Deep physical deletion, restore target registration and storage cleanup remain Backend/lifecycle-owned; Core must not duplicate that subsystem.

§49 plaintext refusal and Core composition are Core-visible, but protected materialization/unlock and deep index locking require the actual Protected Content/index contract. Core must not persist protected plaintext or synthesize an unlocked representation to satisfy the test.

For §50, Core owns the Personal-Memory reset composition/acceptance surface only. Knowledge, Raw Archive/Chat and Sources remain unchanged. Project preservation can only be proven once a real Project persistence contract exists in the current runtime tree.

## Coordination state

- Error handoff reviewed before this run: OPEN none, IN_PROGRESS none, BLOCKED none; ERR-0019 is FIXED. It also records exact worker `57e133507ab4b8edc78d4af8467f2320dce0e906` Quality `34121540987 = success`.
- Backend handoff reviewed; WAL/runtime/storage ownership is disjoint from the Core plaintext-refusal proof, while any deep Protected Content/index storage contract must remain coordinated rather than duplicated.
- UI handoff reviewed; current startup/accessibility/keyboard-focus presentation work is disjoint from §49 Core security semantics.
- Integrator handoff reviewed. Current Develop advanced to `200648457ba647173376109d09f94725730ee659`; the worker is not force-synchronized over that moving baseline and no Develop change was overwritten.

## Next Core action

1. Treat `57e133507ab4b8edc78d4af8467f2320dce0e906` as exact-green verified predecessor via Quality `34121540987`.
2. Preserve §49 fail-closed plaintext behavior. Do not claim full Protected Lock until a real Protected Content passphrase/unlock boundary and concrete index/suggestion attachment are available for acceptance.
3. On the next safe synchronization, compare the moving Develop lineage and retain all foreign Backend/UI/Integrator changes using history-preserving, non-force integration only.
4. Immediately take the highest remaining evidence-backed Core-owned CHAT/KNOWLEDGE/RESEARCH/PALLAS/Human-Control P0/P1/P2 gap that does not depend on the missing §49 cross-component contract; do not spend another run repeating this analysis.
5. If a new exact-SHA failure appears, repair only its smallest proven root cause; no Skip/XFail, weakened assertions or synthetic provenance.

## Release regression obligations

Before Beta/release promotion retain explicit regression coverage for pypdf frozen packaging metadata and fail-closed child argv/two-EXE routing, bounded desktop/worker process tree, 2048-context adaptive output reserve, Windows lane-lock PermissionError/SchedulerLaneOwnershipError/packaged-worker OSError cluster, duplicate-column startup migration, ATHENA Core startup failure, and storage-bootstrap failure. Historical signatures are OPEN only when reproduced on an exact candidate SHA.
