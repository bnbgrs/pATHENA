# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline: `develop/pathena-next@7c784b77af3bc0ec0c2579cc89b6947aadaf701c`.
- Previous worker head: `postmerge/backend@552209e005b82d31577d9f8a466af4dd97b99866`.
- Previous exact canonical Quality: `34069825099 = success` on `552209e005b82d31577d9f8a466af4dd97b99866`.
- Current history-preserving NON-FORCE synchronization: `315ec37fc43c1030cd431217545d4512b5623155`, parents previous worker + exact current Develop.
- `main` and `bnbgrs/ATHENA` remain strict read-only and untouched.

## Applied verified slice

Area: Storage / WAL maintenance diagnosis runtime boundary.

The exact-green Backend product blob `src/athena/storage/wal_maintenance.py@d30a171549715db123bb4db923ca99c08ed9f362` and focused regression blob `tests/unit/test_wal_maintenance_diagnosis_boundaries.py@a0ce6d2d629555f64794d50125e7230047d5cdd9` were overlaid onto the exact current Develop tree only. No other Backend, Core, UI, Error or Integrator file was imported.

`WalMaintenanceDiagnosis` now fails deterministically for malformed/unhashable/non-text/unknown `level` values and requires `cycle` to be a real `WalMaintenanceCycle`. Valid diagnosis semantics are unchanged.

## Call chain

`WalMaintenanceOrchestrator.run_cycle -> WalMaintenanceDiagnosis.__post_init__ -> exact text/known-level validation -> exact WalMaintenanceCycle validation -> nonnegative counters -> requires_attention`.

## Preserved invariants

- ExternalAccessGateway runtime boundaries remain exact-green and unchanged: TTL/max-bytes are genuine ints with bool rejected; timeout is numeric, non-bool and finite.
- No silent Tor-to-Direct fallback; Direct remains explicitly authorized only.
- No loopback/private proxy leak; redirect authorization, HTTPS/default-port fail-closed, compression rejection and response-size fail-closed remain unchanged.
- WAL automatic checkpoint remains PASSIVE only; TRUNCATE requires explicit idle confirmation; no manual WAL deletion.
- WAL no-follow regular-file handle/path identity checks remain intact.
- Persistence, recovery, provenance, fsync and transactional Source finalization are unchanged.
- Windows pypdf/frozen argv/two-EXE/process-tree, Direct-Chat small-context reserve and lane-lock crash signatures remain Beta/release regression knowledge and are not reopened without exact-SHA reproduction.
- No Skip/XFail/assertion/guard weakening; no retries/crypto added; no force push or history rewrite.

## Verification state

- Source worker `552209e005b82d31577d9f8a466af4dd97b99866`: canonical Quality `34069825099 = success`.
- Current Develop-compatible sync `315ec37fc43c1030cd431217545d4512b5623155`: exact canonical verification required after this synchronization; no PASS is claimed until a run completes on the final handoff descendant.

## Coordination

- Errors head observed: `bf54a05a9ebccfe52a7087589fefce7446f58bbe`; Error ledger reports no OPEN/BLOCKED defect and records prior Backend source lineage green.
- Spec/Core head observed: `b6cd1383caf7d60b17ff5a9141c0fef8cafafbe9`; Core-owned memory work was not imported.
- UI head observed: `cf808b725fcd7ac6c302cf8a3f59c20e385f8f2c`; UI work was not imported.
- Integrator/Develop head observed and used exactly: `7c784b77af3bc0ec0c2579cc89b6947aadaf701c`.

## Integrator handoff

READY_SOURCE only: the WAL diagnosis runtime boundary is exact-green on source worker `552209e005b82d31577d9f8a466af4dd97b99866` via Quality `34069825099`. The new Develop-compatible synchronization is NOT_READY until exact canonical Quality is green.

## Next backend slice

Consume exact Quality for the final handoff descendant. If green, promote only this Develop-compatible WAL diagnosis boundary and re-trace current Alpha/Beta contracts for the highest unclaimed disjoint Backend/System P1/P2 gap; do not mechanically continue WAL hardening. If red, isolate only the exact Backend-owned primary failure and preserve all network, storage, recovery, provenance and Windows runtime invariants.
