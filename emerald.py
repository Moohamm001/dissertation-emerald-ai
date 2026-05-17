"""Zero-install launcher for the EMERALD-AI CLI.

Run with:  python emerald.py <command>  [--options]

This wrapper lets you drive every project task without installing the package
as editable (no `pip install -e .` required). Works identically on Windows,
macOS, and Linux. You still need the runtime dependencies — install them with:

    pip install -r requirements.txt
    # OR
    pip install -e ".[dev,docs]"

Examples:
    python emerald.py --help
    python emerald.py version
    python emerald.py research status
    python emerald.py proposal
    python emerald.py test
"""
from __future__ import annotations

import sys
from pathlib import Path

# Make src/ importable without requiring the package to be installed.
_SRC = Path(__file__).resolve().parent / "src"
if _SRC.exists() and str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from emerald_ai.cli import app  # noqa: E402

if __name__ == "__main__":
    app()
