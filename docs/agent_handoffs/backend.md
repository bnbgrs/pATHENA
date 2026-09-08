# pATHENA Backend & Systems Handoff

## Baseline

- Shared baseline: `develop/pathena-next@1e6b3b17117c938f5aee26c9797432959a4544c9`.
- Pre-run worker: `postmerge/backend@55a6e95486c8b7501f27ed07748dc922803025ea`.
- Previous exact Backend Quality: `34226856389 = failure`; the known shared canonical-pytest failure remains tracked under `ERR-0025` and no exact Backend-primary traceback was established.
- Current coordination heads reviewed: errors `476fb6f2360529ea330abc0ff9d310a8644e5b6c`; spec-core `ebb0c1f9a6c230395f0ea6468c167f9d61565938`; UI `932face973987d84a44c5d37fc61509285466279`; integrator from exact Develop `1e6b3b17117c938f5aee26c9797432959a4544c9`.
- History-preserving NON-FORCE sync commit: `0dea708ebedfac077a24ed32ca8aa4b52a18c0b1`, parents prior Backend and exact current Develop. Develop-only `integrator.md`, `ALPHA_BETA_PROGRESS.md`, and UI-owned `pathena_settings_runtime.py` were imported byte-identically while Backend work was preserved.
- `main` and `bnbgrs/ATHENA` remain untouched/read-only.

## ExternalAccessGateway priority

Exact current Develop already contains the requested fail-before-side-effect runtime boundaries and tests: `ttl_seconds` and `max_bytes` reject bool and require genuine ints; `timeout_seconds` rejects bool, non-numeric, NaN and infinities while preserving valid ranges. The prepared patch was not duplicated.

## Current Backend slice — Exhaustive Research §75 durable Delta lower boundary

Spec/Core identified a real persistence gap: `ResearchMode.DELTA` existed, but a Research scope persisted only its upper `snapshot_commit_seq`, so a restart-safe Delta run could not truthfully identify the prior completed snapshot or distinguish newly imported Sources without guessing from wall-clock metadata.

The Backend now supplies the smallest explicit durable representation:

- `schema_contract.py` advances the schema from v40 to v41 with migration id `0041_research_delta_boundary`.
- `research_delta_migration.py` adds `research_delta_boundaries(scope_id, base_scope_id, lower_commit_seq, created_at_us)` plus an index, foreign keys and fail-closed schema verification.
- v40→v41 is an additive `BEGIN IMMEDIATE` migration. Input v40 is verified before mutation; metadata/user_version are advanced transactionally; fresh start and subsequent restart both verify v41 rather than silently reapplying the migration.
- v41 preserves the complete v40 Grounded-response receipt checks in addition to all inherited v39 contracts.
- `ResearchDeltaBoundaryRepository` persists one exact completed baseline scope and requires `lower_commit_seq == base_scope.snapshot_commit_seq <= delta_scope.snapshot_commit_seq`. The target must be `ResearchMode.DELTA`; the baseline must be `COMPLETED`; mismatched rebinding fails closed.
- No timestamp, internet-scope or in-memory surrogate is used as a lower-bound substitute.

Product lineage:

- `da3b4421079197332a6e35860b544ca5bde82a21` — add v41 migration module.
- `4c8f5e415244355a963ac5b898d240e6b5a09f78` — advance stable schema contract to v41.
- `5d72196d109699783e2013c564011ad9fc941e80` — wire v40→v41 startup migration and final v41 verification.
- `156452d3f03757cfc4e96c1afc46c3f1be12351d` — add durable Research Delta boundary repository/record.
- `ea51c8340de7fe63d96ed6eb720ab8359b40b02e` — add focused fresh-DB/restart and exact row-mapping regression.
- `e81957a388763d3b5931df694a06908a0ba29f75` — preserve complete v40 Grounded-receipt verification under v41.

## Verification

- Previous exact Quality `34226856389`: FAILURE; no new Backend-primary attribution.
- Intermediate Quality runs for superseded commits were cancelled by newer worker commits.
- Exact functional head `e81957a388763d3b5931df694a06908a0ba29f75`: Quality `34233916176 = pending` at handoff creation.
- Focused regression source: `tests/unit/test_research_delta_boundary_persistence.py`, covering fresh database v41 creation, migration metadata/table shape, explicit `verify_schema_v41`, restart verification and exact UUID/lower-bound row mapping.
- No current-head PASS, global-green or promotion-ready claim is made.
- No Skip/XFail, assertion weakening or safety-guard relaxation was introduced.

## Invariants retained

- Delta lower boundary is explicit persisted provenance, never inferred from wall-clock timestamps.
- A Delta scope can bind only to an existing completed baseline scope.
- Lower commit must exactly equal the baseline snapshot and cannot exceed the Delta upper snapshot.
- Existing exact binding is idempotent; conflicting rebind fails closed before durable mutation.
- v40 database compatibility is verified before migration; v41 is additive and restart-verifiable.
- no silent Tor→Direct fallback; Direct fallback explicit only;
- no loopback/private proxy leak; redirects re-authorized before fetch;
- HTTPS/default-port, compressed-response and response-size handling fail closed;
- Audit/Provenance/fsync/transactional Source finalization unchanged;
- PASSIVE-only automatic WAL maintenance; explicit idle-only TRUNCATE; no manual WAL deletion;
- existing WAL-aware scheduler composition and PROVIDER isolation unchanged;
- no new scheduler process/loop/thread/timer/retry;
- packaging/lane-lock/process-tree/DirectChat/network/crypto semantics unchanged;
- no force push, rebase, history rewrite or main mutation.

## Release regression knowledge

Historical Windows/runtime signatures remain regression obligations only absent exact-current reproduction: pypdf metadata/frozen argv routing; two-EXE Desktop/Worker split and bounded process tree; adaptive small-context DirectChat reserve; lane-lock `PermissionError` → `SchedulerLaneOwnershipError` → packaged-worker `OSError`; duplicate-column startup; Core startup failure; storage-bootstrap failure.

## Spec/Core handoff

The §75 persistence prerequisite is now implemented pending exact Quality. Once the Backend v41 lineage is exact-green, Core can add the smallest Delta enqueue/application/repository composition and candidate selection over `(lower_commit_seq, snapshot_commit_seq]`, preserving normal scope filters/dedup and restart identity.

## Next Backend action

Consume exact Quality `34233916176` for `e81957a388763d3b5931df694a06908a0ba29f75` or this documentation-only descendant. If Backend-owned migration/storage gates are green, mark the v41 durable Delta-boundary prerequisite VERIFIED/INTEGRATOR_READY and run/consume the smallest schema-migration/restart/Research plus ExternalAccessGateway/network-security regression evidence needed for handoff. If an exact Backend-owned failure appears, repair only that primary failure. If canonical pytest remains red solely under shared `ERR-0025`, do not mutate speculatively; proceed to the next independent evidence-backed Backend/Recovery/Provider/Platform gap while Core consumes §75.