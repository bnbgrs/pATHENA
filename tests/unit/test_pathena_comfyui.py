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


class _Handler(BaseHTTPRequestHandler):
    posted: list[dict[str, object]] = []

    def log_message(self, _format: str, *_args: object) -> None:
        return

    def do_GET(self) -> None:  # noqa: N802
        if self.path != "/system_stats":
            self.send_error(404)
            return
        body = json.dumps(
            {
                "system": {"comfyui_version": "test-local"},
                "devices": [{"name": "diagnostic-gpu"}],
            }
        ).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/prompt":
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length", "0"))
        payload = json.loads(self.rfile.read(length).decode())
        type(self).posted.append(payload)
        body = json.dumps(
            {"prompt_id": "prompt-local-1", "number": 7, "node_errors": {}}
        ).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


@pytest.fixture
def local_comfyui():
    _Handler.posted.clear()
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


def _app() -> QApplication:
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        return existing
    return QApplication([])


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


def test_queue_uses_real_prompt_contract(local_comfyui: str) -> None:
    receipt = ComfyUiClient(local_comfyui).queue_workflow(_workflow())

    assert receipt.prompt_id == "prompt-local-1"
    assert _Handler.posted == [{"prompt": _workflow()}]


def test_api_workflow_validation_rejects_ui_graph(tmp_path: Path) -> None:
    path = tmp_path / "workflow.json"
    path.write_text(json.dumps({"nodes": [], "links": []}), encoding="utf-8")

    with pytest.raises(ComfyUiError, match="API format"):
        load_api_workflow(path)


def test_dialog_loads_checks_and_queues_local_workflow(
    local_comfyui: str,
    tmp_path: Path,
) -> None:
    _app()
    window = QWidget()

    class _Palette(QObject):
        def __init__(self) -> None:
            super().__init__(window)
            self.window = window
            self._commands = ()

    palette = _Palette()
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

    assert controller.dialog.objectName() == "comfyUiDialog"
    assert controller.dialog.property("pathenaComfyUiLocalOnly") is True
    assert controller.receipt.property("pathenaComfyUiPromptId") == "prompt-local-1"
    assert "Open ComfyUI" in {command.label for command in palette._commands}
