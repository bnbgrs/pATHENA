# UI Reference Identity Validator — 2026-09-14

## Purpose

Prepare the fail-closed visual-evidence invariant discovered while closing ERR-0059: eleven captured files are not sufficient proof that the eleven authoritative human reference identities were captured in the correct states.

Base: `develop/pathena-next@b3766e0c690aac4db0567c63a3e2886f8fbce368`.

This branch is intentionally staged without a PR while current Develop qualification lanes are active.

## Canonical slot identities

1. ComfyUI
2. PALLAS
3. Settings
4. Help
5. Dark Workspace / Evidence
6. Jobs
7. Command Palette
8. System
9. Research
10. Light Workspace
11. Local Memory

## Validator contract

`scripts/validate_ui_pair_evidence.py` requires every evidence row to bind its slot to the canonical reference identity. A rendered pair additionally requires the runtime render identity to equal the same canonical identity, the reference and runtime state strings to match, and the runtime render to carry an exact 40-character commit SHA.

A MATCH/CLOSE/GAP verdict is rejected unless the original and runtime render are both opened, identity-aligned and state-aligned. Visual readiness remains false when any slot is unverified or has a gap.

## Regression

`tests/qa/test_ui_pair_reference_identity.py` locks the full eleven-slot mapping and explicitly proves that slot 10 rejects `Files` when the required identity is `Light Workspace`, including a false-MATCH case with otherwise matching state text and a valid-looking SHA.

## Consumption rule

After the active current-Develop PRs settle, reconstruct this exact tooling on the then-current green Develop head and run canonical Quality before integration. This is evidence tooling only; it must not fabricate missing runtime states, auto-promote baselines, change comparator thresholds or claim any visual MATCH.
