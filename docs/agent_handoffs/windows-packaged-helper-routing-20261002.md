# Windows packaged desktop helper routing — 2026-10-02

## Ausgangslage

The supported Windows package uses a two-executable topology. In a frozen desktop,
`prepare_frozen_desktop_runtime()` rewrites `sys.executable` from `pATHENA.exe`
to the sibling `pATHENA-Worker.exe`. Desktop workspaces intentionally launch
short-lived Core-backed helpers through `sys.executable -m ...`.

On current `develop/pathena-next@67174198e1494fd4c8678aad60756c39ef5c160b`,
the strict worker dispatcher allowed Core, the generic ATHENA CLI, Jobs, hardware
acceptance and recovery, but it did not allow the helper modules used by Research,
Research Results, Sources, Knowledge, Obsidian export or canonical-memory actions.

That meant those workflows could work from a source checkout while the packaged
Windows desktop rejected the same child launches as unsupported module dispatches.

## Root Cause

The packaging architecture was correct to fail closed, but the allowlist in
`src/athena/desktop/packaged_app.py` had fallen behind the actual desktop
`sys.executable -m ...` call sites. The Windows package smoke only exercised
`athena` and `athena.api.process`, so a successful package/start smoke did not
prove the main workspace helper processes could start.

## Änderungen

- Added explicit packaged targets and allowlist entries for:
  - `athena.desktop.research_cli`
  - `athena.desktop.research_results_cli`
  - `athena.desktop.sources_cli`
  - `athena.desktop.knowledge_cli`
  - `athena.desktop.knowledge_obsidian_export`
  - `athena.desktop.canonical_memory_cli`
- Added corresponding lazy worker dispatch in `packaged_worker.py`.
- Kept unknown `-m` modules fail-closed; no generic Python/module execution was enabled.
- Extended the Windows worker smoke to execute every desktop helper with `--help`
  against the built `pATHENA-Worker.exe`.
- Added unit coverage for every explicit route and a source-level guard that scans
  desktop Python files containing `sys.executable` for literal `-m <module>`
  invocations. Every discovered literal module must be accepted by the packaged router.
  This makes future allowlist drift fail during the packaging contract test.
- Updated portable-package `START_HERE.txt` generation so the documented worker
  responsibility matches the real package topology.

## Dateien

- `src/athena/desktop/packaged_app.py`
- `src/athena/desktop/packaged_worker.py`
- `tests/unit/test_windows_packaging_contract.py`
- `.github/workflows/windows-package.yml`
- `scripts/build_windows_portable.ps1`
- this handoff

## Verhalten danach

A frozen `pATHENA.exe` can continue to redirect all internal Python child launches
to the sibling worker without breaking Research, Research Results, Sources, Knowledge,
Obsidian export or canonical-memory UI workflows. Unsupported module names remain
rejected.

## Validierung

Static verification completed on the exact branch:
- branch started from current Develop SHA
  `67174198e1494fd4c8678aad60756c39ef5c160b`;
- no active #325/#327/#329/#330/#331/#332/#333/#334 product file set was modified;
- pre-handoff diff was ahead of Develop and not behind;
- all known desktop QProcess/`sys.executable` call sites inspected during this run
  are either existing allowed roles or one of the newly added roles.

Executable validation is delegated to exact-head GitHub Actions because this chat
runtime does not provide a checked-out Windows build environment. Do not claim the
package fix release-ready until the Windows package workflow and relevant Quality
checks are terminal green.

## Bekannte Restprobleme

- Native Windows end-to-end clicks through the affected workspaces are still desirable
  after the worker-routing smoke is green; `--help` proves executable routing/import,
  not every database/state transition.
- The separate Quality segmentation fault in
  `test_desktop_chat_selection_state.py` is owned by active PR #327 and was not
  duplicated here.
- Chat cancellation is owned by #329; LM Studio runtime by #331/#334; Settings News
  recovery by #333; Update manifest hardening by #332; Storage bundle by #325.

## Abhängigkeiten / Konfliktrisiko

This branch deliberately avoids the current active product files above. The only
open historical overlap noticed is stale build-trigger PR #314 touching
`.github/workflows/windows-package.yml`; it is based on an old Develop candidate and
must not overwrite this workflow change. Reconcile only if #314 is unexpectedly revived.

## Nächste sinnvolle Schritte

1. Require exact-head Windows package smoke to pass for this branch.
2. Require canonical Quality to pass or attribute any failure to an independently
   owned current gate issue (notably #327) with exact logs.
3. On native Windows, launch the built candidate and exercise:
   Research list/show, Research Results, Sources list/show/import, Knowledge list/show,
   canonical-memory relations/merge, and an Obsidian preview.
4. Merge only after the exact candidate is green; do not salvage the change by
   weakening the worker's fail-closed routing.

## Branch / Commit

- Branch: `fix/windows-packaged-helper-routing-20261002-sol`
- Base: `develop/pathena-next@67174198e1494fd4c8678aad60756c39ef5c160b`
- Last product/docs commit before this handoff:
  `72a1bdd15a73b1945cb04d6030a509092503b04e`
