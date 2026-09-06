# pATHENA Alpha/Beta Core Handoff

## Current state

- Baseline: `develop/pathena-next@70f985ce7a28044824bfbfa53769b982fa152747`.
- Worker: `postmerge/spec-core`.
- Prior exact worker `07263cc7474954f1591523077caa8eb8532605dd` passed canonical ATHENA Quality `34032612712 = success`.
- History-preserving NON-FORCE synchronization onto current Develop: `c3ec46becb13362ab7a692cf88bef7389cdc5e47`, parents `07263cc7474954f1591523077caa8eb8532605dd` + `70f985ce7a28044824bfbfa53769b982fa152747`.
- `main` and `bnbgrs/ATHENA` remain untouched/read-only.

## Verified Core slice

Personal Memory `Why is this remembered` is implemented as a read-only, content-free projection from canonical `PersonalMemorySnapshot` state:

- `src/athena/memory/explanation.py` exact verified blob `b4a182e38c335b747682e38b37fa3d5a63997f32`;
- `tests/unit/test_personal_memory_explanation.py` exact verified blob `3bcbb71c6568dc23c1059cced48b813a610e105d`.

The projection exposes only `memory_id`, current `revision_id`, canonical `learning_mode` origin, current revision timestamp, and canonical `last_confirmed_at_us`. It exposes no Memory content and synthesizes no provenance.

Canonical Quality `34032612712` verifies the exact prior worker containing this slice. Current Develop does not contain these two files, so the verified blobs were overlaid byte-identically onto the exact current Develop tree in `c3ec46becb13362ab7a692cf88bef7389cdc5e47` without overwriting foreign changes.

## Search status

Normal-Hybrid Search `HybridRetrievalService -> AthenaApplication -> CoreApiFacade -> search.normal.hybrid` is already integrated on current Develop with the required attachment/capability/delegation/DTO/error-propagation/application-identity contract. Do not reopen it unless current exact-SHA evidence regresses.

## Coordination

- Error worker current head checked; no current Core blocker was identified.
- Backend and UI ownership remain disjoint from this Memory explanation slice.
- Personal-Memory Review Queue/idempotency remains blocked until a real durable proposal/review-decision identity exists; Core must not invent a synthetic identity or take Backend-owned schema work.

## Readiness

`07263cc7474954f1591523077caa8eb8532605dd` is exact canonical green for the verified Memory explanation product/test blobs. `c3ec46becb13362ab7a692cf88bef7389cdc5e47` is the current-Develop synchronization candidate and requires exact-head canonical Quality before Integrator READY is claimed for this synchronization.

## Next Core gap

After exact-head verification of the synchronization, select the highest evidence-backed bounded CHAT/KNOWLEDGE/RESEARCH/PALLAS/Human-Control Alpha/Beta gap. Prefer a contract that can be implemented without synthetic provenance, fake PALLAS data, Protected-scope leakage, or deep Backend-owned storage migration. Preserve the release regression matrix for packaging, bounded worker process trees, 2048-context DirectChat, Windows lane-lock/Scheduler ownership, and storage-bootstrap startup signatures.
