"""Dedicated helper-process dispatcher for packaged pATHENA desktop workspaces."""

from __future__ import annotations

import sys
from collections.abc import Callable, Sequence


def _dispatch(module_name: str) -> Callable[[Sequence[str] | None], int] | None:
    if module_name == "athena.desktop.jobs_cli":
        from athena.desktop.jobs_cli import main

        return main
    if module_name == "athena.desktop.sources_cli":
        from athena.desktop.sources_cli import main

        return main
    if module_name == "athena.desktop.research_cli":
        from athena.desktop.research_cli import main

        return main
    if module_name == "athena":
        from athena.__main__ import main

        return main
    return None


def main(argv: Sequence[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    if len(arguments) < 2 or arguments[0] != "-m":
        print("pATHENA helper requires a supported '-m <module>' invocation.", file=sys.stderr)
        return 2

    module_name = arguments[1]
    target = _dispatch(module_name)
    if target is None:
        print(f"Unsupported packaged helper module: {module_name}", file=sys.stderr)
        return 2

    return int(target(arguments[2:]))


if __name__ == "__main__":
    raise SystemExit(main())
