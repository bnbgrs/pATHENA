# pATHENA Error Handoff

## Baseline

- Develop source of truth: `develop/pathena-next@f29abc4341895f8ecd28ebeb0baa2e80b030fdf7`.
- Error worker entered this run at `postmerge/errors@86a990c600643a25168013ee18dce62fa35b55e1`.
- Current workers: Spec/Core `b8df82b23583d42a8d5ae8f387aea0fbd0e7859e`; Backend `c8ee2b0b0152a646a63ad4116526a8ce1fdabf90`; UI `af50dfb76b04e396a2dbf65ec1eeb265f30177fa`.
- Previous Develop canonical Quality: `34504620300@e316843d1f45fc2fd3733d4ae10ec0ad1ac90f58 = SUCCESS`.
- Exact current Develop canonical Quality: `34510755656@f29abc4341895f8ecd28ebeb0baa2e80b030fdf7 = IN_PROGRESS` at checkpoint. No competing canonical run was started by Errors.
- Exact compare `e316843d1f45fc2fd3733d4ae10ec0ad1ac90f58...f29abc4341895f8ecd28ebeb0baa2e80b030fdf7` is one commit and changes only `.github/workflows/quality.yml` plus `docs/agent_handoffs/integrator.md`; no Backend/Storage product source changed.
- `postmerge/errors@86a990c600643a25168013ee18dce62fa35b55e1` had zero check runs before this mutation.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- OPEN: `ERR-0033`.
- IN_PROGRESS: none.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`, `ERR-0031`, `ERR-0032`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`.
- BLOCKED: none.

## Hard progress this run — ERR-0033 direct exact-SHA source verification

### ERR-0033 — Windows emergency-reserve directory-identity binding gap

Status: `OPEN`, P1. Specialist owner: Backend / BE-046.

Backend handoff at `postmerge/backend@c8ee2b0b0152a646a63ad4116526a8ce1fdabf90` still marks BE-046 `OPEN / P1 / CURRENTLY REPRODUCED BY SOURCE TRACE` and gives no bounded product candidate. Errors therefore did not parallel-mutate Backend-owned product code.

Fresh direct verification was performed on exact current Develop `f29abc4341895f8ecd28ebeb0baa2e80b030fdf7` in `src/athena/storage/emergency_reserve.py`. POSIX creation opens the reserve directory and performs file creation through `_RESERVE_FILENAME` with `dir_fd=root_fd`; POSIX release likewise opens/unlinks through the same bound directory FD and repeatedly verifies that directory identity remains current. The non-POSIX path instead opens `self.path`, checks the created file identity against a subsequent pathname stat, and cleanup/release later uses `self.path.stat()` / `self.path.unlink()` plus `fsync_directory(self.reserve_root)`. This verifies the exact current SHA still lacks a directory-handle-bound Windows mutation/release path.

The current Develop commit did not touch Backend/Storage source: exact compare from the previous canonical-green Develop `e316843d1...` to `f29abc434...` changes only Quality workflow and Integrator handoff. Thus this is new exact-SHA verification, not repetition of stale source evidence.

Canonical Quality `34510755656@f29abc434...` is still in progress, so no PASS/FIXED claim is made. The prior exact Develop `e316843d1...` is canonical-green, demonstrating that existing canonical coverage does not currently exercise this uncovered directory-identity invariant.

Preserve physical non-sparse reserve allocation, exact release accounting and fail-closed Storage/Recovery behavior. Do not replace the requirement with pathname-only checks, broad exception suppression, `IF NOT EXISTS`, Skip/XFail, or assertion weakening.

## Integrator handoff

- Current Develop: `f29abc4341895f8ecd28ebeb0baa2e80b030fdf7`.
- Current canonical Quality: `34510755656@f29abc4341895f8ecd28ebeb0baa2e80b030fdf7 = IN_PROGRESS` at checkpoint; previous exact Develop `e316843d1...` is canonical `SUCCESS` via `34504620300`.
- `ERR-0033 = OPEN / P1`; maps to Backend `BE-046` on current worker `c8ee2b0b0152a646a63ad4116526a8ce1fdabf90`.
- Fresh exact-current source evidence: `src/athena/storage/emergency_reserve.py@f29abc434...` binds POSIX mutation/release to `root_fd`, while non-POSIX mutation/release remains pathname-driven around `self.path` and does not carry a bound reserve-directory identity through the operation.
- Product mutation by Errors: none; Backend owns BE-046 and currently has no focused candidate.
- Closure prerequisite: Backend provides one bounded Windows identity-binding candidate plus a focused regression that proves reserve directory identity cannot be swapped between validation and create/release, while preserving allocation/accounting/durability semantics. Only then move to `FIXED_PENDING_VERIFY` or `FIXED` with exact-SHA evidence.
- Preserve pypdf packaging, Frozen argv, two-EXE topology, bounded workers, adaptive 2048-context reserve, Windows lane-lock mapping, duplicate-column/Core-startup/storage-bootstrap guards and WAL exact-type fail-closed semantics.
