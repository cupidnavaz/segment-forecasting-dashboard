"""Command-line entry point."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    """Launch the Streamlit application."""
    app = Path(__file__).resolve().parents[2] / "app.py"
    return subprocess.call([sys.executable, "-m", "streamlit", "run", str(app)])


if __name__ == "__main__":
    raise SystemExit(main())
