# pATHENA Feature Integrator Handoff

## Current branch state

- `main` remains strict read-only at `0d4d621f8a38ddf8eccfa09622bf193687619943`.
- Develop before this run: `abfe054654ae69994ad22d5a1079aeae42fba09f`.
- Integration target: `develop/pathena-next` only.
- Worker heads reviewed: errors `f4208cedd9574e6fddcc4cf47dac2694eeab69c8`; spec-core `b8858f986ec96e5973d47f8b74d2a120149a2037`; backend `77ce30acb409881e00f12a9ab78655b81b0cdd1e`; ui `59b2046d5e127664195f7ecf17245c45f70f00ca`.
- `main` and `bnbgrs/ATHENA` were untouched; no force update, history rewrite or auto-merge was used.

## Integrated this run — Storage/Recovery journal-mode exact status shape

Backend journal-mode exact-status-shape lineage `a6b3e0d7b185fd08a851b0b3f05127d66428697b` passed canonical ATHENA Quality Gate `34045619981 = success`. Independent review selected only product commit `1e3a28402343628b2fdfd3cb53ae78bf3ac21801` semantics and exact focused regression `tests/unit/test_migration_executor_journal_mode_shape.py`; divergent Backend history and later user_version/busy-domain work were excluded.

Develop commits created this run:
- `6bfe7e1ee5061a5ee3c9f9c2492338ccc51b870b` — require `PRAGMA journal_mode = DELETE` to return exactly one status field before accepting text `delete`.
- `1824f5a4ddc8752f46942c84653dc460043875c2` — exact focused regression for empty, multi-field and canonical single-field journal-mode status.

The integrated change preserves candidate-only migration, exact SQLite runtime typing, three-field WAL checkpoint validation, complete checkpoint requirements, path/link safety, sidecar-free activation, and unrelated Security/Provider/UI/Windows behavior.

## Current readiness/error state

- Backend current handoff now marks user_version exact-status-shape lineage `4f09ad222547f279e27fb3d34285feb82f6a8f71` / Quality `34048748410 = success` as READY for a later bounded run.
- Backend checkpoint busy-domain product `38dac1166d951f4a11b55181f927389304b3cd2e` + regression `eacb43bee6f8d168346198d5bb4b7630156b1570` remains NOT READY pending exact canonical completion.
- Error worker still tracks `ERR-0018` as Core-owned pending successful exact verification; no Backend defect is implicated.
- Exact-current-Develop global Quality is not claimed after this composition.

## UI / Alpha-Beta state

- Eleven-screen implementation remains pending visual-reference review; no pixel-level MATCH claim is made without original reference evidence.
- `docs/development/ALPHA_BETA_PROGRESS.md` remains canonical. No unsafe whole-file replacement was attempted from truncated retrieval; this run's evidence is versioned here.

## Next integration order

1. Obtain exact-current-Develop canonical Quality if available.
2. Prefer the exact-green bounded Backend user_version exact-status-shape successor if still independently compatible.
3. Do not consume checkpoint busy-domain, new UI, or Core candidates without exact READY evidence.
4. Keep `ERR-0018` excluded from closure until exact corrected Core SHA is canonical-green.

## Persistent release guards

Retain explicit Beta/release regression acceptance for pypdf packaging metadata, fail-closed frozen argv routing and Desktop/Worker two-EXE split, exactly one Desktop with bounded/non-growing workers, adaptive 2048-context DirectChat budgeting, the Windows lane-lock `PermissionError` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError` crash cluster, and storage-bootstrap/migration startup signatures.

## Rules retained

No direct work on `main`; no main promotion; no force-push/history rewrite/auto-merge; no Skip/XFail or weaker assertions; no Security/Storage/Windows/Recovery/validator relaxation; no fake success or fabricated provenance.
