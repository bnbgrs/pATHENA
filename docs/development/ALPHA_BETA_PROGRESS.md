# pATHENA Alpha / Beta Progress

Evidence-backed post-merge development tracker for `develop/pathena-next`.

Status values: `MISSING`, `PARTIAL`, `IMPLEMENTED_PENDING_VERIFY`, `VERIFIED`.

| Capability / contract | Spec / evidence anchor | Status | Current evidence | Owner / next action |
|---|---|---|---|---|
| Normal hybrid retrieval / RRF | Beta Retrieval §§24–26, §64 | `VERIFIED` | Consolidated baseline already contains deterministic hybrid/RRF implementation; no new product mutation in this integration run. | `postmerge/spec-core` continues response/provenance gap tracing. |
| Search response retrieval-method provenance | Beta Retrieval §34 and §52 | `PARTIAL` | Beta requires candidate `retrieval method` and Search Response `retrieval methods`; current core audit identified this as the next explainability contract to trace through result constructors/serialization/tests before mutation. | `postmerge/spec-core` to verify consumers then implement only if still missing. |
| Resource policy runtime mutation boundary | Existing backend audit task 289 + current backend handoff | `PARTIAL` | `ResourceManager.set_mode()` is statically reported to persist `mode.value` without a runtime `ResourceMode` guard; no product patch or focused regression is ready yet. | `postmerge/backend` owns surgical guard + regression. |
| Grounded Chat inspector hierarchy / Evidence & Activity copy | UI contract + `UI-GAP-0001` | `PARTIAL` | Right inspector currently maps legacy `INSPECTOR` copy to generic `DETAILS`; UI worker has not yet submitted a tested product patch. | `postmerge/ui` owns copy/accessibility slice. |
| Contextual inspector visibility | UI contract + `UI-GAP-0002` | `PARTIAL` | Inspector is currently forced visible in reference-shell paths; change requires focus/reduced-motion/progressive-disclosure contract review. | `postmerge/ui` owns analysis-first slice. |
| Canonical post-merge error state | Exact-main Quality run `33694896994` | `VERIFIED` | No current exact-baseline failures are open in the canonical error ledger; historical pre-merge failures remain stale unless they recur. | `postmerge/errors` continues fresh scans. |

## Tracking rules

- Never infer a completion percentage from this table.
- `VERIFIED` requires concrete code/runtime/test evidence on the stated lineage.
- `IMPLEMENTED_PENDING_VERIFY` means implementation exists but required verification is incomplete.
- `PARTIAL` means a real path exists but a spec/UI/contract gap remains or its coverage is not yet fully traced.
- Worker handoffs are evidence inputs, not automatic proof that a product change is correct.
- `main` is read-only; all post-merge integration lands only on `develop/pathena-next` until a separately authorized release phase.
