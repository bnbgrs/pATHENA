# pATHENA on Windows

This document describes the supported local-development/runtime path for pATHENA on Windows.

## 1. Bootstrap

Open PowerShell in the pATHENA repository and run:

```powershell
.\scripts\bootstrap_windows.ps1
```

The script verifies or installs the pinned `uv 0.11.21`, installs Python 3.12 through `uv`, runs the locked dependency sync including the desktop extra, imports the installed package, and starts/stops the real ATHENA Core once as a storage/runtime smoke test.

A custom operational root can be selected explicitly:

```powershell
.\scripts\bootstrap_windows.ps1 -LocalRoot "D:\pATHENA-data"
```

The repository itself is not the personal knowledge store.

## 2. Runtime locations

Without overrides pATHENA uses:

```text
%LOCALAPPDATA%\ATHENA
```

Important subpaths are derived from that root:

```text
state\athena.db     canonical SQLite state
state\spool\        durable pending bytes
archive/derived data depends on configured roots and source state
derived\            reconstructible indexes/caches
logs\               local logs
tmp\                temporary runtime files
```

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

## 3. Diagnose the local installation

Run:

```powershell
uv run --locked --extra desktop athena-doctor
```

The doctor checks:

- Python 3.12
- resolved local runtime root
- local write access
- free disk space
- read-only SQLite preflight/integrity
- real Core startup and orderly shutdown
- LM Studio connectivity/model discovery

LM Studio being offline is reported separately and does not prevent the Core itself from being considered runnable.

To require a working model backend as part of the check:

```powershell
uv run --locked --extra desktop athena-doctor --require-model
```

## 4. Start the desktop

```powershell
.\scripts\start_windows.ps1
```

The launcher synchronizes the locked runtime first and then launches `athena-desktop`.

For a previously synchronized environment:

```powershell
.\scripts\start_windows.ps1 -NoSync
```

For an isolated runtime root:

```powershell
.\scripts\start_windows.ps1 -LocalRoot "D:\pATHENA-data"
```

For a non-default local LM Studio port:

```powershell
.\scripts\start_windows.ps1 -LmStudioBaseUrl "http://127.0.0.1:1234"
```

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

## 7. Recovery behavior

pATHENA performs a read-only SQLite inspection before normal writer startup. If the database, WAL/SHM state, application ID, schema version or quick integrity check is unsafe, normal startup fails closed instead of silently replacing state.

Run the doctor first when startup fails:

```powershell
uv run --locked --extra desktop athena-doctor
```

Do not delete `athena.db`, `athena.db-wal` or `athena.db-shm` merely to make startup succeed. Those files can contain durable operational state.

The recovery CLI is available as:

```powershell
uv run --locked --extra desktop athena-recover --help
```

## 8. Development checks

Targeted tests:

```powershell
uv run --locked --extra dev --extra desktop pytest tests/unit/test_pathena_doctor.py -q
```

Full repository quality command:

```powershell
uv run --locked --extra dev --extra desktop python scripts/quality.py
```

A failing GitHub Actions run is useful engineering evidence, but local Windows runtime correctness is also validated through the bootstrap, doctor, targeted tests and actual desktop/Core startup path.
