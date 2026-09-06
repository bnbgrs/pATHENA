# pATHENA Feature Integrator Handoff

## Current branch state

- `main` remains strict read-only at `0d4d621f8a38ddf8eccfa09622bf193687619943`.
- Develop before this run: `1cc7b8dceb5b4ff098442e9f17f89b8cc36cb390`.
- Integration target: `develop/pathena-next` only.
- Worker heads reviewed at run start: errors `d53cfd799fab60859f6e2b2fe76e4154fa4555bd`; spec-core `5714f3c7724cb82ccd75a7e852c668bfe78c6d5d`; backend `74df90dc3b189d397c7a9f18afd0929a25e372bc`; ui `4be3a9c897313f63f8c49ddc6eb9ecfea9186ded`.
- `main` and `bnbgrs/ATHENA` were untouched; no force update, history rewrite or auto-merge was used.

## Integrated this run — Storage/WAL policy exact status shape

Backend BE-053 WAL-policy exact-status-shape lineage `2ea98794facffcae29d4f94b337fc84083028526` passed canonical ATHENA Quality Gate `34058195011 = success`. Independent review selected only product commit `76cda6717b15784d7d6722e07f0775179577c6eb` semantics and focused regression `978d67958bddf0e4e3a72f4b5bc2220146242a1f`; divergent Backend history and later `WalRuntimeStatus.autocheckpoint_bytes` work were excluded.

Develop commits created this run:
- `be2fbc3192e65fe62acb6e4ac0d760f3ca114e06` — require `PRAGMA page_size` and `PRAGMA wal_autocheckpoint` to each return exactly one status field before policy values are accepted.
- `b037c6d4d25f699be85de9b8a48c88decff46c62` — exact focused regression for absent/empty/multi-field policy rows and canonical single-field acceptance, including fail-before-WAL-observation behavior.

The integrated contract preserves positive true-int policy validation, no-follow/identity-checked WAL observation, PASSIVE-only automatic checkpointing, explicit-idle TRUNCATE, exact checkpoint result validation, Storage/Recovery invariants, and unrelated Core/UI/Security/Provider/Windows behavior. No test or guard was weakened.

## Current readiness/error state

- Backend current handoff marks `WalRuntimeStatus.autocheckpoint_bytes` true-int boundary product `22fa292c2213e8dbeca4e0a6733d32e71f5141df` + regression `fcd0b9a453cdf15c8d13c9708ebc5cd206ccbdad` NOT READY pending exact canonical success.
- Error worker tracks only Core-owned `ERR-0018` Ruff import-order rejection; no Backend defect is implicated.
- Exact-current-Develop global Quality is not claimed after this composition.

## UI / Alpha-Beta state

- Eleven-screen implementation remains pending visual-reference review; no pixel-level MATCH claim is made without original reference evidence.
- `docs/development/ALPHA_BETA_PROGRESS.md` remains canonical. Its complete body was not safely writable through the connector in this run because retrieval was truncated; no destructive whole-file replacement was attempted. This integration evidence is versioned here until a safe line-preserving tracker update path is available.

## Next integration order

1. Obtain exact-current-Develop canonical Quality if available.
2. Consume exactly one independently compatible bounded READY Core/Backend/UI successor.
3. Do not consume the Backend derived WAL-byte boundary without exact successful canonical evidence.
4. Keep `ERR-0018` excluded from closure until exact corrected Core SHA is canonical-green.

## Persistent release guards

Retain explicit Beta/release regression acceptance for pypdf packaging metadata, fail-closed frozen argv routing and Desktop/Worker two-EXE split, exactly one Desktop with bounded/non-growing workers, adaptive 2048-context DirectChat budgeting, the Windows lane-lock `PermissionError` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError` crash cluster, and storage-bootstrap/migration startup signatures including duplicate-column startup failures.

## Rules retained

No direct work on `main`; no main promotion; no force-push/history rewrite/auto-merge; no Skip/XFail or weaker assertions; no Security/Storage/Windows/Recovery/validator relaxation; no fake success or fabricated provenance.
