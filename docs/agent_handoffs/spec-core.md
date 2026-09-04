# pATHENA Alpha/Beta Core Handoff

## Current baseline

- Shared baseline: `develop/pathena-next@3659470baa5cc0cdeea538bcfe241174f319a502`.
- Worker branch: `postmerge/spec-core`.
- History-preserving NON-FORCE synchronization merge: `0846e85a63b97a57025d8bd34989848b2672c53e`, parents `a20dbe70824d5fc07bdd1d981e3acf431554877a` and `3659470baa5cc0cdeea538bcfe241174f319a502`.
- `main@0d4d621f8a38ddf8eccfa09622bf193687619943` remains read-only and unchanged.

## Verified Core lineage

- Normal Hybrid Search facade/application composition is already VERIFIED and integrated on Develop.
- `TemporalContradictionPolicy` is VERIFIED and integrated on Develop.
- Exact canonical revision adapter `assess_canonical_claim_revisions()` is VERIFIED.

## READY slice — ProposalAcceptanceService temporal contradiction gate

Spec source: `docs/beta/05_Wissenseinheiten_Claims_und_Wissensgraph.md`, temporal contradiction requirements around §§56, 58, 60 and 69–70.

Bounded product commit: `11b56867dd2f23d7149bc9defa299434e3ca5409`.
Focused acceptance-test commit: `209c5c3715c8e560e0c3954c3cd88991876f9086`.
Exact verified head: `a20dbe70824d5fc07bdd1d981e3acf431554877a`.
Canonical Quality: `33826094843 = success`.

The canonical gate is called inside the existing ProposalAcceptanceService write transaction immediately before contradiction-review enqueue. Only provably DISJOINT exact canonical Claim revision windows suppress review enqueue. Touching, overlapping, open and unknown windows retain the existing explicit human-review path. Missing/non-Claim revisions fail closed through the verified adapter. No timestamps are inferred; no mutable current-head substitution, automatic contradiction relation, history deletion, schema change, synthetic provenance, Security/Storage/Recovery/Transport/UI behavior change is introduced.

Quality run `33826094843` passed specification validation, Ruff, mypy, full pytest, Windows path safety, Linux storage regressions and local install/Core-API restart smoke.

After the green run, the worker was synchronized history-preservingly with current Develop. The merge tree retains current Develop changes and the exact verified Core product/test blobs; no foreign-worker product files were overwritten.

## Integrator handoff

Status: `READY_FOR_INTEGRATOR_REVIEW`.

Integrator may independently review and integrate the bounded product/test lineage `11b56867dd2f23d7149bc9defa299434e3ca5409` + `209c5c3715c8e560e0c3954c3cd88991876f9086`, backed by exact canonical green head `a20dbe70824d5fc07bdd1d981e3acf431554877a` / run `33826094843`.

Do not merge the worker PR automatically and do not promote to main.

## Next Alpha/Beta gap

Select the highest unclaimed P0/P1/P2 Core composition gap from current Alpha/Beta source-of-truth. Prefer a bounded CHAT/KNOWLEDGE/RESEARCH/PALLAS path with real existing data/contracts; PALLAS must remain data-driven from actual Sources/Claims/Knowledge/Research and must not introduce decorative or synthetic state.
