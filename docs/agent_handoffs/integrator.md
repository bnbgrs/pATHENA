# pATHENA Feature Integrator Handoff

## Current integration

- Integration target: `develop/pathena-next`.
- Develop parent before this integration: `099eae91912e423ed5aa85064b0b7d081a9d4a47`.
- Exact canonical Quality on that parent: `34804219596 = SUCCESS`.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## Iteration — canonical Claim inspection API adapter

No current worker branch offered a new bounded product delta after the project-Knowledge-membership integration. The current Spec/Core handoff identifies central Claim inspection/API composition as the next Core dependency. This integration therefore adds the transport-neutral adapter layer needed for that composition without mutating Storage, repository semantics, or contradiction-review safety.

`src/athena/api/knowledge_inspection.py` adapts the existing `KnowledgeInspectionService` boundary to the already-defined API DTO contracts for canonical Claim revisions, provenance inputs, evidence, and contradiction reviews. Claim lists/details/history and pending contradiction review reads remain read-only. Review resolution converts only the explicit `confirm`/`reject` client decision and obtains the actor identity from an injected local actor provider before delegating to the existing domain service; unknown decisions fail before any domain mutation.

`tests/unit/test_api_knowledge_inspection.py` covers JSON-safe canonical Claim DTO conversion including provenance/evidence, local actor propagation plus typed contradiction decision mapping, and fail-closed rejection of unsupported decisions before a domain call.

This slice deliberately does not yet alter `AthenaApplication` or `CoreApiFacade`; the next compatible Core composition step can attach this adapter to the canonical `ClaimRepository`, `ReviewService`, and local actor provider without inventing a second data path. No repository object or SQL row is exposed through the adapter.

## Current worker truth at integration time

- Errors: `80ffef405415a9dfde9bff8b1f54764224652ef7` — no new bounded product fix selected.
- Spec/Core: `2c1aef57d1ffd5ab53283a05843c912c9e3e93ad` — its project-membership product delta is already integrated; no newer worker product delta exists.
- Backend: `52eb61de9ecfde4074778a1bab2966e18aab526d` — no selected product delta.
- UI: `5922cdca385ad622b9e97f4e17b32edb00c847b8` — current exact Visual lane remains failed and the branch is not promoted here.

## Source-of-truth notes

- `docs/agent_logs/ERROR_LEDGER.md` remains historical wherever newer exact-SHA evidence exists.
- `docs/ui/11_SCREEN_REFERENCE_MANIFEST.md` and `docs/ui/VISUAL_GAP_LEDGER.md` remain fail-closed: no `MATCH` without an opened original reference and a real rendered exact-SHA state.
- The verified Send target remains 44×44 outer geometry.

## Persistent release guards

Retain without relaxation: pypdf packaging; fail-closed Frozen argv; Desktop/Worker two-EXE split; exactly one Desktop instance with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock cluster; duplicate-column/Core-startup/storage-bootstrap signatures; Security/Storage/Recovery guards; no Skip/XFail.

## Promotion state

`PROMOTION_READY=NO`

Require canonical Quality on the resulting exact Develop SHA before any further Develop mutation. If green, the next Core-owned gap is the bounded central composition of `KnowledgeInspectionService` + `KnowledgeInspectionApiService` into `AthenaApplication`/`CoreApiFacade`, with no duplicate persistence path.
