# pATHENA Error Handoff

## Baseline

- Develop source of truth: `develop/pathena-next@8d34591f08ab1f1a42dbb032963769968aefab2e`.
- Error worker entered this run at `postmerge/errors@23b0c22e2b219fd28a44feb94296c883fab75327`.
- Current workers: Spec/Core `008345141aac276f9723b536a70497e2dec74b20`; Backend `38a61d5f6b41bd151c3662bd1ef2a5a35f240a87`; UI `51c109f6a0e31f82392be6c5bfe1d7d167377499`.
- Develop canonical Quality `34689663093@8d34591f08ab1f1a42dbb032963769968aefab2e = IN_PROGRESS` at observation time; latest completed Develop canonical is `34687050578@63423bccaf9bf5b4049e55998e2d3303f59ecaf7 = SUCCESS`.
- Backend exact `38a61d5f6b41bd151c3662bd1ef2a5a35f240a87`: Backend Focused `34689028510 = SUCCESS`; canonical `34689028433 = FAILURE`, isolated by job metadata to full pytest while all other canonical lanes pass.
- Spec/Core exact `008345141aac276f9723b536a70497e2dec74b20`: Core Focused `34688220222 = SUCCESS`; canonical `34688220225 = IN_PROGRESS` at observation time.
- UI exact `51c109f6a0e31f82392be6c5bfe1d7d167377499`: UI Focused `34686843794 = SUCCESS`; Integrator reports canonical SUCCESS but exact visual regression FAILURE.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- OPEN: `ERR-0040`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED includes `ERR-0033` and `ERR-0035`.
- STALE includes historical `ERR-0038` and `ERR-0039`.
- BLOCKED: none.

## Hard progress this run — current Backend canonical failure classified

### ERR-0040 — scheduled-materialization candidate full-suite regression

Status: `OPEN / P1`.

Exact reproducer is `postmerge/backend@38a61d5f6b41bd151c3662bd1ef2a5a35f240a87`.

Exact canonical Quality `34689028433` is `FAILURE`. The Python 3.12 quality job passes specification validation, Ruff and mypy, then fails only in `Quality — pytest`; Windows Path Safety, Linux Storage Regressions and Local Install are all green. The same SHA passes Backend Focused Candidate `34689028510`.

The latest completed Develop parent used by this Backend lineage, `63423bccaf9bf5b4049e55998e2d3303f59ecaf7`, is canonical-green via `34687050578 = SUCCESS`. The candidate adds the scheduled-occurrence materialization slice, including `src/athena/jobs/scheduled_materialization.py` and `tests/unit/test_scheduled_materialization.py`.

This proves a real full-suite-only regression on the current Backend exact SHA and blocks promotion. It does **not** yet prove which pytest node is the root cause. The canonical diagnostics artifact `canonical-quality-diagnostics-38a61d5f6b41bd151c3662bd1ef2a5a35f240a87` exists, but the available workflow metadata does not expose its text payload. Therefore no historical UI, Storage or Recovery signature is being guessed or reopened.

Backend already owns this active product slice. Required next owner action: consume the canonical diagnostics, reproduce the named failing pytest node first, then apply the smallest fix and rerun the relevant regression set followed by exact canonical Quality. Error worker should verify that evidence rather than parallel-editing Backend product code.

### Other clusters

`ERR-0035 = FIXED / P1`; integrated closure remains `34680853488@8c885669ce3a3d718588d0327828341684c88c71 = SUCCESS`.

`ERR-0033 = FIXED / P1`; integrated closure remains `34666307002@ca87e42c8820c47db7d6626feb17698560cd3b49 = SUCCESS`.

`ERR-0038` and `ERR-0039` remain `STALE`; reopen only with current exact-SHA reproduction.

## CI discipline

- `postmerge/errors@23b0c22e2b219fd28a44feb94296c883fab75327` had zero workflow runs before the ledger mutation.
- After ledger commit `5572c42c5f0d7fcb8b731839eef822721d80539f`, the Error branch again had zero workflow runs before this handoff mutation.
- No canonical Quality run was started by Errors.
- No mutation was made to Develop, Backend, Spec/Core, UI, `main`, or `bnbgrs/ATHENA`.

## Integrator handoff

- Develop: `8d34591f08ab1f1a42dbb032963769968aefab2e`; canonical `34689663093 = IN_PROGRESS`. Do not treat the current Develop SHA as qualified until that run completes.
- `ERR-0040 = OPEN / P1`: Backend exact `38a61d5f6b41bd151c3662bd1ef2a5a35f240a87`; Backend Focused `34689028510 = SUCCESS`; canonical `34689028433 = FAILURE`, isolated to full pytest by job metadata.
- The Backend candidate is not promotion-ready until the exact failing pytest node is identified, reproduced and fixed with exact canonical SUCCESS.
- Spec/Core: `008345141aac276f9723b536a70497e2dec74b20`; focused SUCCESS, canonical still IN_PROGRESS at observation time.
- UI: `51c109f6a0e31f82392be6c5bfe1d7d167377499`; focused SUCCESS; Integrator records canonical SUCCESS but visual regression FAILURE, so no UI promotion is implied here.
- Preserve pypdf packaging, Frozen argv, two-EXE topology, bounded workers, adaptive 2048-context reserve, Windows lane-lock mapping, duplicate-column/Core-startup/storage-bootstrap guards and all Storage/Recovery/Security fail-closed invariants.
