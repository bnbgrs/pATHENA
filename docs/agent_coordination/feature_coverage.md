# pATHENA Feature Coverage Matrix

Purpose: prevent repetitive rescans and drive systematic Alpha/Beta-to-code coverage.

Coverage states: `UNCHECKED` · `PARTIAL` · `COVERED` · `CHANGED_NEEDS_RECHECK`

Last matrix baseline: `agent/pathena` @ `6c112216fcf618ca8399781c44ccba8d2bf29353`

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
| A13 | Storage / synchronization / portability | UNCHECKED | — | — |
| A14 | Security / privacy / trust | PARTIAL | 6c11221 | ProtectedContentService lock/unlock and fail-closed decryption traced while checking B09 protection-aware context integration. FG-012 identified. Full Alpha security chapter scan pending. |
| A15 | Backup / restore / disaster recovery | UNCHECKED | — | — |
| A16 | Desktop application / UI | PARTIAL | 6c11221 | Current model selector/settings path traced for B08. It exposes discovery/loaded state and generation controls but not the complete Beta Model Manager/switch/load/signature flow; see FG-011. Full desktop chapter scan pending. |
| A17 | Update / version / compatibility | UNCHECKED | — | — |
| A18 | Plugin / extension system | UNCHECKED | — | Deferred by current product instructions unless needed for consistency. |
| A19 | Audit / provenance / traceability | UNCHECKED | — | — |
| A20 | Data lifecycle / retention / deletion | UNCHECKED | — | — |
| A21 | Model freedom / content neutrality | UNCHECKED | — | — |
| A22 | Context management / conversations / continuity | PARTIAL | 6c11221 | ContextBuilderService, retrieval candidate contracts, protected-content boundary and durable package concerns traced. FG-005/FG-006 plus FG-012. Full Alpha chapter trace pending. |
| A23 | Knowledge quality / consistency / self-maintenance | UNCHECKED | — | — |
| A24 | Performance / scaling / resources | UNCHECKED | — | — |
| A25 | Data formats / Obsidian / long-term readability | UNCHECKED | — | Obsidian implementation explicitly deferred; only consistency scan when reached. |
| A26 | Mobile future / multi-device | UNCHECKED | 22b5f19 | B27 confirms mobile remote and v1 shared-write/CRDT work are intentionally later; do not open implementation gaps from those deferred requirements. Full Alpha chapter consistency scan remains. |
| A27 | Recovery mode / diagnostics / errors | UNCHECKED | — | — |
| A28 | Roadmap / development boundaries / Beta transition | COVERED | 22b5f19 | Alpha explicitly permits incremental first-version implementation and delegates concrete technical decisions to Beta. Missing long-term capabilities are not automatically current defects. |
| A29 | Immutable-rule summary | UNCHECKED | — | Non-normative summary; use as consistency check after normative chapters. |

## Beta Specification v0.1

| Chapter | Area | Status | Last checked commit | Findings / note |
|---|---|---|---|---|
| B01 | System architecture / technical basis | UNCHECKED | — | — |
| B02 | Persistent data model / IDs | UNCHECKED | — | — |
| B03 | Storage / databases / migrations | UNCHECKED | — | — |
| B04 | Sources / raw archive / import pipeline | UNCHECKED | — | — |
| B05 | Knowledge units / claims / graph | UNCHECKED | — | — |
| B06 | Personal memory | UNCHECKED | — | — |
| B07 | Provenance / audit / versioning | UNCHECKED | — | — |
| B08 | Primary model / provider system | PARTIAL | 6c11221 | Revalidated current domain, ports, ModelRegistry, ModelSignature/ProcessingRun, LM Studio adapter and desktop model controls. READY: FG-008 revision provenance, FG-009 ModelSession, FG-010 failure taxonomy. FG-011 records the MIXED/BLOCKED Model Manager/load/switch/signature UI gap; FG-001 lifecycle remains blocker. Continue exact load timeout/auto-load/resource-arbitration orchestration and provider contract tests. |
| B09 | Context Builder / token budget | PARTIAL | 6c11221 | ContextBuilderService and retrieval candidate contracts traced against protected-content requirements. Ordinary FTS explicitly excludes protected payloads; ProtectedContentService enforces runtime lock/decryption, but protection scope is not carried into Ranked/Hybrid/Context candidates. FG-012 READY for authorized unlocked protected retrieval-to-context integration. Existing diversity and dynamic budgeting findings retained. Continue hierarchical processing, task-specific builders, ContextPackage/cache and tests 60–68. |
| B10 | Retrieval / search | PARTIAL | 6c11221 | Unprotected SearchResult → RankedSearchResult → HybridSearchResult chain inspected while tracing FG-012; protected payloads are explicitly excluded from this projection and no protection-scope field crosses these contracts. Full retrieval chapter scan pending. |
| B11 | Exhaustive Research | UNCHECKED | — | — |
| B12 | Job system / queue / scheduler | UNCHECKED | — | — |
| B13 | Resource management | UNCHECKED | — | — |
| B14 | News / events | UNCHECKED | — | — |
| B15 | External Access Gateway / network | UNCHECKED | — | — |
| B16 | Security architecture / protected content | PARTIAL | 6c11221 | Runtime protection service traced: unlocked scopes are in-memory only; lock wipes keys; load_payload requires unlocked matching scope. Cross-layer protected retrieval/context integration remains absent in inspected contracts; see FG-012. Full B16 scan pending. |
| B17 | Plugin system / permissions | UNCHECKED | 22b5f19 | B27 places Plugins in a later vertical slice; current product instructions additionally defer plugin work. Scan only for security/architecture consistency until reprioritized. |
| B18 | Desktop application / tray | PARTIAL | 6c11221 | Model-control portion inspected for B08; current selector/settings represent availability/loaded state, but complete Model Manager lifecycle UI is not connected. Full B18 scan pending. |
| B19 | Core API / future clients | UNCHECKED | — | — |
| B20 | Obsidian / external editing | UNCHECKED | 22b5f19 | B27 places Obsidian in a later vertical slice; implementation remains explicitly deferred by current product instructions. Do not open current feature gaps unless required for architectural consistency. |
| B21 | Backup / restore | UNCHECKED | — | — |
| B22 | Recovery mode / diagnostics | UNCHECKED | — | — |
| B23 | Updates / migrations / compatibility | UNCHECKED | — | — |
| B24 | Logging / monitoring / observability | UNCHECKED | — | — |
| B25 | Repository / code structure | UNCHECKED | — | — |
| B26 | Test strategy | UNCHECKED | — | — |
| B27 | Development phases / vertical slices | COVERED | 22b5f19 | Full roadmap classified. Explicitly later: mobile remote client, multi-device shared write/CRDT, cloud sync, alternative DB, advanced graph DB and persistent encrypted protected vector index. Vertical-slice DoD requires tests, observability, security, docs and migrations where applicable. |

## Next scan order

1. Finish B09: hierarchical Map/Reduce, task-specific builders, ContextPackage/cache behavior and tests 60–68.
2. Finish B08 backend load timeout/auto-load/resource-arbitration orchestration and provider contract tests; leave FG-011 UI blocked until lifecycle contract stabilizes.
3. Deep-scan B16 protected-content architecture around unlocked retrieval, cache invalidation and logging boundaries to refine FG-012.
4. Scan B01–B03 foundation against current Core/storage/migrations.
