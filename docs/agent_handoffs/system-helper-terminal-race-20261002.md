# System helper terminal ownership — 2026-10-02

## Ausgangslage

The SYSTEM workspace owns two short-lived QProcess helpers:

- Hardware Acceptance: `athena.hardware_acceptance`
- Recovery diagnosis: `athena.recovery_cli diagnose`

Both panels connect `errorOccurred` and `finished` to independent terminal handlers.

## Root Cause

A helper process can report a specific QProcess error and then still deliver a terminal
`finished` notification for the same run. Before this slice, the first handler rendered
the useful crash/start error, while the later finished handler independently attempted to
load a report or parse stdout. That second path could overwrite the original diagnosis
with generic "no diagnostic output", JSON, or report-loading failure text.

Recovery also enabled its Run button directly from `errorOccurred` without checking
whether the QProcess was already terminal.

This is a terminal-state ownership bug, not a rendering problem.

## Änderungen

- Track whether the current helper run has already emitted a QProcess error.
- Reset that marker only when starting a new run or consuming the matching late
  `finished` callback.
- If `finished` follows a process error, preserve the already-rendered specific failure
  instead of parsing/overwriting it.
- Re-enable the action from `errorOccurred` only when QProcess is already NotRunning.
- Normalize the post-error action label to `Run again`.
- Add focused regressions that explicitly execute error -> finished ordering for both
  Hardware Acceptance and Recovery and assert the original detail survives.

## Dateien

- `src/athena/desktop/system_hardware_acceptance.py`
- `src/athena/desktop/system_recovery.py`
- `tests/unit/test_pathena_system_hardware_acceptance.py`
- `tests/unit/test_system_recovery.py`

## Parallelität / Konfliktrisiko

Fresh branch reconstructed from
`develop/pathena-next@467ef434236c320e4afe9d21a39c20a4a2b75728`.

The four touched files were byte-identical between the earlier inspected Develop SHA and
this fresh base. No current Chat, Sources, Jobs, Research, Knowledge, Storage, LM Studio,
Packaging, or PALLAS agent file is touched.

## Validierung

Focused regressions are included in the candidate. Exact-head GitHub Quality/UI checks are
required before integration. No local native Qt execution is claimed from this chat runtime.

## Nächste Schritte

1. Require exact-head Quality to execute both focused System tests.
2. If any Qt signal-order test fails, fix the terminal ownership on this branch; do not
   weaken the assertion.
3. Recheck fresh Develop drift before integration.
4. After merge, exercise both SYSTEM actions in the packaged Windows candidate so process
   startup failures preserve actionable diagnostics.

## Branch

`fix/system-helper-terminal-race-20261002-sol-v2`
