# pATHENA Alpha/Beta Core Handoff

## Current baseline

- Current shared baseline reviewed: `develop/pathena-next@a9b04acc020218ac8991eed7457e4a9428e10bd5`.
- Worker branch: `postmerge/spec-core` only.
- Pre-run worker head: `71d49c94dde94616705ffb60010ff57fc0ec127e`.
- Current worker repair head: `cf48d89d414c37d7019b22802f0f2ff013b71b45` before this handoff update.
- `main` and `bnbgrs/ATHENA` remain untouched/read-only; no force update, rebase or history rewrite was used.

## Verified Core contracts

Normal Hybrid Search remains unchanged from the exact-green verified Core lineage: one-time `attach_normal_search`, capability `search.normal.hybrid` only after attachment, exact `query/model_id/limit/entity_type` delegation, canonical `hybrid_search_result_response()` mapping, unchanged `SemanticRetrievalUnavailableError` propagation, and application identity `app.api._normal_search is app.hybrid_retrieval`.

§68 durable 60%-restart acceptance remains inherited from exact-green Spec/Core evidence. §69 model-drift fail-closed acceptance remains covered by the existing real orchestration test. §70 Large Archive / pinned 2048-context acceptance was integrated into current Develop by Integrator and remains preserved.

## Exhaustive Research §71 — contradiction acceptance repair pending exact verify

Normative §71 requires two actually opposing real Sources to remain explicitly visible as a final contradiction with precise provenance to both SourceAnalysis final artifacts.

`tests/unit/test_exhaustive_research_contradiction.py` was added in `71d49c94dde94616705ffb60010ff57fc0ec127e`. Canonical ATHENA Quality `34179449007` on that exact SHA completed `failure` only in full pytest; Validator, Ruff, mypy, Local install smoke, Linux storage regressions and Windows path safety all succeeded.

Direct test/provider inspection identified a harness-only source-analysis propagation defect. The fixture emitted distinct opposing findings only when `"map" in schema_id`; real SourceAnalysis then passed through non-MAP reduce/final synthesis calls, where the inherited provider returned generic source findings. As a result the §71 test could not reliably carry both opposing persisted SourceAnalysis findings into the prepared Research FINAL synthesis input.

Minimal repair `cf48d89d414c37d7019b22802f0f2ff013b71b45` changes only the §71 test provider behavior: Research-synthesis schemas still delegate to the canonical shared synthesis fixture; SourceAnalysis calls containing exactly one launch outcome now preserve that outcome through MAP and non-MAP reduce/final responses. Production code, contradiction policy, provenance mapping, persistence semantics and all §71 assertions remain unchanged.

Status: `§71 FIXED_PENDING_VERIFY @ cf48d89d414c37d7019b22802f0f2ff013b71b45`. No PASS/READY claim until focused/canonical execution succeeds on this SHA or an unchanged descendant.

## Coordination state

- Error handoff reviewed at `postmerge/errors@226ba95aead51d42b723b787b444a9b001ab3293`; ERR-0023 is a separate Jobs product-copy issue and does not own the §71 Research test repair.
- Backend active head was reviewed via current Error coordination evidence; Backend storage/WAL/scheduler ownership remains disjoint and no Backend file was changed here.
- UI active head was reviewed via current Error coordination evidence; UI Jobs/accessibility ownership remains disjoint and no UI file was changed here.
- Integrator handoff/current Develop was reviewed at `develop/pathena-next@a9b04acc020218ac8991eed7457e4a9428e10bd5`; current Develop records prior Large Archive acceptance integration.
- All Core mutations remain NON-FORCE and no foreign branch/history was overwritten.

## Next Core action

1. Consume exact CI/Quality for `cf48d89d414c37d7019b22802f0f2ff013b71b45` or this unchanged handoff descendant.
2. If green, mark §71 READY with exact SHA/Quality and hand to Integrator.
3. Immediately inspect/execute normative §72 Unavailable NAS Test. Reuse existing unit accounting for unavailable sources but add only the missing real orchestration/NAS acceptance; do not duplicate unit-only coverage.
4. If §71 remains red, repair only the new exact pytest primary failure without weakening the two-opposing-source or precise-provenance assertions.

## Release regression obligations

Before Beta/release promotion retain explicit regression coverage for pypdf frozen packaging metadata and fail-closed child argv/two-EXE routing, bounded desktop/worker process tree, 2048-context adaptive output reserve, Windows lane-lock PermissionError/SchedulerLaneOwnershipError/packaged-worker OSError cluster, duplicate-column startup migration, ATHENA Core startup failure, and storage-bootstrap failure. Historical signatures are OPEN only when reproduced on an exact candidate SHA.
