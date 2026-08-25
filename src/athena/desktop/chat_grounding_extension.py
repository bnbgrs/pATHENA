"""Inline grounded provenance for the persisted assistant message.

The extension consumes only ``GroundedChatResponse`` data already validated by Core.
It adds no synthetic sources or claims and exposes a PALLAS action only when the
matching semantic graph is installed and contains the exact persisted entity.
"""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QObject, Qt, Slot
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from athena.api.contracts import GroundedChatResponse, GroundedEvidenceResponse
from athena.desktop.api_controller import DesktopApiController
from athena.desktop.pathena_pallas_field import PallasGroundedFieldController


@dataclass(frozen=True, slots=True)
class ChatEvidenceReference:
    """One stable inline reference backed by a grounded response entity."""

    context_id: str
    node_id: str
    entity_type: str
    entity_id: str
    title: str
    summary: str
    source_name: str | None
    location: str | None
    epistemic_status: str | None
    cited: bool


def project_chat_evidence(
    response: GroundedChatResponse,
) -> tuple[ChatEvidenceReference, ...]:
    """Project response evidence without changing order or inventing labels."""
    references: list[ChatEvidenceReference] = []
    seen_context_ids: set[str] = set()
    for item in response.evidence:
        if item.context_id in seen_context_ids:
            continue
        seen_context_ids.add(item.context_id)
        references.append(
            ChatEvidenceReference(
                context_id=item.context_id,
                node_id=f"{item.entity_type}:{item.entity_id}",
                entity_type=item.entity_type,
                entity_id=item.entity_id,
                title=_evidence_title(item),
                summary=item.text,
                source_name=item.source_name,
                location=_source_location(item),
                epistemic_status=item.epistemic_status,
                cited=item.cited,
            )
        )
    return tuple(references)


class ChatGroundingController(QObject):
    """Attach real evidence references to the latest persisted assistant row."""

    def __init__(
        self,
        window: QWidget,
        api_controller: DesktopApiController | None,
    ) -> None:
        super().__init__(window)
        self.window = window
        self.api_controller = api_controller
        self.last_run_id: str | None = None
        self.last_state = "empty"
        if api_controller is not None:
            api_controller.grounded_chat_sent.connect(self.apply_grounded_response)

    @Slot(object)
    def apply_grounded_response(self, payload: object) -> None:
        if not isinstance(payload, GroundedChatResponse):
            self.last_state = "error"
            return
        current_chat_id = getattr(self.window, "current_chat_id", None)
        if current_chat_id != payload.thread.chat_id:
            self.last_state = "stale"
            return
        assistant = next(
            (
                message
                for message in reversed(payload.thread.messages)
                if message.message_type == "assistant"
            ),
            None,
        )
        if assistant is None:
            self.last_state = "error"
            return
        container = self._message_container(assistant.message_id)
        if container is None:
            self.last_state = "error"
            return

        existing = container.findChild(QWidget, "groundedEvidenceSummary")
        if existing is not None:
            existing.deleteLater()

        references = project_chat_evidence(payload)
        panel = self._build_panel(payload, references, container)
        layout = container.layout()
        if not isinstance(layout, QVBoxLayout):
            panel.deleteLater()
            self.last_state = "error"
            return
        layout.insertWidget(max(0, layout.count() - 1), panel)
        self.last_run_id = payload.processing_run_id
        self.last_state = "ready" if references else "empty"
        container.setProperty("pathenaGroundedRunId", payload.processing_run_id)
        container.setProperty("pathenaGroundedEvidenceCount", len(references))

    def _message_container(self, message_id: str) -> QWidget | None:
        document = getattr(self.window, "chat_messages_widget", None)
        if not isinstance(document, QWidget):
            return None
        return next(
            (
                item
                for item in document.findChildren(QWidget, "chatMessage")
                if item.property("messageId") == message_id
            ),
            None,
        )

    def _build_panel(
        self,
        response: GroundedChatResponse,
        references: tuple[ChatEvidenceReference, ...],
        parent: QWidget,
    ) -> QFrame:
        panel = QFrame(parent)
        panel.setObjectName("groundedEvidenceSummary")
        panel.setProperty("pathenaUiState", "ready" if references else "empty")
        panel.setProperty("groundedRunId", response.processing_run_id)
        panel.setAccessibleName("Grounded evidence for this assistant response")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 6, 0, 4)
        layout.setSpacing(5)

        cited_count = sum(reference.cited for reference in references)
        heading = QLabel(
            f"Grounded evidence · {cited_count} cited · {len(references)} available",
            panel,
        )
        heading.setObjectName("groundedEvidenceHeading")
        heading.setProperty("role", "muted")
        heading.setAccessibleName(
            f"Grounded evidence, {cited_count} cited, {len(references)} available"
        )
        layout.addWidget(heading)

        if not references:
            empty = QLabel("No evidence entities were returned for this grounded run.", panel)
            empty.setObjectName("groundedEvidenceEmpty")
            empty.setWordWrap(True)
            empty.setProperty("role", "muted")
            layout.addWidget(empty)
            return panel

        for reference in references:
            layout.addLayout(self._reference_row(response, reference, panel))
        return panel

    def _reference_row(
        self,
        response: GroundedChatResponse,
        reference: ChatEvidenceReference,
        parent: QWidget,
    ) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(8)

        text_column = QVBoxLayout()
        text_column.setContentsMargins(0, 0, 0, 0)
        text_column.setSpacing(1)

        title = QLabel(reference.title, parent)
        title.setObjectName("groundedEvidenceTitle")
        title.setWordWrap(True)
        title.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        title.setProperty("contextId", reference.context_id)
        title.setProperty("entityId", reference.entity_id)
        title.setProperty("cited", reference.cited)
        title.setToolTip(reference.summary)
        title.setAccessibleName(reference.title)
        text_column.addWidget(title)

        metadata = QLabel(_reference_metadata(reference), parent)
        metadata.setObjectName("groundedEvidenceMeta")
        metadata.setWordWrap(True)
        metadata.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        metadata.setProperty("role", "muted")
        metadata.setProperty("contextId", reference.context_id)
        metadata.setAccessibleName(_reference_metadata(reference))
        text_column.addWidget(metadata)
        row.addLayout(text_column, 1)

        action = QPushButton("Open in PALLAS", parent)
        action.setObjectName("openPallasEvidenceButton")
        action.setProperty("contextId", reference.context_id)
        action.setProperty("pallasNodeId", reference.node_id)
        action.setAccessibleName(f"Open {reference.title} in PALLAS")
        enabled, reason = self._pallas_availability(response, reference.node_id)
        action.setEnabled(enabled)
        action.setToolTip(reason)
        if enabled:
            action.clicked.connect(
                lambda _checked=False, node_id=reference.node_id: self._focus_pallas_node(
                    node_id
                )
            )
        row.addWidget(action)
        return row

    def _pallas_availability(
        self,
        response: GroundedChatResponse,
        node_id: str,
    ) -> tuple[bool, str]:
        controller = self._pallas_controller()
        if controller is None:
            return False, "PALLAS is not installed for this window."
        snapshot = controller.field.snapshot
        expected_graph = f"grounded-run:{response.processing_run_id}"
        if snapshot is None or snapshot.graph_id != expected_graph:
            return False, "PALLAS does not contain this grounded run."
        if snapshot.node(node_id) is None:
            return False, "This evidence entity is not present in PALLAS."
        return True, "Focus this exact persisted evidence entity in PALLAS."

    def _pallas_controller(self) -> PallasGroundedFieldController | None:
        candidate = self.window.property("pathenaPallasGroundedController")
        return candidate if isinstance(candidate, PallasGroundedFieldController) else None

    def _focus_pallas_node(self, node_id: str) -> None:
        controller = self._pallas_controller()
        if controller is not None:
            controller.field.focus_node(node_id)


def install_chat_grounding_extension(
    window: QWidget,
    api_controller: DesktopApiController | None = None,
) -> ChatGroundingController:
    """Install inline grounding without changing the shared shell or chat renderer."""
    resolved = api_controller
    if resolved is None:
        candidate = getattr(window, "api_controller", None)
        if isinstance(candidate, DesktopApiController):
            resolved = candidate
    controller = ChatGroundingController(window, resolved)
    window.setProperty("pathenaChatGroundingController", controller)
    window.setProperty("pathenaChatGroundingInstalled", True)
    return controller


def _evidence_title(item: GroundedEvidenceResponse) -> str:
    return item.title or item.source_name or item.entity_type.replace("_", " ").title()


def _source_location(item: GroundedEvidenceResponse) -> str | None:
    if item.page_start is None:
        return None
    if item.page_end is not None and item.page_end != item.page_start:
        return f"pages {item.page_start}–{item.page_end}"
    return f"page {item.page_start}"


def _reference_metadata(reference: ChatEvidenceReference) -> str:
    """Return compact provenance using only persisted response fields."""
    parts = [
        "CITED" if reference.cited else "CONTEXT",
        reference.entity_type.upper(),
        reference.entity_id,
    ]
    if reference.source_name and reference.source_name != reference.title:
        parts.append(reference.source_name)
    if reference.location:
        parts.append(reference.location)
    if reference.epistemic_status:
        parts.append(reference.epistemic_status)
    return " · ".join(parts)
