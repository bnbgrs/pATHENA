# Agent Error Log — uv version failure path masks intended diagnostic

- Timestamp: 2026-08-23T00:07:38+02:00
- pATHENA branch: `agent/pathena`
- pATHENA HEAD at discovery: `f2b24918d38316187996926715dd771a322e1a5e`
- Fix commits: `e93cab55faf36870278b5f0c540f2352f7b51cd6`, `07e612909eba3a4c3080ac3f1ded4f0f30332be5`, `1d62b7a40ed5998fdd014cd6010982e83f0ce6b0`, `eedabbbe389c7b4fc809282ec73d583254f9c2a0`, `4ec9412b84594822618af9ec6f62d469ba3144cb`
- Status: FIXED
- Classification: WINDOWS LOCAL-STARTUP RELIABILITY
- Components: `scripts/bootstrap_windows.ps1`, `scripts/start_windows.ps1`, `scripts/check_windows.ps1`, `scripts/windows_common.ps1`

## Reproduction / check

Static inspection at discovery showed version probing in the Windows path calling `.Trim()` directly on native-command output before checking the native exit code, for example:

```powershell
$uvVersion = (& uv --version).Trim()
if ($LASTEXITCODE -ne 0 -or $uvVersion -ne "uv 0.11.21") {
```

The bootstrap had the same ordering inside its local uv version resolver.

## Failure mode

If `uv` resolved through `Get-Command` but the executable failed, crashed, was blocked, or produced no stdout, the command expression could yield `$null`. Calling `.Trim()` then raised a PowerShell method/null error before the intended `$LASTEXITCODE` handling ran. The user received an incidental PowerShell failure instead of pATHENA's actionable bootstrap diagnostic.

## Root cause

Native-process output was dereferenced before exit status and output presence were validated. The same probe logic was duplicated across bootstrap/start/check.

## Fix

`windows_common.ps1` now owns `Get-PathenaUvVersion`. The helper:

- returns `$null` when `uv` is absent,
- catches native invocation failures,
- captures stdout before dereferencing it,
- snapshots `$LASTEXITCODE`,
- returns `$null` for non-zero exit or empty output,
- safely joins and trims output only after those checks.

`bootstrap_windows.ps1`, `start_windows.ps1`, and `check_windows.ps1` now use the shared helper. The bootstrap's duplicate resolver was removed.

`tests/unit/test_windows_uv_probe_safety.py` statically enforces the shared helper and prevents reintroduction of `(& uv --version).Trim()` in Windows entry points.

## Verification evidence

- Static defect reproduction at discovery: PASS.
- Shared helper committed: PASS.
- Bootstrap migrated to shared helper: PASS.
- Desktop launcher migrated to shared helper: PASS.
- Diagnostic script migrated to shared helper: PASS.
- Regression test committed: PASS.
- Native Windows PowerShell execution from this connector environment: NOT EXECUTABLE.
- Full Python test suite from this connector environment: NOT EXECUTABLE.

No runtime PASS is claimed without observed execution evidence.

## Next action

Continue the Windows-local startup audit. Prioritize bootstrap installation, locked-environment synchronization, diagnostics, runtime-root handling, API/core startup, desktop launch, and provider/model configuration. Record each newly found defect in `docs/agent_logs/`.
