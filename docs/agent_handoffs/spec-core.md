# pATHENA Alpha/Beta Core Handoff

## Current slice

- Baseline: `develop/pathena-next@e76b4cb2cca1612fe68b1ddd66554213352d32a9`
- Worker branch: `postmerge/spec-core`
- NON-FORCE sync: worker fast-forwarded from `3a5dfffaea7b3a1bc3e0f376e2edac6cf1a8dc5c` to the current develop baseline before mutation.
- Product commit: `3a29225a4d79fac558f2b0d7c7757471daa34aaf`
- Focused-test commit: `9ee3c3c21ea6629b6ca203a73b56de221ccca871`
- Status: `IMPLEMENTED_PENDING_VERIFY`

## Spec anchor

`docs/beta/10_Retrieval_und_Suche.md` §5 requires a protection context in SearchRequest, §8 requires Protection Scope filtering before final ranking where possible, §19 keeps protected embeddings out of normal persistent HNSW state, §52 requires `protection state` in every Search Response, and §§59-61 require authorization-first protected retrieval, no metadata leak while locked, and Protection Labels to survive mixed ranking into the Context Builder.

The current code establishes two authoritative result classes:

- `LocalSearchService` and `LocalSemanticSearchService` are unprotected retrieval pipelines. Local FTS explicitly excludes protected payloads; semantic results are joined back through that unprotected FTS projection.
- `ProtectedRuntimeSourceSearchService` returns `ProtectedRuntimeSearchResult` only from authorized unlocked scopes and each result carries its actual `protection_scope_id`.

This slice therefore labels only facts already established by those pipelines. It does not infer current unlock state and does not expose protected metadata for results that were never authorized/returned.

## Implemented product contract

Added `src/athena/retrieval/protection.py` with:

- `SearchProtectionState.UNPROTECTED` and `.PROTECTED`;
- immutable `SearchProtectionRef(state, protection_scope_id)`;
- `unprotected_search_protection_ref()` for the explicitly unprotected retrieval paths;
- `protected_search_protection_ref(result)` which preserves the authorized result's real ProtectionScope UUID.

Invariants:

- unprotected labels cannot carry a scope id;
- protected labels must carry an actual UUID scope id;
- `protected` is a classification, not a claim that the scope remains unlocked later;
- no plaintext, hash, title, score, unlock flag, durable row, actor, commit, or synthetic scope is created;
- a malformed protected result fails closed rather than degrading to an unprotected label.

This is an additive Search Response value contract. It does not yet merge protected and unprotected ranking pipelines or alter authorization behavior.

## Files

- `src/athena/retrieval/protection.py`
- `tests/unit/test_search_protection_ref.py`
- `docs/agent_handoffs/spec-core.md`

## Focused verification contract

Focused tests cover:

- unprotected label contains no scope metadata;
- protected adapter preserves the exact authorized `protection_scope_id`;
- inconsistent unprotected+scope state is rejected;
- protected labels reject missing/non-UUID scope values;
- malformed protected result adapters fail closed.

Runtime/CI result is pending exact-head verification. No PASS is claimed until the worker head is verified.

## Safety / compatibility

- No search ranking, selection, candidate visibility, FTS, HNSW, persistence, recovery, network/provider, or UI behavior changed.
- No Protected Source plaintext or derived hashes are persisted.
- No locked-scope metadata is surfaced.
- No Skip/XFail/assertion/security/storage guard weakening.
- `ERR-0001` deletion-ledger files remain owned by Backend and untouched.

## Coordination

- Error worker: latest handoff records `ERR-0001` blocked from error-worker mutation because Backend owns deletion-ledger tasks 290-293; no overlap here.
- Backend worker: no overlap with ResourceMode or deletion-ledger files.
- UI worker: may eventually display this real label after integration/wiring; must not infer unlock state or fabricate scope ids.
- Integrator: review the two additive commits and integrate only after exact-head verification succeeds.

## Previous completed source-anchor slice

Archive Search source-anchor provenance was integrated into `develop/pathena-next` and is tracked there as verified. No further mutation to that slice was made in this run.

## Remaining Search Response gap

Beta §52 still lacks one canonical serialized response DTO joining rank, retrieval methods, source anchor and protection label across the actual domain-specific result types. Do not create a parallel response architecture. Trace the existing API/controller boundary and wire these verified value adapters into that real boundary as a separate slice.

## Next Alpha/Beta gap

Trace the actual Search API/controller/serialization call chain. Highest safe next step is a small cross-domain response adapter only if an existing boundary is found. Protected/unprotected mixed ranking itself remains a separate larger capability and must preserve §§59-61 authorization/no-leak invariants.
