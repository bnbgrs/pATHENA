# pATHENA Error Handoff

## Baseline

- Develop source of truth: `develop/pathena-next@c670d7809c9f0aa5e6c31956b57e897091f1b9d6`.
- Error worker entered this run at `postmerge/errors@6ada3662333696a2373f0b6eb30eff9e5367e373`.
- Current workers: Spec/Core `8019ff39c2352e40513532814760804eaa3c2df4`; Backend `195814616f394e1794aa4f3b2a16a584c092ab31`; UI `4eeb75a6f5909fb1aa194c2c6df2d5ce1b431748`.
- Exact-current Develop canonical Quality: `34639093541@c670d7809c9f0aa5e6c31956b57e897091f1b9d6 = IN_PROGRESS`; do not infer PASS/FAIL while it is running.
- Backend exact-head canonical Quality: `34604847434@195814616f394e1794aa4f3b2a16a584c092ab31 = SUCCESS`, but the SHA contains no BE-046 fix candidate and therefore does not close `ERR-0033`.
- Current Spec/Core and UI heads have no exact-head workflow result yet; evidence from older SHAs is not promoted to them.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- OPEN: `ERR-0033`, `ERR-0035`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`, `ERR-0031`, `ERR-0032`, `ERR-0034`, `ERR-0036`, `ERR-0037`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`, `ERR-0038`.
- BLOCKED: none.

## Hard progress this run — ERR-0033 hardlink insertion after attestation

### ERR-0033 — Emergency-reserve filesystem-object identity/capacity gap

Status: `OPEN / P1 / Backend BE-046 owned`.

On exact-current Develop `c670d7809c9f0aa5e6c31956b57e897091f1b9d6`, the EmergencyReserve storage implementation is unchanged by the intervening UI/Core/docs commits. POSIX `release()` opens the reserve, obtains `file_stat = os.fstat(descriptor)` and captures `size`, closes that reserve descriptor, revalidates only the parent directory, unlinks `_RESERVE_FILENAME` relative to the directory FD, fsyncs the directory and returns the earlier logical size.

This run closes an ambiguity in the previous BE-046 handoff: adding only a single-link admission check such as `st_nlink == 1` would not be a sufficient fix. Such a check is merely a snapshot. After that snapshot and after pATHENA closes its reserve descriptor, another actor can add a hardlink to the already-attested inode before the canonical name is unlinked. pATHENA can then successfully unlink the canonical name while the new hardlink continues to reference the same inode and its blocks; `release()` would nevertheless return the old logical size as if that emergency capacity had been reclaimed.

The existing unit coverage does not exercise this seam. It covers stable release and a POSIX parent-directory replacement at unlink time, but no adversarial hardlink insertion after file attestation and before unlink. Therefore BE-046 closure must prove continuity across the entire attestation-to-accounting interval, not merely add a static `st_nlink` check.

Required focused regression shape: provision a valid non-sparse reserve; intercept the release boundary after `fstat`/attestation but before unlink; create a second hardlink to that same inode; then prove the implementation fails closed or otherwise does not report those bytes as physically reclaimable while the second link still retains the object. This is deduplicated into the existing `ERR-0033 / BE-046` root cause alongside parent/target substitution, unknown allocation metadata and pre-opened descriptor reclamation.

Backend continues to own BE-046 and has not supplied a bounded BE-046 product candidate, so Errors made no competing Storage product mutation.

### ERR-0035 — SQLite preflight identity through live writer startup

Status remains `OPEN / P1 / Backend BE-052 owned`. No newer bounded exact-tested BE-052 candidate was observed. Errors made no competing Database/Storage product mutation.

### ERR-0038 — historical Spec/Core Ruff failure

Status remains `STALE`. No current exact Spec/Core SHA reproduced the historical `I001` defect; do not reopen it from older run IDs.

## CI discipline

- `postmerge/errors@6ada3662333696a2373f0b6eb30eff9e5367e373` had zero workflow runs before the ledger mutation.
- The resulting ledger commit `e63f35e3508afba3cc223c04b9c61031aa1c96fc` also had zero workflow runs before this handoff mutation.
- Errors started no canonical Quality run and did not mutate a branch with an active exact-head canonical run.
- Develop canonical `34639093541@c670d7809c9f0aa5e6c31956b57e897091f1b9d6` remains in progress and was left untouched.

## Integrator handoff

- Develop: `c670d7809c9f0aa5e6c31956b57e897091f1b9d6`; canonical `34639093541 = IN_PROGRESS` at this handoff. Consume it before deriving Develop integration status.
- Backend: `195814616f394e1794aa4f3b2a16a584c092ab31`; canonical `34604847434 = SUCCESS`, but no BE-046 candidate exists on that SHA.
- `ERR-0033 = OPEN / P1`, Backend BE-046 owned. New evidence: a one-time single-link check does not close release accounting because a hardlink can be inserted after attestation and before unlink; closure requires an adversarial attestation-to-unlink hardlink-race test and a bounded physical-reclamation guarantee across that whole interval.
- `ERR-0035 = OPEN / P1`, Backend BE-052 owned; unchanged this run.
- `ERR-0038 = STALE`; do not reopen without current exact-SHA reproduction.
- Preserve pypdf packaging, Frozen argv, two-EXE topology, bounded workers, adaptive 2048-context reserve, Windows lane-lock mapping, duplicate-column/Core-startup/storage-bootstrap guards and all Storage/Recovery/Security fail-closed invariants.