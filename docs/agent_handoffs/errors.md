# pATHENA Error Handoff

## Baseline

- Develop source of truth: `develop/pathena-next@fec368f50307a9e24038baca3a80b10ee2a3c4fc`.
- Error worker entered this run at `postmerge/errors@d212c92f5d139c8c2d5c03c1985e497ffd4671a1`.
- Current workers: Spec/Core `e9a6a1d28281e78c9b8ee0548582ed4a39d424b4`; Backend `195814616f394e1794aa4f3b2a16a584c092ab31`; UI `d71bf6951c10920eb709dbe5bb3e708c72b43c6a`.
- Exact-current Develop canonical Quality: `34618898303@fec368f50307a9e24038baca3a80b10ee2a3c4fc = SUCCESS`.
- Exact-current Spec/Core canonical Quality: `34621318923@e9a6a1d28281e78c9b8ee0548582ed4a39d424b4 = SUCCESS`.
- Exact-current Spec/Core focused candidate: `34621318964@e9a6a1d28281e78c9b8ee0548582ed4a39d424b4 = SUCCESS`.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- OPEN: `ERR-0033`, `ERR-0035`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`, `ERR-0031`, `ERR-0032`, `ERR-0034`, `ERR-0036`, `ERR-0037`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`, `ERR-0038`.
- BLOCKED: none.

## Hard progress this run — ERR-0038 reclassified from OPEN to STALE

### ERR-0038 — Spec/Core exact-head Ruff failure

Status: `STALE / formerly P1 integration blocker / Spec-Core owned`.

The previous exact reproducer was `53c3824e214b66e989cba1f425bfe7881190e12f`, where canonical Quality `34609297666` failed on Ruff `I001` at `src/athena/knowledge/revision_diff.py:3:1`.

That historical failure is no longer current. Spec/Core is now at exact head `e9a6a1d28281e78c9b8ee0548582ed4a39d424b4`; canonical Quality `34621318923` and focused candidate `34621318964` both completed `SUCCESS` on that exact SHA.

The current worker lineage is six commits ahead of the old reproducer. The exact compare shows that `src/athena/knowledge/revision_diff.py` and `tests/unit/test_claim_revision_diff.py` were removed from the current worker tree while a disjoint Concept Note provenance slice was added. Direct fetch of `revision_diff.py` at current worker head returns not found. Therefore the old `I001` cannot be treated as an active exact-head defect merely because it existed on the superseded candidate.

This is deliberately classified `STALE`, not `FIXED`: the broken revision-diff candidate was superseded/abandoned rather than repaired in place. Reopen only if a current exact SHA reproduces the Ruff failure again.

No Core product mutation was made by Errors. No canonical run was started by Errors.

### ERR-0033 — Emergency-reserve filesystem-object identity/capacity gap

Status remains `OPEN / P1 / Backend BE-046 owned`. Backend has no newer bounded exact-tested BE-046 candidate. The documented parent/target identity, inspection/acceptance, hardlink ownership and unknown-allocation fail-closed closure requirements remain applicable. Errors made no competing Storage product mutation.

### ERR-0035 — SQLite preflight identity through live writer startup

Status remains `OPEN / P1 / Backend BE-052 owned`. Backend has no newer bounded exact-tested BE-052 candidate. Errors made no competing Database/Storage product mutation.

## Integrator handoff

- Current Develop: `fec368f50307a9e24038baca3a80b10ee2a3c4fc`; canonical `34618898303 = SUCCESS`.
- `ERR-0038 = STALE`: old reproducer `53c3824e...` is superseded; current Spec/Core `e9a6a1d2...` has exact canonical `34621318923 = SUCCESS` and focused `34621318964 = SUCCESS`, and the offending revision-diff files are absent from the current worker tree.
- `ERR-0033 = OPEN / P1`, Backend BE-046 owned; no Errors product mutation.
- `ERR-0035 = OPEN / P1`, Backend BE-052 owned; no Errors product mutation.
- No closed/stale cluster was reopened without current exact-SHA evidence.
- Preserve pypdf packaging, Frozen argv, two-EXE topology, bounded workers, adaptive 2048-context reserve, Windows lane-lock mapping, duplicate-column/Core-startup/storage-bootstrap guards and all Storage/Recovery/Security fail-closed invariants.