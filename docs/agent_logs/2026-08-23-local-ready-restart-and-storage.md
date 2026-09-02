# Local-ready restart and storage defects — 2026-08-23

Run timestamp: `2026-08-23T02:04:49+02:00`

pATHENA HEAD when this log was assembled: `7f4990808304c9ede5270cef9cfbe5ce7113cb30`

Scope: `bnbgrs/pATHENA`, branch `agent/pathena`. `bnbgrs/ATHENA` was not modified.

## 1. Local smoke could mutate the configured live runtime root

- Affected components: `src/athena/local_smoke.py`, `tests/unit/test_local_smoke_safety.py`
- Reproduction/check: set `ATHENA_LOCAL_ROOT` to an absolute directory and invoke `athena-local-smoke --keep-root <same-directory>` on the pre-fix implementation.
- Relevant pre-fix behavior: `--keep-root` accepted any absolute path and immediately executed `root.mkdir(...)` followed by `run_local_smoke(root)`, which creates a durable chat.
- Root-cause classification: safety boundary / destructive diagnostic target selection.
- Status: `FIXED_PENDING_CI`
- Fix: commit `fb3c0468ffbdd1a3dde8969a356078c57eebc49a` adds `_assert_safe_keep_root()` and refuses the configured live pATHENA runtime root; commit `b1539b4c3da274ecc5bb0a30120c711d8cddead9` adds allow/reject tests.
- Actual verification evidence: remote file inspection confirms the guard and both tests are committed. Full pytest execution was not available in this automation environment.
- Next action: confirm the targeted unit test and full quality gate in CI; on a Windows machine also exercise the CLI against a separate test root.

## 2. Local restart smoke did not prove database/schema health or repeated cleanup

- Affected components: `src/athena/local_smoke.py`, `tests/integration/test_local_smoke.py`, `scripts/check_windows.ps1`
- Reproduction/check: inspect the pre-fix `run_local_smoke()` implementation; it created one chat, performed one restart, and checked only that the chat could be listed/loaded.
- Relevant pre-fix behavior: no post-shutdown database preflight, no explicit schema-version assertion, no check for stale `core-api.json` / `core-api.token`, and only one restart cycle.
- Root-cause classification: local-readiness coverage gap / restart diagnostics.
- Status: `FIXED_PENDING_CI`
- Fix: commits `1f7272192ff46d2f205222c26c2209f295a8cbff` and `dc2e671f7d84aa622b9320f5d64294594fee397c` verify the canonical SQLite file read-only at the current `SCHEMA_VERSION`; commits `e8c79db60af611dfd2122fd6264b6831c8be8f8d` and `ef078f96aa5dc252a983d8923f5b4d5fab419c94` require Core API discovery/token cleanup; commits `906803eec7be42fc76be0760e72fac793d0caba7` and `9e25a2d89d3a5455615b3d97d15c07277c01f76f` add repeated restart cycles and integration coverage. `check_windows.ps1` exposes the cycle count in `631c572917cd43b91757fc6952dbf230897a1363`.
- Actual verification evidence: remote inspection confirms the assertions and integration test are committed. No local Core/API execution was possible because the automation runtime could not clone the repository.
- Next action: run `uv run --locked --extra desktop pytest tests/integration/test_local_smoke.py` and then `scripts/check_windows.ps1 -RestartCycles 3` on Windows.

## 3. Doctor reported configured optional storage roots as PASS without proving write access

- Affected components: `src/athena/doctor.py`, `tests/unit/test_doctor_storage_roots.py`
- Reproduction/check: configure an archive/backup/projection directory that exists but rejects writes; the pre-fix `_check_optional_storage_root()` returned `PASS` solely from `root.is_dir()`.
- Exact relevant pre-fix excerpt: `return DoctorCheck(name, "PASS", str(root))`
- Root-cause classification: diagnostic false positive / storage capability check.
- Status: `FIXED_PENDING_CI`
- Fix: commit `9ab870e293b9d83e4a4891b7c66080b491da7d6a` performs a create/write/flush/delete temporary-file probe for each configured optional root and reports `WARN` if it fails; `4c89ebfa0ac0d65c8bb72ec2d1446901365f6407` covers success and simulated access denial.
- Actual verification evidence: source and unit tests are committed and were re-read from `agent/pathena`. Python test execution was not available locally in this automation runtime.
- Next action: CI targeted tests plus one real Windows check against a deliberately read-only test directory.

## 4. Windows runtime root could be placed inside the Git repository

- Affected components: `scripts/windows_common.ps1`, `scripts/bootstrap_windows.ps1`, `scripts/check_windows.ps1`, `scripts/start_windows.ps1`, `tests/unit/test_windows_runtime_root_contract.py`
- Reproduction/check: pre-fix, pass `-LocalRoot <repository>` or set `ATHENA_LOCAL_ROOT` to a repository subdirectory. `Assert-PathenaLocalRootReady` created and write-probed that path without checking repository containment.
- Relevant risk: subsequent runtime initialization can create `state/athena.db`, `state/spool`, `derived`, `logs`, and `tmp` in the source tree, making durable user state vulnerable to Git cleanup/commit mistakes.
- Root-cause classification: Windows path-safety boundary / data-source separation.
- Status: `FIXED_PENDING_CI`
- Fix: `849d90ea7fc7c04dbb306297375c488bb8258f9e` adds `Assert-PathenaRuntimeRootOutsideRepository`; `7c3fa84612e6a4441072d473c9808b9278459eb7`, `fddd0a7423db184b8fdd759c5b49f52de7e65152`, and `2b6faa6928e81482194d0abde555b709d71c2b61` wire the fence into bootstrap/check/start before runtime creation; `11d328420020f02c858180f76ef71719941d7fa6` enforces the static contract.
- Actual verification evidence: all four remote files were re-read after mutation and contain the common `-RepoRoot` fence. PowerShell execution is `NOT EXECUTABLE` in the current non-Windows runtime.
- Next action: execute the three scripts on Windows with both a repository-contained path (expected reject) and a sibling/AppData path (expected accept).

## 5. Automation runtime cannot clone pATHENA for local test execution

- Affected components: automation execution environment only; repository code is not the cause.
- Reproduction/check command: `git clone --depth 1 --branch agent/pathena https://github.com/bnbgrs/pATHENA.git /tmp/pathena`
- Exact relevant error excerpt: `fatal: unable to access 'https://github.com/bnbgrs/pATHENA.git/': Could not resolve host: github.com`
- Root-cause classification: environment/network DNS blocker.
- Status: `BLOCKED`
- Fix/mitigation: repository reads/writes continue through the authenticated GitHub connector; tests are added and CI is inspected instead of claiming unobserved local execution.
- Actual verification evidence: the clone command exited with status `128` and the exact DNS error above.
- Next action: do not treat this as a pATHENA defect. Use GitHub Actions and a real Windows workstation for executable verification until the automation runtime has outbound GitHub DNS/network access.

## 6. Disposable smoke roots made failed Windows restart diagnosis ephemeral

- Affected components: `scripts/check_windows.ps1`, `tests/unit/test_windows_runtime_root_contract.py`
- Reproduction/check: pre-fix `check_windows.ps1` always invoked `athena-local-smoke` without `--keep-root`; its temporary directory was therefore removed when the process exited, including after many classes of failure.
- Root-cause classification: diagnostics / reproducibility gap.
- Status: `FIXED_PENDING_CI`
- Fix: `0cbf585843214697df7b46ed22dfe08910f76b5d` adds `-SmokeRoot` and forwards it as an absolute `--keep-root`; `a7a4b31d16b5739783c47e716fa044cb459f9592` enforces the static contract.
- Actual verification evidence: remote source inspection confirms the argument is resolved and forwarded. Windows execution remains `NOT EXECUTABLE` here.
- Next action: on Windows run `scripts/check_windows.ps1 -SmokeRoot D:\pATHENA-smoke -RestartCycles 3` and retain that directory if a restart/migration fault occurs.
