# pATHENA Backend & Systems Handoff

## Baseline

- Integration target: `develop/pathena-next@eab481a0901423ee5821e9d4101f0a0bbf804ef8`.
- Exact Develop canonical Quality: `34662951154 = SUCCESS`.
- Worker branch: `postmerge/backend`.
- Product candidate: `b595c960a747d9805b0865ea9f7237094318b706`.
- `main` and `bnbgrs/ATHENA` remain strictly read-only and untouched.

## Selected backend slice

Area: `BE-046 / ERR-0033` emergency-reserve POSIX physical-reclamation and release-accounting continuity.

Fresh current-lineage Error/Integrator evidence reproduced that pathname deletion alone did not prove physical reclamation while foreign descriptors or alternate hardlinks could retain the inode. Product commit `b595c960a747d9805b0865ea9f7237094318b706` hardens the POSIX release path without weakening Storage, Recovery, Security, allocation or accounting invariants.

Changed product/test files relative to the candidate base:

- `src/athena/storage/emergency_reserve.py`
- `tests/unit/test_emergency_reserve.py`

No `main`, ATHENA, Security, TOR, Provider, UI, packaging or unrelated persistence code changed.

## Exact verification evidence

Exact candidate `b595c960a747d9805b0865ea9f7237094318b706` completed:

- canonical Quality `34662086156 = SUCCESS`;
- Core Focused Candidate `34662086028 = SUCCESS`;
- canonical storage/Windows/path-safety/local-install/Ruff/mypy/full-pytest gates therefore completed green on the exact candidate SHA.

Current Develop `eab481a0901423ee5821e9d4101f0a0bbf804ef8` completed canonical Quality `34662951154 = SUCCESS` and differs from the candidate base by the Integrator-owned CI commit `ci(storage): add exact focused candidate lane`; it does not integrate the Backend product candidate.

The active product diff against current Develop remains bounded to `src/athena/storage/emergency_reserve.py` and `tests/unit/test_emergency_reserve.py`. The worker history is intentionally not an integration unit; Integrator should import/reapply only this bounded exact-green product/test delta onto current Develop and retain the newer Develop CI workflow.

## Retained invariants

- release remains fail-closed when reserve identity cannot be proven;
- same-parent reserve-file substitution is rejected before destructive unlink of a foreign file;
- additional hardlinks prevent a false physical-reclamation claim;
- an externally held descriptor cannot cause released-byte accounting to claim physical reclamation that cannot be proven;
- existing parent-directory substitution protection remains intact;
- no physical-allocation, Storage, Recovery or Security guard was relaxed;
- no Skip/XFail or assertion relaxation was introduced.

## Verification / readiness state

- `BE-046` POSIX reclamation/accounting sub-slice: `INTEGRATOR_READY` at exact product SHA `b595c960a747d9805b0865ea9f7237094318b706`.
- This does **not** close BE-046 globally. Native-Windows parent/target HANDLE identity continuity through the destructive release step remains a separate open sub-slice and still requires native-Windows adversarial proof.
- `BE-052 / ERR-0035` remains separate and untouched by this candidate; no pathname-only SQLite revalidation is accepted as a fix.

## Integrator handoff

READY for conservative integration of the bounded BE-046 POSIX product/test delta from exact-green candidate `b595c960a747d9805b0865ea9f7237094318b706` onto current `develop/pathena-next@eab481a0901423ee5821e9d4101f0a0bbf804ef8`.

Prerequisites:

1. preserve current Develop's newer `.github/workflows/storage-focused-candidate.yml`;
2. import only the bounded emergency-reserve product/test delta, not the worker's historical ancestry;
3. run the new Storage Focused Candidate lane and canonical Quality on the resulting exact integration SHA;
4. do not mark global BE-046 CLOSED until the native-Windows identity-continuity sub-slice is independently exact-tested and integrated.

## Next backend slice

After Integrator consumes this candidate, select the highest currently authoritative Backend/System gap. Do not rework the exact-green POSIX reclamation slice absent a fresh regression. If the required native-Windows adversarial path is available, continue the disjoint Windows portion of BE-046; otherwise move to the next safely testable independent backend gap rather than repeatedly re-analyzing it.
