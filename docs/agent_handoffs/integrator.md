# pATHENA Feature Integrator Handoff

## Current branch state

- `main` remains strict read-only at `0d4d621f8a38ddf8eccfa09622bf193687619943`.
- Develop before this run: `8236500a5ae0ae58e7dce5bb3cf0771eb534670d`.
- Integration target: `develop/pathena-next` only.
- Worker heads reviewed: errors `0049ca90d1687b1c5ea8722895e1c9f2a1fe9e76`; spec-core `a43a471b611c78d24ebb8c67253b855b6a0642f3`; backend `d6fca835ad432e05aecbdc3c790a55ec2691a11b`; ui `8cbec3ef97a13caf626450a0111ee3dc50b262cc`.
- `main` and `bnbgrs/ATHENA` were untouched.

## Integrated this run — UI-GAP-0035 Research detail reader keyboard focus

READY UI lineage independently reviewed:

- product commit `f9d0a01de648ea806bfd725c3b35a68fc9eb425d`;
- focused regression `4183addc10689496101c2b4d6ae7d45fcb4cf3d1`;
- exact verified UI documentation head `089a0e4b0b8fc43e37f00f8288f64cd62014fbb4`;
- canonical ATHENA Quality `34019891561 = success`.

Compatibility review against exact Develop showed `src/athena/desktop/pathena_shared_components.py` lacked the Research-detail focus selector and the focused test path did not exist. The worker product delta was exactly one selector addition and the focused test was exactly ten lines. To avoid importing divergent UI history, the semantic one-line product delta and exact focused regression were applied directly to the exact Develop tree.

Develop product/test commit: `51e74e5cf294f54c4c2f29666af0fee6e89c0c61`.

Independent compare `8236500a5ae0ae58e7dce5bb3cf0771eb534670d..51e74e5cf294f54c4c2f29666af0fee6e89c0c61` is ahead 1, behind 0, and changes exactly:

- `src/athena/desktop/pathena_shared_components.py`: +1/-0;
- `tests/unit/test_pathena_research_detail_focus.py`: +10/-0.

## Contract now covered

- The read-only Research detail reader has an explicit canonical keyboard-focus presentation.
- The focus border uses the existing `PALETTE.accent` token and shared focus block.
- No Research content, selection routing, persistence, provenance, Backend, Storage, Security, Provider, Worker, Scheduler or Windows-runtime behavior changed.

## Validation state

- Exact UI source lineage passed canonical Quality `34019891561 = success`.
- Independent Develop diff review confirms the integrated change is exactly the bounded one-line selector plus its focused regression.
- Local checkout/test execution was unavailable because DNS resolution for `github.com` failed; this was treated as a tooling limitation rather than a product blocker because the GitHub connector provided complete blobs and safe repository mutation.
- No workflow run is currently associated with exact Develop product/test SHA `51e74e5cf294f54c4c2f29666af0fee6e89c0c61`; exact-current-Develop repository-wide green is therefore not claimed.

## Other current inputs

- Core provenance-boundary handoff reports exact green Quality `34018695781`, but independent review found its isolated diff is not directly applicable to the exact Develop `models.py` shape without importing prerequisite Proposal structure; it is deferred pending a bounded compatible composition.
- Backend `ERR-0016` is OPEN on the oversize-before-accounting lineage. The explicit poison-state fix exists but is `FIXED_PENDING_VERIFY`, so that lineage is rejected as READY until exact canonical green.
- UI-GAP-0036 is implemented but remains pending canonical verification.
- All eleven UI screens remain `IMPLEMENTED_PENDING_VISUAL_REVIEW`; pixel-level `MATCH` remains unclaimed without original references.
- `ALPHA_BETA_PROGRESS.md` was read, but its connector response is truncated; no whole-file rewrite is attempted because that could discard tracker content. This integration evidence is preserved here until a safe complete-file update path is available.

## Runtime/release guards retained

Known Windows pypdf packaging, fail-closed frozen argv routing, bounded process tree, adaptive 2048-context DirectChat budgeting, lane-lock/SchedulerLaneOwnership packaged-worker crash cluster and storage-bootstrap/migration startup signatures remain explicit Beta/release regression requirements. This UI slice does not alter their owning semantics.

## Next integration order

1. Prefer a bounded compatible Core provenance-boundary composition if a worker supplies exact-green evidence against the current Develop shape.
2. Otherwise consume exactly one compatible READY UI/Backend successor; UI-GAP-0036 must first obtain exact canonical green, while Backend `ERR-0016` fix must close with exact poisoning + oversize-accounting evidence.
3. Obtain exact-current-Develop Quality before repository-wide green or promotion-ready claims.
4. Before Beta/release readiness, explicitly regress all retained Windows packaging/process-tree/startup/chat-context/lane-lock crash classes on the exact candidate SHA.

## Rules retained

- No direct work on `main`; no main promotion.
- No force-push, history rewrite or auto-merge.
- No Skip/XFail, weaker assertions, Security/Storage/Windows/Recovery/validator relaxation, fake success or fabricated provenance.
