# pATHENA Alpha/Beta Core Handoff

## Current baseline

- Current shared baseline reviewed: `develop/pathena-next@df05e76c998148e2445401de04115a7c5dccd708`.
- Worker branch: `postmerge/spec-core` only.
- Pre-run worker head: `ac8dad2af4d5bb8b38c2fdcb6f4ea61b3deb5b00`.
- Current §72 acceptance repair lineage: `124bdd9d789230d33452cfbc2452b307d410316c` -> handoff descendant `ac8dad2af4d5bb8b38c2fdcb6f4ea61b3deb5b00`.
- `main` and `bnbgrs/ATHENA` remain untouched/read-only; no force update, rebase or history rewrite was used.

## Verified Core contracts

Normal Hybrid Search remains unchanged from the exact-green verified Core lineage: one-time `attach_normal_search`, capability `search.normal.hybrid` only after attachment, exact `query/model_id/limit/entity_type` delegation, canonical `hybrid_search_result_response()` mapping, unchanged `SemanticRetrievalUnavailableError` propagation, and application identity `app.api._normal_search is app.hybrid_retrieval`.

§68 durable 60%-restart acceptance remains exact-green. §69 model-drift fail-closed acceptance remains covered by the existing real orchestration test. §70 Large Archive / pinned 2048-context acceptance remains integrated and preserved. §71 two-opposing-source contradiction acceptance remains exact-green and integrated.

## Exhaustive Research §72 — Unavailable NAS acceptance

Normative §72 requires an unavailable/offline part of the frozen Research scope to reduce coverage as `unavailable`, never to be reclassified as `irrelevant`.

Existing `tests/unit/test_research_coverage.py` already proves the pure coverage arithmetic: unavailable work is processed but not coverage-positive and cannot yield full coverage. That unit accounting is not duplicated.

Initial orchestration acceptance `5fbe0dc8b3d7674a18c562e96c118ddf4e476985` failed canonical Quality `34186455107` only in full pytest. The source-identity repair `124bdd9d789230d33452cfbc2452b307d410316c` corrected a real acceptance defect by resolving persisted Research work through candidate -> exact `source_id` and marking the actual captured `nas-offline.txt` work item UNAVAILABLE instead of relying on list position.

Exact re-verification materially advanced and is still red: Quality `34190083267` on `124bdd9d789230d33452cfbc2452b307d410316c` completed FAILURE only in canonical full pytest; specification validator, Ruff, mypy, Local install smoke, Linux storage regressions and Windows path safety all succeeded. The unchanged handoff descendant `ac8dad2af4d5bb8b38c2fdcb6f4ea61b3deb5b00` likewise completed Quality `34190114472 = failure`, again only in full pytest with all other canonical gates green.

The canonical run uploaded diagnostics artifact `canonical-quality-diagnostics-ac8dad2af4d5bb8b38c2fdcb6f4ea61b3deb5b00` (artifact id `10042945285`, SHA-256 digest `56777ff40908e91e04e13eda76c8c90d3c608ae3f8506220d081752f4e6713a8`). The current GitHub connector can enumerate that artifact but does not permit downloading the artifact ZIP or job log endpoint, and the local runner still cannot resolve `github.com`; therefore the exact remaining pytest assertion/traceback could not be retrieved in this run. This is now the concrete blocker. The already-fixed list-order/source-identity hypothesis is explicitly closed and must not be repeated.

No speculative product patch was made without the exact remaining assertion. The §72 acceptance still retains exact source identity, one SUCCESSFUL / one IRRELEVANT / one UNAVAILABLE, processed=3, failed=0, coverage=2/3, persisted scope parity and durable UNAVAILABLE-not-IRRELEVANT assertions. No production code, Storage/WAL behavior, provider/transport path, Search, UI, provenance semantics, Skip/XFail or release guards changed.

Status: `§72 BLOCKED_ON_EXACT_PYTEST_DIAGNOSTIC`; `ERR-0024 IN_PROGRESS`. No PASS/READY claim exists for `124bdd9d789230d33452cfbc2452b307d410316c` or `ac8dad2af4d5bb8b38c2fdcb6f4ea61b3deb5b00`.

## Coordination state

- Error handoff reviewed at `postmerge/errors`: `ERR-0024 IN_PROGRESS`; it independently records both pytest-only reds and holds §72.
- Backend current head recorded by Error coordination: `5fb145df421059314b4d90f53b9fc69b1c4333ab`; Backend remains WAL/scheduler/storage-owned and disjoint.
- UI current head recorded by Error coordination: `4c656c2c5dfb55e6d3f0078719183cbbad73a555`; UI remains Jobs/accessibility-owned and disjoint.
- Integrator current shared baseline is `develop/pathena-next@df05e76c998148e2445401de04115a7c5dccd708`; §72 remains held and prior §68-§71 Core work remains preserved.
- All Core mutations remain NON-FORCE and no foreign branch/history was overwritten.

## Next Core action

1. Retrieve the exact remaining pytest assertion/traceback for Quality `34190114472` (or a later unchanged-descendant run) from canonical diagnostics; do not repeat source-order analysis.
2. Apply the smallest demonstrated §72 product/harness correction on `postmerge/spec-core`, preserving exact NAS source identity, unavailable-vs-irrelevant distinction, 2/3 coverage and durability assertions.
3. Run focused §72 verification and canonical Quality. Only an exact green successor may be marked READY and handed to Integrator.
4. Once §72 is exact-green, immediately inspect/execute normative §73 External Capture Test unless equivalent real acceptance already exists.
5. Before mutation re-check latest Develop/Error/Backend/UI heads and preserve all foreign deltas.

## Release regression obligations

Before Beta/release promotion retain explicit regression coverage for pypdf frozen packaging metadata and fail-closed child argv/two-EXE routing, bounded desktop/worker process tree, 2048-context adaptive output reserve, Windows lane-lock PermissionError/SchedulerLaneOwnershipError/packaged-worker OSError cluster, duplicate-column startup migration, ATHENA Core startup failure, and storage-bootstrap failure. Historical signatures are OPEN only when reproduced on an exact candidate SHA.
