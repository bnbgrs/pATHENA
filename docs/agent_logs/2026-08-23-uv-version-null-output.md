# Agent Error Log — uv version failure path masks intended diagnostic

- Timestamp: 2026-08-23T00:07:38+02:00
- pATHENA branch: `agent/pathena`
- pATHENA HEAD at discovery: `f2b24918d38316187996926715dd771a322e1a5e`
- Status: OPEN
- Classification: WINDOWS LOCAL-STARTUP RELIABILITY
- Components: `scripts/bootstrap_windows.ps1`, `scripts/start_windows.ps1`, `scripts/check_windows.ps1`, `scripts/windows_common.ps1`

## Reproduction / check

Static inspection shows version probing in the Windows path calling `.Trim()` directly on native-command output before checking the native exit code, for example:

```powershell
$uvVersion = (& uv --version).Trim()
if ($LASTEXITCODE -ne 0 -or $uvVersion -ne "uv 0.11.21") {
```

The bootstrap has the same ordering inside its uv version resolver.

## Failure mode

If `uv` resolves through `Get-Command` but the executable fails, crashes, is blocked, or produces no stdout, the command expression can yield `$null`. Calling `.Trim()` then raises a PowerShell method/null error before the intended `$LASTEXITCODE` handling runs. The user receives an incidental PowerShell failure instead of pATHENA's actionable bootstrap diagnostic.

## Root cause

Native-process output is dereferenced before exit status and output presence are validated. The same probe logic is duplicated across bootstrap/start/check.

## Planned fix

Move uv version probing into `windows_common.ps1` as a shared helper that:

- returns `$null` when `uv` is absent,
- captures stdout without dereferencing it first,
- checks `$LASTEXITCODE` before trimming,
- returns `$null` for empty output,
- normalizes multi-line output safely.

Then use that helper from bootstrap, start, and check so all Windows entry points have one failure contract.

## Verification status

- Static defect reproduction: PASS.
- Fix verification: NOT EXECUTABLE yet; fix not applied at time of this log entry.
- Native Windows runtime execution: NOT EXECUTABLE from the GitHub connector environment.

## Next action

Patch the shared helper and all three Windows entry points, add/update regression coverage, inspect remote files, then update this log with exact evidence.
