# pATHENA Alpha / Beta Progress

Evidence-backed post-merge development tracker for `develop/pathena-next`.

Status values: `MISSING`, `PARTIAL`, `IMPLEMENTED_PENDING_VERIFY`, `VERIFIED`.

| Capability / contract | Spec / evidence anchor | Status | Current evidence | Owner / next action |
|---|---|---|---|---|
| Normal hybrid retrieval / RRF | Beta Retrieval §§24–26, §64 | `VERIFIED` | Deterministic hybrid/RRF implementation is present on Develop. | Core continues response/provenance coverage. |
| Search response retrieval-method provenance | Beta Retrieval §34, §52 | `VERIFIED` | Canonical retrieval-method provenance is preserved and tested. | Core. |
| Search response final rank | Beta Retrieval §52 | `VERIFIED` | Final returned hybrid results carry contiguous final rank. | Core. |
| Archive Search source-anchor provenance | Beta Retrieval §34, §52 | `VERIFIED` | Verified archive representation/offset/hash provenance is preserved without fabricated persisted anchor IDs. | Core. |
| Search response protection-state provenance | Beta Retrieval §§52, 59–61 | `VERIFIED` | Protected/unprotected classification and real scope provenance are fail-closed. | Core. |
| Canonical Search API DTO + normal-Hybrid adapter | Beta Retrieval §52 | `VERIFIED` | Canonical `SearchResultResponse` mapping is integrated and verified. | Core. |
| Normal-Hybrid facade/application composition | Beta Retrieval §52 | `VERIFIED` | One-time attachment, capability gating, exact delegation and application identity wiring are integrated; combined Develop validation `33799110483` passed. | Core proceeds to next gap. |
| Temporal contradiction disjoint-window policy | Beta Knowledge/Claims §§56, 58, 60, 69–70 | `VERIFIED` | Deterministic disjoint-window suppression policy is integrated; exact worker Quality `33801697326` passed. | Core composes policy into contradiction review. |
| Canonical contradiction-review exact-revision adapter | Beta Knowledge/Claims §§56, 58, 60, 69–70 | `IMPLEMENTED_PENDING_VERIFY` | Exact revision adapter itself previously passed `33812392688`; current ProposalAcceptanceService temporal-gate composition has bounded product/test commits but run `33825883574` was cancelled. | Core must provide fresh exact-green composition evidence before integration. |
| Resource policy runtime mutation boundary | Backend audit task 289 | `VERIFIED` | `ResourceManager.set_mode()` rejects invalid runtime values before local-user/database side effects. | Backend. |
| ExternalAccessGateway exact runtime-type policy boundaries | Gateway hardening | `VERIFIED` | Bool-safe TTL/max-bytes and finite non-bool timeout validation integrated; exact product Quality `33790984890` and combined Develop `33799110483` passed. | Backend. |
| ExternalAccessGateway authorization/runtime fail-before-side-effect boundaries | Backend audit findings 295–296 | `VERIFIED` | Purpose/allowed-host/privacy-route/Direct-host/Direct-TTL boundary bundle integrated as `c8cf496def52629df341196613bc6c30409aa44a`; canonical combined Develop validation `33815279390` completed `success`. | Backend proceeds to next runtime boundary. |
| ExternalAccessGateway capture-URL runtime text boundary | Backend handoff | `VERIFIED` | Backend product/test blobs from `07782c78d6e2cb1e9f4bfb6bf9175c9fb041a806` are integrated on Develop as `071a60e898710239e7d7ea9ec399bd75f8f9bf61`; canonical Quality `33822032100` passed on synchronized worker SHA `6eb421cf5efc510898006868bfc475c7928bc32b`, whose Gateway/test blob SHAs exactly match the integrated blobs. | Backend proceeds to ExternalResearch URL-container boundary. |
| Deletion-ledger runtime boundaries / recovery cursor | ERR-0001 + Backend tasks 290–293 | `VERIFIED` | Exact-type/bool-safe fail-before-SQL validation integrated and verified. | Error/Backend scan for recurrence only. |
| Grounded Chat inspector hierarchy / Evidence & Activity copy | UI-GAP-0001 | `VERIFIED` | Hierarchy/copy integrated and canonical-green. | UI continues screen gaps. |
| Contextual inspector visibility | UI-GAP-0002 | `VERIFIED` | Context-sensitive inspector visibility integrated and canonical-green. | UI. |
| PALLAS tab-order lifecycle resilience | UI-GAP-0003 | `VERIFIED` | Transient missing document binding is a safe no-op lifecycle state; exact UI Quality `33751403354` passed. | UI. |
| Startup/readiness foreground copy | UI-GAP-0004 | `VERIFIED` | Final startup/readiness product/test tree passed focused `33804104455` and canonical `33804193396`; equivalent blobs integrated. | Screen 11 remains pending visual review. |
| Persistent desktop system tray | Alpha Desktop/UI contract + UI-GAP-0005 | `VERIFIED` | Exact UI product/test head `acc156a8538e83ffec4e3eba4b9bef3e9c2fdb37` passed canonical Quality `33814651800`; bounded tray controller, focused tests and SystemWorkspace single-install wiring are integrated. | UI continues tray truthfulness/state gaps. |
| Tray runtime-state visibility | Alpha Desktop/UI contract + UI-GAP-0006 | `VERIFIED` | Exact UI head `72e43bc18c28b5c92f6528919abf788f66924ba9` passed canonical Quality `33822861477`. Integrator independently reviewed and carried only the verified tray controller, SystemWorkspace state forwarding and focused Qt test blobs onto Develop in commits `aa2cdbc8...`, `f5cbe19d...`, `0cb6f5cb...`. No synthetic telemetry was added; unknown states fail closed to unavailable. | UI proceeds to UI-GAP-0007 System-subnav truthfulness. |
| Canonical post-merge error state | Error ledger | `VERIFIED` | `ERR-0001` through `ERR-0004` are closed; no current Error-owned product mutation is pending. | Error resumes fresh exact-lineage regression scanning. |

## UI reference state

The original eleven user reference images remain unavailable in the current repository/tool path. All eleven manifest slots remain `IMPLEMENTED_PENDING_VISUAL_REVIEW`; zero `MATCH` claims are made. `MATCH` requires opening an original reference and comparing it with a real rendered state from the exact implementation SHA.

## Tracking rules

- Never infer a completion percentage from this table.
- `VERIFIED` requires concrete code/runtime/test evidence on the stated integrated lineage.
- `IMPLEMENTED_PENDING_VERIFY` covers implemented candidates whose exact required verification or shared-Develop integration is still outstanding.
- `PARTIAL` means a real path exists but a concrete contract gap remains.
- Pending, cancelled, action-required-with-no-jobs, or still-running Quality is not PASS evidence.
- No test/guard weakening, fake success path, fabricated provenance or automatic promotion to `main` is allowed.
- `main` remains read-only; post-merge integration lands only on `develop/pathena-next` until separately authorized.
