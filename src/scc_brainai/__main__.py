"""Permet ``python -m scc_brainai``."""

from __future__ import annotations

import sys

from scc_brainai.cli import main

if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
