# pATHENA Feature Integrator Handoff

## Current integration baseline

- Integration target: `develop/pathena-next`.
- Exact current Develop: `305703362d539ed467dec27cbc7300a495b3ca03`.
- Exact Develop canonical Quality: `34726544110 = SUCCESS`.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.
- Current worker heads observed during this integrator run: Errors `4d56cdbde52af238917568948daf86bd7c112930`; Spec/Core `78d51621cbdfa3282cd236b5d0c7f5984abedcae`; Backend `185662aafe7ab539fafd698e021635debfcc2a60`; UI `722ca4fd3afa6af9b2eecc3c82700efe287e77ed`.

## Manual bounded UI candidate

A separate integrator-owned branch exists at `manual/longrun-20260913@03ab0b813cdf489502a8ac08bb69c7d25878634a`, Draft PR `#127`, based exactly on current green Develop. It does not mutate any worker branch.

Bounded product behavior in that candidate:

- the existing local-only ComfyUI controller is hosted inside the shared pATHENA workspace shell rather than a detached dialog;
- invalid optional `PATHENA_COMFYUI_URL` configuration fails closed without preventing the desktop from starting;
- Command Palette truth no longer installs ComfyUI as a side effect and instead reports only already-registered capabilities;
- full PALLAS is hosted in the shared center workspace rather than a detached dialog while preserving synchronized PALLAS state;
- PALLAS and ComfyUI shell workspaces are mutually exclusive so two center surfaces cannot remain visible concurrently;
- Settings secondary navigation uses the existing Settings destinations in a dedicated quiet rail;
- focused Qt regressions cover shell hosting, optional ComfyUI failure, PALLAS/ComfyUI exclusivity, navigation restoration and Settings secondary navigation.

Exact evidence:

- pATHENA UI Focused Candidate `34729288667 = SUCCESS` on exact head `03ab0b813cdf489502a8ac08bb69c7d25878634a`.
- Exact-head canonical Quality `34729288659`: Linux Storage `SUCCESS`, Local Install `SUCCESS`, Windows Path Safety/release guards `SUCCESS`; in Python 3.12 quality, Specification Validator `SUCCESS`, Ruff `SUCCESS`, mypy `SUCCESS`, while full pytest was still running at the last observation in this run.
- Do not promote PR `#127` from stale earlier-head evidence. Only exact-head canonical completion is promotion-relevant.

The UI worker itself is currently only synchronized to Develop at `722ca4fd3afa6af9b2eecc3c82700efe287e77ed`; no newer worker product slice was observed after that synchronization during this run.

## Current worker qualification

### Spec/Core

Current worker head moved to `78d51621cbdfa3282cd236b5d0c7f5984abedcae` (`fix(core): distinguish unsupplied revision reason`) after the previously canonical-green `80e7c8f8bb3c15c41ec8483dd0a57687016ba99c` revision-history candidate.

Do not integrate the older `80e7c8f8...` merely because its canonical evidence is green while the owner is actively mutating the same Knowledge-History files. Requalify the current exact Spec/Core head or consume a later owner handoff first.

### Backend

Current Backend head `185662aafe7ab539fafd698e021635debfcc2a60` remains bounded versus Develop to `src/athena/jobs/schedule_startup.py` and `tests/unit/test_schedule_startup.py`.

Evidence:

- Backend Focused `34728206760 = SUCCESS`.
- Canonical `34728206821 = FAILURE`, but downloaded exact diagnostics show the schedule-startup owner failure is gone.
- Full pytest result is `1 failed, 5029 passed, 17 skipped` and the sole failure is the independent process-separated storage-startup race now tracked as `ERR-0049`.
- Specification Validator, Ruff, mypy, Linux Storage, Windows Path Safety/release guards and Local Install are green on that Backend exact run.

Do not integrate Backend until `ERR-0049` has an owner-green successor and exact canonical evidence.

### Errors / ERR-0049

Errors handoff `postmerge/errors@4d56cdbde52af238917568948daf86bd7c112930` classifies `ERR-0049 = OPEN / P1`.

The failure is in concurrent startup against the same SQLite runtime. `SQLiteDatabase._revalidate_existing_identity()` currently accepts exact identity, complete absent→complete WAL/SHM publication and complete→absent withdrawal, but rejects a complete→complete WAL/SHM object-identity transition even when the primary DB identity is unchanged.

The existing recovery inspection is intentionally strong: read-only validation rejects symlink/reparse or invalid file types, validates ATHENA SQLite identity/schema, runs `PRAGMA quick_check`, and re-captures filesystem identity. Any repair must preserve the immediate fail-closed primary DB identity guard, partial-sidecar rejection and foreign/tamper protections.

Ownership remains Backend/Storage. This integrator run deliberately did not parallel-modify the storage guard because the Error handoff explicitly assigns the product repair to Backend/Storage and asks Error to verify/close rather than compete on the mutation.

## Requalified stale boundary handoff

`docs/agent_handoffs/manual-open-boundaries-current-20260912.md` still describes issues `#92`, `#93`, `#95`, and `#96` as awaiting integration, but that text is stale and must not be used to schedule another port.

Read-only requalification in this run established:

- old candidate `manual/open-boundaries-current-20260912@b03c27a1521923d319bb2d17ce0ebff110f3a402` had exact canonical Quality `34677566133 = SUCCESS` and dedicated `pATHENA Windows Runtime Boundary` `34677566055 = SUCCESS`;
- current Develop contains the same boundary implementation lineage;
- representative owned blobs are byte-identical between the old candidate and current Develop: `scripts/validate_spec.py@86425b26305b0e067bd2d24417548d84194e6243`, `scripts/windows_packaging_safety.ps1@8c2735d6f829bb36fc540c460055988bba3bc236`, and `.github/workflows/windows-runtime-boundary.yml@5ebf22b6361ddc66658a10718f5d8e999585c512`;
- current Develop canonical `34726544110 = SUCCESS` is later exact integrated evidence;
- GitHub issues `#92`, `#93`, `#95`, and `#96` are already `closed / completed`.

Therefore these four boundary repairs are **already integrated and closed**. Do not recreate, re-port, reopen, or merge the historical boundary candidate unless a new current exact-SHA reproducer establishes a distinct regression.

## Collision avoidance

- Manual UI candidate touches only desktop UI files/tests listed in PR `#127`.
- Backend effective product delta is schedule-startup code/tests and does not overlap the manual UI candidate.
- Spec/Core current effective product delta is Knowledge-History code/tests and does not overlap the manual UI candidate.
- The P1 storage race was investigated read-only here and left to its declared owner.
- Historical Boundary issues `#92/#93/#95/#96` are integrated/closed and are not work items.
- No force push, history rewrite, Skip/XFail, release-guard relaxation, worker-branch mutation or `main` mutation occurred.

## Current evidence rules

- `docs/agent_logs/ERROR_LEDGER.md` remains historical where newer exact-SHA evidence exists.
- `docs/agent_logs/ALPHA_BETA_PROGRESS.md` contains no invented completion percentage.
- Historical release-guard signatures are not reopened without current exact-SHA reproduction.
- `docs/ui/11_SCREEN_REFERENCE_MANIFEST.md` and `docs/ui/VISUAL_GAP_LEDGER.md` remain fail-closed: no screenshot `MATCH` without opened original reference plus a real exact-SHA render.
- Superseded Worker CI is not accepted as evidence for a newer worker head.

## Persistent release guards

Retain without relaxation: pypdf packaging; fail-closed Frozen argv; Desktop/Worker two-EXE split; exactly one Desktop instance with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock cluster; duplicate-column, Core-startup and storage-bootstrap regression signatures.

## Promotion state

`PROMOTION_READY=NO`

Next integrator actions, in order:

1. Consume exact-head completion of manual UI canonical `34729288659`; only if all jobs are green may PR `#127` advance from Draft/integration review.
2. Requalify the current Spec/Core head rather than importing its older exact-green predecessor while the same owner files are moving.
3. Wait for an owner-green Backend/Storage successor that closes `ERR-0049`; then re-run/consume exact Backend canonical before integrating schedule-startup.
4. Do not spend worker or integrator cycles on already closed boundary issues `#92/#93/#95/#96` absent a new reproducer.
5. After any integration into Develop, require canonical Quality on the resulting exact Develop SHA before the next Develop mutation.
