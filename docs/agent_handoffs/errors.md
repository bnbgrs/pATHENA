# pATHENA Error Handoff

## Baseline

- Develop source of truth: `develop/pathena-next@f29abc4341895f8ecd28ebeb0baa2e80b030fdf7`.
- Error worker entered this run at `postmerge/errors@b07d493c5352b497b5ab873f6d2936665a29ce29`.
- Current workers: Spec/Core `b8df82b23583d42a8d5ae8f387aea0fbd0e7859e`; Backend `c8ee2b0b0152a646a63ad4116526a8ce1fdabf90`; UI `af50dfb76b04e396a2dbf65ec1eeb265f30177fa`.
- Exact current Develop canonical Quality: `34510755656@f29abc4341895f8ecd28ebeb0baa2e80b030fdf7 = SUCCESS`.
- Previous Develop canonical Quality: `34504620300@e316843d1f45fc2fd3733d4ae10ec0ad1ac90f58 = SUCCESS`.
- Current Develop differs from the previous exact-green SHA by one CI/Integrator-only commit; no Backend/Storage product source changed.
- `postmerge/errors@b07d493c5352b497b5ab873f6d2936665a29ce29` had zero canonical Quality runs before mutation, and the first ledger commit of this run also triggered no canonical run before this handoff update.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- OPEN: `ERR-0033`.
- IN_PROGRESS: none.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`, `ERR-0031`, `ERR-0032`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`.
- BLOCKED: none.

## Hard progress this run — ERR-0033 canonical baseline closure

### ERR-0033 — Windows emergency-reserve directory-identity binding gap

Status: `OPEN`, P1. Specialist owner: Backend / BE-046.

The previously running exact Develop Quality has now completed: `34510755656@f29abc4341895f8ecd28ebeb0baa2e80b030fdf7 = SUCCESS`. This closes uncertainty about broader integration health on the exact current Develop SHA. It does not close ERR-0033, because no existing canonical lane adversarially swaps the reserve directory across the non-POSIX create/release mutation boundary.

Fresh direct source verification on the same exact SHA confirms `src/athena/storage/emergency_reserve.py` still binds POSIX reserve creation to an opened reserve-directory FD and performs filename-relative mutation through `dir_fd=root_fd`, while the non-POSIX branch still opens `self.path`, validates file identity against a later pathname stat, and retains pathname-driven cleanup/release behavior. Thus the directory identity itself is not carried as a bound Windows handle through the mutation.

The current Develop commit is CI/Integrator-only relative to the previous canonical-green `e316843d1f45fc2fd3733d4ae10ec0ad1ac90f58`; no relevant Backend/Storage product source changed. Backend head `c8ee2b0b0152a646a63ad4116526a8ce1fdabf90` still owns BE-046 and supplies no bounded candidate, so Errors did not parallel-mutate product code.

Preserve physical non-sparse allocation, exact release accounting and fail-closed Storage/Recovery behavior. Do not replace the invariant with pathname-only checks, broad exception suppression, Skip/XFail or assertion weakening.

## Integrator handoff

- Current Develop: `f29abc4341895f8ecd28ebeb0baa2e80b030fdf7`.
- Exact canonical Quality: `34510755656@f29abc4341895f8ecd28ebeb0baa2e80b030fdf7 = SUCCESS`.
- `ERR-0033 = OPEN / P1`; specialist mapping Backend `BE-046`, current Backend head `c8ee2b0b0152a646a63ad4116526a8ce1fdabf90`.
- Exact-current source evidence: POSIX reserve mutation/release is directory-FD-bound; non-POSIX remains pathname-driven and does not carry reserve-directory identity through create/release mutation.
- Product mutation by Errors: none; ownership remains with Backend and no focused candidate exists yet.
- Closure prerequisite: one bounded Backend Windows identity-binding candidate plus focused native-Windows regression proving an adversarial reserve-directory swap cannot redirect create/release, while preserving allocation, accounting and durability semantics. Only then move to `FIXED_PENDING_VERIFY` or `FIXED` with exact-SHA evidence.
- Preserve pypdf packaging, Frozen argv, two-EXE topology, bounded workers, adaptive 2048-context reserve, Windows lane-lock mapping, duplicate-column/Core-startup/storage-bootstrap guards and WAL exact-type fail-closed semantics.
