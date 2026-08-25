"""Controlled native-Windows source launch for SHA-bound acceptance diagnostics."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from collections.abc import Sequence
from pathlib import Path


def _safe_name(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")
    return normalized or "screen"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--screenshot-directory", type=Path, required=True)
    parser.add_argument("--initial-delay-seconds", type=int, default=7)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if os.name != "nt":
        raise RuntimeError("This diagnostic is valid only on native Windows.")
    if args.initial_delay_seconds < 5:
        raise ValueError("The desktop needs at least five seconds before capture.")

    runtime_root = args.runtime_root.resolve()
    screenshot_directory = args.screenshot_directory.resolve()
    runtime_root.mkdir(parents=True, exist_ok=True)
    screenshot_directory.mkdir(parents=True, exist_ok=True)
    os.environ["ATHENA_LOCAL_ROOT"] = str(runtime_root)
    os.environ["QT_QPA_PLATFORM"] = "offscreen"

    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QMainWindow, QWidget

    from athena.desktop.app import create_application
    from athena.desktop.app import main as desktop_main
    from athena.desktop.command_palette import CommandPaletteController
    from athena.desktop.pathena_pallas_field import PallasGroundedFieldController
    from athena.desktop.pathena_pallas_semantic import (
        PallasGraphSnapshot,
        PallasNodeKind,
        PallasSemanticEdge,
        PallasSemanticNode,
    )

    app = create_application(["pathena-windows-candidate-acceptance"])
    captures: list[dict[str, object]] = []
    errors: list[str] = []
    started = time.monotonic()

    def find_window() -> QMainWindow:
        windows = [
            widget
            for widget in app.topLevelWidgets()
            if isinstance(widget, QMainWindow) and widget.isVisible()
        ]
        if len(windows) != 1:
            raise RuntimeError(
                f"Expected exactly one visible main window, found {len(windows)}."
            )
        return windows[0]

    def save_widget(widget: QWidget, *, ordinal: int, label: str, kind: str) -> str:
        output = screenshot_directory / f"{ordinal:02d}-{_safe_name(label)}.png"
        if not widget.grab().save(str(output), "PNG"):
            raise RuntimeError(f"Qt failed to save {output.name}.")
        captures.append(
            {
                "ordinal": ordinal,
                "label": label,
                "kind": kind,
                "file": output.name,
                "width": widget.width(),
                "height": widget.height(),
            }
        )
        return output.name

    def capture_row(row: int) -> None:
        try:
            window = find_window()
            navigation = getattr(window, "navigation", None)
            pages = getattr(window, "pages", None)
            if navigation is None or pages is None:
                raise RuntimeError("Desktop navigation contract is unavailable.")
            if navigation.count() != 7 or pages.count() != 7:
                raise RuntimeError(
                    "Candidate must expose its seven primary navigation pages for this probe; "
                    f"found {navigation.count()} nav items and {pages.count()} pages."
                )
            navigation.setCurrentRow(row)
            app.processEvents()
            label = navigation.item(row).text()
            save_widget(window, ordinal=row + 1, label=label, kind="workspace")
            captures[-1]["row"] = row
            captures[-1]["page_index"] = pages.currentIndex()
        except Exception as exc:  # noqa: BLE001 - callback must preserve evidence
            errors.append(f"workspace row {row}: {type(exc).__name__}: {exc}")

    def diagnostic_pallas_snapshot() -> PallasGraphSnapshot:
        focus = PallasSemanticNode(
            node_id="focus:windows-reference",
            kind=PallasNodeKind.FOCUS,
            entity_type="diagnostic_reference",
            entity_id="windows-reference",
            revision_id=None,
            title="Grounded response",
            summary="Deterministic Windows acceptance fixture for the real PALLAS renderer.",
            epistemic_status=None,
            cited=True,
        )
        source = PallasSemanticNode(
            node_id="source_anchor:source-reference",
            kind=PallasNodeKind.SOURCE,
            entity_type="source_anchor",
            entity_id="source-reference",
            revision_id="revision-source-reference",
            title="Persisted source",
            summary="A source-shaped fixture used only to exercise presentation.",
            epistemic_status=None,
            cited=True,
        )
        claim = PallasSemanticNode(
            node_id="canonical_claim:claim-reference",
            kind=PallasNodeKind.CLAIM,
            entity_type="canonical_claim",
            entity_id="claim-reference",
            revision_id="revision-claim-reference",
            title="Supported claim",
            summary="A claim-shaped fixture used only to exercise presentation.",
            epistemic_status="supported",
            cited=True,
            confidence=0.92,
        )
        knowledge = PallasSemanticNode(
            node_id="knowledge_unit:knowledge-reference",
            kind=PallasNodeKind.KNOWLEDGE,
            entity_type="knowledge_unit",
            entity_id="knowledge-reference",
            revision_id="revision-knowledge-reference",
            title="Canonical knowledge",
            summary="A knowledge-shaped fixture used only to exercise presentation.",
            epistemic_status="accepted",
            cited=True,
            confidence=0.88,
        )
        conflict = PallasSemanticNode(
            node_id="conflict:conflict-reference",
            kind=PallasNodeKind.CONFLICT,
            entity_type="diagnostic_conflict",
            entity_id="conflict-reference",
            revision_id=None,
            title="Conflicting evidence",
            summary="A conflict-shaped fixture used only to exercise presentation.",
            epistemic_status="conflict",
            cited=False,
            confidence=0.51,
        )
        return PallasGraphSnapshot(
            graph_id="diagnostic:windows-reference",
            nodes=(focus, source, claim, knowledge, conflict),
            edges=(
                PallasSemanticEdge(focus.node_id, source.node_id, "cites"),
                PallasSemanticEdge(focus.node_id, claim.node_id, "cites"),
                PallasSemanticEdge(focus.node_id, knowledge.node_id, "includes_context"),
                PallasSemanticEdge(focus.node_id, conflict.node_id, "includes_context"),
            ),
            focus_id=focus.node_id,
            status="ready",
            status_detail="Windows acceptance fixture for the real PALLAS renderer.",
        )

    def capture_pallas() -> None:
        try:
            window = find_window()
            grounded = window.property("pathenaPallasGroundedController")
            if not isinstance(grounded, PallasGroundedFieldController):
                raise RuntimeError("Real PALLAS grounded controller is unavailable.")
            grounded.apply_snapshot(diagnostic_pallas_snapshot())

            full_view = getattr(window, "_pathena_pallas_full_view_controller", None)
            if full_view is None or not callable(getattr(full_view, "open_workspace", None)):
                raise RuntimeError("Real PALLAS full-view controller is unavailable.")
            full_view.open_workspace()
            app.processEvents()
            dialog = getattr(full_view, "dialog", None)
            workspace = getattr(full_view, "workspace", None)
            if not isinstance(dialog, QWidget) or not dialog.isVisible() or workspace is None:
                raise RuntimeError("PALLAS full workspace did not become visible.")
            if workspace.field.property("pathenaPallasMode") != "full":
                raise RuntimeError("PALLAS reference capture is not using the full renderer.")
            if workspace.field.property("pathenaUiState") != "ready":
                raise RuntimeError("PALLAS reference capture did not reach ready state.")
            if int(workspace.field.property("pathenaPallasNodeCount") or 0) != 5:
                raise RuntimeError("PALLAS reference graph did not render all diagnostic nodes.")
            save_widget(dialog, ordinal=8, label="PALLAS", kind="full-pallas")
            captures[-1]["fixture"] = "diagnostic semantic graph; presentation only"
            dialog.hide()
        except Exception as exc:  # noqa: BLE001 - callback must preserve evidence
            errors.append(f"PALLAS: {type(exc).__name__}: {exc}")

    def palette_controller() -> CommandPaletteController:
        window = find_window()
        controller = next(
            (
                child
                for child in window.children()
                if isinstance(child, CommandPaletteController)
            ),
            None,
        )
        if controller is None:
            raise RuntimeError("Real Command Palette controller is unavailable.")
        return controller

    def capture_commands() -> None:
        try:
            controller = palette_controller()
            controller.open()
            app.processEvents()
            if not controller.dialog.isVisible():
                raise RuntimeError("Command Palette did not become visible.")
            if controller.results.count() < 10:
                raise RuntimeError(
                    f"Command Palette exposed only {controller.results.count()} live commands."
                )
            save_widget(
                controller.dialog,
                ordinal=9,
                label="Command Palette",
                kind="command-palette",
            )
            captures[-1]["result_count"] = controller.results.count()
            controller.dialog.hide()
        except Exception as exc:  # noqa: BLE001 - callback must preserve evidence
            errors.append(f"Command Palette: {type(exc).__name__}: {exc}")

    def capture_help() -> None:
        try:
            controller = palette_controller()
            controller.open_help()
            app.processEvents()
            if not controller.help_dialog.isVisible():
                raise RuntimeError("Help surface did not become visible.")
            help_text = controller.help_text.toPlainText()
            if "pATHENA capabilities" not in help_text or "Keyboard" not in help_text:
                raise RuntimeError("Help did not render the live capability guide.")
            save_widget(controller.help_dialog, ordinal=10, label="Help", kind="help")
            captures[-1]["catalog_version"] = str(
                controller.help_text.property("pathenaCapabilityCatalogVersion") or ""
            )
            captures[-1]["catalog_drift"] = bool(
                controller.help_text.property("pathenaCapabilityCatalogDrift")
            )
            controller.help_dialog.hide()
        except Exception as exc:  # noqa: BLE001 - callback must preserve evidence
            errors.append(f"Help: {type(exc).__name__}: {exc}")

    interval_ms = 500
    first_capture_ms = args.initial_delay_seconds * 1_000
    for row in range(7):
        QTimer.singleShot(
            first_capture_ms + row * interval_ms,
            lambda selected_row=row: capture_row(selected_row),
        )

    after_workspaces_ms = first_capture_ms + 7 * interval_ms + 500
    QTimer.singleShot(after_workspaces_ms, capture_pallas)
    QTimer.singleShot(after_workspaces_ms + 1_000, capture_commands)
    QTimer.singleShot(after_workspaces_ms + 2_000, capture_help)
    QTimer.singleShot(after_workspaces_ms + 3_000, app.quit)

    exit_code = desktop_main(["pathena-windows-candidate-acceptance"])
    duration_seconds = time.monotonic() - started
    expected_capture_count = 10
    manifest = {
        "candidate_sha": os.environ.get("CANDIDATE_SHA", ""),
        "platform": sys.platform,
        "status": (
            "PASS"
            if not errors and len(captures) == expected_capture_count
            else "FAIL"
        ),
        "duration_seconds": round(duration_seconds, 3),
        "captures": captures,
        "errors": errors,
        "target_coverage": {
            "captured_reference_surfaces": [
                "Chat",
                "Knowledge",
                "Research",
                "Jobs",
                "Files",
                "System",
                "Settings",
                "interactive PALLAS",
                "standalone search/command palette reference state",
                "Help",
            ],
            "not_implemented_as_target_screens": ["ComfyUI"],
            "captured_reference_count": expected_capture_count,
            "assigned_reference_count": 11,
        },
    }
    (screenshot_directory / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    if exit_code != 0:
        raise RuntimeError(f"Desktop returned exit code {exit_code}.")
    if errors or len(captures) != expected_capture_count:
        raise RuntimeError(
            "Desktop capture failed: " + "; ".join(errors or ["capture count mismatch"])
        )
    if duration_seconds < args.initial_delay_seconds:
        raise RuntimeError("Desktop exited before the controlled capture window.")

    print(json.dumps(manifest, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
