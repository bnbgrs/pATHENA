# Post-Merge Feature Handoff - Integrator

Generated: 2026-09-10T21:48Z
Branch: `develop/pathena-next`
HEAD at run start: `cbd0f7036feebc92443b12dec79ac840834dea2d`

## Current evidence

- `main` and `bnbgrs/ATHENA` remain read-only and untouched.
- Current worker heads reviewed: Errors `6b3a9090f305201cd562312b928e41ad61ea78ed`, Spec/Core `b8df82b23583d42a8d5ae8f387aea0fbd0e7859e`, Backend `b411e75a3481649b33edc70b74c22f64ab71c6d4`, UI `6b1777ef181dc2f1b15f5a7f70c3cab84ff0b9dc`.
- Exact Develop canonical Quality `34529111566@cbd0f7036feebc92443b12dec79ac840834dea2d = SUCCESS`.
- Immediately before this mutation, Develop had zero queued and zero in-progress workflow runs.
- `ERROR_LEDGER.md` and `ALPHA_BETA_PROGRESS.md` are not present at repository root on current Develop; no replacement percentages are synthesized.
- Develop visual source of truth remains `docs/ui/11_SCREEN_REFERENCE_MANIFEST.md` and `docs/ui/VISUAL_GAP_LEDGER.md`; neither supports a screenshot-level `MATCH` claim yet.

## Worker qualification

- Errors has no new bounded product candidate and continues to leave the Windows emergency-reserve directory-identity gap Backend-owned.
- Spec/Core has no new head.
- Backend has no new bounded exact-verified product candidate.
- UI advanced to `6b1777ef...` with a bounded typography hierarchy change in `pathena_design_tokens.py` plus focused assertions in `test_pathena_design_tokens.py`. Exact Windows visual run `34533820471` proved checkout identity, locked environment, Ruff, mypy comparator, comparator contract tests, eleven-surface native-font capture, comparison/proposal generation, and artifact upload. Its only failing step was the intentionally fail-closed visual verdict because no approved committed baseline exists.
- The UI candidate therefore has useful exact render evidence, but its focused design-token unit test is not selected by the visual workflow. It is not promoted in this run.

## Bounded tooling unblock - focused UI token evidence

To make the next UI visual candidate independently promotion-qualifiable, `.github/workflows/ui-snapshot.yml` now executes `tests/unit/test_pathena_design_tokens.py` on the exact candidate SHA before the eleven-surface capture. This closes an evidence-selection gap only; it does not alter desktop product code, typography values, comparator thresholds, visual baselines, test assertions, or fail-closed enforcement.

No Skip/XFail, Storage/Recovery/Security weakening, force push, history rewrite, auto-merge, or main mutation is introduced.

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
2. Re-qualify the then-current UI head. Require exact-head focused design-token success plus real native-Windows capture before promoting any bounded hierarchy slice.
3. Keep the visual verdict fail-closed and do not bless a generated baseline without direct reference/current-render review.
4. Keep Backend-owned BE-046/ERR-0033 out of parallel Integrator mutation unless a bounded Backend candidate with focused native-Windows adversarial identity evidence becomes READY.
