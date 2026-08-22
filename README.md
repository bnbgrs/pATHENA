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

The bootstrap repairs/verifies the pinned `uv 0.11.21`, installs Python 3.12 through `uv`, synchronizes the locked desktop environment, validates runtime configuration, runs the Core doctor, and proves model-independent Core/API persistence across a disposable restart.

Then run the normal local readiness check at any time with:

```powershell
.\scripts\check_windows.ps1
```

Start the desktop application:

```powershell
.\scripts\start_windows.ps1
```

The launcher performs a fast runtime/database preflight before opening the desktop. LM Studio may be offline; model-backed operations become available when a compatible local model is loaded.

By default operational state is stored outside the repository in:

```text
%LOCALAPPDATA%\ATHENA
```

Choose a different absolute runtime root during bootstrap when desired:

```powershell
.\scripts\bootstrap_windows.ps1 -LocalRoot "D:\pATHENA-data"
```

Validated bootstrap overrides are saved in the repository-local, git-ignored `.pathena.windows.ps1`, so the normal `start_windows.ps1` command reuses them without modifying global Windows environment variables.

A non-default local LM Studio endpoint can be persisted the same way:

```powershell
.\scripts\bootstrap_windows.ps1 `
    -LocalRoot "D:\pATHENA-data" `
    -LmStudioBaseUrl "http://127.0.0.1:1234"
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

Require a loaded local LLM as part of the Windows readiness check with:

```powershell
.\scripts\check_windows.ps1 -RequireModel
```

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
