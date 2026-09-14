# Integrator maintenance hardening — current Develop reconstruction

Date: 2026-09-14
Owner: Integrator / release-readiness maintenance
Target: `develop/pathena-next`
Base at reconstruction: `fa0ac0e9bc4545b00de1d02987fb5c0a5fdf96bd`

## Purpose

Reconstruct the independently reviewed maintenance repairs from #140, #141 and #142 directly on the current Develop line after #145 and #147 were integrated.

No historical merge, rebase, force-push or product-runtime mutation is used. The nine functional blobs are copied byte-for-byte from #148; only this handoff is current-lineage documentation.

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

## Behavior

### Local Quality

- lock validation before execution;
- all Python quality commands through locked `uv run --locked --extra dev --extra desktop`;
- repository-root anchoring;
- isolated Desktop API controller pytest plus remaining canonical suite;
- fail-fast by default, explicit `--keep-going`, deterministic `--dry-run`;
- fail closed when `uv` cannot execute.

### Coordination Guard

- commit path arrays are non-empty and non-blank;
- changed candidate SHA requires at least one commit;
- unchanged candidate SHA cannot carry commits;
- final supplied commit SHA must equal the declared candidate SHA.

### Promotion Guard / workflow

- exact trigger SHA checkout with identity proof;
- pinned checkout/setup-python/runtime inputs;
- no persisted checkout credentials;
- explicit `--actual-ref` required;
- required workflow must be a non-symlink regular file;
- forbidden broken symlinks fail closed.

## Collision boundary

No Core/Knowledge product logic, Storage/WAL, UI/PALLAS, provider, scheduler, Security implementation or user-facing behavior is changed. #147's Core Focused workflow is retained from current Develop and is not modified by this slice.

## Qualification rule

Require current Develop `fa0ac0e9...` post-merge canonical green and fresh exact-head canonical green for this reconstruction before integration. No Skip/XFail, threshold relaxation or automatic merge.
