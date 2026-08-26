"""Strict local hardware acceptance for the supported pATHENA Windows package.

This probe is intentionally separate from ordinary cloud acceptance. It is meant to be
run on the actual workstation that will host pATHENA, where it can verify the expected
GPU, a loaded LM Studio model, and one real local inference without pretending that a
GitHub-hosted runner represents the target hardware.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from athena.config.settings import AthenaSettings, ConfigurationError
from athena.model.adapters.lm_studio import LMStudioProvider, ModelProviderError
from athena.model.domain import ModelChatMessage, ModelInfo
from athena.version import __version__

DEFAULT_EXPECTED_GPU = "AMD Radeon RX 7900 XTX"
INFERENCE_MARKER = "PATHENA_LOCAL_INFERENCE_OK"


class HardwareAcceptanceError(RuntimeError):
    """Raised when the target workstation cannot be inspected safely."""


class _AcceptanceProvider(Protocol):
    @property
    def base_url(self) -> str: ...

    def discover_models(self) -> tuple[ModelInfo, ...]: ...

    def stream_chat(
        self,
        *,
        model_id: str,
        messages: Sequence[ModelChatMessage],
        max_output_tokens: int | None = None,
        reasoning_mode: str | None = None,
        temperature: float | None = None,
    ) -> Iterator[str]: ...


@dataclass(frozen=True, slots=True)
class HardwareAcceptanceCheck:
    name: str
    status: str
    detail: str


@dataclass(frozen=True, slots=True)
class HardwareAcceptanceReport:
    checks: tuple[HardwareAcceptanceCheck, ...]
    expected_gpu: str
    detected_gpus: tuple[str, ...]
    selected_model_id: str | None
    gpu_ready: bool
    model_ready: bool
    inference_ready: bool

    @property
    def overall_ready(self) -> bool:
        return self.gpu_ready and self.model_ready and self.inference_ready


def _video_controller_names_from_payload(payload: str) -> tuple[str, ...]:
    text = payload.strip()
    if not text:
        return ()
    try:
        decoded = json.loads(text)
    except json.JSONDecodeError as exc:
        raise HardwareAcceptanceError(
            "Windows video-controller query returned invalid JSON."
        ) from exc
    if not isinstance(decoded, dict):
        raise HardwareAcceptanceError(
            "Windows video-controller query returned an unexpected payload."
        )
    names = decoded.get("names")
    if names is None:
        return ()
    if isinstance(names, str):
        names = [names]
    if not isinstance(names, list):
        raise HardwareAcceptanceError(
            "Windows video-controller query returned an invalid names field."
        )
    normalized: list[str] = []
    for value in names:
        if not isinstance(value, str) or not value.strip():
            raise HardwareAcceptanceError(
                "Windows video-controller query returned an invalid controller name."
            )
        normalized.append(value.strip())
    return tuple(normalized)


def detect_windows_video_controllers() -> tuple[str, ...]:
    """Read display-adapter names through CIM without requiring vendor tooling."""
    if os.name != "nt":
        raise HardwareAcceptanceError(
            "Local hardware acceptance is supported only on Windows."
        )
    powershell = shutil.which("powershell.exe") or shutil.which("pwsh.exe")
    if powershell is None:
        raise HardwareAcceptanceError(
            "PowerShell is required to inspect the Windows video controller."
        )
    command = (
        "$ErrorActionPreference='Stop'; "
        "$names=@(Get-CimInstance Win32_VideoController | ForEach-Object { $_.Name }); "
        "[ordered]@{names=$names} | ConvertTo-Json -Compress"
    )
    creationflags = int(getattr(subprocess, "CREATE_NO_WINDOW", 0))
    try:
        completed = subprocess.run(
            [powershell, "-NoLogo", "-NoProfile", "-NonInteractive", "-Command", command],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
            creationflags=creationflags,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise HardwareAcceptanceError(
            f"Windows video-controller query failed: {exc}"
        ) from exc
    if completed.returncode != 0:
        detail = completed.stderr.strip() or f"exit code {completed.returncode}"
        raise HardwareAcceptanceError(
            f"Windows video-controller query failed: {detail}"
        )
    return _video_controller_names_from_payload(completed.stdout)


def _gpu_matches(expected_gpu: str, detected_gpu: str) -> bool:
    expected = " ".join(expected_gpu.casefold().split())
    detected = " ".join(detected_gpu.casefold().split())
    return bool(expected) and (expected == detected or expected in detected)


def _select_loaded_llm(
    provider: _AcceptanceProvider,
    requested_model_id: str | None,
) -> ModelInfo:
    models = provider.discover_models()
    loaded_llms = tuple(
        model for model in models if model.model_type == "llm" and model.loaded
    )
    if requested_model_id is None:
        if not loaded_llms:
            raise HardwareAcceptanceError(
                "LM Studio is reachable but no local LLM is loaded."
            )
        return loaded_llms[0]
    normalized = requested_model_id.strip()
    if not normalized:
        raise HardwareAcceptanceError("Requested LM Studio model id must not be empty.")
    for model in loaded_llms:
        if model.backend_model_id == normalized:
            return model
    raise HardwareAcceptanceError(
        f"Requested LM Studio model is not loaded: {normalized}"
    )


def _run_live_inference(provider: _AcceptanceProvider, model: ModelInfo) -> str:
    prompt = (
        "This is a local pATHENA hardware acceptance probe. "
        f"Reply with exactly {INFERENCE_MARKER} and nothing else."
    )
    chunks = provider.stream_chat(
        model_id=model.backend_model_id,
        messages=(ModelChatMessage(role="user", content=prompt),),
        max_output_tokens=32,
        reasoning_mode="off",
        temperature=0.0,
    )
    response = "".join(chunks).strip()
    if not response:
        raise HardwareAcceptanceError("LM Studio returned an empty inference response.")
    if response != INFERENCE_MARKER:
        clipped = response[:160].replace("\r", " ").replace("\n", " ")
        raise HardwareAcceptanceError(
            "LM Studio inference completed but did not return exactly "
            "the acceptance marker: "
            f"{clipped!r}"
        )
    return response


def run_hardware_acceptance(
    settings: AthenaSettings,
    *,
    expected_gpu: str = DEFAULT_EXPECTED_GPU,
    requested_model_id: str | None = None,
    video_controllers: Sequence[str] | None = None,
    provider: _AcceptanceProvider | None = None,
) -> HardwareAcceptanceReport:
    """Execute all target-workstation checks and preserve independent failure evidence."""
    if not isinstance(settings, AthenaSettings):
        raise ValueError("Hardware acceptance settings must be AthenaSettings.")
    normalized_expected_gpu = expected_gpu.strip()
    if not normalized_expected_gpu:
        raise ValueError("expected_gpu must not be empty.")

    checks: list[HardwareAcceptanceCheck] = []
    detected: tuple[str, ...]
    try:
        detected = (
            tuple(video_controllers)
            if video_controllers is not None
            else detect_windows_video_controllers()
        )
    except HardwareAcceptanceError as exc:
        detected = ()
        checks.append(HardwareAcceptanceCheck("target-gpu", "FAIL", str(exc)))
        gpu_ready = False
    else:
        matched = next(
            (
                name
                for name in detected
                if _gpu_matches(normalized_expected_gpu, name)
            ),
            None,
        )
        gpu_ready = matched is not None
        if matched is None:
            listed = ", ".join(detected) or "<none>"
            checks.append(
                HardwareAcceptanceCheck(
                    "target-gpu",
                    "FAIL",
                    f"expected {normalized_expected_gpu}; detected {listed}",
                )
            )
        else:
            checks.append(
                HardwareAcceptanceCheck(
                    "target-gpu",
                    "PASS",
                    f"matched {matched}",
                )
            )

    active_provider: _AcceptanceProvider = provider or LMStudioProvider(
        base_url=settings.lm_studio_base_url,
        timeout_seconds=settings.model_request_timeout_seconds,
        generation_timeout_seconds=settings.model_generation_timeout_seconds,
    )
    selected_model: ModelInfo | None = None
    try:
        selected_model = _select_loaded_llm(active_provider, requested_model_id)
    except (HardwareAcceptanceError, ModelProviderError) as exc:
        checks.append(HardwareAcceptanceCheck("lm-studio-model", "FAIL", str(exc)))
        model_ready = False
    else:
        model_ready = True
        checks.append(
            HardwareAcceptanceCheck(
                "lm-studio-model",
                "PASS",
                f"loaded {selected_model.backend_model_id} at {active_provider.base_url}",
            )
        )

    inference_ready = False
    if selected_model is None:
        checks.append(
            HardwareAcceptanceCheck(
                "live-inference",
                "SKIP",
                "no loaded LM Studio LLM passed selection",
            )
        )
    else:
        try:
            response = _run_live_inference(active_provider, selected_model)
        except (HardwareAcceptanceError, ModelProviderError) as exc:
            checks.append(HardwareAcceptanceCheck("live-inference", "FAIL", str(exc)))
        else:
            inference_ready = True
            checks.append(
                HardwareAcceptanceCheck(
                    "live-inference",
                    "PASS",
                    f"received {INFERENCE_MARKER}; response_chars={len(response)}",
                )
            )

    return HardwareAcceptanceReport(
        checks=tuple(checks),
        expected_gpu=normalized_expected_gpu,
        detected_gpus=detected,
        selected_model_id=(
            selected_model.backend_model_id if selected_model is not None else None
        ),
        gpu_ready=gpu_ready,
        model_ready=model_ready,
        inference_ready=inference_ready,
    )


def _report_payload(report: HardwareAcceptanceReport) -> dict[str, object]:
    return {
        "version": __version__,
        "platform": platform.platform(),
        "python": sys.version.replace("\n", " "),
        "expected_gpu": report.expected_gpu,
        "detected_gpus": list(report.detected_gpus),
        "selected_model_id": report.selected_model_id,
        "gpu_ready": report.gpu_ready,
        "model_ready": report.model_ready,
        "inference_ready": report.inference_ready,
        "overall_ready": report.overall_ready,
        "checks": [
            {"name": check.name, "status": check.status, "detail": check.detail}
            for check in report.checks
        ],
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pathena-hardware-acceptance",
        description=(
            "Verify the actual Windows GPU and one real LM Studio inference for pATHENA."
        ),
    )
    parser.add_argument(
        "--expected-gpu",
        default=os.environ.get("PATHENA_EXPECTED_GPU", DEFAULT_EXPECTED_GPU),
        help=f"Expected Windows GPU name (default: {DEFAULT_EXPECTED_GPU}).",
    )
    parser.add_argument(
        "--model-id",
        default=None,
        help="Require one specific already-loaded LM Studio LLM id.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit the full machine-readable report to stdout.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Also write the machine-readable report to this JSON file.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        settings = AthenaSettings.from_environment()
        report = run_hardware_acceptance(
            settings,
            expected_gpu=args.expected_gpu,
            requested_model_id=args.model_id,
        )
        payload = _report_payload(report)
    except (ConfigurationError, ValueError) as exc:
        payload = {
            "version": __version__,
            "overall_ready": False,
            "checks": [
                {"name": "configuration", "status": "FAIL", "detail": str(exc)}
            ],
        }
        rendered = json.dumps(payload, indent=2, sort_keys=True)
        if args.output is not None:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered + "\n", encoding="utf-8")
        if args.json:
            print(json.dumps(payload, sort_keys=True))
        else:
            print(f"[FAIL] configuration: {exc}")
        return 5

    rendered = json.dumps(payload, indent=2, sort_keys=True)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(payload, sort_keys=True))
    else:
        print(f"pATHENA local hardware acceptance {__version__}")
        for check in report.checks:
            print(f"[{check.status}] {check.name}: {check.detail}")
        print(f"Target hardware ready: {'YES' if report.overall_ready else 'NO'}")

    if not report.gpu_ready:
        return 2
    if not report.model_ready:
        return 3
    if not report.inference_ready:
        return 4
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
