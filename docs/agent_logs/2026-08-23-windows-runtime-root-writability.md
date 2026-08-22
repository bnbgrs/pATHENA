# Windows runtime root writability fence

- Timestamp: 2026-08-23T01:10:00+02:00
- pATHENA HEAD observed before fix: `3d8c14537b36008e567901434e890b977acdb494`
- Affected components: `scripts/windows_common.ps1`, `scripts/bootstrap_windows.ps1`, `scripts/check_windows.ps1`, `scripts/start_windows.ps1`, `tests/unit/test_windows_runtime_root_contract.py`
- Reproduction/check: configure `ATHENA_LOCAL_ROOT` or `-LocalRoot` to a path that cannot be created or written, then start bootstrap/check/desktop.
- Relevant error excerpt: prior to this fix there was no early Windows-script error; failure would occur later during SQLite/database/runtime initialization.
- Root-cause classification: local bootstrap/preflight gap
- Status: FIXED_PENDING_CI
- Fix/mitigation: added canonical effective-root resolution plus `Assert-PathenaLocalRootReady`, which creates the directory, writes and removes a unique probe, and raises an actionable error. Bootstrap, readiness check, and desktop launcher now all invoke the fence before their runtime work.
- Verification evidence: repository inspection confirms all three Windows entrypoints call `Assert-PathenaLocalRootReady`; `tests/unit/test_windows_runtime_root_contract.py` statically enforces that contract at HEAD `0b6aea2b8660e7b3b65ca428cf052671ef40d91c`. PowerShell execution is NOT EXECUTABLE in the current non-Windows runtime; no local Windows PASS is claimed.
- Next action: observe CI for the static Python contract, then execute `scripts/bootstrap_windows.ps1`, `scripts/check_windows.ps1 -RequireModel`, and `scripts/start_windows.ps1` on the user's Windows machine.
