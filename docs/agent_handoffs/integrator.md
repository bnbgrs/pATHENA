# Post-Merge Feature Handoff - Integrator

Generated: 2026-09-10T19:49Z
Branch: `develop/pathena-next`
HEAD at run start: `effe7fb43246d4f3c4d9ac0f2f5d363c2135bb36`

## Current evidence

- `main` and `bnbgrs/ATHENA` remain read-only and untouched.
- Current worker heads reviewed: Errors `aa603d87200b937efce37fcabfa1195a338b78a5`, Spec/Core `b8df82b23583d42a8d5ae8f387aea0fbd0e7859e`, Backend `baae5dd42195eea1e2a7320d1be813431a3beecf`, UI `2ede7add4d70ee9f11ef2e05103504e9a1838a2a`.
- Exact Develop canonical Quality `34516879382@effe7fb43246d4f3c4d9ac0f2f5d363c2135bb36 = FAILURE`. Python 3.12 quality, Linux storage regressions and Local install smoke are SUCCESS; Windows path safety failed specifically at `Run Windows storage path regressions`.
- The failing Develop commit changed no production code or test assertions; it only added `test_durable_fs.py` and `test_durable_fs_parent_identity.py` to the native Windows storage command plus this handoff.
- Errors classifies the newly exposed native-Windows durable-filesystem failure as `ERR-0034 / P1`; `ERR-0033 / BE-046` remains separately Backend-owned and is not attributed to this CI-only regression.
- Backend head `baae5dd4...` contains a bounded CI-only candidate that separates the Windows-applicable durable-fs subset from POSIX-only tests. The candidate has no exact-head canonical Quality run, so its broad worker history remains non-promotable; only the bounded workflow delta is reconciled against current Develop.
- `ERROR_LEDGER.md` and `ALPHA_BETA_PROGRESS.md` are not present under those exact names in the current Develop tree and are not synthesized as source of truth.
- UI source of truth remains `docs/ui/11_SCREEN_REFERENCE_MANIFEST.md` and `docs/ui/VISUAL_GAP_LEDGER.md`. All 11 slots remain `IMPLEMENTED_PENDING_VISUAL_REVIEW`; screenshot-level `MATCH` is unproven.

## Bounded blocker fix — isolate POSIX-only durable filesystem tests from native Windows

`tests/unit/test_durable_fs.py` contains tests explicitly named `test_posix_*` that force the POSIX implementation path and exercise POSIX-only `dir_fd` / directory-fsync semantics. `tests/unit/test_durable_fs_parent_identity.py` is entirely POSIX-gated (`os.name != "posix"` skips every test). Running both modules wholesale inside `windows-latest` therefore mixed platform-specific POSIX contracts into the native Windows release lane.

The canonical Windows workflow now:

1. Restores `Run Windows storage path regressions` to the previously green Windows-applicable storage set.
2. Adds a dedicated `Run Windows durable filesystem regressions` step executing `tests/unit/test_durable_fs.py -k "not test_posix"`.
3. Leaves `test_durable_fs_parent_identity.py` in the Linux storage regression lane, where its parent-directory identity contract is substantive.

No test, assertion, production Storage/Recovery/Security code, HANDLE-bound rename behavior, reparse/symlink rejection, or durability invariant is weakened. No Skip/XFail is added. This is a platform-selection correction for the exact failing canonical lane, not a closure claim for `ERR-0033 / BE-046`.

## Persistent release guards

- pypdf packaging remains fail-closed and selected on Linux and Windows canonical lanes.
- Frozen argv and Desktop/Worker two-EXE contracts remain selected in native Windows Quality.
- Exactly one Desktop instance with bounded worker ownership/lifecycle remains guarded.
- Adaptive 2048-context Chat reserve remains selected in native Windows Quality.
- Windows lane-lock/path-safety remains fail-closed.
- Storage-bootstrap, Core-startup and duplicate-column/schema-reinitialization signatures remain selected in Windows Quality.
- Durable filesystem native-Windows behavior remains explicitly tested, while POSIX-only identity contracts remain in Linux storage Quality.

## Next integration

1. Consume canonical Quality on the resulting exact Develop SHA first and freeze Develop while it is queued/in progress.
2. If red, diagnose only the exact failing Windows test/step before any mutation; do not weaken tests or Storage/Recovery/Security behavior.
3. Keep `ERR-0033 / BE-046` Backend-owned unless a fresh bounded current-Develop candidate with focused native-Windows adversarial directory-identity evidence becomes READY.
4. Do not absorb the diverged broad Backend worker history or re-integrate already landed Core/UI/runtime slices.
