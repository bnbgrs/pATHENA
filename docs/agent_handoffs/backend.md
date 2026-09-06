# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline reviewed: `develop/pathena-next@208efc473cbcbb30f7af08a2e5e1dc6956c557ce`.
- Worker branch: `postmerge/backend`.
- Prior worker `1509167f4458df90884697bea973f45fd57ceafc` passed canonical ATHENA Quality Gate `34064067226 = success`.
- History-preserving NON-FORCE synchronization onto exact current Develop: `a1a1b5095527fe3e0fe9206980d03829f2e2ce65`, parents prior Backend `1509167f4458df90884697bea973f45fd57ceafc` + exact Develop `208efc473cbcbb30f7af08a2e5e1dc6956c557ce`.
- Sync tree equals exact Develop; no foreign-worker product delta was overwritten. `main` and `bnbgrs/ATHENA` remain untouched.

## Verified predecessor

- ExternalAccessGateway runtime boundaries remain exact-green at `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6` / Quality `33884210684 = success`.
- The Develop-compatible `WalRuntimeStatus.autocheckpoint_bytes` true-int boundary is integrated on Develop and prior Backend handoff `1509167f4458df90884697bea973f45fd57ceafc` passed Quality `34064067226 = success`.

## Current bounded Backend slice

Area: Storage/WAL maintenance diagnosis runtime boundary.

Product commit `04582fdb6f1d2f27582f9d6f6afde909e3377195` hardens `WalMaintenanceDiagnosis.__post_init__()` so malformed runtime diagnosis levels, including unhashable/non-text values, fail deterministically with the existing invalid-level boundary instead of leaking a Python container/hash error, and `cycle` must be an actual `WalMaintenanceCycle` before diagnosis consumers observe it.

Focused regression commit `5aafb48244c9bea1906044fb13c557c924ce8f83` adds `tests/unit/test_wal_maintenance_diagnosis_boundaries.py` covering unhashable/non-text/unknown levels, non-cycle payload rejection, and canonical diagnosis acceptance.

## Call chain / invariants

`WalMaintenanceOrchestrator.run_cycle() -> WalMaintenanceDiagnosis(...) -> exact diagnosis-level runtime boundary -> exact WalMaintenanceCycle runtime boundary -> nonnegative blocked/growth counters -> requires_attention`.

Retained invariants:

- PASSIVE remains the only automatic checkpoint mode; TRUNCATE still requires explicit idle confirmation.
- WAL files are never manually deleted.
- WAL observation remains no-follow, regular-file and handle/path-identity checked.
- page size, autocheckpoint pages and derived autocheckpoint bytes remain positive genuine non-bool integers.
- checkpoint result remains exact three fields with bounded busy value and non-negative frame counters.
- no migration/schema/transaction/Provider/TOR/Security/UI/retry/cryptography/process-tree semantics changed.
- no Skip/XFail, guard weakening, force update, history rewrite or `main` mutation.

## Coordination reviewed

- Errors: `postmerge/errors@5f2bf47b9a63d03d3558528fe373f5629fbf9d81`; OPEN/BLOCKED none, ERR-0018 closed on exact canonical evidence.
- Spec/Core: `postmerge/spec-core@09341777eb56a77abf247190707b2cb189570a1b`; Search facade/application composition remains Core-owned and disjoint.
- UI: `postmerge/ui@a9c17d91f1c332e3ef0d9950dd858a5f8d7d7f3f`; startup accessibility work remains UI-owned and disjoint.
- Integrator/Develop: `208efc473cbcbb30f7af08a2e5e1dc6956c557ce`; it records the verified WAL byte-boundary integration.

## Verification state

- Verified predecessor: Quality `34064067226 = success` at exact Backend SHA `1509167f4458df90884697bea973f45fd57ceafc`.
- Current focused product/test head: `5aafb48244c9bea1906044fb13c557c924ce8f83`.
- Canonical Quality `34067049868` was created for that exact SHA and was pending at handoff time; no PASS is claimed for the new diagnosis slice until an exact completed run or descendant succeeds.

## Persistent release regression knowledge

Retain without reopening absent exact-current reproduction: Windows pypdf metadata; fail-closed frozen child argv; two-EXE Desktop/Worker split; exactly one Desktop with bounded workers; adaptive small-context DirectChat reserve; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; duplicate `source_processing_job_id`; Core startup failure; storage-bootstrap startup failure.

## Integrator handoff

READY predecessor: ExternalAccessGateway runtime boundaries and the Develop-compatible WAL byte runtime boundary are exact-green.

NOT READY current slice: `04582fdb6f1d2f27582f9d6f6afde909e3377195` + `5aafb48244c9bea1906044fb13c557c924ce8f83` until canonical Quality succeeds on the exact candidate or this documentation descendant.

## Next backend slice

Consume the exact canonical result for the diagnosis-boundary candidate/descendant. If green, promote only this bounded Storage/WAL diagnosis runtime boundary and re-trace current Alpha/Beta/source contracts for the highest unclaimed disjoint Backend/System P1/P2 gap. If red, isolate and minimally repair only the exact Backend-owned primary failure without weakening WAL, Storage/Recovery, ExternalAccessGateway, persistence, provenance or Windows runtime invariants. If cancelled, do not repeat unchanged; use another executable verification route or a distinct evidence-backed Backend/System slice.
