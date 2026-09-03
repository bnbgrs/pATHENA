# pATHENA UI Handoff

## Current baseline

- Base: `develop/pathena-next@1dc2da1bd38e6147d01d3b1d6833ea1ea6a0e37b`
- Worker: `postmerge/ui`
- Worker synchronization commit: `0d87382f31bc9ff3985b35d9004b1658a9c105c2`
- Current UI candidate: `99d6b31c78be2932154137a6527200759f349628`
- Original eleven reference images: `VISUAL_REFERENCE_PENDING`; no pixel-level parity or `MATCH` claim is made.

## Current slice

### UI-GAP-0004 — Startup/readiness infrastructure copy

Status: `FIXED_PENDING_VERIFY`, P1, Screen 11.

Spec anchor: `docs/alpha/16_Desktop_Anwendung_und_Benutzeroberflaeche.md` requires normal use to present pATHENA while daemon/workers/providers remain background infrastructure. The real startup/readiness chain exposed local-Core implementation terminology in `localStatus`, the composer guidance and the disconnected empty-state title.

Candidate `99d6b31c78be2932154137a6527200759f349628` changes presentation only:

- `Local core offline` -> `pATHENA reconnecting`.
- `Waiting for the local core` -> `Getting pATHENA ready`.
- Core-specific normal-workspace tooltips/placeholders become pATHENA/model-level guidance.
- `OfflineComprehensionController` continues to expose the truthful internal `core-offline` readiness state and refreshes user-facing copy without changing reconnect, provider, model, transport, persistence or security behavior.
- Technical recovery detail remains available through System-oriented next steps.

Focused assertions were added to `tests/unit/test_pathena_startup_experience_2900.py` and `tests/unit/test_pathena_offline_comprehension.py` for the new presentation contract. No exact-SHA execution is claimed: there is currently no workflow run associated with candidate `99d6b31...`, and local repository checkout remains unavailable in this tool path. Keep the gap `FIXED_PENDING_VERIFY` until these Qt suites actually pass.

## Collision / ownership guidance

- Core: normal-Hybrid Search composition remains Core-owned; no overlap.
- Backend: ExternalAccessGateway runtime-boundary hardening remains Backend-owned; no overlap.
- Error: no new reproduced defect was created or assigned in this slice; preserve the integrated contextual Evidence & Activity contract.
- UI owns only presentation copy/state hierarchy here. No controller availability decision, backend semantics or recovery rule was changed.

## Integrator handoff

Do not integrate `99d6b31c78be2932154137a6527200759f349628` as READY until at minimum `tests/unit/test_pathena_startup_experience_2900.py` and `tests/unit/test_pathena_offline_comprehension.py` execute successfully on the exact candidate lineage. Then run the relevant desktop/UI regressions or canonical Quality as available. The preceding `0d87382f...` is synchronization only.

## Next UI work

First verify UI-GAP-0004. After verification, retry opening the actual eleven references and render Screen 11 for direct comparison. If reference pixels remain unavailable, select the next gap only from explicit versioned UI/Alpha/Beta evidence; do not infer screenshot geometry or claim `MATCH`.
