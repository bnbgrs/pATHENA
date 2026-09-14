# PALLAS Living Semantic Token Cache — 2026-09-14

## Purpose

Prepare a bounded performance follow-up on top of current living-field foundation head `b7844cc7c38a9a9b263edaa9b3f7b942a984c1c3` without changing or retriggering PR #151 while its canonical qualification is running.

## Problem

The foundation computes pairwise semantic attraction on every living tick. Before this follow-up, every pair called `semantic_similarity(left, right)`, which tokenized both node title/summary strings again. At a 30 FPS target this multiplies text normalization work by the number of node pairs on every frame.

The force simulation is still intentionally pairwise, but repeated lexical tokenization does not need to be.

## Change

- cache each node's normalized semantic token set during `PallasLivingEngine.reconcile()`;
- use cached token sets during pairwise attraction calculations;
- clear the cache with the engine;
- refresh all token sets on every reconcile so changed snapshot text cannot retain stale lexical state;
- keep the public `semantic_similarity()` helper behavior unchanged.

No graph node/edge membership, provenance, force constant, vitality rule, age progression, renderer contract or lens behavior changes.

## Regression

`tests/unit/test_pathena_pallas_living_token_cache.py` instruments token extraction and proves:

- reconcile tokenizes each node once;
- repeated living ticks perform no additional node tokenization;
- a later reconcile refreshes both cached token sets.

## Consumption rule

This branch is intentionally staged without a PR. Only consume after the foundation lands on Develop, then reconstruct on the current green head and obtain focused plus canonical evidence. Do not combine with UI shell reconciliation until both lineages are current.
