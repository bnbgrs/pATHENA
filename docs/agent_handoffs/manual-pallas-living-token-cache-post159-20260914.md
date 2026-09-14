# PALLAS living semantic-token cache — post-#159 requalification

Status: CANDIDATE_REQUIRES_EXACT_GREEN

Base: `develop/pathena-next@4634af7ab0db315574e692c57635585d3a3b3bf6`

## Scope

Performance-only follow-up for the merged PALLAS living-field foundation. Cache normalized semantic token sets during `reconcile()` and reuse them across living-field ticks instead of re-tokenizing every node pair on every frame.

## Contract preserved

- semantic attraction remains presentation/layout-only;
- graph membership and provenance are never synthesized or mutated;
- contradiction, edge, vitality, age and focus semantics are unchanged;
- public `semantic_similarity()` behavior remains unchanged;
- `clear()` invalidates the cache;
- every `reconcile()` rebuilds the cache from the exact current snapshot.

## Regression evidence

`tests/unit/test_pathena_pallas_living_token_cache.py` instruments `_tokens` and requires:

1. exactly one tokenization per node during reconcile;
2. zero tokenizations during 30 consecutive `step()` calls;
3. a later reconcile refreshes tokens for the new snapshot.

The post-#159 base carries the exact same pre-change PALLAS source blob (`c4892fa24b6b78c61e5b22d4f5cef0b6816b9913`) as the post-#158 staging base. Product blob `c2b3788c5cb715bc0459b304c3236c629ce4134e` and regression blob `ee61f0e9fac5e5336b97fab9e2a8067d1caf9952` are therefore carried byte-identically.

## Integration boundary

Do not merge until exact-head focused/UI-relevant checks and canonical Quality are green, post-#159 Develop canonical Quality is green, the PR head is unchanged, and final compare contains only this product file, the regression test, and this handoff.
