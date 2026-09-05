# pATHENA Feature Integrator Handoff

## Current branch state

- `main` remains strict read-only at `0d4d621f8a38ddf8eccfa09622bf193687619943`.
- Develop before this run: `415debaae20fd84cd12fa0613dc063dc48dd134f`.
- Integration target: `develop/pathena-next` only.
- Worker heads reviewed: errors `0017b4d83481ba46e020d12492eb5c1d0a5fca7a`; spec-core `eaa43526398c2e5abb6efb2ec2ae58c53178e878`; backend `35a7ca4a31a86aa31cecc2d6140518071f1c7b71`; ui `779b28a0845e80bb16feadca28f5eaba26124db9`.
- `main` and `bnbgrs/ATHENA` were untouched.

## Integrated this run — Disk-pressure threshold consistency

READY Backend lineage independently reviewed:

- product `c0ee910a20fb396b0c20429f2da33873b407c641`;
- focused test `dde63f019c5ecd95d1805ff9c19fdd986fe4b436`;
- exact green descendant `5b04d7e335823f59bd33847e5b5c2c5b7e23458c`;
- canonical ATHENA Quality `33978168395 = success`.

Current Develop already contained the preceding reserve-release state and released-volume guards. The worker delta is bounded to the invariant that `before_release.thresholds` and `after_release.thresholds` must remain identical during one check. Exact current Develop files were inspected and the two-line guard plus focused regression were applied without importing older Backend history.

Integration commits: product `d29f21c7d1fcc99ce59d2e89822900c0b91f0749`, focused regression `e639ed59cc449738c74bf550503282f7f2df9d4b`.

## Contract now covered

- `DiskPressureCheckResult` fails closed when thresholds change during a single release/reassessment cycle;
- volume-size, released-volume, EMERGENCY-only release and zero-release identity guards remain intact;
- no SQLite/WAL, recovery, fsync, transport, Security, audit or provenance semantics changed;
- no Skip/XFail, assertion weakening or guard relaxation was introduced.

## Validation state

- Backend exact descendant Quality `33978168395 = success` verifies the product/test lineage.
- Independent diff review confirmed the worker product change is only the threshold equality guard and the test adds only the focused threshold-change rejection.
- Exact-current-Develop workflow lookup for `e639ed59cc449738c74bf550503282f7f2df9d4b` returned no associated run yet; repository-wide global green is not claimed.

## Other current inputs

- Core Local+Web Research product/test commit `6c5431f35951b7916e1db97138306de41a5da622` has focused pytest 10 passed, Ruff PASS and mypy PASS, but canonical Quality is not green yet; NOT READY.
- Backend assessment-state truth and reserve-provision free-space boundary are READY through exact Backend descendant `94c6e37d2d6b1d1993703dbaef351fffbc734f6d`, Quality `33984348331 = success`.
- Backend reserve-provision EMERGENCY-boundary truth remains APPLIED / CANONICAL_PENDING.
- UI-GAP-0027 remains IMPLEMENTED_PENDING_VERIFY; do not integrate without exact canonical green.
- `ERR-0014` is STALE after repeated exact clean successors on unchanged affected controller/test lineage; reopen only if the exact exit-139 signature recurs.

## Tracker handling

`docs/development/ALPHA_BETA_PROGRESS.md` remains read-only in this run because complete safe retrieval for replacement was not established. No fabricated percentage or unsafe truncated rewrite was made.

## Next integration order

1. Prefer a newer exact-green bounded Core successor if Local+Web obtains canonical green.
2. Otherwise independently integrate exactly one READY Backend assessment-state or reserve-provision free-space slice.
3. Do not integrate Backend reserve-provision EMERGENCY-boundary truth or UI-GAP-0027 without exact green evidence.
4. Reopen `ERR-0014` only on recurrence of the exact Qt/controller SIGSEGV signature.
5. Obtain exact-current-Develop Quality before any repository-wide green claim.

## Rules retained

- No direct work on `main`; no main promotion.
- No force-push, history rewrite or auto-merge.
- No Skip/XFail, weaker assertions, Security/Storage/Windows/Recovery/validator relaxation, fake success or fabricated provenance.
