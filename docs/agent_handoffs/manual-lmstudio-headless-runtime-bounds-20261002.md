# pATHENA handoff — LM Studio headless runtime bounds

Date: 2026-10-02
Branch: `fix/lmstudio-headless-runtime-bounds-20261002`
PR: #334
Base at branch creation: `develop/pathena-next@67174198e1494fd4c8678aad60756c39ef5c160b`
Scope owner: Desktop LM Studio lifecycle/runtime only.

## Ausgangslage

Current Develop already contained the LM Studio runtime controller and desktop wiring, so stale PR #297 was used only as historical source material and was not merged.

The current runtime still had concrete lifecycle/state defects:

1. IPv6 loopback endpoints were accepted, but automatic server startup always rebound LM Studio to IPv4 `127.0.0.1`.
2. Headless startup did not establish llmster with `lms daemon up` before starting the HTTP server.
3. CLI child processes had no deadline and could leave the runtime permanently busy.
4. Model-load pending/confirmation state could exist before a successful `lms load`, so unrelated Core refreshes could report a false confirmation failure.
5. Restart aborted if `server stop` returned non-zero even when the server was simply already stopped.
6. Qt `QSettings` integer coercion could turn a malformed persisted bool into an idle TTL of one minute.
7. Core snapshots received during active load/unload/restart work could overwrite the truthful CLI status with stale `available`/`loaded` UI text.
8. Desktop shutdown did not explicitly clean up a pATHENA-owned in-flight `lms` CLI child.

## Root Cause

Endpoint validation discarded loopback-family identity. Runtime intent, CLI process lifetime and Core-confirmed state were not separated tightly enough: pending identity was created before the successful command boundary, restart treated its stop phase as mandatory success, persisted values were coerced before validation, and snapshot presentation was allowed to overwrite an active operation.

## Änderungen

- Added `_endpoint()` returning the validated loopback bind host and port:
  - `localhost` -> `127.0.0.1`;
  - `::1` remains `::1`.
- Added daemon-first `_server_start_steps()`: `lms daemon up` then loopback-bound `lms server start`.
- Restart performs stop -> daemon up -> start and may continue after a failed `server_stop` when recovery steps remain.
- Added operation deadlines:
  - daemon/server/control: 45 s;
  - unload: 120 s;
  - model load: 600 s.
- Timeout kills only the owned CLI child, clears queued/confirmation state, reports the timeout, then asks Core for fresh truth.
- Model pending identity is now established only after the exact `model_load` command exits successfully; only then does the bounded Core-confirmation window open.
- Rejected command, non-zero load exit, process error and timeout clear load state before later Core refreshes.
- Raw idle TTL is validated by `_coerce_idle_minutes()`; bool and malformed types fall back to the safe default instead of Qt coercion.
- While any CLI sequence is busy, Core snapshots update cached truth but do not replace the operation-owned visible status.
- Added idempotent `LMStudioRuntimeController.dispose()`; desktop quit cancels only pATHENA-owned CLI work and deliberately leaves the persistent LM Studio daemon/server alone.
- Wired `app.aboutToQuit` to runtime disposal.

## Regression coverage

`tests/unit/test_lmstudio_runtime_qol.py` now covers:

- IPv4/localhost/IPv6 bind identity;
- daemon-before-server startup;
- bounded per-operation timeouts;
- load identity from a well-formed completed command;
- safe idle-TTL coercion;
- restart continuation only for the stop phase;
- a real Qt `PathenaMainWindow` + `LMStudioRuntimeController` regression proving a Core snapshot does not overwrite an active CLI status.

## Dateien

- `src/athena/desktop/lmstudio_runtime.py`
- `src/athena/desktop/app.py`
- `tests/unit/test_lmstudio_runtime_qol.py`
- this handoff

## Parallel-work coordination

The run continuously re-synchronized active PRs.

- #331 independently started on the same runtime area after #334 existed. It was subsequently closed rather than kept as a competing integration candidate.
- Bot branch `fix/lmstudio-runtime-race-followup-20261002-sol` explicitly stacked on #334 and documented three residual defects: premature pending identity, restart-on-already-stopped-server, and raw TTL validation. Its handoff instructed the parent owner to consume the delta rather than reimplement it independently. Those deltas were consumed into #334.
- #346 owns LM Studio provider/model-identity validation only (`src/athena/model/adapters/lm_studio.py` + provider tests); it is file-disjoint and compatible.
- #333 owns Settings/News persistence/hydration only; it does not own the runtime preferred-model key.
- Chat cancellation (#329/#335/#337), Storage, Sources, Windows packaging and helper-lifecycle PRs remain outside this slice.
- Product PALLAS PR #302 is untouched.
- PALLAS visual-harness determinism is isolated in separate QA PR #352; no product PALLAS file is changed there either.

Do not revive or merge stale #297/#331 on top of this branch. Do not separately reapply the consumed runtime-race follow-up.

## Validation observed during this run

Because the assistant execution container cannot resolve `github.com`, local clone/pytest execution was unavailable. No local PASS is claimed.

Real GitHub Actions evidence from superseded exact heads:

- Local install smoke: PASS.
- Linux storage regressions: PASS.
- UI Focused Candidate: PASS.
- A later exact runtime head completed Windows path safety: PASS.
- Eleven-surface Windows capture itself completed successfully on the superseded runtime head. Its verdict failed only on `08-pallas.png`; Chat, Research, Files, System and Settings were exact or inside policy. That PALLAS-only nondeterminism was independently root-caused and isolated into QA PR #352 rather than patched in this runtime branch.

The branch has changed since those runs. Final authority is the fresh exact-head CI for PR #334 after this handoff commit. Do not treat superseded-head green jobs as final approval.

## Verhalten danach

pATHENA can use the configured loopback family, bootstrap LM Studio headlessly, recover restart when the server is already stopped, bound hung CLI work, preserve truthful in-flight status, and only claim a model-load confirmation after the load command actually completed. Shutdown does not leave pATHENA-owned CLI work hanging and does not kill the persistent model service.

## Bekannte Restprobleme

- Native Windows acceptance with a real installed LM Studio and a downloaded model is still required. CI cannot prove the user's actual installation/model/GPU path.
- Provider-level prompt cancellation belongs to the active Chat cancellation control-plane work and is intentionally not duplicated here.
- A 600 s model-load deadline is deliberately generous but finite; change it only from measured large-model evidence.
- Final merge/readiness depends on exact-head Quality plus relevant Windows evidence.

## Nächste sinnvolle Schritte

1. Require exact-head PR #334 Quality/focused checks and inspect any failure at the failing step/log rather than weakening gates.
2. Native Windows acceptance with LM Studio GUI closed:
   - launch pATHENA;
   - verify daemon/server starts headlessly;
   - select a downloaded model;
   - verify Core reports that exact model loaded;
   - send Chat and verify the exact selected backend model ID is used;
   - restart when the server is already stopped;
   - exercise unload and one controlled CLI failure/timeout;
   - quit during owned CLI work and verify no orphan CLI child remains while llmster/server remain available.
3. Integrator should keep #346 provider identity validation adjacent but independent.

## Key commits

- `073310d28770c0b8b229134708ac32a8ac975ab7` — daemon/bind/deadline runtime hardening.
- `4e1fa364562de901344998c6bc77a3e7c88280ff` — initial focused tests.
- `0e51b334fb20550974827aa5e20f62e71f247111` / `7b0ff571e25ead5b0d51a4eebcbe8af54d3bf75f` — owned CLI shutdown cleanup + app wiring.
- `8c90549d9b5cb159a348f4517ff619b57eb496f1` — consume stacked runtime race follow-up.
- `4dbe0ede1ac0628685f6f6f86a5c89f1c862d977` — race/TTL/restart regressions.
- `4fa3ecb132828d4a1a7895cf7a179c7611b62f66` — preserve active CLI status across snapshots.
- `234d0e103f1f34c1960358de2458ee9f2fa32a64` — real Qt regression for active CLI status.
