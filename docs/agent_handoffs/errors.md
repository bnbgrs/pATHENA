# pATHENA Error Handoff

## Baseline

- Develop source of truth: `develop/pathena-next@5db4c92f40d5d14119a991796be38fb9248072de`.
- Error worker entered this run at `postmerge/errors@06069895fc703b1258b2d2cfe54fab96bc0a2769`.
- Current workers: Spec/Core `d47634453d63cad0b21fb6d370c95602b0d0a286`; Backend `32485db642d71ec2caef8b49adc35ac2132aa651`; UI `e5801b57ca2c4bc62929382427ded0d0e51d55fd`.
- Exact-current Develop canonical Quality: `34659583545@5db4c92f40d5d14119a991796be38fb9248072de = IN_PROGRESS`; do not infer PASS/FAIL while it is running.
- Previous Develop canonical Quality: `34656021355@c0f523921a460137aef7b59d9d703a3f8ce94225 = SUCCESS`.
- Exact-current Spec/Core canonical Quality: `34653170296@d47634453d63cad0b21fb6d370c95602b0d0a286 = SUCCESS`.
- Exact-current Spec/Core focused Candidate: `34653170251@d47634453d63cad0b21fb6d370c95602b0d0a286 = SUCCESS`.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- OPEN: `ERR-0033`, `ERR-0035`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- STALE includes historical `ERR-0038` and `ERR-0039`.
- BLOCKED: none.

## Hard progress this run — ERR-0033 freshly reproduced on current exact Develop

### ERR-0033 — Emergency-reserve physical-reclamation/accounting continuity

Status: `OPEN / P1 / Backend BE-046 owned`.

The previous Backend handoff correctly treats BE-046 as a historical design concern unless current-lineage evidence reopens it. This run supplied that evidence on exact current Develop `5db4c92f40d5d14119a991796be38fb9248072de`.

Current source `src/athena/storage/emergency_reserve.py` still implements POSIX `EmergencyReserveStore.release()` as follows: open/attest the reserve, obtain `file_stat = os.fstat(descriptor)`, capture `size = file_stat.st_size`, close pATHENA's reserve descriptor, revalidate only the reserve directory, unlink `emergency.reserve`, fsync/revalidate the directory, and return the captured logical size. The source blob on current Develop is `bf06e386ba54492ee67bf6fda6d4645f75a48297`, confirming the sequence survived the latest Develop advance unchanged.

That exact-current sequence does not prove that the returned bytes were physically reclaimed. A second descriptor already opened by another process can remain attached to the unlinked inode and continue to retain its blocks. Likewise, another link to the inode defeats the inference that pathname removal equals capacity recovery. pATHENA can therefore report the entire logical reserve size as released even though the underlying storage can still be referenced.

This is a current exact-SHA reproduction of the existing BE-046 root-cause family, not a new error ID. `ERR-0033` remains `OPEN` based on fresh current evidence rather than historical priority.

Required owner closure: a bounded Backend candidate plus focused adversarial coverage where a foreign descriptor is opened before release and remains open through unlink, together with alternate-link ownership coverage. The result must prove that release accounting never confirms bytes that remain referenced; if portable immediate-reclamation proof is unavailable, accounting must remain conservative/fail-closed. Preserve physical non-sparse reserve allocation, directory/target identity guards, Storage/Recovery semantics and all existing guards.

No Backend product code was changed on `postmerge/errors` because Backend owns BE-046.

### ERR-0035 — SQLite preflight-to-writer whole-file-set continuity

Status remains carried as `OPEN / P1 / Backend BE-052 owned`, but this cluster was deliberately not revalidated or advanced in this run. It must not outrank a freshly reproduced current-exact failure merely because of historical evidence.

### ERR-0039 — historical Spec/Core Ruff blocker

Status remains `STALE`. Current Spec/Core exact head is green and the old failing path is absent; do not reopen without a new exact-SHA reproduction.

### ERR-0038 — historical revision-diff Ruff failure

Status remains `STALE`. Do not reopen without its own current exact-SHA reproduction.

## CI discipline

- `postmerge/errors@06069895fc703b1258b2d2cfe54fab96bc0a2769` had zero workflow runs before the first ledger mutation.
- Intermediate Error-worker commits were checked before each subsequent documentation mutation and had zero workflow runs.
- Errors started no canonical Quality run and did not commit onto a branch with a queued/in-progress Error-worker run.
- Current Develop canonical `34659583545@5db4c92f40d5d14119a991796be38fb9248072de` is in progress and was left untouched.

## Integrator handoff

- Develop: `5db4c92f40d5d14119a991796be38fb9248072de`; canonical `34659583545 = IN_PROGRESS`. Consume before deriving integration status.
- Previous Develop: `c0f523921a460137aef7b59d9d703a3f8ce94225`; canonical `34656021355 = SUCCESS`.
- Spec/Core: `d47634453d63cad0b21fb6d370c95602b0d0a286`; canonical `34653170296 = SUCCESS`, focused `34653170251 = SUCCESS`.
- Backend: `32485db642d71ec2caef8b49adc35ac2132aa651`.
- UI: `e5801b57ca2c4bc62929382427ded0d0e51d55fd`.
- `ERR-0033 = OPEN / P1`: freshly reproduced on exact current Develop by the POSIX release sequence described above; Backend BE-046 owns remediation.
- `ERR-0035 = OPEN / P1` remains carried but was not current-exact revalidated this run.
- `ERR-0039 = STALE`.
- `ERR-0038 = STALE`.
- Preserve pypdf packaging, Frozen argv, two-EXE topology, bounded workers, adaptive 2048-context reserve, Windows lane-lock mapping, duplicate-column/Core-startup/storage-bootstrap guards and all Storage/Recovery/Security fail-closed invariants.
