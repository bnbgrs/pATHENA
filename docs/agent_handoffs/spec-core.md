# pATHENA Alpha/Beta Core Handoff

## Current baseline

- Current shared baseline reviewed: `develop/pathena-next@c775d37f50e332639007ba162b4ff7f591434f1c`.
- Worker branch: `postmerge/spec-core` only.
- Pre-run worker head: `3b425e527fd701a984ee723c310ac86be062022d`.
- Current §72 acceptance repair: `124bdd9d789230d33452cfbc2452b307d410316c`.
- `main` and `bnbgrs/ATHENA` remain untouched/read-only; no force update, rebase or history rewrite was used.

## Verified Core contracts

Normal Hybrid Search remains unchanged from the exact-green verified Core lineage: one-time `attach_normal_search`, capability `search.normal.hybrid` only after attachment, exact `query/model_id/limit/entity_type` delegation, canonical `hybrid_search_result_response()` mapping, unchanged `SemanticRetrievalUnavailableError` propagation, and application identity `app.api._normal_search is app.hybrid_retrieval`.

§68 durable 60%-restart acceptance remains exact-green. §69 model-drift fail-closed acceptance remains covered by the existing real orchestration test. §70 Large Archive / pinned 2048-context acceptance remains integrated and preserved. §71 two-opposing-source contradiction acceptance remains exact-green and integrated.

## Exhaustive Research §72 — Unavailable NAS acceptance

Normative §72 requires an unavailable/offline part of the frozen Research scope to reduce coverage as `unavailable`, never to be reclassified as `irrelevant`.

Existing `tests/unit/test_research_coverage.py` already proves the pure coverage arithmetic: unavailable work is processed but not coverage-positive and cannot yield full coverage. That unit accounting is not duplicated.

Initial real orchestration acceptance `5fbe0dc8b3d7674a18c562e96c118ddf4e476985` ran canonical ATHENA Quality `34186455107 = failure`. Validator, Ruff, mypy, Linux storage regressions, Windows path safety and local install smoke all passed; only canonical full pytest failed. Error handoff tracks this exact condition as `ERR-0024` and correctly makes no speculative product-vs-harness claim because the connector does not expose the traceback artifact.

Independent test/code inspection established an additional concrete acceptance defect that must be corrected regardless of the hidden traceback: the original test assigned SUCCESSFUL/IRRELEVANT/UNAVAILABLE to `work[0]`, `work[1]`, `work[2]` and therefore never proved that the work item marked UNAVAILABLE actually belonged to the NAS source. Work-item listing order is not the normative source identity contract.

Repair `124bdd9d789230d33452cfbc2452b307d410316c` strengthens the acceptance without touching production code or weakening any assertion. It resolves each persisted Research work item through its candidate to the exact captured `source_id`, proves the three captured source identities are represented, and then marks the exact `nas-offline.txt` source work item UNAVAILABLE. It retains the exact three-candidate, processed=3, success=1, irrelevant=1, unavailable=1, failed=0, coverage=2/3, persisted-scope parity and durable UNAVAILABLE-not-IRRELEVANT assertions.

No Storage/WAL behavior, provider/transport path, Search, UI, provenance semantics, Skip/XFail or release guards changed.

Status: `§72 FIXED_PENDING_EXACT_VERIFY`. No PASS/READY claim exists yet for `124bdd9d789230d33452cfbc2452b307d410316c` or a descendant.

## Coordination state

- Error handoff reviewed on current Develop: `ERR-0024 IN_PROGRESS` for the exact §72 pytest-only failure; no conflicting Error-owned product mutation exists.
- Backend current work remains WAL/scheduler/storage-owned and disjoint from this Research acceptance.
- UI current work remains Jobs/accessibility-owned and disjoint from this Research acceptance.
- Integrator holds §72 until exact-green evidence and already preserves prior integrated §68-§71 Core work.
- All Core mutations remain NON-FORCE and no foreign branch/history was overwritten.

## Next Core action

1. Consume the first exact canonical Quality run on `124bdd9d789230d33452cfbc2452b307d410316c` or an unchanged descendant.
2. If green, mark §72 READY with exact SHA/Quality, hand it to Integrator, and immediately execute normative §73 External Capture Test unless equivalent real acceptance already exists.
3. If red, use the new exact failure evidence to classify and repair only the demonstrated remaining §72 product/harness defect; do not weaken exact NAS-source identity, unavailable-vs-irrelevant, 2/3 coverage or durability assertions.
4. Before any new mutation, re-check latest Develop/Error/Backend/UI heads and preserve all foreign deltas.

## Release regression obligations

Before Beta/release promotion retain explicit regression coverage for pypdf frozen packaging metadata and fail-closed child argv/two-EXE routing, bounded desktop/worker process tree, 2048-context adaptive output reserve, Windows lane-lock PermissionError/SchedulerLaneOwnershipError/packaged-worker OSError cluster, duplicate-column startup migration, ATHENA Core startup failure, and storage-bootstrap failure. Historical signatures are OPEN only when reproduced on an exact candidate SHA.
