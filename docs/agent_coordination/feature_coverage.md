# pATHENA Feature Coverage Matrix

Purpose: prevent repetitive rescans and drive systematic Alpha/Beta-to-code coverage.

Coverage states: `UNCHECKED` · `PARTIAL` · `COVERED` · `CHANGED_NEEDS_RECHECK`

Last matrix baseline: `agent/pathena` @ `a82254ff1decda8082925329d8f3ec9077d7c612`

A `COVERED` row may be rescanned only when its specification or mapped implementation paths changed after the recorded commit. `PARTIAL` means useful code tracing was completed but the full chapter/cross-layer path was not yet exhausted.

## Alpha v2.0.1 Final

| Chapter | Area | Status | Last checked commit | Findings / note |
|---|---|---|---|---|
| A01 | Vision / identity | UNCHECKED | — | — |
| A02 | Philosophy / principles | UNCHECKED | — | — |
| A03 | System architecture | UNCHECKED | — | — |
| A04 | Knowledge system | UNCHECKED | — | — |
| A05 | Raw archive / sources | UNCHECKED | — | — |
| A06 | Knowledge extraction / graph | UNCHECKED | — | — |
| A07 | Primary / infrastructure models | PARTIAL | 6c11221 | B08 traced across provider domain/ports/registry/provenance/LM Studio adapter and current desktop model controls. FG-001..FG-004 and FG-007..FG-011 cover lifecycle, registry, health/capabilities, load ownership, revision provenance, ModelSession, failure taxonomy and incomplete model-management UI. Full Alpha chapter trace still required. |
| A08 | Personal memory | UNCHECKED | — | — |
| A09 | Search / retrieval | UNCHECKED | — | — |
| A10 | Internet / anonymization / external sources | UNCHECKED | — | — |
| A11 | News / events | UNCHECKED | — | — |
| A12 | Background services / scheduler / tasks | UNCHECKED | — | — |
| A13 | Storage / synchronization / portability | PARTIAL | a82254f | Storage bootstrap enforces local-state safety, provisions the emergency reserve before migration/database startup, routes legacy schemas through clone migration, and preserves rollback/recovery boundaries. FG-014 and FG-015 are implemented. B03 connection-policy revalidation identified FG-016; long-term sync/replication/portability remains unscanned. |
| A14 | Security / privacy / trust | PARTIAL | 6c11221 | ProtectedContentService lock/unlock and fail-closed decryption traced while checking B09 protection-aware context integration. FG-012 identified. Full Alpha security chapter scan pending. |
| A15 | Backup / restore / disaster recovery | UNCHECKED | — | — |
| A16 | Desktop application / UI | PARTIAL | 6c11221 | Current model selector/settings path traced for B08. It exposes discovery/loaded state and generation controls but not the complete Beta Model Manager/switch/load/signature flow; see FG-011. Full desktop chapter scan pending. |
| A17 | Update / version / compatibility | UNCHECKED | — | — |
| A18 | Plugin / extension system | UNCHECKED | — | Deferred by current product instructions unless needed for consistency. |
| A19 | Audit / provenance / traceability | UNCHECKED | — | — |
| A20 | Data lifecycle / retention / deletion | UNCHECKED | — | — |
| A21 | Model freedom / content neutrality | UNCHECKED | — | — |
| A22 | Context management / conversations / continuity | PARTIAL | 528e901 | ContextBuilderService plus async retrieval ContextBuilder, ContextPackage, Research synthesis map/reduce, protected-content boundary and durable package concerns traced. FG-005 is implemented; FG-006 is stale after dynamic chat budgeting revalidation; FG-012 remains in progress for protected generation orchestration. Full Alpha chapter trace pending. |
| A23 | Knowledge quality / consistency / self-maintenance | UNCHECKED | — | — |
| A24 | Performance / scaling / resources | PARTIAL | a82254f | Disk-pressure runtime path was revalidated end-to-end: bootstrap binds the pressure controller into `SQLiteDatabase`, and every canonical `write_transaction()` evaluates the gate before `BEGIN IMMEDIATE`; dedicated pressure regressions cover ordinary-write blocking plus explicit recovery writes. FG-015 is IMPLEMENTED. Broader CPU/GPU/model resource arbitration remains unscanned. |
| A25 | Data formats / Obsidian / long-term readability | UNCHECKED | — | Obsidian implementation explicitly deferred; only consistency scan when reached. |
| A26 | Mobile future / multi-device | UNCHECKED | 22b5f19 | B27 confirms mobile remote and v1 shared-write/CRDT work are intentionally later; do not open implementation gaps from those deferred requirements. Full Alpha chapter consistency scan remains. |
| A27 | Recovery mode / diagnostics / errors | PARTIAL | ab412d5 | Storage startup detects migration recovery artifacts, refuses unsafe writable continuation, distinguishes explicit recovery-required from disk-pressure read-only-required startup, and preserves reserve space for controlled recovery. Full recovery-mode UX/diagnostics/error-surface scan remains. |
| A28 | Roadmap / development boundaries / Beta transition | COVERED | 22b5f19 | Alpha explicitly permits incremental first-version implementation and delegates concrete technical decisions to Beta. Missing long-term capabilities are not automatically current defects. |
| A29 | Immutable-rule summary | UNCHECKED | — | Non-normative summary; use as consistency check after normative chapters. |

## Beta Specification v0.1

| Chapter | Area | Status | Last checked commit | Findings / note |
|---|---|---|---|---|
| B01 | System architecture / technical basis | PARTIAL | 528e901 | First architecture trace completed. `src/athena/api/server.py` implements a loopback-only Core API listener on `127.0.0.1`, and the API surface uses `/api/v1/...` routes, matching B01 local-binding/versioning requirements. The repository is already split into Core/API/UI/model/knowledge/jobs/config/external/etc. modules rather than microservices. Full trace still required for isolated worker failure boundaries, resource manager integration, authoritative-write routing and long-running checkpoint semantics. No new gap opened from this partial trace. |
| B02 | Persistent data model / IDs | PARTIAL | 528e901 | Initial identity trace completed. Beta requires stable UUIDv7 identities independent of path/content; `src/athena/common/ids.py` implements RFC-9562 UUIDv7 generation plus canonical 16-byte conversion. This confirms the ID primitive rather than merely documenting it. Full cross-domain entity/revision/provenance/durable-state invariant scan remains. |
| B03 | Storage / databases / migrations | PARTIAL | a82254f | Live-runtime storage semantics were advanced. Product startup configures the disk-pressure gate before SQLite starts; canonical writes invoke it before `BEGIN IMMEDIATE`, so FG-015 is IMPLEMENTED rather than an open integration gap. `_configure_connection()` matches the Beta values for WAL, `foreign_keys`, `synchronous=FULL`, `busy_timeout=5000`, `secure_delete`, `read_uncommitted`, `wal_autocheckpoint=1000` and `trusted_schema=OFF`, and it explicitly verifies WAL mode. Beta 03 nevertheless requires readback of `foreign_keys` and `trusted_schema`; the current path does not verify those values, and busy_timeout is fixed rather than configurable. FG-016 records this narrow BACKEND handoff. FG-013 remains the Alembic-vs-custom architecture decision. Remaining B03 scan: WAL-size monitoring/checkpoint policy, incremental-vacuum policy, live corruption/disk-full behavior, backup/restore interaction and long-term replication semantics. |
| B04 | Sources / raw archive / import pipeline | UNCHECKED | — | — |
| B05 | Knowledge units / claims / graph | UNCHECKED | — | — |
| B06 | Personal memory | UNCHECKED | — | — |
| B07 | Provenance / audit / versioning | UNCHECKED | — | — |
| B08 | Primary model / provider system | PARTIAL | 6c11221 | Revalidated current domain, ports, ModelRegistry, ModelSignature/ProcessingRun, LM Studio adapter and desktop model controls. FG-002/003/004/005/007/008 are implemented or later reclassified as appropriate; FG-001 is blocked on adapter ownership, FG-009/010 remain partial, and FG-011 records the MIXED/BLOCKED Model Manager/load/switch/signature UI gap. Continue exact load timeout/auto-load/resource-arbitration orchestration and provider contract tests. |
| B09 | Context Builder / token budget | PARTIAL | 528e901 | Deeper trace completed. `ContextPackage` already carries request ID, pinned ModelSignature, purpose, separated context sections, included refs, excluded summary, token estimates, explicit budget and optional snapshot commit sequence; audit serialization omits cleartext. Current ContextBuilder paths implement source-diversity ordering and semantic shrink/truncation. Research `SynthesisService` performs per-query map work followed by reduce synthesis, so hierarchical processing is behaviorally present rather than absent. FG-005 is IMPLEMENTED, not a READY gap; its visible legacy unit file does not itself provide an explicit source-diversity regression, so VERIFIED is not claimed here. Caching is optional in the spec and its absence alone is not a defect. Remaining scan: task-specific builder coverage, protected generation boundary, and tests 60–68 / equivalent modern regressions. |
| B10 | Retrieval / search | PARTIAL | 6c11221 | Unprotected SearchResult → RankedSearchResult → HybridSearchResult chain inspected while tracing FG-012; protected payloads are explicitly excluded from this projection and no protection-scope field crosses these contracts. Full retrieval chapter scan pending. |
| B11 | Exhaustive Research | PARTIAL | 528e901 | While tracing B09 hierarchical processing, `research/synthesis_service.py` was confirmed to execute per-query research units and reduce their representative results into a final synthesis context. This establishes real map/reduce-style behavior and provenance-carrying intermediate aggregation. Full B11 exhaustive-research requirements remain unscanned. |
| B12 | Job system / queue / scheduler | UNCHECKED | — | — |
| B13 | Resource management | PARTIAL | a82254f | Storage-resource slice now has end-to-end live-write arbitration: deterministic disk-pressure thresholds, physical reserve ownership/lifecycle, startup refusal at EMERGENCY, bootstrap binding of `assert_noncritical_write_allowed`, and pre-transaction enforcement in `SQLiteDatabase.write_transaction()`. FG-015 is IMPLEMENTED; broader GPU/model/process resource arbitration remains unscanned. |
| B14 | News / events | UNCHECKED | — | — |
| B15 | External Access Gateway / network | UNCHECKED | — | — |
| B16 | Security architecture / protected content | PARTIAL | 6c11221 | Runtime protection service traced: unlocked scopes are in-memory only; lock wipes keys; load_payload requires unlocked matching scope. Dedicated protected runtime retrieval and execution-guard boundaries now exist; FG-012 is IN_PROGRESS for an actual model-call orchestration path plus deliberate persistence policy. Full B16 scan pending. |
| B17 | Plugin system / permissions | UNCHECKED | 22b5f19 | B27 places Plugins in a later vertical slice; current product instructions additionally defer plugin work. Scan only for security/architecture consistency until reprioritized. |
| B18 | Desktop application / tray | PARTIAL | 6c11221 | Model-control portion inspected for B08; current selector/settings represent availability/loaded state, but complete Model Manager lifecycle UI is not connected. Full B18 scan pending. |
| B19 | Core API / future clients | PARTIAL | 528e901 | B01 trace confirmed a real local Core API implementation with loopback-only listener and versioned `/api/v1` routes. Full B19 contract/versioning/authentication/future-client scan remains. |
| B20 | Obsidian / external editing | UNCHECKED | 22b5f19 | B27 places Obsidian in a later vertical slice; implementation remains explicitly deferred by current product instructions. Do not open current feature gaps unless required for architectural consistency. |
| B21 | Backup / restore | UNCHECKED | — | — |
| B22 | Recovery mode / diagnostics | PARTIAL | ab412d5 | Storage bootstrap recovery boundary traced. Migration artifacts requiring manual review fail closed before writable startup; EMERGENCY pressure yields a distinct read-only-required condition and preserves released reserve space for recovery. Full recovery-mode command/UI/diagnostic flow remains unscanned. |
| B23 | Updates / migrations / compatibility | PARTIAL | ab412d5 | Migration compatibility path includes read-only preflight, versioned migration planning, clone execution, external durable phase journal, exclusive lock, candidate verification, rollback-preserving activation and recovery assessment. FG-013 no longer represents missing startup integration; it is limited to the explicit Alembic-vs-custom architecture decision. Full software-update/version compatibility chapter remains pending. |
| B24 | Logging / monitoring / observability | UNCHECKED | — | — |
| B25 | Repository / code structure | UNCHECKED | — | — |
| B26 | Test strategy | UNCHECKED | — | — |
| B27 | Development phases / vertical slices | COVERED | 22b5f19 | Full roadmap classified. Explicitly later: mobile remote client, multi-device shared write/CRDT, cloud sync, alternative DB, advanced graph DB and persistent encrypted protected vector index. Vertical-slice DoD requires tests, observability, security, docs and migrations where applicable. |

## Next scan order

1. Continue B03 with WAL-size monitoring/checkpoint policy and incremental-vacuum policy; FG-015 is closed to IMPLEMENTED and must not be rescanned unless relevant code changes.
2. Deep-scan B16 provider bridge/generated-content persistence/relock invalidation/logging boundaries for FG-012.
3. Finish B09 task-specific builder/test coverage and correlate modern regressions to normative tests 60–68; do not reopen already-implemented source diversity or Research map/reduce.
4. Scan B21 backup/restore and cross-link B03 corruption/restore invariants.
5. Continue B01 into process isolation/resource management/authoritative-write/checkpoint boundaries and cross-link B12/B13.
6. Continue B02 cross-domain entity/revision/provenance and durable-state invariants.
