# pATHENA Alpha/Beta Core Handoff

## Current slice

- Baseline: `develop/pathena-next@0a0953e34f6da2a9e47119d00da29662397944e8`
- Worker branch: `postmerge/spec-core`
- Product commit: `52e73e2a86afc3190a3695ebf9b3b5da341eb870`
- Focused-test commit: `e90306776b32cdfa0b6b0227b490845279870792`
- Status: `IMPLEMENTED_PENDING_VERIFY`

## Spec anchor

`docs/beta/10_Retrieval_und_Suche.md` §34 requires retrieval candidates to retain source/chunk provenance, and §52 requires Search Responses to include a source anchor. Archive lexical search already exposed `stable_anchor_key` from a verified SourceChunk. Semantic and hybrid archive results carry the same verified `representation_id`, start/end offsets, and SHA-256 content hash but had no shared Search Response adapter for that provenance.

`src/athena/source/anchor_service.py` establishes the canonical durable text SourceAnchor materialization contract: representation id + start/end offsets + quoted SHA-256 hash. Search must not invent an anchor id or mutate canonical state merely to format a response.

## Implemented product contract

Added `SearchSourceAnchorRef` and `source_anchor_ref()` in `src/athena/retrieval/source_anchor.py`.

- The adapter projects only existing verified archive-result inputs: `representation_id`, `start_anchor_value`, `end_anchor_value`, `content_hash`.
- It produces the exact representation/range/hash tuple required to materialize a durable text SourceAnchor later.
- It does not create a SourceAnchor row, actor, commit, or other canonical mutation during search.
- It rejects booleans/non-integer offsets, negative/empty ranges, non-bytes hashes, and non-SHA-256-length digests.
- It does not synthesize a SourceAnchor UUID.

This is an additive provenance adapter rather than a replacement storage architecture.

## Files

- `src/athena/retrieval/source_anchor.py`
- `tests/unit/test_search_source_anchor_ref.py`
- `docs/agent_handoffs/spec-core.md`

## Focused verification contract

Added focused unit coverage proving that:

- verified archive anchor inputs project unchanged into the Search source-anchor reference;
- `stable_key` preserves `(representation_id, start_offset, end_offset, quoted_hash)` exactly;
- malformed materialization inputs fail closed.

Runtime result is pending canonical verification. No PASS is claimed until exact-head CI succeeds.

## Safety / compatibility

- No search ranking or candidate-selection change.
- No storage/persistence/recovery mutation.
- No SourceAnchor creation during read-only search.
- No protected-content widening.
- No network/provider/UI mutation.
- No Skip/XFail/assertion weakening.

## Coordination

- Error worker: no current confirmed `ERR-*` ownership collision on the reviewed develop handoff.
- Backend worker: no overlap with ResourceMode or deletion-ledger files.
- UI worker: may consume this value only after integration; do not invent anchor UUIDs or source provenance in the UI.
- Integrator: integrate only after exact-head focused/canonical verification succeeds and independent diff review confirms the adapter remains additive.

## Remaining source-anchor gap

This slice establishes the deterministic Search Response provenance value for archive results, but does not yet wire it into a broader serialized Search API response object because no single canonical cross-domain response DTO has been identified on the current code path. That wiring should be a separate small slice once the actual response boundary is traced.

## Next Alpha/Beta gap

Trace `protection state` against the authoritative visibility/protection contracts next. Current unprotected LocalSearch and ArchiveSearch paths explicitly exclude protected payloads/scopes, but do not synthesize a constant label until the response boundary and protected-search merge path are identified.
