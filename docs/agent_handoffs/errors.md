# pATHENA Error Handoff

## Baseline

- Develop source of truth: `develop/pathena-next@2ac4a605853fdc82b320f97b96494f3e17eaffa7`.
- Error worker entered this run at `postmerge/errors@685db6e76d68b32c620192d123edcb902e9b267a`.
- Current workers: Spec/Core `5cbd31a5cf46c7cfcb75411d8216b3890aa5dec4`; Backend `195814616f394e1794aa4f3b2a16a584c092ab31`; UI `7f33ae92ec84d6a82052e4196bdd74c829fdf079`.
- Exact-current Develop canonical Quality: `34607013250@2ac4a605853fdc82b320f97b96494f3e17eaffa7 = IN_PROGRESS`; no result inferred.
- Previous completed Develop canonical: `34601243038@b26eea46c89a8b628c2006d24d1fdac7492baa91 = SUCCESS`.
- Exact current Spec/Core canonical: `34603615414@5cbd31a5cf46c7cfcb75411d8216b3890aa5dec4 = FAILURE`.
- Exact current Spec/Core focused candidate: `34603615415@5cbd31a5cf46c7cfcb75411d8216b3890aa5dec4 = FAILURE` at the Ruff job.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- OPEN: `ERR-0038`, `ERR-0033`, `ERR-0035`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`, `ERR-0031`, `ERR-0032`, `ERR-0034`, `ERR-0036`, `ERR-0037`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`.
- BLOCKED: none.

## Hard progress this run — ERR-0038 failed repair requalified on newer exact SHA

### ERR-0038 — Spec/Core exact-head Ruff failure

Status: `OPEN / P1 integration blocker / Spec-Core owned`.

The prior candidate `2a9b76dd3581cb13052741907d0fad8357553536` failed canonical Quality because Ruff rejected `src/athena/knowledge/revision_diff.py`. Spec/Core has now advanced the branch to `5cbd31a5cf46c7cfcb75411d8216b3890aa5dec4` with a commit intended to close that lint regression.

That repair is not successful evidence. Exact canonical Quality `34603615414@5cbd31a5...` is `FAILURE`, and the exact focused candidate run `34603615415@5cbd31a5...` is also `FAILURE`; its `Exact Core candidate lint and focused tests` check fails at Ruff. Therefore `ERR-0038` remains current and is not moved to `FIXED_PENDING_VERIFY`.

Source inspection of the exact head still shows the standard-library block as:

- `import uuid`
- `from dataclasses import dataclass`
- `from enum import Enum`
- `from typing import TypeAlias`

The exact focused Ruff failure means the specialist must consume the current Ruff diagnostic rather than treating the commit message as closure. The current PR remains bounded to `src/athena/knowledge/revision_diff.py` and `tests/unit/test_claim_revision_diff.py`, so this is still a contained Spec/Core integration blocker rather than a broad product cascade.

Integrator evidence already holds this candidate until both exact-head Ruff and focused pytest are observable and green. Develop now contains a focused-workflow observability improvement that allows both sibling evidence steps to run while preserving fail-closed aggregate enforcement; that tooling change does not retroactively make `5cbd31a5...` READY.

Errors made no Core product mutation because Spec/Core actively owns the same root cause. No canonical run was started by Errors while Develop canonical `34607013250` is already in progress.

Closure contract:

1. Newer exact Spec/Core SHA with the current Ruff diagnostic resolved without semantic/test weakening.
2. Exact-head Ruff green on the bounded changed files.
3. Relevant revision-diff focused pytest green on the same SHA.
4. Exact candidate canonical Quality green before `ERR-0038 = FIXED`.

### ERR-0033 — Emergency-reserve filesystem-object identity/capacity gap

Status remains `OPEN / P1 / Backend BE-046 owned`. Backend has synchronized onto a current canonical-green Develop tree but has not supplied a bounded exact-tested BE-046 candidate. The documented parent/target identity, inspection/acceptance, hardlink ownership and unknown-allocation fail-closed closure requirements remain applicable. Errors made no competing Storage product mutation.

### ERR-0035 — SQLite preflight identity through live writer startup

Status remains `OPEN / P1 / Backend BE-052 owned`. Backend has not supplied a bounded exact-tested BE-052 candidate. Errors made no competing Database/Storage product mutation.

## Integrator handoff

- Current Develop: `2ac4a605853fdc82b320f97b96494f3e17eaffa7`; canonical `34607013250 = IN_PROGRESS`.
- Previous completed Develop canonical: `34601243038@b26eea46c89a8b628c2006d24d1fdac7492baa91 = SUCCESS`.
- Highest current exact failure: `ERR-0038 = OPEN / P1`, Spec/Core-owned at `5cbd31a5cf46c7cfcb75411d8216b3890aa5dec4`; canonical `34603615414 = FAILURE` and exact focused `34603615415 = FAILURE` at Ruff. The attempted repair therefore does not qualify for promotion.
- `ERR-0033 = OPEN / P1`, Backend BE-046 owned; no Errors product mutation.
- `ERR-0035 = OPEN / P1`, Backend BE-052 owned; no Errors product mutation.
- No closed/stale cluster was reopened without current exact-SHA evidence.
- Preserve pypdf packaging, Frozen argv, two-EXE topology, bounded workers, adaptive 2048-context reserve, Windows lane-lock mapping, duplicate-column/Core-startup/storage-bootstrap guards and all Storage/Recovery/Security fail-closed invariants.
