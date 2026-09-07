# pATHENA Alpha/Beta Core Handoff

## Current baseline

- Shared baseline synchronized this run: `develop/pathena-next@1bbbc693db781f1d56a7c75151fe9951a21363cc`.
- Worker branch: `postmerge/spec-core`.
- Exact verified pre-sync Core head: `c7cd4d9b1e0889a00b4599dfe76738442378b17b`.
- Exact canonical ATHENA Quality for that head: `34110957854 = success`.
- History-preserving NON-FORCE synchronization: `39438e3bd016382da6660876cb6f1c0bbdd893d6`, parents `c7cd4d9b1e0889a00b4599dfe76738442378b17b` and `1bbbc693db781f1d56a7c75151fe9951a21363cc`.
- Synchronization Quality: `34115725744 = in_progress` at handoff update time; do not call the synchronized head READY until it succeeds.
- `main` and `bnbgrs/ATHENA` remain untouched/read-only.

## Verified Core contracts

Normal Hybrid Search remains exact-green on the verified Core lineage: one-time `attach_normal_search`, capability `search.normal.hybrid` only after attachment, exact `query/model_id/limit/entity_type` delegation, canonical `hybrid_search_result_response()` mapping, unchanged `SemanticRetrievalUnavailableError` propagation, and application identity `app.api._normal_search is app.hybrid_retrieval`. No Archive/Protected expansion or synthetic provenance is introduced.

Personal Memory Beta acceptance through §47 is exact-green on `c7cd4d9b1e0889a00b4599dfe76738442378b17b`. The verified slice covers domain routing, explicit save, inference provenance/review gating, sensitive/protected fail-closed behavior, project-over-global scope priority, and current-turn instruction precedence over conflicting durable preference without mutating durable memory.

The §47 harness repair is canonical-green via Quality `34110957854`; the prior ERR-0019 evidence is therefore superseded for this exact Core SHA even if the independent Error handoff has not yet been refreshed.

## Synchronization evidence

Before synchronization, Develop-side deltas were checked and were disjoint from the verified Personal-Memory Core files: Integrator/progress documentation, UI startup/accessibility work, and Backend WAL/lane-lock/storage tests. The synchronization tree was constructed from the exact current Develop tree plus the exact verified Core blobs, then committed with two parents and advanced NON-FORCE. No foreign worker file was overwritten and no history was rewritten.

## Next Beta gap / ownership boundary

§48 Delete/Restore was inspected against `src/athena/lifecycle/deletion.py`, `src/athena/memory/service.py`, and `src/athena/memory/repository.py`. The generic lifecycle layer already owns durable deletion markers and restore-time re-deletion, while Personal Memory currently exposes no Core-owned delete API or repository marker integration. Implementing the physical deletion/restore persistence target would cross into the existing Backend-owned lifecycle/storage boundary. Core must not duplicate or bypass that layer. §48 therefore requires a versioned Backend/Integrator composition handoff or an established lifecycle target registration before Core adds only the transport/composition surface.

Core should next take the highest bounded Core-owned Personal-Memory gap not requiring deep storage ownership. §50 Trace is the next candidate: prove or implement a real Personal Memory revision -> `USED_MEMORY` provenance edge -> final Message -> ModelSignature trace, with no fabricated edge or identifier. Current repository code search did not find a `USED_MEMORY` symbol on the indexed branch, so this must be traced against the actual provenance graph contracts before mutation. If no established graph edge type exists, record that concrete dependency rather than inventing one.

## Release regression obligations

Before Beta/release promotion retain explicit regression coverage for pypdf frozen packaging metadata and fail-closed child argv/two-EXE routing, bounded desktop/worker process tree, 2048-context adaptive output reserve, Windows lane-lock PermissionError/SchedulerLaneOwnershipError/packaged-worker OSError cluster, duplicate-column startup migration, ATHENA Core startup failure, and storage-bootstrap failure. Historical signatures are OPEN only when reproduced on an exact candidate SHA.