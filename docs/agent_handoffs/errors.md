# pATHENA Error Handoff

## Baseline

- Develop source of truth: `develop/pathena-next@fec368f50307a9e24038baca3a80b10ee2a3c4fc`.
- Error worker entered this run at `postmerge/errors@aa4ebda2d09fdaa3a7622f1cd2f514c670a9e0b4`.
- Current workers: Spec/Core `53c3824e214b66e989cba1f425bfe7881190e12f`; Backend `195814616f394e1794aa4f3b2a16a584c092ab31`; UI `f94a6d1edaddd2c4fc009f60134fd1bce6440500`.
- Exact-current Develop canonical Quality: `34618898303@fec368f50307a9e24038baca3a80b10ee2a3c4fc = IN_PROGRESS`; no result inferred.
- Previous completed Develop canonical: `34612944150@8f320658368633dc8b2c586f4e5ec1c25a86d704 = SUCCESS`.
- Exact current Spec/Core canonical remains `34609297666@53c3824e214b66e989cba1f425bfe7881190e12f = FAILURE`.
- Exact current Spec/Core focused candidate remains `34609297743@53c3824e214b66e989cba1f425bfe7881190e12f = FAILURE`.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- OPEN: `ERR-0038`, `ERR-0033`, `ERR-0035`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`, `ERR-0031`, `ERR-0032`, `ERR-0034`, `ERR-0036`, `ERR-0037`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`.
- BLOCKED: none.

## Hard progress this run — ERR-0038 exact gate isolation strengthened

### ERR-0038 — Spec/Core exact-head Ruff failure

Status: `OPEN / P1 integration blocker / Spec-Core owned`.

The specialist worker head is still exactly `53c3824e214b66e989cba1f425bfe7881190e12f`; no newer Spec/Core candidate exists in this run. The exact file still contains the same import block beginning with `from __future__ import annotations`, `import uuid`, `from dataclasses import dataclass`, `from enum import Enum`, then the first-party `ClaimRevision` import. Errors did not mutate Core product code because Spec/Core owns this root cause.

Fresh exact job-level verification of canonical Quality `34609297666@53c3824e...` materially tightens the diagnosis:

- `Windows path safety = success`;
- `Linux storage regressions = success`;
- `Local install smoke = success`;
- inside `Python 3.12 quality`: specification validator = success, Ruff = failure, mypy = success, pytest = success;
- final canonical enforcement = failure because Ruff is red.

This proves the exact candidate has one failing gate and excludes a hidden Windows, Linux-storage, local-install, typing or semantic-test cascade. The authoritative Ruff diagnostic remains `I001 [*] Import block is un-sorted or un-formatted` at `src/athena/knowledge/revision_diff.py:3:1`.

The current `spec-core.md` handoff is stale relative to the actual branch head and still describes an older Search slice. It therefore cannot override the exact branch/run evidence above. Integrator should continue to hold this candidate until a newer exact Spec/Core SHA is Ruff-clean and exact-head focused tests plus canonical Quality are green.

Current Develop `fec368f5...` contains CI/UI candidate-verification work and has canonical `34618898303` already in progress. Errors started no competing canonical run.

Closure contract remains:

1. newer exact Spec/Core SHA with the current `I001` actually resolved;
2. exact-head Ruff green on the bounded changed files;
3. relevant revision-diff focused pytest green on the same SHA;
4. exact candidate canonical Quality green before `ERR-0038 = FIXED`.

### ERR-0033 — Emergency-reserve filesystem-object identity/capacity gap

Status remains `OPEN / P1 / Backend BE-046 owned`. Backend has no newer bounded exact-tested BE-046 candidate. The documented parent/target identity, inspection/acceptance, hardlink ownership and unknown-allocation fail-closed closure requirements remain applicable. Errors made no competing Storage product mutation.

### ERR-0035 — SQLite preflight identity through live writer startup

Status remains `OPEN / P1 / Backend BE-052 owned`. Backend has no newer bounded exact-tested BE-052 candidate. Errors made no competing Database/Storage product mutation.

## Integrator handoff

- Current Develop: `fec368f50307a9e24038baca3a80b10ee2a3c4fc`; canonical `34618898303 = IN_PROGRESS`.
- Previous completed Develop canonical: `34612944150@8f320658368633dc8b2c586f4e5ec1c25a86d704 = SUCCESS`.
- Highest current exact failure: `ERR-0038 = OPEN / P1`, Spec/Core-owned at `53c3824e214b66e989cba1f425bfe7881190e12f`; canonical `34609297666 = FAILURE`. Exact job evidence proves every other canonical job is green and, inside Python quality, only Ruff is red; diagnostic remains `I001` at `revision_diff.py:3:1`.
- `ERR-0033 = OPEN / P1`, Backend BE-046 owned; no Errors product mutation.
- `ERR-0035 = OPEN / P1`, Backend BE-052 owned; no Errors product mutation.
- No closed/stale cluster was reopened without current exact-SHA evidence.
- Preserve pypdf packaging, Frozen argv, two-EXE topology, bounded workers, adaptive 2048-context reserve, Windows lane-lock mapping, duplicate-column/Core-startup/storage-bootstrap guards and all Storage/Recovery/Security fail-closed invariants.