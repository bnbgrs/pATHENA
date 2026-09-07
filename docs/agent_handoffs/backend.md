# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline reviewed: `develop/pathena-next@9a7ae283ae8476c61f3a689e95bbc943a319939c`.
- Worker branch: `postmerge/backend` only.
- Previous worker head `92493b4ae9e59eed2ce05586f1268f1a557272ae` passed canonical ATHENA Quality Gate `34073089618 = success`.
- Integrator has already applied the verified WAL diagnosis runtime-boundary product/regression onto Develop.
- History-preserving NON-FORCE synchronization for this run: `1ccec98d2d778e06589abd7fe8b57b990e211037`, parents Backend `92493b4ae9e59eed2ce05586f1268f1a557272ae` and Develop `9a7ae283ae8476c61f3a689e95bbc943a319939c`, using the exact Develop tree.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched. No force update or history rewrite.

## ExternalAccessGateway priority state

The requested ExternalAccessGateway runtime-boundary slice remains implemented and exact-canonical green from prior verified lineage. The current Develop/Backend source preserves genuine-int rejection for bool `ttl_seconds`/`max_bytes`, numeric non-bool finite `timeout_seconds`, and the existing Tor/direct, redirect, proxy, HTTPS/default-port, compression, response-size, audit/provenance/fsync and transactional Source-finalization invariants. No ExternalAccessGateway mutation was required in this run because the requested patch is already applied and verified.

## Selected backend slice

Area: `storage/wal_maintenance.py` runtime checkpoint-result boundary, within active P1 `BE-053`.

Source trace found that `WalCheckpointResult.__post_init__()` performed set membership directly on `mode`. A malformed unhashable runtime value such as `[]` therefore escaped as Python `TypeError` rather than the DTO's deterministic invalid-mode contract. This is a runtime-boundary defect, not a checkpoint-policy change.

Product commit: `f675fe4b384b5e20bde5a279df2bdafca463ace6`.
Focused regression commit: `deb251713acf103f994b0ba47954a778fe599867`.

The product now requires `mode` to be text before checking the canonical `PASSIVE`/`TRUNCATE` values. Invalid non-text/unhashable values fail before any downstream use. Valid checkpoint modes are unchanged.

## Focused acceptance

New `tests/unit/test_wal_checkpoint_result_boundaries.py` covers:

- unhashable mode rejected deterministically with `ValueError`;
- non-text mode rejected with the same contract;
- canonical `PASSIVE` accepted;
- canonical `TRUNCATE` accepted.

Exact Quality `34076447467` was created on the focused-test head and was pending when this handoff was written. No PASS is claimed for the new slice until an exact completed run succeeds.

## Retained invariants

- automatic maintenance remains PASSIVE-only;
- TRUNCATE still requires explicit idle confirmation;
- no manual WAL deletion;
- WAL observation remains no-follow, regular-file and path/handle identity checked;
- page size/autocheckpoint policy exact-shape and positive genuine-int checks remain;
- checkpoint status remains exactly three fields with bounded busy domain and nonnegative frame counts;
- diagnosis and runtime status guards remain unchanged;
- no schema, migration, transaction, persistence, recovery, Provider/Transport, Security, retry or cryptographic behavior changed;
- Windows pypdf/frozen argv/two-EXE/process-tree, DirectChat small-context reserve, lane-lock/scheduler/packaged-worker and storage-bootstrap crash classes remain Beta/release regression knowledge and are not reopened absent exact-current reproduction.

## Worker coordination

- Errors handoff reports no current Backend-owned primary defect and exact previous Backend head green.
- Spec/Core work remains Core-owned and was not imported or overwritten.
- UI work remains UI-owned and was not imported or overwritten.
- Integrator target remains `develop/pathena-next`; Backend does not merge to Develop or main.

## Integrator handoff

READY SOURCE from earlier runs: ExternalAccessGateway runtime boundaries and the WAL diagnosis boundary already consumed by Integrator.

NOT READY yet: checkpoint-result mode runtime boundary at product `f675fe4b384b5e20bde5a279df2bdafca463ace6` + regression `deb251713acf103f994b0ba47954a778fe599867`; wait for exact canonical Quality completion on the final handoff descendant before integration.

## Next backend slice

Consume the exact canonical Quality result for this handoff lineage. If green, mark the checkpoint-result runtime boundary verified/Integrator-ready and re-trace current Alpha/Beta contracts for the highest unclaimed Backend/System P1/P2 gap, preferring a concrete BE-053 orchestration/long-reader integration gap or another disjoint system slice over repeated DTO hardening. If red, repair only the exact Backend-owned primary failure without weakening WAL, Storage/Recovery, ExternalAccessGateway, persistence/provenance or Windows runtime invariants.
