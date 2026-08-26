# Independent hardware-acceptance boundary run — 2026-08-26

## Scope and collision policy

This run started from exact candidate `6bbf6232288e4e634b1d4c3c058195ec62db4cb2` on isolated branch `manual/independent-boundaries-20260826b`.

Before mutation, the live coordination ledger and scheduled worker responsibilities were re-read. The run deliberately avoided active ownership zones: Secondary Navigation/Settings/shared UI, Storage/Core API/Desktop health, WAL/durable-filesystem work, LM Studio adapter/streaming security, and Quality/Visual/workflow harness work. No files in those active product scopes were modified.

The prior ContextPackage structured-schema follow-up was also re-read first. It is already fixed on the current candidate: schema serialization `TypeError`/`ValueError` is translated to `ContextPackageError`, and non-standard JSON constants are rejected on parse. No duplicate mutation was made.

## Completed slices

### IHB-001 — require the exact local-inference acceptance marker

Status: **FIXED**.

`_run_live_inference()` instructs the local model to reply with exactly `PATHENA_LOCAL_INFERENCE_OK` and nothing else. The implementation nevertheless accepted any response containing that marker as a substring. For example, `prefix PATHENA_LOCAL_INFERENCE_OK suffix` could produce `inference_ready=True` even though the model violated the acceptance contract.

Change:

- normalize only incidental outer whitespace using the existing `.strip()`;
- require the resulting response to equal `INFERENCE_MARKER` exactly;
- update the failure detail to state that the exact marker was required.

Regression coverage:

- marker embedded in prefix/suffix text is rejected;
- surrounding whitespace/newline around the otherwise exact marker remains accepted.

Product commit: `c91e5c6763b6f3c868f6011a3017e18792bb6b0d`.

### IHB-002 — fail closed on malformed Windows controller-name evidence

Status: **FIXED**.

`_video_controller_names_from_payload()` validated that `names` was a string or list, but then silently discarded list members that were not non-empty strings. A malformed payload such as `{"names":["AMD Radeon RX 7900 XTX",123]}` could therefore retain the expected GPU string, discard the invalid evidence, and still allow a hardware PASS.

Change:

- after normalizing a single string to a list, every element must be a non-empty string;
- any non-string or blank element raises `HardwareAcceptanceError`;
- valid controller names are still whitespace-trimmed before matching.

Regression coverage:

- mixed string/integer `names` lists fail closed;
- blank controller names fail closed;
- existing valid single/multiple-name behavior remains governed by the pre-existing hardware acceptance tests.

Product commit: `c91e5c6763b6f3c868f6011a3017e18792bb6b0d`.
Test commits: `7f6d992dd16caac5539c17f0b5491942dd365ce1`, `592c5078272e2ea0fec214d99acf6dca7ebbac85`.

## Deliberately not changed

### ContextPackage structured-schema serialization

The earlier follow-up is already implemented on the current candidate. Do not reopen it from the previous handoff without fresh evidence.

### GPU name substring matching

`_gpu_matches()` currently accepts the normalized expected GPU either as an exact name or as a substring of the detected controller name. This could theoretically broaden acceptance, but this run did not find authoritative Windows naming evidence proving the current tolerance is wrong. Tightening it would risk rejecting legitimate vendor/driver name variants. No mutation is justified without observed target-machine evidence.

## Files changed

- `src/athena/hardware_acceptance.py`
- `tests/unit/test_hardware_acceptance_boundaries.py`
- `docs/agent_logs/2026-08-26-independent-hardware-boundaries-run.md`

No LM Studio adapter, desktop, storage, API, scheduler, UI, workflow, visual-harness, or coordination-ledger file was changed.

## Validation performed

- Re-read the exact candidate implementation before mutation and reproduced both fail-open conditions by source-path analysis.
- Added four narrow regression cases around the modified boundaries.
- Compared the isolated branch to frozen base before documentation: only `hardware_acceptance.py` and the new boundary test file were present in the product/test diff; product change was 15 lines total.
- Re-read the prior ContextPackage follow-up and confirmed it is already fixed, avoiding duplicate work.
- A full repository Quality PASS is not claimed until GitHub CI executes the PR/integrated head. Existing historical PASS evidence is not reused for this branch.

## Instructions for other agents

1. Do not duplicate IHB-001 or IHB-002 after this branch is integrated unless current-head tests reproduce a failure.
2. Do not reopen the ContextPackage structured-schema serialization item from the previous handoff; current candidate already translates the serializer error family.
3. Do not tighten `_gpu_matches()` from static suspicion alone; obtain real target-machine controller-name evidence first.
4. Existing Backend, UI, Security and GATES workers should continue their active claims normally; this run does not occupy their paths.
5. If CI reports a regression attributable to this slice, constrain follow-up to `hardware_acceptance.py` and `test_hardware_acceptance_boundaries.py` unless evidence shows a wider cause.
