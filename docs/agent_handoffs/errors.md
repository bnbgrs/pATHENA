# pATHENA Error Handoff

## Baseline

- Develop source of truth: `develop/pathena-next@b58964d577aba5d4fcb6c2969f48b445f3a1d4d7`.
- Error worker entered this run at `postmerge/errors@4134bb4ff3ab48b7e57fbfa86d92d6fd0e38cc2b`.
- Current workers: Spec/Core `b8df82b23583d42a8d5ae8f387aea0fbd0e7859e`; Backend `fa995bf462aa8135d24f4e9e7059bc24f6992622`; UI `dcfe263eaf4c23fc9513b362dada138ae3108854`.
- Exact-current canonical Quality: `34572000094@b58964d577aba5d4fcb6c2969f48b445f3a1d4d7 = IN_PROGRESS`.
- Previous exact Develop canonical: `34567856833@e6ba3d7557bd46094ad4e8f067a238e1c2375f8e = SUCCESS`.
- The sole Develop delta from `e6ba3d7557bd46094ad4e8f067a238e1c2375f8e` to `b58964d577aba5d4fcb6c2969f48b445f3a1d4d7` changes only `.github/workflows/ui-snapshot.yml` and `docs/agent_handoffs/integrator.md`; EmergencyReserve product/tests are unchanged.
- `postmerge/errors@4134bb4ff3ab48b7e57fbfa86d92d6fd0e38cc2b` had zero canonical Quality runs before the ledger mutation; after ledger commit `9633c724f10c2144294a16823da78e30a90adb01` there were still zero runs before this handoff update.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- OPEN: `ERR-0033`, `ERR-0035`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`, `ERR-0031`, `ERR-0032`, `ERR-0034`, `ERR-0036`, `ERR-0037`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`.
- BLOCKED: none.

## Hard progress this run — ERR-0033 POSIX failure-cleanup target identity seam

### ERR-0033 — Emergency-reserve mutation identity binding gap

Status remains `OPEN`, P1, Backend / BE-046 owned.

Current Develop is exact-source-equivalent to the previous green Develop for EmergencyReserve: the one new commit changes only UI snapshot diagnostics and Integrator documentation. The root cause therefore remains current on `b58964d577aba5d4fcb6c2969f48b445f3a1d4d7`.

Prior evidence established incomplete parent-directory and destructive target-file identity continuity in Windows/non-POSIX cleanup/release and POSIX release. This run identifies one additional destructive seam on exact current source: **POSIX failure cleanup**.

`_ensure_posix()` creates `emergency.reserve` relative to the bound `root_fd` and records only `created = True`. If any later operation fails, the exception path first closes the created file descriptor. It then executes `os.unlink(_RESERVE_FILENAME, dir_fd=root_fd)` whenever `created` is true, followed by `os.fsync(root_fd)`. The parent directory identity remains correctly bound, but the original target-file identity is no longer held or compared before the unlink. A same-parent replacement of the filename after creation and before cleanup can therefore redirect deletion to the replacement file.

The existing focused tests do not cover this seam. `test_store_cleans_partial_file_when_allocation_fails` verifies ordinary cleanup only. `test_posix_store_creation_does_not_publish_into_replaced_reserve_root` and `test_posix_store_release_does_not_unlink_replacement_root_file` inject parent-directory replacement, not same-parent filename replacement during the `_ensure_posix()` exception cleanup boundary.

This remains deduplicated into ERR-0033: the primary defect is incomplete EmergencyReserve filesystem-object identity continuity across destructive mutation. Backend still owns BE-046 and its current handoff contains no tested bounded product candidate, so Errors made no competing Storage product mutation.

Focused closure evidence now required from Backend:

1. Native-Windows adversarial parent substitution across create-success, failure-cleanup and release.
2. Same-parent `emergency.reserve` substitution between identity validation and unlink for non-POSIX cleanup and release.
3. Same-parent filename substitution during POSIX release after file inspection but before unlink.
4. Same-parent filename substitution during POSIX `_ensure_posix()` failure cleanup after the created descriptor has lost continuity.
5. Proof that no replacement file is deleted and the operation fails closed while preserving physical allocation, exact release accounting and Storage/Recovery durability semantics.

### ERR-0035 — SQLite preflight identity is not carried into live writer startup

Status remains `OPEN`, P1, Backend / BE-052 owned. It remains distinct from ERR-0033 and has no current tested Backend candidate. No parallel product mutation was made.

### ERR-0037 — startup event-filter lifecycle race

Status remains `FIXED`. In addition to its earlier closure evidence, canonical Quality `34567856833@e6ba3d7557bd46094ad4e8f067a238e1c2375f8e = SUCCESS` now verifies the direct teardown regression guard on exact Develop.

## Integrator handoff

- Current Develop: `b58964d577aba5d4fcb6c2969f48b445f3a1d4d7`.
- Current canonical Quality: `34572000094 = IN_PROGRESS`; no PASS/FAIL is inferred until completion.
- Previous completed canonical: `34567856833@e6ba3d7557bd46094ad4e8f067a238e1c2375f8e = SUCCESS`.
- `ERR-0033 = OPEN / P1`, Backend BE-046 owned. Closure scope now explicitly includes POSIX `_ensure_posix()` failure-cleanup target identity, in addition to the already known Windows/non-POSIX and POSIX release seams.
- `ERR-0035 = OPEN / P1`, Backend BE-052 owned; no Errors product mutation.
- `ERR-0037 = FIXED`; direct regression guard now has completed canonical evidence.
- No closed/stale cluster was reopened without exact-current reproduction.
- Preserve pypdf packaging, Frozen argv, two-EXE topology, bounded workers, adaptive 2048-context reserve, Windows lane-lock mapping, duplicate-column/Core-startup/storage-bootstrap guards, WAL exact-type fail-closed semantics, durable HANDLE-bound rename and reparse/path-safety invariants.
