# pATHENA handoff — LM Studio runtime race follow-up

Date: 2026-10-02
Branch: `fix/lmstudio-runtime-race-followup-20261002-sol`
Stacked base: `fix/lmstudio-headless-runtime-bounds-20261002@7b0ff571e25ead5b0d51a4eebcbe8af54d3bf75f`
Parent PR: #334
Status: IMPLEMENTED_PENDING_VERIFY

## Ausgangslage

PR #334 already owns the current-Develop LM Studio headless lifecycle work. This follow-up was created only after #334 appeared during a parallel run and was reviewed to avoid maintaining two competing implementations. It does not replace #334 and must not be merged before its parent.

Three residual defects remained in the exact #334 head:

1. `ensure_selected_model()` assigned `_pending_model_id` before `lms load` completed. A Core snapshot arriving while the CLI process was still running could therefore enter confirmation with a zero budget and emit a false "Core did not confirm ... loaded" failure.
2. Restart queues `server stop -> daemon up -> server start`, but any non-zero `server stop` result cleared the queue. Restart therefore could not recover the common "server is already stopped" state.
3. `QSettings.value(..., type=int)` could coerce a malformed persisted bool into integer `1` before runtime validation.

## Root Cause

Pending model identity was owned by selection/intent rather than by the exact successfully completed load command. Restart treated its recovery-oriented stop phase as a mandatory success. Persisted idle-TTL validation occurred after Qt type coercion rather than at the raw settings boundary.

## Änderungen

- Pending model identity is no longer set before dispatch/completion.
- Added `_accepted_model_load_id()`; successful `model_load` completion derives the exact model identity from the completed command before opening the bounded Core-confirmation window.
- Invalid/malformed completed load-command state fails closed.
- Added `_continue_after_failed_step()`; only a failed `server_stop` with remaining queued restart steps is tolerated, allowing daemon-up/server-start recovery. Other command failures still abort.
- Idle TTL is read raw from QSettings before coercion.
- Added `_coerce_idle_minutes()` accepting genuine ints and canonical signed decimal strings, rejecting bool/other types to the safe default, then clamping 0..1440.
- Added focused regression tests for all three boundaries.

## Dateien

- `src/athena/desktop/lmstudio_runtime.py`
- `tests/unit/test_lmstudio_runtime_qol.py`
- this handoff file

Parent #334 files such as `src/athena/desktop/app.py` and its shutdown `dispose()` wiring are preserved unchanged.

## Verhalten danach

A model is considered pending only after its exact `lms load` command returns success. Core refreshes during a still-running load cannot consume a confirmation budget that does not yet exist. Restart can recover an already-stopped server. Malformed bool persistence cannot silently become a one-minute idle unload.

## Validierung

- Exact stacked-base diff was reviewed before mutation.
- The follow-up is intentionally limited to the two Runtime source/test files before this handoff.
- Local execution remains unavailable in this environment because the container cannot resolve github.com; no local PASS is claimed.
- Exact-head GitHub Actions are required before readiness.
- Real Windows + installed LM Studio acceptance remains required for full runtime verification.

## Abhängigkeiten / Konfliktrisiko

- Parent #334 is authoritative for daemon bootstrap, endpoint bind identity, operation-specific watchdogs, shutdown disposal, and the main runtime handoff.
- Do not merge this follow-up directly to Develop without #334.
- Do not independently reimplement these residual fixes on #334 while this stacked candidate is active; either consume the commits or supersede them explicitly.
- Chat cancellation (#329/#335/#337), Sources (#336), Settings News (#333), Update (#332), Storage (#325), Research UI and Qt CI remain outside this slice.

## Nächste sinnvolle Schritte

1. Run exact-head Quality/focused gates on the stacked candidate.
2. If green, parent owner/Integrator should consume this small delta into #334 (or merge stack in order).
3. On a real Windows machine with LM Studio installed and GUI closed, verify:
   - headless daemon/server startup,
   - exact selected-model load,
   - no premature confirmation while load is still running,
   - restart when server is already stopped,
   - unload/restart/shutdown cleanup,
   - chat uses the exact Core-reported selected backend model.
4. Only after native evidence mark the runtime E2E fully verified.

## Commits

- `25f727d10b827c9dd841cd044a79a631e90736e7` — residual load/restart race fix
- `130e82188f60e617de4464758b0009124a1baa87` — focused race tests
- `9e8a8765457123dcb99e530dee7a5e8fccb3c960` — validate raw persisted TTL before Qt coercion
- `ee864a7a7859812d50595d638157c5985cce31f9` — raw TTL regression coverage
