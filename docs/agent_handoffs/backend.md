# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline: `develop/pathena-next@3954ce3076f6f03d0d850834fbe33cc5deb57e6c`.
- Worker branch: `postmerge/backend` only.
- Previous worker `7db1e9864f0a0d0fbeafdc987963475f84701ab7` completed canonical Quality `34079743908 = success`.
- Integrator already incorporated the preceding checkpoint-result mode boundary into Develop and recorded it at `3954ce3076f6f03d0d850834fbe33cc5deb57e6c`.
- History-preserving NON-FORCE sync to current Develop: `1b1dac228e0426f8dac05efd68f794486a012e0a`, parents previous worker + current Develop, resulting tree exactly current Develop before the new slice.
- `main` and `bnbgrs/ATHENA` remain strictly read-only and untouched.

## Current slice

Area: Storage / WAL maintenance service runtime checkpoint-mode boundary.

Product commit `2c5f19bba44117136e99d9f0e211f57b0b7c602e` changes `WalMaintenanceService._checkpoint()` to reject non-text/unhashable runtime mode values before membership evaluation, database access, transaction inspection or SQLite PRAGMA execution. This closes a deterministic fail-before-side-effect contract leak where an unhashable malformed value could raise Python `TypeError` instead of `WalMaintenanceError`.

Focused regression commit `724acbbb5d94c424245906d7d57d05e04b0aeb57` adds direct boundary coverage proving malformed unhashable and non-text modes fail before any database attribute can be accessed.

Valid `PASSIVE` and `TRUNCATE` call paths are unchanged. Automatic maintenance remains PASSIVE-only; TRUNCATE remains gated behind explicit `idle_confirmed is True`.

## Preserved invariants

- ExternalAccessGateway runtime-boundary slice remains unchanged and previously exact-green: ttl/max_bytes genuine non-bool ints; timeout numeric, non-bool and finite.
- No silent Tor-to-Direct fallback; Direct fallback explicit only; no loopback/private proxy leak; redirect reauthorization, HTTPS/default-port fail-closed, compressed-response and response-size fail-closed behavior unchanged.
- Storage audit/provenance/fsync/transactional finalization unchanged.
- WAL files are never manually deleted; no new retries or cryptography.
- WAL no-follow/path-handle identity checks, transaction refusal, exact SQLite checkpoint result shape and bounded numeric guards remain unchanged.
- Historical Windows pypdf/frozen-child/two-EXE/process-tree/DirectChat/lane-lock/storage-bootstrap crash signatures remain release regression knowledge only absent exact-current reproduction.
- No Skip/XFail, assertion weakening, main mutation, force update or history rewrite.

## Worker coordination reviewed

- Error head: `postmerge/errors@9c480a9c7e7deb0362061ea7fecce4792542353e`; ledger reports no OPEN/BLOCKED defect.
- Spec/Core head: `postmerge/spec-core@35e5f46df9c81a918b274ea5e29f7a265b6f1791`; Core-owned memory/Search work remains disjoint.
- UI head: `postmerge/ui@7d5b99d4715352843b800253f67f50b56095aec2`; UI-owned responsive-startup work remains disjoint.
- Integrator/Develop head reviewed: `3954ce3076f6f03d0d850834fbe33cc5deb57e6c`.

## Verification state

- Previous Backend exact worker Quality `34079743908 = success` was consumed before mutation.
- New product/test commits are real repository mutations, not patch-only or analysis-only handoffs.
- At handoff creation, no exact canonical workflow had yet appeared for focused-test head `724acbbb5d94c424245906d7d57d05e04b0aeb57`; therefore no PASS is claimed for the new slice.

## Integrator handoff

NOT READY until an exact canonical Quality run on a head carrying unchanged product `2c5f19bba44117136e99d9f0e211f57b0b7c602e` and regression `724acbbb5d94c424245906d7d57d05e04b0aeb57` completes successfully.

## Next backend slice

First consume exact canonical evidence for this handoff successor. If green, mark only this WAL service runtime mode boundary VERIFIED/INTEGRATOR_READY and re-trace the highest current evidence-backed Backend/System P1/P2 gap, preferring BE-053 orchestration/long-reader integration or another substantive provider/recovery/platform slice over further DTO hardening. If red, repair only the exact Backend-owned primary failure without weakening WAL, Storage/Recovery, ExternalAccessGateway, persistence, provenance or Windows runtime invariants.
