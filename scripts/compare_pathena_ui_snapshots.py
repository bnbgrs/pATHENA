"""Compare the eleven canonical pATHENA UI captures against a versioned baseline bundle."""

from __future__ import annotations

import argparse
import base64
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

import numpy as np
from numpy.typing import NDArray
from PySide6.QtGui import QImage

EXPECTED_SURFACES = (
    "01-chat.png",
    "02-knowledge.png",
    "03-research.png",
    "04-jobs.png",
    "05-files.png",
    "06-system.png",
    "07-settings.png",
    "08-pallas.png",
    "09-command-palette.png",
    "10-help.png",
    "11-comfyui.png",
)

PixelArray = NDArray[np.uint8]


@dataclass(frozen=True)
class ComparisonPolicy:
    channel_tolerance: int = 4
    max_changed_ratio: float = 0.002
    max_mean_channel_delta: float = 0.35


def _load_rgba(path: Path) -> PixelArray:
    image = QImage(str(path))
    if image.isNull():
        raise ValueError(f"Unable to decode PNG: {path}")
    image = image.convertToFormat(QImage.Format.Format_RGBA8888)
    data = np.frombuffer(image.bits(), dtype=np.uint8, count=image.sizeInBytes())
    return cast(
        PixelArray,
        data.reshape((image.height(), image.bytesPerLine()))[:, : image.width() * 4]
        .reshape(image.height(), image.width(), 4)
        .copy(),
    )


def _load_rgba_bytes(payload: bytes) -> PixelArray:
    image = QImage.fromData(payload)
    if image.isNull():
        raise ValueError("Unable to decode baseline PNG payload")
    image = image.convertToFormat(QImage.Format.Format_RGBA8888)
    data = np.frombuffer(image.bits(), dtype=np.uint8, count=image.sizeInBytes())
    return cast(
        PixelArray,
        data.reshape((image.height(), image.bytesPerLine()))[:, : image.width() * 4]
        .reshape(image.height(), image.width(), 4)
        .copy(),
    )


def _png_bytes(path: Path) -> bytes:
    payload = path.read_bytes()
    if not payload.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError(f"Expected PNG file: {path}")
    return payload


def _actual_surface_files(actual_dir: Path) -> tuple[str, ...]:
    return tuple(sorted(path.name for path in actual_dir.glob("*.png")))


def _validate_surface_set(actual_dir: Path) -> None:
    actual = _actual_surface_files(actual_dir)
    if actual != EXPECTED_SURFACES:
        missing = sorted(set(EXPECTED_SURFACES) - set(actual))
        extra = sorted(set(actual) - set(EXPECTED_SURFACES))
        raise ValueError(f"Surface set mismatch; missing={missing}, extra={extra}")


def write_baseline_bundle(
    actual_dir: Path,
    destination: Path,
    *,
    candidate_sha: str,
    policy: ComparisonPolicy | None = None,
) -> None:
    resolved_policy = policy or ComparisonPolicy()
    _validate_surface_set(actual_dir)
    surfaces: dict[str, dict[str, object]] = {}
    for name in EXPECTED_SURFACES:
        pixels = _load_rgba(actual_dir / name)
        surfaces[name] = {
            "width": int(pixels.shape[1]),
            "height": int(pixels.shape[0]),
            "png_base64": base64.b64encode(_png_bytes(actual_dir / name)).decode("ascii"),
        }
    payload = {
        "schema_version": 1,
        "platform": "windows-2025",
        "candidate_sha": candidate_sha,
        "policy": {
            "channel_tolerance": resolved_policy.channel_tolerance,
            "max_changed_ratio": resolved_policy.max_changed_ratio,
            "max_mean_channel_delta": resolved_policy.max_mean_channel_delta,
        },
        "surfaces": surfaces,
    }
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _save_diff(diff: PixelArray, destination: Path) -> None:
    amplified = np.clip(diff * 8, 0, 255).astype(np.uint8)
    amplified[:, :, 3] = 255
    height, width, _channels = amplified.shape
    image = QImage(
        amplified.data,
        width,
        height,
        width * 4,
        QImage.Format.Format_RGBA8888,
    ).copy()
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not image.save(str(destination), b"PNG"):
        raise RuntimeError(f"Unable to save visual diff: {destination}")


def _load_baseline(path: Path) -> dict[str, Any]:
    parsed: object = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(parsed, dict):
        raise ValueError("Visual baseline root must be an object")
    return cast(dict[str, Any], parsed)


def compare_bundle(
    actual_dir: Path,
    baseline_bundle: Path,
    diff_dir: Path,
) -> dict[str, object]:
    _validate_surface_set(actual_dir)
    baseline = _load_baseline(baseline_bundle)
    if baseline.get("schema_version") != 1 or baseline.get("platform") != "windows-2025":
        raise ValueError("Unsupported visual baseline bundle")
    surfaces_value = baseline.get("surfaces")
    if not isinstance(surfaces_value, dict):
        raise ValueError("Baseline surfaces are missing")
    surfaces = cast(dict[str, Any], surfaces_value)
    if tuple(sorted(surfaces)) != EXPECTED_SURFACES:
        raise ValueError("Baseline surface set does not match the canonical eleven surfaces")
    raw_policy_value = baseline.get("policy")
    if not isinstance(raw_policy_value, dict):
        raise ValueError("Baseline comparison policy is missing")
    raw_policy = cast(dict[str, Any], raw_policy_value)
    policy = ComparisonPolicy(
        channel_tolerance=int(raw_policy["channel_tolerance"]),
        max_changed_ratio=float(raw_policy["max_changed_ratio"]),
        max_mean_channel_delta=float(raw_policy["max_mean_channel_delta"]),
    )

    results: list[dict[str, object]] = []
    failures: list[str] = []
    for name in EXPECTED_SURFACES:
        entry_value = surfaces[name]
        if not isinstance(entry_value, dict):
            raise ValueError(f"Invalid baseline entry for {name}")
        entry = cast(dict[str, Any], entry_value)
        encoded = entry.get("png_base64")
        if not isinstance(encoded, str):
            raise ValueError(f"Missing baseline PNG payload for {name}")
        expected = _load_rgba_bytes(base64.b64decode(encoded, validate=True))
        actual = _load_rgba(actual_dir / name)
        if actual.shape != expected.shape:
            failures.append(f"{name}: geometry {actual.shape} != {expected.shape}")
            results.append({"surface": name, "status": "FAIL", "reason": "geometry"})
            continue
        delta = cast(
            PixelArray,
            np.abs(actual.astype(np.int16) - expected.astype(np.int16)).astype(np.uint8),
        )
        changed = np.any(delta[:, :, :3] > policy.channel_tolerance, axis=2)
        changed_ratio = float(changed.mean())
        mean_delta = float(delta[:, :, :3].mean())
        status = (
            "PASS"
            if changed_ratio <= policy.max_changed_ratio
            and mean_delta <= policy.max_mean_channel_delta
            else "FAIL"
        )
        results.append(
            {
                "surface": name,
                "status": status,
                "changed_ratio": round(changed_ratio, 8),
                "mean_channel_delta": round(mean_delta, 8),
            }
        )
        if status == "FAIL":
            failures.append(
                f"{name}: changed_ratio={changed_ratio:.6f}, mean_delta={mean_delta:.6f}"
            )
            _save_diff(delta, diff_dir / name)

    report: dict[str, object] = {
        "status": "PASS" if not failures else "FAIL",
        "baseline_candidate_sha": str(baseline.get("candidate_sha", "")),
        "policy": raw_policy,
        "results": results,
        "failures": failures,
    }
    diff_dir.mkdir(parents=True, exist_ok=True)
    (diff_dir / "report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return report


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--actual-dir", type=Path, required=True)
    parser.add_argument("--baseline-bundle", type=Path, required=True)
    parser.add_argument("--diff-dir", type=Path, required=True)
    parser.add_argument("--write-baseline", action="store_true")
    parser.add_argument("--candidate-sha", default="")
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    if args.write_baseline:
        if not args.candidate_sha:
            raise ValueError("--candidate-sha is required when writing a baseline")
        write_baseline_bundle(
            args.actual_dir,
            args.baseline_bundle,
            candidate_sha=args.candidate_sha,
        )
        print(args.baseline_bundle.resolve())
        return 0
    if not args.baseline_bundle.is_file():
        raise FileNotFoundError(f"Committed visual baseline is missing: {args.baseline_bundle}")
    report = compare_bundle(args.actual_dir, args.baseline_bundle, args.diff_dir)
    print(json.dumps(report, sort_keys=True))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
