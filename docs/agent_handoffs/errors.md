# Error worker handoff

## Exact source of truth

- Develop: `5024a7c2b60c80083d1650ae924c89cb3085019e`; canonical `34815625453 = IN_PROGRESS`.
- Error worker before this handoff commit: `35871d5e32dd49306b433374de9b2693048eb24f`; canonical `34812544236 = FAILURE`, but Storage, Windows release guards including pypdf, Local Install, validator, Ruff and mypy are green. The red pytest remains inherited stale UI geometry, not a new Error-owned release/storage root cause.
- Spec/Core: `ae82147ab8de6d3805bb5f2299497296af8ff19f`; keep closed absent a new exact matching failure.
- Backend: `52eb61de9ecfde4074778a1bab2966e18aab526d`; keep closed absent a new exact matching failure.
- UI: `ec05db2214680cbfb4c5112d7b42c24e389c7ea6`; exact Visual `34816280825 = FAILURE` during native capture; canonical `34816284933 = IN_PROGRESS`.

## ERR-0063 — OPEN — UI capture still fails before eleven surfaces

Exact Visual `34816280825` passes visual-harness Ruff, comparator mypy/tests, hierarchy-token and navigation-accessibility checks, then fails at `Capture exactly eleven canonical surfaces with native fonts`. Route-identity verification, baseline compare/proposal and final verdict are skipped. The current UI commit changes manifest reporting only, so it does not close the route/capture root cause.

Ownership stays with UI. Error worker must not patch UI product code in parallel. Closure requires a real seven-route capture followed by all eleven surfaces, with the existing route identity guard intact.

## ERR-0059 — FIXED_PENDING_VERIFY — bounded fix now on current UI successor

Current UI commit `ec05db2214680cbfb4c5112d7b42c24e389c7ea6` changes the manifest to derive `captured_reference_surfaces` from the real `captures` and `captured_reference_count` from `len(captures)`, preserving `assigned_reference_count = 11`. This is the exact bounded fix requested and matches the already-fixed Error/Develop lineage.

The exact Visual run executed this SHA and uploaded `pathena-visual-ec05db2214680cbfb4c5112d7b42c24e389c7ea6`, but the binary artifact manifest was not directly inspected in this run. Because capture still aborts on `ERR-0063`, keep `ERR-0059` at `FIXED_PENDING_VERIFY`, not `FIXED`, until exact artifact evidence proves truthful partial-capture metadata and the unchanged fail-closed eleven-capture PASS contract.

## ERR-0054 — BLOCKED — UI/Visual Review

Visual review cannot truthfully proceed while `ERR-0063` prevents eleven exact renders. No Error-worker baseline creation or acceptance. After capture is technically complete, UI/Visual Review must open all eleven reference/render pairs and obtain final-verdict success.

## Green / held clusters

- Spec/Core remains held closed absent new exact matching evidence.
- Backend remains held closed absent new exact matching evidence.
- Develop current integration candidate is running and must not be superseded.
- Persistent pypdf/Frozen-argv/two-EXE/bounded-worker/adaptive-2048/lane-lock/duplicate-column/Core-startup/storage-bootstrap guards remain unchanged.
- Error-worker 48px Send geometry remains `STALE`, not a new product root cause.

## Next root cause

1. Consume Develop `34815625453` terminal result.
2. UI closes `ERR-0063` without weakening route identity.
3. Inspect exact UI manifest evidence and close `ERR-0059` only after truthful partial/full capture metadata is proven.
4. Only after truthful eleven-surface capture does `ERR-0054` return to active visual-review ownership.
