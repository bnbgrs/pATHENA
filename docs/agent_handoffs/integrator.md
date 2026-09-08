# pATHENA Feature Integrator Handoff

## Current branch state

- `main` remains strict read-only at `0d4d621f8a38ddf8eccfa09622bf193687619943`.
- Develop before this run: `b5f824082fcd9d335ea55de76f88d23a3c0ee7e8`.
- Integration target: `develop/pathena-next` only.
- Worker heads reviewed: errors `d15f50e3e4197e247e1111e86aa33cd80d0e5309`; spec-core `af1f9da019fbee21984cf62fb77a2e8bbacaed5b`; backend `ea601b96d681580c2e8f1f1af40c7d97c347511e`; UI `de3ae27e58e41e478648a368d37d1bba160bfc7a`.
- `main` and `bnbgrs/ATHENA` were untouched; no force update, rebase, history rewrite, auto-merge or main promotion was used.

## Progress this run — Spec/Core §72 unavailable-NAS acceptance

Spec/Core §72 was independently reviewed and integrated as the single bounded progress slice.

- Worker acceptance repair lineage culminates at `772c2bfdc8767b7c0d032dbb8709120de635f6c0`.
- Exact canonical Quality `34198674038` on `772c2bfdc8767b7c0d032dbb8709120de635f6c0` completed `success`.
- The current Spec/Core head `af1f9da019fbee21984cf62fb77a2e8bbacaed5b` only adds handoff documentation after that exact-green parent; its newer Quality `34198712540` was still in progress during review and was not needed for the already exact-green bounded acceptance.
- Develop integration commit: `7d39c25faf93068f3363b68e9bac7d4c4e93ac89`.

The integrated test uses real `AthenaApplication.start()/stop()` lifecycle, captures three exact scoped Sources, resolves Research work items through candidate -> exact source identity, marks one SUCCESSFUL, one IRRELEVANT and the exact NAS source UNAVAILABLE, and locks processed=3, failed=0, unavailable=1, irrelevant=1, coverage=2/3 plus durable UNAVAILABLE-not-IRRELEVANT state. No production code, Search, Storage/WAL, Security, provider/transport, scheduler/worker, packaging or Windows runtime semantics changed.

## Verification state

- Exact worker/canonical evidence for the integrated §72 acceptance is green at `772c2bfdc8767b7c0d032dbb8709120de635f6c0` / Quality `34198674038`.
- Develop received only the exact verified acceptance file; divergent Spec/Core history and documentation were not imported.
- No exact-current-Develop canonical workflow is yet associated with the post-integration descendant; global-green/promotion-ready is not claimed.
- No Skip/XFail, assertion weakening or guard relaxation was introduced.

## Other worker state

- UI current head `de3ae27e58e41e478648a368d37d1bba160bfc7a` adds focused coverage for Jobs verification-failure copy; Quality `34200490506` was pending at review, so it is not READY.
- Backend product `efdae09dc71a661ea5c81f67b8e2b09ac90c0080` had Quality `34195556143 = cancelled`; current Backend handoff descendant is not exact-green and remains held.
- Error handoff still records ERR-0024 IN_PROGRESS from pre-repair evidence and ERR-0023 FIXED_PENDING_VERIFY; the exact-green §72 successor should be consumed by Error on its next scan to close/reclassify ERR-0024 without reviving the now-fixed teardown defect.

## UI / Alpha-Beta state

- Eleven-screen status remains implemented pending visual review; no MATCH claim is made without original-reference evidence.
- `docs/development/ALPHA_BETA_PROGRESS.md` was read; no percentage is inferred. A destructive partial rewrite was not attempted because the connector returned a truncated large body.
- No historical Windows/runtime crash class is reopened without exact-current reproduction.

## Next integration order

1. Obtain exact-current-Develop canonical Quality on a descendant carrying `7d39c25faf93068f3363b68e9bac7d4c4e93ac89`.
2. Error worker should consume exact-green §72 evidence and close/reclassify ERR-0024 accordingly; keep ERR-0023 pending until exact Develop verification.
3. Consume exactly one compatible bounded successor: UI Jobs verification-failure copy if its exact canonical run succeeds; otherwise a later exact-green Backend/Core successor.
4. Preserve the release crash-regression matrix before any Windows candidate or promotion claim.

## Persistent release guards

Retain explicit Beta/release regression acceptance for pypdf packaging metadata; fail-closed frozen argv routing and Desktop/Worker two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context DirectChat budgeting; Windows lane-lock `PermissionError` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError`; and storage-bootstrap/migration startup signatures including duplicate-column failures.

## Rules retained

No direct work on `main`; no main promotion; no force-push/history rewrite/auto-merge; no Skip/XFail or weaker assertions; no Security/Storage/Windows/Recovery/validator relaxation; no fake success or fabricated provenance.
