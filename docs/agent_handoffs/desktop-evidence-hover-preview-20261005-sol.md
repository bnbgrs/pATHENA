# Handoff — Grounded evidence hover previews — 2026-10-05

## Baseline

- Repository: `bnbgrs/pATHENA`
- Stacked base: PR #487 / `desktop/chat-edit-fork-controls-20261005-sol`
- Branch: `desktop/evidence-hover-preview-20261005-sol`
- Intended integration target after #487: `develop/pathena-next`

## Why this slice exists

Issue #296 still lists “source/evidence hover previews” as open. Grounded chat already returns canonical `GroundedEvidenceResponse` objects containing source identity, URI, page/offset ranges, epistemic status and exact evidence text. The Desktop previously collapsed that real data into one inspector text block and a count summary, so there was no compact per-item preview surface.

## Implemented

- Adds a dedicated `evidencePreviewHost` inside the existing evidence-chain surface.
- Renders one non-clickable `evidencePreviewChip` per real `GroundedEvidenceResponse`.
- Chips are labels, not buttons: no fake navigation or action is implied.
- Each chip carries the real context/entity/revision/source IDs as Qt properties.
- Hover/focus metadata is derived only from the persisted grounded response:
  - cited vs context state;
  - evidence class;
  - source name or evidence title;
  - source URI when present;
  - page range;
  - byte/text offsets;
  - epistemic status;
  - clipped evidence text.
- The summary label also receives the combined preview tooltip for discoverability.
- Direct chat, empty chat, chat switches and ordinary thread renders clear all prior evidence previews before rendering new state.

## Validation

Focused UI regression verifies:

1. two persisted evidence items render as exactly two preview chips;
2. cited/context state is preserved;
3. source identity, URI, page range and offsets are shown in hover text;
4. canonical evidence title/text are shown without inventing source metadata;
5. accessible description equals the hover preview;
6. clearing removes all preview widgets, hides the host and clears stale tooltip state.

## Scope boundaries

- No source-opening action is added.
- No external URL is opened.
- No evidence is synthesized from assistant prose.
- No decorative/static evidence rail is re-enabled.
- Personal Memory remains separate from factual evidence.
- This does not implement related Knowledge suggestions or research diffs.

## Next integration step

After #487 merges, retarget this PR to `develop/pathena-next`, require exact-head UI + Quality + visual evidence, then mark only the “source/evidence hover previews” checkbox in #296 complete.
