# Agent Error Log — Windows settings code execution

- Timestamp: 2026-08-23T00:07:38+02:00
- pATHENA branch: `agent/pathena`
- pATHENA HEAD at discovery: `52716e63230029adc9185df3e481c477c256b71f`
- Fix commits: `e293f816c0a5de01a42d8710711ecf0179be21cf`, `baa66c7cc4a0c92fa179cae387d8d02dc2a1ebcf`
- Status: FIXED
- Classification: SECURITY / LOCAL-STARTUP RELIABILITY
- Components: `scripts/windows_common.ps1`, Windows bootstrap/start/check path

## Reproduction / check

Static inspection of the discovery revision:

```powershell
Select-String -Path .\scripts\windows_common.ps1 -SimpleMatch '. $settingsPath'
```

Observed relevant source excerpt at discovery:

```powershell
. $settingsPath
```

`Import-PathenaWindowsSettings` dot-sourced `.pathena.windows.ps1`. Therefore a local settings file was executed as arbitrary PowerShell during normal bootstrap/start/check rather than being treated as data.

## Impact

A malformed or modified local settings file could execute commands in the user's PowerShell context. Even without malicious modification, arbitrary syntax in the file could break local startup before pATHENA diagnostics ran. The file is git-ignored, so its contents are not reviewable through repository history.

## Root cause

The settings persistence helper wrote PowerShell assignment syntax and the import helper restored settings by dot-sourcing the whole file. The implementation conflated configuration data with executable code.

## Fix

The existing `.pathena.windows.ps1` filename and generated assignment syntax were retained for backward compatibility, but the importer no longer executes the file. It now:

- reads the file as text,
- permits comments and blank lines,
- allowlists only `ATHENA_LOCAL_ROOT` and `ATHENA_LMSTUDIO_BASE_URL`,
- requires single-quoted data literals,
- decodes doubled single quotes without evaluation,
- rejects malformed syntax, unsupported settings, and duplicate settings,
- writes validated values to the process environment only after parsing.

A static regression test in `tests/unit/test_windows_settings_script_safety.py` prevents reintroduction of direct settings-file execution and checks the allowlist/parser guard.

## Verification evidence

- Static defect reproduction at discovery: PASS.
- Updated remote source inspection: PASS — direct `. $settingsPath` execution is absent and the strict parser/allowlist is present.
- Regression test committed and remote content inspected: PASS.
- Python test-suite execution from this connector environment: NOT EXECUTABLE.
- Native Windows PowerShell runtime execution from this connector environment: NOT EXECUTABLE.

No runtime PASS is claimed without observed execution evidence.

## Next action

Continue auditing the Windows-local startup path. Prioritize failures that can prevent bootstrap, diagnostics, database startup, API startup, desktop launch, or provider configuration. Record every new defect in `docs/agent_logs/` before or alongside its fix.
