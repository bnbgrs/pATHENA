# Knowledge selection ownership handoff — 2026-10-02

## Ausgangslage

Fresh branch from `develop/pathena-next@67174198e1494fd4c8678aad60756c39ef5c160b`.

The durable Knowledge workspace had three related state-truth defects:

1. Entity detail subprocesses tracked only the operation name, not the entity ID that owned the request. A user could select Knowledge/Claim/Decision B while a detail request for A was still running. The old A response could then be rendered under the new B selection.
2. Local filtering hid non-matching rows but did not reconcile selection. History/Obsidian/review actions could remain attached to an item that was no longer visible.
3. `QProcess.errorOccurred` cleared the operation but never moved an owned detail pane out of `busy`, leaving a failed detail request visually stuck.

## Root Cause

The UI lacked the ownership contract already used in Jobs/Sources. `_knowledge_operation` identified only `show`, `history`, etc.; it did not persist the corresponding Knowledge/Claim/Review ID. Detail streaming, completion, failure, and filtering therefore could not prove that the visible selection still owned the response.

## Änderungen

### `src/athena/desktop/knowledge_workspace.py`

- Added explicit per-operation entity ownership via `_knowledge_operation_entity_id`.
- Added operation-domain helpers for Knowledge, Claims, read-only Decisions, and review mutations.
- Detail streaming now writes only while the active entity still matches the visible selection.
- Selection changes during an active detail request replace stale partial output with a truthful pending state.
- Stale read completions/failures no longer overwrite or error the newly selected entity; the current selection is reloaded after the old request finishes.
- Review accept/reject preserves a newer review selection instead of clearing it when an older review action completes.
- Filtering now chooses the first visible match when the current row becomes hidden.
- A filter with zero matches clears canonical selection and disables History/Obsidian/review actions rather than leaving hidden-item actions live.
- Clearing the filter restores a visible selection.
- Owned process errors now mark the correct detail pane `error` instead of leaving it `busy`.

### `tests/unit/test_knowledge_workspace.py`

Added regression coverage for:

- filter-driven selection handoff to a visible Knowledge item;
- zero-match filter clearing hidden-item actions and recovery after clearing the filter;
- stale detail completion not replacing a newer selection;
- owned detail process errors leaving the pane in error state;
- review mutation completion preserving a newer selected review.

## Dateien

- `src/athena/desktop/knowledge_workspace.py`
- `tests/unit/test_knowledge_workspace.py`
- this handoff

## Verhalten danach

Visible selection is now the authority for entity detail rendering and user actions. A late local subprocess response cannot silently relabel itself as the currently selected entity, and a hidden filtered item cannot remain an actionable canonical selection.

## Validierung

Repository mutation and exact diff scope verified through GitHub compare.

Local Python/Qt execution is not available in this connector-only runtime, so no local PASS is claimed. Required exact-head validation:

- focused `tests/unit/test_knowledge_workspace.py`;
- Ruff;
- mypy;
- canonical ATHENA Quality;
- relevant UI-focused gate if triggered.

## Bekannte Restprobleme

- This slice does not redesign Knowledge UI and does not add universal search.
- It does not alter Obsidian runtime semantics.
- It does not touch Chat cancellation, Settings/News, LM Studio runtime, Storage, Research, or the Qt Quality harness.
- Native interaction should confirm rapid selection changes during real local CLI output; automated regressions cover the ownership contract.

## Abhängigkeiten / Konfliktrisiko

Current active parallel PRs inspected before mutation:

- #329 Chat cancellation — disjoint
- #330 Chat/shell UI — disjoint
- #332 update manifest — disjoint
- #333 Settings News — disjoint
- #334 LM Studio runtime — disjoint
- #325 Storage bundle — disjoint
- #327 Qt Quality harness — disjoint

No active PR in that set touches either modified Knowledge file.

## Commit / Branch

- Branch: `fix/knowledge-selection-ownership-20261002-sol`
- Base: `67174198e1494fd4c8678aad60756c39ef5c160b`
- Product commit: `05728739c9fc53a00b8101715b27ff53bc06f2b4`
- Test commit / pre-handoff head: `60e8d791a9c08fac53f4b63282dbd64fe49a19cd`

## Nächste sinnvolle Schritte

1. Qualify the exact PR head with focused Knowledge tests + Ruff + mypy + canonical Quality.
2. If a failure is specific to this slice, fix on this branch rather than opening a duplicate Knowledge PR.
3. After green gates, Integrator may merge normally into fresh `develop/pathena-next`.
4. Then exercise Knowledge filtering + rapid selection manually in the real Qt build and continue with another disjoint Alpha/Beta workflow gap.


## Erweiterung desselben Slices — List transport truthfulness

A second Knowledge-specific integrity defect was found while qualifying the ownership fix.

### Ausgangslage / Root Cause

Knowledge/Claim/Review list transport is line-delimited TSV.

- `knowledge_cli._safe()` removed tab/CR/LF only. Python `splitlines()` also recognizes VT, FF, NEL, U+2028 and U+2029, so user-controlled Knowledge titles or review reasons containing those separators could split one canonical record into multiple UI records.
- The Qt list renderers silently skipped malformed lines and still reported refresh success. An exit-0 but corrupted/truncated response could therefore partially replace a previously verified list.

### Änderungen

`src/athena/desktop/knowledge_cli.py`
- single-line fields now collapse all `splitlines()` separators plus tabs before emission.

`src/athena/desktop/knowledge_review.py`
- added pure all-or-nothing parsers for canonical Knowledge lists, Claim lists and pending Review lists;
- validates canonical UUID identity, revision number, single-line metadata and finite review confidence in [0, 1];
- malformed records fail closed through `KnowledgeReviewError`.

`src/athena/desktop/knowledge_workspace.py`
- list responses are fully parsed before any QListWidget mutation;
- invalid exit-0 output preserves the previously verified list;
- browser status becomes explicit error with diagnostic tooltip/accessibility description;
- successful list parse clears the error UI state.

Tests:
- `tests/unit/test_pathena_knowledge_review.py` now covers valid records, split/malformed records, invalid review confidence/identity and preservation of an existing UI list on corrupt exit-0 output;
- older direct detail tests were aligned with the new explicit request/entity ownership contract;
- `tests/unit/test_knowledge_cli_framing.py` covers tab, CRLF, VT, FF, NEL, U+2028 and U+2029 framing boundaries.

### Additional commits

- `b8c95cad069a31b420d30e1981beaaed4c6cf324` — align existing Knowledge detail tests with request ownership
- `bfdc96cafb644d23458236fce5a23dcf11c6ec3b` — canonical list parsers
- `b1dea1ab8e4f1f31bbfa5326f376f5996f323f75` — CLI single-record framing
- `07cfb49ed94863467da001f44f3afc78fd6f207b` — fail closed before Qt list mutation
- `f821147bc6b08ecb0202275671904aa1a9595d1f` — import normalization
- `258613a139b6adb6731e4c8c2c3b9ca8eccaf247` — list protocol/UI preservation regressions
- `1cf0e0ad1752c66ad94735899c008449fea5f09c` — CLI framing regressions

### Visual gate evidence from superseded head

The earlier exact head `65de262ff9a4dbb6ac05fc414f974240729ef367` completed 11/11 Windows captures. Its Knowledge surface passed comparator policy:
- changed_ratio 0.00114339 <= 0.002
- mean_delta 0.11345896 <= 0.35

That workflow failed only on autonomous PALLAS capture:
- changed_ratio 0.01056006
- mean_delta 0.64363388

This branch did not touch PALLAS. PR #352 now owns the demonstrated PALLAS visual-capture determinism defect. Do not weaken thresholds or update PALLAS baseline in #343.

### Validation state after extension

Fresh exact-head workflows were created for `1cf0e0ad1752c66ad94735899c008449fea5f09c` before this handoff edit:
- ATHENA Quality Gate: queued
- pATHENA Core Focused Candidate: queued
- pATHENA UI Focused Candidate: queued
- pATHENA 11-Surface Visual Regression: queued

No terminal PASS is claimed yet.


### Diff-review correction

Final ownership review found one self-introduced risk before integration: global filtering could reconcile selections in inactive Claim/Decision tabs and therefore trigger unnecessary hidden-tab detail subprocesses. Selection reconciliation is now limited to the currently visible canonical tab while visibility filtering remains global.

- Product commit: `64c3f679580537efdc7d666a9ae7c0d6edf2ead8`
- Regression: `200b9360283bd273c992f6d0970d795252052462`
- Expected result: typing in the Knowledge filter cannot start hidden Claim/Decision detail I/O; switching tabs applies the same filter and reconciles that tab normally.

After this handoff update, treat the resulting commit as the exact candidate head. Do not infer terminal CI success from superseded workflow runs.
