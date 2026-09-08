# pATHENA UI Handoff

## Current baseline

- Base: `develop/pathena-next@df05e76c998148e2445401de04115a7c5dccd708`.
- Worker: `postmerge/ui`.
- History-preserving NON-FORCE synchronization commit: `ceb1cab9748211a27fd71c69abd62228abf10ace`, with parents `4c656c2c5dfb55e6d3f0078719183cbbad73a555` and `df05e76c998148e2445401de04115a7c5dccd708`.
- `main` and `bnbgrs/ATHENA` remain untouched/read-only.
- Original eleven reference images: `VISUAL_REFERENCE_PENDING`; no pixel-level parity or `MATCH` claim is made.

## Verified handoff

### UI-GAP-0074 — Jobs nonzero-exit status command jargon

Status: `FIXED_INTEGRATOR_READY`, P2.

- Product commit: `ee2dafc9453c8e3b5d67aed107a955b086111f68`.
- Focused regression: `10ddf88043757628906480541e179323f5af7247`.
- Exact descendant head `4d6d1f7b3bc99dbff3015ddb8c499af885859ac8` passed ATHENA Quality Gate `34187727628 = success` carrying the unchanged product/test commits.
- Visible nonzero-exit copy now names the user operation instead of a Jobs command while retaining exit codes and background ownership.

### UI-GAP-0075 — Jobs QProcess error surface command/process jargon

Status: `FIXED_INTEGRATOR_READY`, P2.

- Product commit: `86444c8a762f910d9929f50841f78376312a0afe`.
- Focused regression: `9af7d23d2daccdee78236b6da335090d512d7fcd`.
- Exact descendant head `4d6d1f7b3bc99dbff3015ddb8c499af885859ac8` passed ATHENA Quality Gate `34187727628 = success` carrying the unchanged product/test commits.
- `_process_error()` now identifies `Jobs refresh`, `Job details`, or the actual job action instead of local/Jobs-command wording. QProcess classification and process-spawn/runtime behavior are unchanged.

### UI-GAP-0076 — Cancellation-requested help exposes Worker architecture

Status: `FIXED_INTEGRATOR_READY`, P2.

- Product commit: `08d64fd4c9ffbbea428c4e18c8ffd784394adf0e`.
- Focused regression: `bcc471caef3b902f8cd4b07c969d896e9ae349cc`.
- Exact worker head `4c656c2c5dfb55e6d3f0078719183cbbad73a555` passed canonical Quality `34191944523 = success`; Windows path safety, Linux storage, local install smoke, specification validator, Ruff, mypy and full pytest all passed.
- Visible tooltip/accessibility help now says cancellation is waiting to complete, without Worker acknowledgement/persistence/lifecycle vocabulary.
- Enabled/disabled action matrix, `cancel_requested` state, transition receipts, scheduler, worker, storage, backend, security and cancellation semantics are unchanged.

The previously demonstrated terminal-state action-copy blocker remains closed on the verified lineage: visible terminal help uses `no actions are available`, with no action-availability or lifecycle-state semantic change.

## Active UI slice

### UI-GAP-0077 — Jobs verification-failure details expose command-output implementation language

Status: `OPEN`, P2.

Evidence: the `JobLifecycleError` detail path still renders `JOB ACTION RESPONSE UNAVAILABLE` and `Raw command output` in the visible details pane. This exposes the CLI transport/output mechanism even though the status and tooltip already use user-facing verification language.

Acceptance for the next bounded slice: preserve the exact diagnostic payload and verification behavior, changing only visible heading/label copy to user-facing recovery language. No parser, process-spawn, lifecycle, scheduler, worker, storage, backend, security or cancellation semantics may change.

## Coordination

- Core: current `spec-core.md` reviewed; no UI-authored Core/Search/Knowledge/Research semantics changed.
- Backend: current `backend.md` reviewed; no UI-authored backend/storage/scheduler/worker/provider/transport semantics changed.
- Errors: current `errors.md` reviewed; no historical Windows crash signature is reopened without exact-SHA reproduction.
- Integrator: current Develop handoff was synchronized through explicit two-parent NON-FORCE commit `ceb1cab9748211a27fd71c69abd62228abf10ace`. UI-GAP-0076 is now ready for independent integration from product `08d64fd4c9ffbbea428c4e18c8ffd784394adf0e` plus regression `bcc471caef3b902f8cd4b07c969d896e9ae349cc`, verified on exact worker head `4c656c2c5dfb55e6d3f0078719183cbbad73a555` by Quality `34191944523 = success`.
- UI-GAP-0077 is not integrator-ready; it has only evidence/acceptance definition at this point.

## Visual evidence

The original eleven screenshots are not accessible through the current repository/tool path. `VISUAL_REFERENCE_PENDING` remains mandatory. No `MATCH`, pixel-spacing, exact-color or screenshot-parity claim is made.
