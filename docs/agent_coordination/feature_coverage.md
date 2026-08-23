# pATHENA Feature Coverage Matrix

Purpose: prevent repetitive rescans and drive systematic Alpha/Beta-to-code coverage.

Coverage states: `UNCHECKED` · `PARTIAL` · `COVERED` · `CHANGED_NEEDS_RECHECK`

Last matrix baseline: `agent/pathena` @ `c2f4b5164929707b6ee7f362ead0d7624765b80c`

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
| A07 | Primary / infrastructure models | PARTIAL | d7a6342 | Cross-checked through Beta 08 provider scan; FG-001, FG-002. Full Alpha chapter trace still required. |
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
| A22 | Context management / conversations / continuity | PARTIAL | d7a6342 | Existing retrieval/chat ContextPackage path located; full cross-layer trace pending. |
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
| B08 | Primary model / provider system | PARTIAL | d7a6342 | Provider interface + model tree traced. FG-001 lifecycle/control contract; FG-002 ModelRegistry. Continue capability reporting, ModelSignature and failure/refusal sections next. |
| B09 | Context Builder / token budget | PARTIAL | d7a6342 | Spec read; `src/athena/retrieval/context_package.py` and durable `src/athena/chat/grounded_context_package.py` located. No gap declared before full builder/retrieval/call-site trace. |
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

1. Finish B08: capability reporting, ModelSignature, refusal/failure, session/load semantics.
2. Finish B09 cross-layer Context Builder trace before declaring additional gaps.
3. Read B27 and A28 to classify intended v1 implementation phase boundaries, preventing false-positive gaps.
4. Then prioritize B01–B03 foundation and B15–B16 security/network invariants before breadth scanning UI-only features.
