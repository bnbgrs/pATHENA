# pATHENA Feature Integrator Handoff

## Current branch state

- `main` remains strict read-only at `0d4d621f8a38ddf8eccfa09622bf193687619943`.
- Develop before this run: `451b2f39377653b44fb178e58d86705b6026bef8`.
- Integration target: `develop/pathena-next` only.
- Worker heads reviewed: errors `b8e050c9756299a70e8f5d4df0139ef54a5f08a0`; spec-core `96c8f17d99017060238da27b51f6e59b77b9eafc`; backend `bc622dcb0554d2449183afe2331669ab15c7c8ef`; ui `6558031bb31e5e35f5c8639bf4f5c8591f7fa250`.
- `main` and `bnbgrs/ATHENA` were untouched.

## Integrated this run — UI-GAP-0036 Jobs detail reader keyboard focus

READY UI lineage independently reviewed:

- product `605c63992e112a168ddeda403b561740d524c018`;
- focused regression `8ae0f51e0637e75d7619e7fb9c4fe65679c6f626`;
- exact verified documentation head `8cbec3ef97a13caf626450a0111ee3dc50b262cc`;
- canonical ATHENA Quality `34022762486 = success`.

The product delta is exactly one selector: `QPlainTextEdit#jobDetails:focus` joins the existing canonical accent-border focus block. The regression is exactly one new 10-line focused test. Divergent UI worker history was not imported; the semantic delta and exact test were applied directly to exact Develop.

Develop commits:

- product `c05bcee68b187fcb09ff1cf653e5df3f12ad8e41`;
- focused test `d11284ee89336a059ad04f0b8086a452429a4d00`.

Independent compare `451b2f39377653b44fb178e58d86705b6026bef8..d11284ee89336a059ad04f0b8086a452429a4d00` is ahead 2, behind 0 and changes exactly `src/athena/desktop/pathena_shared_components.py` +1 and `tests/unit/test_pathena_jobs_detail_focus.py` +10.

## Validation and error state

- Worker exact lineage passed canonical Quality `34022762486 = success`.
- Exact-current-Develop global green is not claimed because no post-integration workflow is associated with `d11284ee89336a059ad04f0b8086a452429a4d00` yet.
- `ERR-0017` is OPEN: current Develop imports `ModelInferredMemoryProposal` from `athena.memory.models`, but the model class is missing. Error worker binds this single root cause to mypy failure, pytest collection abort and API/local-install smoke failures.
- Spec/Core provides the bounded compatible exact-green correction: its verified provenance-boundary lineage includes `src/athena/memory/models.py` and focused validation, with Quality `34018695781 = success`; newer synchronized Core head also carries the dependency.
- `ERR-0016` remains `FIXED_PENDING_VERIFY`; its Backend poisoning fix must be reverified after ERR-0017 is repaired.

## UI state

- UI-GAP-0036 is verified and integrated.
- UI-GAP-0037 is implemented but not READY until its own canonical Quality succeeds.
- All eleven screens remain `IMPLEMENTED_PENDING_VISUAL_REVIEW`; no pixel-level MATCH claim is valid while original references are pending.

## Alpha/Beta progress

`docs/development/ALPHA_BETA_PROGRESS.md` was read. It continues to show verified Normal-Hybrid facade/application composition and extensive verified Core/Backend contracts. No whole-file tracker rewrite was attempted because connector retrieval is truncated; this run's evidence is preserved here rather than risking data loss.

## Next integration order

1. Repair `ERR-0017` by composing only the bounded compatible `ModelInferredMemoryProposal` model dependency and its focused provenance validation from exact-green Spec/Core lineage; do not weaken the service import or review/provenance guards.
2. Require focused Personal-Memory tests, mypy/full pytest/API/local-install regressions and canonical Quality on the corrected exact lineage before closing ERR-0017.
3. Reverify Backend ERR-0016 poisoning/oversize semantics on that corrected lineage.
4. Consume UI-GAP-0037 only after its own exact canonical green evidence.

## Persistent release guards

Retain explicit Beta/release regression acceptance for pypdf packaging metadata, fail-closed frozen argv routing and two-EXE split, one Desktop with bounded/non-growing workers, adaptive 2048-context DirectChat budgeting, the Windows lane-lock/SchedulerLaneOwnership/packaged-worker crash cluster, and storage-bootstrap/migration startup signatures.

## Rules retained

No direct work on `main`; no main promotion; no force-push/history rewrite/auto-merge; no Skip/XFail or weaker assertions; no Security/Storage/Windows/Recovery/validator relaxation; no fake success or fabricated provenance.