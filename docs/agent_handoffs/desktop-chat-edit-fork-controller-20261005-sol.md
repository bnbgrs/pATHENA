# Handoff — Desktop chat edit/fork controller — 2026-10-05

## Baseline

- Repository: `bnbgrs/pATHENA`
- Stacked base: `core/chat-edit-fork-api-20261005-sol` / PR #485
- Branch: `desktop/chat-edit-fork-controller-20261005-sol`
- Target after #485 merge: `develop/pathena-next`

## Implemented

- Extends the Desktop Core gateway protocol with the exact-revision edit/fork methods exposed by #485.
- Adds asynchronous `_ChatTask` operations for immutable user-message edit and durable chat fork.
- Validates returned chat identity and edited message content before publishing results.
- Adds public `DesktopApiController.edit_message(...)` and `fork_chat_from_message(...)` entry points.
- Reuses the canonical `chat_loaded` signal so existing thread rendering/switching can consume the returned persisted thread without UI-only state.
- Keeps both mutations off the Qt UI thread and serialized through the controller's existing chat busy boundary.

## Validation

Focused controller regressions verify:
- edit runs off the UI thread, preserves exact chat/message/revision identity and returns the canonical revised thread;
- fork runs off the UI thread and publishes a different persisted chat identity.

## Non-goals

- No message action buttons are added yet.
- No Regenerate semantics are invented.
- No issue #296 checkbox should be closed until the Desktop controls invoke these controller methods end to end.

## Next safe slice

After #485 and this PR are integrated:
1. expose Edit only on persisted local-user messages with a real revision ID;
2. expose “New chat from here” only on persisted messages with a real revision ID;
3. invoke these controller methods and let the existing `chat_loaded` path render/switch the canonical returned thread;
4. add focused UI tests for enablement, stale-revision errors and fork switching.
