# Manual handoff — Sources multi-file import queue — 2026-10-02

## Ausgangslage

Canonical base for this slice: `develop/pathena-next@67174198e1494fd4c8678aad60756c39ef5c160b`.

The Sources workspace already imported one local file correctly through the existing
`athena.desktop.sources_cli` helper process, but the native file picker exposed only
single-file selection. Repeating imports required reopening the picker for every file.
The workspace also had no safe queue state for accepting multiple import requests while
the one allowed helper process was busy.

This slice does **not** change Source capture, Raw Archive, representation, chunking,
SQLite ownership, the CLI protocol, or security validation. Those remain canonical Core
concerns.

## Root cause

`FilesWorkspace._choose_file()` called `QFileDialog.getOpenFileName()` and immediately
started one `QProcess`. The class deliberately owns only one helper process, so simply
starting multiple processes would create overlapping UI ownership and state races.

The correct product boundary is therefore a small UI-side path queue feeding the existing
single helper process sequentially.

## Änderungen

- File picker now uses multi-selection through `getOpenFileNames()`.
- Added `import_paths()` for a real sequential import queue.
- Existing files are normalized to absolute paths for queue identity without resolving
  symlinks; backend no-follow/security policy remains authoritative.
- Missing paths are ignored before enqueue.
- Duplicate pending paths and the currently active import path are not queued twice.
- Only one existing helper `QProcess` is used at a time.
- Controls remain disabled while queued work exists, including the event-loop gap between
  completed import N and import N+1.
- Success, non-zero command failure, and QProcess start/error paths all continue to the
  next queued file instead of abandoning the rest of the batch.
- Intermediate imports do not trigger redundant Source-list refreshes. The list refreshes
  after the queue drains.
- Status text identifies the current file and the real number of imports still queued.
- Sources list/details/import control now have explicit accessibility names/descriptions.
- No percentage progress is invented.

## Dateien

- `src/athena/desktop/files_workspace.py`
- `tests/unit/test_files_workspace_import_queue.py`
- this handoff

## Tests

New unit coverage is intentionally state-based and does not instantiate QApplication or
QWidget. This avoids adding more process-global PySide lifecycle pressure while PR #327
is independently fixing the canonical Qt test isolation problem.

Covered contracts:

1. duplicate/missing paths are filtered and the first valid file starts;
2. paths may queue while another helper operation is busy;
3. successful import immediately advances to the next queued file;
4. a non-zero import exit advances to the next queued file;
5. QProcess FailedToStart advances to the next queued file;
6. the native picker delegates multiple selected files into the queue.

Exact-head GitHub CI is still required before this slice is integration-ready.

## Parallel work / conflict risk

This branch deliberately avoids the active ownership areas:

- #327 Qt/Quality harness
- #329 direct Chat cancellation control plane
- LM Studio / Windows runtime work
- Research UI #326, which was integrated immediately before this slice

Primary conflict surface is only `src/athena/desktop/files_workspace.py`. UI/QA workers
should avoid unrelated edits to that file until this PR is qualified or explicitly
superseded.

## Do not repeat

- Do not introduce parallel Source import QProcesses to simulate throughput.
- Do not move Source validation/security policy into the UI.
- Do not resolve symlinks in the UI as a substitute for canonical intake validation.
- Do not claim batch success when one item fails; each import remains independently
  reported and later items continue.
- Do not add fake percent progress.

## Next steps

1. Run exact-head ATHENA Quality / relevant UI-focused gates.
2. Fix only failures attributable to this branch; do not weaken tests or harness rules.
3. If green, hand exact head to the Integrator for normal/history-preserving merge to
   `develop/pathena-next`.
4. After integration, optional drag-and-drop can call the already-real `import_paths()`
   contract without changing Source Core semantics, but that UI work is not required by
   this slice.

## Branch / commits

Branch: `fix/sources-multi-import-queue-20261002-sol`

Base: `67174198e1494fd4c8678aad60756c39ef5c160b`

Product/test commits before this handoff:

- `742503fa23ecac9212692c32ed5ac7d521edd518` — sequential queue implementation
- `a42068f75777331a050ef55d02dd22327a4105de` — initial queue regression coverage
- `455978996d91e2a66906aa48008bc05e7ae9608e` — remove Qt lifecycle dependency from tests
- `a7f0282f4399508952bc11049756bde6e18793e4` — accessibility / product polish
- `9528eca73b23c4a44d2ea9e6ef638bccc01c1e57` — test cleanup

PR: to be created after this handoff commit.
