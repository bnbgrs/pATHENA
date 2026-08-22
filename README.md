# pATHENA

**Adaptive Thinking, History, Evidence & Networked Archive**

pATHENA is a local-first, user-controlled personal knowledge assistant and long-term knowledge system.

> The user thinks. ATHENA organizes.

## Windows quick start

Requirements:

- Windows 10/11
- PowerShell 5.1 or newer
- internet access for the first dependency installation
- LM Studio is optional for startup, but required for local model generation

From the repository root:

```powershell
.\scripts\bootstrap_windows.ps1
```

The bootstrap installs/verifies the pinned `uv` version, installs Python 3.12 through `uv`, synchronizes the locked desktop environment and performs a real Core startup/storage smoke test.

Then run the local diagnostics:

```powershell
uv run --locked --extra desktop athena-doctor
```

Start the desktop application:

```powershell
.\scripts\start_windows.ps1
```

By default operational state is stored outside the repository in:

```text
%LOCALAPPDATA%\ATHENA
```

Use a different absolute runtime root for testing or isolated profiles:

```powershell
.\scripts\bootstrap_windows.ps1 -LocalRoot "D:\pATHENA-data"
.\scripts\start_windows.ps1 -LocalRoot "D:\pATHENA-data"
```

See [`docs/WINDOWS_LOCAL.md`](docs/WINDOWS_LOCAL.md) for detailed setup, LM Studio configuration, troubleshooting, runtime paths and recovery guidance.

## LM Studio

The default local endpoint is:

```text
http://127.0.0.1:1234
```

Check connectivity and discovered models with:

```powershell
uv run --locked --extra desktop athena model status
uv run --locked --extra desktop athena model list
```

The desktop and Core can start while LM Studio is offline. Model-backed operations will become available after LM Studio is running and a compatible model is loaded.

## Project status

- Alpha architecture: `docs/alpha/`
- Alpha specification: v2.0.1 final
- Beta specification: v0.1 complete first technical draft
- Technical implementation details belong in `docs/beta/`

## Architecture

Start with [`docs/alpha/INDEX.md`](docs/alpha/INDEX.md). It defines the normative hierarchy and links all 29 Alpha chapters.

The current technical implementation specification is indexed at [`docs/beta/INDEX.md`](docs/beta/INDEX.md) and contains 27 Beta chapters.

## Core principles

- user control over autonomy
- local first
- knowledge and original sources remain portable
- traceability and provenance
- model and backend independence
- graceful degradation and recoverability
- open, documented data formats

The personal pATHENA knowledge store is separate from this development repository.

## Repository filename policy

Repository filenames use ASCII transliteration (`ae`, `oe`, `ue`, `ss`) for portability across Git clients, shells, ZIP tools and upload paths. Document contents remain normal UTF-8.
