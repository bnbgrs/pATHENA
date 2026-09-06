# pATHENA Error Handoff

## Baseline

- Current baseline reviewed: `develop/pathena-next@1cc7b8dceb5b4ff098442e9f17f89b8cc36cb390`.
- Error branch prior head: `postmerge/errors@045e3fc6b73c7f79b7b305f6d284f22be8dba0a3`.
- Worker heads reviewed: Spec/Core `528ed7d3d7d80470a0fa78458ff2babd59bff20e`; Backend `2ea98794facffcae29d4f94b337fc84083028526`; Integrator/Develop `1cc7b8dceb5b4ff098442e9f17f89b8cc36cb390`.
- `spec-core.md`, `backend.md`, `ui.md`, `integrator.md`, worker heads and canonical Quality evidence were reviewed. `main` and `bnbgrs/ATHENA` remained read-only.

## Current state

- OPEN: `ERR-0018`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015`, `ERR-0016`, `ERR-0017`.
- STALE: `ERR-0014`.
- BLOCKED: none.

## ERR-0018 — fourth correction concretely rejected; guessing stopped

Spec/Core head `528ed7d3d7d80470a0fa78458ff2babd59bff20e` was concretely verified with canonical Quality `34057610329 = failure`. The run completed with exactly one primary gate failure: Ruff `I001 [*] Import block is un-sorted or un-formatted` at `src/athena/memory/context.py:3:1`.

Everything else is green on that exact SHA: Local install/Core-API restart PASS; Windows path safety PASS; Linux storage/API path-boundary PASS; Validator 63/63 PASS; mypy PASS; full pytest `4736 passed, 3 skipped, 2 warnings`; focused `tests/unit/test_personal_memory_context.py` also passes inside the full suite.

The exact current import block is:

```python
from __future__ import annotations

import uuid
from dataclasses import dataclass

from athena.memory.models import MemoryScopeKind, MemorySensitivity, PersonalMemorySnapshot
```

This is the previously proposed remaining permutation, and canonical Ruff still rejects it. Therefore the prior handoff claim that the root cause/corrective shape was finalized by enumerating four hand-written permutations was incorrect and is withdrawn. `ERR-0018` remains bounded to import-block normalization, but the next mutation must be produced from the repository-pinned `ruff==0.15.22` fixer itself (`python -m ruff check src/athena/memory/context.py --fix`) rather than another manually guessed ordering/wrapping variant.

No semantic Personal Memory defect is evidenced. Do not alter projection, protection, duplicate/snapshot identity or active-only behavior. Develop/Error still must not import this unintegrated Spec/Core feature as a workaround.

## Other evidence

- Backend current worker head `postmerge/backend@2ea98794facffcae29d4f94b337fc84083028526` is a history-preserving WAL-policy synchronization descendant; no independent primary error was confirmed in this scan.
- Current Develop `1cc7b8dceb5b4ff098442e9f17f89b8cc36cb390` advanced through integrator checkpoint-counter documentation/integration and has no exact completed canonical Quality verified by Error in this run; no promotion-ready claim.

## Integrator handoff

- Reject Spec/Core `528ed7d3d7d80470a0fa78458ff2babd59bff20e` as ready: exact Quality `34057610329` is Ruff-only failure.
- Do not repeat any hand-written import permutation. Spec/Core must run pinned `ruff==0.15.22` with `--fix` on `src/athena/memory/context.py`, commit only the fixer-produced import-block change, then rerun exact verification.
- Require exact corrected SHA: Ruff PASS, focused `tests/unit/test_personal_memory_context.py` PASS, full pytest PASS and canonical Quality SUCCESS before `ERR-0018` becomes FIXED.
- Do not weaken Ruff or import the unintegrated feature into Develop/Error as a workaround.
- Preserve Provider/Transport byte-budget/deadline/poisoning, Personal-Memory provenance/review, Windows path safety, Storage, Security and Recovery guards.

## Persistent Beta/release regression knowledge

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded workers; adaptive 2048-context Chat reserve; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

## Next scan

1. Verify the first Spec/Core descendant of `528ed7d3d7d80470a0fa78458ff2babd59bff20e` generated using pinned Ruff `--fix`; close `ERR-0018` only on exact Ruff + focused + full canonical evidence.
2. Consume latest Backend/UI canonical runs to completion and inspect the next exact current Develop/worker canonical or runtime signal.
3. Deduplicate any new failure against the ledger and persistent crash matrix before allocating a new ERR id.
