# pATHENA Alpha/Beta Core Handoff

## Current slice

- Baseline: `develop/pathena-next@96489c4c493992ff9d8c7efd57557a69aa578e56`
- Worker branch: `postmerge/spec-core`
- NON-FORCE sync: worker fast-forwarded from the previously integrated Core head to the exact current develop baseline before mutation.
- Product commit: `a6f36715982c399f7138faf0760e55e30e970f8b`
- Focused-test commit: `2c9773ad95436ba304ba78caaa221d403a088c60`
- Status: `IMPLEMENTED_PENDING_VERIFY`

## Spec anchor

`docs/beta/10_Retrieval_und_Suche.md` §34 requires candidates to retain entity/revision, source/chunk, retrieval method, rank, score and selection reason. §52 requires the Search API response to expose at least result ref, title/preview, entity type, revision, rank, retrieval methods, source anchor and protection state. §§59-61 require protected candidates to be authorization-first, leak no locked metadata and retain Protection Labels through mixed retrieval.

The repository already has the canonical transport-neutral client boundary in `src/athena/api/contracts.py`: `ApiContract` recursively emits JSON-safe DTO dictionaries, and `CoreApiFacade` is documented as the stable client boundary rather than repositories/provider payloads. The normal hybrid retrieval result already carries deterministic `rank` and `retrieval_methods`; prior verified Core slices supply stable source-anchor and protection value contracts.

## Implemented product contract

Added `src/athena/api/search_contracts.py` as an additive extension of the existing `ApiContract` architecture, not a second facade or transport:

- `SearchResultResponse` is the canonical transport-neutral §52 result shape;
- `SearchSourceAnchorResponse` serializes only stable representation/range/SHA-256 materialization inputs and never invents a durable anchor id;
- `SearchProtectionResponse` serializes protection classification and preserves a real protected scope UUID without claiming current unlock state;
- source anchor remains explicitly nullable for result classes that have no SourceChunk provenance;
- rank must be a real positive integer (bool rejected);
- retrieval methods must be non-empty, textual and unique;
- unprotected results cannot carry protection scope metadata;
- protected results must retain a canonical UUID scope;
- malformed source ranges/digests fail closed.

No search execution, ranking, authorization, persistence, unlock state, candidate visibility or source loading behavior changes in this slice.

## Files

- `src/athena/api/search_contracts.py`
- `tests/unit/test_search_api_contracts.py`
- `docs/agent_handoffs/spec-core.md`

## Focused verification contract

Focused tests cover:

- exact JSON-safe serialization of all Beta §52 fields, including nested source-anchor and protection records;
- no scope metadata on unprotected responses;
- mandatory real UUID scope on protected responses;
- bool/invalid rank rejection and duplicate retrieval-method rejection;
- fail-closed source-anchor range and SHA-256 validation.

Exact-head runtime/CI verification is pending. No PASS/VERIFIED claim is made until the worker head has canonical evidence.

## Safety / compatibility

- No endpoint, facade attachment, ranking, retrieval selection, protected candidate visibility, FTS/HNSW, persistence, recovery, network/provider or UI code changed.
- No protected plaintext or hash is derived from locked data; the DTO can only serialize values a caller already possesses after the relevant authorization path.
- No Skip/XFail/assertion/security/storage/Windows guard weakening.
- Backend-owned `ERR-0001` deletion-ledger files remain untouched.
- UI worker files remain untouched.

## Coordination

- Error worker: no overlap; `ERR-0001` remains Backend-owned.
- Backend worker: no overlap with ResourceMode/deletion-ledger work.
- UI worker: no visible UI mutation. Later Search UI may consume this DTO only after real facade/controller wiring.
- Integrator: integrate only after exact-head Quality succeeds and independent review confirms this remains an additive `ApiContract` extension.

## Previous verified slices

The Archive Search source-anchor contract and Search protection-state contract are already integrated and verified on `develop/pathena-next`; this slice consumes their established semantics but does not modify them.

## Remaining Search Response gap

The DTO shape now exists inside the real API contract architecture, but it is intentionally not yet advertised as a capability or exposed through `CoreApiFacade`. The next Core slice must wire actual `HybridSearchResult`/archive result adapters into `CoreApiFacade` (and only then transport/controller layers) without fabricating source anchors or protected state. Archive hybrid retrieval still needs an authoritative carried rank/retrieval-method signal before its §52 adapter can be complete; do not infer method membership from a zero/nonzero score.

## Next Alpha/Beta gap

Trace application construction for the existing Hybrid retrieval services and add the smallest real `CoreApiFacade` Search attachment/call only after this DTO slice verifies. Preserve §§59-61: unprotected normal search must remain unable to reveal locked protected candidates, and protected results must come only from the authorized runtime path.
