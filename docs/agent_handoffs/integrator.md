# pATHENA Feature Integrator Handoff

## Current branch state

- `main` remains strict read-only at `0d4d621f8a38ddf8eccfa09622bf193687619943`.
- Develop before this run: `e16a4d14f367f29e29deb794d0e1581b41226a49`.
- Integration target: `develop/pathena-next` only.
- Worker heads reviewed: errors `921940cc2c5b76b24f3622201da473421a065c9a`; spec-core `0d0fe488fcf52e7bc89ec6e5feeb373aec93f823`; backend `c964506791611da78dd3959aa64c12b2614e253b`; UI `352b4c72c39d5cafe866c604a050a1b93df71940`.
- `main` and `bnbgrs/ATHENA` were untouched; no force update, rebase, history rewrite or auto-merge was used.

## Integrated this run — Exhaustive Research §68 acceptance

The exact-green Spec/Core §68 acceptance was independently reviewed and integrated onto current Develop as a bounded test-only slice.

- Exact repair commit: `95ad54ce07af61d79baf31fbcb7f07ab2f6ff4f6`.
- Exact canonical ATHENA Quality: `34166054576 = success`.
- Exact handoff descendant: `80915e1e8c7dff42fc998e9035df41273bdb08ca`, Quality `34166094972 = success`.
- Develop integration commit: `31310a6c449b50034378adb02bdd055e69e089c5`.
- Added only `tests/unit/test_exhaustive_research_resume.py`; no production file changed.
- The acceptance exercises the real persistent AthenaApplication, five real Source capture/preprocessing paths, Research parent/child orchestration, persisted ResearchWorkItems, SourceAnalysis final artifacts/content hashes and Finding payloads. It stops after exactly 3/5 successful sources, requires coverage 0.6, reconstructs the application against the same durable root, proves the first three identities/content hashes/Finding payloads survive, completes the remaining two sources, and requires coverage 1.0 with five unique work items, analysis jobs, final artifacts and Finding payloads.
- Fixture dispatch preserves `resume-source-*` identity through MAP and reduce/final synthesis responses; no production path, persistence, provenance, Recovery, Security, Storage, Search or model-selection semantics changed.

## Verification state

- Spec/Core repair `95ad54ce07af61d79baf31fbcb7f07ab2f6ff4f6`: canonical Quality `34166054576 = success`.
- Spec/Core handoff descendant `80915e1e8c7dff42fc998e9035df41273bdb08ca`: canonical Quality `34166094972 = success`.
- Current Develop integration head `31310a6c449b50034378adb02bdd055e69e089c5` has no associated exact workflow run yet; no global-green or promotion-ready claim is made.
- Current UI head `352b4c72c39d5cafe866c604a050a1b93df71940` has Quality `34174030199` pending and is not READY.
- No Skip/XFail, weakened assertion, guard relaxation or fake production path was introduced.

## Error state

- `ERR-0020` is FIXED by exact-green §68 evidence; no current production defect was established by that failure lineage.
- Historical Windows/runtime crash classes are not reopened absent exact-current reproduction and remain mandatory Beta/release regression guards.

## UI / Alpha-Beta state

- Eleven-screen implementation remains `IMPLEMENTED_PENDING_VISUAL_REVIEW`; original reference payloads remain unavailable and no screenshot-level `MATCH` claim is made.
- UI-GAP-0072 remains integrated and exact-green on its worker evidence.
- Current UI successor is not READY while its exact Quality is pending.
- `docs/development/ALPHA_BETA_PROGRESS.md` remains authoritative. The connector exposed only a truncated large-file view in this run, so no destructive partial replacement was performed. This handoff records the exact §68 integration evidence for safe tracker synchronization.
- No percentage progress is inferred.

## Next integration order

1. Obtain exact-current-Develop canonical Quality for `31310a6c449b50034378adb02bdd055e69e089c5` or a product-identical documentation descendant.
2. Independently consume exactly one compatible bounded successor.
3. Prefer an exact-green Backend bounded successor if present; otherwise consume the next exact-green UI gap after its canonical run completes.
4. Core may proceed to the next normative uncovered acceptance after §68/§69, without duplicating already-covered §69 model-drift behavior.
5. Preserve Beta/release runtime regression coverage before any Windows candidate or promotion claim.

## Persistent release guards

Retain explicit Beta/release regression acceptance for pypdf packaging metadata, fail-closed frozen argv routing and Desktop/Worker two-EXE split, exactly one Desktop with bounded/non-growing workers, adaptive 2048-context DirectChat budgeting, the Windows lane-lock `PermissionError` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError` crash cluster, and storage-bootstrap/migration startup signatures including duplicate-column startup failures.

## Rules retained

No direct work on `main`; no main promotion; no force-push/history rewrite/auto-merge; no Skip/XFail or weaker assertions; no Security/Storage/Windows/Recovery/validator relaxation; no fake success or fabricated provenance.
