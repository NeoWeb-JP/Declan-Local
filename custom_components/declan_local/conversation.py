"""Conversation platform for the configured Home Voice Assistant integration."""
from .agent import JarvisAgent
async def async_setup_entry(hass, entry, async_add_entities):
    agent = JarvisAgent(hass)
    hass.data["declan_local"]["agent"] = agent
    async_add_entities([agent])
