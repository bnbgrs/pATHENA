# pATHENA on Windows

This document describes the supported local-development/runtime path for pATHENA on Windows.

## 1. Bootstrap

Open PowerShell in the pATHENA repository and run:

```powershell
.\scripts\bootstrap_windows.ps1
```

The bootstrap repairs the required `uv 0.11.21` version when `uv` is missing or a different version is active, installs Python 3.12 through `uv`, resolves the effective local runtime root, verifies that the root is outside the Git repository, creates it when needed, proves that it is writable with a temporary write probe, synchronizes the locked desktop environment, validates the installed package/configuration, runs the local doctor, and runs the model-free Core/API restart smoke test.

A custom operational root can be selected explicitly:

```powershell
.\scripts\bootstrap_windows.ps1 -LocalRoot "D:\pATHENA-data"
```

A non-default local LM Studio endpoint can be selected at the same time:

```powershell
.\scripts\bootstrap_windows.ps1 `
    -LocalRoot "D:\pATHENA-data" `
    -LmStudioBaseUrl "http://127.0.0.1:1234"
```

Explicit bootstrap settings are validated and then saved in the repository-local, git-ignored `.pathena.windows.ps1`. Subsequent Windows launches reuse them automatically. This does not modify global Windows environment variables. Use `-NoPersistSettings` for a one-off bootstrap override.

The repository itself is not the personal knowledge store. pATHENA now rejects a runtime root that is the repository itself or a directory below it. Use `%LOCALAPPDATA%\ATHENA`, `D:\pATHENA-data`, or another directory outside the checkout.

## 2. Runtime locations

Without overrides pATHENA uses:

```text
%LOCALAPPDATA%\ATHENA
```

The bootstrap, readiness check, and desktop launcher all use the same resolver for this default. If `ATHENA_LOCAL_ROOT` is set, that absolute path becomes the effective root instead. Before Core/database work begins, the Windows scripts verify that the root is outside the repository, create it if necessary, and verify that a temporary file can be written and removed there.

If the path is inside the repository, startup stops before runtime data is created with an error beginning with:

```text
pATHENA runtime root must be outside the repository:
```

If the write probe fails, pATHENA stops early with an error beginning with:

```text
pATHENA runtime root is not writable:
```

Choose a separate writable root, for example:

```powershell
.\scripts\bootstrap_windows.ps1 -LocalRoot "D:\pATHENA-data"
```

Important subpaths are derived from that root:

```text
state\athena.db     canonical SQLite state
state\spool\        durable pending bytes
derived\            reconstructible indexes/caches
logs\               local logs
tmp\                temporary runtime files
```

Archive, backup and projection data use their configured roots when present. The doctor now probes configured optional roots for actual write access instead of treating an existing directory as sufficient.

The primary environment variables are:

```text
ATHENA_LOCAL_ROOT
ATHENA_ARCHIVE_ROOT
ATHENA_BACKUP_ROOT
ATHENA_PROJECTION_ROOT
ATHENA_LMSTUDIO_BASE_URL
ATHENA_LOG_LEVEL
ATHENA_MODEL_REQUEST_TIMEOUT_SECONDS
ATHENA_MODEL_GENERATION_TIMEOUT_SECONDS
```

Path overrides must be absolute. Archive, backup and projection roots are intentionally not invented automatically.

## 3. One-command local readiness check

After bootstrap, the normal Windows diagnostic is:

```powershell
.\scripts\check_windows.ps1
```

It verifies that the effective runtime root is separated from the source checkout and writable, synchronizes the locked desktop runtime, runs the full pATHENA doctor including Core startup/shutdown, and then proves model-independent Core/API persistence across repeated clean process restarts in a disposable runtime root.

The restart smoke performs two full stop/start verification cycles by default. To stress the restart path more heavily:

```powershell
.\scripts\check_windows.ps1 -RestartCycles 5
```

`-RestartCycles` accepts values from 1 through 10.

When diagnosing a restart, migration, or cleanup failure, preserve the smoke database and runtime files in a dedicated test directory:

```powershell
.\scripts\check_windows.ps1 `
    -SmokeRoot "D:\pATHENA-smoke" `
    -RestartCycles 3
```

`-SmokeRoot` is test data. It must not be the configured live pATHENA runtime root; `athena-local-smoke` rejects that combination before creating a test chat.

To require a loaded LM Studio LLM as part of the check:

```powershell
.\scripts\check_windows.ps1 -RequireModel
```

For a previously synchronized environment:

```powershell
.\scripts\check_windows.ps1 -NoSync
```

The lower-level doctor remains available directly:

```powershell
uv run --locked --extra desktop athena-doctor
```

The doctor checks:

- Python 3.12
- resolved local runtime root
- local write access
- free disk space
- configured archive/backup/projection availability and write access
- read-only SQLite preflight and `quick_check` integrity
- real Core startup and orderly shutdown
- LM Studio connectivity/model discovery

LM Studio being offline is reported separately and does not prevent the Core itself from being considered runnable.

## 4. Start the desktop

```powershell
.\scripts\start_windows.ps1
```

The launcher loads `.pathena.windows.ps1` when present, applies any explicit command-line overrides, verifies that the effective runtime root is outside the repository and writable, synchronizes the locked runtime, runs a fast model-independent runtime/database preflight, and only then launches `athena-desktop`.

For a previously synchronized environment:

```powershell
.\scripts\start_windows.ps1 -NoSync
```

For an isolated one-off runtime root:

```powershell
.\scripts\start_windows.ps1 -LocalRoot "D:\pATHENA-data"
```

For a non-default local LM Studio port:

```powershell
.\scripts\start_windows.ps1 -LmStudioBaseUrl "http://127.0.0.1:1234"
```

`start_windows.ps1` command-line overrides apply only to that process; use the bootstrap parameters above when you want them persisted. `-SkipPreflight` exists for diagnostics but should not be the normal startup path.

The desktop owns one dedicated Core child process. The Core binds only to loopback and uses runtime discovery so the desktop does not rely on a fixed API port.

## 5. LM Studio

pATHENA defaults to:

```text
http://127.0.0.1:1234
```

Only loopback LM Studio endpoints are accepted by the current v1 configuration.

Check provider health:

```powershell
uv run --locked --extra desktop athena model status
```

List models visible through LM Studio:

```powershell
uv run --locked --extra desktop athena model list
```

A model must be loaded before generation can succeed. If multiple compatible LLMs are loaded, callers may need to select the exact model ID.

## 6. Core-only smoke tests

Show the effective runtime paths and start/stop the Core once:

```powershell
uv run --locked --extra desktop athena --show-paths
```

Create a persistent chat without invoking a model:

```powershell
uv run --locked --extra desktop athena chat new
```

Model-independent persistence should work even while LM Studio is offline.

The disposable restart test can also be run directly:

```powershell
uv run --locked --extra desktop athena-local-smoke
```

It creates a chat through the loopback Core API, shuts the Core down, verifies that the API discovery/token files were removed, starts fresh Core instances against the same disposable database, and verifies after every restart that the same durable chat is recoverable. After the final shutdown it opens the database through the read-only startup preflight and requires the current pATHENA schema version.

Run more restart cycles directly:

```powershell
uv run --locked --extra desktop athena-local-smoke --restart-cycles 5
```

Retain a dedicated test root for inspection:

```powershell
uv run --locked --extra desktop athena-local-smoke `
    --keep-root "D:\pATHENA-smoke" `
    --restart-cycles 3
```

The configured live pATHENA root is deliberately rejected as `--keep-root`; the smoke test creates durable test data and must remain isolated from personal data.

## 7. Recovery behavior

pATHENA performs a read-only SQLite inspection before normal writer startup. If the database, WAL/SHM state, application ID, schema version or quick integrity check is unsafe, normal startup fails closed instead of silently replacing state.

Run the Windows check first when startup fails:

```powershell
.\scripts\check_windows.ps1
```

For a reproducible database/restart failure, rerun with a persistent test root rather than deleting files:

```powershell
.\scripts\check_windows.ps1 `
    -SmokeRoot "D:\pATHENA-smoke" `
    -RestartCycles 3
```

Do not delete `athena.db`, `athena.db-wal` or `athena.db-shm` merely to make startup succeed. Those files can contain durable operational state.

The recovery CLI is available as:

```powershell
uv run --locked --extra desktop athena-recover --help
```

## 8. Development checks

Targeted Windows-contract test:

```powershell
uv run --locked --extra dev --extra desktop pytest tests/unit/test_windows_runtime_root_contract.py -q
```

Targeted local-smoke tests:

```powershell
uv run --locked --extra dev --extra desktop pytest `
    tests/unit/test_local_smoke_safety.py `
    tests/integration/test_local_smoke.py -q
```

Targeted doctor storage-root tests:

```powershell
uv run --locked --extra dev --extra desktop pytest tests/unit/test_doctor_storage_roots.py -q
```

Full repository quality command:

```powershell
uv run --locked --extra dev --extra desktop python scripts/quality.py
```

A failing GitHub Actions run is useful engineering evidence, but local Windows runtime correctness is also validated through the bootstrap, repository/runtime separation fence, root-writability fence, doctor, repeated restart test and actual desktop/Core startup path.
