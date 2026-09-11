# Independent Manual Release-Closure Handoff

Generated: 2026-09-11
Current continuation branch: `manual/independent-release-closure2-20260911`
Parent evidence branch: `manual/independent-release-closure-20260911@a26b026a374ce88f2fb1d87ccdddfb0f15958b40`
Develop baseline used for both: `develop/pathena-next@17d06d258ec2f5841049227504034ef601cdcdf8`

## Ownership / collision rule

This work deliberately does **not** modify `main`, `develop/pathena-next`, `postmerge/errors`, `postmerge/spec-core`, `postmerge/backend`, or `postmerge/ui`. No Storage product code, Qt/UI product code, packaging product code, workflow, or release guard is changed. The continuation contains only diagnostics, evidence contracts and QA coverage. Active workers should cherry-pick only the independent tooling they own after revalidating against their then-current base.

The parent branch remains frozen while its canonical Quality run is in progress. This continuation was branched from that frozen exact head instead of stacking another commit onto an in-flight candidate.

## Storage identity — Backend + Fehlerjäger handoff

`scripts/audit_storage_identity_contract.py` is now strengthened beyond the first detector.

Current machine-readable findings on the inherited Develop baseline:

- `BE-046_POSIX_FD_CLOSED_BEFORE_PATH_UNLINK`
- `BE-046_NONPOSIX_PATHNAME_UNLINK_AFTER_IDENTITY_CHECK`
- `BE-052_PREFLIGHT_IDENTITY_NOT_BOUND_TO_WRITER_OPEN`
- `BE-052_FILESET_SIDECAR_ATTESTATION_DROPPED_BEFORE_WRITER`

The fourth finding incorporates the Fehlerjäger refinement from current ERR-0035 evidence: read-only recovery inspection attests WAL/SHM presence, but `SQLiteDatabase.start()` discards the preflight result and opens the later writer independently. The audit now returns source file/line evidence plus six explicit acceptance cases:

1. POSIX same-parent target replacement after object validation;
2. Windows same-parent target replacement;
3. Windows parent-directory substitution;
4. WAL appears after preflight;
5. SHM is replaced after preflight;
6. primary database is replaced after preflight.

Required closure remains product-owned by Backend. BE-046 must bind actual filesystem object identity through the destructive release. BE-052 must preserve or fail-closed revalidate the identity/snapshot of the primary database plus WAL/SHM through writer establishment. This branch does not implement competing Storage code.

Continuation Storage commit: `c673b539bd56aa8dc196cd9f9f43e7688abf7ba1`.

## 11-screen UI evidence — UI bot handoff

The existing Markdown-manifest validator remains available. New continuation tool:

`scripts/validate_ui_pair_evidence.py`

It defines the evidence contract for a real per-slot verdict rather than inferring visual status from QSS/code/tests:

- exactly slots 01–11 in order;
- `MATCH`, `CLOSE` or `GAP` require both the original reference and exact runtime render to have been opened;
- runtime render must carry an exact 40-character commit SHA;
- reference and runtime must identify the same visible state;
- `MATCH` cannot carry visible gaps;
- `GAP` must carry at least one concrete visible gap;
- `VISUAL_READY_11_OF_11` can only become true with eleven verified same-state pairs and no `GAP`/`UNVERIFIED` verdict.

This intentionally does not touch Help/Qt/product presentation, where the UI worker is currently active. It only gives the worker a fail-closed acceptance format that prevents cross-state or stale-SHA visual claims.

Continuation UI commit: `c692115f72b62723fcfc73d9473845f0b8db5093`.

## Windows / packaging / runtime — Integrator + Backend handoff

The existing repository-level contract validator remains available. New continuation tool:

`scripts/validate_windows_exact_sha_evidence.py`

It validates exported native-Windows Actions evidence and rejects:

- a run for any SHA other than the requested exact 40-character candidate SHA;
- workflow status other than `completed`;
- workflow conclusion other than `success`;
- missing or non-success `Windows path safety` job;
- missing/non-success required Windows release steps.

Required Windows steps include native active-state locality, deterministic locality, Windows Storage paths, durable filesystem, API runtime boundaries, Core/API ownership, packaged runtime contracts, adaptive chat reserve, restart smoke, pypdf packaging and final release-guard enforcement.

This closes an evidence-quality gap: a static packaging contract or a green historical Windows run can no longer be mistaken for native evidence for a different current candidate SHA. It does not itself build an EXE or replace real Windows runtime acceptance.

Continuation Windows commit: `c3c1b933d797c736dc785da76b609174a901904c`.

## QA coverage

`tests/qa/test_manual_release_closure.py` now covers both generations of tooling. New assertions prove:

- the refined BE-052 WAL/SHM continuity finding and acceptance-case set are emitted;
- one valid same-state UI pair is counted without overstating 11/11 readiness;
- a cross-state UI `MATCH` is rejected;
- a complete native-Windows step set for an exact SHA is accepted;
- an otherwise-green Windows evidence packet for the wrong SHA is rejected.

QA coverage commit: `aafc3adb4db23ef8168ace0a6b1cc9940720c470`.

## Integration guidance

Do not merge either manual branch wholesale merely because CI is green. Consume the pieces by ownership:

- Backend/Error: Storage audit IDs, evidence lines and acceptance cases;
- UI: pair-evidence validator/schema only; keep product Help/Qt work on `postmerge/ui`;
- Integrator/Backend: static Windows contract validator and exact-SHA evidence validator.

Revalidate every selected piece against the then-current Develop/worker head. Once Backend actually closes BE-046/BE-052, update or remove the diagnostic canary assertions rather than preserving signatures of the old defect.
