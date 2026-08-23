from __future__ import annotations

from PySide6.QtWidgets import QApplication, QFrame, QLabel, QPushButton, QVBoxLayout, QWidget

from athena.desktop.app import create_application
from athena.desktop.pathena_workspace_presentation import (
    _sync_dynamic_workspace_copy,
    apply_workspace_presentation,
)


def _app() -> QApplication:
    return create_application(["pathena-files-system-presentation-test"])


def test_files_actions_and_system_metrics_follow_quiet_presentation() -> None:
    app = _app()
    window = QWidget()
    root = QVBoxLayout(window)

    files = QWidget(window)
    files.setObjectName("filesWorkspace")
    files_layout = QVBoxLayout(files)
    refresh = QPushButton("REFRESH", files)
    process = QPushButton("PROCESS / RETRY", files)
    import_file = QPushButton("IMPORT FILE", files)
    process.setEnabled(False)
    for widget in (refresh, process, import_file):
        files_layout.addWidget(widget)
    root.addWidget(files)

    system = QWidget(window)
    system.setObjectName("systemWorkspace")
    system_layout = QVBoxLayout(system)
    metric = QFrame(system)
    metric.setObjectName("systemMetric")
    metric_layout = QVBoxLayout(metric)
    metric_heading = QLabel("CORE", metric)
    metric_value = QLabel("READY", metric)
    metric_value.setObjectName("settingsValue")
    metric_layout.addWidget(metric_heading)
    metric_layout.addWidget(metric_value)
    system_layout.addWidget(metric)
    root.addWidget(system)

    try:
        apply_workspace_presentation(window)
        _sync_dynamic_workspace_copy(window)
        app.processEvents()

        assert refresh.objectName() == "fileRefreshButton"
        assert process.objectName() == "fileProcessButton"
        assert import_file.objectName() == "fileImportButton"
        assert import_file.property("role") == "primary"
        assert process.isHidden()

        assert metric.objectName() == "systemMetricQuiet"
        assert metric_heading.text() == "Core"
        assert metric_value.text() == "Ready"

        process.setEnabled(True)
        metric_value.setText("DISCONNECTED")
        _sync_dynamic_workspace_copy(window)
        app.processEvents()
        assert process.isHidden() is False
        assert metric_value.text() == "Disconnected"
    finally:
        window.close()
        app.processEvents()
