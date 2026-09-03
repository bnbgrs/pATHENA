# pATHENA UI Handoff

## Current baseline

- Current integration target: `develop/pathena-next@647ea036329280378a7e573aca0df905f48ac3b1`.
- Worker: `postmerge/ui`.
- UI-GAP-0004 product candidate: `99d6b31c78be2932154137a6527200759f349628`.
- B010 harness correction: `77e7b4c7d95202e6814226e2b4a2c4a54e3f5c8e`.
- Final I001 harness correction: `a5d9530525bd0b6bf0eae3945c23a6805f6b9669`.
- Original eleven reference images: `VISUAL_REFERENCE_PENDING`; no pixel-level parity or `MATCH` claim is made.

## UI-GAP-0004 — Startup/readiness infrastructure copy

Status: `FIXED`, P1, Screen 11, technically verified and Integrator-ready.

Spec anchor: `docs/alpha/16_Desktop_Anwendung_und_Benutzeroberflaeche.md` requires normal use to present pATHENA while daemon/workers/providers remain background infrastructure.

The product candidate changes presentation only:

- `Local core offline` -> `pATHENA reconnecting`.
- `Waiting for the local core` -> `Getting pATHENA ready`.
- Core-specific normal-workspace tooltips/placeholders become pATHENA/model-level guidance.
- `OfflineComprehensionController` continues to expose the truthful internal `core-offline` readiness state.
- reconnect, provider, transport, persistence, recovery and security semantics remain unchanged.

Focused assertions remain in `tests/unit/test_pathena_startup_experience_2900.py` and `tests/unit/test_pathena_offline_comprehension.py`.

## Exact verification chain

1. Quality run `33785726577` isolated Ruff B010 at the startup harness after all other required stages and full pytest passed.
2. `77e7b4c7d95202e6814226e2b4a2c4a54e3f5c8e` fixed B010 with a typed disconnected startup-window subclass; assertions/product behavior remained unchanged.
3. Quality run `33792012599` then isolated Ruff I001 in the same harness while Windows path safety, Linux storage, local-install smoke, validator, mypy and full pytest (`4492 passed`, three existing Windows-specific skips) passed.
4. The multiline-only import formatting attempt `ecbf44ddd0fb8c7428d4cca090834eca284b997e` did not fully satisfy Ruff ordering.
5. Final correction `a5d9530525bd0b6bf0eae3945c23a6805f6b9669` orders the SCREAMING_SNAKE_CASE QtWidgets symbol before CamelCase as Ruff/isort requires.
6. Focused validation run `33804104455` passed dependency-lock validation, Ruff on both affected harnesses and both required startup/offline pytest files.
7. Canonical Quality run `33804193396` completed `success` on the byte-identical retained product/test tree after temporary validation-workflow cleanup. Python 3.12 quality, specification validator, Ruff, mypy, full pytest, Windows path safety, Linux storage regressions, local-install smoke and canonical enforcement all passed.

UI-GAP-0004 is therefore technically `FIXED`. The remaining Screen 11 status is only `IMPLEMENTED_PENDING_VISUAL_REVIEW` because the original reference pixels are unavailable.

## Integrator / Error handoff

- Integrator: UI-GAP-0004 is READY for bounded integration to `develop/pathena-next`. Independently review and integrate only the product/test lineage through final harness commit `a5d9530525bd0b6bf0eae3945c23a6805f6b9669`; temporary validation-workflow commits are cleanup-only and must not be promoted as product functionality.
- Error: `ERR-0004` can now be closed from canonical Quality run `33804193396`; both the original B010 and follow-up I001 harness defects are gone on the verified candidate tree.
- Core: no overlap with Core-owned Search/Chat/Knowledge/Research/PALLAS product semantics.
- Backend: no overlap with Backend-owned ExternalAccessGateway/system hardening.

## Next UI work

The eleven slots currently have no remaining evidence-backed technical gap in this ledger; every slot is `IMPLEMENTED_PENDING_VISUAL_REVIEW`, never `MATCH`. The next mutation must therefore come from one of two evidence sources only:

1. actual original reference pixels plus a real rendered current build, yielding a concrete `STRUCTURE|HIERARCHY|SPACING|TYPOGRAPHY|COLOR|CONTROL|STATE|INTERACTION|ACCESSIBILITY|RESPONSIVE` gap; or
2. a new explicit Alpha/Beta/UI contract mismatch traced against current code/tests.

Until image access exists, continue with explicit spec/code tracing for the next real UI gap; do not manufacture screenshot geometry or decorative work.
