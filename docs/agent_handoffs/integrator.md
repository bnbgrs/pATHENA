# pATHENA Feature Integrator Handoff

## Current integration baseline

- Integration target: `develop/pathena-next`.
- Exact current Develop: `305703362d539ed467dec27cbc7300a495b3ca03`.
- Exact Develop canonical Quality: `34726544110 = SUCCESS`.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.
- Current worker heads observed during this integrator run: Errors `4d56cdbde52af238917568948daf86bd7c112930`; Spec/Core `78d51621cbdfa3282cd236b5d0c7f5984abedcae`; Backend `a709c229d6994c159490c2c1eaf3f2549f12cf56`; UI `722ca4fd3afa6af9b2eecc3c82700efe287e77ed`.

## Manual bounded UI candidate — exact-head green

Integrator-owned branch: `manual/longrun-20260913@03ab0b813cdf489502a8ac08bb69c7d25878634a`, PR `#127`, based exactly on current green Develop. It does not mutate any worker branch.

Bounded product behavior:

- host the existing local-only ComfyUI controller inside the shared pATHENA workspace shell rather than a detached dialog;
- invalid optional `PATHENA_COMFYUI_URL` configuration fails closed without preventing desktop startup;
- Command Palette truth no longer installs ComfyUI as a side effect and instead reports only already-registered capabilities;
- full PALLAS is hosted in the shared center workspace rather than a detached dialog while preserving synchronized PALLAS state;
- PALLAS and ComfyUI shell workspaces are mutually exclusive so two center surfaces cannot remain visible concurrently;
- Settings secondary navigation uses the existing Settings destinations in a dedicated quiet rail;
- focused Qt regressions cover shell hosting, optional ComfyUI failure, PALLAS/ComfyUI exclusivity, navigation restoration and Settings secondary navigation.

Exact evidence:

- pATHENA UI Focused Candidate `34729288667 = SUCCESS` on exact head `03ab0b813cdf489502a8ac08bb69c7d25878634a`.
- Canonical Quality `34729288659 = SUCCESS` on the same exact head.
- Full pytest, Specification Validator, Ruff, mypy, Linux Storage, Windows Path Safety/release guards and Local Install all completed `SUCCESS`.
- PR `#127` is `draft=false` / Ready for review and remained mergeable against exact Develop `305703362...` at the latest drift check.

The UI worker itself is currently only synchronized to Develop at `722ca4fd3afa6af9b2eecc3c82700efe287e77ed`; no newer worker product slice was observed after that synchronization during this run.

## Current worker qualification

### Spec/Core — current exact head still in canonical full pytest

Current worker head remains `78d51621cbdfa3282cd236b5d0c7f5984abedcae` (`fix(core): distinguish unsupplied revision reason`).

Effective current delta versus Develop is bounded to:

- `src/athena/api/knowledge_history.py`;
- `src/athena/knowledge/revision_change_explanation.py`;
- `tests/unit/test_knowledge_history_api.py`;
- `tests/unit/test_revision_change_explanation.py`.

Integrator review found the semantics provenance-safe: the API returns stored revision identity/actor/time plus deterministic payload-diff explanation; it does not invent an unstored reason. The follow-up wording correctly distinguishes “no reason supplied to this explanation” from a claim that no persisted reason exists.

Evidence on exact current head:

- Core Focused `34730134596 = SUCCESS`.
- Canonical `34730134589`: Local Install `SUCCESS`, Linux Storage `SUCCESS`, Windows Path Safety/release guards `SUCCESS`, Specification Validator `SUCCESS`, Ruff `SUCCESS`, mypy `SUCCESS`.
- Full canonical pytest was still `in_progress` at the latest observation in this run.

Do not consume the older `80e7c8f8...` predecessor. Consume only the exact current head after its exact canonical final result and a branch-head recheck.

### Backend/Storage — owner repair for ERR-0049 is now present

Current Backend head advanced to `a709c229d6994c159490c2c1eaf3f2549f12cf56` (`fix(storage): validate complete sidecar rotation`).

Effective current delta versus Develop is bounded to:

- `src/athena/jobs/schedule_startup.py`;
- `src/athena/storage/database.py`;
- `tests/unit/test_schedule_startup.py`.

The new Storage repair targets the exact `ERR-0049` root cause previously isolated by the failing process-separated startup test. It preserves immediate fail-closed behavior when the primary DB identity changes, preserves rejection of partial/mixed WAL/SHM transitions, and only permits coordinated complete→complete WAL/SHM rotation to proceed to the existing full read-only validation and post-validation identity check.

Integrator review of schedule-startup also found the slice bounded: an active write transaction is required; only missing due occurrences are materialized; backfill policy is respected; and identity collisions are detected before partial insertion.

Exact evidence on current Backend head:

- Backend Focused `34730587779 = SUCCESS`.
- Storage Focused `34730587918 = SUCCESS`.
- Canonical `34730587873`: Local Install `SUCCESS`, Linux Storage `SUCCESS`, Windows Path Safety/release guards `SUCCESS`, Specification Validator `SUCCESS`, Ruff `SUCCESS`, mypy `SUCCESS`.
- Full canonical pytest was still `in_progress` at the latest observation in this run.

`ERR-0049` must remain operationally open until this exact current Backend canonical run completes successfully and/or the Error owner consumes that evidence. Do not mark the error closed from focused evidence alone.

### Errors / ERR-0049 historical root cause

Errors handoff `postmerge/errors@4d56cdbde52af238917568948daf86bd7c112930` still classifies `ERR-0049 = OPEN / P1`.

The original failure was concurrent startup against the same SQLite runtime: the primary DB identity stayed stable while a legitimate WAL/SHM complete→complete object rotation occurred between startup preflight and revalidation. The old guard accepted exact identity, complete absent→complete publication and complete→absent withdrawal, but rejected that coordinated rotation.

The owner repair now exists on Backend `a709c229...`; wait for exact canonical closure before updating Error state.

## Requalified stale boundary handoff

`docs/agent_handoffs/manual-open-boundaries-current-20260912.md` is now explicitly marked `HISTORICAL / DO NOT RE-PORT` on this integrator branch.

Read-only requalification established:

- old candidate `manual/open-boundaries-current-20260912@b03c27a1521923d319bb2d17ce0ebff110f3a402` had exact canonical Quality `34677566133 = SUCCESS` and dedicated Windows Runtime Boundary `34677566055 = SUCCESS`;
- current Develop contains the same boundary implementation lineage;
- representative owned blobs are byte-identical between the old candidate and current Develop: `scripts/validate_spec.py@86425b26305b0e067bd2d24417548d84194e6243`, `scripts/windows_packaging_safety.ps1@8c2735d6f829bb36fc540c460055988bba3bc236`, and `.github/workflows/windows-runtime-boundary.yml@5ebf22b6361ddc66658a10718f5d8e999585c512`;
- current Develop canonical `34726544110 = SUCCESS` is later exact integrated evidence;
- GitHub issues `#92`, `#93`, `#95`, and `#96` are already `closed / completed`.

Therefore those four boundary repairs are already integrated and closed. Do not recreate, re-port, reopen, or merge the historical boundary candidate absent a new current exact-SHA reproducer.

## Deferred SHM telemetry candidate

Historical branch `manual/product-release-closure-20260912@befee1e92bec47388e96b8c1dbd59b930626d602` contains a small Storage-health delta adding `shm_size_bytes` telemetry plus a focused test. Current Develop does not contain that field.

This integrator run deliberately did **not** port it:

- it changes a public `StorageHealthSnapshot` dataclass contract;
- GitHub code-search indexing was incomplete for a trustworthy current-consumer inventory;
- Backend/Storage currently owns the more important active `ERR-0049` repair;
- this telemetry is not on the critical release path compared with exact qualification/integration of UI, Core and Backend.

Requalify consumers/serialization and owner availability before any future port. Do not use this historical candidate as a merge-ready signal.

## Collision avoidance and integration strategy

- Manual UI candidate touches only desktop UI files/tests listed in PR `#127`.
- Spec/Core effective current product delta is Knowledge-History code/tests and is disjoint from the UI candidate.
- Backend effective current product delta is schedule-startup + Storage-startup identity code/tests and is disjoint from both UI and Spec/Core current deltas.
- Historical Boundary issues `#92/#93/#95/#96` are integrated/closed and are not work items.
- SHM telemetry is deferred, not promoted.
- No force push, history rewrite, Skip/XFail, release-guard relaxation, worker-branch mutation or `main` mutation occurred.

If Spec/Core `78d51621...` and Backend `a709c229...` both finish exact-current canonical-green **without either worker head moving**, prefer one bounded integration batch based on exact-green UI head `03ab0b81...` rather than two additional serial Develop mutations. Copy only the exact verified effective files from each owner head, open a new Draft integration PR, and require the full combined exact-head gate suite. Do not directly merge worker branch history.

If either owner head moves or its canonical fails, keep PR `#127` independently promotionsfähig and do not delay it indefinitely for batching.

## Current evidence rules

- `docs/agent_logs/ERROR_LEDGER.md` remains historical where newer exact-SHA evidence exists.
- `docs/agent_logs/ALPHA_BETA_PROGRESS.md` currently lags newer worker/Gate evidence and must not override exact current CI.
- `docs/agent_logs/ALPHA_BETA_PROGRESS.md` contains no invented completion percentage.
- Historical release-guard signatures are not reopened without current exact-SHA reproduction.
- `docs/ui/11_SCREEN_REFERENCE_MANIFEST.md` and `docs/ui/VISUAL_GAP_LEDGER.md` remain fail-closed: no screenshot `MATCH` without opened original reference plus a real exact-SHA render.
- Superseded Worker CI is not accepted as evidence for a newer worker head.

## Persistent release guards

Retain without relaxation: pypdf packaging; fail-closed Frozen argv; Desktop/Worker two-EXE split; exactly one Desktop instance with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock cluster; duplicate-column, Core-startup and storage-bootstrap regression signatures.

## Promotion state

`PROMOTION_READY=NO` for Develop/release as a whole.

Current bounded promotion state:

- UI PR `#127`: `EXACT_HEAD_CANONICAL_GREEN / READY_FOR_INTEGRATION_REVIEW`.
- Spec/Core `78d51621...`: `FOCUSED_AND_FAST_CANONICAL_GREEN / FULL_PYTEST_PENDING`.
- Backend `a709c229...`: `BACKEND_AND_STORAGE_FOCUSED_GREEN / FAST_CANONICAL_GREEN / FULL_PYTEST_PENDING`.
- `ERR-0049`: `OWNER_FIX_PRESENT / CLOSURE_PENDING_EXACT_CANONICAL`.

Next integrator actions, in order:

1. Re-read Spec/Core exact canonical `34730134589` and Backend exact canonical `34730587873` after their full pytest steps finish.
2. Re-read `develop/pathena-next`, `postmerge/spec-core`, and `postmerge/backend`; reject stale evidence if any head moved.
3. If Core and Backend are exact-current canonical-green and still disjoint, build one bounded integration candidate on top of exact-green UI `03ab0b81...`, copying only the verified current effective files.
4. Require all focused lanes plus canonical Quality on the combined exact integration head before any Develop mutation.
5. If either worker is not exact-current green, integrate/review UI independently rather than weakening or bypassing a worker gate.
6. Do not spend worker or integrator cycles on already closed boundary issues `#92/#93/#95/#96` or deferred SHM telemetry absent new evidence.
7. After any integration into Develop, require canonical Quality on the resulting exact Develop SHA before the next Develop mutation.
