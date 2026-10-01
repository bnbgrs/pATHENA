# Research desktop protocol truth / selection recovery handoff — 2026-10-02

## Ausgangslage

Base: develop/pathena-next@67174198e1494fd4c8678aad60756c39ef5c160b.

The native Research workspace runs research_cli through a short-lived QProcess. The Core service itself already has durable state semantics, but the desktop trusted exit code 0 more than the helper response contract.

Concrete pre-change failures:

1. enqueue reported "Research job queued" and cleared the user's question even if an exit-0 response did not contain a valid JOB_QUEUED identity.
2. cancel always projected cancel_requested after exit 0, regardless of the actual service result. This is materially wrong: queued/waiting/paused jobs are cancelled synchronously by DurableJobRepository, while running jobs become cancel_requested.
3. cancel did not bind the response to the requested job ID, so a malformed/wrong helper response could mutate the selected run's state.
4. list parsing mutated QListWidget while parsing. Malformed rows were silently skipped, while invalid coverage could raise ValueError from the Qt callback. An exit-0 partial/corrupt response could therefore be shown as a successful refresh or break the callback.
5. show/cancel helper output could be written into the details pane after the user selected a different Research run while the helper was still active.
6. after protecting the pane from background output, a new continuity gap remained: once the old operation completed, the newly selected run was not automatically loaded.
7. QProcess.errorOccurred followed by finished could overwrite the first specific error with a second generic terminal status.

## Root Cause

The desktop had no explicit trust boundary for research_cli receipts and no durable ownership identity for an in-flight job-specific UI operation. Process exit code, selected job state, and details ownership were treated as if they were equivalent.

## Änderungen

### src/athena/desktop/research_workspace_protocol.py

New small process-boundary parser module. It does not change Research Core semantics.

- ResearchJobListEntry immutable projection.
- ResearchCancelReceipt immutable verified receipt.
- parse_research_job_list():
  - validates the entire list before UI mutation;
  - requires exactly five TSV fields per non-empty row;
  - validates UUID and known durable state;
  - requires a stage field;
  - validates finite coverage in [0, 1] or the explicit "-" unknown marker.
- parse_research_enqueue_receipt():
  - requires exactly one valid JOB_QUEUED UUID.
- parse_research_cancel_receipt():
  - requires JOB_CANCEL;
  - binds to the exact requested run;
  - accepts only the real service terminal outcomes: cancelled or cancel_requested.

### src/athena/desktop/research_workspace.py

- Tracks _operation_job_id for job-specific show/cancel operations.
- Tracks process-error terminal handling so errorOccurred is not overwritten by finished.
- Centralizes visible/accessibility status text plus diagnostic tooltip.
- Only show output streams into details, and only while the operation still owns the selected run.
- Selection changes during a busy job-specific operation show an explicit background-owner message instead of foreign output.
- After the old show/cancel operation finishes or fails, the current Research selection is automatically loaded when idle.
- Exit-0 list responses are fully validated before QListWidget is cleared/rebuilt.
- Invalid exit-0 list refreshes preserve the previous list/selection.
- Exit-0 enqueue without a verified receipt fails closed and preserves the user's query.
- Cancel applies the verified service-returned state instead of forcing cancel_requested.
- Cancel updates the selected list item's state only when the response belongs to that exact run.
- Background list failures do not replace selected run details with helper diagnostics.
- Successful enqueue/cancel no longer exposes raw helper protocol lines as normal user-facing details.

### tests/unit/test_research_workspace_protocol.py

Focused regression coverage for:

- valid/invalid Research list framing;
- NaN/out-of-range coverage rejection;
- exact enqueue identity;
- duplicate/missing/malformed enqueue receipt rejection;
- cancel receipt binding and both real service outcomes;
- queued -> cancelled UI projection;
- foreign cancel receipt fail-closed behavior;
- exit-0 enqueue without receipt preserving the typed question;
- invalid exit-0 list preserving previous projection/details;
- selection ownership during an in-flight show;
- current-selection detail reload after background show completion;
- errorOccurred -> finished status preservation.

## Verhalten danach

Research desktop success is now tied to verified helper data, not just process exit code. The UI projects the actual durable cancellation state and preserves the user's current selection/context during background helper completion.

## Dateien

- src/athena/desktop/research_workspace_protocol.py
- src/athena/desktop/research_workspace.py
- tests/unit/test_research_workspace_protocol.py
- this handoff

## Validierung

Completed:
- Active PR/file ownership was rechecked immediately before the branch.
- Branch is based exactly on current develop/pathena-next@67174198e1494fd4c8678aad60756c39ef5c160b.
- Compare before handoff: 0 commits behind Develop.
- Exact written source was re-read after the UI patch.

Not locally executable in this runtime:
- the execution container cannot resolve github.com, so a local checkout and pytest/Qt run cannot be performed;
- no local PASS is claimed.

Required exact-head checks:
1. pytest tests/unit/test_research_workspace_protocol.py
2. existing Research desktop/UI tests, especially cancel truth and Research experience
3. Ruff/format/type checks from canonical Quality
4. ATHENA Quality Gate
5. UI Focused / Visual regression if attached

## Parallel work / dependencies

No file overlap with the active Research work at branch creation; #326 had already merged.

Two parallel helper PRs appeared during this run and were inspected:
- #353 changes lifecycle/bootstrap of research_cli.py/research_results_cli.py and other helper CLIs but does not change the list/enqueue/cancel output contract parsed here.
- #351 hardens Jobs CLI single-line framing and is complementary to, not conflicting with, the separate Jobs parser work.

Do not overwrite #353 or reimplement its helper lifecycle changes here.

## Konfliktrisiko

If Develop advances with changes to research_workspace.py before integration, compare/reconstruct this bounded desktop delta on the fresh base rather than force-merging.

The new research_workspace_protocol.py and its focused test are branch-owned by this slice.

## Nächste sinnvolle Schritte

1. Qualify the exact PR head with focused Research tests and canonical Quality.
2. If red, inspect the exact failing job/log and fix root cause on this branch.
3. If #353 merges first, rebase/reconstruct only if Develop moved; the output protocol assumptions remain compatible based on inspected diff.
4. Merge only after exact-head evidence is green and the branch remains conflict-free.
5. After integration, separately review ResearchResults proposal-list framing; do not fold unrelated Core/worker work into this slice.

## Commit / Branch

Branch: fix/research-desktop-protocol-truth-20261002-sol

Commits before this handoff:
- 05534d92c17381e24c23d8c30a2dce5f5eb3364d — validate Research desktop helper responses
- 6d9a6a6972d70e95c6f2e7f2dd54f8759f835853 — bind desktop state to verified helper receipts
- f2745f0841f7d3c2bcd22743008554ddd79d4ddd — protocol truth regression coverage
- e062a02dbf3eb3db755a9baac3b4a2d4f00d6755 — recover current detail selection after background work
- 1f482e759b63af2691e0da55ed273fdb56f2e99b — current-selection detail recovery regression

## Follow-up during the same run: process-error recovery race

After PR creation, static QProcess ordering review found one final ownership edge:

- errorOccurred can be emitted while the old process is not yet fully NotRunning;
- an immediate scheduled reload of the user's new selection can therefore correctly refuse to start because the old helper is still active;
- finished must retry that pending reload after the process is terminal.

Repair:
- finished checks the existing background-operation owner marker after a prior process error and schedules the current-selection reload again;
- the reload is still guarded by QProcess idleness and exact current selection.

Additional commit:
- f5ae5891313c1145004521144f042aa6e1a4d64c — retry current-selection recovery after process error

Requalify the latest PR head, not the earlier 0f4c9631 intermediate head.

