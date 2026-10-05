# Handoff — Desktop Recovery/Continue controller — 2026-10-05

## Baseline

- Repository: `bnbgrs/pATHENA`
- Stacked base: PR #490 / `core/unified-recovery-continue-20261005-sol`
- Branch: `desktop/recovery-controller-20261005-sol`

## Purpose

PR #490 exposes durable Unified recovery inspection and safe Continue through the local Core API. This slice consumes that contract in the Desktop controller without yet adding visible UI controls.

## Implemented

### Gateway contract

Desktop `CoreApiGateway` now consumes:
- `chat_operation_recovery(chat_id, operation_id)`
- `continue_unified_local_chat_operation(chat_id, operation_id)`

### Async controller

Adds:
- `inspect_chat_recovery(...)`
- `continue_chat_operation(...)`
- `chat_recovery_ready` signal

Both execute through the existing chat worker pool, never on the Qt UI thread.

Recovery inspection validates that returned chat/operation identity exactly matches the request before it is surfaced to UI consumers.

Continue returns the canonical `GroundedChatResponse` and reuses the existing `grounded_chat_sent` path.

### Cancellation

A running `continue_recovery` operation is treated as a cancellable generation operation:
- the stable persisted operation ID becomes the active cancellation identity;
- `can_cancel_active_chat` remains true while Continue is active;
- the existing separate cancellation worker sends Stop without waiting behind the generation worker;
- `generation_cancelled` is surfaced through the existing `chat_cancelled` signal.

No new cancellation state machine is introduced.

## Tests

Focused controller regressions prove:
1. recovery inspection runs off the UI thread and emits the exact immutable recovery DTO;
2. Continue runs off the UI thread and emits canonical Grounded output;
3. Continue preserves the exact existing operation ID;
4. Stop remains available while Continue is blocked;
5. cancellation of Continue completes through the existing cancellation signal and clears busy state.

## Scope boundary

This slice intentionally adds no visible Continue button yet.

The next UI slice should:
- inspect only persisted operations whose identity can be derived from durable chat state;
- show Continue only when Core returns `can_continue=true`;
- show an explicit recovery-required/ambiguous state otherwise;
- never reconstruct the original prompt/model/retrieval configuration in the UI.
