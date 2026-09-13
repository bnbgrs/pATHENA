# pATHENA Alpha/Beta Progress

Evidence-only progress register for `develop/pathena-next`. This file intentionally contains no invented completion percentage.

## Current baseline

- Develop parent before current integration: `305703362d539ed467dec27cbc7300a495b3ca03`.
- Exact parent canonical Quality `34728645613 = SUCCESS`.
- Worker heads checked: Errors `4d56cdbde52af238917568948daf86bd7c112930`; Spec/Core `78d51621cbdfa3282cd236b5d0c7f5984abedcae`; Backend `a709c229d6994c159490c2c1eaf3f2549f12cf56`; UI `031f291bbbb215e6319bb30e7aed92768e6aac18`.

## Current integration state

- Durable schedule identity/materialization/recovery and deterministic versioned schedule serialization remain integrated.
- SQLite startup identity remains fail-closed for partial or foreign sidecar changes; Backend's newer complete-sidecar rotation work is not yet integrated because its exact canonical gate was still active at qualification time.
- Truthful Knowledge provenance explanation, transport-neutral current-revision explanation API, adjacent revision-change explanation and Knowledge revision-history projection are integrated.
- Revision-change wording now distinguishes an unsupplied reason from a persisted reason proven unavailable.
- Core-Focused candidate selection remains restricted to Core-owned focused test families with its regression guard intact.

## Exact Worker evidence

- Spec/Core `78d51621cbdfa3282cd236b5d0c7f5984abedcae`: Core Focused `34730134596 = SUCCESS`; canonical Quality `34730134589 = SUCCESS`; effective delta versus Develop is four Knowledge product/test files and is selected for integration.
- Backend `a709c229d6994c159490c2c1eaf3f2549f12cf56`: effective delta versus Develop is schedule-startup code/tests plus SQLite startup-identity hardening; Storage Focused is green, canonical Quality `34730587873` was still in progress at qualification time. Conservative hold.
- UI `031f291bbbb215e6319bb30e7aed92768e6aac18`: broad UI/render/evidence delta also removes Core-owned orphan Knowledge files; no broad promotion.
- Errors `4d56cdbde52af238917568948daf86bd7c112930`: current diagnostic handoff supersedes the historical repository Error Ledger where exact-SHA evidence differs.

## Error and visual truth rules

- `docs/agent_logs/ERROR_LEDGER.md` remains historical relative to current Develop; historical signatures are not reopened without current reproduction.
- Eleven-screen status remains fail-closed; no visual `MATCH` without opened original reference plus real exact-SHA render.

## Persistent release guards

Do not relax: pypdf packaging; fail-closed Frozen argv; Desktop/Worker two-EXE split; exactly one Desktop instance with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock cluster; duplicate-column/Core-startup/storage-bootstrap signatures; Security/Storage/Recovery guards; test strength; Skip/XFail prohibitions.

## Promotion state

`PROMOTION_READY=NO`

The newly integrated Knowledge history/reason-truth slices require exact-current Develop canonical Quality before they are integrated-green. Develop becomes Beta/Release-ready only after exact-current canonical Quality plus the known Windows/Packaging/Runtime regression matrix are green.
