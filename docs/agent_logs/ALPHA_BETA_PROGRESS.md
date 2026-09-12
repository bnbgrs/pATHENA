# pATHENA Alpha/Beta Progress

Evidence-only progress register for `develop/pathena-next`. This file intentionally contains no invented completion percentage.

## Current baseline

- Develop parent before current integration: `1213c49a391f4ffed6f64d63bcf1527a21adf071`.
- Exact parent canonical Quality `34721255765 = SUCCESS`.
- Worker heads checked: Errors `6cc64cb75cf1e419051de7384a2c45ffcf834881`; Spec/Core `bd97e30adbd2a5fd2e41dbd4dcaa79e3d099943e`; Backend `e4103c5b29e610dcda7618082cb77eaab0850264`; UI `c7422f47c18fba9ad3dd8b1e49eb64448aa23c24`.

## Current integration state

- Durable schedule identity, materialization, recovery and deterministic versioned schedule serialization remain integrated.
- Validated complete WAL+SHM withdrawal remains accepted only with unchanged primary database identity; partial or foreign identity changes remain fail-closed.
- Truthful Knowledge provenance explanation is integrated and now gains a transport-neutral API projection backed only by the recorded current revision and its provenance inputs.
- Direct Knowledge revision-change explanation is integrated with explicit adjacency, identity and timestamp invariants and without fabricated reasons.
- Source-free user Knowledge, correction conflict visibility, fail-closed release-readiness assessment and Core-Focused candidate regression guards remain integrated.

## Exact Worker evidence

- Spec/Core `bd97e30adbd2a5fd2e41dbd4dcaa79e3d099943e`: Core Focused `34722264650 = SUCCESS`; canonical Quality `34722264705 = SUCCESS`; effective product/test delta versus current Develop is four additive files covering Knowledge provenance API projection and revision-change explanation.
- Backend `e4103c5b29e610dcda7618082cb77eaab0850264`: current synchronization head; no independent Backend product delta selected in this integration.
- UI `c7422f47c18fba9ad3dd8b1e49eb64448aa23c24`: synchronization head; visual parity remains separately evidence-gated.
- Errors `6cc64cb75cf1e419051de7384a2c45ffcf834881`: current handoff keeps `ERR-0042` pending integrated verification and `ERR-0046` open as a Core-Focused ownership-selection issue; newer exact-SHA workflow evidence takes precedence over the historical ledger.

## Error and visual truth rules

- `docs/agent_logs/ERROR_LEDGER.md` is historical relative to current Develop and is not the sole authority where newer exact-SHA evidence exists.
- Historical release-guard signatures are not reopened without current exact-SHA reproduction.
- Eleven-screen status remains fail-closed; no visual `MATCH` without opened original reference plus real exact-SHA render.

## Persistent release guards

Do not relax: pypdf packaging; fail-closed Frozen argv; Desktop/Worker two-EXE split; exactly one Desktop instance with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock cluster; duplicate-column/Core-startup/storage-bootstrap signatures; Security/Storage/Recovery guards; test strength; Skip/XFail prohibitions.

## Promotion state

`PROMOTION_READY=NO`

The newly integrated Core slices require exact-current Develop canonical Quality before they are considered integrated-green. Develop becomes Beta/Release-ready only after exact-current canonical Quality plus the known Windows/Packaging/Runtime regression matrix are green.
