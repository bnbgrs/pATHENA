# pATHENA Alpha/Beta Progress

Evidence-only progress register for `develop/pathena-next`. This file intentionally contains no invented completion percentage.

## Current baseline

- Develop SHA: `63423bccaf9bf5b4049e55998e2d3303f59ecaf7`
- Exact canonical Quality: `34687050578 = SUCCESS`
- Current worker heads checked in this integrator run:
  - Errors: `23b0c22e2b219fd28a44feb94296c883fab75327`
  - Spec/Core: `008345141aac276f9723b536a70497e2dec74b20`
  - Backend: `38a61d5f6b41bd151c3662bd1ef2a5a35f240a87`
  - UI: `51c109f6a0e31f82392be6c5bfe1d7d167377499`

## Current integration state

- Durable schedule identity primitives are integrated on Develop.
- Spec/Core exact focused candidate on `008345141aac276f9723b536a70497e2dec74b20` is green, but exact canonical Quality remains in progress; not READY yet.
- Backend exact focused candidate on `38a61d5f6b41bd151c3662bd1ef2a5a35f240a87` is green, but exact canonical Quality is failed; not READY.
- UI exact focused and canonical Quality on `51c109f6a0e31f82392be6c5bfe1d7d167377499` are green, but the worker is heavily diverged from current Develop and exact visual regression is failed; no bounded promotion is asserted from that head.

## Error and visual truth rules

- `docs/agent_logs/ERROR_LEDGER.md` is historical relative to the current Develop SHA and is not the sole authority for current OPEN state.
- Historical release-guard signatures are not reopened without current reproduction.
- Eleven-screen visual status remains fail-closed until an original reference and real exact-SHA render establish a truthful comparison. No `MATCH` is inferred from worker prose or metadata.

## Persistent release guards

Do not relax: pypdf packaging; fail-closed Frozen argv; Desktop/Worker two-EXE split; exactly one Desktop instance with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock cluster; duplicate-column/Core-startup/storage-bootstrap regression signatures; Security/Storage/Recovery guards; test strength; Skip/XFail prohibitions.

## Promotion state

`PROMOTION_READY=NO`

Develop becomes Beta/Release-ready only after exact-current canonical Quality plus the known Windows/Packaging/Runtime regression matrix are green.
