# pATHENA UI Handoff

## Current baseline

- Base: `develop/pathena-next@4f077e36248a49d261f13d3f3838d62a376f506f`
- Worker: `postmerge/ui`
- Worker synchronization commit: `a8ac931976c59c12db459902174f008088d2f3c2`
- Original eleven reference images: `VISUAL_REFERENCE_PENDING`; no pixel-level parity or `MATCH` claim is made.

## Work completed — UI-GAP-0004 Jobs verification failure copy

- The real Jobs `JobLifecycleError` verification-failure path no longer exposes command/transport implementation headings such as `JOB_ACTION_RESPONSE_UNAVAILABLE` and `Raw command output`.
- Visible failure copy uses `JOB ACTION COULD NOT BE VERIFIED` plus `Diagnostic details`, while preserving the exact exception/output payload for diagnosis.
- Lifecycle parsing, action availability, process behavior, scheduler/worker behavior, persistence, Backend, Storage and Security semantics are unchanged.
- Focused Jobs regressions cover the user-facing copy and diagnostic payload. UI-authored module-level `pytest.importorskip("PySide6")` guards were removed from touched Jobs harnesses; no Skip/XFail or assertion weakening was introduced.
- Exact UI head `b0c74459af0d6382f23106819f34778c86b6f18b` passed canonical Quality run `34240229731` with Windows path safety, Linux storage, local install smoke, specification validator, Ruff, mypy and full pytest all green.
- Current Develop was synchronized into the UI worker using non-force, history-preserving two-parent merge `a8ac931976c59c12db459902174f008088d2f3c2`; the verified five-file Jobs UI/test delta was preserved over the current Develop tree.
- `docs/ui/VISUAL_GAP_LEDGER.md` now records the slice as stable `UI-GAP-0004` with status `FIXED / INTEGRATOR_READY`.
- `docs/ui/11_SCREEN_REFERENCE_MANIFEST.md` remains exactly eleven slots; Screen 04 remains `IMPLEMENTED_PENDING_VISUAL_REVIEW` because original reference pixels are unavailable.

## Verification

- Canonical exact-green product/test head: `b0c74459af0d6382f23106819f34778c86b6f18b`.
- Canonical Quality: `34240229731 = success`.
- Current synchronized lineage starts at `a8ac931976c59c12db459902174f008088d2f3c2`; documentation commits after it do not change product/test semantics.
- No original reference screenshot was opened; `VISUAL_REFERENCE_PENDING` remains mandatory.

## Collision / ownership guidance

- UI owns the Jobs presentation/copy delta on `postmerge/ui`.
- Core/Backend should not duplicate or reinterpret the UI failure-copy change.
- No Backend, Storage, Security, scheduler, worker, transport, process-spawn or runtime semantic change is handed off from this slice.
- Historical Windows crash signatures remain release-regression knowledge only unless reproduced on an exact current SHA.

## Integrator handoff

`UI-GAP-0004` is integrator-ready from exact canonical evidence: product/test head `b0c74459af0d6382f23106819f34778c86b6f18b` passed Quality `34240229731`. Integrate only the bounded Jobs copy/test delta from the current `postmerge/ui` lineage; preserve the non-force history and do not infer screenshot-level `MATCH` from this technical closure.

## Next UI slice

After exact-current-worker Quality is consumed, select at most one distinct evidence-backed gap from the eleven-screen manifest/ledger: accessibility, interaction/state, responsive hierarchy or user-facing copy. Do not reopen UI-GAP-0004 unless an exact-SHA regression reproduces it.
