# Manual UI research-operation ownership repair — 2026-09-14

## Purpose

Prevent asynchronous Research `show` / `cancel` completion from mutating the detail pane or state of a different research job after the user changes selection while the helper process is still running.

## Exact lineage

- Parent presentation helper: `manual/ui-structured-details-20260914@8c53a58a32698876035034c61ef445653422607e`.
- Original UI worker lineage beneath that helper: `postmerge/ui@de4efa5d3814948d47d83484c4a27ac0c2daf64c`.
- Sequential repair branch: `manual/ui-research-operation-ownership-20260914`.

## Root cause

`ResearchWorkspace` tracked only an operation name and the current selection. Unlike Jobs and Sources, it did not remember the job that owned a running job-scoped operation. Because the list remains selectable while a `QProcess` runs, a user could change selection before `show` or `cancel` completed. The old completion path could then render the previous job's details under the new selection or mark the newly selected job as `cancel_requested`.

## Bounded repair

- Track `_operation_job_id` for job-scoped Research operations.
- Bind `show` and `cancel` to the job selected when the operation starts.
- Treat unscoped `list` / `enqueue` operations as owning no selected detail pane.
- When selection changes during a running operation, keep the new selection visible and show a background-operation notice rather than writing stale output into it.
- Render successful `show` output only when the original job is still selected.
- Apply `cancel_requested` UI state only when the cancelled job is still the selected job.
- Preserve raw failed `show` diagnostics only in the pane owned by that operation.
- Include the owning job label in status text for background completion/failure.
- Add focused unit coverage for the ownership predicate.

## Explicit non-changes

No research repository, scheduler, job lifecycle, persistence, provenance, scope snapshot, retry, cancellation persistence or CLI output contract is changed.

## Consumption rule

This is intentionally sequential on top of the structured-details helper. Do not cherry-pick it ahead of that parent slice. After `manual/ui-structured-details-20260914` is consumed by `postmerge/ui` and exact-head gates are green, consume this bounded repair, re-run UI Focused + canonical Quality, then generate a fresh Windows 11-surface snapshot.
