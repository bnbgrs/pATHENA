# Independent hardware-acceptance boundaries handoff — 2026-08-26

## Integration status

- **INTEGRATED** into `bot/pathena-candidate`.
- Candidate merge: `b95c00d23d0a4cd4e417218beebc3c1287df177e`.
- Pull request: `#23` (merged).
- Final PR head: `f8a91660d0ac482dbf72cc220781191b13dca194`.
- Isolated branch: `manual/independent-boundaries-20260826b`.
- Frozen base: `6bbf6232288e4e634b1d4c3c058195ec62db4cb2`.
- Detailed candidate log: `docs/agent_logs/2026-08-26-independent-hardware-boundaries-run.md`.

## Completed work

### IHB-001 — exact local inference marker

`src/athena/hardware_acceptance.py::_run_live_inference()` now enforces the prompt's actual acceptance contract. After incidental outer whitespace is stripped, the response must equal `PATHENA_LOCAL_INFERENCE_OK`; merely containing the marker is no longer enough.

Regression coverage proves:

- `prefix PATHENA_LOCAL_INFERENCE_OK suffix` fails;
- surrounding whitespace/newline around the exact marker remains accepted.

### IHB-002 — strict Windows controller evidence

`_video_controller_names_from_payload()` no longer silently discards malformed members of the `names` list. Every controller entry must be a non-empty string; mixed-type or blank entries fail closed with `HardwareAcceptanceError`.

The final implementation validates in an explicit loop and appends only narrowed `str` values, preserving strict-mypy type stability.

Regression coverage proves:

- a mixed string/integer names list fails;
- a blank controller name fails.

## CI evidence and supersession

PR #23 produced multiple workflow heads while the slice was corrected.

- Run **#3147** / head `db9918db4204d5ddee2bb172682f6143f020ba58`: superseded. Local install smoke PASS, Linux storage lane PASS, Windows path-safety lane PASS. Ruff failed on a slice-owned overlong diagnostic line; that line was corrected afterward. mypy also reported failure on this superseded head; do not attribute or promote it without canonical diagnostics because the head changed again.
- Run **#3148** / head `7760a85e041fd2597c15881f42cf449368ea912e`: superseded before becoming authoritative.
- Run **#3149** / final PR head `f8a91660d0ac482dbf72cc220781191b13dca194`: **authoritative pending follow-up evidence**. This is the only PR-head run that should be used to validate the integrated slice.

Do not report a full Quality PASS for this handoff until #3149 (or a newer exact-candidate run containing the merge) completes and is decoded.

## Collision statement

The run deliberately did not modify active ownership areas for:

- Secondary Navigation / Settings / shared UI;
- Storage/Core API/Desktop health telemetry;
- WAL and durable filesystem work;
- LM Studio adapter/streaming security;
- Quality/Visual/workflow harness;
- scheduler or shared coordination ledger.

Changed candidate files are limited to:

- `src/athena/hardware_acceptance.py`;
- `tests/unit/test_hardware_acceptance_boundaries.py`;
- `docs/agent_logs/2026-08-26-independent-hardware-boundaries-run.md`.

## Stale/future items

- The previously noted ContextPackage structured-schema serializer error-family issue is already fixed on the current candidate. Do not reopen it from older handoff text without fresh evidence.
- `_gpu_matches()` still permits the expected GPU name as a substring of a detected controller name. This run intentionally did not tighten that rule because no authoritative target-Windows naming evidence established that the compatibility tolerance is wrong. Require observed hardware evidence before changing it.

## Bot instructions

1. Do not duplicate IHB-001 or IHB-002 unless current-head evidence reproduces a failure.
2. GATES/QA should use #3149 or a newer exact-candidate run; #3147 and #3148 are superseded for this slice.
3. Do not reopen the prior ContextPackage structured-schema boundary from stale notes.
4. Do not tighten GPU-name matching without real target-machine evidence.
5. Backend, UI and Security workers can continue their existing claims; this integration did not occupy their paths.
