# Manual handoff — Sources multi-file queue stacked after detail ownership — 2026-10-02

## Ausgangslage / parent

This is intentionally a **stacked** Sources slice.

Parent PR: #348 `Sources: decouple import from selected detail ownership`  
Parent branch: `fix/sources-import-detail-ownership-20261002-sol`  
Parent exact head used here: `3e3f516e13ee2cf9b8322d6494424f38bf857bfc`  
Canonical Develop under the parent: `67174198e1494fd4c8678aad60756c39ef5c160b`.

PR #348 fixed a real ownership bug: an import must not borrow the currently selected
Source ID or mutate that Source's detail pane. This queue work deliberately builds on
that fix instead of competing with it.

The superseded independent queue PR #336 should not be integrated. Its useful queue work
has been re-applied here on top of #348.

## Root cause addressed by this child

The native Sources picker exposed only one file per dialog invocation even though the
product workflow commonly needs several local documents. The workspace owns a single
helper `QProcess`, so launching multiple import helpers in parallel would create
operation/state races.

The correct boundary is a small UI-side path queue that feeds the existing helper
sequentially while preserving #348's strict import/detail ownership separation.

## Änderungen in this child

- native picker uses `QFileDialog.getOpenFileNames()`;
- `import_paths()` accepts multiple paths, ignores missing files, normalizes queue
  identity to absolute paths, and deduplicates active/pending paths;
- one existing helper process imports files sequentially;
- every queued import uses `source_id=None` and therefore never claims the selected
  Source detail pane;
- import completion does not replace the selected Source ID with the newly captured ID;
- import failure / QProcess startup failure does not poison selected Source details;
- later queued files continue after success, command failure, or process-start failure;
- Source-list refresh is deferred until the import queue drains;
- controls stay disabled while queued work remains, including the zero-delay handoff
  between helper processes;
- automatic refresh also respects a pending import queue;
- status text shows the current filename and the real number of remaining queued files;
- import/list/detail controls receive explicit accessibility metadata;
- no fake percentage or parallel-import throughput is introduced.

## Files changed by this child

- `src/athena/desktop/files_workspace.py`
- `tests/unit/test_pathena_files_workspace_import_queue.py`
- this handoff

Parent #348 additionally owns:
- `tests/unit/test_files_workspace_import_ownership.py`
- `docs/agent_handoffs/sources-import-detail-ownership-20261002.md`

Do not collapse the parent and child by copying one branch over the other.

## Validation coverage

The child queue tests are intentionally state-based and do not create QApplication or
QWidget instances. This avoids adding process-global Qt lifetime pressure while #327
owns the canonical Qt isolation work.

Contracts covered:

1. duplicate/missing files are filtered and the first valid import starts;
2. imports can wait safely behind another helper operation;
3. successful import advances the queue while preserving the pre-selected Source ID and
   detail text;
4. non-zero import failure advances the queue while preserving selected details;
5. FailedToStart advances the queue while preserving selected details;
6. the real picker boundary delegates all selected files to the queue.

The test filename follows `test_pathena_*.py` so the UI Focused candidate workflow
discovers it directly.

No exact-head CI PASS is claimed until the GitHub runs on the final child head are
terminal.

## Windows / packaging dependency

Frozen Windows execution needs the packaged worker to route
`athena.desktop.sources_cli`. Current bot work #347 broadens packaged helper routing and
supersedes the narrower #339 direction. Do not duplicate packaging changes in this
Sources UI child.

## Conflict / merge order

Required order:

1. qualify and integrate parent #348;
2. retarget this child from `fix/sources-import-detail-ownership-20261002-sol` to
   `develop/pathena-next`;
3. verify that the child diff remains only the queue/accessibility/tests/handoff delta;
4. rerun exact-head gates after retarget if GitHub changes the effective merge base;
5. integrate this child normally/history-preserving.

Primary product conflict surface: `src/athena/desktop/files_workspace.py`.

The old independent #336 is superseded specifically to eliminate this conflict.

## Do not repeat

- do not give imports a selected Source identity;
- do not clear/mark selected Source details busy merely because a file import starts;
- do not run multiple Source helper QProcesses concurrently;
- do not move canonical intake/symlink/security validation into Qt;
- do not resolve symlinks in the UI as a substitute for canonical Source validation;
- do not stop the whole batch because one file failed;
- do not invent percentage progress.

## Branch / commits

Child branch: `fix/sources-multi-import-after-ownership-20261002-sol`

Parent exact head: `3e3f516e13ee2cf9b8322d6494424f38bf857bfc`

Child commits before this handoff:
- `9723b6a1c965516c08947a37e3728ef50dee0dd8` — sequential queue stacked on ownership fix
- `28be8c16d47b321b82e91435aa0eb85516de4c8a` — state-based queue + ownership regressions

Replacement PR: to be created with #348's branch as base.
