# pATHENA Alpha/Beta Progress

Evidence-only progress register for `develop/pathena-next`. This file intentionally contains no invented completion percentage.

## Current baseline

- Develop parent before the current repair: `146fb7280dbfe30f2bec129aec8ee77f015ce040`.
- Exact parent canonical Quality `34697870543 = FAILURE`, isolated to canonical Ruff. Specification validation, mypy, full pytest, Windows path safety/release guards, Linux storage regressions and local install smoke passed on the same SHA.
- Current worker heads checked:
  - Errors: `e33839260e5582e972aa6e311c9631afbe08fe24`
  - Spec/Core: `a35a67f1afe2789d8a568fa3484ef5fe29f46de9`
  - Backend: `6fcfdf8a71abcabad7e3b4a661ad35ee1f6603f8`
  - UI: `9e9227dc722d7d771ae4ce4e45a75983330fed97`

## Current integration state

- Durable schedule identity primitives and scheduled-job materialization remain integrated on Develop.
- Spec/Core user-correction conflict visibility and source-free user Knowledge remain integrated.
- The fail-closed release-readiness assessment remains integrated and behaviorally unchanged.
- Current repair only normalizes Ruff-sensitive formatting in `src/athena/release_readiness.py` and `tests/unit/test_release_readiness.py`; no worker feature slice is promoted until the repaired exact Develop SHA is canonically verified.

## Worker readiness snapshot

- Errors reports `ERR-0041` on the older Spec/Core provenance-explanation import ordering and correctly leaves the Core-owned mutation to Spec/Core.
- Spec/Core current head contains an owner-side Ruff correction, but Develop repair/reverification takes precedence before any further integration.
- Backend current head carries an equivalent release-readiness formatting normalization; exact Backend Focused Candidate `34700396671 = SUCCESS`, with canonical Quality still in progress at observation time.
- UI current head is synchronized with Develop before further workspace-hierarchy work; no UI product slice is promoted in this repair run.

## Error and visual truth rules

- `docs/agent_logs/ERROR_LEDGER.md` remains historical relative to current Develop and is not the sole authority for current OPEN state.
- Historical release-guard signatures are not reopened without current exact-SHA reproduction.
- `docs/ui/11_SCREEN_REFERENCE_MANIFEST.md` keeps all eleven slots at `IMPLEMENTED_PENDING_VISUAL_REVIEW`; no `MATCH` is inferred without an opened original reference plus a real exact-SHA render.
- `docs/ui/VISUAL_GAP_LEDGER.md` likewise makes no screenshot-level `MATCH` claim.

## Persistent release guards

Do not relax: pypdf packaging; fail-closed Frozen argv; Desktop/Worker two-EXE split; exactly one Desktop instance with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock cluster; duplicate-column/Core-startup/storage-bootstrap regression signatures; Security/Storage/Recovery guards; test strength; Skip/XFail prohibitions.

## Promotion state

`PROMOTION_READY=NO`

Develop becomes Beta/Release-ready only after exact-current canonical Quality plus the known Windows/Packaging/Runtime regression matrix are green.
