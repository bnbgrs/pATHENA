# pATHENA Feature Integrator Handoff

## Current branch state

- `main` remains strict read-only at `0d4d621f8a38ddf8eccfa09622bf193687619943`.
- Develop before this run: `14ca6fece527d6b51956b3e5fa3ec7b291252420`.
- Integration target: `develop/pathena-next` only.
- Worker heads reviewed: errors `3392f70d4c4c0830fefe2833d098bed34fa2127b`; spec-core `f7e29299871394fb78d9129a4436b9cedcaee3a3`; backend `c991482a9f49dec50e69779f73e3a0939df5c73b`; ui `bf7fadf849140697dc63c92c6a5c6c69335e3278`.
- `main` and `bnbgrs/ATHENA` were untouched.

## Integrated this run — UI-GAP-0033 Library focused-current rows

READY UI lineage independently reviewed:

- product `5b6f8a5740d463524daf4cfae14c0335b2207693`;
- focused regression `35dacd3fc1ef3e6aa37051cfa14fb751f03c726d`;
- exact documentation head `644c3cd5e3fd9c646b5e9d881a821b25d55b70ea`;
- canonical ATHENA Quality `34012079406 = success`.

The Worker history is divergent and contains unrelated UI history, so the product blob was not transplanted wholesale. The exact eight-line selector delta was independently reviewed and semantically applied to exact current Develop, followed by the exact focused regression file.

Develop product commit: `b697520b6e1208d555ee7c358a4a3d80d6d7d28f`.
Focused test commit: `3e901ae27c0b91428a1b57b55fd13dd378e93eb2`.

## Contract now covered

`persistentKnowledgeList`, `persistentClaimList`, and `semanticReviewList` now expose explicit `:focus::item:current` presentation using canonical readable text, `surface_hover`, and the existing 2px accent left edge. Selection routing, list content, refresh behavior, persistence, provenance, backend/storage/security/provider/worker/scheduler behavior and Windows runtime ownership are unchanged.

## Validation state

- Worker focused regression is covered by exact green canonical Quality `34012079406 = success`.
- Independent Develop compare from `14ca6fece527d6b51956b3e5fa3ec7b291252420` to `3e901ae27c0b91428a1b57b55fd13dd378e93eb2` is ahead 2 / behind 0 and changes exactly `src/athena/desktop/pathena_shared_components.py` (+8) plus `tests/unit/test_pathena_knowledge_list_focus.py` (+18).
- No pull-request-triggered workflow run is associated with exact Develop test commit `3e901ae27c0b91428a1b57b55fd13dd378e93eb2`; repository-wide green is therefore not claimed for this exact SHA.

## Other current inputs

- Core explicit reviewed Personal-Memory inference acceptance is READY under product/test `f4a793171e56305f47e49d177e16287619b943bf`, exact verified descendant `b4d7ac9d0102981b133983c5fa93e113e2df4360`, canonical Quality `34013788076 = success` and focused verification `34013731297 = success`; deferred by this run's single bounded integration slice.
- Backend bounded local response constructor limits are READY under exact head `20edbed46471a50e72661e2e69502b094a0b599f`, canonical Quality `34014111747 = success`; deferred.
- Backend oversize-before-accounting mutation remains NOT READY while Quality `34016494344` is pending.
- UI-GAP-0034 is READY under product `0da430fdccb469b1edf8fd7adf01773b5ec5340f`, focused regression `3d9339295f3c413c4c7a31c2a7037600bc3b93f6`, exact documentation head `5a40e75ed78293ddd8c1ea3533c5632d6dea2910`, Quality `34014713429 = success`; deferred.
- Error handoff has no OPEN/IN_PROGRESS blocker; `ERR-0001` through `ERR-0013` and `ERR-0015` are FIXED, `ERR-0014` remains STALE.
- All eleven UI screens remain `IMPLEMENTED_PENDING_VISUAL_REVIEW`; original references remain unavailable and pixel-level `MATCH` remains unclaimed.

## Runtime/release guards retained

Known Windows pypdf packaging, fail-closed frozen argv routing, bounded process tree, adaptive 2048-context DirectChat budgeting, lane-lock/SchedulerLaneOwnership packaged-worker crash cluster and storage-bootstrap/migration startup signatures remain explicit Beta/release regression requirements. This UI slice does not alter their owning semantics.

## Next integration order

1. Prefer the exact-green bounded Core reviewed Personal-Memory inference acceptance after compatibility review against current Develop.
2. Otherwise consume exactly one compatible READY successor; Backend constructor limits or UI-GAP-0034 are eligible.
3. Do not integrate Backend oversize-before-accounting mutation until exact canonical Quality succeeds.
4. Obtain exact-current-Develop Quality before repository-wide green or promotion-ready claims.
5. Before Beta/release readiness, explicitly regress all retained Windows packaging/process-tree/startup/chat-context/lane-lock crash classes on the exact candidate SHA.

## Rules retained

- No direct work on `main`; no main promotion.
- No force-push, history rewrite or auto-merge.
- No Skip/XFail, weaker assertions, Security/Storage/Windows/Recovery/validator relaxation, fake success or fabricated provenance.
