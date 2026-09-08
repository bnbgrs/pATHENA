# pATHENA Feature Integrator Handoff

## Current branch state

- `main` remains strict read-only at `0d4d621f8a38ddf8eccfa09622bf193687619943`.
- Develop before this run: `eeaf49fa22f1b9b3f9dfae46c7cd2c2d1146d9ff`.
- Integration target: `develop/pathena-next` only.
- Worker heads reviewed: errors `d35beafc4c5844aae184ad98e619887ce567efe1`; spec-core `71d49c94dde94616705ffb60010ff57fc0ec127e`; backend `43b16ec2b51e5d2f8f624ae2ff4c59e9facd8b08`; UI `9af7d23d2daccdee78236b6da335090d512d7fcd`.
- `main` and `bnbgrs/ATHENA` were untouched; no force update, rebase, history rewrite, auto-merge or main promotion was used.

## Integrated this run — Large Archive acceptance

The previously exact-green bounded Spec/Core Large Archive acceptance from `d97ffca766868e3eb3ad1e9197fc1478a0e8e7a5` was independently reviewed against current Develop. The target test file did not exist on Develop, so only that exact test-only acceptance blob was added; divergent Spec/Core history and unrelated memory/Core files were not imported.

- Verified Spec/Core head: `d97ffca766868e3eb3ad1e9197fc1478a0e8e7a5`.
- Canonical ATHENA Quality: `34176070442 = success` on that exact head.
- Source acceptance blob: `tests/unit/test_exhaustive_research_large_archive.py@5e8c45c14ee6575d306806f6b96cd4cc3b317b29`.
- Develop integration commit: `880850f184fa82cb5406c14f3f1be273ce46bec6`.
- Acceptance uses the real synthesis service with 40 source artifacts and a pinned 2048-token context; it requires the oversized final synthesis to split, verifies every executed synthesis call satisfies `input + output_limit + safety_margin <= effective_context_limit`, requires more than one synthesis call, converges to a final artifact, and preserves precise provenance to all source artifacts.
- No production code, provider/transport behavior, Search, Storage, Security, scheduler/worker, packaging or Windows runtime semantics changed.

## Verification / READY state

- Large Archive exact worker Quality `34176070442`: SUCCESS.
- Current Develop integration commit `880850f184fa82cb5406c14f3f1be273ce46bec6`: no associated exact completed workflow run observed during this integration run; global-green/promotion-ready is not claimed.
- Current Spec/Core head `71d49c94dde94616705ffb60010ff57fc0ec127e` adds a separate opposing-source contradiction acceptance on top of `d97ff...`; it was not selected because this run consumes exactly one bounded slice and current exact canonical evidence for that newer head was not established here.
- Backend current head `43b16ec2b51e5d2f8f624ae2ff4c59e9facd8b08` was not integrated; current exact READY evidence was not established here.
- UI current head `9af7d23d2daccdee78236b6da335090d512d7fcd` was not integrated; current exact READY evidence was not established here.
- No Skip/XFail, weakened assertions or relaxed Security/Storage/Windows/Recovery/validator guard was introduced.

## Error state

- Error worker head `d35beafc4c5844aae184ad98e619887ce567efe1` documents verified closures for ERR-0021 and ERR-0022.
- Historical Windows/runtime crash classes remain Beta/release regression obligations only absent exact-current reproduction.

## UI / Alpha-Beta state

- Eleven-screen status remains implemented pending visual review; no MATCH claim is made without original-reference visual evidence.
- The Large Archive acceptance is integrated with exact-green worker evidence.
- `docs/development/ALPHA_BETA_PROGRESS.md` was not destructively rewritten because a complete safe replacement body was not obtained in this run; this versioned handoff records the integration evidence for later tracker synchronization.
- No percentage progress is inferred.

## Next integration order

1. Obtain exact-current-Develop canonical Quality for `880850f184fa82cb5406c14f3f1be273ce46bec6` or a product-identical documentation descendant.
2. Independently review current Spec/Core opposing-source contradiction acceptance and integrate only if exact-green and compatible.
3. Review Backend single-assignment WAL-hook binding and UI Jobs process-error-copy lineage for exact READY evidence before selecting either.
4. Preserve the release crash-regression matrix before any Windows candidate or promotion claim.

## Persistent release guards

Retain explicit Beta/release regression acceptance for pypdf packaging metadata; fail-closed frozen argv routing and Desktop/Worker two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context DirectChat budgeting; Windows lane-lock `PermissionError` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError`; and storage-bootstrap/migration startup signatures including duplicate-column failures.

## Rules retained

No direct work on `main`; no main promotion; no force-push/history rewrite/auto-merge; no Skip/XFail or weaker assertions; no Security/Storage/Windows/Recovery/validator relaxation; no fake success or fabricated provenance.
