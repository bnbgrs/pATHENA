# Manual Handoff — Chat immutable edits and durable forks — 2026-10-02

## Baseline

- Repository: `bnbgrs/pATHENA`
- Integration target: `develop/pathena-next`
- Exact base: `67174198e1494fd4c8678aad60756c39ef5c160b`
- Working branch: `feature/chat-branching-core-20261002-sol`
- `main` and `bnbgrs/ATHENA` remain untouched.
- This slice is intentionally disjoint from active #329 Chat cancellation, #330 Desktop composer truthfulness, #331 LM Studio runtime, #332 update-manifest hardening, and #333 Settings/News recovery.

## Ausgangslage

Issue #296 requires conversation editing/branching to be backed by real Core persistence, not UI-only mutation. The existing chat repository had immutable revision tables and multi-input provenance, but exposed only chat creation and append-only message creation. There was no supported way to:

- edit a prior user turn without overwriting history;
- create a new persisted chat from an exact prior message revision;
- preserve durable source revision identity for either operation.

## Root Cause

The schema already contains the required primitives (`revisions.parent_revision_id`, `provenance_records`, and `provenance_inputs`), but `ChatRepository` never composed them for edit/fork use cases. Any Desktop-only implementation would therefore have had to fake state or lose provenance.

## Änderungen

### Immutable user-message edit

`ChatRepository.edit_user_message()` now:

- accepts only a message belonging to the requested standard chat;
- requires the caller's exact expected current revision and fails with `ChatRevisionConflictError` on a stale edit, preventing lost updates;
- accepts only a `user` message authored by the editing actor;
- creates a new revision instead of mutating the existing row;
- links `parent_revision_id` to the exact previous head;
- records `chat_message.edit` provenance;
- records a `provenance_inputs` edge with role `prior_revision`;
- advances `entity_heads` only after the new revision exists;
- records an `update` commit change;
- fails closed before mutation when the chat, message entity, or current message payload is protected, because this slice does not own protection-scope-aware re-encryption.

`ChatService.edit_user_message()` rejects blank text before persistence and routes through the stable local-user actor.

### Durable “new chat from here” fork

`ChatRepository.fork_chat_from_message()` now:

- validates that the fork point belongs to the requested standard chat;
- requires the exact source revision visible to the caller and fails with `ChatRevisionConflictError` if that revision is stale, preventing a fork from silently moving to a newer edited head;
- creates a new independent standard chat;
- copies only history through the selected message sequence;
- creates new immutable message entities/revisions for the fork;
- preserves source message type and actor identity;
- records `chat.fork` provenance whose `fork_point` input is the exact selected source message revision;
- records `chat_message.fork` provenance for every copied message whose `fork_source` input is the exact source message revision;
- performs the entire fork inside one write transaction and one canonical `chat.fork` commit record, so an invalid fork point cannot leave a partial chat;
- reuses the exact source revision payload hash for each copied immutable revision;
- fails closed before mutation if the source chat, any copied message entity, or any copied payload is protected, preventing an implicit downgrade into an unprotected fork.

`ChatService.fork_chat_from_message()` exposes the use case without adding Desktop/API controls in this slice.

### Canonical fork-origin read path

`ChatForkOrigin` plus `ChatRepository.get_fork_origin()` / `ChatService.get_fork_origin()` project the exact persisted source message and source revision for a forked chat. Normal chats return `None`; ambiguous or malformed fork provenance fails closed instead of choosing an arbitrary parent.

## Dateien

- `src/athena/chat/models.py`
- `src/athena/chat/repository.py`
- `src/athena/chat/service.py`
- `src/athena/chat/__init__.py`
- `tests/unit/test_chat_branching.py`
- this handoff

## Tests added

`tests/unit/test_chat_branching.py` covers:

1. edit creates revision 2, keeps old payload, links the exact parent revision and provenance input;
2. stale edit expectations fail without creating a successor revision;
3. assistant messages cannot be rewritten through the user-edit path and gain no extra revision;
4. fork copies exactly the prefix through the selected revision and retains exact per-message/source provenance;
5. the canonical fork-origin read path returns that exact source message/revision and returns `None` for an ordinary chat;
6. a stale fork source revision fails without creating a partial chat;
7. protected chat/message/payload states fail closed for edit and fork without adding a revision or partial chat;
8. a fork point from a different chat fails before any partial chat is created.

## Validation

Direct local checkout/test execution is unavailable in this execution environment because `github.com` DNS resolution is blocked. No local PASS is claimed.

The initial product diff was verified as disjoint from active bot-owned files before the draft PR was opened. Subsequent commits only harden this same chat persistence/test/handoff slice.

Draft PR: #342. Exact-head GitHub CI is required before integration; older workflow runs from superseded branch heads do not count as validation.

## Known remaining scope

This slice intentionally does **not** yet implement:

- Core API/IPC projection for edit/fork;
- Desktop “Edit”, “Regenerate”, or “New chat from here” controls;
- regeneration semantics after an edited turn;
- pin/favorite conversations;
- provider transport cancellation;
- protection-scope-aware fork/edit re-encryption (current behavior intentionally fails closed rather than weakening protection).

Those should be layered on only after the repository/service contract is exact-head green.

## Conflict risk

Low relative to current active work. Do not merge by wholesale copying old Chat cancellation branches. Future API work may touch files currently owned by #329; wait for or build on that integration rather than duplicating it.

## Next sensible steps

1. Run exact-head focused chat tests and canonical Quality on this branch.
2. If green, integrate this bounded repository/service slice into `develop/pathena-next`.
3. After #329 settles, project edit/fork through the Core API with stable DTOs.
4. Only then expose truthful Desktop controls backed by those Core methods.
