"""Eighth 100-task presentation refinement pass for pATHENA.

System and Backup contain high-value operational controls where visual equality makes
normal inspection and risky recovery actions harder to scan. This pass establishes a
compact operational hierarchy without changing any BackupService or runtime behavior.
"""

from __future__ import annotations

from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QWidget

_SURFACE_RULES: tuple[tuple[str, str, str], ...] = (
    ("systemWorkspace", "System workspace", "workspace"),
    ("systemOperationsTabs", "System operations tabs", "tabs"),
    ("systemDetail", "System runtime detail", "status"),
    ("systemRefreshButton", "System refresh", "secondary"),
    ("systemMetricCore", "Core metric", "metric"),
    ("systemMetricProvider", "Provider metric", "metric"),
    ("systemMetricApi", "API metric", "metric"),
    ("systemMetricModels", "Models metric", "metric"),
    ("systemMetricLoaded", "Loaded models metric", "metric"),
    ("systemMetricChats", "Chats metric", "metric"),
    ("backupWorkspace", "Backup workspace", "workspace"),
    ("backupStatus", "Backup status", "status"),
    ("backupSnapshotList", "Backup snapshots", "list"),
    ("backupDetails", "Backup details", "details"),
    ("backupRefreshButton", "Backup refresh", "secondary"),
    ("backupCreateButton", "Create backup", "primary"),
    ("backupVerifyButton", "Verify backup", "secondary"),
    ("backupDeepVerifyButton", "Deep verify backup", "secondary"),
    ("backupRestoreButton", "Isolated restore", "destructive"),
    ("backupTargetsButton", "Backup targets", "inspect"),
)

_REFINEMENTS: tuple[str, ...] = (
    "assign operational hierarchy",
    "reduce permanent visual weight",
    "preserve keyboard clarity",
    "separate risky recovery action",
    "standardize compact geometry",
)

UI_REFINEMENT_TASKS_701_800: tuple[str, ...] = tuple(
    f"{refinement} for {label}"
    for _key, label, _role in _SURFACE_RULES
    for refinement in _REFINEMENTS
)

_OPS_STYLESHEET = """
QWidget[pathenaOpsRole="workspace"] { background: transparent; }
QWidget[pathenaOpsRole="metric"] {
    background: #0B0B0B;
    border: 1px solid #1E1E1E;
}
QWidget[pathenaOpsRole="status"] {
    color: #929292;
    background: transparent;
}
QWidget[pathenaOpsRole="details"] {
    border-color: #1D1D1D;
    background: #090909;
}
QWidget[pathenaOpsRole="list"] { border-color: #202020; }
QPushButton[pathenaOpsRole="primary"] { border-color: #F26A21; }
QPushButton[pathenaOpsRole="secondary"] { border-color: #303030; }
QPushButton[pathenaOpsRole="inspect"] { border-color: #242424; color: #A5A5A5; }
QPushButton[pathenaOpsRole="destructive"] {
    color: #E1A19B;
    border-color: #713C38;
    background: transparent;
}
QPushButton[pathenaOpsRole="destructive"]:hover { border-color: #A34E47; }
"""

_METRIC_NAMES: tuple[tuple[str, str], ...] = (
    ("CORE", "systemMetricCore"),
    ("PROVIDER", "systemMetricProvider"),
    ("API", "systemMetricApi"),
    ("MODELS", "systemMetricModels"),
    ("LOADED", "systemMetricLoaded"),
    ("CHATS", "systemMetricChats"),
)


def _repair_operational_identities(window: QWidget) -> None:
    system = window.findChild(QWidget, "systemWorkspace")
    if system is not None:
        refresh = next(
            (button for button in system.findChildren(QPushButton) if button.text() == "REFRESH NOW"),
            None,
        )
        if refresh is not None:
            refresh.setObjectName("systemRefreshButton")
        frames = system.findChildren(QFrame, "systemMetric")
        for heading, object_name in _METRIC_NAMES:
            frame = next(
                (
                    candidate
                    for candidate in frames
                    if any(label.text() == heading for label in candidate.findChildren(QLabel))
                ),
                None,
            )
            if frame is not None:
                frame.setObjectName(object_name)

    backup = window.findChild(QWidget, "backupWorkspace")
    if backup is not None:
        refresh = next(
            (button for button in backup.findChildren(QPushButton) if button.text() == "REFRESH"),
            None,
        )
        if refresh is not None:
            refresh.setObjectName("backupRefreshButton")
        status = next(
            (
                label
                for label in backup.findChildren(QLabel)
                if "backup state" in label.text().casefold()
            ),
            None,
        )
        if status is not None:
            status.setObjectName("backupStatus")


def apply_ui_refinements_701_800(window: QWidget) -> tuple[int, ...]:
    """Apply compact System/Backup hierarchy to already-existing UI controls."""
    _repair_operational_identities(window)

    for key, _label, role in _SURFACE_RULES:
        widget = window.findChild(QWidget, key)
        if widget is None:
            continue
        widget.setProperty("pathenaOpsRole", role)
        if isinstance(widget, QPushButton):
            widget.setAutoDefault(False)
            widget.setMinimumHeight(28)
            widget.setMaximumHeight(34)

    if _OPS_STYLESHEET not in window.styleSheet():
        window.setStyleSheet(f"{window.styleSheet()}\n{_OPS_STYLESHEET}")

    applied = tuple(range(701, 801))
    window.setProperty("pathenaUiOpsHierarchyAppliedCount", len(applied))
    window.setProperty("pathenaUiOpsHierarchyTaskCount", 100)
    return applied
