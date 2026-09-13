# pATHENA Alpha/Beta Progress

Evidence-only progress register for `develop/pathena-next`. No invented completion percentage.

## Current baseline

- Develop parent before current integration: `d7a5bcf6d836c47588b907d666b5541386ca0678`.
- Exact parent canonical Quality `34737035739 = FAILURE` only in pytest contract enforcement after native Qt controller isolation; controller module itself passed 6/6 and the remaining suite completed with `1 failed, 5029 passed, 17 skipped`.
- Worker heads checked: Errors `2a777c98dd10d22cefc487e0f76d0552415efdf5`; Spec/Core `fc253bd8646028a4226aa603d7188830daf54d7d`; Backend `7063801bcefc7153f4ef5de4b3d82669861b4208`; UI `2f003f7de2cc9b9499b1853cc8e4869b404488eb`.

## Current integration state

- Canonical Qt-controller isolation remains mandatory and fail-closed. Its repository contract now verifies both mandatory pytest invocations and their combined failure enforcement instead of requiring the superseded single-process command string.
- Truthful Knowledge provenance/current-revision/revision-history/revision-change surfaces remain integrated.
- Knowledge model disclosure is selected from exact-green Spec/Core `fc253bd8...`: user revisions cannot claim fabricated model provenance; primary-model disclosure requires a matching succeeded ProcessingRun/ModelSignature pair.
- Transactional schedule-startup recovery remains integrated.
- Backend paired-sidecar startup identity work remains excluded while Storage Focused is red.

## Exact evidence

- Develop `d7a5bcf6...`: canonical `34737035739 = FAILURE`; Linux Storage, Windows path/recovery/package guards, Local Install and pypdf are green; isolated controller 6/6 passes; remaining suite sole failure is `test_quality_workflow_contract.py::test_canonical_quality_keeps_full_pytest_and_enforces_all_core_checks`.
- Spec/Core `fc253bd8...`: Core Focused `34737394852 = SUCCESS`; canonical `34737394871 = SUCCESS`.
- Backend `7063801b...`: Storage Focused `34738082478 = FAILURE`; no Storage promotion.

## Error and visual truth rules

- `docs/agent_logs/ERROR_LEDGER.md` remains historical where newer exact-SHA evidence exists.
- Eleven-screen status remains fail-closed; no visual `MATCH` without opened original reference plus real exact-SHA render.

## Persistent release guards

Do not relax: pypdf packaging; fail-closed Frozen argv; Desktop/Worker two-EXE split; exactly one Desktop instance with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock cluster; duplicate-column/Core-startup/storage-bootstrap signatures; Security/Storage/Recovery guards; test strength; Skip/XFail prohibitions.

## Promotion state

`PROMOTION_READY=NO`

The integrated regression fix and Knowledge disclosure slice require exact-current Develop canonical Quality before any further Develop mutation.
