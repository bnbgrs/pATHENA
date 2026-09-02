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
from PySide6.QtWidgets import QApplication, QLabel, QWidget

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
        body = self.rfile.read(length) if length else b"{}"
        payload = json.loads(body)
        if self.path == "/prompt":
            type(self).posted.append(payload)
            self._json({"prompt_id": "prompt-1"})
            return
        if self.path == "/free":
            type(self).freed.append(payload)
            self._json({"ok": True})
            return
        self.send_error(404)


@pytest.fixture
def comfyui_server() -> tuple[str, type[_Handler]]:
    _Handler.posted = []
    _Handler.freed = []
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
    host, port = server.server_address
    try:
        yield f"http://{host}:{port}", _Handler
    finally:
        server.shutdown()
        thread.join(timeout=2)
        server.server_close()


@pytest.fixture
def qt_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    assert isinstance(app, QApplication)
    return app


class _Palette(QObject):
    def __init__(self, window: QWidget) -> None:
        super().__init__(window)
        self.window = window
        self._commands: tuple[object, ...] = ()


def _workflow_file(tmp_path: Path) -> Path:
    path = tmp_path / "workflow.json"
    path.write_text(json.dumps({"1": {"class_type": "KSampler", "inputs": {}}}))
    return path


def test_client_projects_live_system_stats(comfyui_server: tuple[str, type[_Handler]]) -> None:
    endpoint, _handler = comfyui_server
    client = ComfyUiClient(endpoint)

    snapshot = client.health()

    assert snapshot.endpoint == endpoint
    assert snapshot.version == "test-local"
    assert snapshot.device_count == 1
    assert snapshot.vram_total_bytes == 24 * _GIB
    assert snapshot.vram_free_bytes == 18 * _GIB


def test_client_reports_unavailable_vram_without_inventing_values(
    comfyui_server: tuple[str, type[_Handler]],
) -> None:
    endpoint, handler = comfyui_server
    handler.system_stats = {"system": {"comfyui_version": "test-local"}, "devices": []}
    client = ComfyUiClient(endpoint)

    snapshot = client.health()

    assert snapshot.version == "test-local"
    assert snapshot.device_count == 0
    assert snapshot.vram_total_bytes is None
    assert snapshot.vram_free_bytes is None


def test_client_queue_and_free_are_explicit_requests(
    comfyui_server: tuple[str, type[_Handler]], tmp_path: Path
) -> None:
    endpoint, handler = comfyui_server
    client = ComfyUiClient(endpoint)
    workflow = load_api_workflow(_workflow_file(tmp_path))

    receipt = client.queue_workflow(workflow)
    client.release_vram()

    assert receipt.prompt_id == "prompt-1"
    assert receipt.node_errors == {}
    assert handler.posted == [{"prompt": workflow}]
    assert handler.freed == [{"unload_models": True, "free_memory": True}]


def test_dialog_projects_measured_vram_and_reference_hierarchy(
    qt_app: QApplication,
    comfyui_server: tuple[str, type[_Handler]],
    tmp_path: Path,
) -> None:
    endpoint, _handler = comfyui_server
    host = QWidget()
    palette = _Palette(host)
    controller = install_comfyui_integration(palette, client=ComfyUiClient(endpoint))
    dialog = controller.dialog
    controller.load_workflow(_workflow_file(tmp_path))

    assert controller.check_connection() is True
    qt_app.processEvents()

    assert controller.status.text() == "Connected · ComfyUI test-local · 1 device."
    assert controller.status.property("pathenaUiState") == "success"
    assert controller.resource_status.text() == (
        "VRAM · 6.0 GiB used · 18.0 GiB free · 24.0 GiB total"
    )
    assert dialog.property("pathenaComfyUiVramAvailable") is True
    assert [
        label.text()
        for label in dialog.findChildren(QLabel)
        if label.objectName() == "comfyUiSectionLabel"
    ] == ["CONNECTION", "WORKFLOW", "ACTIVITY"]
    assert controller.queue_button.isEnabled()

    controller.deleteLater()
    dialog.deleteLater()
    palette.deleteLater()
    host.deleteLater()


def test_dialog_exposes_retry_state_after_disconnect(
    qt_app: QApplication,
    tmp_path: Path,
) -> None:
    host = QWidget()
    palette = _Palette(host)
    controller = install_comfyui_integration(
        palette,
        client=ComfyUiClient("http://127.0.0.1:9", timeout=0.05),
    )
    dialog = controller.dialog
    controller.load_workflow(_workflow_file(tmp_path))

    assert controller.check_connection() is False
    qt_app.processEvents()

    assert controller.status.property("pathenaUiState") == "error"
    assert dialog.property("pathenaComfyUiVramAvailable") is False
    assert "unavailable" in controller.resource_status.text()
    assert "Retry" in controller.check_button.text()

    controller.deleteLater()
    dialog.deleteLater()
    palette.deleteLater()
    host.deleteLater()


def test_dialog_tab_order_reaches_reference_actions(qt_app: QApplication) -> None:
    host = QWidget()
    palette = _Palette(host)
    controller = install_comfyui_integration(palette)

    assert controller.check_button.nextInFocusChain() is controller.browse_button
    assert controller.browse_button.nextInFocusChain() is controller.queue_button
    assert controller.queue_button.nextInFocusChain() is controller.refresh_job_button
    assert controller.refresh_job_button.nextInFocusChain() is controller.release_vram_button

    controller.deleteLater()
    controller.dialog.deleteLater()
    palette.deleteLater()
    host.deleteLater()


def test_invalid_endpoint_fails_closed() -> None:
    with pytest.raises(ComfyUiError, match="local HTTP"):
        ComfyUiClient("https://example.com:8188")
    with pytest.raises(ComfyUiError, match="loopback"):
        ComfyUiClient("http://example.com:8188")
