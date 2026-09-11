# pATHENA UI Handoff

## Current baseline — 2026-09-11

- Run-start Develop checked first: `develop/pathena-next@e6ba3d7557bd46094ad4e8f067a238e1c2375f8e`.
- Exact canonical ATHENA Quality Gate: `34567856833 = SUCCESS`.
- UI worker run-start HEAD: `postmerge/ui@c51ef04787ef6affa2e6acc3a902e138cf6b7409`.
- `main` and `bnbgrs/ATHENA` remained READ-ONLY and untouched.
- Current Spec/Core, Backend, Errors, Integrator, 11-screen manifest and Visual Gap Ledger were consumed before product work.

## Exact visual evidence this run

All 11 user reference PNGs were opened directly. The exact Windows/PySide6 artifact for `103feb7ca6b3513077ce47f83569c13cc626b600`, previously inaccessible at the byte level, was successfully downloaded and all eleven runtime PNGs were opened. Fresh pixels reproduced a repeated product issue: non-Chat Knowledge, Research, Jobs, Sources and Settings routes displayed the Chat-oriented `CHAT / NONE` inspector.

The change was intentionally bounded to two contexts only: Jobs and Settings. It lives in the existing `NavigationContextAccessibility` presentation controller and does not add a second router or alter Backend, Storage or Security semantics. Jobs uses a truthful no-selection overlay describing `EXECUTION` and `RESOURCES`; Settings uses `System status`, the actually available local status string at route sync time, and explicit wording that no synthetic health state is shown.

## Candidate history

1. `069dff56d64cd78e2ddd255460db375f8eeb3041` — product + focused unit contract. Native capture failed immediately because the implementation attempted to connect `QLabel.textChanged`, which does not exist. The artifact contained the exact traceback; no visual parity claim was made.
2. `75029071aa63dbaa73ef42da16fb709cc6d8ca99` — render-safe correction removing the invalid signal dependency and adjusting the focused test accordingly.
3. Exact Windows visual run `34571930149` on `75029071…`: immutable checkout, locked environment install, Ruff, mypy, comparator contract tests, all eleven native-font captures, comparison/proposal and artifact upload succeeded. The final visual verdict failed only because the repository still has no approved committed visual baseline.

All 11 final-candidate runtime PNGs were downloaded and opened. BEFORE -> AFTER is visibly confirmed for both targeted routes:

- Jobs: generic `CHAT / NONE` inspector -> `JOB / NONE`, `No job selected`, `EXECUTION`, `RESOURCES`.
- Settings: generic `CHAT / NONE` inspector -> `SETTINGS / LOCAL`, `System status`, actual captured core status and explicit no-synthetic-health-state copy.

The references remain substantially richer and often show populated states, so neither route is called MATCH. Strict accounting remains `PAIRS_VERIFIED_0_OF_11 · MATCH_0_OF_11`.

## Tests / Quality discipline

- A focused unit test was added for Jobs/Settings overlay truthfulness, visibility transitions and preservation of actual status text.
- The exact visual workflow does not select that unit file, so no standalone focused-pytest PASS is claimed.
- The final exact visual candidate passed the visual workflow's Ruff, mypy and comparator contract tests plus all eleven native captures.
- Canonical worker Quality was not started.
- No commit was pushed while an exact visual run was in progress.

## Current visual priority

`VISUAL-GAP-0002` remains the largest verified repeated defect, now partially reduced. Knowledge, Research and Sources still show the generic Chat inspector. The next bounded pair should be Knowledge + Research because both have strong reference evidence and existing real selection/workspace semantics. Use explicit none/unavailable states until real selection data is available. Do not modify System's real Runtime/Backup/Security-posture semantics.

Standalone PALLAS, Help and ComfyUI framing remain visible P1 gaps, but they affect fewer surfaces and stay behind the shared inspector problem.

## Readiness

- Run-start Develop canonical Quality: `SUCCESS` at `e6ba3d…`.
- Final rendered product SHA: `75029071aa63dbaa73ef42da16fb709cc6d8ca99`.
- Exact final runtime surfaces opened: `11/11`.
- Same-state/reference-equivalent pairs: `0/11` under the strict rule.
- Visual readiness: NOT READY.
- Integrator-ready claim: not made; worker remains materially divergent from Develop and the focused unit test has not yet received standalone exact-SHA execution evidence.

## Next run

1. Consume any exact-SHA results already present for the current worker before new work.
2. Re-open all 11 references and all 11 exact current runtime surfaces.
3. If the repeated inspector defect remains, bind at most Knowledge + Research truthful contexts.
4. Add or extend focused Qt coverage without weakening guards.
5. Produce/open a fresh exact-SHA Windows capture and document BEFORE -> AFTER before further mutation.
