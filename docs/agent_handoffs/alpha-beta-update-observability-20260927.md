# Alpha/Beta Update + Observability seed — 2026-09-27

Base Develop: `0c68facde0f7bf9e5d0210925674eb24ddf969bf`
Worker: `fix/alpha-beta-update-observability`

## Observability #192 reconstructed now

This commit reconstructs the canonical-green secure JSONL end state from historical PR #218 directly on current Develop.

Exact qualified blobs:
- `src/athena/observability/jsonl.py` = `2529bf5e73ea604e507920d52e3d9569319dc54e`
- `tests/unit/test_observability_jsonl.py` = `3dc382e361b3a3bbbbd4523e84e6a763ec6952a7`
- `tests/unit/test_observability_jsonl_retention.py` = `26dfab4f2ddc86ce7e5b4e82ff17b2017a040b38`

Behavior:
- privacy-preserving shared JsonFormatter;
- ATHENA namespace-owned JSONL sink;
- independent Console/JSONL thresholds;
- bounded rotation/retention;
- secure actual-open boundary on delayed first open and rollover reopen;
- O_NOFOLLOW where available, descriptor/path identity verification, parent revalidation;
- symlink/junction substitution fails closed before bytes reach the substituted target;
- older unsafe ATHENA-owned handlers are replaced rather than reused.

## Do not restart #192 diagnosis

First qualify this exact reconstruction with focused tests, Ruff, mypy and canonical Quality. If green, #192 is ready for integration.

## Next independent work

After #192 qualification:
1. compose persistent diagnostics into AthenaApplication only after trusted runtime-layout/database preflight;
2. retain local-only/privacy defaults;
3. continue Alpha 17 / Beta 23 application update staging/rollback as a separate slice.

Do not mix application-update code into this secure-open PR before qualification.
