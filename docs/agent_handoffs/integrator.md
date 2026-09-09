# pATHENA Feature Integrator Handoff

## Current source of truth

- `main` remains strict read-only at `0d4d621f8a38ddf8eccfa09622bf193687619943`.
- Develop baseline before this integration: `82aaef0caaa90599f530acc84d728b602dee6739`.
- Worker heads reviewed: errors `3318f6cddd9a8d4b455531845ef3291b236839f0`; spec-core `3590faef81e4eabf440e8ed88be96d860a5eef37`; backend `5fb8d5b7b5ee29af09bd70ccde8824633f0e0c8a`; UI `eb04282287fff68bcf764c0b8515c160be31c81b`.
- Exact Develop baseline had no queued/in-progress canonical Quality when mutation eligibility was checked immediately before mutation.
- UI exact-head Quality `34320320195` is in progress; Ruff, mypy, Windows path safety, Linux storage and local-install smoke are green while full pytest is still running. UI-GAP-0004 therefore remains `IMPLEMENTED_PENDING_VERIFY` and was not consumed.
- Backend exact-head lineage remains non-READY because canonical Quality `34311050843` is red on Ruff import sorting in `src/athena/storage/schema.py`; no manual formatter guess was applied.
- Spec/Core has no new product delta from Develop.

## Progress this run — fail-closed pypdf packaging metadata smoke

No Worker slice was READY, so this run used the hard progress rule for one collision-free cross-cutting release path. Added `athena-packaging-smoke`, backed by `src/athena/packaging_smoke.py`, to verify required distribution metadata without importing `pypdf` itself.

The smoke checks `importlib.metadata.version("pypdf")` and fails closed when the distribution metadata is absent, lookup fails, or an empty version is returned. The CLI returns exit code `0` only when required metadata is available and `2` otherwise, with optional `--json` output for packaging/CI consumption. This directly covers the known packaged-runtime crash class where missing pypdf distribution metadata can raise `PackageNotFoundError` before normal document-processing paths are usable.

The slice is file-disjoint from active Backend schema/WAL work and from the current UI composer candidate. It does not change Storage, Recovery, Security, scheduler/worker, model, chat, Qt, or database behavior.

## Focused verification

- New focused test: `tests/unit/test_packaging_smoke.py`.
- Locally executed against the exact new module in isolation: `4 passed`.
- Python compilation of the new module: pass.
- Covered contracts: installed pypdf metadata reports version; missing metadata is a FAIL; CLI returns failure for missing metadata; non-canonical distribution names fail closed.
- No Skip/XFail, weaker assertion, fake success path, or guard relaxation was introduced.

## Quality / promotion state

- Exact-current Develop canonical Quality is required after this integration before any further Develop mutation or Beta/release-ready claim.
- UI current candidate remains held until its exact-head Quality completes without superseding commits.
- Backend remains held until exact Ruff/full-pytest evidence is green.
- Historical Windows/runtime signatures remain release guards only unless reproduced on an exact current SHA.

## Tracker / visual state

The current 11-screen manifest and Visual Gap Ledger were read from Develop. All eleven screens remain `IMPLEMENTED_PENDING_VISUAL_REVIEW`; no screenshot-level `MATCH` claim is made. The current Develop ledger contains UI-GAP-0001 through UI-GAP-0003 as fixed and retains `VISUAL_REFERENCE_PENDING`. The UI worker has a newer UI-GAP-0004 composer-scale candidate, but it is not integrated while exact-head Quality is running.

`ALPHA_BETA_PROGRESS.md` was reviewed. No percentage or completion state is fabricated. Tracker reconciliation for this packaging release guard should be performed only after exact-current Develop CI completes so a documentation-only commit cannot supersede a running gate.

No separate current `ERROR_LEDGER.md` artifact was discoverable from repository code search in this run; no error state was invented from that absence.

## Next integration order

1. Re-check exact-current Develop CI and keep Develop frozen while a canonical gate is queued/in-progress.
2. If UI `eb04282287fff68bcf764c0b8515c160be31c81b` finishes exact-green without a superseding commit, independently review and integrate only its bounded composer-scale product/test/docs delta.
3. Keep Backend schema/WAL work conservative until the exact Ruff 0.15.22 formatter result and full-pytest lineage are green; never guess import ordering.
4. Reconcile `ALPHA_BETA_PROGRESS.md` after exact-current Develop CI permits a safe documentation update.
5. Before Windows Beta/release, retain explicit acceptance for pypdf packaging metadata; fail-closed frozen argv; Desktop/Worker two-EXE split; one Desktop with bounded workers; adaptive 2048-context DirectChat budgeting; Windows lane-lock ownership cluster; and duplicate-column/Core-startup/storage-bootstrap signatures.

## Rules retained

No main mutation or promotion; no force push/history rewrite/auto-merge; no Skip/XFail addition; no weaker assertions; no Security/Storage/Recovery/Windows/validator relaxation; no fake success or fabricated provenance.
