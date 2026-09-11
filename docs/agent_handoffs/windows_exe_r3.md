# Windows EXE R3 packaging handoff

Status: `PACKAGING_VALIDATION_IN_PROGRESS`

## Why this exists

Real-machine testing of packaging-only R2 exposed a severe frozen-runtime failure: the pATHENA test EXE opened/relaunched repeatedly, emitted many errors, and could drive the machine toward resource exhaustion. R1 had already exposed a separate missing `pypdf` distribution-metadata failure.

Do not use or integrate artifacts from packaging PRs #73 or #74. They are superseded by this R3 validation line.

## Product baseline

- Product source: `develop/pathena-next@d14aca9504021bdacadb89dc478ca41545ab4316`
- `main` untouched.
- No pATHENA product source file is changed on this branch.

## Root packaging hazard

The frozen executable is intentionally reused for child roles. Product launchers use:

- Core: `pATHENA.exe -m athena.api.process`
- Scheduler supervisor: `pATHENA.exe -m athena job scheduler-run ... --lane supervisor`
- Scheduler supervisor then spawns control/provider lanes through `sys.executable -m athena job scheduler-run ...`.

R2's packaging entry point had a dangerous default: any argv not matching the two known `-m` prefixes fell through to `desktop_main`. Any unexpected frozen child invocation could therefore become another GUI process and recursively create its own Core/Scheduler tree.

## R3 containment

Packaging-only `scripts/pathena_frozen_entry.py` now:

1. permits desktop startup only when argv is empty;
2. explicitly routes `-m athena.api.process` to Core;
3. explicitly routes `-m athena` to CLI/Scheduler roles;
4. fails closed with exit 64 for all other argv;
5. uses a Windows named mutex so only one real desktop can exist;
6. retains `multiprocessing.freeze_support()` before dispatch;
7. emits per-process role traces when `ATHENA_FROZEN_TRACE_DIR` is set;
8. writes fatal frozen-startup tracebacks to the runtime log directory;
9. keeps the R2 `pypdf` distribution-metadata correction.

## Required validation before user distribution

`.github/workflows/windows-test-exe-r3.yml` must be fully green. It builds a one-file Windows executable and then launches the actual desktop from a clean environment with an isolated `ATHENA_LOCAL_ROOT`.

The test requires exactly one logical invocation of each role:

- desktop
- Core
- scheduler supervisor
- scheduler control
- scheduler provider

It then samples OS process count twice and rejects growth or an excessive one-file process count. A second desktop launch must be blocked by the singleton. Unknown argv must exit 64 without leaving any pATHENA process alive.

If this full-tree test is not green, do not provide the EXE to the user and do not weaken the assertions.

## Collision guidance

Active Backend/Core/UI/Error bots should not touch these packaging-only files. Conversely this packaging branch must not modify their product files or central progress ledgers. Any product defect discovered by the full-tree test should be handed to the owning worker rather than patched broadly here unless it is strictly required for a safe disposable test build.
