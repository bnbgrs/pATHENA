# PALLAS Living Semantic Token Cache — post-#158 reconstruction

Date: 2026-09-14
Base: `develop/pathena-next@a2dfc6b381ead94996f319ca06fc65e25992fb70`
Source lineage: staged token-cache follow-up rooted in the same byte-identical PALLAS living foundation now merged by PR #158.

## Scope

This branch reconstructs the bounded semantic-token cache optimization on the exact post-#158 Develop head.

Functional changes:

- cache normalized semantic token sets during `PallasLivingEngine.reconcile()`;
- reuse cached token sets during repeated living ticks;
- clear token cache with engine state;
- refresh tokens on every reconcile so changed node text cannot retain stale lexical state;
- keep public `semantic_similarity()` behavior unchanged;
- add a focused regression proving reconcile tokenizes each node once, repeated ticks do not re-tokenize, and a later reconcile refreshes the cache.

## Safety boundary

This is a performance-only presentation-layer change. It does not alter graph node or edge membership, provenance, force constants, contradiction semantics, vitality propagation, age progression, renderer contracts, or PALLAS lens behavior.

## Blob provenance

The functional source blob and focused regression-test blob are byte-identical to the previously staged follow-up. The current PALLAS source before applying the patch is the byte-identical foundation source that the staged follow-up was originally based on.

## Integration rule

Do not merge on lineage alone. Require fresh exact-head focused and canonical Quality evidence on this branch, then re-check that Develop has not advanced and the net diff remains limited to the PALLAS living source, the token-cache regression, and this handoff.