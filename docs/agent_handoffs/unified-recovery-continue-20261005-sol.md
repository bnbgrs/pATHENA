# Handoff — Explicit Unified recovery/Continue — 2026-10-05

## Baseline

- Repository: `bnbgrs/pATHENA`
- Base: `develop/pathena-next` @ `6732e6a5e798d9cbc782e83d6d26c55c1c0a6d5b`
- Branch: `core/unified-recovery-continue-20261005-sol`

## Purpose

Issue #296 requires interrupted generation recovery to be explicit and requires Continue to resume persisted state rather than reconstructing or inventing request state in the Desktop.

The durable Unified/Grounded path already had:
- stable operation IDs;
- a persisted request fingerprint;
- a persisted pre-user Unified send plan;
- a persisted ContextPackage;
- a pre-provider replay checkpoint;
- Grounded recovery states including `RESUMABLE`, `AMBIGUOUS`, `RESULT_AVAILABLE`, `FINALIZATION_REQUIRED` and `COMPLETE`;
- internal replay code used when the original send is retried with all original request inputs.

What was missing was a public recovery contract that can be invoked from persisted operation identity alone.

## Implemented

### Domain

`UnifiedLocalChatService.inspect_operation_recovery(...)`:
- loads the durable Unified send plan by operation ID;
- uses its persisted fingerprint rather than caller-reconstructed input;
- verifies the operation belongs to the requested chat;
- returns the existing Grounded recovery state without provider execution.

`UnifiedLocalChatService.continue_operation(...)`:
- accepts only chat ID + operation ID;
- reloads the persisted send plan/fingerprint;
- finalizes already-recorded provider results when safe;
- replays already-complete operations without another provider call;
- resumes `RESUMABLE` state from the persisted pre-provider replay checkpoint;
- refuses `AMBIGUOUS`, `CONFLICT`, `ABSENT` and other unsafe states through `UnifiedGroundedRecoveryRequiredError`;
- never asks the caller/Desktop to repost the original prompt, retrieval query, model selection or context configuration.

### API contract

Adds `ChatOperationRecoveryResponse`:
- `operation_id`
- `chat_id`
- `mode`
- `state`
- `can_continue`
- `processing_run_id`

`can_continue` is true only for states the Core can safely advance:
- `resumable`
- `result_available`
- `finalization_required`

### Local API

New authenticated routes:

- `GET /api/v1/chats/{chat_id}/operations/{operation_id}/recovery`
- `POST /api/v1/chats/{chat_id}/operations/{operation_id}/continue`

Continue is serialized on the Core owner thread. Its operation ID is reserved in the out-of-band cancellation registry before owner dispatch, so a resumed provider call retains the existing Stop/cancel race guarantee.

Unsafe states map to explicit non-retryable 409 responses:
- `chat_recovery_ambiguous`
- `chat_recovery_conflict`
- `chat_recovery_unavailable`

### Client

`CoreApiClient` now exposes:
- `chat_operation_recovery(...)`
- `continue_unified_local_chat_operation(...)`

Continue sends an empty POST body. Original generation input is not reconstructed in the client.

## Tests

Added/extended coverage proves:
- client GET parses and validates exact operation/chat identity;
- client Continue posts no reconstructed request payload;
- ASGI returns persisted recovery state;
- ASGI Continue returns canonical Grounded output;
- ambiguous state returns 409 rather than replaying automatically;
- owner-queue Continue reserves cancellation before dispatch;
- domain Continue passes the persisted fingerprint and retrieval override into the existing replay path;
- domain Continue never invokes resume from an ambiguous provider boundary;
- absent state is reported without creating request state.

## Safety boundary / remaining work

This slice does **not** claim arbitrary partial-token recovery.

A provider attempt that may already have begun but has no durable result is `AMBIGUOUS`. ATHENA deliberately refuses automatic Continue there because repeating the provider call could duplicate an external side effect.

Likewise, a user-cancelled ProcessingRun is not re-opened as if it had never ended.

Therefore the full #296 checkbox “recover interrupted/partial output explicitly; Continue must resume from persisted state rather than inventing state” remains only **partially complete** until one of the following is implemented truthfully:
- durable provider-side/transport resume identity, or
- durable partial-output/checkpoint semantics that prove where a provider continuation may resume.

## Next safe slice

After this Core/API PR is exact-head green and integrated:
1. Desktop may inspect recovery state for the latest persisted user operation on chat load.
2. Show Continue only when `can_continue=true`.
3. Route Continue through the new client method off the Qt UI thread.
4. For `ambiguous`, show an explicit recovery-required state, never a retry button that silently repeats generation.
