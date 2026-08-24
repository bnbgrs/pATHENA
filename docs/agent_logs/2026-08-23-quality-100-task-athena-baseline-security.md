# pATHENA quality run — ATHENA baseline and security boundaries

Date: 2026-08-23
Branch: `agent/pathena`
Scope: pATHENA writes only; `bnbgrs/ATHENA` inspected read-only as compatibility baseline.

## Baseline checks

- pATHENA and ATHENA retain the same Python 3.12 quality-tool pins: Ruff 0.15.22, mypy 2.3.0, pytest 9.1.1, uv 0.11.21.
- pATHENA quality execution remains Spec -> Ruff -> mypy -> pytest, so later stages are not interpreted when an earlier stage fails.
- The branch is highly concurrent. Every attempted same-file write used a freshly read blob SHA; stale writes were discarded after GitHub 409 responses.
- `agent/pathena` is substantially diverged from pATHENA `main`, so this run intentionally avoided broad rebases or branch rewrites.

## Concrete repairs

### Research model formatting

`src/athena/research/models.py` contained an extra top-level blank line between `ResearchCoverage` and `ResearchSynthesisStage`. The formatting-only repair was committed as:

- `c2266b9c161aa30677ab70bcce67ed4e127b5b45` — `fix: normalize research model spacing`

No model field, enum value, persistence contract, or behavior changed.

### Protected Blob DEK lifecycle

Both current ATHENA and pATHENA placed `wrap_blob_dek()` and staging-directory creation before the `finally` that wipes the per-blob DEK. pATHENA was hardened without changing ATHENA: the wipe region now begins immediately after DEK creation and cleanup only unlinks a staging path after one has actually been allocated.

Commits:

- `7d333f0c5d0d1e579eef43d338d7b7f2aa116e8b` — `fix: wipe protected blob DEK on early capture failure`
- `ff16d0d699451559f303550337621e302c2c748d` — initial wrap-failure regression test
- `598a2f6fb3cd4c01afbeb7c34fb57ba764278671` — accurate `tmp_path: Path` annotation
- `f75fa6cd0387a286e2923d3b8c8ea606f04bf1bd` — staging-directory failure regression coverage

The tests assert that the in-memory DEK has been zeroed after both an envelope-wrap failure and a staging-directory creation failure.

## Parallel-agent findings

- A Ruff F401 risk in `pathena_jobs_experience_2800.py` (`QListWidget`/`QPushButton` imports) was found, but a parallel agent removed those unused imports before this run could write; the stale write was rejected with 409 and was not forced.
- Retrieval degradation briefly changed from ATHENA-compatible duck typing to concrete provider identity. The concurrently added test required duck-typed resolver compatibility. Before this run wrote a competing patch, the latest branch had already converged on capability validation via an `_EmbeddingResolver` Protocol and `resolve_model` callable check.
- The latest inspected `doctor.py` storage-root diagnostics preserve existing application lifecycle boundaries and introduce no persistent state mutation beyond temporary writability probes.

## Verification status

The GitHub commit-status endpoint had not yet registered a status for the latest run commits when this log was written. No CI PASS is claimed here. The container runtime also could not clone GitHub due DNS restrictions, so no local Ruff/mypy/pytest result is fabricated. Verification must use the subsequent push-triggered Quality Gate on the exact branch checkout.
