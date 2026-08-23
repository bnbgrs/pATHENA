# pATHENA Backend Queue

Persistent prioritized backend work queue for `agent/pathena`.
Status: `READY` · `IN_PROGRESS` · `BLOCKED` · `DONE` · `STALE`.
Last queue refresh: 2026-08-23.

## Active / ready work

### BE-028 — Clone/journal migration before live schema mutation
- Priority: P1
- Status: IN_PROGRESS
- Evidence: clone-first startup, reserve, candidate migration, journal, lock, activation and recovery stack are implemented. POSIX durable replace/byte publication/directory creation are parent-FD bound; recovery artifact presence classification uses no-follow file handles plus pathname/handle identity fencing. Remaining work is Windows HANDLE publication, SQLite clone destination binding and the Alembic-vs-custom decision.
- Components: migration storage stack, `storage/durable_fs.py`, `storage/migration_recovery.py`, `core/application.py`, tests.
- Dependencies: BE-027/029/031/032/033/034/035/040/042/043 DONE; BE-036/038/039 active.
- Last verification: 2026-08-23 current remote; focused storage run on the earlier durable-mkdir commit produced 172 passed / 4 stale-test failures / 2 skipped. Stale tests and the resulting own Ruff/mypy findings were subsequently corrected; no green rerun claimed yet.

### BE-036 — Close migration parent-replacement TOCTOU
- Priority: P1
- Status: IN_PROGRESS
- Evidence: POSIX replace/write/mkdir mutations are bound to opened parent directory FDs and fail closed on parent identity drift. Recovery regular-file classification is handle-bound. Deterministic race tests cover replace/open/mkdir plus recovery file replacement. Cross-platform closure still requires BE-038, BE-039 and reserve publication follow-up BE-046.
- Components: `storage/durable_fs.py`, `storage/migration_journal.py`, `storage/migration_recovery.py`, activation/recovery tests.
- Dependencies: BE-028; BE-035 DONE.
- Last verification: 2026-08-23; old pathname-instrumentation tests aligned in `11811fd`; Ruff B904 from the new mkdir branch corrected in `187af1f`; recovery enum mypy fallback corrected in `9abca48`.

### BE-038 — Windows HANDLE-bound durable filesystem publication
- Priority: P1
- Status: READY
- Evidence: Windows still uses pathname-based `MoveFileExW` after static reparse checks. Race closure needs source/destination HANDLE identity bound through mutation.
- Components: `storage/durable_fs.py`, Windows-only race tests, migration consumers.
- Dependencies: BE-036 POSIX primitives implemented.
- Last verification: 2026-08-23 current remote; prior Windows path-safety job was green but does not prove HANDLE-bound race closure.

### BE-039 — Bind migration SQLite clone destination to parent identity
- Priority: P1
- Status: READY
- Evidence: `create_migration_clone()` still calls `sqlite3.connect(candidate_path)` after pathname/reparse checks. Repeated checks do not close parent replacement between validation and SQLite open.
- Components: `storage/migration_clone.py`, coordinator, deterministic race tests.
- Dependencies: BE-036; platform-specific SQLite-compatible strategy required.
- Last verification: 2026-08-23 current remote.

### BE-046 — Bind Emergency Reserve publication/release to directory identity
- Priority: P1
- Status: READY
- Evidence: `EmergencyReserveStore` still creates the reserve file and releases it through pathname-based open/unlink after boundary checks. A parent replacement can redirect reserve allocation or deletion. Fix must preserve physical non-sparse allocation, fsync durability, Windows support and exact release accounting.
- Components: `storage/emergency_reserve.py`, `storage/durable_fs.py` shared primitives if appropriate, disk-pressure tests.
- Dependencies: BE-036 parent-identity primitives; avoid partial check-then-open fixes.
- Last verification: 2026-08-23 current remote audit.

### BE-020 — Runtime ModelSignature drift guard in generation
- Priority: P1
- Status: READY
- Evidence: reusable revision-aware guard exists; shared `chat/generation.py` still uses older inline comparison.
- Components: chat generation/signature guard/tests.
- Dependencies: safe mutation window for shared generation file.

### BE-021 — ContextPackage temperature conversion overflow
- Priority: P2
- Status: READY
- Evidence: extreme JSON integer can escape the ContextPackage error contract via `float()` OverflowError.
- Components: `retrieval/context_package.py`, tests.
- Dependencies: safe mutation window for shared file.

### BE-048 — Make Research domain scalar validation type-stable
- Priority: P2
- Status: READY
- Evidence: current quality evidence reports `research/models.py` strict-mypy failures in `_positive_int` and a reused loop variable. Runtime validation is mostly sound, but helpers should return validated ints and validation loops should use type-stable local names so strict typing proves the intended contracts.
- Components: `research/models.py`, targeted model boundary tests.
- Dependencies: safe mutation window for the central Research model file.
- Last verification: 2026-08-23 quality log from focused branch run.

## Recently completed backend/storage slices

### BE-047 — Require exact integers in persisted semantic index state
- Priority: P2
- Status: DONE
- Evidence: Semantic Derived State previously used `int(value)` and therefore accepted numeric strings/floats/objects from corrupted rows. `_persisted_int` now requires a real non-bool `int` and preserves positive/nonnegative bounds. This also removes the strict-mypy ambiguity from the conversion path.
- Components: `retrieval/semantic.py`.
- Last verification: 2026-08-23 current remote after `682864b`; no green rerun claimed.

### BE-045 — Preserve model revision in durable Grounded ContextPackage journal
- Priority: P1
- Status: DONE
- Evidence: Grounded ContextPackage encoding omitted `ContextModelSignature.model_revision`, so retries could lose exact provider revision provenance. New payloads persist it; decoding uses optional field semantics so existing format-v1 rows without the field remain backward compatible as `None`. Roundtrip and legacy decode regressions added.
- Components: `chat/grounded_context_package.py`, `tests/unit/test_grounded_context_package_model_revision.py`.
- Last verification: 2026-08-23 current remote after `9e6001c` / `c32b405`; no green rerun claimed.

### BE-044 — Restore ChatKnowledgeExtraction application wiring
- Priority: P1
- Status: DONE
- Evidence: Core smoke exposed `ChatKnowledgeExtractionService.__init__()` missing required keyword-only `chat`; strict mypy reported the same application line. `AthenaApplication` now passes its canonical `ChatService` explicitly. Commit diff was re-read and confirmed to contain exactly the one intended wiring line; construction regression added.
- Components: `core/application.py`, `tests/unit/test_application_wiring.py`.
- Last verification: 2026-08-23 current remote after `cc0ec3a` / `79c517f`; no green rerun claimed.

### BE-043 — Handle-bound migration recovery artifact classification
- Priority: P1
- Status: DONE
- Evidence: recovery presence checks open source/candidate/rollback with `O_NOFOLLOW` when available, require regular `fstat`, re-check boundaries and compare opened-handle identity with `lstat` via `samestat`. Replacement/disappearance during classification fails closed. Mypy-unreachable fallback was subsequently made reachable by branching on persisted phase values, preserving future fail-closed behavior.
- Components: `storage/migration_recovery.py`, tests.
- Last verification: 2026-08-23 current remote through `9abca48`; no green rerun claimed.

### BE-042 — Recheck disk pressure immediately before live writer startup
- Priority: P1
- Status: DONE
- Evidence: after optional clone migration, bootstrap performs a final `DiskPressureController.check()` immediately before `SQLiteDatabase.start()`. If the volume entered EMERGENCY, reserve is released, safe mode remains latched and writable startup is refused.
- Components: `storage/bootstrap.py`, tests.
- Last verification: 2026-08-23 current remote after `62658b9` / `7a0d9fc`; no green rerun claimed.

### BE-041 — Verify SQLite runtime connection policy
- Priority: P1
- Status: DONE
- Evidence: bounded 5,000–120,000 ms busy timeout; live connection applies and reads back `foreign_keys=ON`, exact `busy_timeout`, `trusted_schema=OFF`; mismatch fails closed. `SQLiteDatabase` uses the same timeout for connect and post-schema policy verification.
- Components: `storage/connection_policy.py`, `storage/database.py`, tests.
- Last verification: 2026-08-23; associated gate was cancelled, no pass claimed.

### BE-040 — Bind POSIX durable mkdir to parent identity
- Priority: P1
- Status: DONE
- Evidence: child creation uses `os.mkdir(..., dir_fd=opened_parent_fd)`, fsyncs that parent FD and checks parent identity before return. Race and nested creation regressions exist. Own Ruff B904 exception-chain finding corrected without changing semantics.
- Components: `storage/durable_fs.py`, durable-fs tests.
- Last verification: 2026-08-23 current remote through `187af1f`; no green rerun claimed.

### BE-049 — Make Research synthesis idempotency runtime guards effective
- Priority: P2
- Status: DONE
- Evidence: private synthesis idempotency inputs/descriptor were annotated narrowly enough that runtime type guards became statically unreachable. Boundary parameters now accept `object`, then narrow explicitly to non-string Sequence and Mapping before deterministic identity construction. Invalid external/runtime values continue to fail before hash generation.
- Components: `research/idempotency.py`.
- Last verification: 2026-08-23 current remote after `a30a369`; no green rerun claimed.

### BE-050 — Make ModelRegistry resource validation type-stable
- Priority: P2
- Status: DONE
- Evidence: mixed validation loops caused incompatible inferred types and unreachable numeric branches. Dedicated optional-int/optional-number validators now preserve bool rejection, finite/nonnegative checks and overflow handling while making each resource contract explicit.
- Components: `model/registry.py`.
- Last verification: 2026-08-23 current remote after `2090bb7`; no green rerun claimed.

### BE-034 — Bound migration journal reads before JSON decode
- Priority: P2
- Status: DONE
- Evidence: journal reads/writes capped at 64 KiB with handle identity and bounded reads.

### BE-035 — Bind migration lock to migration-root identity
- Priority: P1
- Status: DONE
- Evidence: parent-level lock plus root identity fencing before/after critical section.

### BE-029 — Physically allocated Emergency Reserve
- Priority: P1
- Status: DONE

### BE-030 — Disk-pressure state controller and runtime write gate
- Priority: P1
- Status: DONE

### BE-031 — Candidate-only schema executor
- Priority: P1
- Status: DONE

### BE-032 — Read-only startup migration planner
- Priority: P1
- Status: DONE

### BE-033 — Integrate safe storage bootstrap ordering
- Priority: P1
- Status: DONE

### BE-037 — Bound backup deletion-ledger resource usage
- Priority: P2
- Status: DONE

## Blocked / in-progress older slices

- BE-002 · P1 · BLOCKED — provider lifecycle/control adapter completion; shared LM Studio adapter ownership window required.
- BE-008 · P2 · BLOCKED — auditable primary-model switch needs durable audit contract.
- BE-009 · P2 · BLOCKED — provider request cancellation needs exact backend request-ID plumbing.
- BE-010 · P2 · IN_PROGRESS — generation numeric/control boundaries; shared generation path remains.
- BE-013 · P1 · BLOCKED — ModelSession exact provider binding remains.
- BE-014 · P1 · IN_PROGRESS — revision-aware ContextPackage/drift guard; generation integration remains.
- BE-015 · P1 · BLOCKED — provider failure taxonomy mapping needs adapter ownership.
- BE-016 · P1 · IN_PROGRESS — protected retrieval execution exists; explicit protected generation/persistence policy remains.
- BE-019 · P2 · BLOCKED — provider identity canonicalization must be atomic with adapter parsing.

## Completed / stale reference

- BE-001 DONE — normative provider health states.
- BE-003 DONE — normalized provider capabilities.
- BE-004 DONE — Context Builder source diversity.
- BE-005 STALE — provider-aware dynamic token accounting already present.
- BE-006 DONE — active primary ModelRegistry.
- BE-007 DONE — model load ownership.
- BE-011 DONE — BlobStore/durable FS symlink+junction confinement.
- BE-012 DONE — provider-observed model revision in signatures.
- BE-017 DONE — ModelSession cancellation invariants.
- BE-018 DONE — UUIDv7 clock-range guard.
- BE-022 DONE — persistent wall-clock int64 guard.
- BE-023 DONE — Unicode line-control rejection in schema IDs.
- BE-024 DONE — runtime mutation lock identity/permissions.
- BE-025 DONE — backup target lock identity.
- BE-026 DONE — reject network-backed active SQLite state.
- BE-027 DONE — clone-migration metadata/free-space contract.
