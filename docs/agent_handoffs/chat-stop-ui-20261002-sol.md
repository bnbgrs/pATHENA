# Chat STOP Desktop/UI handoff — 2026-10-02

## Scope and lineage

- Worker branch: `ui/chat-stop-control-plane-20261002-sol`.
- Stacked source: PR #329 head `a01f253d7b5dd183d5da56cf099d1e05b20b2ad2`.
- Integration target remains `develop/pathena-next`.
- Draft integration/validation PR: #337.
- This slice is intentionally stacked on #329. Do not merge it independently before #329 is integrated or reconstructed onto the resulting Develop head.
- No Core cancellation registry/API implementation, LM Studio transport, Storage, Research, bot configuration, or foreign branch was modified.

## Ausgangslage

PR #329 establishes a real out-of-band cancellation endpoint for active **direct-chat** operation IDs. The Desktop did not consume that control plane, so the running composer still exposed only a generic busy state and had no truthful Stop path.

Grounded/Unified sends carry operation IDs but #329 does not register them in the cancellation registry. Exposing Stop for Grounded/Unified would therefore be fake functionality.

A second integration hazard existed in the Desktop: the normal chat worker can run in a one-thread `QThreadPool`. Sending a cancellation task through that same pool would serialize the cancel request behind the blocked generation and make Stop ineffective.

## Root cause

The Desktop controller did not retain the active direct-send operation identity as UI control-plane state and had no independent worker lane for the cancellation POST. The composer consequently had no way to distinguish:

- normal idle Send,
- cancellable direct generation,
- non-cancellable busy operations,
- cancellation request in flight,
- accepted cancellation awaiting termination,
- late/expired cancellation,
- request failure.

## Changes

### Desktop API controller

`src/athena/desktop/api_controller.py`

- Extends the Desktop gateway protocol with the already-existing #329 `cancel_chat_operation(operation_id)` API.
- Retains the exact active operation ID only for direct `send` operations.
- Adds a dedicated one-thread **control** `QThreadPool`, separate from the chat send pool.
- Adds an out-of-band cancel runnable and identity-checked result queue.
- Publishes truthful cancellation state: `requesting`, `accepted`, `expired`, `failed`.
- Keeps `chat_busy` true until the original send task actually terminates.
- Reconciles Core `generation_cancelled` without replaying the POST. A durable user turn may be rendered; no incomplete assistant turn is invented.
- Treats accepted-but-too-late cancellation as completed/expired rather than claiming the completed response was stopped.
- Ignores stale cancel results after the active operation identity has changed.

### Desktop composer behavior

`src/athena/desktop/window.py`

- While idle: normal Send behavior.
- While a direct send is active: Send action becomes a real Stop action.
- While cancellation is requesting/accepted: Stop becomes disabled pending termination.
- While Grounded/Unified or another non-cancellable chat operation is active: action remains disabled and does not pretend Stop exists.
- Accessibility/tooltips distinguish Stop, cancellation requested, and generic chat-operation busy states.
- Terminal confirmed cancellation schedules a normal Core refresh and states that no incomplete assistant response was saved.

### V3 presentation

`src/athena/desktop/pathena_window.py`

The existing single-paint composer contract is preserved:

- `→` idle Send,
- `■` cancellable direct generation,
- `…` cancellation pending or non-cancellable busy state.

No second visible action/button was introduced.

## Tests added

`tests/unit/test_desktop_api_controller.py`

- proves cancellation runs on a different worker thread even when the normal send pool has `maxThreadCount=1` and is blocked;
- proves confirmed cancellation keeps only the reconciled durable user turn and emits cancellation rather than success;
- proves a rejected/expired cancel leaves the send running and allows a later retry;
- proves an accepted-but-late cancel is reported as completed/expired, not falsely cancelled.

`tests/unit/test_pathena_window.py`

- proves the V3 composer exposes `■` Stop only for a real cancellable direct send;
- proves prompt/ground controls remain disabled while generation is active;
- proves cancellation-pending and non-cancellable busy states disable the action and expose truthful accessibility;
- proves normal idle Send returns to `→`.

## Validation

Local checkout/test execution from this agent environment is blocked because DNS resolution for `github.com` fails. No local PASS is claimed.

PR #337 is used for exact-head repository validation. Required evidence is:

- ATHENA Quality Gate,
- pATHENA UI Focused Candidate,
- pATHENA 11-Surface Visual Regression.

Use the final PR #337 exact-head run IDs as the authoritative validation record.

## Known remaining problem

#329 itself explicitly retains a transport-level limitation: synchronous LM Studio `urllib` `open()/readline()` can block until data/timeout because the current transport does not expose a safely interruptible in-flight request handle. The new Desktop Stop is real at the Core cancellation control plane, but bounded interruption while inside that blocking transport remains a Runtime follow-up. Do not mask this with polling or fake progress.

Grounded/Unified cancellation also remains unsupported by this UI because #329 does not register that path in the cancellation registry.

## Collision risk

This stacked slice changes only:

- `src/athena/desktop/api_controller.py`
- `src/athena/desktop/window.py`
- `src/athena/desktop/pathena_window.py`
- `tests/unit/test_desktop_api_controller.py`
- `tests/unit/test_pathena_window.py`
- this handoff file

UI bots touching the same composer/controller files should consume this branch/PR before making competing STOP changes. Core/Backend bots should leave the Desktop slice intact and continue #329/LM Studio work independently.

## Next steps

1. Require terminal exact-head CI success on PR #337.
2. Require #329 exact-head Quality success and integration/reconstruction onto current Develop.
3. Reconstruct/retarget this bounded five-code/test-file Desktop delta onto the post-#329 Develop head; do not merge old stacked history blindly.
4. Re-run Quality + UI Focused + 11-Surface gates on that resulting exact candidate.
5. Then address the independent LM Studio transport abort limitation with a genuinely interruptible transport/lifecycle design.
6. Extend cancellation to Grounded/Unified only after the Core path has a real registry/checkpoint contract; until then keep Stop unavailable there.
