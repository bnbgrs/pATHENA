# pATHENA Alpha/Beta Core Handoff

## Current baseline

- Current shared baseline reviewed: `develop/pathena-next@b5f824082fcd9d335ea55de76f88d23a3c0ee7e8`.
- Worker branch: `postmerge/spec-core` only.
- Pre-run worker head: `147d9527ff06ce772aa378e29befa00d77031e9e`.
- Current §72 corrective product/test SHA: `772c2bfdc8767b7c0d032dbb8709120de635f6c0`.
- `main` and `bnbgrs/ATHENA` remain untouched/read-only; no force update, rebase or history rewrite was used.

## Verified Core contracts

Normal Hybrid Search remains unchanged from the exact-green verified Core lineage: one-time `attach_normal_search`, capability `search.normal.hybrid` only after attachment, exact `query/model_id/limit/entity_type` delegation, canonical `hybrid_search_result_response()` mapping, unchanged `SemanticRetrievalUnavailableError` propagation, and application identity `app.api._normal_search is app.hybrid_retrieval`.

§68 durable restart, §69 model drift, §70 Large Archive / pinned 2048-context and §71 opposing-source contradiction contracts remain preserved.

## Exhaustive Research §72 — Unavailable NAS acceptance

Exact Quality `34190114472` on prior handoff descendant `ac8dad2af4d5bb8b38c2fdcb6f4ea61b3deb5b00` failed full pytest with two failures. The GitHub Actions job log is now directly available and provides the exact §72 traceback that was previously blocked.

The §72 test itself completes every product assertion successfully: exact captured NAS source identity is resolved through candidate -> source_id, one work item is SUCCESSFUL, one IRRELEVANT, the exact NAS work item UNAVAILABLE, processed=3, failed=0, unavailable=1, irrelevant=1, coverage=2/3, persisted scope parity holds, and the durable NAS work state remains UNAVAILABLE rather than IRRELEVANT.

Its only §72 failure occurs in teardown at `tests/unit/test_exhaustive_research_unavailable_nas.py:87`: `AttributeError: 'AthenaApplication' object has no attribute 'close'`. The real application lifecycle API is `stop()`. Commit `772c2bfdc8767b7c0d032dbb8709120de635f6c0` changes only that teardown call from `app.close()` to `app.stop()`. No assertion, product code, persistence, provenance, safety or scope behavior changed.

The same canonical run also contains a separate integration failure in `tests/integration/test_core_api_process_lifecycle.py::test_authenticated_shutdown_stops_the_dedicated_core_process`: authenticated shutdown receives `CoreApiClientError: A valid local ATHENA session token is required.` That failure is independent of the §72 Research acceptance and must be deduplicated/owned separately; it must not be patched inside the §72 test.

Status: `§72 FIXED_PENDING_EXACT_VERIFY`; `ERR-0024` should consume `772c2bfdc8767b7c0d032dbb8709120de635f6c0` and distinguish the unrelated Core API lifecycle failure when canonical verification completes.

## Coordination state

- Error handoff reviewed at current `postmerge/errors`; `ERR-0024 IN_PROGRESS` and current worker coordination were consumed.
- Backend current head recorded by Error coordination: `ea601b96d681580c2e8f1f1af40c7d97c347511e`; Backend remains WAL/scheduler/storage-owned and disjoint.
- UI current head recorded by Error coordination: `bcce837f347f8b67f3b4de1ab465f3e80c750eea`; UI remains Jobs/accessibility-owned and disjoint.
- Integrator shared baseline reviewed at `develop/pathena-next@b5f824082fcd9d335ea55de76f88d23a3c0ee7e8`; §72 remains held pending exact-green evidence.
- All Core mutations remain NON-FORCE and no foreign branch/history was overwritten.

## Next Core action

1. Consume focused/canonical verification for `772c2bfdc8767b7c0d032dbb8709120de635f6c0` or its unchanged handoff descendant.
2. If §72 passes but canonical Quality remains red solely because of the separate Core API process-lifecycle failure, classify §72 as product/test-green but do not claim global canonical PASS; hand the unrelated exact failure to Error/Integrator ownership without expanding the Research slice.
3. Mark §72 READY only with exact evidence that the §72 acceptance passes, preserving exact NAS source identity, unavailable-vs-irrelevant distinction, 2/3 coverage and durable-state assertions.
4. Then immediately inspect/execute normative §73 External Capture Test unless equivalent real acceptance already exists.

## Release regression obligations

Before Beta/release promotion retain explicit regression coverage for pypdf frozen packaging metadata and fail-closed child argv/two-EXE routing, bounded desktop/worker process tree, 2048-context adaptive output reserve, Windows lane-lock PermissionError/SchedulerLaneOwnershipError/packaged-worker OSError cluster, duplicate-column startup migration, ATHENA Core startup failure, and storage-bootstrap failure. Historical signatures are OPEN only when reproduced on an exact candidate SHA.
