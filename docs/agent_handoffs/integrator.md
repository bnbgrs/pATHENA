# pATHENA Feature Integrator Handoff

## Current branch state

- `main` remains strict read-only at `0d4d621f8a38ddf8eccfa09622bf193687619943`.
- Develop before this run: `62aa4e9ff20919f32d5147d183521fbf98f49535`.
- Integration target: `develop/pathena-next` only.
- Worker heads reviewed: errors `118f3b2c182de43d1876c7c369a00282800018fa`; spec-core `b9e8f18c83b25b2b3c6675ec9439b02393124457`; backend `e4ddf651db85c1abe1c42e8b3f65a7b77fd08eba`; ui `856d9f56fac059f257451c2e31fd35b4e554e55f`.
- `main` and `bnbgrs/ATHENA` were untouched.

## Integrated this run — model-facing Personal Memory precedence acceptance

READY Core lineage independently reviewed:

- acceptance commit `91e511860c0a9346582f1077212cf247bdf2347d`;
- exact-green Core lineage through `daf618982b068557919b58a3e0e6935c9cf41afe`;
- canonical Quality `34003641444 = success`.

Current Develop already carried the verified Personal Memory product contract from the preceding run and did not contain `tests/unit/test_personal_memory_context_priority.py`. The exact verified worker test blob `5d6d43f4003f6fb6afa4c1068858eb47e6578f6f` was added without importing unrelated Core history. Compare `62aa4e9ff20919f32d5147d183521fbf98f49535..977437441c1d3b91764c6d737699fd8006d1d6b4` is ahead by one commit, behind by zero, and changes exactly that one test file (+62/-0).

Integration commit: `977437441c1d3b91764c6d737699fd8006d1d6b4`.

## Contract now covered

The already-integrated exact-scope ordering — matching scoped Personal Memory, then global core collaboration preferences, then global fallback Memory — is now accepted through the real `ContextBuilderService` model-facing composition. The test also preserves current-turn override policy text and exact scope identity. No production semantics changed in this slice.

## Validation state

- Model-facing precedence acceptance passed canonical Quality `34003641444` in the exact verified Core lineage.
- Independent Develop compare confirms a single new acceptance-test file and no production mutation.
- Exact-current-Develop repository-wide green is not claimed because no post-integration workflow is bound to the new Develop SHA in this connector run.
- `ALPHA_BETA_PROGRESS.md` was read; connector retrieval remains truncated, so no unsafe whole-file rewrite was attempted.

## Other current inputs

- Backend local-provider HTTP error-body total-deadline hardening remains an exact-green READY candidate from Quality `34001608473`; later Backend successors require their own exact evidence.
- UI-GAP-0030 remains an exact-green READY candidate from Quality `34001923188`; later UI successors require their own exact evidence.
- Error handoff has no current exact-SHA OPEN blocker; historical crash signatures stay release-regression requirements unless reproduced on the current exact SHA.
- Eleven UI screens remain implemented pending visual review; pixel-level MATCH remains unclaimed.

## Runtime/release guards retained

Known Windows pypdf packaging, fail-closed frozen argv routing, bounded process tree, adaptive 2048-context DirectChat budgeting, lane-lock/SchedulerLaneOwnership packaged-worker crash cluster and storage-bootstrap/migration startup signatures remain explicit Beta/release regression requirements. This acceptance-only Memory slice does not alter their owning code.

## Next integration order

1. Prefer any newer exact-green bounded Core composition successor after independent compatibility review.
2. Otherwise consume exactly one READY Backend/UI successor; Backend HTTP error-body total deadline and UI-GAP-0030 are eligible candidates if still compatible with exact current Develop.
3. Obtain exact-current-Develop Quality before repository-wide green or promotion-ready claims.
4. Before Beta/release readiness, explicitly regress all retained Windows packaging/process-tree/startup/chat-context/lane-lock crash classes on the exact candidate SHA.

## Rules retained

- No direct work on `main`; no main promotion.
- No force-push, history rewrite or auto-merge.
- No Skip/XFail, weaker assertions, Security/Storage/Windows/Recovery/validator relaxation, fake success or fabricated provenance.
