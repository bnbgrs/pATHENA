from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from PySide6.QtGui import QImage

from scripts.compare_pathena_ui_snapshots import (
    EXPECTED_SURFACES,
    compare_bundle,
    write_baseline_bundle,
)
from scripts.render_pathena_ui_snapshot import WORKSPACE_SURFACE_LABELS, _safe_name


def _write_png(path: Path, *, value: int, changed_pixel: tuple[int, int] | None = None) -> None:
    pixels = np.full((20, 20, 4), value, dtype=np.uint8)
    pixels[:, :, 3] = 255
    if changed_pixel is not None:
        y, x = changed_pixel
        pixels[y, x, :3] = 255 - value
    image = QImage(
        pixels.data,
        pixels.shape[1],
        pixels.shape[0],
        pixels.shape[1] * 4,
        QImage.Format.Format_RGBA8888,
    ).copy()
    assert image.save(str(path), "PNG")


def _capture_set(root: Path, *, changed_surface: str | None = None) -> None:
    root.mkdir(parents=True, exist_ok=True)
    for index, name in enumerate(EXPECTED_SURFACES):
        changed = (0, 0) if name == changed_surface else None
        _write_png(root / name, value=20 + index, changed_pixel=changed)


def test_renderer_workspace_names_match_comparator_contract() -> None:
    workspace_names = tuple(
        f"{ordinal:02d}-{_safe_name(label)}.png"
        for ordinal, label in enumerate(WORKSPACE_SURFACE_LABELS, start=1)
    )
    renderer_names = workspace_names + (
        "08-pallas.png",
        "09-command-palette.png",
        "10-help.png",
        "11-comfyui.png",
    )

    assert renderer_names == EXPECTED_SURFACES


def test_identical_baseline_passes(tmp_path: Path) -> None:
    actual = tmp_path / "actual"
    bundle = tmp_path / "baseline.json"
    diff = tmp_path / "diff"
    _capture_set(actual)
    write_baseline_bundle(actual, bundle, candidate_sha="a" * 40)

    report = compare_bundle(actual, bundle, diff)

    assert report["status"] == "PASS"
    assert report["failures"] == []


def test_known_pixel_delta_fails_and_writes_diff(tmp_path: Path) -> None:
    baseline_capture = tmp_path / "baseline-capture"
    actual = tmp_path / "actual"
    bundle = tmp_path / "baseline.json"
    diff = tmp_path / "diff"
    _capture_set(baseline_capture)
    _capture_set(actual, changed_surface="01-chat.png")
    write_baseline_bundle(baseline_capture, bundle, candidate_sha="b" * 40)

    report = compare_bundle(actual, bundle, diff)

    assert report["status"] == "FAIL"
    assert (diff / "01-chat.png").is_file()


def test_missing_surface_fails_closed(tmp_path: Path) -> None:
    actual = tmp_path / "actual"
    bundle = tmp_path / "baseline.json"
    diff = tmp_path / "diff"
    _capture_set(actual)
    write_baseline_bundle(actual, bundle, candidate_sha="c" * 40)
    (actual / "11-comfyui.png").unlink()

    with pytest.raises(ValueError, match="Surface set mismatch"):
        compare_bundle(actual, bundle, diff)


def test_extra_surface_fails_closed(tmp_path: Path) -> None:
    actual = tmp_path / "actual"
    bundle = tmp_path / "baseline.json"
    diff = tmp_path / "diff"
    _capture_set(actual)
    write_baseline_bundle(actual, bundle, candidate_sha="d" * 40)
    _write_png(actual / "12-unexpected.png", value=42)

    with pytest.raises(ValueError, match="Surface set mismatch"):
        compare_bundle(actual, bundle, diff)
