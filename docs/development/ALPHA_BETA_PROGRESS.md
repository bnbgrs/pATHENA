# pATHENA Alpha / Beta Progress

Evidence-backed post-merge development tracker for `develop/pathena-next`.

Status values: `MISSING`, `PARTIAL`, `IMPLEMENTED_PENDING_VERIFY`, `VERIFIED`.

| Capability / contract | Spec / evidence anchor | Status | Current evidence | Owner / next action |
|---|---|---|---|---|
| Normal hybrid retrieval / RRF | Beta Retrieval §§24–26, §64 | `VERIFIED` | Consolidated baseline contains deterministic hybrid/RRF implementation. | `postmerge/spec-core` continues response/provenance gap tracing. |
| Search response retrieval-method provenance | Beta Retrieval §34 and §52 | `VERIFIED` | `HybridSearchResult.retrieval_methods` is derived from actual lexical/semantic contributors, validated for canonical ordering/uniqueness, preserved through diversity adjustment, and covered by focused tests. Exact product/test SHA `ececd7741ca17a8c5c75af161359a5284fe88695` passed canonical Quality run `33703529634` and is integrated into develop. | `postmerge/spec-core` continues Search Response explainability tracing. |
| Search response final rank | Beta Retrieval §52 | `VERIFIED` | `HybridSearchResult.rank` is additive/backward-compatible and final returned hybrid lists receive contiguous ranks after diversity/reweighting. Exact product/test SHA `11720aa82b38175b2f06e6a0ed80ddafd15f63ea` passed ATHENA Quality Gate run `33706998826`; worker lineage `54ca55da93074993c7f81757b53683ddbdfd3f4a` was explicitly merged into develop as `8b5f684c7200675c46d098430cf3e17b1525565e`. | `postmerge/spec-core` trace source anchor next, then protection state, without inventing provenance. |
| Resource policy runtime mutation boundary | Existing backend audit task 289 + current backend handoff | `IMPLEMENTED_PENDING_VERIFY` | Product commit `881d662958b9fe6b94a9ad549a72d91abb24e692` adds pre-side-effect `ResourceMode` runtime validation. Exact synchronized SHA `8ac7b3d5822daa395f71ee6fc797946ccd3d04b0` passed ATHENA Quality Gate run `33707952053`. It is not yet integrated because the backend PR became non-mergeable after the Core merge changed develop; status therefore remains pending on the shared branch despite successful worker verification. | `postmerge/backend` must safely NON-FORCE synchronize to current develop and resubmit the same bounded slice. |
| Grounded Chat inspector hierarchy / Evidence & Activity copy | UI contract + `UI-GAP-0001` | `PARTIAL` | Right inspector still uses legacy/generic naming; UI worker has no tested product patch integrated. | `postmerge/ui` owns copy/accessibility slice on its synchronized branch. |
| Contextual inspector visibility | UI contract + `UI-GAP-0002` | `PARTIAL` | Inspector visibility still requires focus/reduced-motion/progressive-disclosure contract review. | `postmerge/ui` owns analysis-first slice after UI-GAP-0001. |
| Canonical post-merge error state | Error ledger + exact-lineage scans | `VERIFIED` | No OPEN/IN_PROGRESS error is currently recorded. This status must be re-evaluated after each product-bearing develop integration; no historical issue is reopened without fresh exact-SHA/reproduction evidence. | `postmerge/errors` rescan current develop after the Core rank integration. |

## Tracking rules

- Never infer a completion percentage from this table.
- `VERIFIED` requires concrete code/runtime/test evidence on the stated integrated lineage.
- `IMPLEMENTED_PENDING_VERIFY` also covers a verified worker implementation that is not yet present on the shared develop lineage; the evidence column must state the precise remaining integration condition.
- `PARTIAL` means a real path exists but a spec/UI/contract gap remains or its coverage is not yet fully traced.
- Worker handoffs are evidence inputs, not automatic proof that a product change is correct.
- `main` is read-only; all post-merge integration lands only on `develop/pathena-next` until a separately authorized release phase.
