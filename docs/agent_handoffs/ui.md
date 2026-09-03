# pATHENA UI Handoff

## Current baseline

- Base: `develop/pathena-next@f76911dfef6530041d62fb6c2e0ddec242d64231`
- Worker: `postmerge/ui`
- Worker synchronization commit: `b76115748aed53e3502a71eef10a41b11f97f8ae`
- UI product candidate retained unchanged: `99d6b31c78be2932154137a6527200759f349628`
- Original eleven reference images: `VISUAL_REFERENCE_PENDING`; no pixel-level parity or `MATCH` claim is made.

## Current slice

### UI-GAP-0004 — Startup/readiness infrastructure copy

Status: `FIXED_PENDING_VERIFY`, P1, Screen 11.

Spec anchor: `docs/alpha/16_Desktop_Anwendung_und_Benutzeroberflaeche.md` requires normal use to present pATHENA while daemon/workers/providers remain background infrastructure.

Candidate `99d6b31c78be2932154137a6527200759f349628` changes presentation only:

- `Local core offline` -> `pATHENA reconnecting`.
- `Waiting for the local core` -> `Getting pATHENA ready`.
- Core-specific normal-workspace tooltips/placeholders become pATHENA/model-level guidance.
- `OfflineComprehensionController` continues to expose the truthful internal `core-offline` readiness state.
- reconnect, provider, transport, persistence, recovery and security semantics remain unchanged.

Focused assertions remain in `tests/unit/test_pathena_startup_experience_2900.py` and `tests/unit/test_pathena_offline_comprehension.py`.

## Synchronization / verification state

`postmerge/ui` had diverged only because Develop added `docs/agent_handoffs/integrator.md` and `docs/development/ALPHA_BETA_PROGRESS.md`. Those exact Develop blobs were merged history-preservingly and NON-FORCE in `b76115748aed53e3502a71eef10a41b11f97f8ae`; no UI/product/test blob was altered by the synchronization.

ATHENA Quality Gate run `33785726577` is SHA-bound to `b76115748aed53e3502a71eef10a41b11f97f8ae` and is currently in progress. Its Python 3.12 quality job includes canonical pytest after validator/Ruff/mypy. Until that run completes successfully, UI-GAP-0004 remains `FIXED_PENDING_VERIFY`; an in-progress run is not PASS evidence.

## Collision / ownership guidance

- Core: normal-Hybrid Search composition remains Core-owned; no overlap.
- Backend: ExternalAccessGateway runtime-boundary hardening remains Backend-owned; no overlap.
- Error: no reproduced defect is assigned in this slice; preserve contextual Evidence & Activity behavior.
- UI owns only presentation copy/state hierarchy here.

## Integrator handoff

Do not integrate UI-GAP-0004 as READY until Quality run `33785726577` completes successfully on `b76115748aed53e3502a71eef10a41b11f97f8ae` (or equivalent exact-lineage focused verification). If green, candidate `99d6b31...` is covered unchanged by the synchronized worker lineage. No visual `MATCH` is implied.

## Next UI work

First resolve the running verification for UI-GAP-0004. Then retry access to the actual eleven references and render Screen 11 for direct comparison. If reference pixels remain unavailable, select the next gap only from explicit versioned UI/Alpha/Beta evidence; do not infer screenshot geometry.
