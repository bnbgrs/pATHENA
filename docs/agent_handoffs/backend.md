# pATHENA Backend & Systems Handoff

## Baseline
- Shared baseline: `develop/pathena-next@f0a0272e564b483f91099846c2644006298dc6a4`.
- Worker branch: `postmerge/backend`.
- History-preserving NON-FORCE synchronization: `91d4f94653f4e3b142010bf24ab07fa61a26de32`, parents prior Backend `a6b3e0d7b185fd08a851b0b3f05127d66428697b` + exact Develop `f0a0272e564b483f91099846c2644006298dc6a4`.
- `main` and `bnbgrs/ATHENA` remain read-only.

## Verified predecessor
- Journal-mode exact-status-shape worker head `a6b3e0d7b185fd08a851b0b3f05127d66428697b` passed canonical ATHENA Quality Gate `34045619981 = success`.
- ExternalAccessGateway runtime-boundary lineage remains previously verified exact-green.

## Current slice
Area: Storage / Recovery / migration user_version status shape.

Product `cc333c33a8c828b205599b470422c69544368002` requires `PRAGMA user_version` to return exactly one status field before schema-version acceptance. Previously malformed multi-field runtime status could be accepted because only `row[0]` was inspected.

Focused regression `ab6b61a75fc4dab856c40cbab0f8f089a9b305d0` covers empty and two-field user_version rows, proves rejection before WAL checkpoint side effects, and retains the canonical single-field schema-version path.

## Invariants
- candidate-only migration; live DB untouched;
- absolute regular non-link candidate and safe ancestry required;
- exact non-bool integer PRAGMA values retained;
- user_version status exactly one field;
- WAL checkpoint status exactly three fields;
- WAL frame counters non-negative and complete checkpoint required;
- journal-mode status exactly one field and text `delete` required;
- sidecar-free activation handoff retained;
- no Security/TOR/Provider/UI semantics, retries, cryptography, schema representation or WAL format changes.

## Coordination
- Error worker reports `ERR-0018` OPEN and Core-owned: Ruff I001 in `src/athena/memory/context.py`; no Backend semantic/runtime defect is implicated.
- Spec/Core corrected head observed: `e8f7199f70c56a79403026926430ea56a5177bec`.
- UI head observed: `550eb74508f7d1cbd4771a41ace283b11ea30fdb`.
- Integrator/Develop: `f0a0272e564b483f91099846c2644006298dc6a4`.

## Integrator handoff
READY: journal-mode exact-status-shape lineage `a6b3e0d7b185fd08a851b0b3f05127d66428697b` / Quality `34045619981 = success`.

NOT READY: user_version exact-status-shape product `cc333c33a8c828b205599b470422c69544368002` + regression `ab6b61a75fc4dab856c40cbab0f8f089a9b305d0` pending exact canonical completion.

## Persistent release regression knowledge
Retain without reopening absent exact-current reproduction: Windows pypdf metadata; fail-closed frozen child argv; two-EXE Desktop/Worker split; exactly one Desktop with bounded workers; adaptive small-context DirectChat reserve; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; duplicate `source_processing_job_id`; Core startup failure; storage-bootstrap startup failure.

## Next backend slice
Consume the first exact canonical Quality containing `ab6b61a75fc4dab856c40cbab0f8f089a9b305d0` or this documentation descendant. If green, promote only the user_version exact-status-shape slice and continue to the highest current unclaimed disjoint Backend/System gap. If red, repair only the smallest Backend-owned primary failure without weakening Storage/Recovery, ExternalAccessGateway, persistence, provenance or platform invariants. If cancelled, do not repeat unchanged; use another executable verification route or a distinct real Backend/System slice.
