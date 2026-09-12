# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA-evidenced failures are active; cascades are deduplicated. `FIXED` requires real verification on the relevant integrated exact SHA. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, assertion/static-check weakening, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop source of truth: `develop/pathena-next@522a01050dba5b4dafa81d60573bd185a8e7e15b` (`test(ci): lock core focused candidate invariants`).
- Develop parent `b8afe9661387c4a1a3d65f539c39ca772f37329c` (`fix(ci): harden core focused candidate selection`) has exact canonical Quality `34710920451 = SUCCESS`.
- Current Develop canonical Quality: `34712404459@522a01050dba5b4dafa81d60573bd185a8e7e15b = IN_PROGRESS`; Errors started no competing canonical run.
- Error worker entered this run at `postmerge/errors@3e3915d5cb0c3964661db1fcef100f98664915c1`.
- Current workers: Spec/Core `f86df7dc1b4f4be5aeb2000986eb7965cafa8dcb`; Backend `956cffa5dca29cbf5af71fd6e06bd87f2a79b4cc`; UI `460e35e74d8c529a5880356bf30b9099d80e39de`.
- Spec/Core exact `f86df7dc1b4f4be5aeb2000986eb7965cafa8dcb`: Core Focused Candidate `34709904332 = FAILURE`; canonical Quality `34709904327 = FAILURE`; exact current blocker remains one Ruff `I001` while six focused behavior tests pass.
- Backend exact `956cffa5dca29cbf5af71fd6e06bd87f2a79b4cc`: Backend Focused Candidate `34710537347 = SUCCESS`; Storage Focused Candidate `34710537370 = FAILURE`; canonical Quality `34710537369 = FAILURE`. Canonical specification validator, Ruff, mypy, Linux storage regressions, Windows path safety/release guards and Local Install are green; canonical failure is full pytest.
- UI exact `460e35e74d8c529a5880356bf30b9099d80e39de`: UI Focused Candidate `34712289041 = SUCCESS`; canonical Quality `34712289012 = IN_PROGRESS` at observation time.
- `postmerge/errors@3e3915d5cb0c3964661db1fcef100f98664915c1` had zero queued and zero in-progress workflow runs before this mutation.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current state

- OPEN: `ERR-0042`, `ERR-0045`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: `ERR-0043`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`, `ERR-0031`, `ERR-0032`, `ERR-0033`, `ERR-0034`, `ERR-0035`, `ERR-0036`, `ERR-0037`, `ERR-0040`, `ERR-0041`, `ERR-0044`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`, `ERR-0038`, `ERR-0039`.
- BLOCKED: none at top level.

## ERR-0045 — Backend absent-sidecar test fixture recreates WAL/SHM during read-only preflight

- Severity: P2 Storage test/harness integration blocker.
- Status: `OPEN`.
- Current exact reproducer: `postmerge/backend@956cffa5dca29cbf5af71fd6e06bd87f2a79b4cc` (`fix(storage): preserve sidecar identity guard during WAL publication`).
- Exact CI: Storage Focused Candidate `34710537370 = FAILURE`; canonical Quality `34710537369 = FAILURE`; Backend Focused Candidate `34710537347 = SUCCESS`.
- Exact downloaded Storage-focused diagnostics: Ruff passes; mypy passes (`Success: no issues found in 35 source files`); pytest is `2 failed, 30 passed`.
- Both failures occur before the new publication guard is exercised. `_inspect_without_sidecars()` checkpoints and deletes `-wal`/`-shm`, then calls `inspect_database_read_only(path)`. That read-only SQLite preflight opens the existing WAL-mode database and, on the exact Linux runner, WAL/SHM exist again before the helper asserts absence. Both `test_bound_preflight_rejects_partial_sidecar_publication` and `test_bound_preflight_accepts_valid_concurrent_sidecar_publication` therefore fail at `assert not identity.wal.exists`.
- This is distinct from `ERR-0043`: the original foreign-existing-sidecar substitution test is no longer among the failures. The remaining red candidate is caused by an invalid absent-sidecar fixture assumption, not evidence that foreign replacement is still accepted.
- Required safe owner repair: construct a genuine sidecar-absent preflight state without asking a WAL-mode read-only inspection to preserve manually deleted sidecars. A bounded approach is to establish a valid database state whose journal mode can legitimately remain without WAL/SHM through preflight, then prove `wal.exists == False` and `shm.exists == False` before exercising the absent-to-publication transition. Do not mock away identity checks, weaken Recovery/Storage guards, or delete/skip the negative tests.
- Also verify whether the absent-sidecar acceptance branch is reachable through a real production preflight; if it is not, simplify fail-closed behavior rather than retaining an unprovable exception path.
- Closure requirement: exact Storage Focused and canonical Quality green on one unchanged Backend SHA, then integrated Develop canonical green before `FIXED`.

## ERR-0043 — Backend SQLite startup revalidation accepts foreign sidecar replacement

- Severity: P1 Storage/release integration blocker.
- Status: `FIXED_PENDING_VERIFY`.
- Historical exact reproducer: `postmerge/backend@c5151466928dbe751a2e62c210717d0858a74bd3`, Storage Focused `34708379880 = FAILURE`, where `test_bound_preflight_rejects_sidecar_mutation_before_writer_open` proved a replaced existing sidecar was accepted.
- Owner repair: `postmerge/backend@956cffa5dca29cbf5af71fd6e06bd87f2a79b4cc` (`fix(storage): preserve sidecar identity guard during WAL publication`). `_revalidate_existing_identity()` now returns immediately only on exact identity equality; otherwise it requires unchanged primary identity and allows a changed sidecar set only when both sidecars were absent at preflight and both are now published, followed by a fresh read-only inspection and exact identity confirmation. Existing-sidecar replacement remains fail-closed.
- Exact current Storage diagnostics are `2 failed, 30 passed`. The two failures are only the new `_inspect_without_sidecars()` fixture assertions described in `ERR-0045`; the former release-guard test `test_bound_preflight_rejects_sidecar_mutation_before_writer_open` is no longer a failure.
- Canonical exact `34710537369`: specification validator, Ruff, mypy, Linux storage regressions, Windows path safety/release guards and Local Install all pass; only full pytest fails, consistent with the two `ERR-0045` tests.
- Therefore the original foreign-sidecar acceptance root cause has current exact corrective evidence, but final verification remains pending because the owner candidate is globally red and not integrated.
- Closure requirement: first close `ERR-0045` without weakening this guard; require exact Storage Focused + canonical `SUCCESS` on the unchanged repaired Backend successor, then integrated Develop canonical `SUCCESS` before `FIXED`.

## ERR-0042 — current Spec/Core Ruff blocker in revision-change slice

- Severity: P1 integration blocker.
- Status: `OPEN`.
- Historical current-run reproducer predecessor: `postmerge/spec-core@39360af3da29101e3038447121ad8d80d11b9f07`, where canonical diagnostics identified Ruff `I001` at `tests/unit/test_revision_change_explanation.py:1:1` and full pytest was `4995 passed, 17 skipped`.
- Current owner head remains `postmerge/spec-core@f86df7dc1b4f4be5aeb2000986eb7965cafa8dcb` (`fix(core): normalize revision change import`).
- Exact successor diagnostics contain exactly one Ruff `I001 [*] Import block is un-sorted or un-formatted` at `tests/unit/test_revision_change_explanation.py:1:1`; focused pytest is `6 passed in 0.17s`.
- Core Focused Candidate `34709904332 = FAILURE`; canonical Quality `34709904327 = FAILURE` on the same exact SHA. Behavior-focused tests remain green; ownership stays Spec/Core.
- The separate Core-Focused remediation-harness defect that previously blocked Ruff fix-diff generation has been repaired on Develop under `ERR-0044`; that harness repair does not itself format this owner-held Spec/Core test file.
- Required next owner action: apply only the pinned Ruff formatting result to the test import block and require Core Focused plus canonical Quality `SUCCESS` on one unchanged exact worker SHA, followed by integrated Develop canonical `SUCCESS` before `FIXED`.

## ERR-0044 — Core Focused harness selects deleted files from PR diff

- Severity: P2 CI/harness integration blocker.
- Status: `FIXED`.
- Historical reproducer: Core Focused Candidate `34709115243` on `postmerge/ui@1c6c3475945c7ee0ba4d7514b81dd4d444d843e6`, where deleted `src/athena/knowledge/orphan_knowledge.py` and `tests/unit/test_orphan_knowledge.py` were incorrectly passed to Ruff/Pytest.
- Root cause was `.github/workflows/core-focused-candidate.yml` selecting paths with deletion-inclusive `git diff --name-only` and its Ruff-remediation cleanliness check seeing the workflow's own untracked evidence files.
- Develop repair is present by `b8afe9661387c4a1a3d65f539c39ca772f37329c`: all three Core path selections use `git diff --diff-filter=ACMR --name-only`; remediation cleanliness uses `git status --porcelain --untracked-files=no`, preserving tracked-mutation detection while ignoring only untracked diagnostics; immutable exact-candidate reset/enforcement remains intact.
- Exact integrated verification: canonical Quality `34710920451@b8afe9661387c4a1a3d65f539c39ca772f37329c = SUCCESS`.
- Current Develop successor `522a01050dba5b4dafa81d60573bd185a8e7e15b` adds dedicated regression tests that lock the three `--diff-filter=ACMR` selectors, forbid the former deletion-inclusive selector, require the tracked-worktree cleanliness semantics, and preserve immutable reset. Its canonical `34712404459` was still running at observation time; this successor does not invalidate the already canonical-green repair.
- No UI product defect is associated with this cluster.

## ERR-0041 — Spec/Core provenance explanation import-order Ruff blocker

- Severity: P1 integration blocker.
- Status: `FIXED`.
- Historical reproducer: `postmerge/spec-core@23dc4c79f1e44cd099992eb23636b2c95014c790`; exact root cause was Ruff `I001` at `src/athena/knowledge/provenance_explanation.py:3:1`.
- Owner repair lineage culminated at `postmerge/spec-core@1f61104959dc6a7d7fcff6051fb013f5f6894706`, with Core Focused Candidate `34701843776 = SUCCESS` and canonical Quality `34701843759 = SUCCESS`.
- Integrated closure: `34703645964@develop/pathena-next@452547ab46c5d8c678c22c3e1fb9d34652b653fd = SUCCESS`.

## ERR-0040 — Scheduled-materialization test fixture violates canonical SQLite journal-mode invariant

- Severity: P1 integration blocker.
- Status: `FIXED`.
- Historical reproducer `postmerge/backend@e4aacf8004e08fddacb41cebe687453a759444cf`; root-cause repair `postmerge/backend@359b675a37b5b59210399bee1506afddc6ccee13`.
- Exact worker verification: Backend Focused `34693685313 = SUCCESS`; canonical `34693685375 = SUCCESS`.
- Integrated closure: `34694827693@develop/pathena-next@cfdcac0bd51973bc18343006a9fb02f6c098a3c0 = SUCCESS`.

## ERR-0035 — SQLite preflight-to-writer file-set identity continuity

- Severity: P1.
- Status: `FIXED`.
- Integrated closure: `34680853488@develop/pathena-next@8c885669ce3a3d718588d0327828341684c88c71 = SUCCESS`.

## ERR-0033 — Emergency-reserve filesystem-object identity and physical-reclamation gap

- Severity: P1.
- Status: `FIXED`.
- Integrated closure: `34666307002@develop/pathena-next@ca87e42c8820c47db7d6626feb17698560cd3b49 = SUCCESS`.

## ERR-0039 / ERR-0038

Both are `STALE`; historical Spec/Core Ruff failures are superseded and may be reopened only with a new current exact-SHA reproduction.

## Persistent release guards

Historical closed/stale clusters remain unchanged. Reopen only with current exact-SHA reproduction. Persistent guards remain binding: Windows `pypdf` packaging; fail-closed Frozen argv; separate Desktop/Worker EXEs; exactly one Desktop with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock `PermissionError` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError`; duplicate-column/Core-startup/storage-bootstrap signatures. Before Beta/release promotion, execute the known-crash regression matrix on the exact candidate SHA. No promotion-ready claim while a known crash signature or removed guard is current.
