"""Reference-driven shell convergence for pATHENA.

The functional window owns controls, signals and durable state. This presentation
pass only rearranges the already-installed real widgets so the running application
tracks the eleven reference screens more closely: a full-height left navigation,
quiet top status, dominant workspace, persistent contextual inspector and a compact
chat composer/status footer.
"""

from __future__ import annotations

from datetime import datetime

from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from athena.desktop.pathena_design_tokens import PALETTE, SHELL

_NAVIGATION: tuple[tuple[str, str], ...] = (
    ("›", "CHAT"),
    ("◇", "KNOWLEDGE"),
    ("◎", "RESEARCH"),
    ("▣", "JOBS"),
    ("▱", "SOURCES"),
    ("◉", "SYSTEM"),
    ("⚙", "SETTINGS"),
)

_SYSTEM_TABS_STYLESHEET = r"""
QTabWidget#systemOperationsTabs::pane {
    background: transparent;
    border: none;
    border-top: 1px solid #252a2e;
    top: -1px;
}
QTabWidget#systemOperationsTabs QTabBar::tab {
    color: #7e888f;
    background: transparent;
    border: none;
    border-bottom: 2px solid transparent;
    min-height: 30px;
    padding: 0 11px;
    margin-right: 5px;
    font-size: 10px;
    font-weight: 500;
}
QTabWidget#systemOperationsTabs QTabBar::tab:hover { color: #cbd1d5; }
QTabWidget#systemOperationsTabs QTabBar::tab:selected {
    color: #eef1f2;
    border-bottom-color: #707d81;
}
"""

_CONVERGENCE_STYLESHEET = f"""
QFrame#convergenceHost,
QFrame#workspaceColumn {{
    background: {PALETTE.canvas};
    border: none;
}}
QFrame#iconRail {{
    min-width: {SHELL.icon_rail_width}px;
    max-width: {SHELL.icon_rail_width}px;
    background: #090909;
    border: none;
    border-right: 1px solid #202020;
}}
QLabel#railWordmark {{
    color: {PALETTE.accent};
    font-family: "Segoe UI Variable", "Segoe UI", sans-serif;
    font-size: 21px;
    font-weight: 400;
    letter-spacing: 3px;
    padding: 4px 8px 22px 8px;
}}
QListWidget#navigation {{
    background: transparent;
    border: none;
    outline: none;
}}
QListWidget#navigation::item {{
    color: #9A9A9A;
    background: transparent;
    border: none;
    border-left: 2px solid transparent;
    padding: 0 14px;
    margin: 2px 0;
    font-family: "Cascadia Mono", "Consolas", monospace;
    font-size: 12px;
    letter-spacing: 1px;
}}
QListWidget#navigation::item:hover {{
    color: #E8E8E8;
    background: #111111;
}}
QListWidget#navigation::item:selected {{
    color: {PALETTE.accent};
    background: #101010;
    border-left: 2px solid {PALETTE.accent};
}}
QFrame#railFooter {{
    background: transparent;
    border: none;
}}
QPushButton#railUtilityButton {{
    min-width: 36px;
    max-width: 36px;
    min-height: 36px;
    max-height: 36px;
    color: #989898;
    background: transparent;
    border: 1px solid transparent;
    border-radius: 5px;
    font-size: 16px;
}}
QPushButton#railUtilityButton:hover,
QPushButton#railUtilityButton:focus {{
    color: #F2F2F2;
    background: #121212;
    border-color: #2A2A2A;
}}
QFrame#topBar {{
    background: #080808;
    border: none;
    border-bottom: 1px solid #202020;
}}
QFrame#shellStatusCluster {{
    background: transparent;
    border: none;
}}
QLabel#shellStatusLabel,
QLabel#shellClock,
QLabel#shellSeparator {{
    color: #989898;
    font-family: "Cascadia Mono", "Consolas", monospace;
    font-size: 11px;
    letter-spacing: 1px;
}}
QLabel#shellSeparator {{ color: #454545; }}
QLabel#coreStateDot {{ font-size: 10px; }}
QLabel#pallasStateDot {{ color: {PALETTE.accent}; font-size: 10px; }}
QFrame#conversation {{ background: {PALETTE.canvas}; }}
QFrame#inspector {{
    background: #0A0A0A;
    border: none;
    border-left: 1px solid #202020;
}}
QPushButton#chatKnowledgePallasButton {{
    color: {PALETTE.accent};
    background: transparent;
    border: none;
    border-top: 1px solid #202020;
    padding: 14px 0 2px 0;
    text-align: left;
    font-family: "Segoe UI Variable", "Segoe UI", sans-serif;
    font-size: 12px;
    font-weight: 500;
}}
QPushButton#chatKnowledgePallasButton:hover,
QPushButton#chatKnowledgePallasButton:focus {{
    color: #FFFFFF;
    background: transparent;
}}
QLabel#pageTitle {{
    color: #F1F1F1;
    font-family: "Segoe UI Variable Display", "Segoe UI", sans-serif;
    font-size: 25px;
    font-weight: 450;
    padding: 2px 0 10px 0;
}}
QFrame#workspaceStatusBar {{
    background: transparent;
    border: none;
}}
QLabel#workspaceStatusKey {{
    color: #777777;
    font-family: "Cascadia Mono", "Consolas", monospace;
    font-size: 10px;
    letter-spacing: 1px;
}}
QLabel#workspaceStatusValue {{
    color: #A9A9A9;
    font-family: "Cascadia Mono", "Consolas", monospace;
    font-size: 10px;
}}
QLabel#workspaceModelValue {{ color: {PALETTE.accent}; }}
QFrame#composer {{
    background: #0A0A0A;
    border: 1px solid #252525;
    border-radius: 16px;
}}
QFrame#composerContent,
QFrame#composerPromptRow,
QFrame#composerActionRow {{
    background: transparent;
    border: none;
}}
QFrame#composerActionRow {{
    border-top: 1px solid #181818;
}}
QLineEdit#promptInput {{
    color: #E6E6E6;
    background: transparent;
    border: none;
    border-radius: 0;
    padding: 0 10px;
    font-size: 15px;
}}
QLineEdit#promptInput:focus {{
    background: transparent;
    border: none;
}}
QPushButton#groundButton {{
    color: #9A9A9A;
    background: transparent;
    border: none;
    padding: 0 8px;
}}
QPushButton#groundButton:hover,
QPushButton#groundButton:focus {{
    color: #E8E8E8;
    background: #111111;
}}
QPushButton#sendButton {{
    min-width: {SHELL.composer_action_size}px;
    max-width: {SHELL.composer_action_size}px;
    min-height: {SHELL.composer_action_size}px;
    max-height: {SHELL.composer_action_size}px;
    color: {PALETTE.accent};
    background: transparent;
    border: none;
    border-radius: 0;
    font-size: 27px;
    font-weight: 300;
}}
QPushButton#sendButton:hover,
QPushButton#sendButton:focus {{
    color: #FF843E;
    background: #111111;
    border: none;
}}
"""


def _install_reference_geometry(window: QWidget) -> None:
    shell = window.findChild(QWidget, "referenceShell")
    top_bar = window.findChild(QFrame, "topBar")
    body = window.findChild(QFrame, "referenceBody")
    rail = window.findChild(QFrame, "iconRail")
    if shell is None or top_bar is None or body is None or rail is None:
        return
    if shell.findChild(QFrame, "convergenceHost") is not None:
        return

    shell_layout = shell.layout()
    body_layout = body.layout()
    if not isinstance(shell_layout, QVBoxLayout) or not isinstance(body_layout, QHBoxLayout):
        return

    body_layout.removeWidget(rail)
    shell_layout.removeWidget(top_bar)
    shell_layout.removeWidget(body)

    host = QFrame(shell)
    host.setObjectName("convergenceHost")
    host_layout = QHBoxLayout(host)
    host_layout.setContentsMargins(0, 0, 0, 0)
    host_layout.setSpacing(0)

    workspace_column = QFrame(host)
    workspace_column.setObjectName("workspaceColumn")
    workspace_layout = QVBoxLayout(workspace_column)
    workspace_layout.setContentsMargins(0, 0, 0, 0)
    workspace_layout.setSpacing(0)

    rail.setParent(host)
    top_bar.setParent(workspace_column)
    body.setParent(workspace_column)
    workspace_layout.addWidget(top_bar)
    workspace_layout.addWidget(body, 1)
    host_layout.addWidget(rail)
    host_layout.addWidget(workspace_column, 1)
    shell_layout.addWidget(host, 1)


def _configure_rail(window: QWidget) -> None:
    rail = window.findChild(QFrame, "iconRail")
    navigation = getattr(window, "navigation", None)
    if rail is None or navigation is None:
        return
    rail.setFixedWidth(SHELL.icon_rail_width)
    layout = rail.layout()
    if not isinstance(layout, QVBoxLayout):
        return
    layout.setContentsMargins(18, 26, 16, 18)
    layout.setSpacing(10)

    brand = rail.findChild(QLabel, "railWordmark")
    if brand is None:
        brand = QLabel("pATHENA  ◌", rail)
        brand.setObjectName("railWordmark")
        brand.setAccessibleName("pATHENA")
        layout.insertWidget(0, brand)

    navigation.setFixedWidth(SHELL.icon_rail_width - 34)
    navigation.setFixedHeight(270)
    for index, (symbol, label) in enumerate(_NAVIGATION):
        if index >= navigation.count():
            break
        item = navigation.item(index)
        item.setText(f"{symbol}   {label}")
        item.setToolTip(label.title())
        item.setData(Qt.ItemDataRole.AccessibleTextRole, label.title())
        item.setSizeHint(item.sizeHint().expandedTo(item.sizeHint()))
        item.setHidden(index >= 5)

    footer = rail.findChild(QFrame, "railFooter")
    if footer is None:
        footer = QFrame(rail)
        footer.setObjectName("railFooter")
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(4, 0, 4, 0)
        footer_layout.setSpacing(8)
        system_button = QPushButton(">_", footer)
        system_button.setObjectName("railUtilityButton")
        system_button.setAccessibleName("System")
        system_button.setToolTip("Open System")
        system_button.clicked.connect(lambda _checked=False: navigation.setCurrentRow(5))
        settings_button = QPushButton("⚙", footer)
        settings_button.setObjectName("railUtilityButton")
        settings_button.setAccessibleName("Settings")
        settings_button.setToolTip("Open Settings")
        settings_button.clicked.connect(lambda _checked=False: navigation.setCurrentRow(6))
        footer_layout.addWidget(system_button)
        footer_layout.addWidget(settings_button)
        footer_layout.addStretch(1)
        layout.addWidget(footer)


def _configure_top_bar(window: QWidget) -> None:
    top_bar = window.findChild(QFrame, "topBar")
    if top_bar is None:
        return
    layout = top_bar.layout()
    if not isinstance(layout, QHBoxLayout):
        return

    cluster = top_bar.findChild(QFrame, "shellStatusCluster")
    if cluster is None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.hide()

        cluster = QFrame(top_bar)
        cluster.setObjectName("shellStatusCluster")
        cluster_layout = QHBoxLayout(cluster)
        cluster_layout.setContentsMargins(0, 0, 0, 0)
        cluster_layout.setSpacing(10)

        core_dot = QLabel("●", cluster)
        core_dot.setObjectName("coreStateDot")
        core_label = QLabel("LOCAL CORE", cluster)
        core_label.setObjectName("shellStatusLabel")
        sep_one = QLabel("│", cluster)
        sep_one.setObjectName("shellSeparator")
        pallas_label = QLabel("PALLAS", cluster)
        pallas_label.setObjectName("shellStatusLabel")
        pallas_dot = QLabel("●", cluster)
        pallas_dot.setObjectName("pallasStateDot")
        sep_two = QLabel("│", cluster)
        sep_two.setObjectName("shellSeparator")
        clock = QLabel("--:--", cluster)
        clock.setObjectName("shellClock")

        for widget in (core_dot, core_label, sep_one, pallas_label, pallas_dot, sep_two, clock):
            cluster_layout.addWidget(widget)

        layout.setContentsMargins(18, 0, 18, 0)
        layout.addStretch(1)
        layout.addWidget(cluster)
        layout.addStretch(1)


def _configure_workspace_footer(window: QWidget) -> None:
    center = window.findChild(QFrame, "conversation")
    composer = window.findChild(QFrame, "composer")
    if center is None or composer is None:
        return
    layout = center.layout()
    if not isinstance(layout, QVBoxLayout):
        return

    status_bar = center.findChild(QFrame, "workspaceStatusBar")
    if status_bar is None:
        status_bar = QFrame(center)
        status_bar.setObjectName("workspaceStatusBar")
        status_layout = QHBoxLayout(status_bar)
        status_layout.setContentsMargins(8, 0, 8, 0)
        status_layout.setSpacing(10)

        model_key = QLabel("MODEL", status_bar)
        model_key.setObjectName("workspaceStatusKey")
        model_value = QLabel("—", status_bar)
        model_value.setObjectName("workspaceModelValue")
        model_value.setProperty("role", "workspaceStatusValue")
        separator = QLabel("•", status_bar)
        separator.setObjectName("workspaceStatusKey")
        context_key = QLabel("CONTEXT", status_bar)
        context_key.setObjectName("workspaceStatusKey")
        context_value = QLabel("—", status_bar)
        context_value.setObjectName("workspaceContextValue")
        context_value.setProperty("role", "workspaceStatusValue")

        for widget in (model_key, model_value, separator, context_key, context_value):
            status_layout.addWidget(widget)
        status_layout.addStretch(1)
        composer_index = layout.indexOf(composer)
        layout.insertWidget(max(0, composer_index), status_bar)

    composer.setMinimumWidth(620)
    composer.setMaximumWidth(760)
    composer.setFixedHeight(118)
    layout.setAlignment(composer, Qt.AlignmentFlag.AlignHCenter)

    prompt = window.findChild(QWidget, "promptInput")
    ground = window.findChild(QPushButton, "groundButton")
    send = window.findChild(QPushButton, "sendButton")
    if prompt is not None:
        prompt.setMinimumHeight(46)
        if hasattr(prompt, "setPlaceholderText"):
            prompt.setPlaceholderText("Ask anything…")
    if ground is not None:
        ground.setText("Ground")

    for object_name in ("detailsToggle", "contextToggle"):
        button = window.findChild(QPushButton, object_name)
        if button is not None:
            button.hide()

    composer_layout = composer.layout()
    content = composer.findChild(QFrame, "composerContent")
    if isinstance(composer_layout, QHBoxLayout) and content is None:
        for widget in (prompt, ground, send):
            if widget is not None:
                composer_layout.removeWidget(widget)

        composer_layout.setContentsMargins(14, 8, 10, 8)
        composer_layout.setSpacing(0)
        content = QFrame(composer)
        content.setObjectName("composerContent")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(2)

        prompt_row = QFrame(content)
        prompt_row.setObjectName("composerPromptRow")
        prompt_layout = QHBoxLayout(prompt_row)
        prompt_layout.setContentsMargins(2, 0, 2, 0)
        prompt_layout.setSpacing(0)
        if prompt is not None:
            prompt_layout.addWidget(prompt, 1)

        action_row = QFrame(content)
        action_row.setObjectName("composerActionRow")
        action_layout = QHBoxLayout(action_row)
        action_layout.setContentsMargins(2, 3, 0, 0)
        action_layout.setSpacing(8)
        if ground is not None:
            action_layout.addWidget(ground)
        action_layout.addStretch(1)
        if send is not None:
            action_layout.addWidget(send)

        content_layout.addWidget(prompt_row, 1)
        content_layout.addWidget(action_row, 0)
        composer_layout.addWidget(content, 1)


def _open_pallas_workspace(window: QWidget) -> None:
    controller = getattr(window, "_pathena_pallas_full_view_controller", None)
    opener = getattr(controller, "open_workspace", None)
    if callable(opener):
        opener()


def _configure_chat_inspector_link(window: QWidget) -> None:
    panel = window.findChild(QFrame, "chatKnowledgeOverview")
    if panel is None:
        return
    layout = panel.layout()
    if not isinstance(layout, QVBoxLayout):
        return

    controller = getattr(window, "_pathena_pallas_full_view_controller", None)
    opener = getattr(controller, "open_workspace", None)
    button = panel.findChild(QPushButton, "chatKnowledgePallasButton")
    if button is None:
        button = QPushButton("Open in PALLAS    →", panel)
        button.setObjectName("chatKnowledgePallasButton")
        button.setAccessibleName("Open Knowledge in PALLAS")
        button.setToolTip("Open the synchronized PALLAS semantic workspace")
        button.clicked.connect(lambda _checked=False: _open_pallas_workspace(window))
        layout.addWidget(button)
    button.setVisible(callable(opener))
    button.setEnabled(callable(opener))


def _sync_reference_state(window: QWidget) -> None:
    navigation = getattr(window, "navigation", None)
    row = navigation.currentRow() if navigation is not None else 0

    for button in window.findChildren(QPushButton, "topNavButton"):
        button.hide()
    for button in window.findChildren(QPushButton, "topUtilityButton"):
        button.hide()
    for name in ("topWordmark", "localPrivateDot", "localPrivateStatus"):
        label = window.findChild(QLabel, name)
        if label is not None:
            label.hide()

    core_dot = window.findChild(QLabel, "coreStateDot")
    if core_dot is not None:
        ready = bool(getattr(window, "_core_transport_ready", False))
        core_dot.setStyleSheet(f"color: {PALETTE.success};" if ready else "color: #5A5A5A;")
        core_dot.setToolTip("Local core ready" if ready else "Local core connecting")

    clock = window.findChild(QLabel, "shellClock")
    if clock is not None:
        clock.setText(datetime.now().strftime("%H:%M"))

    page_title = getattr(window, "page_title", None)
    if page_title is not None:
        page_title.setVisible(row != 0)

    keyboard_hint = window.findChild(QLabel, "keyboardHint")
    if keyboard_hint is not None:
        keyboard_hint.hide()

    center = window.findChild(QFrame, "conversation")
    if center is not None:
        center_layout = center.layout()
        if isinstance(center_layout, QVBoxLayout):
            center_layout.setContentsMargins(36, 16, 36, 18)
        for rule in center.findChildren(QFrame, "rule"):
            if rule.parentWidget() is center:
                rule.setVisible(row != 0)

    inspector = window.findChild(QFrame, "inspector")
    if inspector is not None:
        inspector.setFixedWidth(SHELL.inspector_width)
        inspector.show()

    _configure_chat_inspector_link(window)

    composer = window.findChild(QFrame, "composer")
    status_bar = window.findChild(QFrame, "workspaceStatusBar")
    if composer is not None:
        composer.setVisible(row == 0)
        composer.setMinimumWidth(620)
        composer.setMaximumWidth(760)
        composer.setFixedHeight(118)
    if status_bar is not None:
        status_bar.setVisible(row == 0)

    model_value = window.findChild(QLabel, "workspaceModelValue")
    if model_value is not None:
        model_selector = getattr(window, "model_selector", None)
        text = model_selector.currentText().strip() if model_selector is not None else ""
        model_value.setText(text or "—")
        model_value.setObjectName("workspaceModelValue")
        model_value.setStyleSheet(f"color: {PALETTE.accent};")

    context_value = window.findChild(QLabel, "workspaceContextValue")
    if context_value is not None:
        source = getattr(window, "context_value_label", None)
        text = source.text().strip() if source is not None else ""
        context_value.setText(text or "—")
        context_value.setStyleSheet("color: #A9A9A9;")

    if navigation is not None:
        navigation.setFixedWidth(SHELL.icon_rail_width - 34)
        navigation.setFixedHeight(270)
        for index, (symbol, label) in enumerate(_NAVIGATION):
            if index >= navigation.count():
                break
            item = navigation.item(index)
            item.setText(f"{symbol}   {label}")
            item.setHidden(index >= 5)
            item.setSizeHint(item.sizeHint().expandedTo(item.sizeHint()))


def apply_shell_density(window: QWidget) -> None:
    """Converge the real installed shell toward the eleven-screen reference geometry."""
    for label in window.findChildren(QLabel, "sessionLabel"):
        label.hide()

    chat_selector = getattr(window, "chat_selector", None)
    if chat_selector is not None:
        chat_selector.setAccessibleName("Conversation")
        chat_selector.setToolTip("Conversation · choose a local conversation")
        chat_selector.setMinimumWidth(280)
        chat_selector.setMaximumWidth(440)

    model_selector = getattr(window, "model_selector", None)
    if model_selector is not None:
        model_selector.setAccessibleName("Model")
        model_selector.setToolTip("Model · choose the local model used for this conversation")
        model_selector.setMinimumWidth(190)
        model_selector.setMaximumWidth(280)

    new_chat_button = getattr(window, "new_chat_button", None)
    if new_chat_button is not None:
        new_chat_button.setAccessibleName("New conversation")
    delete_chat_button = getattr(window, "delete_chat_button", None)
    if delete_chat_button is not None:
        delete_chat_button.setAccessibleName("Delete conversation")

    _install_reference_geometry(window)
    _configure_rail(window)
    _configure_top_bar(window)
    _configure_workspace_footer(window)

    system_tabs = window.findChild(QTabWidget, "systemOperationsTabs")
    if system_tabs is not None:
        system_tabs.setDocumentMode(True)
        system_tabs.setUsesScrollButtons(False)
        system_tabs.setStyleSheet(_SYSTEM_TABS_STYLESHEET)

    if _CONVERGENCE_STYLESHEET not in window.styleSheet():
        window.setStyleSheet(f"{window.styleSheet()}\n{_CONVERGENCE_STYLESHEET}")

    navigation = getattr(window, "navigation", None)
    if navigation is not None:
        navigation.currentRowChanged.connect(lambda _row: _sync_reference_state(window))

    timer = QTimer(window)
    timer.setObjectName("visualConvergenceTimer")
    timer.setInterval(1000)
    timer.timeout.connect(lambda: _sync_reference_state(window))
    timer.start()
    setattr(window, "_visual_convergence_timer", timer)
    _sync_reference_state(window)
