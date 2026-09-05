# pATHENA Feature Integrator Handoff

## Current branch state

- `main` remains strict read-only at `0d4d621f8a38ddf8eccfa09622bf193687619943`.
- Develop before this run: `7710c7aaa82b4fe4725238cbe8f84d5be9ed3017`.
- Integration target: `develop/pathena-next` only.
- Worker heads reviewed: errors `eaa7e17d8425a05682e011639504d8266c32acb9`; spec-core `1bf7a9947a004b813924c91aad105fe2eacffa56`; backend `1cc0017d560a1534de1fc2c83989d26e05238236`; ui `77b3f9582d4530dbe081e3c81b8768ad00d3f050`.
- Required worker handoffs and current Alpha/Beta tracker were reviewed.
- `main` and `bnbgrs/ATHENA` remained untouched.

## Integrated this run — Scoped Project Research

READY Core lineage independently reviewed:

- exact verified worker product/test head `de0863e0c26f9d0c1474ef7c4f405cfc3ab6c79d`;
- canonical ATHENA Quality `33960242573 = success`;
- history-preserving Core synchronization `9416aa810c13c746c1d5e55545591477b00ef4c4` against prior Develop `8c2f08ef5a9dcafd9cf029da944527d97313cd2b` changed exactly three files.

Collision review established that current Develop retained the same pre-slice blobs as `8c2f08ef...` for `src/athena/research/service.py` and `src/athena/jobs/payload_validation.py`, and `tests/unit/test_research_scoped_project.py` was still absent. Therefore the exact verified worker blobs were applied to the current Develop tree without copying an older worker tree or disturbing newer StorageHealth/integrator changes.

Integrated exact blobs:

- `src/athena/research/service.py@ea69a4c2318da0f7faf2d6fc73d5022ae11ae8b3`;
- `src/athena/jobs/payload_validation.py@c8dfae33147ec02b9589300324eb5ca26086552a`;
- `tests/unit/test_research_scoped_project.py@dbdac1a7a87e94eba7825a741d9648decafffce8`.

Integration commit: `55f1c1638ad5032818ce156f97dc252f23ab3dc8`.
Independent compare `7710c7aaa82b4fe4725238cbe8f84d5be9ed3017..55f1c1638ad5032818ce156f97dc252f23ab3dc8` is exactly one commit and exactly three files: payload validator `+9/-1`, ResearchService `+79/-1`, and one focused test file `+69`.

## Product contract preserved

- `enqueue_scoped_project()` persists truthful `ResearchMode.SCOPED_PROJECT`.
- Project scope is mandatory and must contain canonical UUIDs before durable persistence.
- Durable `research.exhaustive` validation permits only `local_exhaustive` and `scoped_project`; scoped-project mode fails closed on empty `project_ids`.
- Project IDs remain sorted/unique/canonical.
- Query, source type, time range, coverage, snapshot, pinned model, candidate dedup and orchestration validation remain unchanged.
- Scoped Project Research does not implicitly enable Internet; `internet_scope` remains null.
- No synthetic source/claim/evidence/provenance/PALLAS data was introduced.

## Validation state

- Exact worker canonical Quality: `33960242573 = success`.
- Exact worker focused acceptance used real AthenaApplication/SQLite persistence and verified truthful mode/project persistence plus empty-project fail-closed behavior.
- Independent integration diff review: PASS, exactly the three expected files and no other tree changes.
- No pull-request-triggered workflow run is currently bound to integration commit `55f1c1638ad5032818ce156f97dc252f23ab3dc8`; therefore no exact-current-Develop repository-wide global-green claim is made.

## Other current inputs

- Backend StorageHealth single-line-detail hardening is READY via exact green Backend head `f7913b50618998b9b16a48ae9a810ed9122b64bc`, Quality `33963593580`, but deferred by the single-bounded-slice rule.
- Backend ASCII-control-detail hardening remains `FIXED_PENDING_VERIFY`.
- UI current lineage has an Error-owned regression handoff: `ERR-0012` is `FIXED_PENDING_VERIFY`; corrected UI head has verification still pending and is not READY on that evidence.
- Previously READY UI bounded slices remain deferred pending fresh dependency/collision review.

## Next integration order

1. Consume any newer exact-green bounded Core successor only after independent compatibility review.
2. Otherwise consume exactly one READY alternative; Backend StorageHealth single-line-detail hardening currently has exact green evidence.
3. Do not integrate the UI corrected lineage for `ERR-0012` until its exact canonical Quality completes successfully.
4. Preserve single-bounded-slice discipline and exact-head evidence before any repository-wide green claim.

## Rules retained

- No direct work on `main`; no main promotion.
- No force-push, history rewrite or auto-merge.
- No Skip/XFail, weaker assertion, Security/Storage/Windows/Recovery/validator relaxation, fake success or fabricated provenance.
