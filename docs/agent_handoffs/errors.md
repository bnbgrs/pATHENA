# pATHENA Error Handoff

## Baseline

- Develop source of truth: `develop/pathena-next@b1e77f8a4b90c12fe75e257b96303cc137d760a9`.
- Error worker entered this run at `postmerge/errors@d9a74db65557bb1db89641c3cbc910d6d1bf6ec1`.
- Current workers: Spec/Core `b8df82b23583d42a8d5ae8f387aea0fbd0e7859e`; Backend `fa995bf462aa8135d24f4e9e7059bc24f6992622`; UI `8ba83c27fcfc19c94339908a42352617421556f8`.
- Latest exact-current canonical Quality: `34556269271@b1e77f8a4b90c12fe75e257b96303cc137d760a9 = IN_PROGRESS`; no new failure is inferred while it is running.
- Last completed Develop canonical Quality: `34552555541@f729959c7b2b0f14b495f06779c790d6cd0d281d = SUCCESS`.
- `postmerge/errors@d9a74db65557bb1db89641c3cbc910d6d1bf6ec1` had zero canonical Quality runs before the ledger mutation; after ledger commit `2936c8607e0ddbde08df7f856f01daa633599a34` there were still zero runs before this handoff update.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- OPEN: `ERR-0033`, `ERR-0035`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`, `ERR-0031`, `ERR-0032`, `ERR-0034`, `ERR-0036`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`.
- BLOCKED: none.

## Hard progress this run — ERR-0033 adversarial seam narrowed on exact-current Develop

### ERR-0033 — Windows emergency-reserve directory-identity binding gap

Status remains `OPEN`, P1, Backend / BE-046 owned.

The current Develop SHA `b1e77f8a4b90c12fe75e257b96303cc137d760a9` was inspected directly. Its exact one-commit delta from canonical-green parent `f729959c7b2b0f14b495f06779c790d6cd0d281d` changes only `.github/workflows/ui-snapshot.yml` and `docs/agent_handoffs/integrator.md`; EmergencyReserve production code is unchanged. The BE-046 source-trace evidence is therefore current rather than historical.

The root-cause boundary is now narrower. POSIX carries `reserve_root` as `root_fd`, creates/unlinks the reserve relative to that descriptor, fsyncs that same descriptor and verifies path-to-handle directory identity. Windows/non-POSIX verifies the newly created reserve **file** with `fstat` versus pathname `stat`, which is useful and must remain, but no parent-directory handle is retained.

Three concrete mutation seams remain:

1. Create success: after file-identity verification and allocation/fsync, the file descriptor is closed and durability is finalized with `fsync_directory(self.reserve_root)` by pathname. The parent directory can be re-resolved independently of the directory in which the validated file was created.
2. Create failure cleanup: cleanup re-resolves `self.path`, compares only file identity, conditionally unlinks by pathname, then fsyncs `self.reserve_root` by pathname. The file guard prevents deleting an unrelated replacement file, but does not prove cleanup/durability stayed inside the originally validated parent directory.
3. Release: `self.path.stat(follow_symlinks=False)` -> `self.path.unlink()` -> `fsync_directory(self.reserve_root)` executes with neither a held reserve-file descriptor nor a held reserve-directory handle. This is the clearest adversarial regression seam because logical size is captured before unlink while object/directory identity is not carried through unlink and durability.

This provides a specific focused-test contract for Backend: native-Windows tests should force reserve-parent substitution at those seams and require fail-closed behavior without deleting or fsyncing through the substituted parent. A pathname-only recheck is insufficient for handle-bound continuity. Physical non-sparse allocation, exact release accounting and Storage/Recovery fail-closed semantics must remain unchanged.

No product mutation was made on `postmerge/errors`: Backend currently owns BE-046 and its latest handoff has no tested bounded candidate.

### ERR-0035 — SQLite preflight identity is not carried into live writer startup

Status remains `OPEN`, P1, Backend / BE-052 owned. It remains distinct from ERR-0033 and is not selected ahead of BE-046 while Backend itself still ranks BE-046 first. No parallel product mutation was made.

### Closed clusters

`ERR-0036` remains `FIXED` via canonical `34544225707@7a6b9ee59f059202f1f3b5c5b8f7b70e319bec2c = SUCCESS`.

`ERR-0034` remains `FIXED` via canonical `34522965434@7fa2108d820cfc5b48a9f92d42ffa61697b74818 = SUCCESS`.

## Integrator handoff

- Current Develop: `b1e77f8a4b90c12fe75e257b96303cc137d760a9`.
- Current canonical Quality: `34556269271 = IN_PROGRESS`; consume it before classifying any new Develop failure.
- Last completed canonical: `34552555541@f729959c7b2b0f14b495f06779c790d6cd0d281d = SUCCESS`.
- `ERR-0033 = OPEN / P1`, Backend BE-046 owned. Exact-current evidence now identifies the concrete Windows create-success, cleanup and release seams where file identity is guarded but parent-directory identity is not carried through mutation/durability.
- `ERR-0035 = OPEN / P1`, Backend BE-052 owned; no Errors product mutation.
- No closed/stale cluster was reopened without exact-current reproduction.
- Preserve pypdf packaging, Frozen argv, two-EXE topology, bounded workers, adaptive 2048-context reserve, Windows lane-lock mapping, duplicate-column/Core-startup/storage-bootstrap guards, WAL exact-type fail-closed semantics, durable HANDLE-bound rename and reparse/path-safety invariants.
