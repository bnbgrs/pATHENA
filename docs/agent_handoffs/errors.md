# pATHENA Error Handoff

## Baseline

- Develop source of truth: `develop/pathena-next@fec368f50307a9e24038baca3a80b10ee2a3c4fc`.
- Error worker entered this run at `postmerge/errors@d079c0d49392a58846b488a405d923ac82e5b1d7`.
- Current workers: Spec/Core `e9a6a1d28281e78c9b8ee0548582ed4a39d424b4`; Backend `195814616f394e1794aa4f3b2a16a584c092ab31`; UI `58fac1d71d4e89cdb9d008e410b0d4da5ea2ebdf`.
- Exact-current Develop canonical Quality: `34618898303@fec368f50307a9e24038baca3a80b10ee2a3c4fc = SUCCESS`.
- Exact-current Spec/Core canonical Quality: `34621318923@e9a6a1d28281e78c9b8ee0548582ed4a39d424b4 = SUCCESS`.
- Exact-current Spec/Core focused candidate: `34621318964@e9a6a1d28281e78c9b8ee0548582ed4a39d424b4 = SUCCESS`.
- Exact-current UI canonical Quality: `34629561706@58fac1d71d4e89cdb9d008e410b0d4da5ea2ebdf = IN_PROGRESS`; do not infer UI PASS/FAIL while it is running.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- OPEN: `ERR-0033`, `ERR-0035`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`, `ERR-0031`, `ERR-0032`, `ERR-0034`, `ERR-0036`, `ERR-0037`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`, `ERR-0038`.
- BLOCKED: none.

## Hard progress this run — ERR-0033 open-handle physical-reclamation gap

### ERR-0033 — Emergency-reserve filesystem-object identity/capacity gap

Status: `OPEN / P1 / Backend BE-046 owned`.

The current exact Develop source (`fec368f50307a9e24038baca3a80b10ee2a3c4fc`) exposes an additional Recovery failure mode within the existing BE-046 root cause. In the POSIX `EmergencyReserveStore.release()` path, pATHENA opens and attests the reserve object with `fstat`, captures its size, then closes its own reserve-file descriptor before issuing `os.unlink(..., dir_fd=root_fd)`. It subsequently reports the previously captured size as released bytes.

That sequence does not prove physical reclamation. A second descriptor that was already open on the same inode can survive unlink and keep the inode/data blocks referenced after the canonical pathname has disappeared. No pathname substitution, parent swap, hardlink, or inode change is required. A writable second descriptor can additionally mutate or truncate that same inode after pATHENA's attestation, so the returned pre-unlink size can be stale even while object identity remains stable.

This is therefore not a new error ID. It extends `ERR-0033 / BE-046` from pathname/object-identity continuity to open-handle ownership and physical-reclamation continuity. Directory-handle binding, same-inode validation, and a single-hardlink invariant are individually insufficient to close it.

Backend currently owns BE-046 and has not supplied a newer bounded exact-tested candidate, so Errors made no competing Storage product mutation. Closure now also requires a focused adversarial second-descriptor regression: pre-open the reserve inode independently, drive release through attestation/unlink, and prove pATHENA cannot report recoverable emergency bytes without a bounded guarantee that those blocks are actually reclaimable. Preserve all fail-closed Storage/Recovery semantics and non-sparse allocation guarantees.

### ERR-0035 — SQLite preflight identity through live writer startup

Status remains `OPEN / P1 / Backend BE-052 owned`. No newer bounded exact-tested BE-052 candidate was observed. Errors made no competing Database/Storage product mutation.

### ERR-0038 — historical Spec/Core Ruff failure

Status remains `STALE`. Current Spec/Core `e9a6a1d28281e78c9b8ee0548582ed4a39d424b4` remains exact-green from the previously consumed canonical/focused evidence; no current exact SHA reproduced the old `I001` defect.

## CI discipline

- `postmerge/errors@d079c0d49392a58846b488a405d923ac82e5b1d7` had zero workflow runs before the ledger mutation.
- The resulting ledger commit `234ab802a870fcecf2e7b6354817b40839ddcc91` also had zero workflow runs before this handoff mutation.
- Errors started no canonical Quality run and did not mutate a branch with an active exact-head canonical run.

## Integrator handoff

- Develop: `fec368f50307a9e24038baca3a80b10ee2a3c4fc`; canonical `34618898303 = SUCCESS`.
- UI `58fac1d71d4e89cdb9d008e410b0d4da5ea2ebdf`: canonical `34629561706 = IN_PROGRESS`; consume it before deriving UI integration status.
- `ERR-0033 = OPEN / P1`, Backend BE-046 owned. New exact-current evidence: POSIX release can unlink the canonical reserve pathname yet still overstate immediately reclaimed emergency capacity because another already-open descriptor can pin or mutate the same inode. Closure requires second-descriptor physical-reclamation evidence in addition to the previously documented identity, hardlink and allocation-attestation cases.
- `ERR-0035 = OPEN / P1`, Backend BE-052 owned; unchanged this run.
- `ERR-0038 = STALE`; do not reopen without a current exact-SHA reproduction.
- No closed/stale cluster was reopened without current exact-SHA evidence.
- Preserve pypdf packaging, Frozen argv, two-EXE topology, bounded workers, adaptive 2048-context reserve, Windows lane-lock mapping, duplicate-column/Core-startup/storage-bootstrap guards and all Storage/Recovery/Security fail-closed invariants.