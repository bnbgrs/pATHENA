# pATHENA handoff — LM Studio headless runtime bounds

Date: 2026-10-02
Branch: `fix/lmstudio-headless-runtime-bounds-20261002`
Base: `develop/pathena-next@67174198e1494fd4c8678aad60756c39ef5c160b`
Scope owner: runtime/Desktop LM Studio lifecycle only.

## Ausgangslage

The current Develop line already contains the LM Studio runtime controller and app wiring, so old PR #297 must **not** be merged wholesale. The current implementation still had three concrete runtime defects:

1. `ATHENA_LMSTUDIO_BASE_URL=http://[::1]:PORT` passed validation, but automatic server startup hard-coded `--bind 127.0.0.1`, so Core would probe IPv6 loopback while the spawned server listened on IPv4 loopback.
2. Automatic headless startup invoked `lms server start` directly. Current LM Studio headless documentation uses `lms daemon up` to start llmster and documents it as idempotent when already running.
3. `QProcess` CLI operations had no deadline. A hung `lms` command could keep the controller busy indefinitely and block restart/unload/load actions.
4. The controller marked a model as pending before a load command was actually scheduled. Auto-load disabled, missing CLI, timeout, or CLI failure could therefore be followed by a Core refresh that replaced the real error with a false “Core did not confirm ... loaded” state.

## Root Cause

Endpoint validation returned only the port and discarded the validated loopback host identity. The startup sequence therefore rebuilt an IPv4 bind target independently. CLI lifecycle code also lacked an explicit daemon bootstrap and command watchdog. Pending model identity was assigned at selection/intent time rather than at accepted command-dispatch time.

## Änderungen

- Added `_endpoint()` returning validated bind host + port; `localhost` normalizes to `127.0.0.1`, `::1` stays `::1`.
- Kept `_endpoint_port()` as a compatibility helper.
- Added `_server_start_steps()`: `lms daemon up` followed by loopback-bound `lms server start --port ... --bind ...`.
- Restart now stops the server, ensures the daemon, then starts the server.
- Added operation-specific watchdogs:
  - control/daemon/server: 45 s
  - unload: 120 s
  - model load: 600 s
- Timeout kills the owned CLI process, clears queued steps, preserves a truthful timeout status, and refreshes Core.
- Process finish/error paths stop the watchdog.
- Model-load pending state is now established only when a real load command can be dispatched; load failure/error/timeout clears pending identity before Core refresh.
- Added focused pure tests for loopback bind identity, daemon-first headless startup, and bounded timeout policy.

## Dateien

- `src/athena/desktop/lmstudio_runtime.py`
- `tests/unit/test_lmstudio_runtime_qol.py`
- `docs/agent_handoffs/manual-lmstudio-headless-runtime-bounds-20261002.md`

## Verhalten danach

Automatic local runtime startup follows the actual configured loopback address, establishes llmster headlessly before starting the HTTP server, and cannot remain permanently blocked on a single CLI child process. Error/timeout states are no longer converted into a fake post-load confirmation failure.

## Validierung

- Static source re-read completed on the exact branch after mutation.
- Diff against current Develop checked: runtime + focused test files only before this handoff.
- LM Studio CLI contract cross-checked against current official docs for `lms daemon up`, headless llmster and `lms server start --bind`.
- Local clone/test execution was **blocked by DNS resolution in the execution container** (`Could not resolve host: github.com`); no local PASS is claimed.
- GitHub exact-head CI must be the execution authority for this branch.

## Bekannte Restprobleme

- This does not prove a real Windows machine with LM Studio installed can load a specific local model; native runtime acceptance still requires Windows evidence.
- The 600 s model-load deadline is intentionally generous and bounded; if real large-model evidence shows it is too short, adjust from measured behavior rather than removing the deadline.
- Provider-level chat cancellation while synchronous LM Studio transport is blocked is owned by current Chat/Runtime cancellation work and is not touched here.

## Abhängigkeiten / Konfliktrisiko

Active PRs inspected before work:
- #329 Chat cancellation: touches API/chat cancellation files, not this runtime file.
- #327 Qt CI isolation: workflow/quality files only.
- #326 Research UI: `research_workspace.py` only.
- #325 Storage canonical commit bundle: storage + focused tests only.

Old PR #297 is stale/diverged by 224 commits and should remain source material only. Do not merge it wholesale after this slice.

## Nächste sinnvolle Schritte

1. Require exact-head Quality and focused runtime tests to pass.
2. Run native Windows acceptance with LM Studio installed but GUI closed:
   - start pATHENA,
   - verify `lms daemon up`/server startup,
   - select a downloaded model,
   - verify Core reports the selected exact model loaded,
   - send chat and confirm the same backend model ID is used,
   - exercise restart/unload and one forced timeout/error case.
3. If CI exposes formatting/type issues, fix this branch only; do not broaden into Chat cancellation or Storage.

## Commits

- `073310d28770c0b8b229134708ac32a8ac975ab7` — headless lifecycle/bounds
- `4e1fa364562de901344998c6bc77a3e7c88280ff` — focused tests
- `ffa45aa758a87b14fa8806542fcf81a3dad9481d` — truthful pending-state cleanup
