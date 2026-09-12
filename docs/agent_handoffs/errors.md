# pATHENA Error Handoff

## Baseline

- Develop: `452547ab46c5d8c678c22c3e1fb9d34652b653fd`.
- Errors worker entered at `9c634dccc829b1a822288afc99ab0339d77efbb1`.
- Current workers: Spec/Core `1f61104959dc6a7d7fcff6051fb013f5f6894706`; Backend `6fcfdf8a71abcabad7e3b4a661ad35ee1f6603f8`; UI `4898bceb9a5af98e1a044eb656714ce03be5e2a4`.
- Develop canonical `34703645964@452547ab46c5d8c678c22c3e1fb9d34652b653fd = IN_PROGRESS`; no competing canonical run started.
- Parent Develop `db159a068a5de1ca8cd302a5ea436f3f07889d9f` has canonical `34700628139 = SUCCESS`.
- `main` and `bnbgrs/ATHENA` remain read-only.

## Current error state

- OPEN: none.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: `ERR-0041`.
- FIXED: `ERR-0040`, `ERR-0035`, `ERR-0033` and prior closed clusters.
- STALE: `ERR-0038`, `ERR-0039` and prior stale clusters.

## Hard progress — ERR-0041 now has exact-green owner canonical evidence

The original reproducer was `postmerge/spec-core@23dc4c79f1e44cd099992eb23636b2c95014c790`, where Ruff `I001` reported `src/athena/knowledge/provenance_explanation.py:3:1`.

The first owner repair at `a35a67f1afe2789d8a568fa3484ef5fe29f46de9` removed that provenance failure; its remaining canonical Ruff errors were separately isolated to release-readiness files.

The superseding current Spec/Core head is now `1f61104959dc6a7d7fcff6051fb013f5f6894706`. It has completed exact-SHA evidence:

- Core Focused Candidate `34701843776 = SUCCESS`;
- canonical Quality `34701843759 = SUCCESS`.

The Integrator handoff records this exact-green bounded provenance slice as READY and integrates it into current Develop `452547ab46c5d8c678c22c3e1fb9d34652b653fd` (`feat(core): integrate knowledge provenance explanation`).

The current Develop canonical Quality `34703645964` is still running. Therefore the owner repair is fully verified, but integrated closure is not yet proven: `ERR-0041` remains `FIXED_PENDING_VERIFY`, not `FIXED`.

## Integrator handoff

- `ERR-0041 = FIXED_PENDING_VERIFY / P1`.
- Superseding owner exact SHA: Spec/Core `1f61104959dc6a7d7fcff6051fb013f5f6894706`.
- Owner evidence: Core Focused Candidate `34701843776 = SUCCESS`; canonical Quality `34701843759 = SUCCESS`.
- Integrated exact SHA: Develop `452547ab46c5d8c678c22c3e1fb9d34652b653fd`.
- Integrated canonical: `34703645964 = IN_PROGRESS` at observation time.
- Closure requires `SUCCESS` on this or a superseding integrated exact Develop SHA carrying the provenance repair.
- Do not reopen historical provenance or release-readiness Ruff failures without a new current exact-SHA reproduction.

## CI discipline

- Errors branch had zero workflow runs before the ledger mutation and again after ledger commit `3737946252e13682a908b466bebb334d17264331` before this handoff mutation.
- No canonical run was started or duplicated by Errors.
- No product code or foreign worker branch was mutated.
- Preserve pypdf packaging, Frozen argv, separate Desktop/Worker EXEs, exactly-one-Desktop bounded-worker topology, adaptive 2048-context reserve, Windows lane-lock mapping, duplicate-column/Core-startup/storage-bootstrap guards, and all Storage/Recovery/Security fail-closed invariants.
