"""Interactive PALLAS miniature for real grounded semantic context.

The extension is deliberately reversible: it mounts inside the existing PALLAS
placeholder and leaves the legacy ASCII painter and shared shell untouched.  A
Lead integration can therefore remove the extension without losing behaviour.
"""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QObject, QPointF, QRectF, Qt, Signal, Slot
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPen, QResizeEvent, QWheelEvent
from PySide6.QtWidgets import (
    QAbstractButton,
    QGraphicsEllipseItem,
    QGraphicsItem,
    QGraphicsLineItem,
    QGraphicsScene,
    QGraphicsSimpleTextItem,
    QGraphicsView,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from athena.api.contracts import GroundedChatResponse
from athena.desktop.api_controller import DesktopApiController
from athena.desktop.pathena_pallas_semantic import (
    PallasGraphSnapshot,
    PallasNodeKind,
    PallasSemanticNode,
    deterministic_layout,
    graph_from_grounded_response,
)

_CANVAS = QColor("#060606")
_TEXT = QColor("#F4F1EC")
_MUTED = QColor("#A9A29A")
_QUIET = QColor("#706B65")
_BORDER = QColor("#202020")
_ACCENT = QColor("#F26A21")
_CONFLICT = QColor("#D96B62")
_UNCERTAIN = QColor("#D5A34B")


@dataclass(frozen=True, slots=True)
class PallasSelection:
    """Stable handoff payload for the shared Context Inspector."""

    graph_id: str
    node: PallasSemanticNode


class _PallasCanvas(QGraphicsView):
    """Bounded pan/zoom canvas with no autonomous animation."""

    def __init__(self, scene: QGraphicsScene, parent: QWidget) -> None:
        super().__init__(scene, parent)
        self._zoom = 1.0
        self._auto_fit = True
        self.setObjectName("pallasSemanticCanvas")
        self.setFrameShape(QGraphicsView.Shape.NoFrame)
        self.setBackgroundBrush(QBrush(_CANVAS))
        self.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    def reset_view(self, bounds: QRectF) -> None:
        self.resetTransform()
        self._zoom = 1.0
        self._auto_fit = True
        if not bounds.isEmpty():
            self.fitInView(bounds, Qt.AspectRatioMode.KeepAspectRatio)
            self._zoom = self.transform().m11()

    def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        super().resizeEvent(event)
        bounds = self.sceneRect()
        if self._auto_fit and not bounds.isEmpty():
            self.fitInView(bounds, Qt.AspectRatioMode.KeepAspectRatio)
            self._zoom = self.transform().m11()

    def wheelEvent(self, event: QWheelEvent) -> None:  # noqa: N802
        direction = event.angleDelta().y()
        if direction == 0:
            event.ignore()
            return
        factor = 1.15 if direction > 0 else 1 / 1.15
        candidate = self._zoom * factor
        if 0.2 <= candidate <= 6.0:
            self.scale(factor, factor)
            self._zoom = candidate
            self._auto_fit = False
        event.accept()


class _PallasNodeItem(QGraphicsEllipseItem):
    def __init__(
        self,
        node: PallasSemanticNode,
        position: QPointF,
        *,
        show_title: bool,
    ) -> None:
        radius = 18.0 if node.kind is PallasNodeKind.FOCUS else 13.0
        super().__init__(-radius, -radius, radius * 2, radius * 2)
        self.node = node
        self.setPos(position)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsFocusable, True)
        self.setBrush(QBrush(_CANVAS))
        self.setPen(QPen(_node_color(node), 1.4))
        self.setToolTip(_node_tooltip(node))

        glyph = QGraphicsSimpleTextItem(node.glyph, self)
        glyph.setBrush(QBrush(_node_color(node)))
        glyph_font = QFont("Cascadia Mono")
        glyph_font.setPixelSize(15 if node.kind is PallasNodeKind.FOCUS else 13)
        glyph.setFont(glyph_font)
        glyph_bounds = glyph.boundingRect()
        glyph.setPos(-glyph_bounds.width() / 2, -glyph_bounds.height() / 2)

        if show_title:
            title = QGraphicsSimpleTextItem(_clip(node.title, 28), self)
            title.setBrush(QBrush(_TEXT if node.cited else _MUTED))
            title_font = QFont("Segoe UI")
            title_font.setPixelSize(11)
            title.setFont(title_font)
            title.setPos(radius + 7, -title.boundingRect().height() / 2)

    def itemChange(
        self,
        change: QGraphicsItem.GraphicsItemChange,
        value: object,
    ) -> object:
        result = super().itemChange(change, value)
        if change is QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
            selected = bool(value)
            self.setPen(QPen(_ACCENT if selected else _node_color(self.node), 2.0 if selected else 1.4))
            self.setZValue(2.0 if selected else 1.0)
        return result


class PallasSemanticField(QWidget):
    """Selectable renderer with explicit loading, empty, ready, and error states."""

    selection_changed = Signal(object)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("pallasSemanticField")
        self.setProperty("pathenaUiState", "empty")
        self.setAccessibleName("PALLAS semantic field")
        self._snapshot: PallasGraphSnapshot | None = None
        self._items: dict[str, _PallasNodeItem] = {}
        self._compact = False

        self.scene = QGraphicsScene(self)
        self.canvas = _PallasCanvas(self.scene, self)
        self.state_label = QLabel("No grounded context yet")
        self.state_label.setObjectName("pallasSemanticState")
        self.state_label.setWordWrap(True)
        self.state_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.state_label.setProperty("role", "muted")
        self.selection_label = QLabel("")
        self.selection_label.setObjectName("pallasSemanticSelection")
        self.selection_label.setWordWrap(True)
        self.selection_label.setProperty("role", "muted")
        self.selection_label.hide()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        layout.addWidget(self.canvas, 1)
        layout.addWidget(self.state_label)
        layout.addWidget(self.selection_label)

        self.scene.selectionChanged.connect(self._publish_selection)
        self.set_empty("No grounded evidence or memory has been received yet.")

    @property
    def snapshot(self) -> PallasGraphSnapshot | None:
        return self._snapshot

    def set_compact_mode(self, compact: bool) -> None:
        """Use a label-free miniature while preserving node tooltips and selection."""
        self._compact = compact
        self.setProperty("pathenaPallasMode", "compact" if compact else "full")
        if compact:
            self.selection_label.hide()

    def set_loading(self, detail: str) -> None:
        self._set_nonready_state("loading", "Resolving grounded context", detail)

    def set_empty(self, detail: str) -> None:
        self._set_nonready_state("empty", "No semantic context", detail)

    def set_error(self, detail: str) -> None:
        self._set_nonready_state("error", "PALLAS could not update", detail)

    def set_snapshot(self, snapshot: PallasGraphSnapshot) -> None:
        if snapshot.status != "ready" or not snapshot.nodes:
            self._snapshot = snapshot
            self.set_empty(snapshot.status_detail)
            return

        self._snapshot = snapshot
        self.scene.clear()
        self._items.clear()
        positions = {
            item.node_id: QPointF(item.x, item.y)
            for item in deterministic_layout(snapshot)
        }

        for edge in snapshot.edges:
            source = positions.get(edge.source_id)
            target = positions.get(edge.target_id)
            if source is None or target is None:
                continue
            line = QGraphicsLineItem(source.x(), source.y(), target.x(), target.y())
            line.setPen(QPen(_BORDER, 1.0))
            line.setToolTip(edge.relation.replace("_", " "))
            line.setZValue(-1.0)
            self.scene.addItem(line)

        for node in snapshot.nodes:
            position = positions.get(node.node_id)
            if position is None:
                continue
            item = _PallasNodeItem(node, position, show_title=not self._compact)
            self._items[node.node_id] = item
            self.scene.addItem(item)

        self.setProperty("pathenaUiState", "ready")
        self.setProperty("pathenaPallasGraphId", snapshot.graph_id)
        self.setProperty("pathenaPallasNodeCount", len(snapshot.nodes))
        self.state_label.hide()
        self.selection_label.hide()
        bounds = self.scene.itemsBoundingRect().adjusted(-24, -24, 24, 24)
        self.scene.setSceneRect(bounds)
        self.canvas.reset_view(bounds)
        self.setAccessibleDescription(snapshot.status_detail)
        if snapshot.focus_id is not None:
            self.focus_node(snapshot.focus_id)

    def focus_node(self, node_id: str) -> bool:
        item = self._items.get(node_id)
        if item is None:
            return False
        self.scene.clearSelection()
        item.setSelected(True)
        item.setFocus()
        self.canvas.centerOn(item)
        return True

    @Slot()
    def _publish_selection(self) -> None:
        snapshot = self._snapshot
        selected = next(
            (
                item
                for item in self.scene.selectedItems()
                if isinstance(item, _PallasNodeItem)
            ),
            None,
        )
        if snapshot is None or selected is None:
            self.setProperty("pathenaPallasSelectionId", "")
            self.selection_label.hide()
            self.selection_changed.emit(None)
            return

        node = selected.node
        selection = PallasSelection(snapshot.graph_id, node)
        self.setProperty("pathenaPallasSelectionId", node.node_id)
        self.selection_label.setText(f"{node.glyph} {node.title} · {node.entity_type}")
        self.selection_label.setToolTip(node.summary)
        self.selection_label.setVisible(not self._compact)
        self.setAccessibleDescription(_node_tooltip(node))
        self.selection_changed.emit(selection)

    def _set_nonready_state(self, state: str, title: str, detail: str) -> None:
        self._snapshot = None
        self.scene.clear()
        self._items.clear()
        self.setProperty("pathenaUiState", state)
        self.setProperty("pathenaPallasGraphId", "")
        self.setProperty("pathenaPallasNodeCount", 0)
        self.setProperty("pathenaPallasSelectionId", "")
        self.state_label.setText(f"{title}\n{detail}")
        self.state_label.show()
        self.selection_label.hide()
        self.setAccessibleDescription(detail)


class PallasGroundedFieldController(QObject):
    """Bind the semantic field to the existing real desktop controller signals."""

    selection_changed = Signal(object)

    def __init__(
        self,
        window: QWidget,
        api_controller: DesktopApiController | None,
    ) -> None:
        super().__init__(window)
        self.window = window
        self.api_controller = api_controller
        target = window.findChild(QWidget, "pallasVisualPlaceholder")
        if target is None:
            raise RuntimeError("PALLAS shared container is unavailable.")
        self.target = target
        self.field = PallasSemanticField(target)
        self.field.set_compact_mode(True)

        existing_layout = target.layout()
        if existing_layout is None:
            layout = QVBoxLayout(target)
            layout.setContentsMargins(1, 1, 1, 1)
            layout.setSpacing(0)
            existing_layout = layout
        existing_layout.addWidget(self.field)

        target.setProperty("pathenaPallasRenderer", "grounded-semantic-v1")
        target.setProperty("pathenaUiState", "empty")
        target.setToolTip(
            "PALLAS — interactive field built only from grounded Core evidence and memory"
        )
        self.field.selection_changed.connect(self._forward_selection)

        if api_controller is None:
            self.field.set_empty("Connect the local Core to receive grounded context.")
            return
        api_controller.grounded_chat_sent.connect(self.apply_grounded_response)
        api_controller.chat_operation_failed.connect(self.apply_chat_operation_failure)
        api_controller.chat_busy_changed.connect(self.apply_chat_busy)

    @Slot(object)
    def apply_grounded_response(self, response: object) -> None:
        if not isinstance(response, GroundedChatResponse):
            self.field.set_error("Core returned an unsupported grounded response.")
            self.target.setProperty("pathenaUiState", "error")
            return
        snapshot = graph_from_grounded_response(response)
        self.field.set_snapshot(snapshot)
        self.target.setProperty("pathenaUiState", snapshot.status)

    @Slot(str, str)
    def apply_chat_operation_failure(self, operation: str, message: str) -> None:
        if operation != "send_grounded":
            return
        self.field.set_error(message)
        self.target.setProperty("pathenaUiState", "error")

    @Slot(bool)
    def apply_chat_busy(self, busy: bool) -> None:
        ground_button = getattr(self.window, "ground_button", None)
        if busy and isinstance(ground_button, QAbstractButton) and ground_button.isChecked():
            self.field.set_loading("Core is resolving evidence and personal memory.")
            self.target.setProperty("pathenaUiState", "loading")

    @Slot(object)
    def _forward_selection(self, selection: object) -> None:
        self.selection_changed.emit(selection)


def install_pallas_grounded_field(
    window: QWidget,
    api_controller: DesktopApiController | None = None,
) -> PallasGroundedFieldController:
    """Install the reversible PALLAS renderer without touching shared shell files."""
    resolved_controller = api_controller
    if resolved_controller is None:
        candidate = getattr(window, "api_controller", None)
        if isinstance(candidate, DesktopApiController):
            resolved_controller = candidate
    controller = PallasGroundedFieldController(window, resolved_controller)
    window.setProperty("pathenaPallasGroundedController", controller)
    window.setProperty("pathenaPallasGroundedInstalled", True)
    return controller


def _node_color(node: PallasSemanticNode) -> QColor:
    if node.kind is PallasNodeKind.FOCUS:
        return _ACCENT
    if node.kind is PallasNodeKind.CONFLICT:
        return _CONFLICT
    if node.kind is PallasNodeKind.UNCERTAIN:
        return _UNCERTAIN
    return _TEXT if node.cited else _QUIET


def _node_tooltip(node: PallasSemanticNode) -> str:
    state = "cited" if node.cited else "available context"
    status = f" · {node.epistemic_status}" if node.epistemic_status else ""
    return f"{node.glyph} {node.title} · {state}{status}\n{node.summary}"


def _clip(value: str, limit: int) -> str:
    normalized = " ".join(value.split())
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 1].rstrip() + "…"
