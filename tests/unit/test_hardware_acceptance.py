from __future__ import annotations

from collections.abc import Iterator, Sequence
from pathlib import Path

from athena.config.settings import AthenaSettings
from athena.desktop.system_hardware_acceptance import (
    hardware_acceptance_launch_spec,
    project_hardware_acceptance_payload,
)
from athena.hardware_acceptance import (
    DEFAULT_EXPECTED_GPU,
    INFERENCE_MARKER,
    _video_controller_names_from_payload,
    run_hardware_acceptance,
)
from athena.model.domain import ModelChatMessage, ModelInfo


def _settings() -> AthenaSettings:
    return AthenaSettings.from_environment()


def _model(*, model_id: str = "local-model", loaded: bool = True) -> ModelInfo:
    return ModelInfo(
        provider="lm_studio",
        backend_model_id=model_id,
        display_name=model_id,
        model_type="llm",
        context_capacity=8192,
        quantization="test",
        loaded=loaded,
        vision=None,
        trained_for_tool_use=None,
    )


class _Provider:
    base_url = "http://127.0.0.1:1234"

    def __init__(
        self,
        *,
        models: tuple[ModelInfo, ...] | None = None,
        response: str = INFERENCE_MARKER,
    ) -> None:
        self.models = models if models is not None else (_model(),)
        self.response = response
        self.calls: list[dict[str, object]] = []

    def discover_models(self) -> tuple[ModelInfo, ...]:
        return self.models

    def stream_chat(
        self,
        *,
        model_id: str,
        messages: Sequence[ModelChatMessage],
        max_output_tokens: int | None = None,
        reasoning_mode: str | None = None,
        temperature: float | None = None,
    ) -> Iterator[str]:
        self.calls.append(
            {
                "model_id": model_id,
                "messages": tuple(messages),
                "max_output_tokens": max_output_tokens,
                "reasoning_mode": reasoning_mode,
                "temperature": temperature,
            }
        )
        yield self.response


def test_video_controller_payload_normalizes_single_and_multiple_names() -> None:
    assert _video_controller_names_from_payload(
        '{"names":"AMD Radeon RX 7900 XTX"}'
    ) == ("AMD Radeon RX 7900 XTX",)
    assert _video_controller_names_from_payload(
        '{"names":["AMD Radeon RX 7900 XTX","Microsoft Basic Display Adapter"]}'
    ) == (
        "AMD Radeon RX 7900 XTX",
        "Microsoft Basic Display Adapter",
    )


def test_target_hardware_passes_only_after_real_inference_marker() -> None:
    provider = _Provider()

    report = run_hardware_acceptance(
        _settings(),
        video_controllers=(DEFAULT_EXPECTED_GPU,),
        provider=provider,
    )

    assert report.gpu_ready is True
    assert report.model_ready is True
    assert report.inference_ready is True
    assert report.overall_ready is True
    assert report.selected_model_id == "local-model"
    assert provider.calls[0]["model_id"] == "local-model"
    assert provider.calls[0]["reasoning_mode"] == "off"
    assert provider.calls[0]["temperature"] == 0.0
    assert provider.calls[0]["max_output_tokens"] == 32
    messages = provider.calls[0]["messages"]
    assert isinstance(messages, tuple)
    assert INFERENCE_MARKER in messages[0].content


def test_wrong_gpu_keeps_model_and_inference_evidence_but_fails_overall() -> None:
    report = run_hardware_acceptance(
        _settings(),
        video_controllers=("Microsoft Basic Display Adapter",),
        provider=_Provider(),
    )

    assert report.gpu_ready is False
    assert report.model_ready is True
    assert report.inference_ready is True
    assert report.overall_ready is False
    assert report.checks[0].status == "FAIL"


def test_no_loaded_llm_skips_live_inference() -> None:
    provider = _Provider(models=(_model(loaded=False),))

    report = run_hardware_acceptance(
        _settings(),
        video_controllers=(DEFAULT_EXPECTED_GPU,),
        provider=provider,
    )

    assert report.gpu_ready is True
    assert report.model_ready is False
    assert report.inference_ready is False
    assert report.overall_ready is False
    assert provider.calls == []
    assert report.checks[-1].status == "SKIP"


def test_specific_loaded_model_can_be_required() -> None:
    provider = _Provider(models=(_model(model_id="a"), _model(model_id="b")))

    report = run_hardware_acceptance(
        _settings(),
        requested_model_id="b",
        video_controllers=(DEFAULT_EXPECTED_GPU,),
        provider=provider,
    )

    assert report.selected_model_id == "b"
    assert provider.calls[0]["model_id"] == "b"
    assert report.overall_ready is True


def test_inference_without_marker_fails_even_when_transport_completed() -> None:
    report = run_hardware_acceptance(
        _settings(),
        video_controllers=(DEFAULT_EXPECTED_GPU,),
        provider=_Provider(response="some other local model response"),
    )

    assert report.gpu_ready is True
    assert report.model_ready is True
    assert report.inference_ready is False
    assert report.overall_ready is False
    assert report.checks[-1].name == "live-inference"
    assert report.checks[-1].status == "FAIL"


def test_system_ui_uses_the_same_hardware_acceptance_worker_contract(tmp_path: Path) -> None:
    report_path = tmp_path / "hardware-acceptance.json"

    program, arguments = hardware_acceptance_launch_spec(
        r"C:\pATHENA\pATHENA-Worker.exe",
        report_path,
    )

    assert program == r"C:\pATHENA\pATHENA-Worker.exe"
    assert arguments == (
        "-m",
        "athena.hardware_acceptance",
        "--output",
        str(report_path),
        "--json",
    )


def test_system_ui_projects_successful_machine_report_without_inventing_evidence() -> None:
    presentation = project_hardware_acceptance_payload(
        {
            "overall_ready": True,
            "detected_gpus": [DEFAULT_EXPECTED_GPU],
            "selected_model_id": "local-model",
            "checks": [],
        }
    )

    assert presentation.status == "PASS"
    assert presentation.state == "success"
    assert DEFAULT_EXPECTED_GPU in presentation.detail
    assert "local-model" in presentation.detail
    assert "live inference passed" in presentation.detail


def test_system_ui_surfaces_real_failure_detail() -> None:
    presentation = project_hardware_acceptance_payload(
        {
            "overall_ready": False,
            "detected_gpus": ["Microsoft Basic Display Adapter"],
            "selected_model_id": None,
            "checks": [
                {
                    "name": "target-gpu",
                    "status": "FAIL",
                    "detail": "expected AMD Radeon RX 7900 XTX; detected Microsoft Basic Display Adapter",
                }
            ],
        }
    )

    assert presentation.status == "FAIL"
    assert presentation.state == "error"
    assert presentation.detail.startswith("expected AMD Radeon RX 7900 XTX")
