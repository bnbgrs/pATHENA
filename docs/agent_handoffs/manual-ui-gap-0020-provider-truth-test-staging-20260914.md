# UI-GAP-0020 provider-truth regression — staging handoff

Date: 2026-09-14
Base: `develop/pathena-next@a2dfc6b381ead94996f319ca06fc65e25992fb70`
Status: staging only; reconstruct on the next canonical-green Develop before integration.

## Finding

The product behavior is already present in the current Settings runtime. When the model list refresh is unavailable but the local Core snapshot still carries a known provider, Settings renders that provider as last-known state rather than replacing provider truth with an unavailable/unknown claim.

The historical regression `test_model_snapshot_failure_keeps_provider_as_last_known` existed in `tests/unit/test_pathena_settings_provider_detail_state.py`, but neither that test name nor its key `LM Studio · last known ready` assertion exists in the current repository test corpus.

## Scope

This staging branch adds one regression test only. It changes no product code and does not reintroduce the two unrelated historical provider-detail tests.

The regression asserts:

- provider identity remains `LM Studio` after model-list refresh failure;
- provider status is explicitly labelled `last known ready`;
- provider UI state is idle, not a fresh success claim;
- freshness is unavailable;
- the model-list failure remains visible as an error detail;
- accessible text matches the rendered provider truth.

## Integration rule

Do not merge this staging branch directly if Develop advances. Reconstruct the two staging blobs on the exact newest canonical-green Develop, qualify the focused UI test plus canonical Quality, then update `UI-GAP-0020` tracker evidence only after the regression is green.