# pATHENA UI Handoff

## Current baseline

- Base: `develop/pathena-next@280066cc5450f172693e2ee913bd269b6755f7bb`.
- Worker: `postmerge/ui`.
- Worker synchronization: history-preserving NON-FORCE merge `aea3f418e28ccc7cae6a3899391c049cc3beaee4` with current Develop. The Develop delta since the old UI base was disjoint from the five UI-owned files, so no foreign product/test/document change was overwritten.
- UI product commit: `177bef4dcdb4956f1df75bfcce9ee10c7a4bd1e2`.
- UI focused-test commit: `ff14f8fbe9c99e043521605c1ae790f20e807ae2`.
- Draft verification PR: #53, base `develop/pathena-next`, no auto-merge.
- Original eleven reference images: `VISUAL_REFERENCE_PENDING`; File Library search locates likely pATHENA assets, but image-open attempts still fail, so no pixel-level parity or `MATCH` claim is made.

## Current slice — UI-GAP-0002

Screen targets: 01 Workspace/Chat and 10 Grounded Chat/Evidence & Activity.

The implementation remains bounded presentation-only glue:

- Chat + no grounded context: inspector hidden.
- Chat + grounded-context availability: inspector visible.
- Any non-chat surface: inspector visible.
- Returning to Chat re-evaluates the same real context state.
- `_set_context_available()` remains the existing state transition used by new/loaded/plain/grounded chat paths; no controller, provenance, storage, security or backend semantics changed.

## Verification state

Exact product/test head `ff14f8fbe9c99e043521605c1ae790f20e807ae2` ran ATHENA Quality Gate `33729667950` and completed with `failure` on 2026-09-03.

Confirmed passing jobs/steps:

- specification validator
- Ruff
- mypy
- Local install smoke
- Windows path safety
- Linux storage regressions

Confirmed failing step:

- Python 3.12 quality → canonical `pytest`

The workflow uploaded diagnostic artifact `canonical-quality-diagnostics-ff14f8fbe9c99e043521605c1ae790f20e807ae2`, but the current GitHub connector can list only artifact metadata; its ZIP/test trace is not readable through the available surface. Therefore the exact failing pytest node/signature is still unknown. No speculative product or test weakening was applied.

## Active UI gaps

### UI-GAP-0001 — Inspector hierarchy/copy

Status: `FIXED`. Product/test lineage `1f0fd548431be122d13a403fe9e2387087edf8fa` + `d85d2a2e144abc9d3ef1008b80f74114c7fafe23`; exact prior worker Quality `33720745475=success`; lineage already integrated into Develop.

### UI-GAP-0002 — Contextual inspector behavior

Status: `FIXED_PENDING_VERIFY`, P1, but with a confirmed failed exact-head canonical run. It is not Integrator-ready. Product `177bef4dcdb4956f1df75bfcce9ee10c7a4bd1e2`; focused tests `ff14f8fbe9c99e043521605c1ae790f20e807ae2`; Quality `33729667950=failure` at canonical pytest.

## Collision / ownership guidance

- UI owns inspector presentation/visibility state on `postmerge/ui`.
- Core/Backend should not implement alternate inspector widgets or mutate this presentation state.
- Backend/storage/security semantics remain untouched.
- Error worker may inspect run `33729667950` diagnostics if it gains readable artifact/log access, but should not patch UI presentation speculatively.

## Visual evidence

`VISUAL_REFERENCE_PENDING`. File Library search locates several plausible original pATHENA dark UI references, including Chat/Knowledge/PALLAS compositions, but actual image payload opening failed again. No exact spacing, proportion, color or screenshot-level `MATCH` claim is permitted. No current-build screenshot was generated because there is no network-enabled local repository checkout in this runtime.

## Integrator handoff

DO NOT integrate UI-GAP-0002. The exact product/test canonical run failed. The worker is now safely synchronized with current Develop, so the next UI run should obtain the exact pytest failure signature if tooling permits, determine whether it is slice-caused or an unrelated lineage failure, apply only the smallest evidence-backed correction, and rerun focused Qt tests plus canonical Quality on the exact corrected worker SHA.

## Next UI gap

UI-GAP-0002 remains first until technical verification is recovered. After that, re-read the 11-screen ledger and choose the next highest evidence-backed P1/P2 gap. Prefer actual reference-image inspection first if image access succeeds; otherwise continue only from the versioned manifest/gap contract and keep pixel claims `VISUAL_REFERENCE_PENDING`.
