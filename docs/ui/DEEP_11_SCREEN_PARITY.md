# Deep 11-screen parity

This slice sits on top of `ui/11-screen-parity-20260915` and keeps the exact eleven-screen reference family as the visible UI contract.

## PALLAS

- The real semantic renderer uses canonical pATHENA design tokens instead of the legacy orange palette.
- Focus and Source use the interaction blue.
- Claim, Knowledge, and Memory use semantic green.
- Hypothesis uses the reference question purple.
- Conflict uses semantic red.
- Uncertain uses semantic yellow.
- `Open PALLAS` invokes the existing synchronized full-view controller; it does not create a second graph state.

## Sources

The fifth workspace is user-facing `Sources`. Internal source/file implementation names remain unchanged where they are implementation details.

## Truthfulness boundaries

- No Jobs steps, live logs, or resource telemetry are invented when the durable job service does not provide them.
- No `Ctrl+Space Universal search` shortcut is advertised because the current palette searches commands and workspaces rather than all local content.
- No backend, persistence, scheduler, or PALLAS graph semantics are changed by this slice.
