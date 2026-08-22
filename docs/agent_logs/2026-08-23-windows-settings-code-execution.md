# Agent Error Log — Windows settings code execution

- Timestamp: 2026-08-23T00:07:38+02:00
- pATHENA branch: `agent/pathena`
- pATHENA HEAD at discovery: `52716e63230029adc9185df3e481c477c256b71f`
- Status: OPEN
- Classification: SECURITY / LOCAL-STARTUP RELIABILITY
- Components: `scripts/windows_common.ps1`, Windows bootstrap/start/check path

## Reproduction / check

Static inspection of the current branch:

```powershell
Select-String -Path .\scripts\windows_common.ps1 -SimpleMatch '. $settingsPath'
```

Observed relevant source excerpt:

```powershell
. $settingsPath
```

`Import-PathenaWindowsSettings` dot-sources `.pathena.windows.ps1`. Therefore a local settings file is executed as arbitrary PowerShell during normal bootstrap/start/check rather than being treated as data.

## Impact

A malformed or modified local settings file can execute commands in the user's PowerShell context. Even without malicious modification, arbitrary syntax in the file can break local startup before pATHENA diagnostics run. The file is git-ignored, so its contents are not reviewable through repository history.

## Root cause

The settings persistence helper writes PowerShell assignment syntax and the import helper restores settings by dot-sourcing the whole file. The implementation conflates configuration data with executable code.

## Planned fix

Keep the existing `.pathena.windows.ps1` filename and generated assignment syntax for backward compatibility, but replace dot-sourcing with a strict parser that accepts only these two assignments:

- `ATHENA_LOCAL_ROOT`
- `ATHENA_LMSTUDIO_BASE_URL`

Blank lines and comments remain allowed. Any other non-comment content must fail closed. Add a regression test that prevents reintroduction of settings-file dot-sourcing and verifies the allowlist/parser guard remains present.

## Verification status

- Static defect reproduction: PASS
- Fix verification: NOT EXECUTABLE yet; fix not applied at time of this log entry.
- Windows runtime execution: NOT EXECUTABLE from the GitHub connector environment.

## Next action

Patch `scripts/windows_common.ps1`, add regression coverage, inspect resulting remote files, then update this log to FIXED or BLOCKED with exact evidence.
