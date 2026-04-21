"""
Veil entry point.

Usage:
    uvicorn backend.main:app --reload
"""

from pathlib import Path
import sys

# Ensure project root is on sys.path so imports work
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.core import create_app
from backend.core.plugin_registry import discover_plugins

# Discover plugins BEFORE creating the app
discover_plugins()

app = create_app()
