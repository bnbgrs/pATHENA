# pATHENA Alpha/Beta Core Handoff

## Current baseline

- Shared baseline inspected: `develop/pathena-next@8941f823d896e85b58c7f566b45bef04bbfdb84d`.
- Worker branch: `postmerge/spec-core`.
- Verified source head: `5714f3c7724cb82ccd75a7e852c668bfe78c6d5d`.
- Exact canonical ATHENA Quality: `34060875144 = success` on that source head.
- History-preserving NON-FORCE synchronization onto the inspected Develop tree: `df9c256a5a545be3706b907462def10e41bc3844`, parents `5714f3c7724cb82ccd75a7e852c668bfe78c6d5d` and `8941f823d896e85b58c7f566b45bef04bbfdb84d`.
- `main` and `bnbgrs/ATHENA` remain untouched.

## Verified Personal Memory Core slice

Exact source head `5714f3c7724cb82ccd75a7e852c668bfe78c6d5d` is READY for Integrator review. Quality `34060875144` closed `ERR-0018`: repository-pinned Ruff accepted the final `src/athena/memory/context.py` shape, and the canonical run completed successfully.

The synchronized Core product/test set consists only of:

- `src/athena/memory/context.py`
- `src/athena/memory/explanation.py`
- `src/athena/memory/export.py`
- `src/athena/memory/view.py`
- `tests/unit/test_personal_memory_context.py`
- `tests/unit/test_personal_memory_explanation.py`
- `tests/unit/test_personal_memory_export.py`
- `tests/unit/test_personal_memory_view.py`

Develop-side foreign changes were preserved by building the synchronization tree from the exact current Develop tree and overlaying only those verified blobs.

## Product contracts retained

- Personal Memory context is explicitly labeled `USER PREFERENCE`, never world fact.
- Only active canonical snapshots influence ordinary model context.
- Protected plaintext fails closed and stays on the Protected Content path.
- Why-is-this-remembered is content-free and derived only from canonical revision state.
- Memory View and Export project canonical state without synthetic provenance.
- Normal-Hybrid Search remains integrated with one-time `attach_normal_search`, capability gating, exact query/model_id/limit/entity_type delegation, canonical DTO mapping, unchanged `SemanticRetrievalUnavailableError` propagation, and application identity `app.api._normal_search is app.hybrid_retrieval`.
- No Archive/Protected search broadening and no synthetic PALLAS data.

## Conflict guard status

Beta Personal Memory current-turn conflict precedence is already materially implemented on current Develop. The model-facing retrieval context explicitly states that the current user message overrides `USER PREFERENCE`, and `tests/unit/test_personal_memory_context_priority.py` covers the precedence/scope ordering. Core must not duplicate this mechanism or mutate durable Personal Memory merely because a current-turn instruction conflicts with it.

## Integrator handoff

READY source: `5714f3c7724cb82ccd75a7e852c668bfe78c6d5d` with exact Quality `34060875144 = success`.

Current-lineage synchronization: `df9c256a5a545be3706b907462def10e41bc3844`. Treat this synchronization commit as pending its own exact canonical Quality before promotion claims; the READY evidence above applies to the verified source head.

## Next Core gap

Do not reimplement the already-covered current-turn conflict guard. Select the next highest evidence-backed bounded Alpha/Beta gap in CHAT / KNOWLEDGE / RESEARCH / PALLAS / Human Control after re-reading current capability coverage and real tests. Personal-Memory Review Queue/idempotency remains blocked unless a real durable proposal/review-decision identity exists; do not synthesize one.

Release/Beta acceptance must retain the known Windows packaging, bounded process-tree, 2048-context, lane-lock and storage-startup regression matrix.
