# pATHENA UI Handoff

## Current baseline

- Base: `develop/pathena-next@7c15b44818e9ac5c3484ee30d4a20d6f0d56087e`
- Worker: `postmerge/ui`
- Worker synchronization commit: `7952eedcda8cc889e60ced3170e72a762245d00c`
- UI product commit: `1f0fd548431be122d13a403fe9e2387087edf8fa`
- UI focused-test commit: `d85d2a2e144abc9d3ef1008b80f74114c7fafe23`
- Original eleven reference images: `VISUAL_REFERENCE_PENDING`; no pixel-level parity or `MATCH` claim is made.

## Work completed

- Reconciled the UI worker with current Develop using a non-force, history-preserving two-parent merge. Develop changed only integrator/progress documentation plus the ResourceMode product/test files since the prior UI base; the UI delta changed only UI-owned files, so no foreign work was overwritten.
- `UI-GAP-0001` product/test lineage remains unchanged: visible inspector copy and accessible name use `Evidence & Activity` without changing controller, provenance, persistence, visibility, focus or backend semantics.
- Exact prior UI head `f31be028652095b18b8a98dfacd65b73be9af763` passed ATHENA Quality Gate run `33720745475` with conclusion `success`.
- Because synchronization produced a new exact worker head, Quality run `33724577775` is currently verifying `7952eedcda8cc889e60ced3170e72a762245d00c`; `UI-GAP-0001` remains `FIXED_PENDING_VERIFY` until that current-head run succeeds.
- Reviewed `UI-GAP-0002` call-chain: `_install_reference_shell()` and `_install_progressive_disclosure()` force the inspector visible; `_sync_progressive_chat_actions()` forces it visible again; `_set_context_available()` already exposes the truthful grounded-context state; grounded responses set that state true while new/loaded/ordinary sent chat paths clear it. This gives a real existing state signal for a later contextual-visibility slice, but no visibility mutation was bundled into this synchronization run.

## Active UI gaps

### UI-GAP-0001 — Inspector hierarchy/copy

Status: `FIXED_PENDING_VERIFY`, P1.

Implementation: `1f0fd548431be122d13a403fe9e2387087edf8fa`; focused Qt contract: `d85d2a2e144abc9d3ef1008b80f74114c7fafe23`. Prior exact UI head is green; current synchronized head still requires successful Quality run `33724577775` before closure. This does not imply screenshot-level `MATCH`.

### UI-GAP-0002 — Contextual inspector behavior

Status: `OPEN / CONTRACT_TRACED`, P1.

Evidence: chat grounded-context availability already has a truthful state transition through `_set_context_available()`. A safe bounded implementation should keep the inspector visible on non-chat surfaces, while Chat visibility should derive from real grounded-context availability instead of unconditional `show()` calls. Any implementation must preserve current non-chat details, immediate/no-animation reduced-motion behavior, and existing focus contracts. No product mutation for this gap was made in this run.

## Collision / ownership guidance

- UI owns inspector presentation/visibility state on `postmerge/ui`.
- Core/Backend should not implement alternate inspector widgets or mutate its presentation state.
- Backend/storage/security semantics remain untouched.
- No verified UI root-cause error is handed to the error worker.

## Verification

- Prior exact UI head `f31be028652095b18b8a98dfacd65b73be9af763`: ATHENA Quality Gate `33720745475` = `success`.
- Current synchronized head `7952eedcda8cc889e60ced3170e72a762245d00c`: ATHENA Quality Gate `33724577775` = `in_progress` at handoff update time.
- No original reference screenshot was opened; `VISUAL_REFERENCE_PENDING` remains mandatory.

## Integrator handoff

Do not integrate the synchronized UI worker until Quality `33724577775` succeeds on exact head `7952eedcda8cc889e60ced3170e72a762245d00c` (or a later documentation-only head with equivalent successful verification). The bounded UI-GAP-0001 product/test lineage remains `1f0fd548431be122d13a403fe9e2387087edf8fa` + `d85d2a2e144abc9d3ef1008b80f74114c7fafe23`. `UI-GAP-0002` remains a separate subsequent interaction slice.
