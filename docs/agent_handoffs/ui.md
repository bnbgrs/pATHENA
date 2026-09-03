# pATHENA UI Handoff

## Current baseline

- Base: `develop/pathena-next@dd4b623cc7bbc5b5a24c4427382f0b98ff50ad02`
- Worker: `postmerge/ui`
- History-preserving NON-FORCE synchronization commit: `0413ae80d20e1488aeb1fba490bbfd19dee5c433`
- UI product candidate retained: `99d6b31c78be2932154137a6527200759f349628`
- Ruff harness correction: `77e7b4c7d95202e6814226e2b4a2c4a54e3f5c8e`
- Evidence updates: ledger `00ec6e7257b23681f780033c7fb046a9ce795ce2`; manifest `e91b1dd10bf6eb295980406012bcfde63a7d1a98`.
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

## Exact failure diagnosis and correction

Canonical Quality run `33785726577` on synchronized lineage `b76115748aed53e3502a71eef10a41b11f97f8ae` completed with Windows path safety, Linux storage, local-install smoke, specification validator, mypy and full pytest passing. Ruff alone failed.

The uploaded canonical diagnostics identify the exact failure as `B010` in `tests/unit/test_pathena_startup_experience_2900.py:61`: `setattr(window, "_core_transport_ready", False)` used a constant attribute name.

Commit `77e7b4c7d95202e6814226e2b4a2c4a54e3f5c8e` fixes only that harness defect by using `_DisconnectedStartupWindow`, a test-only `QWidget` subclass whose `_core_transport_ready` class attribute is `False`. This preserves the exact disconnected-state behavior exercised by `PathenaStartupExperience.sync()` and does not suppress Ruff/mypy, weaken assertions, change product code or alter backend/storage/security semantics.

A new ATHENA Quality Gate was automatically started for the corrected lineage. Because subsequent ledger/manifest/handoff documentation commits are behavior-neutral descendants, the final branch-head Quality result is the integration evidence to consume. Until that exact final worker-head run is green, UI-GAP-0004 remains `FIXED_PENDING_VERIFY`.

## Synchronization state

Develop was one documentation commit ahead of the prior UI worker. The current Integrator handoff blob was first carried onto UI, then merge commit `0413ae80d20e1488aeb1fba490bbfd19dee5c433` recorded both UI and `develop/pathena-next@dd4b623cc7bbc5b5a24c4427382f0b98ff50ad02` as parents. The worker ref was advanced NON-FORCE. No UI product/test blob was overwritten by synchronization.

## Collision / ownership guidance

- Core: normal-Hybrid Search composition remains Core-owned; no overlap.
- Backend: ExternalAccessGateway runtime-boundary hardening remains Backend-owned; no overlap.
- Error: `ERR-0004` corresponds to this Ruff harness failure; UI owns the correction in the active test file. Error should verify/close it from exact successful evidence rather than create a competing mutation.
- Preserve contextual Evidence & Activity behavior and PALLAS lifecycle fixes already integrated.

## Integrator handoff

Do not integrate UI-GAP-0004 as READY until canonical Quality completes successfully on the exact final `postmerge/ui` head containing `77e7b4c7...` plus only the documented synchronization/evidence commits. If green, independently review the bounded product/test diff and integrate only to `develop/pathena-next`. No visual `MATCH` is implied.

## Next UI work

1. Consume the exact final-head Quality result; if any stage fails, fix the exact current-lineage cause before taking another product slice.
2. If green, mark UI-GAP-0004 technically `FIXED` and hand the exact worker SHA to Integrator/Error.
3. Retry access to the actual eleven references and render Screen 11 for direct comparison. If reference pixels remain unavailable, select the next gap only from explicit versioned UI/Alpha/Beta evidence; do not infer screenshot geometry.
