# PALLAS Living Field

## Purpose

PALLAS is a living presentation of already-grounded semantic state. It may reorganize the visual field, but it must not become a second knowledge engine or a provenance authority.

## Semantic truth boundary

The immutable `PallasGraphSnapshot` remains the semantic source of truth. The living engine must never add, remove, rewrite, infer, or persist semantic nodes or edges. Lexical similarity is a presentation force only. It may pull visually similar nodes closer together but cannot create a relationship. Vitality diffusion follows only existing graph edges. Contradiction-specific repulsion is enabled only by explicit contradiction relations or an explicit Core conflict node.

## Runtime model

The living engine targets 30 FPS and keeps mutable presentation state per node: position, velocity, runtime age, vitality, and active state. New nodes are seeded from the deterministic PALLAS layout, recurring entity IDs retain their living state, and nodes absent from the next grounded snapshot are removed from runtime state.

Forces are deterministic for the same snapshot, seed positions, configuration, and step sequence:

- ordinary pair repulsion prevents collapse;
- real graph edges act as springs;
- lexical semantic similarity adds visual attraction only;
- explicit contradictions add stronger repulsion;
- the focus or synthesis node is biased toward the center;
- deterministic temporal drift prevents a frozen graph;
- velocity damping, maximum speed, and a bounded world radius prevent instability.

## Cellular vitality

Vitality implements the PALLAS birth, survive, diffuse, and decay model without modifying semantic membership.

- **Birth:** an inactive presentation cell can reactivate when it has enough active neighbors connected by real edges.
- **Survive:** well-connected active cells retain more vitality than isolated cells.
- **Diffuse:** vitality transfers only across real graph edges.
- **Decay:** all cells lose a small age-weighted amount of vitality over runtime.

Cited nodes and the current focus receive a modest vitality bias. Confidence is used only when the existing semantic node already carries it.

## Age language

Runtime age is visible through the documented progression:

`· : + o O ░ ▒ ▓ █`

Age is runtime observation age. PALLAS must not fabricate historical timestamps when Core did not provide them.

## Visual semantic language

The living renderer uses:

- fact or durable knowledge: `△`
- hypothesis: `◆`
- source: `■`
- synthesis or focus: `◉`
- contradiction or conflict: `×`

Memory and uncertain context retain distinct fallback glyphs.

## Lenses

The full PALLAS view exposes three non-semantic display lenses:

- **Semantic:** normal epistemic glyphs plus a small runtime age marker.
- **Age:** age becomes the primary glyph while the semantic glyph remains as the small marker.
- **Vitality:** node opacity and the small percentage marker expose current vitality.

Changing a lens cannot change the graph snapshot.

## Synchronization

One `PallasLivingQtController` owns the living engine used by compact and full PALLAS views. It updates already-rendered node positions and the existing real graph lines. Selection synchronization and the Context Inspector continue to use the original `PallasSemanticNode` objects.

## Required regression invariants

1. Fixed seeds and fixed steps are deterministic.
2. Similarity attraction does not add graph edges.
3. Explicit contradiction relations repel more strongly than ordinary pairs.
4. Runtime age follows the documented glyph progression.
5. Reconciliation preserves state for recurring entity IDs.
6. Vitality diffusion occurs only across existing graph edges.
7. Loading, empty, and error states must not display invented living data.
8. The Qt bridge must stop when the PALLAS view is disposed.
