# pATHENA Feature Integrator Handoff

## Current branch state

- `main` remains strict read-only at `0d4d621f8a38ddf8eccfa09622bf193687619943`.
- Develop before this run: `4ce70615cffcbf0e76ec404e7e58b34c7c5e308a`.
- Integration target: `develop/pathena-next` only.
- Worker heads reviewed: errors `8cfa0784496cb26b1da9f396b424d6c10ed1d45f`; spec-core `00b510090b7ffea7d7492e224e4cccfc646317d1`; backend `4c9855df8e662e47a66cb2dcb9f66704c4d8f780`; ui `3262343d1f3e31e31d289dd0b0d22ff9559c458e`.
- Required worker handoffs were reviewed. `main` and `bnbgrs/ATHENA` were untouched.

## Integrated this run — Historical Backfill Research

READY Core lineage independently reviewed:

- product entrypoint `f696d26308b25ae7954167e253cae9a4469a87d1`;
- durable payload validation `eab1e98b51b4ba5bde071d5c62841d72882aad01`;
- focused real-application acceptance `1bf7a9947a004b813924c91aad105fe2eacffa56`;
- canonical ATHENA Quality `33965803951 = success` on the exact product/test head.

The worker and current Develop diverged only because Develop already contained the previously integrated Scoped Project Research/progress lineage. The exact verified worker blobs for the two product files and the new focused test were therefore applied onto the current Develop base tree rather than transplanting an older worker tree.

Integrated exact blobs:

- `src/athena/research/service.py@902ab0423b8d63cd4ee7e16f60cb45fcd389264d`;
- `src/athena/jobs/payload_validation.py@171fddf4c8d2bd2643fffdb338a19976ede645d8`;
- `tests/unit/test_research_historical_backfill.py@1340b5ce4d63d6c317321c44a1d3fe231d1b7c02`.

Integration commit: `70d5f135d9e9eb2640117314658a175f7d6a04f6`.
Independent compare from prior Develop is exactly one commit and exactly three files: payload validator `+6/-7`, ResearchService `+48/-1`, historical-backfill focused test `+88`.

## Product contract preserved

- `enqueue_historical_backfill()` persists truthful `ResearchMode.HISTORICAL_BACKFILL`.
- Both time bounds are mandatory non-negative genuine integers; bool is rejected.
- End-before-start fails closed before durable job persistence.
- Durable `research.exhaustive` validation independently requires both bounds for historical-backfill mode.
- Existing local/scoped-project behavior, project/source filters, coverage, snapshot pinning, candidate dedup identity, model parameters and orchestration remain unchanged.
- `internet_scope` remains null; Historical Backfill does not implicitly enable external access.
- No synthetic source, claim, evidence, provenance or PALLAS data was introduced.

## Validation state

- Exact worker canonical Quality: `33965803951 = success`.
- Focused acceptance uses the real `AthenaApplication`/SQLite path and verifies truthful mode/time persistence, initialization, invalid interval rejection before persistence, and bool rejection.
- Independent integration diff review: PASS; exactly the expected three files.
- No exact-current-Develop canonical Quality result is available yet, therefore repository-wide global green is not claimed.

## Other current inputs

- Backend StorageHealth ASCII-control-detail is READY through exact Backend head `1cc0017d560a1534de1fc2c83989d26e05238236`, Quality `33966299076 = success`.
- Backend DiskPressure reserve-release-state hardening remains pending exact green verification.
- UI-GAP-0024 is READY: exact UI head `77b3f9582d4530dbe081e3c81b8768ad00d3f050`, Quality `33966822035 = success`.
- Error handoff is stale relative to that completed UI Quality and still lists `ERR-0012`/`ERR-0013` as FIXED_PENDING_VERIFY; Error worker should consume the exact green UI evidence before closure.
- All eleven UI screens remain implemented pending visual review; no pixel-level MATCH claim is made.

## Next integration order

1. Independently review any newer exact-green bounded Core successor first.
2. Otherwise integrate exactly one READY alternative; Backend ASCII-control-detail and UI-GAP-0024 are current candidates.
3. Error worker should close `ERR-0012`/`ERR-0013` only after independently consuming exact UI Quality `33966822035` and confirming the unavailable-path guard plus Ruff correction remain present.
4. Preserve single-bounded-slice discipline and exact-head evidence before any repository-wide green claim.

## Rules retained

- No direct work on `main`; no main promotion.
- No force-push, history rewrite or auto-merge.
- No Skip/XFail, weaker assertions, Security/Storage/Windows/Recovery/validator relaxation, fake success or fabricated provenance.
