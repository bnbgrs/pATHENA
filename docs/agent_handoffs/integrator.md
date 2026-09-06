# pATHENA Feature Integrator Handoff

## Current branch state

- `main` remains strict read-only at `0d4d621f8a38ddf8eccfa09622bf193687619943`.
- Develop before this run: `8b6c7a2f44104675570152a5b44fa65979493bc9`.
- Integration target: `develop/pathena-next` only.
- Worker heads reviewed: errors `410bdc595d3f4c370541b0701386cfe4b4b880ce`; spec-core `942d19f46a91af6672bb7639c1fca4cadf378ac7`; backend `80bd67a2a0ad9b1b013635597f6cdaeca0f05cba`; ui `38a28f61af16d0b12500b4056b586ba934a2ba1a`.
- `main` and `bnbgrs/ATHENA` were untouched; no force update, history rewrite or auto-merge was used.

## Integrated this run — Storage/Recovery user_version exact status shape

Backend user_version exact-status-shape lineage `4f09ad222547f279e27fb3d34285feb82f6a8f71` passed canonical ATHENA Quality Gate `34048748410 = success`. Independent review selected only product commit `cc333c33a8c828b205599b470422c69544368002` semantics and exact focused regression `ab6b61a75fc4dab856c40cbab0f8f089a9b305d0`; divergent Backend history and later busy-domain/WAL-policy work were excluded.

Develop commits created this run:
- `5f676db28049e874bf03c79c6f56d55bb448c2f6` — require `PRAGMA user_version` to return exactly one status field before schema-version acceptance.
- `59627044bf1bfd13a3ee8522150ab7a53edc47b1` — exact focused regression for empty, multi-field and canonical single-field user_version status, including proof that malformed status fails before checkpoint side effects.

The integrated change preserves candidate-only migration, exact SQLite runtime typing, three-field WAL checkpoint validation, journal-mode exact-status validation, path/link safety, sidecar-free activation and unrelated Security/Provider/UI/Windows behavior.

## Current readiness/error state

- Backend checkpoint busy-domain lineage `77ce30acb409881e00f12a9ab78655b81b0cdd1e` / Quality `34052064954 = success` is READY for a later bounded run.
- Backend WAL policy exact-status-shape product `76cda6717b15784d7d6722e07f0775179577c6eb` + regression `978d67958bddf0e4e3a72f4b5bc2220146242a1f` remains NOT READY in the current handoff pending exact canonical success.
- Error worker still tracks `ERR-0018` as Core-owned pending successful exact verification; no Backend defect is implicated.
- Exact-current-Develop global Quality is not claimed after this composition.

## UI / Alpha-Beta state

- Eleven-screen implementation remains pending visual-reference review; no pixel-level MATCH claim is made without original reference evidence.
- `docs/development/ALPHA_BETA_PROGRESS.md` remains canonical. No unsafe whole-file replacement was attempted from partial retrieval; this run's evidence is versioned here.

## Next integration order

1. Obtain exact-current-Develop canonical Quality if available.
2. Prefer the exact-green bounded Backend checkpoint busy-domain successor if still independently compatible.
3. Do not consume WAL-policy, new UI, or Core candidates without exact READY evidence.
4. Keep `ERR-0018` excluded from closure until exact corrected Core SHA is canonical-green.

## Persistent release guards

Retain explicit Beta/release regression acceptance for pypdf packaging metadata, fail-closed frozen argv routing and Desktop/Worker two-EXE split, exactly one Desktop with bounded/non-growing workers, adaptive 2048-context DirectChat budgeting, the Windows lane-lock `PermissionError` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError` crash cluster, and storage-bootstrap/migration startup signatures.

## Rules retained

No direct work on `main`; no main promotion; no force-push/history rewrite/auto-merge; no Skip/XFail or weaker assertions; no Security/Storage/Windows/Recovery/validator relaxation; no fake success or fabricated provenance.
