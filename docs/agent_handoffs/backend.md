# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline: `develop/pathena-next@70f985ce7a28044824bfbfa53769b982fa152747`.
- Worker pre-run head: `postmerge/backend@8964f9ae22f0b3f98d06f9c000a47a98dc54f473`.
- Worker heads reviewed: Error reports OPEN none; Spec/Core and UI are disjoint; Integrator is current Develop.
- History-preserving NON-FORCE synchronization: `2e1b1b5b06c6b2486066054b62cc02982bb270b6`, parents prior Backend head plus exact Develop, using exact Develop tree plus only Backend-owned migration/handoff blobs.
- `main` and `bnbgrs/ATHENA` remained strictly read-only; no force update or history rewrite was used.

## ExternalAccessGateway runtime boundaries — VERIFIED / READY

Required runtime validation remains exact-green and integrated: `ttl_seconds` and `max_bytes` require true non-bool integers; `timeout_seconds` requires finite numeric non-bool input. Canonical Quality `33884210684@c67fa646d8ba4e4137cdf69992b9c8b42ad904d6 = success`.

No Tor/Direct, proxy, redirect, HTTPS/default-port, compressed-response, response-size, audit, provenance, fsync or transactional Source-finalization invariant was weakened.

## Prior Storage/Recovery slice — migration PRAGMA runtime types VERIFIED / READY

Canonical Quality `34033392294@8964f9ae22f0b3f98d06f9c000a47a98dc54f473 = success`. Safety-critical PRAGMA values are exact runtime types: `user_version` and WAL checkpoint counters are genuine non-bool integers; `journal_mode` is genuine text. This lineage is now Integrator-ready.

## New Storage/Recovery slice — WAL checkpoint frame-count domain

Product `051b9d3f553f686ff30c20a0bf79291281023c8f` strengthens candidate migration acceptance so `log_frames` and `checkpointed_frames` must be non-negative genuine integers. Previously the exact-type boundary still allowed `(busy=0, log_frames=-1, checkpointed_frames=-1)` to satisfy equality and falsely pass complete-checkpoint acceptance even though negative SQLite frame counts are invalid.

Focused regression `633300e071143b7b43dba8e6bc49f132ba37350f` adds negative `log_frames` and negative `checkpointed_frames` cases and verifies fail-closed `MigrationExecutorError` before journal-mode/activation eligibility.

Canonical Quality `34036277571@633300e071143b7b43dba8e6bc49f132ba37350f` exists and was pending at the exact check. No PASS is claimed for the new slice until a completed exact descendant succeeds.

## Call chain / invariants

`migrate_schema_candidate -> candidate path/link/type guards -> SQLite candidate-only open -> initialize_schema -> exact user_version -> TRUNCATE checkpoint -> exact busy integer -> non-negative exact log/checkpointed frame counters -> complete checkpoint equality -> exact text DELETE journal mode -> close -> sidecar absence verification`.

Retained invariants: candidate-only mutation; no live database migration; no coercion of safety-critical PRAGMA values; complete WAL checkpoint required; DELETE journal mode required before activation; candidate path absolute/regular/non-link with safe ancestors; sidecar-free handoff mandatory; no transaction/WAL/recovery format change; no new retry or crypto behavior.

## Queue correction

The 2026-08-24 backend queue is stale in two places reviewed this run: current Develop already contains Windows HANDLE-bound durable replacement in `storage/durable_fs.py` (so BE-038 must not be blindly re-applied), and Chat generation already calls the reusable revision-aware ModelSignature guard (so BE-020 is no longer a current mutation gap). Backend therefore did not duplicate either stale item.

## Persistent release regression knowledge

Retain Windows `pypdf` packaging metadata, fail-closed frozen child argv, Desktop/Worker two-EXE split, exactly one Desktop with bounded workers, adaptive 2048-context DirectChat reserve, lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`, and storage-bootstrap/migration startup signatures as Beta/release acceptance knowledge. Reopen only on exact-current reproduction.

## Integrator handoff

READY: ExternalAccessGateway runtime boundaries; corrected Local HTTP lineage; migration PRAGMA exact-runtime-type boundary through `8964f9ae22f0b3f98d06f9c000a47a98dc54f473` / Quality `34033392294`.

NOT READY: negative WAL checkpoint frame-count rejection `051b9d3f553f686ff30c20a0bf79291281023c8f` + regression `633300e071143b7b43dba8e6bc49f132ba37350f` until canonical Quality succeeds on an exact descendant.

## Next backend slice

Consume the first completed canonical Quality containing `633300e071143b7b43dba8e6bc49f132ba37350f` or this documentation-only descendant. If green, promote negative checkpoint-frame rejection VERIFIED / INTEGRATOR_READY and take the highest current non-stale, disjoint Backend/System P1/P2 gap. If red, isolate the smallest Backend-owned failure and repair without weakening schema/WAL/recovery/path or Provider/Security invariants. If cancelled, do not repeat the runner state unchanged; use a different executable verification route or a distinct real Backend/System slice.
