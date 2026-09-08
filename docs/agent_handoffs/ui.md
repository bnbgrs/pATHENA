# pATHENA UI Handoff

## Current baseline

- Base: `develop/pathena-next@cdc9e8e0064db659f9eabbfdb5f3720a76114fd6`.
- Worker: `postmerge/ui`.
- History-preserving NON-FORCE synchronization: `fc174c80f03c54fb23a68d18a281f5b4c80bacbf`, with parents UI `4d128a864ecbb9463e54273d7f0d527910384591` and Develop `cdc9e8e0064db659f9eabbfdb5f3720a76114fd6`.
- Original eleven reference images: `VISUAL_REFERENCE_PENDING`; no pixel parity or `MATCH` claim is made.

## Exact verification consumed this run

Canonical ATHENA Quality Gate `34270643737` completed `success` on exact UI head `4d128a864ecbb9463e54273d7f0d527910384591`.

That exact lineage contains both currently relevant bounded UI deltas:

1. Global icon-rail accessibility: product `319a0d7660bf7dc03e1a6c3550efd0e15b76e94b`, focused test `19924adc2881b3eff06a6c4c343abba7e635ecbc`.
2. Quiet message-action lifecycle guard: product/fix `4d128a864ecbb9463e54273d7f0d527910384591`.

No Skip/XFail, assertion weakening, backend/storage/security behavior, process spawning, scheduler ownership, provider/transport behavior or persistence semantics were changed.

## UI-GAP-0004 — Global rail accessible page names

Status: `FIXED / INTEGRATED`.

The icon-only navigation keeps its existing visible glyphs and existing human tooltips. The human tooltip text is additionally exposed through `Qt.ItemDataRole.AccessibleTextRole`, so assistive technology receives the real page name without altering layout, routing or visual density.

Integrator already transplanted the bounded product/test blobs onto Develop as `bf25017d37e88438a9644445b9f5da47c11098d0` and recorded the integration in `cdc9e8e0064db659f9eabbfdb5f3720a76114fd6`.

## UI-GAP-0005 — Quiet message-action lifecycle guard

Status: `FIXED_VERIFIED_PENDING_INTEGRATION`.

Quality `34264917412` exposed one exact failure in `tests/unit/test_pathena_pallas_full_view.py::test_open_workspace_reuses_one_synchronized_full_surface`: `MessageActionQuietController.eventFilter()` could be invoked during Qt lifecycle churn before/after the controller had a usable `document` binding.

Fix `4d128a864ecbb9463e54273d7f0d527910384591` uses `getattr(self, "document", None)` inside the event filter, matching the already established lifecycle-safe tab-order controller pattern. A transiently absent document is treated as a no-op. Visibility, opacity policy, callbacks, focus behavior and action layout remain unchanged.

Exact verification: `34270643737 = success` on `4d128a864ecbb9463e54273d7f0d527910384591`.

Current worker synchronization `fc174c80f03c54fb23a68d18a281f5b4c80bacbf` uses current Develop as the tree base and overlays only the verified quiet-action blob, so unrelated worker history is not imported into the current tree.

## Manifest / visual evidence

`docs/ui/11_SCREEN_REFERENCE_MANIFEST.md` remains exactly eleven slots. Screen 01 records the technically verified rail accessibility closure; Screen 08 records the technically verified quiet-action lifecycle closure. All screens remain `IMPLEMENTED_PENDING_VISUAL_REVIEW` because the original user reference images are not available for direct opening in the current repository/tool path.

## Runtime/release guard retention

Historical Windows/runtime signatures remain regression/release knowledge only unless reproduced on an exact current SHA: frozen-child argv relaunch loops; two-EXE Desktop/Worker invariant; 2048-context DirectChat reserve/persisted assistant turn; lane-lock `PermissionError` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError`; duplicate-column/storage-bootstrap startup failures. This UI run did not modify those systems.

## Integrator handoff

- `UI-GAP-0004`: already integrated; preserve the exact rail accessibility behavior.
- `UI-GAP-0005`: READY for bounded Integrator review using verified fix `4d128a864ecbb9463e54273d7f0d527910384591`, with canonical Quality `34270643737 = success`.
- The current synchronized/documentation descendant must receive its own canonical Quality result before any whole-lineage integration claim. Integrator may instead transplant only the verified quiet-action blob/fix after independent collision review.
- Do not infer screenshot parity or `MATCH` from technical verification.

## Next UI gap

After consuming canonical Quality for the synchronized/documentation descendant, select at most one new evidence-backed accessibility/state/interaction/responsive/hierarchy/human-copy gap from the real UI. Do not reopen `UI-GAP-0004` or `UI-GAP-0005` absent exact-current regression evidence.
