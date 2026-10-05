# Handoff — Desktop chat edit/fork controls — 2026-10-05

## Baseline

- Repository: `bnbgrs/pATHENA`
- Base: `develop/pathena-next` after merged PR #486
- Branch: `desktop/chat-edit-fork-controls-20261005-sol`
- Integration target: `develop/pathena-next`

## Implemented

- Persisted user messages expose a real **Edit** action.
- Persisted messages expose a real **New chat** action backed by durable fork provenance.
- Edit opens a multiline editor seeded with the persisted content and submits the exact `chat_id`, `message_id` and `revision_id` through `DesktopApiController.edit_message(...)`.
- New chat submits the exact source message revision through `DesktopApiController.fork_chat_from_message(...)`.
- Edit is only present for user messages; fork is available for persisted messages.
- Both controls obey the existing busy/pending/Core-ready enablement rules.
- Failures are labeled truthfully as Message edit / Chat fork, including non-retry mutation notes.
- pATHENA presentation and message-action accessibility include the new controls.

## Validation

Focused UI regression verifies:
- Edit exists only for user messages;
- New chat exists for user and assistant messages;
- accessible names are stable;
- button clicks call the controller with exact persisted identities;
- edit submits replacement text returned by the modal editor.

## Non-goals

- Regenerate remains intentionally separate.
- No synthetic branch state is kept in the Desktop.
- No issue #296 checkbox is closed until this PR is integrated and exact-head gates are green.
