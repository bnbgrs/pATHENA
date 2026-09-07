# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline: `develop/pathena-next@af09641cdf2b872688cb4b67c9815194af9e7621`.
- Worker branch before sync: `postmerge/backend@35883180205c83cabc1d20ef2fad39d8ee691699`.
- Verified predecessor: canonical Quality `34067080370` = SUCCESS on exact worker SHA `35883180205c83cabc1d20ef2fad39d8ee691699`.
- History-preserving NON-FORCE synchronization: `08ea0bc692ebde70d0cd9e6b8f3353d22ac63d58`, parents worker+Develop, tree based on exact Develop with only verified WAL diagnosis product/test blobs overlaid.
- `main` and `bnbgrs/ATHENA` remain strictly read-only and untouched.

## Selected slice

Area: Storage/WAL maintenance diagnosis runtime boundary.

Verified product behavior in `src/athena/storage/wal_maintenance.py` makes `WalMaintenanceDiagnosis` reject malformed `level` values deterministically and requires `cycle` to be a real `WalMaintenanceCycle`. The regression file `tests/unit/test_wal_maintenance_diagnosis_boundaries.py` covers unhashable/non-text/unknown levels, non-cycle payloads, and canonical acceptance.

The verified source/test blobs are now applied to current Develop-compatible Backend lineage. This run does not broaden WAL checkpoint policy, migration semantics, retries, crypto, network routing, UI or Core behavior.

## Invariants

- ExternalAccessGateway runtime-boundary hardening remains unchanged and previously canonical-green.
- No silent Tor to Direct fallback; Direct remains explicitly authorized only.
- WAL automatic checkpoint remains PASSIVE only; TRUNCATE requires explicit idle confirmation.
- No manual WAL deletion.
- WAL no-follow regular-file handle/path identity checks remain intact.
- Persistence, recovery, provenance, fsync and transaction boundaries are unchanged.
- Windows frozen-entrypoint/two-EXE/process-tree, Direct-Chat small-context and lane-lock crash signatures remain release-regression knowledge and are not reopened without exact-SHA reproduction.
- No Skip/XFail/assertion/guard weakening; no force push or history rewrite.

## Verification

- Source lineage `35883180205c83cabc1d20ef2fad39d8ee691699`: canonical Quality `34067080370` = SUCCESS.
- Develop-compatible synchronization `08ea0bc692ebde70d0cd9e6b8f3353d22ac63d58`: canonical verification is required before Integrator promotion; no PASS is claimed until an exact run completes.

## Coordination

- Error worker head observed: `e9eb438d5c5b048a695bfc0dbdad7d0519a269d2`.
- Spec/Core worker head observed: `57aa31ec49ddec2d68147e91ea6b3c311d33881a`; Core-owned memory work was not imported.
- UI remains disjoint and UI-owned; no UI file was modified.
- Integrator target remains `develop/pathena-next`; Backend does not self-merge there.

## Next backend slice

First consume exact canonical verification for this Develop-compatible lineage. If green, mark only the WAL diagnosis boundary Integrator-ready and select the highest current evidence-backed disjoint Backend/System P1/P2 gap after re-reading Alpha/Beta contracts and worker handoffs; do not mechanically extend WAL hardening. If red, isolate only the exact Backend-owned primary failure and preserve all network, storage, recovery, provenance and Windows runtime invariants.
