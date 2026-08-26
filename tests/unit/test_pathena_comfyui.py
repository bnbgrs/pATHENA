from __future__ import annotations

import json
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PySide6")

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


def _workflow_file(tmp_path: Path) -> Path:
    path = tmp_path / "workflow.json"
    path.write_text(json.dumps({"1": {"class_type": "KSampler", "inputs": {}}}))
    return path


def test_client_projects_live_system_stats(comfyui_server: tuple[str, type[_Handler]]) -> None:
    endpoint, _handler = comfyui_server
    client = ComfyUiClient(endpoint)

    snapshot = client.probe()

    assert snapshot.connected is True
    assert snapshot.endpoint == endpoint
    assert snapshot.vram_total_bytes == 24 * _GIB
    assert snapshot.vram_free_bytes == 18 * _GIB
    assert snapshot.device_name == "diagnostic-gpu"


def test_client_reports_unavailable_vram_without_inventing_values(
    comfyui_server: tuple[str, type[_Handler]],
) -> None:
    endpoint, handler = comfyui_server
    handler.system_stats = {"system": {"comfyui_version": "test-local"}, "devices": []}
    client = ComfyUiClient(endpoint)

    snapshot = client.probe()

    assert snapshot.connected is True
    assert snapshot.vram_total_bytes is None
    assert snapshot.vram_free_bytes is None
    assert snapshot.device_name is None


def test_client_queue_and_free_are_explicit_requests(
    comfyui_server: tuple[str, type[_Handler]], tmp_path: Path
) -> None:
    endpoint, handler = comfyui_server
    client = ComfyUiClient(endpoint)
    workflow = load_api_workflow(_workflow_file(tmp_path))

    prompt_id = client.queue_prompt(workflow)
    client.free_memory(unload_models=True)

    assert prompt_id == "prompt-1"
    assert handler.posted == [{"prompt": workflow}]
    assert handler.freed == [{"unload_models": True, "free_memory": True}]


def test_dialog_projects_measured_vram_and_reference_hierarchy(
    qt_app: QApplication,
    comfyui_server: tuple[str, type[_Handler]],
    tmp_path: Path,
) -> None:
    endpoint, _handler = comfyui_server
    host = QWidget()
    controller = install_comfyui_integration(host)
    dialog = controller.dialog
    dialog.endpoint_edit.setText(endpoint)
    dialog.workflow_edit.setText(str(_workflow_file(tmp_path)))

    dialog.refresh_connection()
    qt_app.processEvents()

    assert dialog.connection_state.text() == "Connected"
    assert dialog.connection_state.property("state") == "connected"
    assert dialog.vram_value.text() == "18.0 GiB free / 24.0 GiB total"
    assert dialog.device_value.text() == "diagnostic-gpu"
    assert [
        label.text()
        for label in dialog.findChildren(QLabel)
        if label.objectName() == "sectionLabel"
    ] == ["Connection", "Workflow", "Activity"]
    assert dialog.run_button.isEnabled()

    controller.deleteLater()
    dialog.deleteLater()
    host.deleteLater()


def test_dialog_exposes_retry_state_after_disconnect(
    qt_app: QApplication,
    tmp_path: Path,
) -> None:
    host = QWidget()
    controller = install_comfyui_integration(host)
    dialog = controller.dialog
    dialog.endpoint_edit.setText("http://127.0.0.1:9")
    dialog.workflow_edit.setText(str(_workflow_file(tmp_path)))

    dialog.refresh_connection()
    qt_app.processEvents()

    assert dialog.connection_state.text() == "Disconnected"
    assert dialog.connection_state.property("state") == "disconnected"
    assert dialog.run_button.isEnabled() is False
    assert "Retry" in dialog.refresh_button.text()

    controller.deleteLater()
    dialog.deleteLater()
    host.deleteLater()


def test_dialog_tab_order_reaches_reference_actions(qt_app: QApplication) -> None:
    host = QWidget()
    controller = install_comfyui_integration(host)
    dialog = controller.dialog

    assert dialog.endpoint_edit.nextInFocusChain() is dialog.refresh_button
    assert dialog.refresh_button.nextInFocusChain() is dialog.workflow_edit
    assert dialog.workflow_edit.nextInFocusChain() is dialog.run_button
    assert dialog.run_button.nextInFocusChain() is dialog.release_vram_button

    controller.deleteLater()
    dialog.deleteLater()
    host.deleteLater()


def test_invalid_endpoint_fails_closed() -> None:
    with pytest.raises(ComfyUiError, match="loopback"):
        ComfyUiClient("https://example.com:8188")
