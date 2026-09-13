# Manual UI structured-details slice — 2026-09-14

## Purpose

Move the Research, Jobs and Sources detail panes away from raw helper-CLI presentation while preserving the existing durable Core, CLI and repository contracts.

## Exact lineage

- Source UI worker head: `de4efa5d3814948d47d83484c4a27ac0c2daf64c` (`postmerge/ui`).
- Manual branch: `manual/ui-structured-details-20260914`.
- This slice is presentation-only.

## Changes

- Add `athena.desktop.workspace_detail_presenter` with pure formatters for successful `show` output from Research, Jobs and Sources.
- Group existing fields into scan-friendly sections such as Scope, Work Items, Execution, Requested Scope, Checkpoints, Capture & Retrieval and Processing.
- Preserve values, multiline JSON continuation lines and unknown future CLI lines instead of dropping them.
- Buffer `show` output until command completion and render the structured view only after a successful exit.
- On failed `show` commands, present the raw merged helper output unchanged so diagnostics remain available.
- Clear the Research and Jobs detail panes when a new selected item starts loading, avoiding accidental append onto stale detail text.
- Add pure unit coverage for Research, Jobs and Sources formatting, including unknown fields and multiline job JSON/checkpoint metadata.

## Explicit non-changes

This slice does **not** change:

- helper CLI output contracts;
- job, research or source repositories;
- persistence or SQLite behavior;
- scheduler semantics;
- provenance, protection or recovery behavior;
- Source capture/chunking semantics;
- job lifecycle transitions;
- release gates or visual baselines.

## Safety / forward compatibility

The presenter recognizes current labels only for display. Unknown top-level lines and indented continuation lines remain visible. A failed helper command never receives presentation formatting; its raw merged output is retained in the detail pane.

## Consumption rule

Do not merge this branch directly into `develop/pathena-next`. The UI worker should consume the bounded delta only after exact-head CI is green and branch drift is checked. After consumption, generate a fresh Windows 11-surface visual snapshot; the older 2026-09-11 snapshot predates meaningful UI changes and is not current release evidence.
