# pATHENA Alpha/Beta Progress

Evidence-only progress register for `develop/pathena-next`. This file intentionally contains no invented completion percentage.

## Current baseline

- Develop parent before current integration: `98b110882910653566fa70b27e9bdaa3f328ef6b`.
- Exact parent canonical Quality `34724047841 = SUCCESS`.
- Worker heads checked: Errors `493b145af1b31c52a3207484be45039c460e5552`; Spec/Core `6cc6977be39809e464ae62a546312a8217698bc9`; Backend `597297aa1f07d36d872df6e8d20a939a7fab941b`; UI `b3d43e4bcaff1a188668b437d31cb0fffdfc0351`.

## Current integration state

- Durable schedule identity, materialization, recovery and deterministic versioned schedule serialization remain integrated.
- Validated complete WAL+SHM withdrawal remains accepted only with unchanged primary database identity; partial or foreign identity changes remain fail-closed.
- Truthful Knowledge provenance explanation, its transport-neutral API projection, and direct Knowledge revision-change explanation remain integrated.
- Core-Focused candidate selection now limits focused pytest to explicit Core-owned test families instead of every changed unit test. The generic cross-ownership selector is regression-tested against reintroduction.
- Source-free user Knowledge, correction conflict visibility, fail-closed release-readiness assessment and Core-Focused candidate integrity guards remain integrated.

## Exact Worker evidence

- Spec/Core `6cc6977be39809e464ae62a546312a8217698bc9`: Core Focused `34725178727 = FAILURE`; canonical `34725178701 = FAILURE`. Ruff and changed focused tests individually passed before the final focused enforcement step failed, therefore no product slice is promoted from this head.
- Backend `597297aa1f07d36d872df6e8d20a939a7fab941b`: effective delta versus Develop is schedule-startup code/tests; Backend Focused `34725622702 = SUCCESS`; canonical was still in progress at qualification time, so the Backend slice remains held conservatively.
- UI `b3d43e4bcaff1a188668b437d31cb0fffdfc0351`: synchronization head before visual shell work; visual parity remains separately evidence-gated.
- Errors `493b145af1b31c52a3207484be45039c460e5552`: current handoff identifies `ERR-0046` as the Core-Focused ownership selector defect and `ERR-0047` as a Backend schedule-startup test-contract blocker.

## Error and visual truth rules

- `docs/agent_logs/ERROR_LEDGER.md` is historical relative to current Develop and is not the sole authority where newer exact-SHA evidence exists.
- Historical release-guard signatures are not reopened without current exact-SHA reproduction.
- Eleven-screen status remains fail-closed; no visual `MATCH` without opened original reference plus real exact-SHA render.

## Persistent release guards

Do not relax: pypdf packaging; fail-closed Frozen argv; Desktop/Worker two-EXE split; exactly one Desktop instance with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock cluster; duplicate-column/Core-startup/storage-bootstrap signatures; Security/Storage/Recovery guards; test strength; Skip/XFail prohibitions.

## Promotion state

`PROMOTION_READY=NO`

The Core-Focused ownership repair requires exact-current Develop canonical Quality before it is considered integrated-green. Develop becomes Beta/Release-ready only after exact-current canonical Quality plus the known Windows/Packaging/Runtime regression matrix are green.
