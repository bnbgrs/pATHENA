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

## UI Chat control truth slice — 2026-10-02 00:xx Europe/Berlin

- Branch: `fix/chat-composer-truthful-controls-20261002-sol`
- PR: #330
- Current branch head before this handoff update: `8e63bfd8ad38507500727720df598c10a639fb57`
- Base at PR creation: `develop/pathena-next@67174198e1494fd4c8678aad60756c39ef5c160b`
- Ausgangslage / Root Cause:
  - The real V3 composer paints the visible send affordance from `send_button.text()`.
  - Legacy `AthenaMainWindow.apply_chat_busy()` mutated that shared button text to `WORKING` while busy and `SEND` afterward. Because V3 reuses the same real button, those words were painted inside the 44×44 V3 send control and replaced the intended arrow.
  - V3 also rendered a permanently teal `v3RuntimeDot` beside the real runtime text. The dot had no Core/provider-state binding, so it visually implied healthy readiness even during connecting/error/disconnected states.
- Änderungen:
  - Send control keeps one stable semantic text through busy/idle. Busy is represented by the existing real disabled state plus accessible description/tooltip; no fake STOP behavior is introduced before Core cancellation is integrated.
  - V3 keeps its intended `↑` glyph because the base busy handler no longer overwrites it.
  - Removed the unmeasured V3 runtime dot; the real runtime status text remains.
  - Added direct-chat and real V3-shell regressions covering stable send text, busy/idle accessible state, and absence of the fake runtime dot.
- Dateien mit verbleibender Delta:
  - `src/athena/desktop/window.py`
  - `src/athena/desktop/pathena_v3_shell.py`
  - `tests/unit/test_desktop_direct_chat.py`
  - `tests/unit/test_pathena_v3_shell.py`
  - this canonical handoff
- Scope correction during the run:
  - Initial hardening changes around legacy `ATTACH` and `networkState` were deliberately reverted after tracing the real startup path. `PathenaMainWindow` already hides those legacy placeholders before V3 composition, so retaining those changes would have added noise without improving the shipped UI.
- Parallelität / Konfliktrisiko:
  - No overlap with #329 Core cancellation files, #325 Storage, #326 Research workspace, or #327 Quality harness.
  - Stale #298 is source material only. #330 reconstructs the send-state fix on current Develop and adds real V3 regression coverage.
  - Future Desktop STOP UI must build on real cancellation after #329 is integrated; do not reintroduce `WORKING`/STOP text as a visual-only substitute.
- Validierung:
  - Earlier #330 head reached UI Focused SUCCESS before the scope correction; those results do not qualify the current head.
  - Current exact-head Quality/UI/Visual workflows must be rechecked after this handoff commit.
  - Native desktop execution is unavailable in this environment, so native evidence must come from the repository's Windows UI/visual workflows.
- Nächster Schritt:
  1. require exact-head UI Focused + Quality + 11-surface Visual to be terminal green;
  2. inspect any visual delta caused by removal of the fake runtime dot rather than updating a baseline blindly;
  3. merge only after current-Develop drift is rechecked;
  4. then supersede/close stale #298 rather than merging both.

