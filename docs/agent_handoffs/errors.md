# pATHENA Error Handoff

## Baseline

- Develop: `522a01050dba5b4dafa81d60573bd185a8e7e15b` (`test(ci): lock core focused candidate invariants`).
- Exact Develop parent `b8afe9661387c4a1a3d65f539c39ca772f37329c` canonical Quality `34710920451 = SUCCESS`.
- Current Develop canonical `34712404459@522a01050dba5b4dafa81d60573bd185a8e7e15b = IN_PROGRESS`; no competing run started by Errors.
- Errors worker entered this run at `3e3915d5cb0c3964661db1fcef100f98664915c1`; ledger update commit: `fd7905d08df53946e8f884698c145872bc299b32`.
- Current workers: Spec/Core `f86df7dc1b4f4be5aeb2000986eb7965cafa8dcb`; Backend `956cffa5dca29cbf5af71fd6e06bd87f2a79b4cc`; UI `460e35e74d8c529a5880356bf30b9099d80e39de`.
- `main` and `bnbgrs/ATHENA` remain read-only.

## Current error state

- OPEN: `ERR-0042`, `ERR-0045`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: `ERR-0043`.
- FIXED: `ERR-0044`, `ERR-0041`, `ERR-0040`, `ERR-0035`, `ERR-0033` and prior closed clusters.
- STALE: `ERR-0038`, `ERR-0039` and prior stale clusters.

## ITERATION-1 — ERR-0044 integrated harness repair verified

`ERR-0044 = FIXED / P2`.

The repository-side Core Focused harness repair is already present on Develop parent `b8afe9661387c4a1a3d65f539c39ca772f37329c` and exact canonical Quality `34710920451 = SUCCESS`.

The repaired workflow uses `git diff --diff-filter=ACMR --name-only` for all three relevant Core path selections, excluding deleted paths while preserving added/copied/modified/renamed candidates. Ruff remediation cleanliness now uses `git status --porcelain --untracked-files=no`, so only the workflow's own untracked evidence is ignored; tracked candidate mutations remain fail-closed. Exact candidate reset and outcome enforcement remain intact.

Current Develop `522a01050dba5b4dafa81d60573bd185a8e7e15b` adds dedicated regression tests locking these invariants. Its canonical Quality `34712404459` is still running, but the root repair itself already has integrated exact-SHA canonical success on its parent.

No UI product defect is associated with this cluster.

## ITERATION-2 — ERR-0043 owner guard repair isolated from successor fixture failure

`ERR-0043 = FIXED_PENDING_VERIFY / P1`.

Current Backend exact head is `956cffa5dca29cbf5af71fd6e06bd87f2a79b4cc` (`fix(storage): preserve sidecar identity guard during WAL publication`). Exact runs:

- Backend Focused `34710537347 = SUCCESS`.
- Storage Focused `34710537370 = FAILURE`.
- canonical Quality `34710537369 = FAILURE`.

The exact Storage artifact was downloaded. Results are Ruff PASS, mypy PASS for 35 source files, and pytest `2 failed, 30 passed`.

Crucially, the original `ERR-0043` negative guard test `test_bound_preflight_rejects_sidecar_mutation_before_writer_open` is no longer among the failures. The repair now rejects identity changes unless the primary database identity is unchanged and the preflight had both sidecars absent while the current state has both sidecars present; that exceptional transition is then re-inspected and exact-identity checked. Replacement of a sidecar that existed at preflight therefore remains fail-closed.

Canonical Linux storage regressions, Windows path/release guards, Ruff, mypy, specification validator and Local Install are all green. The current global red result is caused by the two new fixture tests in `ERR-0045`, so the foreign-existing-sidecar acceptance root cause has current corrective evidence but cannot be marked `FIXED` until the owner candidate is globally green and integrated.

## ITERATION-3 — ERR-0045 opened from exact Storage diagnostics

`ERR-0045 = OPEN / P2`.

Both remaining failures on Backend `956cffa5...` occur inside `_inspect_without_sidecars()` before the intended publication guard is exercised:

- `test_bound_preflight_rejects_partial_sidecar_publication`
- `test_bound_preflight_accepts_valid_concurrent_sidecar_publication`

The helper checkpoints the database, closes the checkpoint connection, unlinks `athena.db-wal` and `athena.db-shm`, then calls `inspect_database_read_only(database_path)`. On the exact Linux runner, after that read-only SQLite inspection `identity.wal.exists` is already true (and SHM is published as well), so the helper fails at `assert not identity.wal.exists`.

The code explains the observation: `inspect_database_read_only()` opens the existing database with SQLite URI `mode=ro`, enables `PRAGMA query_only`, reads metadata/quick-check, and captures the file-set identity before closing. For this WAL-mode fixture SQLite recreates/publishes sidecars during that preflight. The test therefore cannot manufacture a genuine absent-sidecar preflight merely by deleting WAL/SHM immediately before calling the normal inspector.

Safe owner action: construct a valid state whose journal mode genuinely permits a sidecar-absent preflight, prove both sidecars are absent in the returned preflight identity, then exercise partial and complete publication. Do not mock away identity enforcement or weaken Storage/Recovery checks. Also determine whether the implementation's absent-at-preflight publication exception is reachable through a genuine production preflight; if not, prefer stricter/simpler fail-closed behavior over an unprovable exception path.

## ITERATION-4 — current independent workers classified

Spec/Core remains independently blocked by `ERR-0042`: exact head `f86df7dc1b4f4be5aeb2000986eb7965cafa8dcb`, Core Focused `34709904332 = FAILURE`, canonical `34709904327 = FAILURE`; exact blocker remains one Ruff `I001`, while six focused behavior tests pass. Develop's `ERR-0044` harness repair removes the remediation-worktree side issue but does not format the owner-held test import block.

UI current head is `460e35e74d8c529a5880356bf30b9099d80e39de`; UI Focused `34712289041 = SUCCESS`, canonical `34712289012 = IN_PROGRESS` at observation time. No current exact UI failure is opened from this state.

## Integrator handoff

- `ERR-0042 = OPEN / P1`; Spec/Core `f86df7dc1b4f4be5aeb2000986eb7965cafa8dcb`; exact Core Focused `34709904332 = FAILURE`, canonical `34709904327 = FAILURE`; one Ruff I001, six focused tests pass.
- `ERR-0043 = FIXED_PENDING_VERIFY / P1`; Backend `956cffa5dca29cbf5af71fd6e06bd87f2a79b4cc`; former foreign-sidecar negative test now passes, but candidate remains red due `ERR-0045`. Do not integrate until exact Storage Focused and canonical are green.
- `ERR-0045 = OPEN / P2`; Backend same exact SHA; Storage Focused `34710537370 = FAILURE`, exact pytest `2 failed, 30 passed`; both failures are invalid absent-sidecar fixture setup because normal read-only preflight republishes WAL/SHM before the absence assertion.
- `ERR-0044 = FIXED / P2`; integrated harness fix at `b8afe9661387c4a1a3d65f539c39ca772f37329c`, canonical `34710920451 = SUCCESS`; current `522a010...` adds invariant regression tests and is still under canonical verification.
- UI `460e35e74d8c529a5880356bf30b9099d80e39de`: UI Focused success; canonical still active, so no promotion claim yet.

## CI discipline

- Before the first Errors mutation, `postmerge/errors@3e3915d5cb0c3964661db1fcef100f98664915c1` had zero queued and zero in-progress workflow runs.
- After ledger commit `fd7905d08df53946e8f884698c145872bc299b32`, Errors again had zero queued and zero in-progress workflow runs before this handoff commit.
- No canonical run was started or duplicated by Errors.
- No product code or foreign worker branch was mutated.

## NEXT_ROOT_CAUSE

1. Consume the next Backend successor first: verify `ERR-0045` fixture repair and ensure `ERR-0043` remains fail-closed; require Storage Focused + canonical success before owner readiness.
2. Consume the next Spec/Core successor for `ERR-0042`; require exact Ruff and canonical success.
3. Consume Develop `34712404459@522a010...`; if green it strengthens the already closed `ERR-0044` with dedicated invariant tests, but a failure must be classified by its exact signature rather than reopening the old root automatically.
4. Consume UI canonical `34712289012@460e35e...` and open a UI error only if a current exact failure exists.
