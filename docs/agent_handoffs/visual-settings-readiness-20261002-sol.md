# Visual Settings readiness handoff — 2026-10-02

BASE: develop/pathena-next@3357bf1e66d9d60d7b1c9e2d528c36632d89fbc5
BRANCH: fix/visual-settings-readiness-20261002-sol

## Reproduced failure

PR #419 changed only the truthful System/Settings inspector copy, but the Windows eleven-surface visual gate produced two different Settings screenshots without a product-code change:

- one capture had a settled Core snapshot ("Model error", LM Studio unavailable, persisted model limits, resolved News state);
- the next capture had the startup state ("Connecting…", model/local service waiting, zero model limits, News waiting).

The committed-baseline refresh therefore failed again immediately. Ten of eleven surfaces were stable in both runs.

## Root cause

The sequential visual harness starts capture after seven seconds while desktop startup schedules Core refresh/recovery attempts at 0.25, 0.75, 1.5, 3, 5, 10 and 20 seconds. Knowledge already has an explicit readiness barrier, but Settings was rendered immediately after route selection. It could therefore race the live Core/model/news snapshot pipeline.

## Fix

- require the Settings runtime controller and API controller;
- wait through the 10-second startup refresh horizon (minimum runtime 11 seconds);
- require a real Settings snapshot, no active Core refresh, and a completed/unsupported News-profile request;
- reject transitional top-level statuses such as "Connecting…";
- require the complete visible Settings state tuple to remain unchanged for 0.5 seconds;
- fail the capture explicitly after 20 seconds instead of accepting a startup race;
- record Settings readiness evidence in the visual manifest;
- add a pure readiness-contract QA test and run it in the Windows visual workflow.

## Integration

This branch deliberately does not touch PR #419's product file or visual baseline. Merge this harness fix first. Then rebase/update #419 and generate exactly one reviewed baseline from the stable exact-head capture.
