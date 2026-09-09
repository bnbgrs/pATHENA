# pATHENA Feature Integrator Handoff

## Current source of truth

- Develop baseline before this integration: `8b6023b64991489f3570f9c99a0feb89f5bbe500`.
- Worker heads reviewed this run: errors `7e83a9ad6045f547ef1670431d7af6775a21c0b3`; spec-core `850b631007ba3f359b9b16c619c692d853d75663`; backend `0f07617e6982f029eb6210e7b7f5a28fab853ffe`; UI `4fad529c471c783e62d6029d6ea72a2147727196`.
- Immediately before Develop mutation, exact baseline `8b6023b64991489f3570f9c99a0feb89f5bbe500` had no associated Actions run and therefore no queued/in-progress canonical Quality.
- UI exact-head Quality `34325659408` remains pending, so the current UI candidate is not READY.
- Backend current head remains non-READY on exact-head Quality evidence; schema/WAL/storage work remains held conservatively.
- Spec/Core and Error handoffs did not provide a new promotion-qualified product slice.
- `main` remains read-only and was not mutated.

## Progress this run — canonical pypdf packaging guard

No Worker slice was READY, so exactly one collision-free cross-cutting release-guard slice was implemented.

The existing fail-closed `athena-packaging-smoke --json` check is now executed by the canonical `Local install smoke` job after lock validation and the disposable Core/API restart smoke. This makes missing `pypdf` distribution metadata a canonical Quality failure instead of leaving the packaging guard callable but unenforced.

The workflow continues to use `uv run --locked --extra dev`; dependency resolution, storage/recovery/security behavior, Windows path checks, Qt/UI behavior, model/chat behavior, process topology, and release trigger semantics are unchanged. No Quality trigger was broadened: the workflow still runs on `main` push and pull requests only.

## Verification / invariants

- Existing focused implementation tests for `src/athena/packaging_smoke.py` remain the product-level contract; no test was deleted, skipped, xfailed, or weakened.
- Canonical workflow now invokes `uv run --locked --extra dev athena-packaging-smoke --json` in the existing local-smoke lane.
- The guard remains fail-closed: nonzero exit from missing/invalid `pypdf` metadata fails the job.
- Active Backend and UI product files are untouched.
- No Storage, Recovery, Security, database migration, worker scheduling, frozen argv, two-EXE, or Windows lane-lock invariant was relaxed.

## Quality / promotion state

- Exact-current Develop Quality must still be established before any Beta/release-ready claim.
- Direct pushes to `develop/pathena-next` do not currently trigger canonical Quality under `.github/workflows/quality.yml`; this run did not alter that trigger policy.
- UI `4fad529c471c783e62d6029d6ea72a2147727196` remains held while Quality `34325659408` is pending.
- Backend remains held until exact-head Ruff/full-pytest/schema-WAL evidence is green.
- Historical Windows/runtime failure signatures remain pre-Beta regression guards unless reproduced on an exact current SHA.

## Tracker / visual state

No visual product mutation was made. No screenshot-level `MATCH` claim is introduced. Existing 11-screen and Visual Gap states remain authoritative until updated by exact current evidence. No percentage or completion state is fabricated.

## Next integration order

1. Re-check exact-current Develop Quality before every mutation; freeze Develop whenever an exact-current canonical run is queued/in-progress.
2. Consume UI only if its current exact-head Quality finishes green without a superseding Worker commit and the bounded delta remains compatible with Develop.
3. Keep Backend schema/WAL/storage integration conservative until exact-head Quality is green.
4. Reconcile progress documentation only when doing so cannot supersede an active exact-Develop gate.
5. Preserve explicit Beta/release acceptance for pypdf packaging metadata; fail-closed frozen argv; Desktop/Worker two-EXE split; exactly one Desktop with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock cluster; and duplicate-column/Core-startup/storage-bootstrap signatures.

## Rules retained

No `main` mutation or promotion; no force push/history rewrite/auto-merge; no Skip/XFail; no weaker assertions; no Security/Storage/Recovery/Windows/validator relaxation; no fabricated evidence.
