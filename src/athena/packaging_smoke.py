"""Fail-closed packaging metadata smoke checks for pATHENA release candidates."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from dataclasses import dataclass
from importlib import metadata

_REQUIRED_DISTRIBUTIONS = ("pypdf",)


@dataclass(frozen=True, slots=True)
class DistributionMetadataCheck:
    distribution: str
    status: str
    detail: str


@dataclass(frozen=True, slots=True)
class PackagingSmokeReport:
    checks: tuple[DistributionMetadataCheck, ...]
    ready: bool


def _canonical_distribution_name(value: object) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError("Distribution name must be non-empty text.")
    if value != value.strip():
        raise ValueError("Distribution name must use canonical trimmed text.")
    return value


def check_distribution_metadata(distribution: str) -> DistributionMetadataCheck:
    canonical = _canonical_distribution_name(distribution)
    try:
        version = metadata.version(canonical)
    except metadata.PackageNotFoundError:
        return DistributionMetadataCheck(
            canonical,
            "FAIL",
            f"{canonical} distribution metadata is unavailable",
        )
    except Exception as exc:
        return DistributionMetadataCheck(
            canonical,
            "FAIL",
            f"{canonical} metadata lookup failed: {type(exc).__name__}: {exc}",
        )
    if not isinstance(version, str) or not version.strip():
        return DistributionMetadataCheck(
            canonical,
            "FAIL",
            f"{canonical} distribution metadata returned an empty version",
        )
    return DistributionMetadataCheck(canonical, "PASS", f"{canonical} {version}")


def run_packaging_smoke(
    required_distributions: Sequence[str] = _REQUIRED_DISTRIBUTIONS,
) -> PackagingSmokeReport:
    if isinstance(required_distributions, (str, bytes)):
        raise ValueError("Required distributions must be a sequence of names.")
    names = tuple(required_distributions)
    if not names:
        raise ValueError("At least one required distribution must be checked.")
    checks = tuple(check_distribution_metadata(name) for name in names)
    return PackagingSmokeReport(
        checks=checks,
        ready=all(check.status == "PASS" for check in checks),
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="athena-packaging-smoke",
        description="Verify distribution metadata required by packaged pATHENA runtimes.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit the packaging smoke result as one machine-readable JSON object.",
    )
    return parser


def _report_payload(report: PackagingSmokeReport) -> dict[str, object]:
    return {
        "checks": [
            {
                "distribution": check.distribution,
                "status": check.status,
                "detail": check.detail,
            }
            for check in report.checks
        ],
        "ready": report.ready,
    }


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    report = run_packaging_smoke()
    if args.json:
        print(json.dumps(_report_payload(report), sort_keys=True))
    else:
        for check in report.checks:
            print(f"[{check.status}] {check.distribution}: {check.detail}")
        print(f"Packaging metadata ready: {'YES' if report.ready else 'NO'}")
    return 0 if report.ready else 2


if __name__ == "__main__":
    raise SystemExit(main())
