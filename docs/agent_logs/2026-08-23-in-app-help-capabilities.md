# In-app help and capability discovery

- Date: 2026-08-23
- Repository: `bnbgrs/pATHENA`
- Branch: `agent/pathena`
- Scope: productive desktop functionality only; no CI or Quality Gate changes

## Problem

The desktop had several functional workspaces and a Ctrl+K command palette, but no central in-app explanation of what pATHENA can currently do. Users had to infer functionality from navigation labels or external documentation.

## Implemented

`src/athena/desktop/command_palette.py` now provides a non-blocking Help / Capabilities dialog.

- `F1` opens Help from anywhere in the desktop window.
- `Ctrl+K` exposes a new `Open help & capabilities` command.
- The command-palette footer advertises `F1 HELP`.
- Help explains the current CHAT, KNOWLEDGE, RESEARCH, JOBS, FILES, SYSTEM and SETTINGS workspaces.
- The available-command list is generated from the command palette's actual registered commands each time Help opens, so command discovery does not become a separately maintained static list.
- Help documents the local-first operating model, Core/provider separation and Raw Archive source behavior.
- The dialog is non-modal and can be closed with Escape, preserving the desktop workflow.

## Production value

This closes a usability gap between implemented capability and discoverability. pATHENA can now explain its current desktop surface without requiring the user to leave the application or inspect source/docs.

## Verification

The implementation is isolated to the desktop command/help surface. It does not modify Core persistence, migrations, ATHENA repositories, CI workflows or Quality Gate behavior.

Next productive work should continue from the then-current `agent/pathena` HEAD and select the highest-value remaining functional gap rather than performing CI stabilization.
