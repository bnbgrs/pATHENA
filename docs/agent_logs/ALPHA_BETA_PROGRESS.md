# pATHENA Alpha/Beta Progress

Evidence-only progress register for `develop/pathena-next`. No invented completion percentage.

## Current baseline

- Develop parent before this integration: `cbe5854e35f6914cc785a2397718f6faff44eb03`.
- Exact canonical Quality on that parent: `34843863295 = SUCCESS`.
- Persistent release guards remain mandatory and unchanged.

## Current integration state

This candidate bundles two independently verified, disjoint bounded slices to reduce Full-Gate idle time without weakening gate discipline.

Core adds deterministic canonical Knowledge supersession planning through the curated relation registry. `superseded_by` is directed Knowledge-to-Knowledge semantics; the planner is persistence-neutral, preserves historical identities, rejects malformed/duplicate/self-supersession inputs and fails closed on registry fallback or semantic drift. Exact source evidence: `7719c3f18de715fe1343980bdc466a2d12cdb286`, Core Focused `34843539383 = SUCCESS`, canonical Quality `34843539369 = SUCCESS`.

Backend adds a scheduler-owned WAL control-housekeeping entrypoint around the existing interval runner. It preserves provider-lane side-effect freedom, injected monotonic-clock behavior, bounded scheduling and existing no-thread/no-retry/no-TRUNCATE constraints. It introduces no schema or migration. Exact source evidence: `8d2b07d4015f34328541ef035a155fd65d13dbf8`, Storage Focused `34844716718 = SUCCESS`, canonical Quality `34844716724 = SUCCESS`.

The two slices share no product/test files and no migration, schema, Security or Recovery prerequisite. Current Develop changes after their compatible bases are outside both slices. A fresh canonical Quality run on the resulting exact Develop SHA is required before any further Develop mutation.

## Current worker truth

- Errors `22d7a2534ff7c256bcf95f9caeb386de4d9c5a61`: classification/documentation only; no separate product slice.
- Spec/Core `7719c3f18de715fe1343980bdc466a2d12cdb286`: supersession slice included in this candidate.
- Backend `8d2b07d4015f34328541ef035a155fd65d13dbf8`: WAL control-housekeeping slice included in this candidate.
- UI `575b8de0a4f25f512e423c78623bfa5b398c379d`: exact canonical Quality was still running at qualification time; not READY for this bundle.

## Error and visual truth rules

- `docs/agent_logs/ERROR_LEDGER.md` is historical wherever newer exact-SHA evidence exists; no historical signature is treated as OPEN without current reproduction.
- Eleven-screen status remains fail-closed. Only slot 01 has direct opened reference evidence. No visual `MATCH` without opened original reference plus a real exact-SHA render and reviewed comparison.
- Verified Send target remains 44×44 outer geometry.

## Persistent release guards

Do not relax: pypdf packaging; fail-closed Frozen argv; Desktop/Worker two-EXE split; exactly one Desktop instance with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock cluster; duplicate-column/Core-startup/storage-bootstrap signatures; Security/Storage/Recovery guards; test strength; Skip/XFail prohibitions.

## Promotion state

`PROMOTION_READY=NO`

Require terminal canonical Quality `SUCCESS` on the resulting exact Develop SHA. After success, reload current worker heads and exact evidence before any subsequent integration.
