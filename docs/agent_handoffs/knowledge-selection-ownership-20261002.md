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
