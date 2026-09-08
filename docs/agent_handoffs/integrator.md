# pATHENA Feature Integrator Handoff

## Current branch state

- `main` remains strict read-only at `0d4d621f8a38ddf8eccfa09622bf193687619943`.
- Develop before this run: `cbc66ecbe8b6080e7e955471a5d7131e2ec84bf9`.
- Integration target: `develop/pathena-next` only.
- Worker heads reviewed: errors `92893883bb34aff3aea2478c177ce67ce87877da`; spec-core `af1f9da019fbee21984cf62fb77a2e8bbacaed5b`; backend `e4370a46bd42785aaea0f5c1806d8d79ced3eb7e`; UI `0bc6947afecd0def64c2cbc0f6bdc1c5b97fc723`.
- `main` and `bnbgrs/ATHENA` were untouched; no force update, rebase, history rewrite, auto-merge or main promotion was used.

## Progress this run — UI-GAP-0014 no-model persistence freshness

Current Backend Quality `34211221630` and current UI Quality `34211448894` were still pending/in-progress, so neither current worker head was READY. The hard progress rule therefore consumed one previously deferred exact-green bounded slice from the canonical Alpha/Beta tracker.

- UI-GAP-0014 product lineage culminates at `e1218685577230fa6ad190291ad0f626912853ac`.
- Focused test commit: `ce7ae251f5d7b8548a21abde6c67cbd2fafa9f24`.
- Exact successful worker head: `3d3ac638ce35c2bd149cea2358ef726f243244f0`; ATHENA Quality Gate `33897120327 = success`.
- Independent Develop review confirmed the current branch still reported `pathenaRuntimeFreshness=fresh` when `_selected_model()` returned `None`, while the verified worker contract requires fail-closed `unavailable` with unchanged visible copy and `idle` UI state.
- Develop product integration commit: `50f80fada32bcf110a329e217a8878b2cdd55474`.

The Develop mutation is exactly one semantic line in `src/athena/desktop/pathena_settings_runtime.py`: `Per-model settings · choose a model` now carries freshness `unavailable` rather than `fresh`. No persistence implementation, storage format, model selection, provider, transport, Security, Recovery, scheduler/worker, packaging or Windows-runtime semantics changed.

The worker focused test itself was not imported because it contains `pytest.importorskip("PySide6")`, while Integrator policy forbids introducing Skip/XFail behavior. Its exact worker lineage nevertheless provides canonical green execution evidence for the product contract; no test or guard was weakened on Develop.

## Verification state

- UI-GAP-0014 exact worker lineage: Quality `33897120327 = success` on exact `3d3ac638ce35c2bd149cea2358ef726f243244f0`.
- Current Develop product descendant after integration: `50f80fada32bcf110a329e217a8878b2cdd55474` before this documentation commit.
- Local checkout/test execution remained DNS-blocked (`Could not resolve host: github.com`), so no exact-current-Develop global-green claim is made.
- No Skip/XFail, assertion weakening or guard relaxation was introduced on Develop.

## Other worker state

- Error head `92893883bb34aff3aea2478c177ce67ce87877da`: ERR-0025 remains shared pytest-failure investigation; ERR-0023 remains FIXED_PENDING_VERIFY.
- Spec/Core head `af1f9da019fbee21984cf62fb77a2e8bbacaed5b`: no new bounded Core slice consumed.
- Backend head `e4370a46bd42785aaea0f5c1806d8d79ced3eb7e`: exact Quality `34211221630` pending at review; WAL runner/adapter changes held.
- UI head `0bc6947afecd0def64c2cbc0f6bdc1c5b97fc723`: exact Quality `34211448894` in progress at review; current branch delta contains Jobs verification-failure copy but its new focused test uses `pytest.importorskip`, so it is not Integrator-ready under the no-Skip rule.

## UI / Alpha-Beta state

- Eleven-screen status remains implemented pending visual review; no MATCH claim is made without original-reference evidence.
- `UI-GAP-0014` is now integrated on Develop with exact-green worker evidence; the Alpha/Beta tracker should be updated from `IMPLEMENTED_PENDING_VERIFY` to `VERIFIED` with this integration SHA.
- No completion percentage is inferred.
- No historical Windows/runtime crash class is reopened without exact-current reproduction.

## Next integration order

1. Consume exact-current Backend/UI Quality results when completed and reject any slice that introduces Skip/XFail or weakens guards.
2. Obtain exact-current-Develop canonical verification on a descendant carrying `50f80fada32bcf110a329e217a8878b2cdd55474`; close ERR-0023 only on exact green evidence.
3. Independently review exactly one next deferred exact-green Settings slice (`UI-GAP-0011`, `0012`, `0015`, `0016`, `0017`, `0018`, or `0020`) or a current exact-green Worker successor.
4. Preserve the release crash-regression matrix before any Windows candidate or promotion claim.

## Persistent release guards

Retain explicit Beta/release regression acceptance for pypdf packaging metadata; fail-closed frozen argv routing and Desktop/Worker two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context DirectChat budgeting; Windows lane-lock `PermissionError` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError`; and storage-bootstrap/migration startup signatures including duplicate-column failures.

## Rules retained

No direct work on `main`; no main promotion; no force-push/history rewrite/auto-merge; no Skip/XFail or weaker assertions; no Security/Storage/Windows/Recovery/validator relaxation; no fake success or fabricated provenance.
