# System Recovery protocol-truth handoff — 2026-10-02

## Ausgangslage

Base: develop/pathena-next@467ef434236c320e4afe9d21a39c20a4a2b75728.

The SYSTEM workspace exposes a read-only Recovery diagnostic panel that runs:

python -m athena.recovery_cli diagnose

The Core recovery contract is explicit:

- healthy -> exit 0 -> canonical integrity confirmed -> normal Core start allowed
- degraded-derived -> exit 3 -> canonical integrity confirmed -> normal Core start allowed
- recovery-required -> exit 4 -> normal Core start blocked

Before this slice the desktop checked that normal_core_start_allowed was a boolean, but did not check whether its value agreed with status. It also accepted any process exit code if the last output line could be projected.

Concrete false-success examples before the change:

- status=healthy + normal_core_start_allowed=false was still rendered as HEALTHY with "normal Core start allowed";
- status=recovery-required + normal_core_start_allowed=true was still rendered as RECOVERY REQUIRED while the payload simultaneously claimed normal start was allowed;
- status=healthy emitted with exit 4 could still render HEALTHY;
- missing canonical_database degraded to the string "unknown" instead of failing the diagnostic trust boundary.

## Root Cause

The desktop treated the Recovery JSON as presentation data rather than as one coherent protocol receipt. Fields whose values are semantically coupled in RecoveryDiagnosticReport were projected independently, and the CLI exit-code/status contract was not checked.

## Änderungen

### src/athena/desktop/system_recovery.py

project_recovery_payload now:

- requires a non-empty canonical_database;
- requires canonical_integrity_confirmed to be a real bool;
- still requires normal_core_start_allowed to be a real bool;
- validates the canonical Recovery exit-code contract when called from a process completion:
  - healthy = 0
  - degraded-derived = 3
  - recovery-required = 4
- rejects healthy/degraded-derived if:
  - canonical_database is not healthy,
  - canonical integrity is not confirmed,
  - or normal Core start is not allowed;
- rejects recovery-required when normal Core start is simultaneously claimed as allowed.

SystemRecoveryPanel now passes the real QProcess exit code into the Recovery payload validator.

The separate QProcess errorOccurred -> finished terminal-race repair is owned by active PR #367 and is intentionally not duplicated in this branch.

No restore/repair action was added. The panel remains read-only.

### tests/unit/test_system_recovery.py

Regression coverage added for:

- contradictory healthy/start-safe fields;
- contradictory degraded canonical-integrity fields;
- recovery-required incorrectly allowing normal Core start;
- missing canonical database identity;
- exact status-to-exit-code binding 0/3/4.

Existing healthy/degraded/recovery-required fixture payloads were updated to include the canonical_integrity_confirmed field that the real RecoveryDiagnosticReport always emits.

## Verhalten danach

The Recovery panel can no longer show HEALTHY or REBUILD NEEDED from a self-contradictory diagnostic payload. A machine-readable Recovery result is trusted only when the status, canonical safety fields, normal-start decision and CLI exit code agree with the Core Recovery contract.

## Dateien

- src/athena/desktop/system_recovery.py
- tests/unit/test_system_recovery.py
- this handoff

## Validierung

Completed:

- active PR file ownership checked immediately before implementation: no open PR touched system_recovery.py or test_system_recovery.py;
- Core RecoveryDiagnosticReport and recovery_cli were inspected first to derive the invariant from real code rather than inventing UI rules;
- branch was created from the then-current develop/pathena-next@467ef434236c320e4afe9d21a39c20a4a2b75728;
- written source and tests were re-read after modification.

Not locally executable in this runtime:

- the execution container still cannot resolve github.com for a local checkout;
- no local pytest/Qt PASS is claimed.

Required exact-head validation:

1. pytest tests/unit/test_system_recovery.py
2. canonical Ruff/format/type checks
3. ATHENA Quality Gate
4. UI Focused / visual checks if attached to the PR

## Parallel work / conflict risk

No active branch overlapped these files at initial implementation time. During the same run, PR #367 appeared and took ownership of System helper terminal-signal races in system_recovery.py and system_hardware_acceptance.py.

After inspecting #367, this branch explicitly removed its duplicate errorOccurred -> finished handling and duplicate test. #373 now owns only Recovery protocol/status truth. Preserve #367's terminal-race work when integrating the two slices.

Do not fold Windows packaging/helper-routing work from #360 into this branch. The Recovery panel launch-routing behavior is a separate packaging concern and was intentionally left untouched.

Do not expand this slice into Backup restore behavior; active backup/security work is separate.

## Nächste sinnvolle Schritte

1. Qualify the exact PR head through focused System Recovery tests and canonical Quality.
2. If CI finds a branch-owned issue, fix it on this branch.
3. Integrate or otherwise preserve #367's helper-terminal-race change; do not re-add that duplicate fix here.
4. If develop/pathena-next moves again before integration, compare the new base and update only if necessary; do not overwrite parallel work.
5. After integration, keep Recovery UI read-only unless an explicit, separately specified restore workflow is approved.

## Commit / Branch

Branch: fix/system-recovery-protocol-truth-20261002-sol

Implementation commits before this handoff:

- cbf5440c816d90ada49d56e60e4bf890988cfb44 — fail closed on contradictory Recovery diagnostics
- f8e525d41bd6a76806838286db61dd484d976572 — Recovery protocol contradiction/process-race tests
- 96fc920dae876e8ad6e0e1cbfbb3e4395c75d93a — regression-file formatting cleanup
- 81759decb99a71816292f000ee1e5366b5445d27 — remove duplicate helper-terminal race owned by #367
- cab9945a52a1ccd9864548a60af64dac2140d1a9 — remove duplicate terminal-race test owned by #367
