# Alpha/Beta Observability runtime v2 — application composition

Date: 2026-09-27
Base Develop: `36e9ec9f2f3e0506c92036e266fc746daba0d75d`
Branch: `fix/alpha-beta-update-runtime-v2`

## This slice
- activates the already-integrated secure rotating JSONL sink in the real Core lifecycle;
- activation occurs only after the initial read-only DB check and successful StorageBootstrap/RuntimeLayout startup, so `log_root` is already a validated local runtime directory;
- uses `log_root/athena.jsonl`, existing privacy-preserving formatter and bounded rotation defaults;
- persistent logging is detached/closed on normal stop and on startup/shutdown failure paths;
- app restart recreates exactly one owned persistent handler.

## Tests
`tests/unit/test_observability_application_jsonl.py`

## Next
After exact-head green:
1. cross-layer correlation/request identifiers where missing;
2. Health/capability exposure of persistent-diagnostics state if still required;
3. Alpha 17/Beta 23 application-update staging/verification/rollback on a fresh branch.

Do not redo #192 secure-open work; it is already integrated.
