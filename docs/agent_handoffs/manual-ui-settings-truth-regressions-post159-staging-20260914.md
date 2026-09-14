# Settings truth regressions — post-#159 staging

Status: STAGED_NOT_QUALIFIED

Base: `develop/pathena-next@4634af7ab0db315574e692c57635585d3a3b3bf6`

## Scope

Regression-only consolidation for tracker gaps UI-GAP-0011, UI-GAP-0012 and UI-GAP-0020. No production file changes are included because current `pathena_settings_runtime.py` already exposes the required fail-closed semantics.

## Contracts

- before the first Core snapshot, provider and local-Core states remain `idle` but freshness is `unavailable`;
- no Internet state is inferred from an unavailable local-Core snapshot;
- initial per-model persistence state reports `unavailable` freshness;
- a model-list refresh failure preserves the known provider identity as `last known ready` while the failure detail remains an error with unavailable freshness.

## No-Skip correction

The earlier UI-GAP-0020 staging test used `pytest.importorskip("PySide6")`. That was removed. Both files import PySide6 directly so missing desktop runtime support fails the candidate rather than silently skipping the contract.

## Integration boundary

Do not open/merge this staging candidate while PR #160 is active. After the active serial integration is resolved and Develop is canonical-green, reconstruct onto the exact new Develop head, run UI Focused plus canonical Quality, then update the Alpha/Beta tracker only after exact-green integrated evidence exists.
