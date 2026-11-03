"""Allow isolated parser tests to import modules without booting Home Assistant.

These lightweight tests import individual integration modules, not the HA integration
entry point. Real Home Assistant integration tests must use HA's test harness.
"""
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if 'custom_components' not in sys.modules:
    package = types.ModuleType('custom_components')
    package.__path__ = [str(ROOT / 'custom_components')]
    sys.modules['custom_components'] = package
if 'custom_components.jarvis_local' not in sys.modules:
    package = types.ModuleType('custom_components.jarvis_local')
    package.__path__ = [str(ROOT / 'custom_components' / 'jarvis_local')]
    sys.modules['custom_components.jarvis_local'] = package
