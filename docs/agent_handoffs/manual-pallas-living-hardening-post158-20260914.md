# PALLAS Living Hardening — post #158 — 2026-09-14

## Base

- Develop branch: `develop/pathena-next`
- Exact base SHA: `a2dfc6b381ead94996f319ca06fc65e25992fb70`
- Authoritative post-merge Quality run on that SHA: `34834496897 = SUCCESS`
- Foundation source: PR #158, already integrated and post-merge verified.

## Scope

This is a bounded follow-up to the integrated provenance-safe living PALLAS foundation. It does not change semantic graph truth, provenance, node or edge membership, force constants, age/vitality rules, lenses, shell hosting, or persisted state.

### 1. Semantic token cache

`PallasLivingEngine.reconcile()` now builds one normalized lexical token set per semantic node and refreshes the complete cache for every new immutable snapshot. The pairwise 30 FPS force step reuses those cached sets instead of repeatedly tokenizing title and summary text for every node pair on every frame.

`clear()` clears the token cache together with snapshot/state, so disposal and empty-state paths cannot retain stale lexical state.

The public `semantic_similarity()` helper remains behavior-compatible and still tokenizes its explicit arguments directly.

### 2. Edge geometry regression

The Qt regression suite now proves that after a living tick the already-rendered real `QGraphicsLineItem` for a semantic edge has endpoints equal to the living engine positions of its real source and target nodes, and that the rendered node items occupy those same positions.

This protects the presentation invariant that living motion cannot visually detach provenance edges from their grounded nodes.

## Files

- `src/athena/desktop/pathena_pallas_living.py`
- `tests/unit/test_pathena_pallas_living_token_cache.py`
- `tests/unit/test_pathena_pallas_living_qt.py`
- this handoff

## Required qualification

- focused PALLAS/Qt tests on the exact PR head;
- Ruff and mypy through the repository's current focused/canonical lanes;
- canonical Quality on the exact PR head;
- final head/base drift check before any integration;
- post-merge canonical Quality on the resulting Develop SHA.

No Skip/XFail, no visual MATCH claim, no baseline change, no shell/UI worker files, no provenance weakening, no auto-merge.
