# Handoff — Chat edit/fork Core API transport — 2026-10-05

## Baseline

- Repository: `bnbgrs/pATHENA`
- Integration target: `develop/pathena-next`
- Exact base: `bd7c683f2ccac498205d580c6666efc6f0d9c60f`
- Branch: `core/chat-edit-fork-api-20261005-sol`
- Pull request: #485
- Durable repository/service substrate: merged #342

## Problem

#342 correctly implemented immutable user-message edits and durable chat forks with exact revision provenance, but intentionally stopped at the domain service. Desktop code cannot truthfully expose Edit or “new chat from here” until that mutation crosses the Core owner-thread and authenticated local API boundaries.

## Implemented

- `CoreApiFacade.edit_chat_message(...)`
  - requires chat ID, message ID, exact expected revision ID and replacement content;
  - delegates to `ChatService.edit_user_message()`;
  - returns the reloaded canonical thread.
- `CoreApiFacade.fork_chat_from_message(...)`
  - requires exact source message revision;
  - delegates to `ChatService.fork_chat_from_message()`;
  - returns the newly persisted fork thread.
- `CoreDomainSurface` + `SerializedCoreApiSurface` carry both mutations through the single owner thread.
- Authenticated local routes:
  - `PATCH /api/v1/chats/{chat_id}/messages/{message_id}/edit`
  - `POST /api/v1/chats/{chat_id}/messages/{message_id}/fork`
- Native `CoreApiClient` methods for both operations.
- Capabilities advertise `chat.edit.user_message` and `chat.fork`.
- ASGI maps domain conflicts fail-closed:
  - missing message -> 404;
  - stale revision -> 409;
  - unsupported edit/protected semantics -> 409;
  - unsupported fork/protected semantics -> 409.
- Mutating client calls are not transport-retried.

## Validation added

- ASGI success path for exact-revision edit and fork.
- ASGI malformed revision payload rejection.
- Client request method/path/body verification.
- Client invalid revision rejection.
- Existing `tests/unit/test_chat_branching.py` remains the authority for immutable revision history, fork provenance, stale guards, and protection fail-closed behavior.

## Deliberately not claimed

This does not complete #296 by itself. Desktop Edit, Regenerate and “new chat from here” controls are not added here. Regenerate semantics remain separate because a truthful regeneration must define which persisted branch receives the new provider output rather than mutating historical turns.

## Next safe slice

After #485 is exact-head green and integrated:

1. add asynchronous DesktopApiController tasks for edit/fork, using the same off-UI-thread pattern as universal search and chat sends;
2. expose Edit only for local-user messages with a real revision ID;
3. after edit, refresh from the returned canonical thread;
4. expose “new chat from here” on persisted messages and switch to the returned fork chat;
5. keep Regenerate separate until its durable branch/output semantics are explicit;
6. only then mark the corresponding #296 boxes complete.
