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
| Exhaustive Research coverage accounting | Beta Exhaustive Research coverage/completeness | `VERIFIED` | Exact synchronized Core head `fa7eec0d332c6119a4a0f069ec6cf0ee92bf64c9` passed canonical Quality `33839797520`; independently reviewed two-file product/test slice integrated. | Core proceeds to durable ResearchScope/ResearchResult coverage composition. |
| Canonical Research coverage formula payload | Beta Exhaustive Research coverage/completeness | `VERIFIED` | Core exact head `b647e17fb972c9acada8e5d77296be8ebd27c860` passed canonical Quality `33848576424`; exact green blobs are integrated. | Core. |
| Durable ResearchScope / ResearchResult coverage composition | Beta Exhaustive Research coverage/completeness | `VERIFIED` | Exact Core head `ae691a463c0188c3b8c824a5d9d784297efcff5d` passed canonical Quality `33855954819`; canonical coverage payload is persisted without duplicate arithmetic while transaction/fence/snapshot/recovery/idempotency semantics remain unchanged. | Core proceeds to next bounded evidence-backed Research composition gap. |
| Source-internal Research coverage policy | Beta Exhaustive Research §37 | `VERIFIED` | Exact Core head `0261a299b8703aec41c6032be0bb6e03d2aba637` passed canonical Quality `33867459130`; exact verified product/test blobs are integrated on Develop. Failed/unavailable remain visible but never coverage-positive; zero eligible units cannot synthesize full coverage. | Core proceeds to real-record per-source coverage composition after exact green verification. |
| Real-record per-source Research coverage composition | Beta Exhaustive Research §37 | `VERIFIED` | Exact Core head `fe356aa1fdea519d1391e61a3694c4e19d92fabc` passed canonical Quality `33877310215`; exact verified product/test files are integrated on Develop as `d0f8f5bf602d559ef3b8d8269cfef76160720ba5` + `62dc9a25b32a0f56391788333ad4cc24d0a8f4e8`. Stable source UUID ordering and fail-closed unknown/duplicate work identity are preserved. | Core proceeds to storage-ready source coverage payload after exact green verification. |
| Reserved ResearchResult source-coverage content | Beta Exhaustive Research §§37, 49–52 | `VERIFIED` | Exact Core head `5e5461a6c0a0a2f2e522d76f48a3870ca8414635` passed canonical Quality `33888920061`; exact verified product/test blobs `0ac130e710fa42b201cc06df8d4d552f87a26912` + `bdb15c7314a0718acc29ee68e2397a283e7cad7e` are integrated on Develop as commits `76cdbb7f8297d33939d9c51456bb49eafd79b1f6` + `8a3e66d36fa56ae951ae131c4b649ad6391165c0`. Semantic override of Core-owned `source_coverage` fails closed. | Core proceeds to transaction-bound source-coverage composition after exact green verification. |
| Resource policy runtime mutation boundary | Backend audit task 289 | `VERIFIED` | `ResourceManager.set_mode()` rejects invalid runtime values before local-user/database side effects. | Backend. |
| ExternalAccessGateway exact runtime-type policy boundaries | Gateway hardening | `VERIFIED` | Bool-safe TTL/max-bytes and finite non-bool timeout validation is present on Develop; canonical Backend head `c67fa646d8ba4e4137cdf69992b9c8b42ad904d6` passed Quality `33884210684`, and exact canonical-harness blob `fbdf55e14cac1483922fd23b3a19c4cb02923075` was integrated as Develop commit `e8574de635dbd6c3cfd4906075b49073e06cf966`. | Backend proceeds to next bounded runtime/storage gap. |
| ExternalAccessGateway authorization/runtime fail-before-side-effect boundaries | Backend audit findings 295–296 | `VERIFIED` | Purpose/allowed-host/privacy-route/Direct-host/Direct-TTL boundary bundle integrated and verified. | Backend. |
| ExternalAccessGateway capture-URL runtime text boundary | Backend handoff | `VERIFIED` | Backend product/test blobs are integrated; canonical Quality passed. | Backend. |
| Research UUID-filter container boundary | Backend Research hardening | `VERIFIED` | Bounded worker fix passed focused verifier and repaired-lineage combined canonical Quality. | Backend. |
| Research source-types Sequence boundary | Backend Research hardening | `VERIFIED` | Canonical Quality `33840621670` completed `success`; independently reviewed product/test blobs integrated. | Backend. |
| WAL checkpoint runtime-mode boundary | Backend Storage/Recovery hardening | `VERIFIED` | Synchronized Backend head passed canonical Quality `33848858160`; exact reviewed source/test blobs integrated. | Backend. |
| Deletion-ledger runtime boundaries / recovery cursor | ERR-0001 + Backend tasks 290–293 | `VERIFIED` | Exact-type/bool-safe fail-before-SQL validation integrated and verified. | Error/Backend scan for recurrence only. |
| Grounded Chat inspector hierarchy / Evidence & Activity copy | UI-GAP-0001 | `VERIFIED` | Hierarchy/copy integrated and canonical-green. | UI continues screen gaps. |
| Contextual inspector visibility | UI-GAP-0002 | `VERIFIED` | Context-sensitive inspector visibility integrated and canonical-green. | UI. |
| PALLAS tab-order lifecycle resilience | UI-GAP-0003 | `VERIFIED` | Transient missing document binding is a safe no-op lifecycle state; exact UI Quality passed. | UI. |
| Startup/readiness foreground copy | UI-GAP-0004 | `VERIFIED` | Final startup/readiness product/test tree passed focused and canonical validation; equivalent blobs integrated. | Screen 11 remains pending visual review. |
| Persistent desktop system tray | Alpha Desktop/UI contract + UI-GAP-0005 | `VERIFIED` | Exact UI product/test head passed canonical Quality; bounded tray controller, tests and wiring integrated. | UI. |
| Tray runtime-state visibility | Alpha Desktop/UI contract + UI-GAP-0006 | `VERIFIED` | Exact UI head passed canonical Quality; verified tray state blobs integrated. | UI. |
| System subnavigation truthfulness | Alpha Desktop/UI contract + UI-GAP-0007 | `VERIFIED` | Exact UI product/test head passed canonical Quality; unsupported destinations are explicitly unavailable. | UI. |
| Settings Local Core vs Internet truthfulness | UI-GAP-0008 / ERR-0008 | `VERIFIED` | Exact UI head `afa319f0ab1b12edccc4b649d4a1ca36bcd7ac39` passed canonical Quality `33854660676`; Local Core readiness is explicitly non-evidence for Internet access. | UI. |
| Settings failed-Core metadata reset | UI-GAP-0009 | `VERIFIED` | Exact UI head `6d6869d4927a52e98158238f396b8d5855b771b9` passed canonical Quality `33860150646`; exact product/test blobs are integrated on Develop. Failed Core refresh clears stale loopback metadata and fails closed to unavailable/no-Internet-inference. | UI. |
| Settings immediate fresh-snapshot accessibility boundary | UI-GAP-0010 | `VERIFIED` | Exact UI head `dc82cdded9e9d3c87be964a5f582965a9f4d3c9a` passed canonical Quality `33864721817`; exact green product/test blobs are integrated on Develop. | UI continues to UI-GAP-0011. |
| Settings pre-first-snapshot fail-closed state | UI-GAP-0011 | `IMPLEMENTED_PENDING_VERIFY` | UI handoff reports exact green head `45e2b84d14bfc11b4878d9b945065063fdc40e6d` / Quality `33874283635`; shared Develop integration remains outstanding. | Integrator may consume after independent baseline/diff review. |
| Settings initial persistence-state freshness metadata | UI-GAP-0012 | `IMPLEMENTED_PENDING_VERIFY` | UI handoff reports product/test candidate verified on exact UI head `3a1be68c48dab4176e9258170147cf127c4b3d2a` / Quality `33879947654`; shared Develop integration remains outstanding. | Integrator may consume after independent baseline/diff review. |
| Canonical post-merge error state | Error ledger | `VERIFIED` | `ERR-0001` through `ERR-0008` are fixed. No active stable `ERR-0009` is allocated; exact current-Develop global PASS is not claimed. | Error worker continues exact-signature scanning. |

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
