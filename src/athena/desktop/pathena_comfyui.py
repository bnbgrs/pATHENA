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

from PySide6.QtCore import QEvent, QObject, Qt
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QFrame,
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
        if normalized not in history:
            return ComfyUiPromptState(normalized, "unknown")

        entry = history[normalized]
        if not isinstance(entry, dict):
            raise ComfyUiError("Local ComfyUI history entry is malformed.")
        status = entry.get("status")
        if not isinstance(status, dict):
            raise ComfyUiError("Local ComfyUI history entry has no status object.")

        status_value = status.get("status_str")
        completed = status.get("completed")
        if not isinstance(status_value, str) or not status_value.strip():
            raise ComfyUiError("Local ComfyUI history status is incomplete.")
        if not isinstance(completed, bool):
            raise ComfyUiError("Local ComfyUI history completion flag is invalid.")

        normalized_status = status_value.strip().casefold()
        if normalized_status == "success":
            if not completed:
                raise ComfyUiError(
                    "Local ComfyUI history reports success without completion."
                )
            return ComfyUiPromptState(normalized, "completed")
        if completed or normalized_status in {"error", "failed", "interrupted"}:
            return ComfyUiPromptState(normalized, "failed")
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

        self._workspace = self.window.findChild(QFrame, "v3Workspace")
        self._shell = getattr(self.window, "_pathena_v3_shell_controller", None)
        self._shell_generation = "v3"
        if self._workspace is None or self._shell is None:
            self._workspace = self.window.findChild(QFrame, "v2Workspace")
            self._shell = getattr(self.window, "_pathena_v2_shell_controller", None)
            self._shell_generation = "v2"

        if self._workspace is not None and self._shell is not None:
            self.dialog.setParent(self._workspace)
            self.dialog.setWindowFlags(Qt.WindowType.Widget)
            self.dialog.setProperty("pathenaShellHosted", True)
            self.dialog.installEventFilter(self)
            self._workspace.installEventFilter(self)
            self.window.navigation.currentRowChanged.connect(
                self._hide_for_navigation
            )
        else:
            self._workspace = None
            self._shell = None
            self._shell_generation = ""
            self.dialog.setProperty("pathenaShellHosted", False)

        self._pallas = getattr(
            self.window,
            "_pathena_pallas_full_view_controller",
            None,
        )
        pallas_opened = getattr(self._pallas, "workspace_opened", None)
        connect_pallas_opened = getattr(pallas_opened, "connect", None)
        if callable(connect_pallas_opened):
            connect_pallas_opened(self._hide_for_pallas)

        outer = QVBoxLayout(self.dialog)
        outer.setContentsMargins(28, 24, 28, 24)
        outer.setSpacing(12)

        title_row = QHBoxLayout()
        title = QLabel("ComfyUI")
        title.setObjectName("comfyUiTitle")
        title.setVisible(self._workspace is None)
        title_row.addWidget(title)
        title_row.addStretch(1)
        self.close_button = QPushButton("Close")
        self.close_button.setObjectName("comfyUiClose")
        self.close_button.setAccessibleName("Close ComfyUI workspace")
        self.close_button.setToolTip("Close ComfyUI and return to the selected workspace")
        self.close_button.clicked.connect(self.dialog.hide)
        self.close_button.setVisible(self._workspace is not None)
        title_row.addWidget(self.close_button)
        outer.addLayout(title_row)

        intro = QLabel("Run local image and video workflows without leaving this device")
        intro.setWordWrap(True)
        intro.setProperty("role", "muted")
        intro.setVisible(self._workspace is None)
        outer.addWidget(intro)

        content = QHBoxLayout()
        content.setContentsMargins(0, 4, 0, 0)
        content.setSpacing(14)

        primary = QVBoxLayout()
        primary.setContentsMargins(0, 0, 0, 0)
        primary.setSpacing(14)

        connection = QFrame()
        connection.setObjectName("comfyUiPanel")
        connection.setAccessibleName("ComfyUI connection")
        connection_layout = QVBoxLayout(connection)
        connection_layout.setContentsMargins(18, 16, 18, 16)
        connection_layout.setSpacing(10)

        connection_heading = QHBoxLayout()
        connection_heading.setContentsMargins(0, 0, 0, 0)
        connection_heading.setSpacing(10)
        connection_label = QLabel("Connection")
        connection_label.setObjectName("comfyUiSectionTitle")
        connection_heading.addWidget(connection_label)
        connection_heading.addStretch(1)
        self.check_button = QPushButton("Check connection")
        self.check_button.setObjectName("comfyUiCheckConnection")
        self.check_button.clicked.connect(self.check_connection)
        connection_heading.addWidget(self.check_button)
        connection_layout.addLayout(connection_heading)

        endpoint_label = QLabel("Local endpoint")
        endpoint_label.setObjectName("comfyUiFieldLabel")
        connection_layout.addWidget(endpoint_label)
        self.endpoint = QLineEdit(self.client.endpoint)
        self.endpoint.setObjectName("comfyUiEndpoint")
        self.endpoint.setReadOnly(True)
        self.endpoint.setAccessibleName("ComfyUI local endpoint")
        connection_layout.addWidget(self.endpoint)

        self.status = QLabel("Connection not checked yet.")
        self.status.setObjectName("comfyUiStatus")
        self.status.setWordWrap(True)
        self.status.setProperty("pathenaUiState", "empty")
        self.status.setAccessibleName("ComfyUI connection status")
        connection_layout.addWidget(self.status)

        self.resource_status = QLabel("GPU memory appears after the connection is checked.")
        self.resource_status.setObjectName("comfyUiResourceStatus")
        self.resource_status.setWordWrap(True)
        self.resource_status.setProperty("role", "muted")
        self.resource_status.setAccessibleName("ComfyUI VRAM status")
        connection_layout.addWidget(self.resource_status)
        primary.addWidget(connection)

        workflow = QFrame()
        workflow.setObjectName("comfyUiPanel")
        workflow.setAccessibleName("ComfyUI workflow")
        workflow_layout = QVBoxLayout(workflow)
        workflow_layout.setContentsMargins(18, 16, 18, 16)
        workflow_layout.setSpacing(10)

        workflow_label = QLabel("Workflow")
        workflow_label.setObjectName("comfyUiSectionTitle")
        workflow_layout.addWidget(workflow_label)

        workflow_hint = QLabel(
            "Choose a ComfyUI API workflow, then run it on the local ComfyUI server."
        )
        workflow_hint.setObjectName("comfyUiPanelHint")
        workflow_hint.setWordWrap(True)
        workflow_layout.addWidget(workflow_hint)

        self.workflow_field = QLineEdit()
        self.workflow_field.setObjectName("comfyUiWorkflowPath")
        self.workflow_field.setReadOnly(True)
        self.workflow_field.setPlaceholderText("No workflow selected")
        self.workflow_field.setAccessibleName("ComfyUI API workflow")
        self.browse_button = QPushButton("Choose workflow…")
        self.browse_button.setObjectName("comfyUiBrowseWorkflow")
        self.browse_button.clicked.connect(self.choose_workflow)
        workflow_row = QHBoxLayout()
        workflow_row.setContentsMargins(0, 0, 0, 0)
        workflow_row.setSpacing(8)
        workflow_row.addWidget(self.workflow_field, 1)
        workflow_row.addWidget(self.browse_button)
        workflow_layout.addLayout(workflow_row)

        workflow_actions = QHBoxLayout()
        workflow_actions.setContentsMargins(0, 0, 0, 0)
        self.queue_button = QPushButton("Run workflow")
        self.queue_button.setObjectName("comfyUiQueueWorkflow")
        self.queue_button.setEnabled(False)
        self.queue_button.clicked.connect(self.queue_selected_workflow)
        workflow_actions.addWidget(self.queue_button)
        workflow_actions.addStretch(1)
        workflow_layout.addLayout(workflow_actions)
        primary.addWidget(workflow)
        primary.addStretch(1)
        content.addLayout(primary, 1)

        activity = QFrame()
        activity.setObjectName("comfyUiActivityPanel")
        activity.setAccessibleName("ComfyUI activity")
        activity.setMinimumWidth(290)
        activity.setMaximumWidth(360)
        activity_layout = QVBoxLayout(activity)
        activity_layout.setContentsMargins(18, 16, 18, 16)
        activity_layout.setSpacing(10)

        activity_label = QLabel("Activity")
        activity_label.setObjectName("comfyUiSectionTitle")
        activity_layout.addWidget(activity_label)

        self.job_status = QLabel("No workflow is running in this session.")
        self.job_status.setObjectName("comfyUiJobStatus")
        self.job_status.setWordWrap(True)
        self.job_status.setProperty("pathenaUiState", "empty")
        self.job_status.setAccessibleName("ComfyUI job status")
        activity_layout.addWidget(self.job_status)

        self.receipt = QLabel("")
        self.receipt.setObjectName("comfyUiQueueReceipt")
        self.receipt.setWordWrap(True)
        self.receipt.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.receipt.setAccessibleName("ComfyUI queue receipt")
        activity_layout.addWidget(self.receipt)

        operations = QHBoxLayout()
        operations.setContentsMargins(0, 0, 0, 0)
        operations.setSpacing(8)
        self.refresh_job_button = QPushButton("Refresh status")
        self.refresh_job_button.setObjectName("comfyUiRefreshJob")
        self.refresh_job_button.setEnabled(False)
        self.refresh_job_button.clicked.connect(self.refresh_prompt_status)
        self.release_vram_button = QPushButton("Free GPU memory")
        self.release_vram_button.setObjectName("comfyUiReleaseVram")
        self.release_vram_button.clicked.connect(self.release_vram)
        operations.addWidget(self.refresh_job_button)
        operations.addWidget(self.release_vram_button)
        activity_layout.addLayout(operations)
        activity_layout.addStretch(1)
        content.addWidget(activity)

        outer.addLayout(content, 1)

        self.dialog.setTabOrder(self.check_button, self.browse_button)
        self.dialog.setTabOrder(self.browse_button, self.queue_button)
        self.dialog.setTabOrder(self.queue_button, self.refresh_job_button)
        self.dialog.setTabOrder(self.refresh_job_button, self.release_vram_button)
        if self._workspace is not None:
            self.dialog.setTabOrder(self.release_vram_button, self.close_button)

        self.dialog.setProperty("pathenaComfyUiEndpoint", self.client.endpoint)
        self.dialog.setProperty(
            "pathenaComfyUiShellHosted",
            self._workspace is not None,
        )
        self.dialog.setProperty("pathenaComfyUiLocalOnly", True)
        self.dialog.setProperty(
            "pathenaComfyUiPresentation",
            "v3" if self.window.findChild(QFrame, "v3Workspace") is not None else "legacy",
        )
        self.dialog.setProperty("pathenaComfyUiGlobalInterruptAvailable", False)
        self.dialog.setProperty("pathenaComfyUiVramAvailable", False)
        # Reparenting the dialog into an as-yet hidden workspace clears Qt's
        # explicit hidden state.  Without restoring it, showing the main window
        # also shows ComfyUI and covers the selected primary route before the
        # user has opened the integration.
        self.dialog.hide()
        self.window.setProperty("pathenaComfyUiController", self)
        self.window.setProperty("pathenaComfyUiInstalled", True)

    def _hide_for_navigation(self, _row: int) -> None:
        """Close the transient ComfyUI canvas when primary navigation takes ownership."""
        if not self.dialog.isHidden():
            self.dialog.hide()

    def _hide_for_pallas(self) -> None:
        """Explicitly close ComfyUI and hand the workbar back to PALLAS."""
        if not self.dialog.isHidden():
            self.dialog.hide()
        self._restore_shell_header()

    def _fit_workspace(self) -> None:
        workspace = self._workspace
        if workspace is None or self.dialog.parent() is not workspace:
            return
        self.dialog.setGeometry(workspace.rect())
        self.dialog.raise_()

    def _set_shell_header(self) -> None:
        inspector = getattr(self._shell, "_inspector", None)
        if isinstance(inspector, QFrame):
            inspector.hide()
        transient_opened = getattr(self._shell, "transient_opened", None)
        if callable(transient_opened):
            transient_opened(
                "ComfyUI",
                "Run local image and video workflows on this device.",
            )
            return
        header = getattr(self._shell, "_header", None)
        set_context = getattr(header, "set_context", None)
        if callable(set_context):
            set_context(
                "ComfyUI",
                "Local image and video workflows · loopback only.",
            )

    def _restore_shell_header(self) -> None:
        if bool(self.window.property("pathenaPallasShellOpen")):
            pallas_opened = getattr(self._shell, "pallas_opened", None)
            if callable(pallas_opened):
                pallas_opened()
            if self._shell_generation == "v2":
                header = getattr(self._shell, "_header", None)
                set_context = getattr(header, "set_context", None)
                if callable(set_context):
                    set_context("PALLAS", "Living semantic workspace")
            return
        transient_closed = getattr(self._shell, "transient_closed", None)
        if callable(transient_closed):
            transient_closed()
            return
        sync_navigation = getattr(self._shell, "_sync_navigation", None)
        if callable(sync_navigation):
            sync_navigation(self.window.navigation.currentRow())

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        workspace = self._workspace
        if workspace is not None:
            if watched is workspace and event.type() == QEvent.Type.Resize:
                if self.dialog.isVisible():
                    self._fit_workspace()
            elif watched is self.dialog:
                if event.type() == QEvent.Type.Show:
                    self._fit_workspace()
                    self._set_shell_header()
                elif event.type() in {QEvent.Type.Hide, QEvent.Type.Close}:
                    self._restore_shell_header()
        return super().eventFilter(watched, event)

    def open(self) -> None:
        self.dialog.show()
        self._fit_workspace()
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
            f"Workflow ready · {len(workflow)} nodes · runs locally.",
        )

    def check_connection(self) -> bool:
        try:
            health = self.client.health()
        except ComfyUiError as exc:
            self.check_button.setText("Retry connection")
            self._set_status("error", str(exc))
            self._set_vram_unavailable("GPU memory · unavailable while ComfyUI is disconnected.")
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
        self._set_status("success", "Workflow sent to local ComfyUI.")
        self.receipt.setText(f"Prompt ID · {receipt.prompt_id}")
        self.receipt.setProperty("pathenaComfyUiPromptId", receipt.prompt_id)
        self._set_job_status("pending", "Queued locally · refresh to read the current state.")
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
            "pending": "Waiting in the local queue.",
            "running": "Running locally in ComfyUI.",
            "completed": "Completed successfully.",
            "failed": "ComfyUI reports that this workflow did not complete successfully.",
            "unknown": "No terminal result is available in the current queue or history.",
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
            "GPU memory release requested · ComfyUI will unload models when safe.",
        )
        self.resource_status.setText(
            "GPU memory release requested · check the connection again for measured memory."
        )
        self.dialog.setProperty("pathenaComfyUiVramReleaseRequested", True)
        return True

    def _set_vram_health(self, health: ComfyUiHealth) -> None:
        total = health.vram_total_bytes
        free = health.vram_free_bytes
        if total is None or free is None:
            self._set_vram_unavailable(
                "GPU memory · unavailable from this local ComfyUI status response."
            )
            return
        used = max(total - free, 0)
        text = f"GPU memory · {_format_gib(used)} used · {_format_gib(free)} free · {_format_gib(total)} total"
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
