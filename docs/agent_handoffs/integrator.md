# pATHENA Feature Integrator Handoff

## Current integration

- Integration target: `develop/pathena-next`.
- Exact Develop parent before this integration: `6a7280ef9847c61c3c3b532c1e3a14068ae14583`.
- Exact canonical Quality on that parent: `34907353758 = SUCCESS`.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.
- `BUNDLED_SLICES=NONE` — one bounded Core slice is selected; Backend remains Recovery-adjacent and is not bundled.

## Iteration — Exhaustive Research transport-neutral API projection

Source head: `52c4592efeeebec7c1ed3d70949a084b3d8c205f`.
Exact evidence: Core Focused `34908178408 = SUCCESS`; canonical Quality `34908178528 = SUCCESS`.

The source branch is one Develop commit behind because `6a7280ef...` integrated the Backend-owned durable Deep verification pipeline after the Core PR base. Worker history is therefore not merged. The independently reviewed bounded extraction is restricted to `src/athena/api/research.py`, `tests/unit/test_api_research.py`, the restrictive Core-focused selector update, and its workflow-contract regression test.

`ResearchApiService` delegates local Exhaustive Research directly to the existing durable `ResearchService.enqueue_local()` boundary and returns only the durable job identity/type/priority/state projection. Query, priority, coverage target, and requested model identity are passed through unchanged. No Research scheduler, repository path, persistence path, transaction path, synthetic provenance, fake result, or parallel Research engine is introduced.

The selector change is a guard strengthening/repair, not a relaxation: `research.py` and `test_api_research.py` become explicit Core-focused trigger/selection paths, and exact worker evidence confirms Ruff, mypy, focused pytest and canonical Quality are green. No Skip/XFail is added.

## Current worker truth at integration time

- Errors: `d081508a572556852099cb8d91c30e05cbd9dc66` — exact handoff refresh only; no selected independent product slice.
- Spec/Core: `52c4592efeeebec7c1ed3d70949a084b3d8c205f` — selected exact-green bounded Research API/qualification slice.
- Backend: `2e42476fdbb276741eed38fbe829e2ad3bbd56a5` — newer Backend candidate exists but is Recovery-adjacent and was not bundled; its exact canonical state must be re-read after this Develop integration.
- UI: `e149515870b773548a164658775159f29de323af` — visual-evidence request lineage; no selected exact-green bounded UI slice.

## Source-of-truth notes

- `ERROR_LEDGER.md` is historical and currently carries no OPEN signature on the exact current Develop baseline; recurrence requires exact-SHA reproduction.
- Eleven-screen visual status remains fail-closed: only slot 01 has opened original-reference pixel evidence, and no screenshot-level `MATCH` may be claimed without a real exact-SHA render and reviewed comparison.
- The Visual Gap Ledger explicitly does not claim screenshot parity.
- Persistent release guards remain mandatory and unchanged.

## Persistent release guards

Retain without relaxation: pypdf packaging; fail-closed Frozen argv; Desktop/Worker two-EXE split; exactly one Desktop instance with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock cluster; duplicate-column/Core-startup/storage-bootstrap signatures; Security/Storage/Recovery guards; no Skip/XFail.

## Promotion state

`PROMOTION_READY=NO`

Require complete canonical Quality `SUCCESS` on the resulting exact Develop SHA before any further Develop mutation.
