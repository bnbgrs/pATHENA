# Alpha/Beta canonical handoff — 2026-10-01


## POST-MERGE CANONICAL STATE — 2026-10-01 23:xx Europe/Berlin

- PR #321 merged history-preserving into `develop/pathena-next`.
- Canonical Develop SHA immediately after merge: `fe8255a76aa0137bb55320c43f9c34bc8bddafa9`.
- #321 exact head before merge: `039df63633d4eab10cb10f05710ec226dd1cd341`.
- Exact-head integration evidence was terminal green on the same #321 head:
  - ATHENA Quality Gate PASS
  - pATHENA Core Focused Candidate PASS
  - pATHENA UI Focused Candidate PASS
  - pATHENA 11-Surface Visual Regression PASS
  - pATHENA Windows Package PASS
- Do not reopen #317/#318/#319/#320/#323 diagnosis. Those paths are closed by #321.
- #324 canonical commit-bundle serializer is green on its old base (Storage Focused PASS + full Quality PASS), but after #321 it is `221` commits behind Develop. Reconstruct its three-file delta on a fresh branch from current Develop, then requalify exact head before merge. Do not merge the stale branch directly.
- New Alpha/Beta E2E gap discovered on #321/current code: Chat STOP/cancellation is MISSING across Core/API/UI. Treat this as a real post-merge functional slice, not a styling issue.
- Cancellation acceptance contract:
  1. stable send-operation identity and concurrent cancel endpoint/state;
  2. cancel before provider call, between chunks, and immediately before assistant persistence;
  3. close provider stream when supported;
  4. ProcessingRun becomes cancelled, not failed, for user cancellation;
  5. durable user turn may remain; incomplete assistant must not persist;
  6. late provider completion after cancel must not persist an assistant;
  7. duplicate/late cancel is idempotent and truthful;
  8. Desktop/UI Stop only after real Core/API cancellation exists;
  9. direct and grounded normal-send paths remain green;
  10. explicitly classify transport-level abort as PARTIAL if a blocking provider `next(stream)` cannot be interrupted.
- Old PR #294 is source material only for cancellation semantics; do not merge it wholesale. It contains a known missing import defect around `GenerationCancelledError`.
- #322 remains old-stack source only. Port only its unique Research wrapping/accessibility delta after the higher-priority functional slices are stable.

### Worker ownership from this point

- **Integrator:** keep `develop/pathena-next` canonical; merge only fresh exact-head qualified slices.
- **Core/Storage:** reconstruct #324 from current Develop; then continue publication/head-verification/conflict-recovery/durable-worker/snapshot-replay gaps.
- **Runtime:** Windows/LM Studio E2E on current Develop, including server start without GUI, selected-model autoload, restart/reconnect/cleanup and truthful readiness.
- **QA/Core:** implement and qualify Chat STOP/cancellation end-to-end.
- **UI:** continue real usability cleanup only on current Develop; do not revive superseded V3 stacks.
- **All workers:** record exact SHA, tests/gates, remaining gap and next owner here after every substantive step.


## Canonical state

- Integration target: `develop/pathena-next`
- Develop before this slice: `6f51095bed7d612cab7308fe19da58f647401c56`
- Canonical integration PR: #321
- #321 exact head before this slice: `c4d916590b337beeaf93dab50369861cdc4f9079`
- Fresh stacked repair branch: `fix/321-quality-unblock-20261001-sol`
- Repair head after edits: `7d2ca7be05ab0988d6524ea486b6fde81c0c73d9`
- Do not restart diagnosis from #317/#318/#319/#320. Treat them only as historical/source branches.

## Exact #321 gate evidence before repair

- pATHENA UI Focused Candidate: PASS
- pATHENA Core Focused Candidate: PASS
- pATHENA 11-Surface Visual Regression: PASS
- pATHENA Windows Package: PASS
- ATHENA Quality Gate: FAIL

The Quality failure had two independent classes:

1. Ruff I001 import formatting in exactly:
   - `src/athena/desktop/pathena_v3_jobs.py`
   - `src/athena/desktop/pathena_v3_research.py`
   - `src/athena/desktop/pathena_v3_sources.py`
2. Canonical pytest:
   - one visible failure at `tests/unit/test_pathena_ui_refinement_100.py`
   - suite reached about 97% and then the 40-minute step timeout fired immediately after `tests/unit/test_update_manifest.py`

## Root cause: UI refinement integrity

The failing refinement contract was not treated as a test problem.

### First wrong product point

Backup actions did not have one stable identity contract across presentation/refinement layers.

- `system_backup.py` initially gives the action buttons a generic shared `newChatButton` object name.
- `pathena_workspace_presentation.py` assigns stable backup IDs by matching visible labels, but #321 did not cover the actual current labels `Create backup…` and `Restore copy…`.
- `pathena_ui_refinement_100.py` still searched backup actions by visible text under the System widget.

This makes accessibility/refinement installation depend on copy and widget ancestry instead of the actual installed controls.

### Repair

`src/athena/desktop/pathena_workspace_presentation.py`

- presentation now recognizes both normalized and current raw labels:
  - `Create backup` / `Create backup…` -> `backupCreateButton`
  - `Restore…` / `Restore copy…` -> `backupRestoreButton`
- existing stable IDs for Verify, Deep Verify, Targets and Add Target are preserved.

`src/athena/desktop/pathena_ui_refinement_100.py`

- tasks 87–92 now target the stable installed control identities:
  - `backupCreateButton`
  - `backupVerifyButton`
  - `backupDeepVerifyButton`
  - `backupRestoreButton`
  - `backupTargetsButton`
  - `backupAddTargetButton`
- no assertion, skip, xfail or safety contract was weakened.

This mirrors the stable identity direction already proven by the green related branch, but is reconstructed directly on #321 rather than merging the divergent branch.

## Ruff repair

Only import formatting was changed in:

- `src/athena/desktop/pathena_v3_jobs.py`
- `src/athena/desktop/pathena_v3_research.py`
- `src/athena/desktop/pathena_v3_sources.py`

No behavior change.

## Timeout classification

The pytest timeout is classified as **insufficient CI margin, not an evidenced hang**.

Evidence:

- #321 Quality pytest step began at approximately 06:11:21 and hit its 40-minute limit at 06:51:34.
- It had reached `tests/unit/test_update_manifest.py` at 97%.
- A related exact-head Quality PASS (#322) uses the same workflow and same 40-minute pytest limit.
- That successful run reached `test_update_manifest.py` at 11:43:02 and needed about 48 additional seconds to finish the remaining suite, reaching 100% at 11:43:50.
- The successful run therefore had only seconds of margin under the 40-minute step budget.

Repair in `.github/workflows/quality.yml`:

- quality job timeout: 50 -> 60 minutes
- canonical pytest step timeout: 40 -> 45 minutes

The suite, assertions and test selection remain unchanged.

## Commits in this repair slice

- `b519848959ee3e402228093944c7c39e335bd3e0` — Ruff import formatting, Jobs
- `c1ab443ba7fdd3458b18d9262e19b17fcc96041d` — Ruff import formatting, Research
- `4934967ef93359b0c806901f3224ca0e85f922c0` — Ruff import formatting, Sources
- `a3df2911c81197b367db896f1caa8aa9275277ba` — stable backup presentation identities
- `12c2ea097075e56b18c2ac1cc97ee55a6a9da0d3` — refinement tasks use stable backup identities
- `7d2ca7be05ab0988d6524ea486b6fde81c0c73d9` — measured Quality timeout margin

## Validation required now

Do not spend another run rediscovering the above. Validate this exact repair head.

Priority order:

1. Ruff must be PASS with the three I001 signatures gone.
2. Focused `tests/unit/test_pathena_ui_refinement_100.py` must PASS.
3. Full ATHENA Quality must reach 100% within the new measured budget.
4. Re-run/verify UI Focused and 11-Surface Visual on the repair head because presentation identity changed.
5. Re-run/verify Core Focused and Windows Package as exact-head integration evidence.

If all are green, merge the stacked repair into #321 (or otherwise preserve the exact repair commits), then merge the resulting #321 candidate history-preserving into `develop/pathena-next`.

## #322 handling

PR #322 head `2384567392b60ee1dcd8fa2fc0a081c67251454b` has Quality PASS but is based on the old #318 stack and diverges substantially from #321.

Do **not** merge #322 directly.

After #321 + this repair is integrated, reconstruct only #322's unique Research UI delta on a fresh branch from the new Develop and qualify it there.

## Parallel Alpha/Beta work while gates run

Core owner should not duplicate this UI/Quality repair. Continue independent spec gaps, especially the explicitly remaining structured-replication work after #291:

- canonical commit-bundle serializer
- verified `long_term_root` filesystem publication
- target-head verification before publication
- conflict/recovery on unexpected target history
- no silent history overwrite
- durable worker composition
- snapshot/replay

Runtime owner should validate the real #321 LM Studio/Windows behavior rather than only package success:

- per-user `lms.exe` discovery
- loopback server start without GUI
- selected-model autoload
- truthful readiness
- restart/reconnect/cleanup
- first-run and persisted Settings behavior

QA owner should proceed to real Alpha/Beta E2E flows once this exact Quality repair is green.

## Next owner / next action

- **Integrator:** exact-head gate qualification and merge path.
- **UI/QA:** only investigate further if `test_pathena_ui_refinement_100.py` remains red on the repair head; use the new failure signature, not the old diagnosis.
- **Core:** continue disjoint Alpha/Beta gaps.
- **Runtime:** continue Windows/LM Studio E2E.
- **All workers:** update this file with exact SHA, evidence, merged PR/commit, remaining gap and next owner after every substantive step.

## UI truthful composer/network slice — 2026-10-02 00:4x Europe/Berlin

- Branch: `fix/chat-composer-truthful-controls-20261002-sol`
- PR: #330
- Product-code head before this handoff commit: `f9d36e04b95c5554251d6990c61fc254090d75a3`
- Base at PR creation: `develop/pathena-next@67174198e1494fd4c8678aad60756c39ef5c160b`
- Ausgangslage / Root Cause:
  - Chat Send mutated its visible label between `SEND` and `WORKING`, while constructor/build paths also disagreed on button text. The control therefore had unstable/competing presentation instead of one identity.
  - Composer rendered `ATTACH` as a static label although no attachment action or Core contract exists. This looked like capability without functionality.
  - Rail hard-coded `NET ONLINE` and `TOR OFF` although the current Desktop/Core snapshot exposes neither network nor TOR truth.
- Änderungen:
  - Send is one stable `→` control with accessible name `Send message`; real busy state remains disabled and is exposed through accessible description + tooltip instead of fake label replacement.
  - Removed the non-functional `ATTACH` affordance.
  - Network/TOR display now fails closed to `UNKNOWN` and states why it cannot claim a measured value.
  - Added focused Qt regression assertions for all three behaviors.
- Dateien:
  - `src/athena/desktop/window.py`
  - `tests/unit/test_desktop_direct_chat.py`
  - `tests/unit/test_desktop_shell.py`
- Parallelität / Konfliktrisiko:
  - No overlap with #329 Core cancellation files, #325 Storage, #326 Research workspace, or #327 Quality harness.
  - Stale #298 is source material only; #330 is the fresh current-Develop reconstruction and should supersede that old-base send-button slice if qualified.
  - Future Desktop STOP UI must build on real cancellation after #329 is integrated; do not reintroduce fake `WORKING`/STOP text before Core cancellation is available on the target base.
- Validierung:
  - Source diff reviewed against current Develop; #330 was 4 commits ahead / 0 behind at PR creation and contained only the three product/test files above.
  - Focused regression tests are committed. GitHub exact-head workflows were not yet visible immediately after PR creation; do not mark the slice integrated until terminal exact-head evidence exists.
  - Native interactive UI was not run in this environment because repository checkout/desktop execution is unavailable here; rely on the repository's Windows UI/visual workflows for native evidence.
- Nächster Schritt:
  1. qualify #330 exact head with UI Focused + Quality + visual/native evidence;
  2. fix any exact-head failure on #330 rather than weakening gates;
  3. merge only after those gates are green and re-check current Develop for drift;
  4. then close/supersede stale #298 rather than merging both.

