from __future__ import annotations

import json
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PySide6")

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QApplication, QWidget

from athena.desktop.pathena_comfyui import (
    ComfyUiClient,
    ComfyUiError,
    install_comfyui_integration,
    load_api_workflow,
)

_GIB = 1024**3


class _Handler(BaseHTTPRequestHandler):
    posted: list[dict[str, object]] = []
    freed: list[dict[str, object]] = []
    queue_running: list[list[object]] = []
    queue_pending: list[list[object]] = []
    history: dict[str, object] = {}
    system_stats: dict[str, object] = {
        "system": {"comfyui_version": "test-local"},
        "devices": [
            {
                "name": "diagnostic-gpu",
                "vram_total": 24 * _GIB,
                "vram_free": 18 * _GIB,
            }
        ],
    }

    def log_message(self, _format: str, *_args: object) -> None:
        return

    def _json(self, payload: dict[str, object]) -> None:
        body = json.dumps(payload).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/system_stats":
            self._json(type(self).system_stats)
            return
        if self.path == "/queue":
            self._json(
                {
                    "queue_running": type(self).queue_running,
                    "queue_pending": type(self).queue_pending,
                }
            )
            return
        if self.path.startswith("/history/"):
            prompt_id = self.path.removeprefix("/history/")
            payload = (
                {prompt_id: type(self).history[prompt_id]}
                if prompt_id in type(self).history
                else {}
            )
            self._json(payload)
            return
        self.send_error(404)

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length", "0"))
        payload = json.loads(self.rfile.read(length).decode()) if length else {}
        if self.path == "/prompt":
            type(self).posted.append(payload)
            self._json(
                {"prompt_id": "prompt-local-1", "number": 7, "node_errors": {}}
            )
            return
        if self.path == "/free":
            type(self).freed.append(payload)
            self.send_response(200)
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        self.send_error(404)


@pytest.fixture
def local_comfyui():
    _Handler.posted.clear()
    _Handler.freed.clear()
    _Handler.queue_running = []
    _Handler.queue_pending = []
    _Handler.history = {}
    _Handler.system_stats = {
        "system": {"comfyui_version": "test-local"},
        "devices": [
            {
                "name": "diagnostic-gpu",
                "vram_total": 24 * _GIB,
                "vram_free": 18 * _GIB,
            }
        ],
    }
    server = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def _workflow() -> dict[str, object]:
    return {
        "1": {
            "class_type": "KSampler",
            "inputs": {"seed": 1},
        }
    }


def _queue_item(prompt_id: str) -> list[object]:
    return [1, prompt_id, _workflow(), {}, ["1"]]


def _app() -> QApplication:
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        return existing
    return QApplication([])


class _Palette(QObject):
    def __init__(self, window: QWidget) -> None:
        super().__init__(window)
        self.window = window
        self._commands = ()


@pytest.mark.parametrize(
    "endpoint",
    [
        "https://127.0.0.1:8188",
        "http://example.com:8188",
        "http://127.0.0.1:8188/api",
        "http://user@127.0.0.1:8188",
        "http://127.0.0.1:8188/?token=secret",
    ],
)
def test_client_rejects_non_loopback_or_non_root_endpoints(endpoint: str) -> None:
    with pytest.raises(ComfyUiError):
        ComfyUiClient(endpoint)


def test_proxy_environment_cannot_capture_loopback_health(
    local_comfyui: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("HTTP_PROXY", "http://127.0.0.1:9")
    monkeypatch.setenv("HTTPS_PROXY", "http://127.0.0.1:9")
    monkeypatch.setenv("NO_PROXY", "")

    health = ComfyUiClient(local_comfyui).health()

    assert health.version == "test-local"
    assert health.device_count == 1
    assert health.vram_total_bytes == 24 * _GIB
    assert health.vram_free_bytes == 18 * _GIB


def test_health_keeps_vram_truthfully_unavailable_when_stats_omit_it(
    local_comfyui: str,
) -> None:
    _Handler.system_stats = {
        "system": {"comfyui_version": "test-local"},
        "devices": [{"name": "diagnostic-gpu"}],
    }

    health = ComfyUiClient(local_comfyui).health()

    assert health.device_count == 1
    assert health.vram_total_bytes is None
    assert health.vram_free_bytes is None


def test_queue_uses_real_prompt_contract(local_comfyui: str) -> None:
    receipt = ComfyUiClient(local_comfyui).queue_workflow(_workflow())

    assert receipt.prompt_id == "prompt-local-1"
    assert _Handler.posted == [{"prompt": _workflow()}]


def test_prompt_state_reads_queue_before_history(local_comfyui: str) -> None:
    client = ComfyUiClient(local_comfyui)

    _Handler.queue_pending = [_queue_item("prompt-local-1")]
    assert client.prompt_state("prompt-local-1").state == "pending"

    _Handler.queue_pending = []
    _Handler.queue_running = [_queue_item("prompt-local-1")]
    assert client.prompt_state("prompt-local-1").state == "running"

    _Handler.queue_running = []
    _Handler.history = {"prompt-local-1": {"outputs": {}, "status": {}}}
    assert client.prompt_state("prompt-local-1").state == "completed"

    _Handler.history = {}
    assert client.prompt_state("prompt-local-1").state == "unknown"


def test_release_vram_uses_explicit_local_free_contract(local_comfyui: str) -> None:
    ComfyUiClient(local_comfyui).release_vram()

    assert _Handler.freed == [{"unload_models": True, "free_memory": True}]


def test_api_workflow_validation_rejects_ui_graph(tmp_path: Path) -> None:
    path = tmp_path / "workflow.json"
    path.write_text(json.dumps({"nodes": [], "links": []}), encoding="utf-8")

    with pytest.raises(ComfyUiError, match="API format"):
        load_api_workflow(path)


def test_dialog_projects_measured_vram_and_reference_hierarchy(
    local_comfyui: str,
) -> None:
    _app()
    window = QWidget()
    palette = _Palette(window)
    controller = install_comfyui_integration(  # type: ignore[arg-type]
        palette,
        client=ComfyUiClient(local_comfyui),
    )

    assert controller.check_connection() is True
    assert controller.dialog.property("pathenaComfyUiVramAvailable") is True
    assert controller.dialog.property("pathenaComfyUiVramTotalBytes") == 24 * _GIB
    assert controller.dialog.property("pathenaComfyUiVramFreeBytes") == 18 * _GIB
    assert "6.0 GiB used" in controller.resource_status.text()
    assert controller.check_button.text() == "Check again"
    assert controller.dialog.findChild(QLabel, "comfyUiSectionLabel") is not None


def test_dialog_shows_unavailable_vram_without_inventing_metrics(
    local_comfyui: str,
) -> None:
    _Handler.system_stats = {
        "system": {"comfyui_version": "test-local"},
        "devices": [{"name": "diagnostic-gpu"}],
    }
    _app()
    window = QWidget()
    palette = _Palette(window)
    controller = install_comfyui_integration(  # type: ignore[arg-type]
        palette,
        client=ComfyUiClient(local_comfyui),
    )

    assert controller.check_connection() is True
    assert controller.dialog.property("pathenaComfyUiVramAvailable") is False
    assert "unavailable" in controller.resource_status.text().lower()


def test_dialog_exposes_retry_state_when_local_endpoint_is_unreachable() -> None:
    _app()
    window = QWidget()
    palette = _Palette(window)
    controller = install_comfyui_integration(  # type: ignore[arg-type]
        palette,
        client=ComfyUiClient("http://127.0.0.1:9", timeout=0.05),
    )

    assert controller.check_connection() is False
    assert controller.check_button.text() == "Retry connection"
    assert controller.dialog.property("pathenaUiState") == "error"
    assert controller.dialog.property("pathenaComfyUiVramAvailable") is False
    assert "disconnected" in controller.resource_status.text().lower()


def test_dialog_loads_checks_queues_tracks_and_releases_local_resources(
    local_comfyui: str,
    tmp_path: Path,
) -> None:
    _app()
    window = QWidget()
    palette = _Palette(window)
    controller = install_comfyui_integration(  # type: ignore[arg-type]
        palette,
        client=ComfyUiClient(local_comfyui),
    )
    workflow_path = tmp_path / "api-workflow.json"
    workflow_path.write_text(json.dumps(_workflow()), encoding="utf-8")

    controller.load_workflow(workflow_path)
    assert controller.queue_button.isEnabled()
    assert controller.check_connection() is True
    assert controller.queue_selected_workflow() is True
    assert controller.refresh_job_button.isEnabled()

    _Handler.queue_pending = [_queue_item("prompt-local-1")]
    assert controller.refresh_prompt_status() is True
    assert controller.dialog.property("pathenaComfyUiPromptState") == "pending"

    assert controller.release_vram() is True
    assert controller.dialog.property("pathenaComfyUiVramReleaseRequested") is True
    assert "check the local endpoint again" in controller.resource_status.text()

    assert controller.dialog.objectName() == "comfyUiDialog"
    assert controller.dialog.property("pathenaComfyUiLocalOnly") is True
    assert controller.dialog.property("pathenaComfyUiGlobalInterruptAvailable") is False
    assert controller.receipt.property("pathenaComfyUiPromptId") == "prompt-local-1"
    assert "Open ComfyUI" in {command.label for command in palette._commands}
