#!/usr/bin/env python3
"""
MegaCLI Entry Point

This script serves as a simple entry point to run the MegaCLI application
from the project root, ensuring the correct PYTHONPATH is set up.

Usage:
    python main.py [args]
"""
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).parent.resolve()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "src"))

if __name__ == "__main__":
    try:
        from src.megacli import main
        main()
    except ImportError as e:
        print(f"Error starting MegaCLI: {e}")
        # Try to run directly if import fails (fallback)
        import runpy
        runpy.run_module("src.megacli", run_name="__main__")
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)
