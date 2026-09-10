# Post-Merge Feature Handoff - Integrator

Generated: 2026-09-10T20:51Z
Branch: `develop/pathena-next`
HEAD at run start: `7fa2108d820cfc5b48a9f92d42ffa61697b74818`

## Current evidence

- `main` and `bnbgrs/ATHENA` remain read-only and untouched.
- Current worker heads reviewed: Errors `d6eee816789c8dc0fa421ac618b8793f80862099`, Spec/Core `b8df82b23583d42a8d5ae8f387aea0fbd0e7859e`, Backend `b411e75a3481649b33edc70b74c22f64ab71c6d4`, UI `191c9cecd6edebe1744d66f0eae6bf9e96e519fe`.
- Exact Develop canonical Quality `34522965434@7fa2108d820cfc5b48a9f92d42ffa61697b74818 = SUCCESS`.
- No queued or in-progress canonical Develop Quality run existed immediately before this mutation.
- `ERROR_LEDGER.md` and `ALPHA_BETA_PROGRESS.md` are not present at repository root on current Develop and are not synthesized as source of truth.
- UI source of truth remains `docs/ui/11_SCREEN_REFERENCE_MANIFEST.md` and `docs/ui/VISUAL_GAP_LEDGER.md`; screenshot-level `MATCH` remains unproven.

## Bounded tooling unblock — exact UI worker visual capture

No new bounded product worker slice was READY. The current UI worker instead produced a narrowly scoped visual-tooling improvement. On exact UI head `191c9cecd6edebe1744d66f0eae6bf9e96e519fe`, Windows visual run `34528380154` proved Ruff, comparator mypy, comparator contract tests, and capture of exactly eleven canonical surfaces all SUCCESS. Baseline comparison/proposal generation and artifact upload also succeeded. The final fail-closed visual verdict remained FAILURE because no accepted committed visual baseline exists; this is not treated as a UI `MATCH` or product-regression closure.

This integration carries only the two bounded tooling changes needed to make that exact capture path usable from the UI worker lineage:

1. `.github/workflows/ui-snapshot.yml` also triggers for `postmerge/ui` and makes the workflow-dispatch candidate description branch-neutral.
2. `scripts/render_pathena_ui_snapshot_fontsafe.py` imports the sibling renderer as `render_pathena_ui_snapshot`, matching direct script execution under `python scripts/...` on Windows.

No desktop product code, visual baseline, comparator threshold, assertion, Storage/Recovery/Security behavior, Skip/XFail, or release guard is changed. The fail-closed `Enforce visual verdict` step remains unchanged.

## Persistent release guards

- pypdf packaging remains fail-closed and selected on Linux and Windows canonical lanes.
- Frozen argv and Desktop/Worker two-EXE contracts remain selected in native Windows Quality.
- Exactly one Desktop instance with bounded worker ownership/lifecycle remains guarded.
- Adaptive 2048-context Chat reserve remains selected in native Windows Quality.
- Windows lane-lock/path-safety remains fail-closed.
- Storage-bootstrap, Core-startup and duplicate-column/schema-reinitialization signatures remain selected in Windows Quality.
- Durable filesystem native-Windows behavior remains explicitly tested while POSIX-only identity contracts remain in Linux storage Quality.

## Next integration

1. Consume canonical Quality on the resulting exact Develop SHA first and freeze Develop while it is queued/in progress.
2. Keep the visual verdict fail-closed. Do not commit or bless a visual baseline without direct artifact/reference review.
3. Use the now-executable UI-worker capture path to obtain exact-SHA renders, then perform evidence-backed 11-screen comparison before any visual `MATCH` claim.
4. Do not absorb broad diverged worker history or re-integrate already landed Core/UI/runtime slices.
