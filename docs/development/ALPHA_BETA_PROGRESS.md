# pATHENA Alpha / Beta Progress

Evidence-backed post-merge development tracker for `develop/pathena-next`.

Status values: `MISSING`, `PARTIAL`, `IMPLEMENTED_PENDING_VERIFY`, `VERIFIED`.

| Capability / contract | Spec / evidence anchor | Status | Current evidence | Owner / next action |
|---|---|---|---|---|
| Normal hybrid retrieval / RRF | Beta Retrieval §§24–26, §64 | `VERIFIED` | Consolidated baseline contains deterministic hybrid/RRF implementation. | `postmerge/spec-core` continues response/provenance gap tracing. |
| Search response retrieval-method provenance | Beta Retrieval §34 and §52 | `VERIFIED` | `HybridSearchResult.retrieval_methods` is derived from actual lexical/semantic contributors, validated for canonical ordering/uniqueness, preserved through diversity adjustment, and covered by focused tests. Exact product/test SHA `ececd7741ca17a8c5c75af161359a5284fe88695` passed canonical Quality run `33703529634`; integrated lineage reaches `db5fab81e1121ed024101c8b1ddf1a8f0f57951b`. | `postmerge/spec-core` trace next missing Search Response explainability field without duplicating existing provenance. |
| Resource policy runtime mutation boundary | Existing backend audit task 289 + current backend handoff | `IMPLEMENTED_PENDING_VERIFY` | Backend worker has candidate product commit `881d662958b9fe6b94a9ad549a72d91abb24e692` adding the pre-side-effect runtime guard plus focused regression file, but no executable focused/Quality evidence yet. | `postmerge/backend` must obtain runtime verification before integration. |
| Grounded Chat inspector hierarchy / Evidence & Activity copy | UI contract + `UI-GAP-0001` | `PARTIAL` | Right inspector currently maps legacy `INSPECTOR` copy to generic `DETAILS`; UI worker has not submitted a tested product patch. | `postmerge/ui` owns copy/accessibility slice after safe branch synchronization. |
| Contextual inspector visibility | UI contract + `UI-GAP-0002` | `PARTIAL` | Inspector is currently forced visible in reference-shell paths; change requires focus/reduced-motion/progressive-disclosure contract review. | `postmerge/ui` owns analysis-first slice. |
| Canonical post-merge error state | Error ledger + exact-main baseline Quality | `VERIFIED` | No current OPEN/IN_PROGRESS error is recorded; error worker continues scanning the evolving development lineage and must reopen only fresh reproduced/exact-SHA failures. | `postmerge/errors` continues fresh scans after each product integration. |

## Tracking rules

- Never infer a completion percentage from this table.
- `VERIFIED` requires concrete code/runtime/test evidence on the stated lineage.
- `IMPLEMENTED_PENDING_VERIFY` means implementation exists but required verification is incomplete.
- `PARTIAL` means a real path exists but a spec/UI/contract gap remains or its coverage is not yet fully traced.
- Worker handoffs are evidence inputs, not automatic proof that a product change is correct.
- `main` is read-only; all post-merge integration lands only on `develop/pathena-next` until a separately authorized release phase.
