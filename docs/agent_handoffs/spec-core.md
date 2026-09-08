# pATHENA Alpha/Beta Core Handoff

## Current baseline

- Current shared baseline reviewed: `develop/pathena-next@1b1b136b63824815f312cbc70e5376c68285dbc0`.
- Worker branch: `postmerge/spec-core` only.
- Pre-run worker head: `b6fab29930459642ab41b42970ca87b92f4e563d`.
- Current §72 acceptance head before this handoff update: `5fbe0dc8b3d7674a18c562e96c118ddf4e476985`.
- `main` and `bnbgrs/ATHENA` remain untouched/read-only; no force update, rebase or history rewrite was used.

## Verified Core contracts

Normal Hybrid Search remains unchanged from the exact-green verified Core lineage: one-time `attach_normal_search`, capability `search.normal.hybrid` only after attachment, exact `query/model_id/limit/entity_type` delegation, canonical `hybrid_search_result_response()` mapping, unchanged `SemanticRetrievalUnavailableError` propagation, and application identity `app.api._normal_search is app.hybrid_retrieval`.

§68 durable 60%-restart acceptance remains exact-green. §69 model-drift fail-closed acceptance remains covered by the existing real orchestration test. §70 Large Archive / pinned 2048-context acceptance remains integrated and preserved.

## Exhaustive Research §71 — exact green and integrated

The repaired two-opposing-source contradiction acceptance `cf48d89d414c37d7019b22802f0f2ff013b71b45` passed canonical ATHENA Quality `34182976875 = success`. The unchanged handoff descendant `b6fab29930459642ab41b42970ca87b92f4e563d` also passed canonical Quality `34183001443 = success`.

Integrator independently consumed the exact repaired acceptance and integrated it into Develop as `b33186c1f9362732657d14dddb47496e2f37048b`; current Develop handoff records §71 integration at `1b1b136b63824815f312cbc70e5376c68285dbc0`. §71 is therefore closed for Core; no duplicate patch/test work is permitted.

## Exhaustive Research §72 — Unavailable NAS acceptance

Normative §72 requires an unavailable/offline part of the frozen Research scope to reduce coverage as `unavailable`, never to be reclassified as `irrelevant`.

Existing `tests/unit/test_research_coverage.py` already proves the pure coverage arithmetic: unavailable work is processed but not coverage-positive and cannot yield full coverage. That unit accounting is not duplicated.

New real orchestration acceptance `tests/unit/test_exhaustive_research_unavailable_nas.py` was committed NON-FORCE as `5fbe0dc8b3d7674a18c562e96c118ddf4e476985`. It uses the real `AthenaApplication`, captures three real Sources, freezes an explicit three-source Research CandidateSet, drives the real persisted Research work-state API to one SUCCESSFUL, one IRRELEVANT and one UNAVAILABLE terminal item, and asserts:

- the CandidateSet remains three eligible candidates;
- processed count is three;
- `unavailable_count == 1` and `irrelevant_count == 1` remain distinct;
- coverage is exactly `2/3`, never 100%;
- persisted ResearchScope coverage mirrors the same unavailable count and ratio;
- the offline work item remains durably `ResearchWorkState.UNAVAILABLE` and is explicitly not `IRRELEVANT`.

No production code, Storage/WAL behavior, provider/transport path, Search, UI, provenance semantics, assertions, Skip/XFail or release guards were changed.

Canonical ATHENA Quality `34186455107` is queued on exact SHA `5fbe0dc8b3d7674a18c562e96c118ddf4e476985`. Status: `§72 PENDING_EXACT_VERIFY`; no PASS/READY claim is made until that exact run completes successfully.

## Coordination state

- Error handoff reviewed at current baseline: OPEN none, IN_PROGRESS none, ERR-0023 remains separate Jobs product-copy `FIXED_PENDING_VERIFY`; current Spec/Core predecessor `b6fab29930459642ab41b42970ca87b92f4e563d` is exact-green via Quality `34183001443`.
- Backend active work remains WAL/scheduler/storage-owned and disjoint from this Research acceptance.
- UI active work remains Jobs/accessibility-owned and disjoint from this Research acceptance.
- Integrator handoff/current Develop records §71 exact-green integration and directs Core to §72 without duplicating unit accounting.
- All Core mutations remain NON-FORCE and no foreign branch/history was overwritten.

## Next Core action

1. Consume exact canonical Quality `34186455107` for `5fbe0dc8b3d7674a18c562e96c118ddf4e476985` or an unchanged descendant.
2. If green, mark §72 READY with exact SHA/Quality, hand it to Integrator, and immediately execute normative §73 External Capture Test unless equivalent real acceptance already exists.
3. If red, retrieve the exact primary Ruff/mypy/pytest failure and repair only that demonstrated §72 acceptance/product-contract defect without weakening unavailable-vs-irrelevant assertions.
4. Before any new mutation, re-check latest Develop/Error/Backend/UI heads and preserve all foreign deltas.

## Release regression obligations

Before Beta/release promotion retain explicit regression coverage for pypdf frozen packaging metadata and fail-closed child argv/two-EXE routing, bounded desktop/worker process tree, 2048-context adaptive output reserve, Windows lane-lock PermissionError/SchedulerLaneOwnershipError/packaged-worker OSError cluster, duplicate-column startup migration, ATHENA Core startup failure, and storage-bootstrap failure. Historical signatures are OPEN only when reproduced on an exact candidate SHA.
