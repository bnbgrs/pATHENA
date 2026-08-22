# Windows runtime root writability fence

- Timestamp: 2026-08-23T01:10:00+02:00
- pATHENA HEAD observed before fix: `3d8c14537b36008e567901434e890b977acdb494`
- Affected components: `scripts/windows_common.ps1`, Windows bootstrap/check/launcher flow
- Reproduction/check: configure `ATHENA_LOCAL_ROOT` or `-LocalRoot` to a path that cannot be created or written, then start bootstrap/doctor/desktop.
- Relevant error excerpt: prior to this fix there was no early Windows-script error; failure would occur later during SQLite/database/runtime initialization.
- Root-cause classification: local bootstrap/preflight gap
- Status: FIXED_PENDING_CI
- Fix/mitigation: added `Resolve-PathenaEffectiveLocalRoot` and `Assert-PathenaLocalRootReady`, including directory creation, a unique write probe, cleanup, and an actionable failure message.
- Verification evidence: repository inspection confirms the helper exists at commit `3c77dc3ae35a6764174c5613a642a2e393c5f197`. PowerShell execution is NOT EXECUTABLE in the current non-Windows runtime; no local Windows PASS is claimed.
- Next action: wire the fence into bootstrap, readiness check, and desktop launcher, then run the Windows-local workflow on an actual Windows host.
