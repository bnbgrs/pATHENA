# System Recovery truthfulness current-Develop handoff — 2026-10-02

## Base
- develop/pathena-next at branch creation: `d80e92954005c7497697186cb945f96dd56017d4`
- That Develop includes merged #342 Chat branching.
- Branch: `fix/system-recovery-truth-current-20261002-sol`

## Purpose
Fresh current-Develop port of the narrow safety contract previously qualified in PR #373. Do not merge the stale #373 branch wholesale.

## Product change
`src/athena/desktop/system_recovery.py`
- require non-empty `canonical_database`;
- require boolean `canonical_integrity_confirmed`;
- require boolean `normal_core_start_allowed`;
- bind status to Recovery CLI exit code: healthy=0, degraded-derived=3, recovery-required=4;
- reject status/exit-code contradictions;
- reject healthy/degraded claims unless canonical DB is healthy, integrity is confirmed, and normal start is allowed;
- reject recovery-required while normal Core start is allowed;
- pass the real QProcess exit code into payload projection.

## Tests
`tests/unit/test_system_recovery.py`
- update existing fixtures with canonical integrity truth;
- reject contradictory start/integrity/database combinations;
- assert status/exit-code binding.

## Commits
- `9eb439c9cfc5cf1a63ba575f5ecad9cfeda747ae` product
- `be1e29df5fbe823a8e41c3fb56cd603ab6d5d251` tests

## Scope proof
At handoff time the branch is exactly 2 commits ahead / 0 behind its creation base and changes only:
- `src/athena/desktop/system_recovery.py`
- `tests/unit/test_system_recovery.py`

## Prior evidence
Old PR #373 had ATHENA Quality PASS + UI Focused PASS. Its Visual failure was unrelated baseline/PALLAS drift. This fresh branch still requires its own exact-head validation before integration.

## Next
Open a non-draft PR only after one of the currently running full Quality slots (#327/#368/#399/#401) finishes. Then run exact-head Quality + UI Focused; visual only as required by current workflow. Supervisor owns final merge.
