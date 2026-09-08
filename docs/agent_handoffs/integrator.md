# pATHENA Feature Integrator Handoff

## Current branch state

- `main` remains strict read-only at `0d4d621f8a38ddf8eccfa09622bf193687619943`.
- Develop before this run: `cdc9e8e0064db659f9eabbfdb5f3720a76114fd6`.
- Integration target: `develop/pathena-next` only.
- Worker heads reviewed: errors `44cfc7cc618fc884568bcb309f1b562b15f357da`; spec-core `de62eb6a657b500f6abd2b1909ff1452c611572a`; backend `8fd7fd305d027f7367de01e53e95e255801a99f7`; UI `4e39464a5a08a34715344bdc7272b6d6658d3687`.
- `main` and `bnbgrs/ATHENA` were untouched; no force update, history rewrite, auto-merge or main promotion was used.

## Progress this run — UI-GAP-0005 quiet message-action lifecycle guard

The current UI handoff supplies a bounded READY slice: product/fix `4d128a864ecbb9463e54273d7f0d527910384591` with exact canonical ATHENA Quality `34270643737 = SUCCESS`. The worker failure was an exact Qt lifecycle regression in `tests/unit/test_pathena_pallas_full_view.py::test_open_workspace_reuses_one_synchronized_full_surface`, where `MessageActionQuietController.eventFilter()` could run while the parent-owned controller had no usable `document` binding.

Independent review of current Develop confirmed the unsafe direct `self.document` access was still present. The worker fix changes only `src/athena/desktop/pathena_message_action_quiet_7000.py`: the event filter obtains `document = getattr(self, "document", None)` and treats a transient missing binding as a no-op before preserving the existing ChildAdded resynchronization and all hover/focus/emphasis behavior.

Develop commit `7b3064524a2dbbae784458011d54fa9b70d0a59e` applies that bounded production change on exact parent `cdc9e8e0064db659f9eabbfdb5f3720a76114fd6`. The independent Develop compare is ahead-only by one commit, one file, +5/-1. No unrelated UI history, test weakening, Skip/XFail, Backend/Core/Storage/Security/Recovery/scheduler/worker/packaging/Windows mutation was imported.

## Current quality/error state

- UI exact source fix `4d128a864ecbb9463e54273d7f0d527910384591`: canonical Quality `34270643737 = SUCCESS`.
- Backend current worker head `8fd7fd305d027f7367de01e53e95e255801a99f7` records exact recovery state; Backend v41/§75 remains held until `ERR-0026` through `ERR-0029` are exact-green.
- Error handoff keeps `ERR-0026` through `ERR-0029` IN_PROGRESS and `ERR-0014`/`ERR-0025` STALE.
- Spec/Core remains blocked on exact-green Backend persistence before §75 Delta composition.
- Exact current Develop after this integration has no completed canonical Quality claim yet; promotion-ready remains false.
- Historical Windows/runtime crash signatures remain release-regression knowledge only absent exact-current reproduction.

## Tracker / visual state

- `docs/development/ALPHA_BETA_PROGRESS.md` was read. It already contains a historical capability row keyed `UI-GAP-0005` for persistent desktop system tray, while the current UI handoff independently reuses `UI-GAP-0005` for the quiet message-action lifecycle guard. To avoid silently corrupting the versioned tracker with a numbering collision, no destructive whole-file replacement was made in this run; the collision is explicitly recorded here for later tracker normalization.
- `docs/ui/11_SCREEN_REFERENCE_MANIFEST.md` remains exactly eleven slots and all remain `IMPLEMENTED_PENDING_VISUAL_REVIEW`; no `MATCH` claim is allowed without the original reference images.
- `docs/ui/VISUAL_GAP_LEDGER.md` was read; its existing evidence-backed entries remain unchanged.
- A separate repository `ERROR_LEDGER` artifact was searched but was not discoverable on the current connector/search surface; `errors.md` is the authoritative exact error handoff consumed this run.

## Next integration order

1. Obtain exact-current-Develop focused lifecycle/PALLAS regression plus canonical Quality for the descendant carrying `7b3064524a2dbbae784458011d54fa9b70d0a59e`, or a product-identical successor.
2. Consume Backend Quality on the current recovery lineage and integrate Backend v41/§75 only after `ERR-0026` through `ERR-0029` are exact-green; do not weaken migration or WAL exact-type guards.
3. If Backend remains non-READY, choose exactly one collision-free exact-green UI/Core successor; normalize the duplicate `UI-GAP-0005` tracker identifier before relying on that number cross-document.
4. Preserve the release crash-regression matrix before any Windows candidate or promotion claim.

## Persistent release guards

Retain explicit Beta/release regression acceptance for pypdf packaging metadata; fail-closed frozen argv routing and Desktop/Worker two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context DirectChat budgeting; Windows lane-lock `PermissionError` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError`; and storage-bootstrap/migration startup signatures including duplicate-column failures.

## Rules retained

No direct work on `main`; no main promotion; no force-push/history rewrite/auto-merge; no Skip/XFail or weaker assertions; no Security/Storage/Windows/Recovery/validator relaxation; no fake success or fabricated provenance.
