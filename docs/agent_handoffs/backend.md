# Backend & Systems Handoff

Generated: 2026-09-10
Branch: `postmerge/backend`

## Current source of truth

- Develop consumed first: `develop/pathena-next@8c342e1b6ea07025983726ec24d48786759c28fa`.
- Backend worker head before this handoff refresh: `c5e750a827de4b353da9873cb38d95b46a119d60`.
- Exact Develop canonical Quality `34447189545@8c342e1b6ea07025983726ec24d48786759c28fa = SUCCESS`.
- Exact Backend canonical Quality `34441278497@c5e750a827de4b353da9873cb38d95b46a119d60 = FAILURE`; no worker Quality run was queued or in progress when this refresh began.
- Current Develop handoffs/spec-core/UI/integrator handoffs and current Alpha/Beta/architecture/runtime/storage documentation were treated as authoritative over historical worker priorities.

## Closed dependency slice — BE-020 runtime ModelSignature drift guard

Status: `CLOSED_ON_DEVELOP / QUEUE_EVIDENCE_STALE`.

The persistent Backend queue still states that shared `chat/generation.py` uses an older inline signature comparison. That statement is stale on current Develop.

On `8c342e1b6ea07025983726ec24d48786759c28fa`, `src/athena/chat/generation.py` imports the reusable `assert_runtime_model_matches_signature` guard from `athena.model.signature_guard`. `ChatGenerationService.send_context_package()` calls that guard against the pinned `ContextPackage` ModelSignature before entering `_generate_and_persist()`. Provider dispatch (`provider.stream_chat(...)`) occurs only later inside `_generate_and_persist()`. A `ModelSignatureDriftError` is converted to a fail-closed `ModelSelectionError` before provider dispatch.

Therefore BE-020 must not cause another Backend product mutation or a duplicate signature-guard implementation. The implementation is already present on authoritative Develop and the exact Develop canonical Quality for the inspected SHA is green.

No production code, test assertion, provider behavior, security boundary, storage/recovery behavior, or fail-closed guard was changed for this closure.

## Previously closed root-cause cluster — Windows storage bootstrap reserve path

Status: `CLOSED_ON_DEVELOP / EXACT_LANE_VERIFIED`.

The earlier Windows storage-bootstrap harness defect was fixed on authoritative Develop. The failing test stub used a POSIX-looking `/tmp/...` path that was not absolute on Windows; production `EmergencyReserveStatus` correctly rejected it fail-closed. The corrected test uses a platform-valid absolute path. No production Storage/Recovery behavior was weakened.

## Current Backend worker red state

The broad historical worker branch remains non-authoritative relative to current Develop. Its last exact canonical run is red and contains worker-only schema-v41 / `research_delta_boundaries` history plus a separate Ruff import-order finding. Do not mechanically repair legacy fixtures to preserve that worker-only schema lineage.

Integrator has already required that broad Backend/Storage/Migration/Runtime history not be absorbed as a unit. Any surviving worker delta must be re-proven as a small current-Develop gap before mutation or integration.

## CI discipline / verification constraints

- No Backend canonical Quality run was queued or in progress on `c5e750a827de4b353da9873cb38d95b46a119d60` when this handoff refresh began; `34441278497` is completed FAILURE.
- The local execution container still cannot resolve the Git mirror host, so a fresh checkout and focused local pytest/Ruff execution remain transiently unavailable.
- This run therefore made no product/test mutation and claims no fabricated focused PASS. BE-020 closure is based on direct exact-SHA source inspection plus the completed exact-SHA green canonical Develop run.
- Any future product/test mutation must begin with current Develop/worker/run re-check and obtain real focused verification before canonical Quality.

## Preserved release guards

- No silent Tor-to-Direct fallback.
- Redirect/Auth/HTTPS/response-size boundaries remain fail-closed.
- WAL maintenance safety remains intact.
- pypdf packaging, Frozen argv and two-EXE topology remain guarded.
- Bounded worker tree and adaptive 2048-context reserve remain guarded.
- Windows lane-lock/path-safety, duplicate-column/Core-startup/storage-bootstrap signatures remain protected and are only OPEN when reproduced on current exact-SHA evidence.
- No Skip/XFail, force push, history rewrite, main mutation, or mutation to `bnbgrs/ATHENA`.

## Integrator prerequisites

- BE-020: CLOSED on Develop `8c342e1b6ea07025983726ec24d48786759c28fa`; no Backend product cherry-pick is required.
- Windows storage bootstrap reserve-path cluster: CLOSED on Develop; no further Backend action required.
- Broad Backend worker history: `HOLD / NOT READY`.
- Do not integrate worker-only schema-v41/WAL/Runtime changes without a fresh bounded reconciliation against current Develop and exact focused/canonical evidence.

## Next Backend action

Consume the then-current Develop and Backend exact-SHA results first. Ignore BE-020 as stale queue work. Select the highest still-authoritative Backend/System gap from current red exact-SHA evidence or current specs/contracts. Do not preserve historical worker-only behavior merely to make its old tests green.
