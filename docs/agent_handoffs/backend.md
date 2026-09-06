# pATHENA Backend & Systems Handoff

## Baseline
- Shared baseline: `develop/pathena-next@abfe054654ae69994ad22d5a1079aeae42fba09f`.
- Worker branch: `postmerge/backend`.
- History-preserving NON-FORCE synchronization: `f3392917e4cfaee87632fa682d898bfd0f9e894b`, parents prior Backend `4f09ad222547f279e27fb3d34285feb82f6a8f71` + exact Develop `abfe054654ae69994ad22d5a1079aeae42fba09f`.
- `main` and `bnbgrs/ATHENA` remain read-only.

## Verified predecessor
- User-version exact-status-shape worker head `4f09ad222547f279e27fb3d34285feb82f6a8f71` passed canonical ATHENA Quality Gate `34048748410 = success`.
- ExternalAccessGateway exact runtime-type boundary lineage remains exact-green at `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6` / Quality `33884210684`.

## Current slice
Area: Storage / Recovery / migration WAL checkpoint busy-domain validation.

Product `38dac1166d951f4a11b55181f927389304b3cd2e` now validates the first `PRAGMA wal_checkpoint(TRUNCATE)` status field (`busy`) with the same exact non-bool, non-negative integer boundary already applied to frame counters. Previously a negative genuine integer failed only later as a generic incomplete-checkpoint condition; it now fails at the runtime-domain boundary before journal-mode transition.

Focused regression `eacb43bee6f8d168346198d5bb4b7630156b1570` covers negative `busy`, `log_frames`, and `checkpointed_frames`, retaining exact checkpoint status-shape rejection and proving journal-mode transition is not attempted.

## Invariants
- candidate-only migration; live DB untouched;
- absolute regular non-link candidate and safe ancestry required;
- exact non-bool integer PRAGMA values retained;
- user_version status exactly one field;
- WAL checkpoint status exactly three fields;
- busy/log/checkpointed counters non-negative; complete non-busy checkpoint required;
- journal-mode status exactly one field and text `delete` required;
- sidecar-free activation handoff retained;
- no Security/TOR/Provider/UI semantics, retries, cryptography, schema representation or WAL format changes.

## Coordination
- Error worker reports `ERR-0018` OPEN and Core-owned (Ruff import-order failure); no Backend runtime/storage/security defect is implicated.
- Current Develop/Integrator baseline: `abfe054654ae69994ad22d5a1079aeae42fba09f`.
- No Core/UI-owned files were modified.

## Integrator handoff
READY: user_version exact-status-shape lineage `4f09ad222547f279e27fb3d34285feb82f6a8f71` / Quality `34048748410 = success`.

NOT READY: checkpoint busy-domain product `38dac1166d951f4a11b55181f927389304b3cd2e` + regression `eacb43bee6f8d168346198d5bb4b7630156b1570` pending exact canonical completion on this documentation descendant.

## Persistent release regression knowledge
Retain without reopening absent exact-current reproduction: Windows pypdf metadata; fail-closed frozen child argv; two-EXE Desktop/Worker split; exactly one Desktop with bounded workers; adaptive small-context DirectChat reserve; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; duplicate `source_processing_job_id`; Core startup failure; storage-bootstrap startup failure.

## Next backend slice
Consume the first exact canonical Quality containing `eacb43bee6f8d168346198d5bb4b7630156b1570` or this documentation descendant. If green, promote only the checkpoint busy-domain slice and continue to the highest current unclaimed disjoint Backend/System gap. If red, repair only the smallest Backend-owned primary failure without weakening Storage/Recovery, ExternalAccessGateway, persistence, provenance or platform invariants. If cancelled, do not repeat unchanged; use another executable verification route or a distinct real Backend/System slice.
