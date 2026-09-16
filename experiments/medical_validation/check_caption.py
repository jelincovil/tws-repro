#!/usr/bin/env python3
"""Shim: canonical checker is qa/check_caption.py."""
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).resolve().parent / "qa" / "check_caption.py"),
               run_name="__main__")
