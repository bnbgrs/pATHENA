# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline: `develop/pathena-next@b1537fc138560fe85d4d97cf76c887b92e63c8f4`.
- Worker pre-run head: `postmerge/backend@2a6d1ba76d4822e324bd8117fc001dd79667d702`.
- Current Error handoff: `postmerge/errors` reports OPEN none; `ERR-0016` and `ERR-0017` FIXED_PENDING_VERIFY.
- History-preserving NON-FORCE synchronization: `54637682087b880622796ee0b618362f7ed802fe`, parents prior Backend head + exact Develop; exact Develop tree was retained except Backend-owned local-provider files/tests/handoff.
- `main` and `bnbgrs/ATHENA` remained strictly read-only.

## ExternalAccessGateway runtime boundaries — VERIFIED / READY

`ttl_seconds` and `max_bytes` require true non-bool integers. `timeout_seconds` accepts finite numeric non-bool values only and rejects NaN/Inf while preserving valid ranges. Exact green lineage remains `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6`; canonical Quality `33884210684 = success`.

No Tor/Direct, proxy, redirect, HTTPS/default-port, compressed-response, response-size, audit, provenance, fsync or transactional Source-finalization invariant was weakened.

## Corrected-lineage re-verification now executing

The prior zero-byte test-head workflow `34027562400@52d7920bbdacd6e3e6e576f136476edb23c586cc` completed `cancelled`, so no PASS was claimed.

Current Develop now structurally contains the bounded ERR-0017 Personal-Memory repair. Backend therefore synchronized onto that exact corrected Develop lineage rather than repeating the old import-graph blocker.

Canonical Quality `34030367660@54637682087b880622796ee0b618362f7ed802fe` was automatically created by the NON-FORCE synchronization and is currently `in_progress`. At the last check all four canonical jobs were actively executing; checkout/setup had succeeded and no exact current failure had yet been emitted. No PASS is claimed before completion.

This corrected-lineage run simultaneously re-verifies:
- ERR-0016 overflow poison semantics and oversize accounting;
- callable response-body delegate guards;
- lifecycle-hook callable guards;
- zero-byte read no-I/O semantics;
- current Develop ERR-0017 import/startup correction under canonical mypy/pytest/API/local-install paths.

## Provider semantics retained

Local-provider transport remains loopback-only, proxy-free, redirect-rejecting, byte-bounded and total-deadline-bounded. Non-byte bodies fail closed. Rejected oversized bytes are not counted and permanently poison subsequent body access. Alternative raw read APIs/body handles remain blocked. `read(0)` performs no delegate body I/O after validation and poison/callable guards.

## Persistent runtime / crash prevention invariants

Retain Beta/release acceptance for Windows `pypdf` metadata, fail-closed frozen child argv, `pATHENA.exe` Desktop + `pATHENA-Worker.exe` split, exactly one Desktop with bounded workers, adaptive 2048-context DirectChat reserve, lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`, and startup signatures `duplicate column name: source_processing_job_id`, `ATHENA Core startup failed`, `Failed to start service 'storage-bootstrap'`. Reopen historical signatures only on exact-current reproduction.

## Next backend slice

Consume exact Quality `34030367660@54637682087b880622796ee0b618362f7ed802fe`. If green, close only exact-supported ERR-0016/Provider pending lineages and immediately take the highest unclaimed disjoint Backend/System P0/P1/P2 gap. If red, isolate the smallest exact Backend-owned primary failure and fix it without weakening ExternalAccessGateway, byte/deadline/type, persistence, recovery, provenance or Windows runtime invariants. If cancelled, do not repeat the runner state unchanged; take a different real disjoint Backend/System slice or alternate executable verification route.
