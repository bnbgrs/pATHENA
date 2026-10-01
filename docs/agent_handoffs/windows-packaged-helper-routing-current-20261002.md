# Windows packaged workspace helper routing — current Develop handoff — 2026-10-02

## Ausgangslage

Fresh candidate rebuilt from current integration head
`develop/pathena-next@467ef434236c320e4afe9d21a39c20a4a2b75728`
(after Chat cancellation PR #329 merged).

The supported frozen Windows desktop intentionally rewrites `sys.executable` from
`pATHENA.exe` to sibling `pATHENA-Worker.exe`. Desktop workspaces use
`sys.executable -m ...` for short-lived Core-backed helper boundaries.

Current Develop routed Core, generic ATHENA CLI, Jobs, hardware acceptance and
recovery, but did not route the actual helpers used by Sources, Research, Research
Results, Knowledge, Obsidian export and canonical-memory actions. Those workflows
could therefore work from a source checkout while the packaged Windows desktop
rejected them fail-closed as unsupported module dispatches.

## Root Cause

The two-executable/fail-closed packaging architecture is intentional. The explicit
worker allowlist drifted behind the real desktop child-process call sites, while the
Windows package smoke covered too few helper roles to detect the drift.

## Änderungen

- Added explicit packaged targets and module routes for:
  - `athena.desktop.sources_cli`
  - `athena.desktop.research_cli`
  - `athena.desktop.research_results_cli`
  - `athena.desktop.knowledge_cli`
  - `athena.desktop.knowledge_obsidian_export`
  - `athena.desktop.canonical_memory_cli`
- Added matching lazy worker dispatch for all six roles.
- Kept unknown `-m` modules fail-closed; no generic Python/module execution.
- Preserved explicit unit route/dispatch coverage and added a source-level drift
  guard: every literal desktop `sys.executable -m <module>` role must resolve
  through the packaged router.
- Extended the native Windows package workflow to prove:
  - all helper roles import/route in the built `pATHENA-Worker.exe`;
  - unsupported module dispatch still fails;
  - Sources import persists and is recovered by a fresh worker/process;
  - Research enqueue persists and is recovered by Research and Jobs helpers;
  - Knowledge and canonical-memory helpers execute real application/storage paths;
  - Research Results reaches its real helper boundary rather than worker rejection;
  - promoted Knowledge is recovered through `knowledge_cli`;
  - Obsidian preview executes against a real temporary vault;
  - existing packaged provider-state and desktop graceful-shutdown smokes remain.
- Updated generated `START_HERE.txt` documentation for the real worker role set.

## Dateien

- `src/athena/desktop/packaged_app.py`
- `src/athena/desktop/packaged_worker.py`
- `tests/unit/test_windows_packaging_contract.py`
- `.github/workflows/windows-package.yml`
- `scripts/build_windows_portable.ps1`
- this handoff

## Vorherige Parallel-Arbeit / Konsolidierung

Two independent implementations appeared during the run:
- #339: Sources-only packaged routing with a strong durable Source reload smoke;
- #347: broader helper routing.

To remove competing ownership, both are now closed. #360 was an intermediate stack
that combined #339 plus the broader roles, but it was based on pre-#329 Develop.
This branch is the single fresh current-Develop consolidation and contains the useful
Source persistence acceptance from #339 plus the broader routing/drift coverage.

Do not revive/cherry-pick #339 or #347 on top of this candidate.

## Validierung

Strong native evidence already exists for the implementation:
- #339 exact candidate Windows Package run 36937864299: PASS. Individual steps for
  packaging contracts, worker fail-closed routing, Sources import + fresh-worker
  reload, persistent Knowledge, actual desktop start/window, graceful process-tree
  shutdown and artifact generation all passed.
- superseded broad candidate `f72f047131a254522c5efd12674a2fc49e6da965`
  Windows Package run 36937879357 / job 110622294545: PASS. It contained the full
  helper role set and real helper lifecycle smoke, then built and launched the actual
  packaged desktop and shut it down cleanly.
- Direct local checkout in the ChatGPT execution container is blocked by github.com
  DNS resolution, so no local PASS is claimed.

The evidence above validates the implementation design on native Windows, but this
fresh current-Develop commit still requires its own exact-head gates before merge.

## Bekannte Restprobleme / Abhängigkeiten

- PR #353 changes the helper CLI lifecycle internally from full
  `AthenaApplication.start()/stop()` to storage-bootstrap-only. It does not own these
  packaging files. If #353 merges before this candidate, refresh onto current Develop
  and rerun native package smoke because helper runtime semantics changed.
- PALLAS visual regression flakiness is independently owned by #352. A #353 visual
  run captured all 11 surfaces successfully and failed only PALLAS
  (`changed_ratio=0.00843243`, `mean_delta=0.48803428`); this packaging slice
  neither changes nor should weaken that visual gate.
- Historical #314 touches the Windows packaging workflow from an old candidate and
  must not overwrite the current workflow.

## Konfliktrisiko

Packaging-only shared files are the conflict surface:
`packaged_app.py`, `packaged_worker.py`, the packaging contract test,
`windows-package.yml`, and the portable-build script.

No Chat, LM Studio, Settings, Storage, Sources UI, Knowledge UI, Jobs UI/protocol,
Backup, Security, Logging or PALLAS product file is changed by this candidate.

## Nächste sinnvolle Schritte

1. Run exact-head Quality + native Windows Package on this fresh candidate.
2. Attribute visual-only PALLAS failures to #352 evidence; do not loosen thresholds.
3. If #353 lands first, rebuild/refresh the candidate from current Develop and rerun
   package acceptance.
4. After native package PASS, manually click the packaged Windows desktop through
   Sources, Research, Research Results, Knowledge, canonical-memory and Obsidian
   preview when a real Windows interactive environment is available.
5. Merge this single candidate; keep #339/#347/#360 superseded to avoid duplicate
   packaging ownership.

## Branch

- Branch: `fix/windows-packaged-helper-routing-current-20261002-sol`
- Parent: `develop/pathena-next@467ef434236c320e4afe9d21a39c20a4a2b75728`
