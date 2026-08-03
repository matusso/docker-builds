#!/usr/bin/env python3
"""Fail if the README catalog and the workflow version pins have drifted apart.

A zero-dependency entry point over :mod:`scripts.catalog`, for running the same
consistency checks the pytest suite runs without installing anything:

    python3 scripts/check_catalog.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from catalog import (
    CatalogError,
    catalog_rows,
    collect_problems,
)


def main() -> int:
    try:
        problems = collect_problems()
        row_count = len(catalog_rows())
    except CatalogError as exc:
        print(f"::error::{exc}", file=sys.stderr)
        return 1

    if problems:
        print(f"Catalog is out of sync ({len(problems)} problem(s)):\n", file=sys.stderr)
        for problem in problems:
            print(f"::error::{problem}", file=sys.stderr)
        print(
            "\nFix the workflow pin, the sonar upstream-ref, or the README catalog "
            "table so all three agree.",
            file=sys.stderr,
        )
        return 1

    print(f"Catalog is consistent: {row_count} images, plus the caddy binary release.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
