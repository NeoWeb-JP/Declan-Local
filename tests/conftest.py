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
if 'custom_components.declan_local' not in sys.modules:
    package = types.ModuleType('custom_components.declan_local')
    package.__path__ = [str(ROOT / 'custom_components' / 'declan_local')]
    sys.modules['custom_components.declan_local'] = package

# Pure unit tests run without Home Assistant installed. Provide only the import
# surface needed by music_blacklist; integration behaviour is tested in HA.
if 'homeassistant.core' not in sys.modules:
    ha = sys.modules.setdefault('homeassistant', types.ModuleType('homeassistant'))
    ha.__path__ = []
    core = types.ModuleType('homeassistant.core')
    core.callback = lambda fn: fn
    sys.modules['homeassistant.core'] = core
    helpers = sys.modules.setdefault('homeassistant.helpers', types.ModuleType('homeassistant.helpers'))
    helpers.__path__ = []
    event = types.ModuleType('homeassistant.helpers.event')
    event.async_track_state_change_event = lambda *args, **kwargs: None
    sys.modules['homeassistant.helpers.event'] = event
    storage = types.ModuleType('homeassistant.helpers.storage')
    class Store:
        def __init__(self, *args, **kwargs):
            raise RuntimeError('Home Assistant storage requires the HA test harness')
    storage.Store = Store
    sys.modules['homeassistant.helpers.storage'] = storage
