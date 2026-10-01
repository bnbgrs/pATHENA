# Alpha/Beta canonical handoff — 2026-10-01

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
