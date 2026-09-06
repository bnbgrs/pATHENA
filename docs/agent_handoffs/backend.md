# pATHENA Backend & Systems Handoff

## Baseline
- Shared baseline reviewed: `develop/pathena-next@1cc7b8dceb5b4ff098442e9f17f89b8cc36cb390`.
- Worker branch: `postmerge/backend`.
- Prior worker `2ea98794facffcae29d4f94b337fc84083028526` passed canonical ATHENA Quality Gate `34058195011 = success`.
- History-preserving NON-FORCE synchronization: `4747d61f2695a39862302c9f7c783fad818a510e`, parents prior Backend `2ea98794facffcae29d4f94b337fc84083028526` + exact Develop `1cc7b8dceb5b4ff098442e9f17f89b8cc36cb390`.
- Sync used exact Develop as base and carried only verified Backend WAL-policy product/test plus this handoff; divergent migration files were intentionally not overwritten.
- `main` and `bnbgrs/ATHENA` remain read-only.

## Verified predecessor
- BE-053 WAL policy exact-status-shape is exact-green on `2ea98794facffcae29d4f94b337fc84083028526` / Quality `34058195011 = success`.
- ExternalAccessGateway runtime boundaries remain exact-green at `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6` / Quality `33884210684 = success`.

## Current slice
Area: Storage / WAL Maintenance / `WalRuntimeStatus` derived-byte runtime boundary.

Product `22fa292c2213e8dbeca4e0a6733d32e71f5141df` validates `autocheckpoint_bytes` through the same positive true-int boundary used for the primitive SQLite policy values before comparing it with `page_size_bytes * autocheckpoint_pages`.

Previously `autocheckpoint_bytes=True` could be accepted when `page_size_bytes == 1` and `autocheckpoint_pages == 1`, because Python equality treats `True == 1`. This allowed a bool to cross a persisted/runtime systems status contract even though neighboring byte/count fields explicitly reject bool.

Focused regression `fcd0b9a453cdf15c8d13c9708ebc5cd206ccbdad` covers bool rejection, nonpositive rejection, and canonical exact positive acceptance without weakening the derived-value equality invariant.

## Invariants
- PASSIVE remains the only automatic checkpoint mode; TRUNCATE still requires explicit idle confirmation.
- WAL files are never manually deleted.
- WAL size observation remains no-follow, regular-file and handle/path-identity checked.
- page size, autocheckpoint pages and derived autocheckpoint bytes are true positive non-bool integers.
- checkpoint result remains exact three fields with bounded busy value and non-negative frame counters.
- no migration/schema/transaction/Provider/TOR/Security/UI/retry/cryptography/process-tree semantics changed.
- ExternalAccessGateway runtime boundaries are unchanged.

## Coordination reviewed
- Error head: `postmerge/errors@d53cfd799fab60859f6e2b2fe76e4154fa4555bd`; only Core-owned ERR-0018 Ruff import ordering remains open.
- Spec/Core head: `postmerge/spec-core@5714f3c7724cb82ccd75a7e852c668bfe78c6d5d`.
- UI head: `postmerge/ui@63a3387107b017d8bae7a46f5ea315cd766f7c9f`.
- Integrator/Develop baseline: `1cc7b8dceb5b4ff098442e9f17f89b8cc36cb390`.
- No Core/UI/Error-owned file was modified.

## Verification
- Verified predecessor: Quality `34058195011 = success` on `2ea98794facffcae29d4f94b337fc84083028526`.
- Current test head Quality `34061282362` was pending when this handoff was written; pushing this required versioned handoff may supersede that run. Require the first exact successful Quality on `fcd0b9a453cdf15c8d13c9708ebc5cd206ccbdad` or this documentation descendant before promotion.
- No PASS is claimed for the new runtime-status slice yet.

## Integrator handoff
READY: BE-053 WAL policy exact-status-shape lineage `2ea98794facffcae29d4f94b337fc84083028526` / Quality `34058195011 = success`.

NOT READY: `WalRuntimeStatus.autocheckpoint_bytes` true-int boundary product `22fa292c2213e8dbeca4e0a6733d32e71f5141df` + focused regression `fcd0b9a453cdf15c8d13c9708ebc5cd206ccbdad`; exact canonical success required.

## Persistent release regression knowledge
Retain without reopening absent exact-current reproduction: Windows pypdf metadata; fail-closed frozen child argv; two-EXE Desktop/Worker split; exactly one Desktop with bounded workers; adaptive small-context DirectChat reserve; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; duplicate `source_processing_job_id`; Core startup failure; storage-bootstrap startup failure.

## Next backend slice
Consume the first exact canonical Quality containing `fcd0b9a453cdf15c8d13c9708ebc5cd206ccbdad` or this handoff descendant. If green, promote only the derived WAL byte boundary and re-trace current Alpha/Beta/source contracts for the highest unclaimed disjoint Backend/System P1/P2 gap. If red, repair only the smallest Backend-owned primary failure without weakening WAL, Storage/Recovery, ExternalAccessGateway, persistence, provenance or platform invariants. If cancelled, do not repeat unchanged; use another executable verification route or a distinct real Backend/System slice.
