# pATHENA Alpha/Beta Core Handoff

## Current slice

- Baseline: `develop/pathena-next@7e23616b79b65f759980ad98a27640b6c29bcea0`
- Worker branch: `postmerge/spec-core`
- Product commit: `3036b5f37d667d5ee6255480e7f460e5d61c8b9e`
- Focused-test commit: `11720aa82b38175b2f06e6a0ed80ddafd15f63ea`
- Verification PR: `#42` (`postmerge/spec-core` -> `develop/pathena-next`, draft, verification only)
- Status: `IMPLEMENTED_PENDING_VERIFY`

## Spec anchor

`docs/beta/10_Retrieval_und_Suche.md` §52 requires Search Responses to include `rank` alongside result identity, revision, retrieval methods, source anchor and protection state. The already integrated `HybridSearchResult` exposed retrieval methods but still did not expose the final returned rank.

## Implemented product contract

`HybridSearchResult` now has additive `rank: int | None = None`.

- Results produced by hybrid diversification receive contiguous final ranks `1..N` after diversity selection and any diversity-score adjustment.
- Explicit ranks must be positive integers; zero, negative values, booleans and non-integers are rejected.
- Direct construction remains source-compatible through the `None` default; only actual returned hybrid result sets assign final rank.
- The rank reflects returned order, not an intermediate lexical/semantic/RRF position.

## Files

- `src/athena/retrieval/hybrid.py`
- `tests/unit/test_hybrid_retrieval_provenance.py`

## Focused verification contract

Added focused coverage that:

- invalid explicit ranks are rejected;
- backward-compatible direct construction leaves `rank is None`;
- diversified result sets expose contiguous final ranks `(1, 2, 3)` in returned order.

No runtime PASS is claimed yet. Draft PR #42 was opened to trigger canonical verification; no workflow run was visible for exact head `11720aa82b38175b2f06e6a0ed80ddafd15f63ea` at handoff update time.

## Safety / compatibility

- No RRF formula or score weights changed.
- No candidate selection rule changed.
- No persistence/storage/recovery mutation.
- No network/provider/security mutation.
- No UI mutation.
- No Skip/XFail/assertion weakening.

## Coordination

- Error worker: no current confirmed `ERR-*` ownership collision from the latest develop handoff.
- Backend worker: no overlap with ResourceMode/deletion-ledger work.
- UI worker: may later consume final `rank` for Search/Knowledge explainability only after integration; no synthetic display rank is needed.
- Feature Integrator: do not integrate `3036b5f3`/`11720aa8` until exact-head focused/canonical verification is successful and no new regression is confirmed.

## Next Alpha/Beta gap

After rank is verified, trace the remaining §52 response fields against real contracts in this order: `source anchor`, then `protection state`. Do not add either until the canonical source/protection ownership path is identified; LocalSearch currently excludes protected payloads, so a simplistic constant protection label would be a fake contract.
