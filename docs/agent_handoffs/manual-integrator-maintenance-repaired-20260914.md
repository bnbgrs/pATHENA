# Integrator maintenance hardening — repaired Develop reconstruction

Date: 2026-09-14
Owner: Integrator / release-readiness maintenance
Target: `develop/pathena-next`
Base at reconstruction: `ee8aa791742f7cbdd056532e66a50da14c461c4a`

## Purpose

Reconstruct the three independently reviewed maintenance repairs from PRs #140, #141 and #142 directly on the repaired Develop line after Claim-inspection recovery #145.

No historical merge and no force-push is used. The functional file blobs are copied byte-for-byte from the previously verified consolidation #144; only this handoff is new so it can describe the current lineage truthfully.

## Included functional blobs

- `.github/workflows/promotion-readiness.yml` — `70197101240aab6d086b961836ddba72fd9c2ba7`
- `scripts/coordination_guard.py` — `8d163172fbdfa72a50452baff8b7067da78fdab5`
- `scripts/promotion_guard.py` — `367d659e9a41518fcb5ad4570f5af3da8543932e`
- `scripts/quality.py` — `78a63ba093c65130c98546ad36cd9ede0a3f3e58`
- `tests/unit/test_coordination_guard.py` — `f0c1befe5fecab325c8d2a5d5aee04ee1a85b754`
- `tests/unit/test_local_quality_runner.py` — `db936babf1594450754d342d3ad8fec1ac6ee195`
- `tests/unit/test_promotion_guard.py` — `c495fd584208c0e6aedc5ab18a1d93fd4dd446cf`
- `tests/unit/test_quality_gate_config.py` — `4e3adf1d95d7e873c60eef9e54d5ce0b4e7e64a3`
- `tests/unit/test_quality_script.py` — `63cf5dc108e6eb7c159c522cf6047d890b666ddc`

## Provenance / prior evidence

The same functional behavior was already qualified independently before consolidation:

- local quality current-base #140 exact head `7aa5f19c...`, canonical run `34792310407 = SUCCESS`;
- coordination guard #141 exact head `e548075c...`, canonical run `34792553351 = SUCCESS`;
- promotion hardening #142 exact head `1228adab...`, canonical run `34792653158 = SUCCESS`.

The first consolidation #144 was intentionally blocked because its then-current parent `5024a7c2...` was red for an unrelated Claim-inspection composition defect. Recovery #145 fixed that defect and was merged only after exact-head canonical run `34816805647 = SUCCESS`, producing repaired Develop merge SHA `ee8aa791...`.

## Behavior retained

### Local Quality

- validate the lock before execution;
- run canonical Python quality commands through locked `uv run --locked --extra dev --extra desktop`;
- anchor execution to repository root;
- retain the isolated Desktop API controller pytest process plus remaining suite;
- preserve fail-fast / `--keep-going` and dry-run visibility;
- fail closed if `uv` cannot execute.

### Coordination Guard

- commit path arrays must be non-empty and non-blank;
- changed candidates cannot provide zero commits;
- unchanged candidates cannot provide commits;
- final supplied commit SHA must equal declared candidate SHA;
- existing claim/classification semantics remain unchanged.

### Promotion Guard / workflow

- bind execution to exact trigger SHA and prove checkout identity;
- pin action/runtime inputs and disable persisted checkout credentials;
- require explicit actual-ref evidence;
- required canonical workflow must be a real non-symlink file;
- broken forbidden legacy symlinks fail closed.

## Collision boundary

No product runtime, Storage/WAL, Core/Knowledge, UI/PALLAS, provider, scheduler or Security implementation is changed. The separate Core Focused selector/environment repair is outside this slice.

## Qualification rule

Do not integrate solely from historical evidence. Require:

1. post-merge canonical Quality on base `ee8aa791...` to finish green;
2. fresh exact-head canonical Quality for this reconstructed candidate;
3. a final Develop/worker drift check immediately before merge.

No Skip/XFail, no threshold relaxation, no automatic merge.
