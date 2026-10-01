# Principal Engineering Handoff — ComfyUI runtime truth — 2026-10-02

## Ausgangslage

Integration target at slice start: `develop/pathena-next@467ef434236c320e4afe9d21a39c20a4a2b75728`.

This slice was selected only after checking current branches, open PRs, active bot work, handoffs and gates. Search, Chat branching/cancellation, Sources clipboard capture, Recovery, Backup, Windows packaging, LM Studio/model boundaries, Knowledge, Jobs, PALLAS and structured-replication publication were already actively owned by other branches/PRs. No current open PR touched `src/athena/desktop/pathena_comfyui.py` when this branch was created.

Branch: `fix/comfyui-history-status-truth-20261002-sol`
PR: #391
Product/test head before this handoff commit: `d75345bab70a06347d35ca400fb1537522b3b91d`

## Root Causes

### 1. Failed ComfyUI workflows could be shown as successful

`ComfyUiClient.prompt_state()` treated the mere presence of a prompt id in `/history/{prompt_id}` as `completed`. It ignored ComfyUI's persisted `status.status_str` and `status.completed` values.

Effect: failed or interrupted workflows could be rendered as successful completion.

### 2. Malformed optional endpoint configuration could abort desktop startup

`_loopback_endpoint()` called `urllib.parse.urlsplit()` and read `parsed.port` without translating their `ValueError` boundaries into `ComfyUiError`.

`ExternalWorkspaceCoordinator` intentionally treats ComfyUI as optional and catches `ComfyUiError`; a malformed `PATHENA_COMFYUI_URL` such as `http://127.0.0.1:not-a-port` therefore escaped the optional-integration boundary and could abort startup.

Port 0 was also accepted despite not being a usable TCP destination.

### 3. VRAM aggregation could combine unrelated or invalid evidence

`_device_vram()` accumulated `vram_total` and `vram_free` independently across devices and only compared list lengths afterwards.

This allowed incomplete multi-device payloads to combine a total from one device with free memory from another. Non-finite numeric values such as `inf` could also reach `int()` and raise.

### 4. The local-only ComfyUI client could follow HTTP redirects off loopback

`urllib.request.build_opener(ProxyHandler({}))` disabled proxy use but retained urllib's default redirect handler.

A loopback ComfyUI response could therefore redirect a request to another origin, including a non-loopback host, despite the configured endpoint itself being loopback-only.

## Änderungen

### `src/athena/desktop/pathena_comfyui.py`

- History entries now require a valid status object.
- Success is projected only when `status_str == "success"` and `completed is True`.
- Terminal non-success states are projected as `failed`.
- Non-terminal stale history remains `unknown`.
- Contradictory/malformed success history fails closed with `ComfyUiError`.
- UI text now distinguishes successful completion, failed workflow, and absence of a terminal result.
- Invalid URL parsing and invalid/out-of-range/zero ports are normalized to `ComfyUiError`, preserving optional startup behavior.
- VRAM metrics are validated per device as finite, non-negative pairs with `free <= total`; aggregation occurs only when every device contributes a complete valid pair.
- Added a dedicated no-redirect urllib handler. ComfyUI HTTP requests now reject redirects rather than allowing the fixed loopback trust boundary to move.

### `tests/unit/test_pathena_comfyui.py`

Added regression coverage for:

- successful vs failed vs stale/missing history;
- malformed/contradictory history status;
- Qt projection of a failed job without fake completion;
- malformed/zero ComfyUI ports;
- malformed IPv6 URL parsing;
- incomplete multi-device VRAM evidence;
- non-finite and impossible VRAM values;
- correct complete multi-GPU aggregation;
- redirect rejection before the redirect target is contacted.

### `tests/unit/test_pathena_optional_comfyui_startup.py`

The existing real `PathenaMainWindow` optional-startup test now also covers malformed and zero ports and proves ComfyUI remains unavailable/fail-closed without breaking the shell or command truth.

## Commits

- `89721845bb6fdf43b22cd898776e76bb07537813` — Fix ComfyUI history status truth
- `43b77a43cdf067dded01de8961ee176abba6ad70` — Test truthful ComfyUI terminal status projection
- `ebd670187a35a4f6f2b7f2497c4cd4c09095288a` — Fail closed on malformed ComfyUI endpoint ports
- `dab343bf1239e1a87a71a327ebe1be3bdf430eb9` — Test malformed ComfyUI endpoint boundaries
- `aff7b26b505f642e5913a789d7b8e1a59726ca01` — Cover fail-closed optional ComfyUI startup configuration
- `7df29d07720214ac4eac723dc2f3744933164569` — Keep ComfyUI VRAM projection evidence-safe
- `ec483cdd9f3984f8c54a6e973a28ea8e21eb4bc1` — Test evidence-safe ComfyUI VRAM aggregation
- `ea8893243241ef8ebc5404bbe5391b3dab391c06` — Block ComfyUI HTTP redirect escapes
- `d75345bab70a06347d35ca400fb1537522b3b91d` — Test ComfyUI redirect containment

## Verhalten danach

- A prompt existing in ComfyUI history is no longer sufficient to claim success.
- Failed/interrupted terminal jobs are visibly non-successful.
- Corrupt history does not become a green status.
- Invalid optional ComfyUI endpoint configuration degrades only the optional integration instead of escaping as a raw parser exception.
- VRAM display remains unavailable when complete measured evidence is not present.
- The bridge cannot leave its configured loopback origin through normal HTTP redirects.

## Validierung

Requested on PR #391 exact final head after this handoff commit:

- ATHENA Quality Gate
- pATHENA UI Focused Candidate
- pATHENA 11-Surface Visual Regression

Earlier workflow runs on superseded intermediate heads were automatically cancelled/replaced by subsequent pushes. They are not validation evidence for the final candidate.

The environment available to this run did not contain a local checkout capable of starting the Qt desktop directly, so manual live UI validation is **not claimed**. The added Qt test uses a real `PathenaMainWindow` for the optional-startup boundary, and the PR CI is the authoritative executable validation for this branch.

## Bekannte Restprobleme

- This slice does not implement Issue #296 vision paste itself. PR #374 already owns Raw Archive clipboard image bytes and active model/provider branches currently touch the multimodal transport boundary; duplicating them would create conflict.
- It does not modify the Internet/TOR gateway; #369/#376 currently own adjacent gateway/Core boundaries.
- It does not change ComfyUI job cancellation/global interrupt semantics; the current UI truthfully exposes that a global interrupt is unavailable.
- Final CI outcome must be read from PR #391 exact head before integration.

## Abhängigkeiten / Konfliktrisiko

Conflict risk is intentionally narrow:
- `src/athena/desktop/pathena_comfyui.py`
- `tests/unit/test_pathena_comfyui.py`
- `tests/unit/test_pathena_optional_comfyui_startup.py`

At branch creation no active current PR modified those files. Old historical UI PRs mention ComfyUI but should not be used as current integration sources without rebasing/reconstruction.

Do not overwrite or merge unrelated active work from Search, Sources, Recovery, Windows packaging, Chat, Knowledge, Jobs, PALLAS, Backup, LM Studio/model or structured replication into this branch.

## Nächste sinnvolle Schritte

1. Wait for/read the three exact-head PR #391 gates; fix only a real new failure signature.
2. If all gates are green, Integrator can review/merge #391 history-preserving into the then-current `develop/pathena-next`, resolving only genuine drift.
3. After integration, continue Issue #296 vision-paste wiring by building on #374 plus the active model/provider work rather than reimplementing image storage.
4. Keep ComfyUI local-only tests as a release guard; any future HTTP client replacement must retain proxy bypass **and** redirect containment.
