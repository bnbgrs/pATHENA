from pathlib import Path


def test_visual_manifest_reports_actual_capture_count_and_surfaces() -> None:
    source = Path("scripts/render_pathena_ui_snapshot.py").read_text(encoding="utf-8")

    assert '"captured_reference_count": len(captures)' in source
    assert '"captured_reference_surfaces": [capture["label"] for capture in captures]' in source
