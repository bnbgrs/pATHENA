# Jobs helper-response truth / recovery handoff — 2026-10-02

## Ausgangslage

Base: `develop/pathena-next@67174198e1494fd4c8678aad60756c39ef5c160b`.

The native Jobs workspace executes the canonical jobs CLI through one short-lived `QProcess`.
Three concrete failure paths were still presenting misleading or destructive UI state:

1. `list` output was parsed directly while mutating the QListWidget. Any non-8-field line was silently skipped, yet an exit-0 helper response still ended as **Jobs refreshed**. A partial/corrupt response could therefore hide rows and be presented as success.
2. An unverified transition set a diagnostic tooltip on the status label, but later successful list/show/action states did not consistently clear it. The visible success state could retain a stale failure diagnostic.
3. Qt can emit `errorOccurred` and later `finished` for the same process failure. `_process_error()` cleared operation identity; the later `_process_finished()` could overwrite the specific failure with a generic second message.
4. A failed background list refresh wrote merged helper output into the details pane even when the user had an existing selected job, destroying useful current context.

## Root Cause

The Jobs UI treated process exit status as the main trust boundary but did not validate the complete exit-0 list payload before projecting it into widgets. Status text, tooltip/accessibility diagnostics, and process-terminal signals were also managed independently instead of as one coherent terminal state.

## Änderungen

### `src/athena/desktop/jobs_lifecycle.py`

- Added immutable `JobListEntry`.
- Added `parse_job_list()` as the list-response trust boundary.
- The parser validates the **entire** response before any UI mutation:
  - exactly 8 tab-separated fields per non-empty line;
  - valid job UUID;
  - recognized job state;
  - non-empty job type/stage;
  - integer priority/retry/update timestamp fields;
  - non-negative retries/timestamp.
- Empty output remains a valid empty queue.

### `src/athena/desktop/jobs_workspace.py`

- List responses are parsed completely before `QListWidget` is cleared/rebuilt.
- Malformed exit-0 list responses fail closed and keep the prior list/selection instead of presenting partial success.
- If a selected job exists, list-refresh failures no longer replace its details pane with raw helper diagnostics.
- Added one status setter that keeps visible text, UI state, tooltip and accessible description synchronized; a later success clears old diagnostics.
- Added per-process error bookkeeping so an `errorOccurred` result is not overwritten by the following `finished` signal.
- `_render_job_list()` now accepts already-validated `JobListEntry` values.

### `tests/unit/test_pathena_jobs_lifecycle.py`

Added regression coverage for:

- successful complete list parsing;
- malformed/unknown-state list rejection;
- preservation of previous list selection/details on invalid exit-0 response;
- preservation of selected details on nonzero background refresh failure;
- stale error diagnostic clearing after later success;
- `errorOccurred -> finished` double-signal behavior preserving the first specific error.

## Verhalten danach

- **Exit 0 is no longer sufficient for Jobs list success.** The complete local response must match the jobs CLI contract.
- A corrupt/partial response leaves the previous user-visible job projection intact and reports an error.
- Background refresh failures do not destroy the selected job's current details.
- Status success/error semantics are internally consistent across text, tooltip, accessibility description and UI-state property.
- One underlying QProcess failure produces one terminal user-visible error instead of a second generic overwrite.

No DurableJobService persistence or transition semantics were changed.

## Dateien

- `src/athena/desktop/jobs_lifecycle.py`
- `src/athena/desktop/jobs_workspace.py`
- `tests/unit/test_pathena_jobs_lifecycle.py`
- this handoff

## Validierung

### Completed

- Parallel-work inventory rechecked immediately before implementation.
- No overlap with active #325/#327/#329/#330/#331/#332/#333/#334/#335/#336/#337/#338/#339/#340 product file sets at the time of the run.
- Branch comparison against the exact base was clean and 0 commits behind before the handoff.
- Exact source was re-read from GitHub after writes.

### Not locally executable in this run

The execution container cannot resolve `github.com`, so the repository cannot be cloned and pytest/Qt cannot be run locally. This is an execution-environment DNS limitation, not a claimed PASS.

Required exact-head validation after the PR is opened:

1. `pytest tests/unit/test_pathena_jobs_lifecycle.py`
2. Ruff / formatting / type checks used by canonical Quality
3. canonical ATHENA Quality gate
4. if a native Windows/UI gate is attached to the PR, inspect it as supporting evidence

Do **not** mark this slice integrated based only on code review.

## Abhängigkeiten / Konfliktrisiko

- Scope is isolated to Jobs projection/lifecycle tests.
- It does not touch Chat cancellation/Stop, LM Studio, Sources, Storage, Research, Settings/News, update security, Windows packaging, or global Qt harness files.
- If `develop/pathena-next` advances with any change to the three Jobs files before integration, compare/reconstruct on the fresh base rather than overwriting that work.

## Nächste sinnvolle Schritte

1. Qualify this exact PR head with the focused Jobs test and canonical Quality.
2. If a failure is attributable to this branch, fix the root cause on this branch and update this handoff.
3. If green and still conflict-free, integrate as one bounded Jobs reliability slice.
4. After integration, continue with another disjoint P0/P1 workflow rather than reopening this area without new evidence.

## Commit / Branch

Branch: `fix/jobs-protocol-truth-20261002-sol`

Product/test commits before this handoff:

- `a831ff8226c9c5d696bbebad6434671fdf8dace1` — validate complete Jobs list responses
- `151eb1756833df470b9ae9b0bb47230a4c947cc1` — synchronize Jobs status/process failure handling
- `586de1fec148ca8d2f4c75b2ef0612a52907bce2` — preserve selected details on refresh failure
- `c83ab20d1d7c34e41ebcebb1ad7f7ce995352b55` — malformed-response/process-race tests
- `584c8a0d0749a0e2c73eed7e54c546868ef5b409` — refresh-failure selection regression

## Follow-up during the same run: background selection recovery

Static race review after PR creation found one additional continuity defect in the same ownership path.

When a user selected a different job while an old show/action helper owned the QProcess, foreign output was correctly kept away from the new selection, but completion of the old operation did not automatically load the new current job. The background-owner banner could therefore remain after the process was already done.

Repair:
- added current-selection detail reload once the previous job-specific operation is terminal and the process is idle;
- applies on success, verified-action failure, nonzero helper exit, and process error;
- errorOccurred may fire before QProcess is fully NotRunning, so finished now retries pending recovery when the background-owner marker is still present;
- focused regression covers successful background show completion selecting/loading the new job.

Additional commits:
- d9745b426b49a6ad3e1692c442cb3c6c4989e59b — reload details after background selection change
- 12d41c865da09092b9c900f54e86f41892c9da43 — background selection detail recovery test
- 26cb2449830db7679e0ded73ee141ebe347eecf9 — retry selection recovery after process error

Parallel dependency observed:
- PR #351 hardens jobs_cli single-line framing. It is complementary to this branch's strict list parser and should be preserved; this branch does not modify jobs_cli.py.
- PR #353 changes short-lived helper bootstrap/shutdown and also touches jobs_cli.py. Its output contract is unchanged by the inspected diff; do not duplicate it here.

Requalify the latest PR head, not the earlier 9ed47e63/12d41c86 intermediate heads.

