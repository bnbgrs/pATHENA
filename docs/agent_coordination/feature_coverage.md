# pATHENA Feature Coverage Matrix

Purpose: prevent repetitive rescans and drive systematic Alpha/Beta-to-code coverage.

Coverage states: `UNCHECKED` · `PARTIAL` · `COVERED` · `CHANGED_NEEDS_RECHECK`

Last matrix baseline: `agent/pathena` @ `4fec947c4de2d4f899fdaf33e07af7fc2205da57`

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
| A07 | Primary / infrastructure models | PARTIAL | 10e58e3 | Cross-checked through B08 provider scan; FG-001..FG-004. Full Alpha chapter trace still required. |
| A08 | Personal memory | UNCHECKED | — | — |
| A09 | Search / retrieval | UNCHECKED | — | — |
| A10 | Internet / anonymization / external sources | UNCHECKED | — | — |
| A11 | News / events | UNCHECKED | — | — |
| A12 | Background services / scheduler / tasks | UNCHECKED | — | — |
| A13 | Storage / synchronization / portability | UNCHECKED | — | — |
| A14 | Security / privacy / trust | UNCHECKED | — | — |
| A15 | Backup / restore / disaster recovery | UNCHECKED | — | — |
| A16 | Desktop application / UI | UNCHECKED | — | — |
| A17 | Update / version / compatibility | UNCHECKED | — | — |
| A18 | Plugin / extension system | UNCHECKED | — | Deferred by current product instructions unless needed for consistency. |
| A19 | Audit / provenance / traceability | UNCHECKED | — | — |
| A20 | Data lifecycle / retention / deletion | UNCHECKED | — | — |
| A21 | Model freedom / content neutrality | UNCHECKED | — | — |
| A22 | Context management / conversations / continuity | PARTIAL | 10e58e3 | ContextBuilderService, ContextPackage and durable package journal traced; FG-005/FG-006 found through B09. Full Alpha chapter trace pending. |
| A23 | Knowledge quality / consistency / self-maintenance | UNCHECKED | — | — |
| A24 | Performance / scaling / resources | UNCHECKED | — | — |
| A25 | Data formats / Obsidian / long-term readability | UNCHECKED | — | Obsidian implementation explicitly deferred; only consistency scan when reached. |
| A26 | Mobile future / multi-device | UNCHECKED | — | Future scope; classify against v1 roadmap before any implementation gap. |
| A27 | Recovery mode / diagnostics / errors | UNCHECKED | — | — |
| A28 | Roadmap / development boundaries / Beta transition | UNCHECKED | — | High value for STALE-vs-gap decisions. |
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
| B08 | Primary model / provider system | PARTIAL | 10e58e3 | Interface, domain health/capability representation, model tree and LM Studio adapter traced. FG-001 lifecycle/control; FG-002 ModelRegistry; FG-003 health states; FG-004 explicit capabilities. Continue ModelSignature, refusal/failure and provider-session semantics. |
| B09 | Context Builder / token budget | PARTIAL | 10e58e3 | ContextBuilderService + ContextPackage + durable package path traced. Existing memory isolation, snapshot drift, output/safety budget recording and semantic truncation preserved. FG-005 source diversity and FG-006 provider-aware dynamic token accounting confirmed. Continue call sites, protected-content behavior, task-specific builders, hierarchical processing and tests 60–68. |
| B10 | Retrieval / search | UNCHECKED | — | — |
| B11 | Exhaustive Research | UNCHECKED | — | — |
| B12 | Job system / queue / scheduler | UNCHECKED | — | — |
| B13 | Resource management | UNCHECKED | — | — |
| B14 | News / events | UNCHECKED | — | — |
| B15 | External Access Gateway / network | UNCHECKED | — | — |
| B16 | Security architecture / protected content | UNCHECKED | — | — |
| B17 | Plugin system / permissions | UNCHECKED | — | Deferred unless required for consistency. |
| B18 | Desktop application / tray | UNCHECKED | — | — |
| B19 | Core API / future clients | UNCHECKED | — | — |
| B20 | Obsidian / external editing | UNCHECKED | — | Implementation explicitly deferred; classify roadmap status before any FG. |
| B21 | Backup / restore | UNCHECKED | — | — |
| B22 | Recovery mode / diagnostics | UNCHECKED | — | — |
| B23 | Updates / migrations / compatibility | UNCHECKED | — | — |
| B24 | Logging / monitoring / observability | UNCHECKED | — | — |
| B25 | Repository / code structure | UNCHECKED | — | — |
| B26 | Test strategy | UNCHECKED | — | — |
| B27 | Development phases / vertical slices | UNCHECKED | — | High value for intentional deferral / STALE classification. |

## Next scan order

1. Read B27 and A28 now to classify intended v1 implementation boundaries before widening the backlog.
2. Finish B08 ModelSignature/refusal/session semantics.
3. Finish B09 call-site, protected-content, hierarchical and test coverage.
4. Then prioritize B01–B03 foundation and B15–B16 security/network invariants before breadth scanning UI-only features.
