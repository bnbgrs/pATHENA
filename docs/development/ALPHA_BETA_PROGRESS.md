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
| Temporal contradiction disjoint-window policy | Beta Knowledge/Claims §§56, 58, 60, 69–70 | `VERIFIED` | Deterministic disjoint-window suppression policy is integrated; exact worker Quality `33801697326` passed. | Core. |
| Proposal-acceptance temporal contradiction gate | Beta Knowledge/Claims §§56, 58, 60, 69–70 | `VERIFIED` | Missing dependency was restored on Develop; repaired-lineage canonical Quality `33838658964` completed `success`. | Core proceeds to next composition gap. |
| Exhaustive Research coverage accounting | Beta Exhaustive Research coverage/completeness | `VERIFIED` | Exact synchronized Core head `fa7eec0d332c6119a4a0f069ec6cf0ee92bf64c9` passed canonical Quality `33839797520`; independently reviewed two-file product/test slice integrated as `6b8d3b101d89393eecdbb0a478c6b74adc82dd3e`. | Core proceeds to durable ResearchScope/ResearchResult coverage composition. |
| Canonical Research coverage formula payload | Beta Exhaustive Research coverage/completeness | `VERIFIED` | Core exact head `b647e17fb972c9acada8e5d77296be8ebd27c860` passed canonical Quality `33848576424`. Exact green blobs `417cfa173de639294307abb6cd83bf2b188e5eb2` and `95eef89a365cd6ba5d7d590c48647e6fc8c2c15c` are integrated on Develop via `b69a1f8fa74c83cce6ddab7dc0089f33890fde0c` and `710229ea4a9bd90fce78b10f22d7962a962ff02d`. | Core composes this canonical payload into durable ResearchScope/ResearchResult state without duplicate arithmetic. |
| Durable ResearchScope / ResearchResult coverage composition | Beta Exhaustive Research coverage/completeness | `VERIFIED` | Exact Core head `ae691a463c0188c3b8c824a5d9d784297efcff5d` passed canonical Quality `33855954819`; focused persistence acceptance evidence was green. Exact blobs `142c98f8ada90d5ea7266a5a8aeeb83bffe618dc` and `cf887fd0278c67d5e2ca72148d8a9f30b39d0fd5` were independently collision-reviewed and integrated on Develop as `31db72b023fbe475ce8d3d5a5044e2b93b2c297c`. Canonical `ResearchCoverage.result_payload()` is now persisted into durable result details without duplicate arithmetic while transaction/fence/snapshot/recovery/idempotency semantics remain unchanged. | Core proceeds to next bounded evidence-backed Research composition gap. |
| Resource policy runtime mutation boundary | Backend audit task 289 | `VERIFIED` | `ResourceManager.set_mode()` rejects invalid runtime values before local-user/database side effects. | Backend. |
| ExternalAccessGateway exact runtime-type policy boundaries | Gateway hardening | `VERIFIED` | Bool-safe TTL/max-bytes and finite non-bool timeout validation integrated; exact product Quality `33790984890` and combined Develop `33799110483` passed. | Backend. |
| ExternalAccessGateway authorization/runtime fail-before-side-effect boundaries | Backend audit findings 295–296 | `VERIFIED` | Purpose/allowed-host/privacy-route/Direct-host/Direct-TTL boundary bundle integrated as `c8cf496def52629df341196613bc6c30409aa44a`; canonical combined Develop validation `33815279390` completed `success`. | Backend proceeds to next runtime boundary. |
| ExternalAccessGateway capture-URL runtime text boundary | Backend handoff | `VERIFIED` | Backend product/test blobs are integrated; canonical Quality `33822032100` passed on synchronized worker SHA with blob identity matching integrated files. | Backend. |
| Research UUID-filter container boundary | Backend Research hardening | `VERIFIED` | Bounded worker fix passed focused verifier `33833496929`; equivalent reviewed product/test blobs integrated on Develop, and repaired-lineage combined canonical Quality `33838658964` completed `success`. | Backend proceeds to source-types Sequence boundary. |
| Research source-types Sequence boundary | Backend Research hardening | `VERIFIED` | Canonical Quality `33840621670` completed `success` on synchronized candidate `75ae07fdb0bf72c100cc8401f7881ffa03b96b03`; independently reviewed product/test blobs integrated on Develop as `d645f7136b4c6325899ccd2f2d13ba95eb4ab2a8`. | Backend. |
| WAL checkpoint runtime-mode boundary | Backend Storage/Recovery hardening | `VERIFIED` | Synchronized Backend head `40180ced8d77debf1479fa53e7e1c814753dea4e` passed canonical Quality `33848858160`; exact reviewed source/test blobs were integrated on Develop as `f07286fe5c9ef346a337d5d904c7f7d2b2b02a4e`. Non-text runtime mode values fail before SQLite connection/SQL side effects while valid checkpoint semantics remain unchanged. | Backend proceeds to next evidence-backed Storage/Recovery/Provider/Packaging boundary. |
| Deletion-ledger runtime boundaries / recovery cursor | ERR-0001 + Backend tasks 290–293 | `VERIFIED` | Exact-type/bool-safe fail-before-SQL validation integrated and verified. | Error/Backend scan for recurrence only. |
| Grounded Chat inspector hierarchy / Evidence & Activity copy | UI-GAP-0001 | `VERIFIED` | Hierarchy/copy integrated and canonical-green. | UI continues screen gaps. |
| Contextual inspector visibility | UI-GAP-0002 | `VERIFIED` | Context-sensitive inspector visibility integrated and canonical-green. | UI. |
| PALLAS tab-order lifecycle resilience | UI-GAP-0003 | `VERIFIED` | Transient missing document binding is a safe no-op lifecycle state; exact UI Quality `33751403354` passed. | UI. |
| Startup/readiness foreground copy | UI-GAP-0004 | `VERIFIED` | Final startup/readiness product/test tree passed focused `33804104455` and canonical `33804193396`; equivalent blobs integrated. | Screen 11 remains pending visual review. |
| Persistent desktop system tray | Alpha Desktop/UI contract + UI-GAP-0005 | `VERIFIED` | Exact UI product/test head passed canonical Quality `33814651800`; bounded tray controller, focused tests and SystemWorkspace single-install wiring are integrated. | UI. |
| Tray runtime-state visibility | Alpha Desktop/UI contract + UI-GAP-0006 | `VERIFIED` | Exact UI head passed canonical Quality `33822861477`; verified tray state blobs are integrated on Develop. | UI. |
| System subnavigation truthfulness | Alpha Desktop/UI contract + UI-GAP-0007 | `VERIFIED` | Exact UI product/test head passed canonical Quality `33830601076`; Overview remains the sole real selected destination while unsupported destinations are explicitly unavailable. | UI selects next evidence-backed truthfulness/state/accessibility gap. |
| Settings Local Core vs Internet truthfulness | UI-GAP-0008 / ERR-0008 | `VERIFIED` | Exact UI head `afa319f0ab1b12edccc4b649d4a1ca36bcd7ac39` passed canonical Quality `33854660676`; exact source/test blobs `297ef96df45bfe13eee3ee0285635111cbf94b71` and `541c34d95a0f93ecf9b782134ba8fb7ab1cd9a28` are integrated on Develop. Local Core readiness is explicitly non-evidence for Internet access. | UI proceeds to UI-GAP-0009 after exact verification. |
| Canonical post-merge error state | Error ledger | `VERIFIED` | `ERR-0001` through `ERR-0008` are fixed in the current error handoff; no open confirmed product defect remains. | Error worker continues fresh regression scanning. |

## UI reference state

The original eleven user reference images remain unavailable in the current repository/tool path. All eleven manifest slots remain `IMPLEMENTED_PENDING_VISUAL_REVIEW`; zero `MATCH` claims are made. `MATCH` requires opening an original reference and comparing it with a real rendered state from the exact implementation SHA.

## Tracking rules

- Never infer a completion percentage from this table.
- `VERIFIED` requires concrete code/runtime/test evidence on the stated integrated lineage.
- `IMPLEMENTED_PENDING_VERIFY` covers implemented candidates whose exact required verification or shared-Develop integration is still outstanding.
- `PARTIAL` means a real path exists but a concrete contract gap remains.
- Pending, cancelled, action-required, failed, or still-running Quality is not PASS evidence.
- No test/guard weakening, fake success path, fabricated provenance or automatic promotion to `main` is allowed.
- `main` remains read-only; post-merge integration lands only on `develop/pathena-next` until separately authorized.
