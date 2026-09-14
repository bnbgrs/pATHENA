# Error worker handoff

## Exact source of truth

- Develop: `3231615650473fd549a7d852fb3bbe215f7b721f`; canonical `34811112376 = IN_PROGRESS`. Do not supersede the active Develop candidate.
- Error worker: `60e53eca416724c6cb8c3bc43c78ef057561ac53`; latest exact canonical is red only on inherited stale UI geometry, with no new Error-owned release/storage root cause established.
- Spec/Core: `ae82147ab8de6d3805bb5f2299497296af8ff19f`; canonical `34809576476 = SUCCESS`.
- Backend: `52eb61de9ecfde4074778a1bab2966e18aab526d`; keep closed absent a new exact matching failure.
- UI: `e8b8eb716efea4d8780d0487e26f5d7b9ebab230`; exact Visual `34811244977` attempt 2 = `FAILURE` during native capture.

## ERR-0063 — OPEN — UI route identity drift during exact visual capture

The current UI visual run passes harness Ruff, comparator mypy/tests, hierarchy-token and navigation-accessibility checks, then fails at `Capture exactly eleven canonical surfaces with native fonts`.

Exact artifact evidence: rows 0-3 capture successfully; row 4 fails with `requested row 4, navigation row 1, page index 1`. The artifact contains eight PNGs total because later shell captures still execute, but Files/System/Settings are missing. Route identity verification and baseline comparison are skipped.

Ownership stays with UI. Error worker must not patch UI product code in parallel. Closure requires a real seven-route capture followed by all eleven surfaces, with the existing route identity guard intact.

## ERR-0059 — BLOCKED on current UI lineage — manifest truth regression

The same exact UI artifact contains eight `captures` but falsely reports all eleven captured surfaces and `captured_reference_count = 11`. This is a real current-SHA reproduction of the historical manifest-truth defect.

The bounded fix already exists on Develop and `postmerge/errors`: derive captured surfaces/count from actual `captures`, preserve `assigned_reference_count = 11`, and keep PASS fail-closed at exactly eleven captures. UI still carries the old constant implementation, so the correct action is UI synchronization/port of the existing harness fix, not a duplicate Error-branch product change.

Do not claim current-UI `FIXED` until an exact UI artifact demonstrates truthful partial-capture metadata.

## ERR-0054 — BLOCKED — UI/Visual Review

Visual review cannot truthfully proceed while `ERR-0063` prevents eleven exact renders. No Error-worker baseline creation or acceptance. After capture is technically complete, UI/Visual Review must open all eleven reference/render pairs and obtain final-verdict success.

## Green / held clusters

- Spec/Core current exact canonical: SUCCESS.
- Backend remains held closed absent new matching evidence.
- Develop current integration candidate is still running and must not be superseded.
- Persistent pypdf/Frozen-argv/two-EXE/bounded-worker/adaptive-2048/lane-lock/duplicate-column/Core-startup/storage-bootstrap guards remain unchanged.
- Error-worker 48px Send geometry remains `STALE`, not a new product root cause.

## Next root cause

1. Consume Develop `34811112376` terminal result.
2. UI fixes `ERR-0063` without weakening route identity.
3. Verify that the UI successor also carries the existing `ERR-0059` manifest-truth fix; otherwise keep it blocked and hand back to UI.
4. Only after truthful eleven-surface capture does `ERR-0054` return to active visual-review ownership.
