# pATHENA Backend & Systems Handoff

## Baseline
- Shared baseline: `develop/pathena-next@8b6c7a2f44104675570152a5b44fa65979493bc9`.
- Worker branch: `postmerge/backend`.
- History-preserving NON-FORCE synchronization: `93d410ad371756a40148a1db0d0c6672bed6d832`, parents prior Backend `77ce30acb409881e00f12a9ab78655b81b0cdd1e` + exact Develop `8b6c7a2f44104675570152a5b44fa65979493bc9`.
- `main` and `bnbgrs/ATHENA` remain read-only.

## Verified predecessor
- Checkpoint busy-domain worker head `77ce30acb409881e00f12a9ab78655b81b0cdd1e` passed canonical ATHENA Quality Gate `34052064954 = success`.
- ExternalAccessGateway exact runtime-type boundary lineage remains exact-green at `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6` / Quality `33884210684`.

## Current slice
Area: Storage / WAL Maintenance / runtime policy status-shape boundary (`BE-053`).

Product `76cda6717b15784d7d6722e07f0775179577c6eb` now requires both `PRAGMA page_size` and `PRAGMA wal_autocheckpoint` observations to return exactly one status field before either value is indexed or the WAL file is observed. Previously `None` was rejected, but empty rows could leak `IndexError` and oversized rows were silently accepted while trailing runtime status was ignored.

Focused regression `978d67958bddf0e4e3a72f4b5bc2220146242a1f` covers `None`, empty, and multi-field rows for both policy PRAGMAs, proves malformed status fails through `WalMaintenanceError` before `_bounded_wal_size`, and retains canonical one-field `4096`/`1000` behavior.

## Invariants
- PASSIVE remains the only automatic checkpoint mode; TRUNCATE still requires explicit idle confirmation;
- WAL files are never manually deleted;
- WAL size observation remains no-follow, regular-file and handle/path-identity checked;
- page size and autocheckpoint values remain true positive non-bool integers;
- checkpoint result remains exact three fields with busy in `{0,1}` and non-negative frame counters;
- no transaction, migration, schema, Security/TOR/Provider/UI, retry, cryptography or Windows process-tree semantics changed;
- ExternalAccessGateway runtime boundaries remain unchanged.

## Coordination
- Error worker head `410bdc595d3f4c370541b0701386cfe4b4b880ce` still tracks only Core-owned `ERR-0018` Ruff import ordering; no Backend defect is implicated.
- Spec/Core head reviewed: `942d19f46a91af6672bb7639c1fca4cadf378ac7`.
- UI head reviewed: `59b2046d5e127664195f7ecf17245c45f70f00ca`.
- Integrator/Develop baseline: `8b6c7a2f44104675570152a5b44fa65979493bc9`.
- No Core/UI-owned file was modified.

## Integrator handoff
READY: checkpoint busy-domain lineage `77ce30acb409881e00f12a9ab78655b81b0cdd1e` / Quality `34052064954 = success`.

NOT READY: WAL policy exact-status-shape product `76cda6717b15784d7d6722e07f0775179577c6eb` + regression `978d67958bddf0e4e3a72f4b5bc2220146242a1f`; Quality `34055278060` was pending on the exact test head when this handoff was written. Require an exact successful descendant before integration.

## Persistent release regression knowledge
Retain without reopening absent exact-current reproduction: Windows pypdf metadata; fail-closed frozen child argv; two-EXE Desktop/Worker split; exactly one Desktop with bounded workers; adaptive small-context DirectChat reserve; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; duplicate `source_processing_job_id`; Core startup failure; storage-bootstrap startup failure.

## Next backend slice
Consume the first exact canonical Quality containing `978d67958bddf0e4e3a72f4b5bc2220146242a1f` or this documentation descendant. If green, promote only the WAL policy status-shape boundary and continue `BE-053` only with a separately evidenced orchestration/diagnosis gap or move to the highest current disjoint Backend/System P1/P2 gap. If red, repair only the smallest Backend-owned primary failure without weakening WAL, Storage/Recovery, ExternalAccessGateway, persistence, provenance or platform invariants. If cancelled, do not repeat unchanged; use another executable verification route or a distinct real Backend/System slice.
