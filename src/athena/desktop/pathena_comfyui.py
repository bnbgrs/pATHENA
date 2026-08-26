"""Local-only ComfyUI bridge and compact desktop surface."""

from __future__ import annotations

import ipaddress
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PySide6.QtCore import QObject, Qt
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from athena.desktop.command_palette import CommandPaletteController, _Command

DEFAULT_COMFYUI_URL = "http://127.0.0.1:8188"
COMFYUI_URL_ENV = "PATHENA_COMFYUI_URL"
_GIB = 1024**3


class ComfyUiError(RuntimeError):
    """Raised when the local ComfyUI contract cannot be used truthfully."""


@dataclass(frozen=True, slots=True)
class ComfyUiHealth:
    endpoint: str
    version: str | None
    device_count: int
    vram_total_bytes: int | None = None
    vram_free_bytes: int | None = None


@dataclass(frozen=True, slots=True)
class ComfyUiQueueReceipt:
    prompt_id: str
    number: float | int | None
    node_errors: dict[str, Any]


@dataclass(frozen=True, slots=True)
class ComfyUiQueueSnapshot:
    running_prompt_ids: tuple[str, ...]
    pending_prompt_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ComfyUiPromptState:
    prompt_id: str
    state: str


def _loopback_endpoint(value: str) -> str:
    raw = value.strip()
    if not raw:
        raise ComfyUiError("ComfyUI endpoint must not be empty.")
    parsed = urllib.parse.urlsplit(raw)
    if parsed.scheme != "http":
        raise ComfyUiError("ComfyUI must use local HTTP.")
    if parsed.username is not None or parsed.password is not None:
        raise ComfyUiError("ComfyUI endpoint must not contain user information.")
    if parsed.query or parsed.fragment:
        raise ComfyUiError("ComfyUI endpoint must not contain a query or fragment.")
    if parsed.path not in ("", "/"):
        raise ComfyUiError("ComfyUI endpoint must point to the local server root.")
    hostname = parsed.hostname
    if hostname is None:
        raise ComfyUiError("ComfyUI endpoint has no host.")
    normalized_host = hostname.casefold()
    if normalized_host == "localhost":
        pass
    else:
        try:
            address = ipaddress.ip_address(hostname)
        except ValueError as exc:
            raise ComfyUiError("ComfyUI endpoint must use localhost or a loopback IP.") from exc
        if not address.is_loopback:
            raise ComfyUiError("ComfyUI endpoint must use a loopback IP.")
    port = parsed.port
    netloc = f"[{hostname}]" if ":" in hostname else hostname
    if port is not None:
        netloc = f"{netloc}:{port}"
    return urllib.parse.urlunsplit(("http", netloc, "", "", ""))


def load_api_workflow(path: str | Path) -> dict[str, Any]:
    workflow_path = Path(path)
    try:
        data = json.loads(workflow_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ComfyUiError(f"Could not read ComfyUI API workflow: {exc}") from exc
    if not isinstance(data, dict) or not data:
        raise ComfyUiError("ComfyUI API workflow must be a non-empty JSON object.")
    if "nodes" in data and "links" in data:
        raise ComfyUiError(
            "This looks like a UI workflow. Export the workflow in ComfyUI API format."
        )
    for node_id, node in data.items():
        if not isinstance(node_id, str) or not isinstance(node, dict):
            raise ComfyUiError("ComfyUI API workflow nodes must be object entries.")
        if "class_type" not in node or not isinstance(node.get("inputs"), dict):
            raise ComfyUiError(
                "ComfyUI API workflow nodes require class_type and inputs."
            )
    return data


def _queue_prompt_ids(items: object) -> tuple[str, ...]:
    if not isinstance(items, list):
        raise ComfyUiError("Local ComfyUI queue response is incomplete.")
    prompt_ids: list[str] = []
    for item in items:
        if not isinstance(item, (list, tuple)) or len(item) < 2:
            raise ComfyUiError("Local ComfyUI queue item is malformed.")
        prompt_id = item[1]
        if not isinstance(prompt_id, str) or not prompt_id.strip():
            raise ComfyUiError("Local ComfyUI queue item has no prompt id.")
        prompt_ids.append(prompt_id)
    return tuple(prompt_ids)


def _device_vram(devices: list[object]) -> tuple[int | None, int | None]:
    totals: list[int] = []
    frees: list[int] = []
    for device in devices:
        if not isinstance(device, dict):
            continue
        total = device.get("vram_total")
        free = device.get("vram_free")
        if isinstance(total, (int, float)) and not isinstance(total, bool) and total >= 0:
            totals.append(int(total))
        if isinstance(free, (int, float)) and not isinstance(free, bool) and free >= 0:
            frees.append(int(free))
    total_bytes = sum(totals) if totals else None
    free_bytes = sum(frees) if frees and len(frees) == len(totals) else None
    return total_bytes, free_bytes


def _format_gib(value: int) -> str:
    return f"{value / _GIB:.1f} GiB"


class ComfyUiClient:
    """Small proxy-free HTTP client restricted to a loopback ComfyUI server."""

    def __init__(self, endpoint: str | None = None, *, timeout: float = 3.0) -> None:
        candidate = endpoint or os.environ.get(COMFYUI_URL_ENV, DEFAULT_COMFYUI_URL)
        self.endpoint = _loopback_endpoint(candidate)
        self.timeout = timeout
        self._opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

    def _request(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        body = None
        headers = {"Accept": "application/json"}
        if payload is not None:
            body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
            headers["Content-Type"] = "application/json"
        request = urllib.request.Request(
            self.endpoint + path,
            data=body,
            headers=headers,
            method=method,
        )
        try:
            with self._opener.open(request, timeout=self.timeout) as response:
                raw = response.read()
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise ComfyUiError(f"Local ComfyUI request failed: {exc}") from exc
        if not raw:
            return {}
        try:
            decoded = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ComfyUiError("Local ComfyUI returned invalid JSON.") from exc
        if not isinstance(decoded, dict):
            raise ComfyUiError("Local ComfyUI returned an unexpected response.")
        return decoded

    def health(self) -> ComfyUiHealth:
        payload = self._request("GET", "/system_stats")
        system = payload.get("system")
        devices = payload.get("devices")
        if not isinstance(system, dict) or not isinstance(devices, list):
            raise ComfyUiError("Local ComfyUI system_stats response is incomplete.")
        version = system.get("comfyui_version")
        total_vram, free_vram = _device_vram(devices)
        return ComfyUiHealth(
            endpoint=self.endpoint,
            version=str(version) if version else None,
            device_count=len(devices),
            vram_total_bytes=total_vram,
            vram_free_bytes=free_vram,
        )

    def queue_workflow(self, workflow: dict[str, Any]) -> ComfyUiQueueReceipt:
        if not isinstance(workflow, dict) or not workflow:
            raise ComfyUiError("ComfyUI API workflow must be a non-empty JSON object.")
        payload = self._request("POST", "/prompt", {"prompt": workflow})
        prompt_id = payload.get("prompt_id")
        if not isinstance(prompt_id, str) or not prompt_id.strip():
            error = payload.get("error")
            raise ComfyUiError(
                "ComfyUI did not queue the workflow"
                + (f": {error}" if error else ".")
            )
        node_errors = payload.get("node_errors", {})
        if not isinstance(node_errors, dict):
            node_errors = {}
        if node_errors:
            raise ComfyUiError("ComfyUI reported node validation errors.")
        number = payload.get("number")
        return ComfyUiQueueReceipt(prompt_id, number, node_errors)

    def queue_snapshot(self) -> ComfyUiQueueSnapshot:
        payload = self._request("GET", "/queue")
        return ComfyUiQueueSnapshot(
            running_prompt_ids=_queue_prompt_ids(payload.get("queue_running")),
            pending_prompt_ids=_queue_prompt_ids(payload.get("queue_pending")),
        )

    def prompt_state(self, prompt_id: str) -> ComfyUiPromptState:
        normalized = prompt_id.strip()
        if not normalized:
            raise ComfyUiError("ComfyUI prompt id must not be empty.")
        queue = self.queue_snapshot()
        if normalized in queue.running_prompt_ids:
            return ComfyUiPromptState(normalized, "running")
        if normalized in queue.pending_prompt_ids:
            return ComfyUiPromptState(normalized, "pending")

        encoded = urllib.parse.quote(normalized, safe="")
        history = self._request("GET", f"/history/{encoded}")
        if normalized in history:
            return ComfyUiPromptState(normalized, "completed")
        return ComfyUiPromptState(normalized, "unknown")

    def release_vram(self) -> None:
        self._request(
            "POST",
            "/free",
            {"unload_models": True, "free_memory": True},
        )


class ComfyUiController(QObject):
    """Truthful modeless surface for local ComfyUI workflow and resource operations."""

    def __init__(
        self,
        palette: CommandPaletteController,
        client: ComfyUiClient | None = None,
    ) -> None:
        super().__init__(palette)
        self.palette = palette
        self.window = palette.window
        self.client = client or ComfyUiClient()
        self.workflow: dict[str, Any] | None = None
        self.workflow_path: Path | None = None
        self.last_prompt_id: str | None = None

        self.dialog = QDialog(self.window)
        self.dialog.setObjectName("comfyUiDialog")
        self.dialog.setWindowTitle("ComfyUI")
        self.dialog.setModal(False)
        self.dialog.resize(760, 560)
        self.dialog.setAccessibleName("ComfyUI local workflow bridge")
        self.dialog.setAccessibleDescription(
            "Connect to local ComfyUI, choose and queue an API workflow, inspect its live "
            "state, and explicitly request model and VRAM release."
        )

        outer = QVBoxLayout(self.dialog)
        outer.setContentsMargins(28, 24, 28, 24)
        outer.setSpacing(12)

        title = QLabel("ComfyUI")
        title.setObjectName("comfyUiTitle")
        outer.addWidget(title)

        intro = QLabel("Local image + video workflow · loopback only")
        intro.setWordWrap(True)
        intro.setProperty("role", "muted")
        outer.addWidget(intro)

        connection_label = QLabel("CONNECTION")
        connection_label.setObjectName("comfyUiSectionLabel")
        connection_label.setProperty("role", "muted")
        outer.addWidget(connection_label)

        form = QFormLayout()
        form.setSpacing(8)
        self.endpoint = QLineEdit(self.client.endpoint)
        self.endpoint.setObjectName("comfyUiEndpoint")
        self.endpoint.setReadOnly(True)
        self.endpoint.setAccessibleName("ComfyUI local endpoint")
        form.addRow("Endpoint", self.endpoint)
        outer.addLayout(form)

        connection_actions = QHBoxLayout()
        self.check_button = QPushButton("Check connection")
        self.check_button.setObjectName("comfyUiCheckConnection")
        self.check_button.clicked.connect(self.check_connection)
        connection_actions.addWidget(self.check_button)
        connection_actions.addStretch(1)
        outer.addLayout(connection_actions)

        self.status = QLabel("Not checked · local endpoint has not been probed.")
        self.status.setObjectName("comfyUiStatus")
        self.status.setWordWrap(True)
        self.status.setProperty("pathenaUiState", "empty")
        self.status.setAccessibleName("ComfyUI connection status")
        outer.addWidget(self.status)

        self.resource_status = QLabel("VRAM · unavailable until the local endpoint is checked.")
        self.resource_status.setObjectName("comfyUiResourceStatus")
        self.resource_status.setWordWrap(True)
        self.resource_status.setProperty("role", "muted")
        self.resource_status.setAccessibleName("ComfyUI VRAM status")
        outer.addWidget(self.resource_status)

        workflow_label = QLabel("WORKFLOW")
        workflow_label.setObjectName("comfyUiSectionLabel")
        workflow_label.setProperty("role", "muted")
        outer.addWidget(workflow_label)

        self.workflow_field = QLineEdit()
        self.workflow_field.setObjectName("comfyUiWorkflowPath")
        self.workflow_field.setReadOnly(True)
        self.workflow_field.setPlaceholderText("No API workflow selected")
        self.workflow_field.setAccessibleName("ComfyUI API workflow")
        self.browse_button = QPushButton("Choose workflow…")
        self.browse_button.setObjectName("comfyUiBrowseWorkflow")
        self.browse_button.clicked.connect(self.choose_workflow)
        workflow_row = QHBoxLayout()
        workflow_row.addWidget(self.workflow_field, 1)
        workflow_row.addWidget(self.browse_button)
        outer.addLayout(workflow_row)

        workflow_actions = QHBoxLayout()
        self.queue_button = QPushButton("Queue workflow")
        self.queue_button.setObjectName("comfyUiQueueWorkflow")
        self.queue_button.setEnabled(False)
        self.queue_button.clicked.connect(self.queue_selected_workflow)
        workflow_actions.addWidget(self.queue_button)
        workflow_actions.addStretch(1)
        outer.addLayout(workflow_actions)

        self.receipt = QLabel("")
        self.receipt.setObjectName("comfyUiQueueReceipt")
        self.receipt.setWordWrap(True)
        self.receipt.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.receipt.setAccessibleName("ComfyUI queue receipt")
        outer.addWidget(self.receipt)

        activity_label = QLabel("ACTIVITY")
        activity_label.setObjectName("comfyUiSectionLabel")
        activity_label.setProperty("role", "muted")
        outer.addWidget(activity_label)

        operations = QHBoxLayout()
        self.refresh_job_button = QPushButton("Refresh job")
        self.refresh_job_button.setObjectName("comfyUiRefreshJob")
        self.refresh_job_button.setEnabled(False)
        self.refresh_job_button.clicked.connect(self.refresh_prompt_status)
        self.release_vram_button = QPushButton("Release VRAM")
        self.release_vram_button.setObjectName("comfyUiReleaseVram")
        self.release_vram_button.clicked.connect(self.release_vram)
        operations.addWidget(self.refresh_job_button)
        operations.addWidget(self.release_vram_button)
        operations.addStretch(1)
        outer.addLayout(operations)

        self.job_status = QLabel("No ComfyUI job tracked in this session.")
        self.job_status.setObjectName("comfyUiJobStatus")
        self.job_status.setWordWrap(True)
        self.job_status.setProperty("pathenaUiState", "empty")
        self.job_status.setAccessibleName("ComfyUI job status")
        outer.addWidget(self.job_status)
        outer.addStretch(1)

        self.dialog.setTabOrder(self.check_button, self.browse_button)
        self.dialog.setTabOrder(self.browse_button, self.queue_button)
        self.dialog.setTabOrder(self.queue_button, self.refresh_job_button)
        self.dialog.setTabOrder(self.refresh_job_button, self.release_vram_button)

        self.dialog.setProperty("pathenaComfyUiEndpoint", self.client.endpoint)
        self.dialog.setProperty("pathenaComfyUiLocalOnly", True)
        self.dialog.setProperty("pathenaComfyUiGlobalInterruptAvailable", False)
        self.dialog.setProperty("pathenaComfyUiVramAvailable", False)
        self.window.setProperty("pathenaComfyUiController", self)
        self.window.setProperty("pathenaComfyUiInstalled", True)

    def open(self) -> None:
        self.dialog.show()
        self.dialog.raise_()
        self.dialog.activateWindow()
        self.check_button.setFocus(Qt.FocusReason.OtherFocusReason)

    def choose_workflow(self) -> None:
        filename, _selected_filter = QFileDialog.getOpenFileName(
            self.dialog,
            "Choose ComfyUI API workflow",
            "",
            "JSON workflow (*.json)",
        )
        if filename:
            self.load_workflow(filename)

    def load_workflow(self, path: str | Path) -> None:
        try:
            workflow = load_api_workflow(path)
        except ComfyUiError as exc:
            self.workflow = None
            self.workflow_path = None
            self.workflow_field.clear()
            self.queue_button.setEnabled(False)
            self._set_status("error", str(exc))
            return
        self.workflow = workflow
        self.workflow_path = Path(path)
        self.workflow_field.setText(str(self.workflow_path))
        self.queue_button.setEnabled(True)
        self.receipt.clear()
        self._set_status(
            "ready",
            f"Workflow ready · {len(workflow)} nodes · queueing stays local.",
        )

    def check_connection(self) -> bool:
        try:
            health = self.client.health()
        except ComfyUiError as exc:
            self.check_button.setText("Retry connection")
            self._set_status("error", str(exc))
            self._set_vram_unavailable("VRAM · unavailable while ComfyUI is disconnected.")
            return False
        self.check_button.setText("Check again")
        version = f" · ComfyUI {health.version}" if health.version else ""
        self._set_status(
            "success",
            f"Connected{version} · {health.device_count} device"
            f"{'s' if health.device_count != 1 else ''}.",
        )
        self._set_vram_health(health)
        return True

    def queue_selected_workflow(self) -> bool:
        if self.workflow is None:
            self._set_status("error", "Select a valid ComfyUI API workflow first.")
            return False
        try:
            receipt = self.client.queue_workflow(self.workflow)
        except ComfyUiError as exc:
            self._set_status("error", str(exc))
            return False
        self.last_prompt_id = receipt.prompt_id
        self.refresh_job_button.setEnabled(True)
        self._set_status("success", "Workflow queued in local ComfyUI.")
        self.receipt.setText(f"Prompt ID · {receipt.prompt_id}")
        self.receipt.setProperty("pathenaComfyUiPromptId", receipt.prompt_id)
        self._set_job_status("pending", "Queued · refresh to read the live ComfyUI state.")
        return True

    def refresh_prompt_status(self) -> bool:
        if self.last_prompt_id is None:
            self._set_job_status("empty", "No ComfyUI job tracked in this session.")
            return False
        try:
            state = self.client.prompt_state(self.last_prompt_id)
        except ComfyUiError as exc:
            self._set_job_status("error", str(exc))
            return False
        labels = {
            "pending": "Pending in ComfyUI queue.",
            "running": "Running in ComfyUI.",
            "completed": "Completed in ComfyUI history.",
            "unknown": "Not present in current ComfyUI queue or history.",
        }
        self._set_job_status(state.state, labels[state.state])
        return True

    def release_vram(self) -> bool:
        try:
            self.client.release_vram()
        except ComfyUiError as exc:
            self._set_status("error", str(exc))
            return False
        self._set_status(
            "success",
            "VRAM release requested · ComfyUI will unload models and free memory when safe.",
        )
        self.resource_status.setText(
            "VRAM release requested · check the local endpoint again for measured memory."
        )
        self.dialog.setProperty("pathenaComfyUiVramReleaseRequested", True)
        return True

    def _set_vram_health(self, health: ComfyUiHealth) -> None:
        total = health.vram_total_bytes
        free = health.vram_free_bytes
        if total is None or free is None:
            self._set_vram_unavailable(
                "VRAM · unavailable from this local ComfyUI system_stats response."
            )
            return
        used = max(total - free, 0)
        text = f"VRAM · {_format_gib(used)} used · {_format_gib(free)} free · {_format_gib(total)} total"
        self.resource_status.setText(text)
        self.resource_status.setAccessibleDescription(text)
        self.dialog.setProperty("pathenaComfyUiVramAvailable", True)
        self.dialog.setProperty("pathenaComfyUiVramTotalBytes", total)
        self.dialog.setProperty("pathenaComfyUiVramFreeBytes", free)

    def _set_vram_unavailable(self, text: str) -> None:
        self.resource_status.setText(text)
        self.resource_status.setAccessibleDescription(text)
        self.dialog.setProperty("pathenaComfyUiVramAvailable", False)
        self.dialog.setProperty("pathenaComfyUiVramTotalBytes", None)
        self.dialog.setProperty("pathenaComfyUiVramFreeBytes", None)

    def _set_job_status(self, state: str, text: str) -> None:
        self.job_status.setText(text)
        self.job_status.setProperty("pathenaUiState", state)
        self.job_status.setAccessibleDescription(text)
        self.dialog.setProperty("pathenaComfyUiPromptState", state)

    def _set_status(self, state: str, text: str) -> None:
        self.status.setText(text)
        self.status.setProperty("pathenaUiState", state)
        self.status.setAccessibleDescription(text)
        self.dialog.setProperty("pathenaUiState", state)


def install_comfyui_integration(
    palette: CommandPaletteController,
    *,
    client: ComfyUiClient | None = None,
) -> ComfyUiController:
    """Install one ComfyUI controller and register its real command before catalog binding."""
    existing = getattr(palette, "_pathena_comfyui_controller", None)
    if isinstance(existing, ComfyUiController):
        return existing
    controller = ComfyUiController(palette, client=client)
    labels = {command.label for command in palette._commands}
    if "Open ComfyUI" not in labels:
        palette._commands = (
            *palette._commands,
            _Command(
                label="Open ComfyUI",
                keywords=("comfyui", "image", "video", "workflow", "local", "vram"),
                action=controller.open,
            ),
        )
    palette.__dict__["_pathena_comfyui_controller"] = controller
    return controller
