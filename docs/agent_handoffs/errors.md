# pATHENA Error Handoff

## Baseline

- Develop: `8c2dda7794ef4949844feb30d265d34248aa4660`; canonical Quality `34744264489 = SUCCESS`.
- Backend worker: `2182382b8aa4a2c37cbf698c51b9de8f7c148287`; Storage Focused `34746286422 = SUCCESS`; canonical Quality `34746286425 = PENDING`.
- UI worker: `541c367547c698489ad548cc791f72dd27d141b4`; UI Focused `34746344232 = SUCCESS`; canonical Quality `34746344225 = PENDING`.
- `main` and `bnbgrs/ATHENA` remain untouched.

## Current error state

- OPEN: none.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: `ERR-0049`, `ERR-0053`.
- FIXED: prior closures plus `ERR-0047`, `ERR-0050`, `ERR-0051`, `ERR-0052`.
- BLOCKED: none.

## ERR-0052 — FIXED

Develop `8c2dda7794ef4949844feb30d265d34248aa4660` completed canonical Quality run `34744264489 = SUCCESS`. The previously integrated knowledge-read fix is therefore closed.

## ERR-0049 — code fixed, exact focused verification green

`ERR-0049 = FIXED_PENDING_VERIFY / P1`.

Root cause was narrowed to startup identity revalidation accepting a complete replacement of an already-bound SQLite WAL/SHM pair. A secondary read-only inspection could still observe a valid prior SQLite state and was not sufficient proof of identity continuity after both published sidecar path identities changed.

Backend fix `2182382b8aa4a2c37cbf698c51b9de8f7c148287` now fails closed on direct complete WAL+SHM replacement during the bound startup window while preserving the accepted complete publication and complete withdrawal transitions.

Exact same-SHA evidence:

- Storage Focused `34746286422 = SUCCESS`.
- Changed Storage Ruff = SUCCESS.
- Storage mypy = SUCCESS, 35 source files clean.
- Focused Storage pytest = `34 passed`.
- The prior failing paired foreign WAL+SHM replacement case is included in this exact focused suite.

Canonical Quality `34746286425` is queued/pending. Promote `ERR-0049` to FIXED only when that exact worker-SHA canonical run completes SUCCESS. No further Storage code change is indicated by current evidence.

## ERR-0053 — code fixed, exact focused verification green

`ERR-0053 = FIXED_PENDING_VERIFY / P2`.

Root cause was the shared foundation QSS overriding the newer 48px shell geometry. `QPushButton#sendButton` still constrained its content box to 42px while the inherited 1px border on each side produced a rendered 44x44 widget. The layout refinement itself already requested the 48px shell token, so changing the layout test or weakening the square invariant would have hidden the real presentation defect.

UI fix `541c367547c698489ad548cc791f72dd27d141b4` derives the send-button foundation content-box size from `SHELL.composer_action_size - 2`, accounting for the two border pixels, and derives the circular radius from the same shell token.

Exact same-SHA evidence:

- UI Focused `34746344232 = SUCCESS` on Windows Server 2022.
- Exact changed UI tests plus navigation invariant = `22 passed`.
- The suite includes `tests/unit/test_pathena_layout_refinement_2200.py`, the previously failing send-button geometry contract.

Canonical Quality `34746344225` is queued/pending. Promote `ERR-0053` to FIXED only when that exact worker-SHA canonical run completes SUCCESS. No further UI code change is indicated by current evidence.

## CI discipline

- No force push, history rewrite, main mutation, Skip/XFail, test weakening, or Storage/Recovery guard relaxation was used.
- Repairs were isolated on manual branches, reviewed through PRs, then merged only into the owning worker branches.
- Backend repair PR `#128` was merged into `postmerge/backend`.
- UI repair PR `#129` was merged into `postmerge/ui`.
- Existing worker-to-Develop verification PRs remain the promotion path; they were not auto-merged into Develop.

## Integrator / worker handoff

- `ERR-0052 = FIXED` — no action.
- `ERR-0049 = FIXED_PENDING_VERIFY` — consume canonical `34746286425`; if SUCCESS, close. If it fails, open/reopen only from the exact failing job evidence rather than altering the already-green Storage focused fix.
- `ERR-0053 = FIXED_PENDING_VERIFY` — consume canonical `34746344225`; if SUCCESS, close. If it fails, classify the exact failing job before changing UI code.

## NEXT_ROOT_CAUSE

No currently open code defect remains in the error ledger. Await exact canonical outcomes for the two repaired worker SHAs. Any new error ID must be backed by new exact-SHA failure evidence rather than inferred from stale runs.
