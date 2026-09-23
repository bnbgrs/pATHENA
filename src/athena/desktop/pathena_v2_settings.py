"""Isolated pATHENA v2 Settings composition.

This module owns presentation only. It reparents existing Settings controls into a
clean v2 information architecture without changing provider, persistence, model,
or inference behavior.
"""

from __future__ import annotations

from PySide6.QtCore import QObject, Qt, Slot
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from athena.desktop.pathena_v2_components import (
    V2FormRow,
    V2NavigationButton,
    V2SectionLabel,
)
from athena.desktop.pathena_window import PathenaMainWindow


class PathenaV2SettingsController(QObject):
    """Recompose the real Settings controls into a focused v2 workspace."""

    def __init__(
        self,
        window: PathenaMainWindow,
        *,
        legacy_host: QWidget | None = None,
    ) -> None:
        super().__init__(window)
        self._window = window
        self._legacy_host = legacy_host
        self._section_buttons: list[V2NavigationButton] = []
        self._stack = QStackedWidget()
        self._stack.setObjectName("v2SettingsStack")
        self._settings = self._replace_page()
        self.set_section(0)

    @property
    def page(self) -> QWidget:
        return self._settings

    @property
    def section_buttons(self) -> tuple[V2NavigationButton, ...]:
        return tuple(self._section_buttons)

    @property
    def current_section(self) -> int:
        return self._stack.currentIndex()

    def _replace_page(self) -> QWidget:
        window = self._window
        pages = window.pages
        old_settings = pages.widget(6)
        if old_settings is None:
            raise RuntimeError("pATHENA v2 Settings requires the real Settings page.")
        if old_settings.objectName() == "v2SettingsPage":
            raise RuntimeError("pATHENA v2 Settings is already installed.")

        runtime_panel = old_settings.findChild(QWidget, "settingsRuntimePanel")

        settings = QWidget()
        settings.setObjectName("v2SettingsPage")
        root = QHBoxLayout(settings)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(28)

        root.addWidget(self._build_section_navigation())
        root.addWidget(self._stack, 1)

        self._stack.addWidget(self._build_inference_page())
        self._stack.addWidget(self._build_runtime_page(runtime_panel))

        current_index = pages.currentIndex()
        pages.removeWidget(old_settings)
        pages.insertWidget(6, settings)
        if current_index == 6:
            pages.setCurrentIndex(6)

        old_settings.setObjectName("legacySettingsPage")
        old_settings.setParent(self._legacy_host or window)
        old_settings.hide()
        return settings

    def _build_section_navigation(self) -> QWidget:
        nav = QFrame()
        nav.setObjectName("v2SettingsNav")
        nav.setFixedWidth(196)

        layout = QVBoxLayout(nav)
        layout.setContentsMargins(0, 4, 16, 0)
        layout.setSpacing(4)

        layout.addWidget(V2SectionLabel("SETTINGS"))
        layout.addSpacing(8)

        sections = (
            ("Models & inference", "Open model and inference settings"),
            ("Runtime status", "Open local runtime status"),
        )
        for index, (label, accessible_name) in enumerate(sections):
            button = V2NavigationButton(label, accessible_name=accessible_name)
            button.setObjectName(f"v2SettingsSection{index}")
            button.clicked.connect(
                lambda _checked=False, section=index: self.set_section(section)
            )
            self._section_buttons.append(button)
            layout.addWidget(button)

        layout.addStretch(1)

        truth = QLabel(
            "Settings shown here are backed by current local controls. "
            "Unavailable capabilities are not exposed."
        )
        truth.setObjectName("v2SettingsNavHint")
        truth.setWordWrap(True)
        truth.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)
        layout.addWidget(truth)
        return nav

    def _build_inference_page(self) -> QWidget:
        window = self._window

        scroll = QScrollArea()
        scroll.setObjectName("v2SettingsScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        form = QWidget()
        form.setObjectName("v2SettingsForm")
        layout = QVBoxLayout(form)
        layout.setContentsMargins(2, 0, 18, 28)
        layout.setSpacing(0)

        title = QLabel("Models & inference")
        title.setObjectName("v2PanelTitle")
        layout.addWidget(title)

        intro = QLabel(
            "Configure the real local model request path. Values are stored through "
            "the existing Settings contracts and remain synchronized with Chat."
        )
        intro.setObjectName("v2SettingsIntro")
        intro.setWordWrap(True)
        intro.setMaximumWidth(780)
        layout.addWidget(intro)
        layout.addSpacing(22)

        model_row = V2FormRow(
            "Local model",
            "Choose the LM Studio model used for chat and inference settings.",
        )
        window.settings_model_selector.setMinimumWidth(240)
        model_row.add_control(window.settings_model_selector, 1)
        window.settings_model_value.setMinimumWidth(90)
        model_row.add_control(window.settings_model_value)
        layout.addWidget(model_row)

        context_row = V2FormRow(
            "Context window",
            "Total token budget available to the selected model for this request.",
        )
        context_row.add_control(window.context_slider, 1)
        context_row.add_control(window.context_spin)
        layout.addWidget(context_row)

        output_row = V2FormRow(
            "Maximum output",
            "Upper bound for generated tokens within the selected context budget.",
        )
        output_row.add_control(window.max_output_slider, 1)
        output_row.add_control(window.max_output_spin)
        layout.addWidget(output_row)

        temperature_row = V2FormRow(
            "Temperature",
            "Higher values increase sampling variation; lower values are more deterministic.",
        )
        temperature_row.control_layout.addStretch(1)
        temperature_row.add_control(window.temperature_spin)
        layout.addWidget(temperature_row)

        thinking_row = V2FormRow(
            "Reasoning",
            "Allow reasoning-capable local models to use their supported reasoning mode.",
        )
        thinking_row.control_layout.addStretch(1)
        thinking_row.add_control(window.thinking_checkbox)
        layout.addWidget(thinking_row)

        layout.addStretch(1)
        scroll.setWidget(form)
        return scroll

    def _build_runtime_page(self, runtime_panel: QWidget | None) -> QWidget:
        page = QWidget()
        page.setObjectName("v2SettingsRuntimePage")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(2, 0, 18, 28)
        layout.setSpacing(12)

        title = QLabel("Runtime status")
        title.setObjectName("v2PanelTitle")
        layout.addWidget(title)

        hint = QLabel(
            "Live state reported by the local Core. pATHENA does not infer provider, "
            "network, or persistence readiness when the Core does not report it."
        )
        hint.setObjectName("v2PanelHint")
        hint.setWordWrap(True)
        hint.setMaximumWidth(780)
        layout.addWidget(hint)
        layout.addSpacing(8)

        status = QFrame()
        status.setObjectName("v2SettingsStatus")
        status_layout = QVBoxLayout(status)
        status_layout.setContentsMargins(20, 18, 20, 20)
        status_layout.setSpacing(12)

        if runtime_panel is None:
            empty = QLabel("Runtime state is not available from the current Settings contract.")
            empty.setObjectName("v2PanelHint")
            empty.setWordWrap(True)
            status_layout.addWidget(empty)
        else:
            runtime_panel.setParent(status)
            runtime_panel.setObjectName("v2SettingsRuntimePanel")
            status_layout.addWidget(runtime_panel)

        status_layout.addStretch(1)
        layout.addWidget(status, 1)
        return page

    @Slot(int)
    def set_section(self, index: int) -> None:
        if not 0 <= index < self._stack.count():
            return
        self._stack.setCurrentIndex(index)
        for button_index, button in enumerate(self._section_buttons):
            button.set_active(button_index == index)


def install_v2_settings(
    window: PathenaMainWindow,
    *,
    legacy_host: QWidget | None = None,
) -> PathenaV2SettingsController:
    """Install one idempotent v2 Settings adapter around the existing controls."""
    existing = getattr(window, "_pathena_v2_settings_controller", None)
    if isinstance(existing, PathenaV2SettingsController):
        return existing

    controller = PathenaV2SettingsController(window, legacy_host=legacy_host)
    window.__dict__["_pathena_v2_settings_controller"] = controller
    return controller
