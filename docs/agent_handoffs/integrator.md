# pATHENA Feature Integrator Handoff

## Current source of truth

- `main` remains strict read-only at `0d4d621f8a38ddf8eccfa09622bf193687619943`.
- Develop baseline before this integration: `a32c63f39a2abca8a080ee78b97bd6b067eae52b`.
- Worker heads reviewed: errors `3318f6cddd9a8d4b455531845ef3291b236839f0`; spec-core `3590faef81e4eabf440e8ed88be96d860a5eef37`; backend `5fb8d5b7b5ee29af09bd70ccde8824633f0e0c8a`; UI `3cbb2aee7fb3e3bc48b7d6a9fefe86ea3132cb9e`.
- Exact Develop baseline had no queued/in-progress canonical Quality when mutation eligibility was checked.
- UI current synchronized head has canonical Quality `34312166038` in progress and was not consumed as whole-candidate evidence.
- Backend exact head Quality `34311050843` is red; Backend Storage/WAL/schema lineage remains held.
- Spec/Core has no new product diff from Develop.

## Progress this run — left-owned primary navigation

Integrated exactly one bounded, independently reviewed UI slice from exact-green predecessor `2cb2feb3685358f629095445554c9d04fd56efd1`, whose canonical Quality `34304620632` completed successfully. The subsequent UI synchronization commit did not cancel or invalidate that completed exact-source evidence.

The transplanted product blob `bc855803ca3531eafcfa4d80765eeae0c7a810d4` removes the duplicate Workspace/Library/Research/Jobs/Sources controls from the horizontal top bar. Primary product navigation remains solely in the existing left icon rail. The top bar is now explicitly `Status and utilities` and retains only System/Settings utility controls plus local/private status. Routing, page-title synchronization, accessibility names/tooltips, Backend, Storage, Security, Recovery, scheduler/worker, packaging and Windows-runtime behavior are unchanged.

The exact focused regression blob `3557539e4b91b03d09d311501b04ed43f3644d34` is integrated with the product. It requires zero `topNavButton` primary controls, preserves left-rail navigation and verifies System/Settings utilities and page routing. No Skip/XFail or assertion weakening was introduced.

## Quality / promotion state

- Source product/test pair: exact canonical Quality `34304620632 = success` at `2cb2feb3685358f629095445554c9d04fd56efd1`.
- Current synchronized UI head remains in progress and was not treated as READY.
- Exact-current Develop canonical Quality is required before any Beta/release-ready claim.
- Historical Windows/runtime signatures remain release guards only unless reproduced on an exact current SHA.

## Tracker / visual state

The 11-screen manifest and Visual Gap Ledger were reviewed. This integration advances the reference-backed shell hierarchy only; it does not claim screenshot-level pixel `MATCH`. `ALPHA_BETA_PROGRESS.md` still needs evidence reconciliation after exact-current Develop CI so no follow-up docs commit can supersede a running gate.

## Next integration order

1. Re-check exact-current Develop CI before any further mutation and keep Develop frozen while a gate is queued/in-progress.
2. Reconcile `ALPHA_BETA_PROGRESS.md` only after that gate is complete.
3. Consume the current UI synchronized descendant only if its exact-head Quality completes green and it contains a genuinely new bounded successor beyond this already integrated navigation slice.
4. Keep Backend v41/schema/WAL integration conservative until exact-green evidence closes the current Ruff/pytest failures.
5. Preserve explicit Beta/release acceptance for pypdf packaging metadata; fail-closed frozen argv; Desktop/Worker two-EXE split; one Desktop with bounded workers; adaptive 2048-context DirectChat budgeting; Windows lane-lock ownership cluster; and duplicate-column/Core-startup/storage-bootstrap signatures.

## Rules retained

No main mutation or promotion; no force push/history rewrite/auto-merge; no Skip/XFail addition; no weaker assertions; no Security/Storage/Recovery/Windows/validator relaxation; no fake success or fabricated provenance.
