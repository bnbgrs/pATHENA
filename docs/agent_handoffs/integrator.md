# pATHENA Feature Integrator Handoff

## Current integration

- Integration target: `develop/pathena-next`.
- Develop parent before this integration: `cbe5854e35f6914cc785a2397718f6faff44eb03`.
- Exact canonical Quality on that parent: `34843863295 = SUCCESS`.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.
- Bundle policy: two independently exact-SHA-verified, bounded, disjoint slices are combined in one Develop candidate.

## Bundled slices

### Core — canonical Knowledge supersession planning

Source head: `7719c3f18de715fe1343980bdc466a2d12cdb286`.
Exact evidence: Core Focused `34843539383 = SUCCESS`; canonical Quality `34843539369 = SUCCESS`.

The slice extends the curated relation registry with directed `superseded_by` Knowledge-to-Knowledge semantics and adds a persistence-neutral supersession planner. It preserves historical Knowledge identities, rejects empty, duplicate and self-supersession inputs, validates UUID types, and fails closed if the registry falls back or changes the directed semantics. The registry contract test explicitly preserves the no-ad-hoc-ontology-growth invariant.

### Backend — WAL scheduler control-housekeeping entrypoint

Source head: `8d2b07d4015f34328541ef035a155fd65d13dbf8`.
Exact evidence: Storage Focused `34844716718 = SUCCESS`; canonical Quality `34844716724 = SUCCESS`.

The slice exposes `run_control_housekeeping()` on the existing WAL scheduler adapter and preserves the injected monotonic-clock path, provider-lane side-effect freedom, bounded interval gate, and no-thread/no-retry/no-TRUNCATE constraints. No schema, migration, Security or Recovery contract changes are introduced.

## Bundle safety

The Core and Backend slices touch no common product or test files and have no shared migration, schema, Storage/Security/Recovery prerequisite. Core changes are limited to Knowledge relation/supersession policy and tests; Backend changes are limited to the existing WAL scheduler adapter and its focused unit tests. Both exact worker heads have focused and canonical green evidence. Current Develop changes since their compatible bases are PALLAS/UI-test lineage and do not overlap these files.

## Current worker truth at integration time

- Errors: `22d7a2534ff7c256bcf95f9caeb386de4d9c5a61` — supersession-registry regression classification/documentation; no separate product slice selected.
- Spec/Core: `7719c3f18de715fe1343980bdc466a2d12cdb286` — bundled bounded supersession slice.
- Backend: `8d2b07d4015f34328541ef035a155fd65d13dbf8` — bundled bounded WAL control-housekeeping slice.
- UI: `575b8de0a4f25f512e423c78623bfa5b398c379d` — current canonical Quality still in progress at qualification time; not bundled.

## Source-of-truth notes

- `docs/agent_logs/ERROR_LEDGER.md` remains historical wherever newer exact-SHA evidence exists; historical signatures are not OPEN without current reproduction.
- `docs/ui/11_SCREEN_REFERENCE_MANIFEST.md` and `docs/ui/VISUAL_GAP_LEDGER.md` remain fail-closed: no `MATCH` without an opened original reference and a real exact-SHA render. Only slot 01 has direct opened reference evidence; verified Send target remains 44×44 outer geometry.

## Persistent release guards

Retain without relaxation: pypdf packaging; fail-closed Frozen argv; Desktop/Worker two-EXE split; exactly one Desktop instance with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock cluster; duplicate-column/Core-startup/storage-bootstrap signatures; Security/Storage/Recovery guards; no Skip/XFail.

## Promotion state

`PROMOTION_READY=NO`

Require a new complete canonical Quality `SUCCESS` on the resulting exact Develop SHA before any further Develop mutation. If it fails, diagnose only the new exact-SHA regression. If it succeeds, reload all worker heads before selecting the next bounded slice or cross-cutting gap.
