# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline: `develop/pathena-next@be0e8da5127f17f6bbc3cbbc8c58496102c9135c`.
- Worker pre-run head: `postmerge/backend@a424e32621d2c7441a144ff3a1a3faecd32ea7c4`.
- Current worker heads reviewed: Error handoff closes `ERR-0016` and `ERR-0017`; Spec/Core remains disjoint Search work; UI remains disjoint Sources focus work; Integrator has composed the corrected-lineage Local HTTP boundaries onto Develop.
- History-preserving NON-FORCE synchronization: `db8a000ac2369fce921887c671ec6778eb30b7c7`, parents prior Backend head plus exact Develop, using the exact Develop tree.
- `main` and `bnbgrs/ATHENA` remained strictly read-only; no force update or history rewrite was used.

## ExternalAccessGateway runtime boundaries — VERIFIED / READY

The required runtime boundary remains exact-green and integrated: `ttl_seconds` and `max_bytes` require true non-bool integers; `timeout_seconds` requires finite numeric non-bool input. Canonical Quality `33884210684@c67fa646d8ba4e4137cdf69992b9c8b42ad904d6 = success`.

No Tor/Direct, proxy, redirect, HTTPS/default-port, compressed-response, response-size, audit, provenance, fsync or transactional Source-finalization invariant was weakened.

## Corrected Local HTTP lineage — VERIFIED / INTEGRATED

Canonical Quality `34030367660@54637682087b880622796ee0b618362f7ed802fe = success`. Error worker now records `ERR-0016` and `ERR-0017` FIXED. Integrator composed the exact verified Local HTTP runtime-boundary blobs onto Develop in `3376fac0051483308d8c24e1e58d6b532bde702e` and documented the composition at current Develop head.

Backend therefore did not repeat the already-verified Provider micro-slice.

## New backend slice — migration PRAGMA readback runtime types

Area: Storage / Recovery / schema-candidate verification.

Product `8eaddc0c40c304b1ba741e9a0980e1f7f760a17c` hardens `src/athena/storage/migration_executor.py` so safety-critical SQLite PRAGMA readbacks no longer pass through permissive `int(...)` / `str(...)` coercion. `user_version`, WAL checkpoint `busy/log_frames/checkpointed_frames` must be genuine non-bool integers; `journal_mode` must be genuine text. Malformed but coercible runtime values fail closed before migration acceptance or activation eligibility.

Focused regression `987fb5b1c548c3a7a7ab0c25e2cc1d3b43c95fb1` extends `tests/unit/test_migration_executor.py` with bool/string/float user-version and checkpoint cases plus non-text journal-mode cases while preserving existing real SQLite candidate migration coverage.

Canonical Quality `34033357836@987fb5b1c548c3a7a7ab0c25e2cc1d3b43c95fb1` was created and was pending at the last exact check. The product-only predecessor run `34033328965@8eaddc0c40c304b1ba741e9a0980e1f7f760a17c` was cancelled by the successor push. No PASS is claimed until a completed exact descendant run succeeds.

## Call chain / invariants

`migrate_schema_candidate -> path/link/type guards -> sqlite connect candidate only -> initialize_schema -> PRAGMA user_version exact-int validation -> WAL TRUNCATE checkpoint exact-int validation -> journal_mode DELETE exact-text validation -> connection close -> sidecar absence verification`.

Retained invariants: candidate-only mutation; no live database migration; no schema-version coercion; complete WAL checkpoint required; DELETE journal mode required before activation; candidate path must be absolute regular file without link-boundary ancestors; sidecar-free handoff remains mandatory; no transaction/WAL/recovery format change; no new retry or crypto behavior.

## Persistent release regression knowledge

Retain Windows `pypdf` packaging metadata, fail-closed frozen child argv, Desktop/Worker two-EXE split, exactly one Desktop with bounded workers, adaptive 2048-context DirectChat reserve, lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`, and storage-bootstrap/migration startup signatures as Beta/release acceptance knowledge. Reopen only on exact-current reproduction.

## Integrator handoff

READY remains the already integrated/verified ExternalAccessGateway and corrected Local HTTP lineage. NOT READY: migration PRAGMA readback exact-runtime-type boundary `8eaddc0c40c304b1ba741e9a0980e1f7f760a17c` + regression `987fb5b1c548c3a7a7ab0c25e2cc1d3b43c95fb1` until canonical Quality completes successfully on an exact descendant.

## Next backend slice

Consume the first completed canonical Quality containing `987fb5b1c548c3a7a7ab0c25e2cc1d3b43c95fb1` or this documentation-only descendant. If green, promote the migration PRAGMA runtime boundary to VERIFIED / INTEGRATOR_READY and immediately take the highest current unclaimed disjoint Backend/System P0/P1/P2 gap. If red, isolate the smallest Backend-owned failure and repair it without weakening schema/WAL/recovery/path or Provider/Security invariants. If cancelled, do not repeat the same runner state unchanged; use another executable verification route or a distinct real Backend/System slice.
