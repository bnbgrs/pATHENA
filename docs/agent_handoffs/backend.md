# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline reviewed: `develop/pathena-next@49212a0f157d433d68e9d04e9a9643e2909b6827`.
- Worker branch: `postmerge/backend`.
- Prior worker head: `5b04d7e335823f59bd33847e5b5c2c5b7e23458c`.
- Required handoffs and worker branches were reviewed before mutation; current observed error worker was `e0d009c4ecc2e0db3000acdb4b0dc726e64005de`, with Develop integrator evidence also recording spec-core `2f62d2a26f9341e7ea8c84abe2ae48762bfe117c` and UI `fb98e47fde410137b971a303678d4e63f66e1d6d`.
- History-preserving NON-FORCE synchronization: `9efa14326b3c4b0eaacff26aa9942202e7a70aca`, with parents prior Backend head and exact Develop.
- `main` and `bnbgrs/ATHENA` remain strict read-only and untouched.

## ExternalAccessGateway runtime boundaries — VERIFIED

Required fail-before-side-effect guards remain present: `ttl_seconds` and `max_bytes` reject bool/non-int values; `timeout_seconds` rejects bool and non-finite values while preserving valid numeric ranges. Gateway lineage through Backend head `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6` is backed by canonical ATHENA Quality `33884210684 = success`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Disk-pressure threshold consistency — VERIFIED

Product `c0ee910a20fb396b0c20429f2da33873b407c641` rejects one-check recovery telemetry where `after_release.thresholds` differs from `before_release.thresholds` while volume size is stable. Focused test `dde63f019c5ecd95d1805ff9c19fdd986fe4b436` covers the contradictory threshold mutation.

The exact documentation descendant Backend head `5b04d7e335823f59bd33847e5b5c2c5b7e23458c` passed canonical ATHENA Quality `33978168395 = success`.

Status: `BACKEND_VERIFIED / INTEGRATOR_READY`.

## Disk-pressure assessment-state truth boundary — APPLIED / PENDING CANONICAL

`DiskPressureAssessment` was externally constructible with a `state` that contradicted its own `free_bytes` and ordered thresholds. Such a contradictory object could feed reserve-release, safe-mode, write-gating, provision-result, or audit paths with false recovery semantics even though controller-generated assessments are consistent.

Product commit `deb69f03a5aa40e655e83bea1f69d6aeaa2b2af8` now derives the expected state from the supplied free-space/threshold boundary and fails closed when the supplied enum differs. Existing strict `< threshold` semantics are preserved. Test commit `918c742e86c0567260f2fbc588efd8febd2114ea` verifies that EMERGENCY free space cannot be mislabeled NORMAL.

No canonical PASS is claimed until an exact run containing `918c742e86c0567260f2fbc588efd8febd2114ea` (or a documentation-only descendant) completes green.

Status: `BACKEND_APPLIED / CANONICAL_PENDING`.

## Invariants retained

- emergency reserve release remains EMERGENCY-only and no canonical data is deleted;
- read-only safe-mode latching and noncritical-write gating remain unchanged;
- storage telemetry does not mutate SQLite/WAL state;
- no persistence format, transaction, recovery, fsync or Source-finalization semantics changed;
- valid Windows/Linux storage behavior remains unchanged;
- local model transport remains loopback-only, proxy-free and redirect-rejecting;
- response-size and total-deadline enforcement remain fail-closed;
- no new retries, routing behavior or cryptography;
- no silent Tor -> Direct fallback; Direct remains explicit-only;
- ExternalAccessGateway redirect authorization, HTTPS/default-port policy and compressed-response rejection unchanged;
- audit and provenance semantics unchanged;
- no Skip/XFail, assertion weakening or guard relaxation;
- no merge to `main`, force-push or history rewrite.

## Error / collision handoff

- Current Error handoff has `ERR-0014` IN_PROGRESS for a Qt/Desktop SIGSEGV on the UI worker lineage; Backend did not mutate that foreign owner path.
- No Backend blocker is introduced by ERR-0014; current DiskPressure work is disjoint.
- No UI/Core-owned files were mutated in this Backend run.

## Integrator handoff

- READY: ExternalAccessGateway runtime boundaries through `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6`, Quality `33884210684 = success`.
- READY: StorageHealth ASCII-control-detail through Backend head `1cc0017d560a1534de1fc2c83989d26e05238236`, Quality `33966299076 = success`.
- READY: Disk-pressure reserve-release-state through `8be678b5fa3e19aa442e788d935436914a53452b`, Quality `33972009715 = success`.
- READY: Disk-pressure released-volume-bound through `be13865f8ab863809a7da28a38e5c5df35b3fa29`, Quality `33974947204 = success`.
- READY: Disk-pressure threshold-consistency product `c0ee910a20fb396b0c20429f2da33873b407c641` + test `dde63f019c5ecd95d1805ff9c19fdd986fe4b436`, exact green descendant `5b04d7e335823f59bd33847e5b5c2c5b7e23458c`, Quality `33978168395 = success`.
- NOT READY: Disk-pressure assessment-state truth boundary product `deb69f03a5aa40e655e83bea1f69d6aeaa2b2af8` + test `918c742e86c0567260f2fbc588efd8febd2114ea` until exact canonical green evidence.

## Next backend slice

Consume the first exact canonical Quality run containing `918c742e86c0567260f2fbc588efd8febd2114ea` or its documentation-only descendant. If green, promote assessment-state truth to VERIFIED/READY and immediately take the highest current unclaimed disjoint Storage/Recovery/Provider/Packaging P0/P1/P2 runtime gap. If red, inspect exact diagnostics and repair only a Backend-owned failure. If no executable result binds next run, use an alternate executable verification path or a different real disjoint Backend/System slice rather than repeating the runner state.
