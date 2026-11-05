"""Home Voice Assistant integration and authenticated sidebar chat."""
from pathlib import Path
from urllib.parse import quote
from .version import read_version
from homeassistant.components import frontend, panel_custom
from homeassistant.components.http import StaticPathConfig
from homeassistant.helpers import config_validation as cv
DOMAIN = "jarvis_local"
CONFIG_SCHEMA = cv.empty_config_schema(DOMAIN)

async def async_setup(hass, config):
    if DOMAIN in config:
        hass.async_create_task(hass.config_entries.flow.async_init(
            DOMAIN, context={"source":"import"}, data={}))
    return True

async def async_setup_entry(hass, entry):
    data = hass.data.setdefault(DOMAIN, {})
    data["version"] = await hass.async_add_executor_job(read_version)
    from .media_search_config import load as load_media_search
    data["media_search_config"] = await load_media_search(hass)
    from .settings import load
    data["settings"] = await load(hass)
    from homeassistant.helpers.storage import Store
    debug_settings = await Store(hass, 1, "jarvis_local.debug").async_load()
    data["debug_enabled"] = isinstance(debug_settings, dict) and debug_settings.get("enabled") is True
    data["diagnostics"] = []
    learning_state = await Store(hass, 1, "jarvis_local.learning_aliases").async_load()
    learning_state = learning_state if isinstance(learning_state, dict) else {}
    data["approved_aliases"] = {k:v for k,v in learning_state.get("approved", {}).items() if isinstance(k,str) and isinstance(v,str)} if isinstance(learning_state.get("approved", {}),dict) else {}
    data["rejected_aliases"] = learning_state.get("rejected", []) if isinstance(learning_state.get("rejected", []),list) else []
    from .learning import load_evidence
    await load_evidence(hass)
    import json
    def load_voice_config():
        path=Path(hass.config.path('jarvis_voice_id.json'))
        if not path.exists():return {}
        with path.open(encoding='utf-8') as f:return json.load(f)
    try:
        voice_config=await hass.async_add_executor_job(load_voice_config)
        data['voice_id_config']=voice_config if isinstance(voice_config,dict) else {}
    except (OSError,ValueError):
        data['voice_id_config']={}

    from .timers import Timers
    data["timers"] = Timers(hass)
    await data["timers"].start()
    if not data.get('ws_registered'):
        from .websocket import register
        register(hass)
        data['ws_registered']=True
    await hass.config_entries.async_forward_entry_setups(entry, ["conversation", "tts", "stt"])
    if not data.get("static_registered"):
        await hass.http.async_register_static_paths([
            StaticPathConfig("/jarvis_local/panel.js", str(Path(__file__).parent / "panel.js"), False),
            StaticPathConfig("/jarvis_local/logo.png", str(Path(__file__).parent / "logo.png"), False)
        ])
        data["static_registered"] = True
    try:
        await panel_custom.async_register_panel(
            hass, frontend_url_path="jarvis-local-app", webcomponent_name="jarvis-local-panel",
            sidebar_title="Home Voice Assistant", sidebar_icon="mdi:robot",
            module_url="/jarvis_local/panel.js?v=" + quote(data["version"], safe=""),
            config={"agent_id":data["agent"].entity_id}, require_admin=True)
        from .guest_authority import create as create_guest_authority
        data['guest_authority'] = await create_guest_authority(hass)
    except Exception:
        if data.get('guest_authority'):
            await data['guest_authority'].stop()
        frontend.async_remove_panel(hass, "jarvis-local-app")
        await data["timers"].stop()
        await hass.config_entries.async_unload_platforms(entry, ["conversation", "tts", "stt"])
        raise
    return True

async def async_unload_entry(hass, entry):
    from .learning import flush_evidence
    await flush_evidence(hass)
    if await hass.config_entries.async_unload_platforms(entry, ["conversation", "tts", "stt"]):
        await hass.data[DOMAIN]['guest_authority'].stop()
        hass.data[DOMAIN].pop('guest_authority', None)
        await hass.data[DOMAIN]["timers"].stop()
        frontend.async_remove_panel(hass, "jarvis-local-app")
        hass.data[DOMAIN].pop("agent", None)
        hass.data[DOMAIN].pop("voice_manager", None)
        hass.data[DOMAIN].pop("diagnostics", None)
        return True
    return False
