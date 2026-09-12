# pATHENA Alpha/Beta Progress

Evidence-only progress register for `develop/pathena-next`. This file intentionally contains no invented completion percentage.

## Current baseline

- Develop parent before the current integration: `d8236b74e69d1eedfdd2b05a52ed767520246671`.
- Exact parent canonical Quality: `34692305368 = SUCCESS`.
- Current worker heads checked:
  - Errors: `531f78037fdb1d6c89e77393b5be0a53a63ac0b3`
  - Spec/Core: `3f864f5dd02db350b8b0df3103e6cc9c09725a37`
  - Backend: `359b675a37b5b59210399bee1506afddc6ccee13`
  - UI: `dd0ad210baf9125d03b532cbac6c807e56e1e558`

## Current integration state

- Durable schedule identity primitives remain integrated on Develop.
- Spec/Core user-correction conflict visibility remains integrated.
- Backend scheduled-job materialization is integrated from exact head `359b675a37b5b59210399bee1506afddc6ccee13`, backed by Backend Focused `34693685313 = SUCCESS` and canonical Quality `34693685375 = SUCCESS`.
- The ERR-0040 fixture root cause is repaired by using a file-backed canonical-schema SQLite fixture; no production journal-mode guard is relaxed.
- UI current head remains unpromoted while its exact canonical/visual evidence is incomplete.

## Error and visual truth rules

- `docs/agent_logs/ERROR_LEDGER.md` is historical relative to current Develop and is not the sole authority for current OPEN state.
- Historical release-guard signatures are not reopened without current exact-SHA reproduction.
- `docs/ui/11_SCREEN_REFERENCE_MANIFEST.md` and `docs/ui/VISUAL_GAP_LEDGER.md` remain fail-closed until an original reference and real exact-SHA render establish a truthful comparison. No `MATCH` is inferred from worker prose or metadata.

## Persistent release guards

Do not relax: pypdf packaging; fail-closed Frozen argv; Desktop/Worker two-EXE split; exactly one Desktop instance with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock cluster; duplicate-column/Core-startup/storage-bootstrap regression signatures; Security/Storage/Recovery guards; test strength; Skip/XFail prohibitions.

## Promotion state

`PROMOTION_READY=NO`

Develop becomes Beta/Release-ready only after exact-current canonical Quality plus the known Windows/Packaging/Runtime regression matrix are green.
