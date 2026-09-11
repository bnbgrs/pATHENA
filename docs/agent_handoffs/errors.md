# pATHENA Error Handoff

## Baseline

- Develop source of truth: `develop/pathena-next@e6ba3d7557bd46094ad4e8f067a238e1c2375f8e`.
- Error worker entered this run at `postmerge/errors@cb2ccb65217ff30bd9863ac77252f01e1318b5e9`.
- Current workers: Spec/Core `b8df82b23583d42a8d5ae8f387aea0fbd0e7859e`; Backend `fa995bf462aa8135d24f4e9e7059bc24f6992622`; UI `c51ef04787ef6affa2e6acc3a902e138cf6b7409`.
- Exact-current canonical Quality: `34567856833@e6ba3d7557bd46094ad4e8f067a238e1c2375f8e = IN_PROGRESS`; Windows path safety, Linux storage and Local-install are already `SUCCESS`, while Python quality remains in pytest. Last completed Develop canonical: `34560421777@95b636c982a800d75f7d219162a04f6c87976e9f = SUCCESS`.
- `postmerge/errors@cb2ccb65217ff30bd9863ac77252f01e1318b5e9` had zero canonical Quality runs before the ledger mutation; after ledger commit `3b6ebb2e3802febbda1aef5fdc55076e3d255aa2` there were still zero runs before this handoff update.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- OPEN: `ERR-0033`, `ERR-0035`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`, `ERR-0031`, `ERR-0032`, `ERR-0034`, `ERR-0036`, `ERR-0037`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`.
- BLOCKED: none.

## Hard progress this run — ERR-0033 root cause narrowed beyond parent-directory identity

### ERR-0033 — Emergency-reserve mutation identity binding gap

Status remains `OPEN`, P1, Backend / BE-046 owned.

Current Develop changes only the direct ERR-0037 teardown regression test plus Integrator handoff, so EmergencyReserve product source is unchanged from the last canonical-green Develop. The previously recorded native-Windows parent-directory identity gap therefore remains current.

New exact-source diagnosis: a directory-handle fix alone is insufficient. The destructive target file itself is not carried continuously through validation to unlink.

On non-POSIX failure cleanup the code performs `self.path.stat()` and validates that result against the originally created descriptor identity, but then executes a separate pathname `self.path.unlink()`. A same-parent substitution of `emergency.reserve` after the successful identity comparison and before `unlink()` can therefore redirect deletion to a different file. Normal non-POSIX `release()` has a still wider pathname sequence (`exists/is_file/stat -> unlink -> fsync_directory`) and never holds a file identity across the destructive boundary.

POSIX release binds the parent directory correctly with `root_fd`, but it opens the reserve file, reads its metadata, closes that descriptor, and only afterward executes `os.unlink(_RESERVE_FILENAME, dir_fd=root_fd)`. A replacement of that filename inside the same bound directory between close and unlink can therefore cause deletion of a different file while still passing all parent-directory identity checks.

This is deduplicated into ERR-0033 rather than creating another ID: the primary defect is incomplete filesystem-object identity continuity across EmergencyReserve mutation. BE-046 closure must bind both parent directory and destructive target identity, not merely repeat pathname checks.

Focused closure evidence now required from Backend:

1. Native-Windows adversarial parent substitution across create-success, failure-cleanup and release.
2. Same-parent `emergency.reserve` substitution between identity validation and unlink for non-POSIX cleanup and release.
3. Same-parent filename substitution during POSIX release after file inspection but before unlink.
4. Proof that no replacement file is deleted and that the operation fails closed while preserving physical allocation, exact release accounting and Storage/Recovery durability semantics.

Backend still owns BE-046 and has no tested bounded candidate in its current handoff, so Errors made no competing Storage product mutation.

### ERR-0035 — SQLite preflight identity is not carried into live writer startup

Status remains `OPEN`, P1, Backend / BE-052 owned. It remains distinct from ERR-0033 and has no current tested Backend candidate. No parallel product mutation was made.

### ERR-0037 — startup event-filter lifecycle race

Status remains `FIXED`. The completed closure evidence is canonical `34560421777@95b636c982a800d75f7d219162a04f6c87976e9f = SUCCESS`. Current Develop `e6ba3d7557bd46094ad4e8f067a238e1c2375f8e` adds a direct teardown regression test, but its canonical run is still in progress, so no new PASS is claimed and the closed cluster is not reopened.

## Integrator handoff

- Current Develop: `e6ba3d7557bd46094ad4e8f067a238e1c2375f8e`.
- Current canonical Quality: `34567856833 = IN_PROGRESS`; already-green jobs include Windows path safety, Linux storage and Local-install; Python pytest remains running.
- Last completed canonical: `34560421777@95b636c982a800d75f7d219162a04f6c87976e9f = SUCCESS`.
- `ERR-0033 = OPEN / P1`, Backend BE-046 owned. Root-cause closure now explicitly requires target-file identity continuity as well as parent-directory identity continuity.
- `ERR-0035 = OPEN / P1`, Backend BE-052 owned; no Errors product mutation.
- `ERR-0037 = FIXED`; current additional regression guard is awaiting canonical completion.
- No closed/stale cluster was reopened without exact-current reproduction.
- Preserve pypdf packaging, Frozen argv, two-EXE topology, bounded workers, adaptive 2048-context reserve, Windows lane-lock mapping, duplicate-column/Core-startup/storage-bootstrap guards, WAL exact-type fail-closed semantics, durable HANDLE-bound rename and reparse/path-safety invariants.
