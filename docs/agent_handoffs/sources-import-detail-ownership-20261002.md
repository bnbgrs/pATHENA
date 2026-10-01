# Sources import detail ownership handoff — 2026-10-02

## Ausgangslage

Fresh branch from `develop/pathena-next@67174198e1494fd4c8678aad60756c39ef5c160b`.

The Sources workspace allowed a file import to inherit the ID of the Source that happened to be selected before the file dialog opened. It also treated `None == None` as detail ownership.

## Root Cause

`FilesWorkspace._choose_file()` called the generic process launcher with `source_id=self._selected_source_id`. That identity belongs to the selected Source, not to the new import. `_operation_owns_details()` then compared identities without requiring a concrete operation Source ID.

Consequences:
- starting an unrelated import cleared and marked the selected Source detail busy;
- import stdout could be streamed into the selected Source detail;
- an import process failure could mark a valid selected Source detail as error;
- with no selection, `None == None` falsely reported detail ownership.

## Änderungen

### `src/athena/desktop/files_workspace.py`

- File import is launched with `source_id=None`; it no longer borrows the currently selected Source identity.
- Import no longer clears or marks the selected Source detail pane busy.
- `_operation_owns_details()` now requires a concrete operation Source ID before equality can establish ownership.

The main Sources status label still truthfully reports import progress/success/failure. Existing selected Source detail remains owned only by show/process operations for that exact Source.

### `tests/unit/test_files_workspace_import_ownership.py`

Added focused regression coverage proving:
- import starts without selected-detail ownership and preserves current detail text;
- detail ownership is false for `None/None` and only true for matching concrete IDs;
- import FailedToStart updates the Sources status but leaves the selected Source detail state/content intact.

## Dateien

- `src/athena/desktop/files_workspace.py`
- `tests/unit/test_files_workspace_import_ownership.py`
- this handoff

## Verhalten danach

Import is a workspace-level operation until the new Source is captured and the canonical list refreshes. It cannot masquerade as an operation on whichever Source the user had selected beforehand.

## Validierung

Exact GitHub diff against Develop verified:
- 2 commits before handoff
- 0 commits behind
- product delta: 9 changed lines
- one focused new test module

Local Python/Qt execution is unavailable in this connector-only runtime, so no local PASS is claimed. Exact-head CI is required before integration.

## Bekannte Restprobleme

- This slice does not change canonical Source capture/processing semantics.
- It does not change Source list parsing or source-processing jobs.
- Native rapid interaction should still be exercised in the packaged Qt build.

## Abhängigkeiten / Konfliktrisiko

Current active parallel PRs were checked before mutation. No inspected active PR (#325, #327, #329, #330, #332, #333, #334) modifies either Source file in this slice.

## Commit / Branch

- Branch: `fix/sources-import-detail-ownership-20261002-sol`
- Base: `67174198e1494fd4c8678aad60756c39ef5c160b`
- Product commit: `b4c22b7b89df5d2dc9f600b898d949b9e2ce12ba`
- Test commit / pre-handoff head: `2a103073d464cdaea2da4202f002840fd361d50e`

## Nächste sinnvolle Schritte

1. Run exact-head focused/UI/Quality gates.
2. If a Source-specific regression appears, fix this branch rather than creating a duplicate slice.
3. After terminal green evidence, hand to the Integrator for normal merge into fresh Develop.
4. Manually exercise: selected Source -> Import -> cancel/success/failure, verifying the selected detail remains stable.
