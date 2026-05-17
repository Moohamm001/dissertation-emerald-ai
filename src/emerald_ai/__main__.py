"""Module entrypoint so `python -m emerald_ai <cmd>` works after install."""
from __future__ import annotations

from emerald_ai.cli import app

if __name__ == "__main__":
    app()
