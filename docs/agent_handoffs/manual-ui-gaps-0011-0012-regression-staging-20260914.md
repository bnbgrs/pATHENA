# UI-GAP-0011 / UI-GAP-0012 regression staging handoff

Date: 2026-09-14
Base: `develop/pathena-next@a2dfc6b381ead94996f319ca06fc65e25992fb70`
Status: staging only; product code is unchanged.

## Audit finding

Current `SettingsRuntimeController` already initializes all visible runtime states fail-closed before the first Core snapshot. Provider, connection, persistence, and detail labels use `pathenaRuntimeFreshness=unavailable`; provider/network/persistence begin in `idle`; network scope is explicitly `unavailable` and Internet state is not inferred. The initial persistence copy is `Per-model settings · not saved yet` and is not represented as fresh state.

The Alpha/Beta tracker still lists UI-GAP-0011 and UI-GAP-0012 as `IMPLEMENTED_PENDING_VERIFY`. Historical worker branches were not discoverable by current branch/PR search, so this staging candidate records only assertions directly supported by today's runtime contract.

## Test scope

`tests/unit/test_pathena_settings_initial_truth.py` adds two no-skip Qt regressions:

1. pre-first-snapshot provider/network truth fails closed to unavailable freshness and never infers Internet state;
2. initial persistence metadata is idle and unavailable, with accessible text matching the rendered state.

## Integration rule

Do not mark the tracker VERIFIED from inspection alone. Reconstruct these blobs on the exact newest canonical-green Develop after active integrations, run the applicable focused UI gate and canonical Quality, then update tracker evidence only after exact-head success.