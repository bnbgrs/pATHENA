from __future__ import annotations

import subprocess
import sys


def test_recovery_cli_import_keeps_unrelated_runtime_graph_unloaded() -> None:
    code = r"""
import sys
import athena.recovery_cli

athena.recovery_cli.build_parser()

forbidden = (
    "athena.backup.service",
    "athena.core.application",
    "athena.model.adapters.lm_studio",
    "athena.model.adapters.lm_studio_embeddings",
    "athena.news.service",
    "athena.security.service",
)

loaded = [
    name
    for name in forbidden
    if name in sys.modules
]

if loaded:
    raise SystemExit(
        "forbidden recovery CLI imports: "
        + ", ".join(loaded)
    )
"""

    completed = subprocess.run(
        [
            sys.executable,
            "-c",
            code,
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, (
        completed.stdout
        + completed.stderr
    )
