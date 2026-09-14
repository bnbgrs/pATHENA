# pATHENA 11-screen UI parity contract

Reference family: `11-screen-2026-08-24`.

This document is the visual contract for the desktop shell. It is deliberately presentation-only: Core behavior, persistence, job semantics, provenance truth and local-only boundaries must not be changed to make a screenshot match.

## Shared shell

Screens 02-09 and 11 use the same workbench geometry at 1480×900:

- 60 px global top bar.
- 68 px icon rail.
- Flexible central workspace.
- 340 px right inspector.
- Near-black canvas with subtle charcoal surfaces and rules.
- White/gray text; orange `#F26A21` only for selection, focus and actionable emphasis.
- Green is reserved for healthy local state; red is reserved for destructive/conflicting state.
- Large workspace titles use the editorial serif hierarchy.
- The right rail is titled `EVIDENCE & ACTIVITY` on workbench screens.
- The footer composer remains visible across the normal workbench and uses a right-arrow send affordance.

Canonical implementation values live in `src/athena/desktop/pathena_design_tokens.py`. Do not reintroduce the older navy/cobalt palette in feature-local stylesheets.

## Screen-by-screen contract

| Ref | Surface | Required visual identity |
| --- | --- | --- |
| 01 | Chat / disconnected startup | Special first-run state. `Getting pATHENA ready`, `LOCAL CORE · CONNECTING`, centered quiet empty state, knowledge-oriented right context, disabled composer remains visible. |
| 02 | Knowledge | Top destination remains `KNOWLEDGE`; workspace title is `Library`; canonical memory/search surfaces stay dense and provenance-first. |
| 03 | Research | `Research` title, query/filter hierarchy, run list and result/canonical-memory detail split. |
| 04 | Jobs | `Jobs` title, quiet tabs/filtering, durable-job list and detail split; no decorative status color. |
| 05 | Sources | `Sources` title, import/refresh actions, source list and source-detail split. |
| 06 | System | `System` title, runtime navigation, operational status and security posture; unavailable values remain explicit rather than fabricated. |
| 07 | Settings | `Settings` title, secondary settings navigation, model/inference controls with restrained slider emphasis. |
| 08 | PALLAS | Full black semantic field, sparse graph, orange grounded-response focus, white canonical/source/claim nodes, red conflicting evidence. |
| 09 | Command palette | Centered compact command surface, 560 px minimum width, orange focus border, workspaces grouped first, keyboard footer visible. |
| 10 | Help | Dedicated help surface, left topic navigation, search-first capability list, same black/orange language without workbench chrome. |
| 11 | ComfyUI | Local loopback workflow utility inside the workbench; conventional controls, no visual treatment that implies remote/cloud execution. |

## Navigation semantics

The global destinations are `CHAT`, `KNOWLEDGE`, `RESEARCH`, `JOBS`, `SOURCES`; System and Settings remain utility destinations. The visible workspace title for Knowledge is intentionally `Library`. This distinction is part of the reference family and should not be normalized away.

## Guardrails

1. Prefer canonical tokens and narrowly scoped selectors over feature-local palettes.
2. Do not change API, persistence or provenance contracts for visual parity.
3. Do not fabricate successful/available state to improve a screenshot.
4. Preserve keyboard access, visible focus and reduced-motion behavior.
5. Treat the eleven screens as one family: a local fix must not regress the shared shell.
6. New UI work should add a focused regression test when it changes a reference invariant.
