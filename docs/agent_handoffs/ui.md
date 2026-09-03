# pATHENA UI Handoff

## Current baseline

- Base: `develop/pathena-next@aed609ef8a7ff4af48e15e3dba953daf35d56b5c`
- Worker: `postmerge/ui`
- UI product candidate retained: `99d6b31c78be2932154137a6527200759f349628`
- First Ruff harness correction: `77e7b4c7d95202e6814226e2b4a2c4a54e3f5c8e`
- Second Ruff harness correction: `ecbf44ddd0fb8c7428d4cca090834eca284b997e`
- Original eleven reference images: `VISUAL_REFERENCE_PENDING`; no pixel-level parity or `MATCH` claim is made.

## Current slice

### UI-GAP-0004 — Startup/readiness infrastructure copy

Status: `FIXED_PENDING_VERIFY`, P1, Screen 11.

Spec anchor: `docs/alpha/16_Desktop_Anwendung_und_Benutzeroberflaeche.md` requires normal use to present pATHENA while daemon/workers/providers remain background infrastructure.

Product candidate `99d6b31c78be2932154137a6527200759f349628` changes presentation only:

- `Local core offline` -> `pATHENA reconnecting`.
- `Waiting for the local core` -> `Getting pATHENA ready`.
- Core-specific normal-workspace tooltips/placeholders become pATHENA/model-level guidance.
- `OfflineComprehensionController` continues to expose the truthful internal `core-offline` readiness state.
- reconnect, provider, transport, persistence, recovery and security semantics remain unchanged.

Focused assertions remain in `tests/unit/test_pathena_startup_experience_2900.py` and `tests/unit/test_pathena_offline_comprehension.py`.

## Exact Quality history and correction chain

1. Canonical Quality run `33785726577` on synchronized lineage `b76115748aed53e3502a71eef10a41b11f97f8ae` passed Windows path safety, Linux storage, local-install smoke, specification validator, mypy and full pytest. Ruff alone failed with exact `B010` at `tests/unit/test_pathena_startup_experience_2900.py:61` because `setattr(window, "_core_transport_ready", False)` used a constant attribute name.
2. Commit `77e7b4c7d95202e6814226e2b4a2c4a54e3f5c8e` fixed only that harness defect with `_DisconnectedStartupWindow`, preserving the exact disconnected-state behavior and without changing product code/assertions/lint configuration.
3. Canonical Quality run `33792012599` on `25addc9833d0d655efa46cd48974e160a7f275dd` again passed Windows path safety, Linux storage, local-install smoke, specification validator, mypy and full pytest (`4492 passed`, three existing Windows-only skips). Ruff found one remaining harness-only defect: `I001` unsorted/unformatted import block at `tests/unit/test_pathena_startup_experience_2900.py:1:1`.
4. Commit `ecbf44ddd0fb8c7428d4cca090834eca284b997e` reformats only the PySide6 `QtWidgets` import into Ruff/isort-compatible multiline form. No product or assertion semantics changed.

Until a Quality run succeeds on the exact current final UI head containing the second correction plus only evidence documentation, UI-GAP-0004 remains `FIXED_PENDING_VERIFY`.

## Collision / ownership guidance

- Core: normal-Hybrid Search composition is Core-owned; no overlap.
- Backend: ExternalAccessGateway runtime-boundary hardening is Backend-owned; no overlap.
- Error: `ERR-0004` corresponds to this startup harness lint chain. Error should verify/close it only from exact successful current-lineage evidence and should not create a competing mutation while UI owns this test file.
- Preserve contextual Evidence & Activity behavior and PALLAS lifecycle fixes already integrated.

## Integrator handoff

Do not integrate UI-GAP-0004 as READY until canonical Quality succeeds on the exact final `postmerge/ui` head containing `ecbf44ddd...`. When green, independently review the bounded product/test diff and integrate only to `develop/pathena-next`. No visual `MATCH` is implied.

## Next UI work

1. Consume exact-head Quality for the current worker. If any stage fails, fix the exact current-lineage cause before taking another product slice.
2. If green, mark UI-GAP-0004 technically `FIXED`, update ledger/manifest, and hand the exact worker SHA to Integrator/Error.
3. Retry access to the actual eleven references and render Screen 11 for direct comparison. If reference pixels remain unavailable, select the next gap only from explicit versioned UI/Alpha/Beta evidence; do not infer screenshot geometry.
