# Settings runtime recovery — handoff (2026-10-02)

## Branch / PR
- Branch: `fix/settings-news-retry-20261002-sol`
- PR: #333 — Settings: recover runtime state and unify model persistence
- Base inspected: `develop/pathena-next@67174198e1494fd4c8678aad60756c39ef5c160b`
- Product files intentionally limited to `src/athena/desktop/pathena_settings_runtime.py` plus its focused unit tests.

## Ausgangslage
Four real Settings-runtime state defects existed on current Develop:
1. A transient failure during the first News-profile load permanently latched `_news_requested=True`, preventing later snapshots from retrying until app restart.
2. Starting a News load/save changed visible copy but retained the preceding semantic `pathenaUiState` and accessible description.
3. `_read_model()` could return on missing/mismatched persisted `model_id` before checking `QSettings.status()`, hiding read/format errors behind stale persistence presentation.
4. The real Settings model chooser did not trigger persisted hydration. It updates the Chat model selector programmatically with signals blocked, so the runtime's prior `model_selector.activated` hook was never reached.

## Root causes / changes
- Initial News failure now releases the request latch only while no valid profile has ever been loaded; save failures with an existing profile keep the valid profile state.
- News load/save request starts explicitly enter neutral `idle` semantics and refresh their accessibility description.
- Persisted model reads always evaluate `QSettings.status()` before treating model identity as absent.
- `settings_model_selector.activated` now invokes the same hydration path as `model_selector.activated`.

## Behavior after
- A transient first News read can recover on a later fresh Core snapshot without restarting pATHENA.
- Loading/saving no longer advertises stale success/error semantics.
- Unreadable local settings fail closed instead of retaining an older success indication.
- Selecting model B from Settings restores model B's persisted context, output, temperature and thinking values exactly as selection from Chat does.

## Validation
Focused regression coverage was added for:
- News retry after initial failure.
- Honest News loading semantics.
- Honest News saving semantics.
- QSettings read error with absent model identity.
- Persistence restoration through the Settings model chooser.

Predecessor exact head `9d1318900c84cc76d6bff9922fadcbf2df512cfd` passed UI Focused run 36937020536. Current head moved after the Settings-selector fix; only gates attached to the final head may be used for integration.

Direct local checkout/execution was unavailable in this agent environment because github.com DNS resolution failed. Native Windows GitHub Actions are therefore the executable evidence source; no local PASS is claimed.

## Native UI / visual-gate evidence
During validation, visual run 36937020465 captured all 11 real Windows surfaces but failed on unrelated runtime-dependent System/PALLAS pixels. The same Develop product tree had passed the visual gate at merged Research #326.

Separate root causes were handed off rather than mixed into this PR:
- #352 owns deterministic PALLAS visual capture.
- System/Settings workspace capture uses a fixed 7 s delay while the real app schedules Core refreshes through 20 s; this can capture either “Waiting for status” or a later Core/provider state. Commented on #352 for a follow-up harness-only slice after its integration. Do not loosen comparator thresholds or blindly replace baselines.

## Parallel work / conflict risk
Do not fold these active scopes into #333:
- #325 Storage
- #327 Qt Quality isolation
- #329 Chat cancellation
- #330 UI send-control state
- #331/#334 LM Studio runtime
- #336 Sources import queue
- #352 PALLAS visual determinism

Potential conflict is low: #333 modifies only the Settings runtime controller and its unit test.

## Commits before this handoff
- `beca477da5d1ca4c63839e709350dcccff12bf60` News retry product fix
- `dd6682c5c60219391f9315a0c4fed8d837dbaa93` News retry regression
- `a3a4db4dbb9745b3beafd009191f2ae0fd596690` News semantic in-flight state
- `2d94cfdf5b829474f0af4c5c028d04b6cd8c3191` semantic-state regressions
- `77672247a783fd986725d4bef42f144a451d1e07` fail-closed persisted read
- `9d1318900c84cc76d6bff9922fadcbf2df512cfd` read-error regression
- `ef3ddcf49302deb0f0bb4ee3e29e79c53df31443` Settings selector hydration
- `f082e1dfc9f04d1c81cd6ad0d07e76060abb51e7` Settings selector regression

## Next integrator action
1. Read the exact final PR head.
2. Require exact-head UI Focused, ATHENA Quality Gate and relevant native visual evidence.
3. If a visual run fails only on known asynchronous System/PALLAS capture drift, inspect the artifact and correlate changed surfaces with the PR diff; do not mutate product code or baselines without causal evidence.
4. Merge only after the exact current head is qualified against then-current `develop/pathena-next`.
