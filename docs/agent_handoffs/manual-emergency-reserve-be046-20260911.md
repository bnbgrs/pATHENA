# Manual BE-046 / ERR-0033 EmergencyReserve handoff — 2026-09-11

## Lineage

Base: `develop/pathena-next@0298f0c4f2d28e516a458390f8b462131ebaf17e`
Branch: `manual/emergency-reserve-be046-20260911`

This is an isolated repair candidate. It does not mutate `postmerge/backend` or any other worker branch.

## Root cause addressed

The old release path attested the reserve through an open descriptor, closed that descriptor, then unlinked by pathname. That lost object identity between attestation and deletion. A same-parent replacement could therefore redirect unlink, a pre-opened second descriptor could keep the old inode's blocks allocated after unlink, hardlinks could defeat exclusive capacity ownership, and platforms without allocation metadata could be accepted without physical-capacity proof.

## Candidate model

The reserve file now has two safe states:

- **provisioned**: exact required logical size, physically allocated, exactly one hard link;
- **released stub**: the same owned pathname/inode at logical size 0 and zero data-block allocation.

Release no longer uses pathname unlink as the capacity primitive. It keeps the attested descriptor open, validates path-to-descriptor identity and single-link ownership, then `ftruncate`s that descriptor to zero and fsyncs it. This physically releases blocks even when another descriptor was opened before release. Keeping the empty stub avoids an unlink-by-name substitution window. A later `ensure()` safely reprovisions the zero stub.

## Identity rules

- POSIX root stays bound to a directory descriptor.
- POSIX reserve operations bind pathname and file descriptor with `samestat` before/after mutation.
- POSIX reserve descriptor is flocked during ensure/release to serialize cooperating pATHENA processes.
- Every accepted provisioned reserve requires `st_nlink == 1`.
- Hardlink insertion during release is detected after truncation; capacity is already reclaimed and no successful byte-release claim is returned.
- Non-POSIX paths keep an open descriptor across identity checks and physical allocation queries.
- Unknown physical allocation now fails closed in store inspection/provisioning instead of silently accepting logical length only.
- On Windows, `GetCompressedFileSizeW` supplies observable allocated-byte count when POSIX `st_blocks` is unavailable.

## Adversarial coverage

`tests/unit/test_emergency_reserve.py` now covers:

- capacity release while a second descriptor was opened before release;
- hardlink ownership rejection;
- hardlink insertion between release attestation and truncation;
- same-parent target substitution during release without touching replacement content;
- parent-directory substitution during release without touching the replacement root file;
- parent substitution during creation without allocating into the new root;
- unknown allocation metadata fail-closed behavior;
- failed allocation returning to a zero-capacity stub;
- reprovisioning the released zero stub.

## Semantic change

`release()` intentionally retains a zero-length owned `emergency.reserve` stub instead of deleting the pathname. The externally relevant contract remains released physical capacity plus returned logical reserve bytes. This change is deliberate because unlink-by-name cannot safely preserve the attested file identity across an adversarial same-parent replacement race, while descriptor truncation can reclaim the actual capacity safely.

## Bot rules

1. Do not parallel-implement BE-046 on `postmerge/backend` without first comparing this candidate.
2. Do not restore unlink-by-name as the primary release mechanism unless an atomic identity-bound deletion primitive is proven for every supported platform.
3. Do not accept `allocated_bytes=None`; unknown physical allocation is a fail-closed condition for a real reserve.
4. Do not remove single-link ownership checks from provisioned reserve acceptance.
5. Preserve non-sparse allocation, state-root and reserve-root link/reparse guards, durable fsync behavior and DiskPressure emergency semantics.
6. Exact canonical Quality plus Linux storage and Windows storage evidence are required before `ERR-0033` can be marked FIXED.
7. If Windows allocation attestation fails in CI, fix the Windows allocation query; do not fall back to logical file size.
8. Keep `ERR-0035 / BE-052` separate; it has its own bounded candidate/PR.
