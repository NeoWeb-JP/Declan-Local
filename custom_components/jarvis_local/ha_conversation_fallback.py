"""Safely delegate genuinely unmatched Declan requests to Home Assistant.

Home Assistant's built-in conversation agent owns registered conversation
triggers (including automations using set_conversation_response). Never route
back into Declan, and never retry an unsuccessful delegation.
"""
import logging

from homeassistant.components import conversation

_LOGGER = logging.getLogger(__name__)
BUILTIN_AGENT = "conversation.home_assistant"


async def delegate_unmatched(hass, user_input, text):
    """Return a successful native HA response or None for Declan to reject.

    Passing the original context/device preserves the listening device and
    the native conversation-trigger response. Do not synthesise an
    acknowledgement: the native response is authoritative.
    """
    try:
        result = await conversation.async_converse(
            hass,
            text,
            user_input.conversation_id,
            user_input.context,
            language=user_input.language,
            agent_id=BUILTIN_AGENT,
            device_id=getattr(user_input, "device_id", None),
        )
    except Exception:
        _LOGGER.exception("Built-in Home Assistant conversation delegation failed")
        return None

    response = getattr(result, "response", None)
    # HA's IntentResponse.response_type is an enum; older/mocked versions
    # may represent it as a string. Only return a confirmed success.
    response_type = getattr(response, "response_type", None)
    if getattr(response_type, "value", response_type) != "action_done":
        _LOGGER.warning("Native HA conversation did not handle automation request (response_type=%s)", response_type)
        return None
    return result
