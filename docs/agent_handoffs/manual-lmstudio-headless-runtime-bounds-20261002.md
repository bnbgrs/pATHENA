# pATHENA handoff — LM Studio headless runtime bounds

Date: 2026-10-02
Branch: `fix/lmstudio-headless-runtime-bounds-20261002`
PR: #334
Base: `develop/pathena-next@67174198e1494fd4c8678aad60756c39ef5c160b`
Scope owner: runtime/Desktop LM Studio lifecycle only.

## Ausgangslage

Current Develop already contained the LM Studio runtime controller and desktop wiring, so stale PR #297 was treated as source material only and was **not** merged. Five concrete runtime/lifecycle defects remained:

1. `ATHENA_LMSTUDIO_BASE_URL=http://[::1]:PORT` passed validation, but automatic server startup hard-coded `--bind 127.0.0.1`; Core could probe IPv6 loopback while the spawned server listened on IPv4.
2. Automatic headless startup invoked `lms server start` directly without first establishing the documented llmster daemon with `lms daemon up`.
3. `QProcess` CLI operations had no deadline; one hung `lms` command could keep the runtime controller busy indefinitely.
4. A selected model could be marked pending before a load command was actually validated/dispatched. Disabled auto-load, missing CLI, unsafe Windows wrapper arguments, timeout, or CLI failure could therefore turn into a false later “Core did not confirm ... loaded” state.
5. Desktop shutdown had no explicit cleanup for an in-flight pATHENA-owned `lms` CLI child process.

## Root Cause

Endpoint validation discarded the validated loopback host identity and retained only the port. Headless service startup, command lifetime, and model-load state were handled as loosely related UI intentions rather than one bounded lifecycle. Pending model identity was created before the command boundary instead of being derived from the command that was actually dispatchable. Shutdown relied on QObject/process teardown rather than an explicit owned-child cleanup contract.

## Änderungen

- Added `_endpoint()` returning validated bind host + port:
  - `localhost` normalizes to `127.0.0.1`;
  - `::1` remains `::1`;
  - only loopback HTTP endpoints and valid ports are accepted.
- Kept `_endpoint_port()` as a compatibility helper.
- Added `_server_start_steps()`: idempotent `lms daemon up` followed by `lms server start --port ... --bind ...`.
- Restart now performs server stop → daemon up → server start.
- Added operation-specific CLI watchdogs:
  - daemon/server/control: 45 s
  - unload: 120 s
  - model load: 600 s
- Timeout kills only the owned CLI child, clears queued work and load-confirmation state, reports the timeout truthfully, then refreshes Core.
- Process finish/error paths stop the watchdog.
- Added `_accepted_model_load_id()`; pending model identity is now derived only from a well-formed model-load command after command validation and immediately before `QProcess.start()`.
- Missing CLI, rejected command, non-zero exit, process error and timeout all clear model-load pending state before any later Core refresh can reinterpret the failure.
- Added `LMStudioRuntimeController.dispose()`; desktop quit cancels only pATHENA-owned in-flight CLI work. It deliberately does **not** stop the persistent LM Studio daemon/server.
- Wired `app.aboutToQuit` to runtime disposal.
- Added focused pure regressions for loopback bind identity, daemon-first headless startup, operation deadlines and accepted/dispatched model identity.

## Dateien

- `src/athena/desktop/lmstudio_runtime.py`
- `src/athena/desktop/app.py`
- `tests/unit/test_lmstudio_runtime_qol.py`
- `docs/agent_handoffs/manual-lmstudio-headless-runtime-bounds-20261002.md`

## Verhalten danach

Automatic local runtime startup follows the configured loopback family, establishes llmster before the HTTP server, and cannot remain permanently blocked on one CLI child process. A model is not represented as pending until pATHENA has a valid load command ready to dispatch. CLI rejection/failure/timeout remains visible as the actual failure rather than being overwritten by a fake Core-confirmation failure. Quitting pATHENA cleans up an active owned CLI command without taking down an otherwise useful persistent local model service.

## Validierung

Observed before this final handoff update:

- Branch comparison against current Develop: ahead only, behind 0; no parallel-bot commits were overwritten.
- Full diff re-read after mutations.
- Current official LM Studio CLI/headless contract cross-checked for `lms daemon up`, headless llmster and `lms server start --bind`.
- Previous exact code head `71c06d67943a4785a4d853bf184089cd63b7ed91`:
  - Local install smoke: PASS.
  - Linux storage regressions: PASS.
  - UI Focused Candidate: PASS.
  - Visual capture/harness itself: PASS for all eleven captures, but visual verdict FAIL only on `08-pallas.png` (changed_ratio 0.00843243, mean_delta 0.48803428). Chat/Research/Files/System/Settings were exact or within policy. This branch does not change PALLAS files; do not “fix” PALLAS from this runtime branch.
  - Windows path-safety job on that superseded head was cancelled after subsequent commits; no PASS claimed.
- Local clone/test execution in the assistant container remained blocked by DNS resolution (`Could not resolve host: github.com`); no local PASS is claimed.
- The final handoff commit intentionally triggers fresh exact-head CI. Use PR #334 checks as the authoritative final execution evidence. Post final results as a PR comment rather than mutating this branch again.

## Bekannte Restprobleme

- Native Windows acceptance with an actual LM Studio installation/model is still required; CI does not prove a real downloaded model can load on the user's workstation.
- Provider-level prompt cancellation while LM Studio synchronous transport is blocked belongs to current Chat/Runtime cancellation work (#329) and is not touched here.
- The PALLAS visual delta observed on the superseded runtime head is outside this branch's changed-file set and should be handled by the PALLAS/UI owner only if it reproduces on the relevant canonical candidate.
- The 600 s model-load deadline is intentionally generous but finite. Change it only from measured large-model evidence.

## Abhängigkeiten / Konfliktrisiko

Active work inspected before and during this slice:

- #329 Chat cancellation: API/chat cancellation files; no overlap with this runtime controller.
- #327 Qt CI isolation: workflow/quality files only.
- #326 Research UI: `research_workspace.py` only.
- #325 Storage canonical commit bundle: storage + focused tests only.

Old #297 is stale/diverged by 224 commits and must not be merged wholesale after this slice.

The old Backend queue item BE-021 (ContextPackage temperature overflow) was re-checked on current Develop during this run. Current `generation_temperature()` already catches `OverflowError` and maps it into `ContextPackageError`; the queue evidence is stale, so no duplicate mutation was made.

## Nächste sinnvolle Schritte

1. Read exact-head checks on PR #334. Fix only reproducible runtime/test/type failures attributable to this branch.
2. Native Windows acceptance with LM Studio installed but GUI closed:
   - launch pATHENA;
   - verify daemon/server start without opening LM Studio GUI;
   - select a downloaded model;
   - verify Core reports that exact model loaded;
   - send chat and verify the selected backend model ID is used;
   - exercise restart/unload;
   - exercise one controlled CLI failure/timeout;
   - quit pATHENA during an owned CLI command and verify no orphan CLI child remains while the persistent LM Studio service is not killed.
3. Keep Chat cancellation (#329), PALLAS visual work and Storage work in their existing ownership lanes.

## Commits before this handoff refresh

- `073310d28770c0b8b229134708ac32a8ac975ab7` — harden headless lifecycle and endpoint/command bounds.
- `4e1fa364562de901344998c6bc77a3e7c88280ff` — focused endpoint/start/timeout tests.
- `ffa45aa758a87b14fa8806542fcf81a3dad9481d` — truthful pending-state cleanup.
- `d709d0b7219461004d1c8ee7ccc5f4da6fb9c59a` — remove unreachable guarded fallback.
- `0e51b334fb20550974827aa5e20f62e71f247111` — explicit owned CLI shutdown cleanup.
- `7b0ff571e25ead5b0d51a4eebcbe8af54d3bf75f` — wire runtime disposal to desktop quit.
- `079cb16cfd17edb9236c02cf15e3001b01cd0c62` — clear rejected model-load state.
- `a429157d06ea2a0a0a12617086a8b36cbd2d7bec` — derive pending model identity at dispatch boundary.
- `f5d3fe6912654b30ca99cbd0f0a597fb73e755d1` — regression for dispatched model identity.
