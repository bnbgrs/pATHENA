# System helper terminal ownership — 2026-10-02

## Ausgangslage

The SYSTEM workspace owns several short-lived QProcess helpers. This slice covers the
three panels that had independent error/finish terminal handlers:

- Hardware Acceptance: `athena.hardware_acceptance`
- Recovery diagnosis: `athena.recovery_cli diagnose`
- Backup operations: canonical `athena backup ...` CLI

Both panels connect `errorOccurred` and `finished` to independent terminal handlers.

## Root Cause

A helper process can report a specific QProcess error and then still deliver a terminal
`finished` notification for the same run. Before this slice, the first handler rendered
the useful crash/start error, while the later finished handler independently attempted to
load a report or parse stdout. That second path could overwrite the original diagnosis
with generic "no diagnostic output", JSON, or report-loading failure text.

Recovery enabled its Run button directly from `errorOccurred` without checking whether
the QProcess was already terminal. Backup similarly cleared operation ownership and
re-enabled all controls immediately from `errorOccurred`, allowing a still-running process
to lose its owner state.

This is a terminal-state ownership bug, not a rendering problem.

A second Backup-specific integrity bug was found in the same review: exit code 0 was
treated as a verified list refresh even when one or more output rows did not match the
canonical backup CLI framing. Malformed rows were silently skipped, so protocol drift
could appear as an empty or partial successful backup list.

## Änderungen

- Track whether the current helper run has already emitted a QProcess error.
- Reset that marker only when starting a new run or consuming the matching late
  `finished` callback.
- If `finished` follows a process error, preserve the already-rendered specific failure
  instead of parsing/overwriting it.
- Re-enable the action from `errorOccurred` only when QProcess is already NotRunning.
- Normalize the post-error action label to `Run again`.
- Apply the same ownership rule to Backup; do not clear its operation identity or re-enable
  controls from an error signal until QProcess is terminal.
- Add focused regressions that explicitly execute error -> finished ordering for Hardware
  Acceptance, Recovery and Backup and assert the original detail survives.
- Parse successful Backup list output as one strict canonical record stream; any malformed
  non-empty row fails the refresh instead of being skipped.
- Preserve the previously rendered snapshot list when a successful process returns invalid
  framing, while surfacing diagnostic output when no snapshot detail is selected.

## Dateien

- `src/athena/desktop/system_hardware_acceptance.py`
- `src/athena/desktop/system_recovery.py`
- `src/athena/desktop/system_backup.py`
- `tests/unit/test_pathena_system_hardware_acceptance.py`
- `tests/unit/test_system_recovery.py`
- `tests/unit/test_desktop_system_backup.py`

## Parallelität / Konfliktrisiko

Fresh branch reconstructed from
`develop/pathena-next@467ef434236c320e4afe9d21a39c20a4a2b75728`.

The original four Hardware/Recovery product/test files were byte-identical between the
earlier inspected Develop SHA and this fresh base. Backup was added only after confirming
that no current open PR owned `system_backup.py`. No current Chat, Sources, Jobs, Research, Knowledge, Storage, LM Studio,
Packaging, or PALLAS agent file is touched.

## Validierung

Focused regressions are included for all three process-error races plus malformed Backup
list framing/preservation. Exact-head GitHub Quality/UI checks are required before integration. No local native Qt execution is claimed from this chat runtime.

## Nächste Schritte

1. Require exact-head Quality to execute both focused System tests.
2. If any Qt signal-order test fails, fix the terminal ownership on this branch; do not
   weaken the assertion.
3. Recheck fresh Develop drift before integration.
4. After merge, exercise both SYSTEM actions in the packaged Windows candidate so process
   startup failures preserve actionable diagnostics.

## Branch

`fix/system-helper-terminal-race-20261002-sol-v2`
