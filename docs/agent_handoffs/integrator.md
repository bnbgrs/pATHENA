# pATHENA Feature Integrator Handoff

## Current integration

- Integration target: `develop/pathena-next`.
- Develop parent before this integration: `e48442210d98ca98a086dd7e4f3e5b3dd26e65bb`.
- Exact canonical Quality on that parent: `34797268583 = FAILURE`.
- Parent failure scope: specification validator, Ruff, mypy, Linux Storage, Windows release guards and Local Install/pypdf are green; full pytest fails only at `tests/integration/test_core_api_process_lifecycle.py::test_dedicated_core_process_serves_until_desktop_requests_stop` with a transient startup 401 (`A valid local ATHENA session token is required`).
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## Iteration — Core API publication readiness race

Exact diagnostics show that `core-api.json` could become visible after the token file was written but before `LocalApiRuntime._token` was installed. The discovery file is the client-visible readiness barrier, so a client that reacts immediately can read the freshly issued token and still receive 401 from the server.

The bounded fix installs the in-memory authenticator immediately after the private token file succeeds and before publishing discovery. Existing failure cleanup remains fail-closed: any later discovery publication error still calls `clear()`, which forgets the token and removes both bootstrap files best-effort.

A focused runtime-boundary regression intercepts discovery publication and proves that the token already authenticates at the exact moment the discovery barrier is about to become visible. No authentication, loopback, filesystem-identity, Storage/Recovery, packaging, Windows, or test-strength guard is relaxed.

## Current worker truth at integration time

- Errors: `80ffef405415a9dfde9bff8b1f54764224652ef7` — exact-SHA truth refresh; no competing product mutation selected.
- Spec/Core: `52b4e322041547e9039a0f3026f6747583605914` — previously promoted merge/split policy; no new product delta selected.
- Backend: `52eb61de9ecfde4074778a1bab2966e18aab526d` — synchronized with the prior Develop baseline; no new product delta selected.
- UI: `6fce1d686f43d4cb8e3ea060055f4a871147df82` — new presentation work remains UI/Visual-owned and is not promoted by this runtime regression fix.

## Source-of-truth notes

- `docs/agent_logs/ERROR_LEDGER.md` remains historical wherever newer exact-SHA evidence exists.
- `docs/ui/11_SCREEN_REFERENCE_MANIFEST.md` and `docs/ui/VISUAL_GAP_LEDGER.md` remain fail-closed: no `MATCH` without an opened original reference and a real rendered exact-SHA state.
- The verified Send target remains 44×44 outer geometry.

## Persistent release guards

Retain without relaxation: pypdf packaging; fail-closed Frozen argv; Desktop/Worker two-EXE split; exactly one Desktop instance with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock cluster; duplicate-column/Core-startup/storage-bootstrap signatures; Security/Storage/Recovery guards; no Skip/XFail.

## Promotion state

`PROMOTION_READY=NO`

Require canonical Quality on the resulting exact Develop SHA before any further Develop mutation.
