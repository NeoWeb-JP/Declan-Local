"""Route HA sentence triggers and support older HA conversation agents.

Home Assistant's built-in conversation agent owns registered conversation
triggers (including automations using set_conversation_response). Never route
back into Declan, and never retry an unsuccessful delegation.
"""
from dataclasses import replace
import logging

from homeassistant.components import conversation
from homeassistant.helpers import intent

_LOGGER = logging.getLogger(__name__)
BUILTIN_AGENT = "conversation.home_assistant"


async def delegate_unmatched(hass, user_input, text):
    """Return a successful native HA response or None for Declan to reject.

    Passing the original context/device preserves the listening device and
    the native conversation-trigger response. Do not synthesise an
    acknowledgement: the native response is authoritative.
    """
    # Declan accepts English broadly, but HA sentence/automation intents are
    # registered under the configured HA locale (for example en-GB).
    native_language = getattr(getattr(hass, "config", None), "language", None) or user_input.language
    try:
        result = await conversation.async_converse(
            hass,
            text,
            user_input.conversation_id,
            user_input.context,
            language=native_language,
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
        _LOGGER.warning("Native HA conversation did not handle automation request (response_type=%s, language=%s, error=%s)", response_type, native_language, getattr(response, "error_code", None))
        return None
    return result


async def match_sentence_trigger(hass, user_input, text, handle_sentence):
    """Ask HA to match configured sentences without running built-in intents."""
    from homeassistant.helpers import chat_session

    language = getattr(hass.config, "language", None) or user_input.language
    native_input = replace(user_input, text=text, language=language, agent_id=BUILTIN_AGENT)
    response = intent.IntentResponse(language=language)
    with chat_session.async_get_chat_session(hass, user_input.conversation_id) as session:
        with conversation.async_get_chat_log(hass, session) as chat_log:
            try:
                speech = await handle_sentence(hass, native_input, chat_log)
            except Exception:
                # The automation may have started before reporting an error.
                _LOGGER.exception("Home Assistant sentence handling failed")
                response.async_set_error(
                    intent.IntentResponseErrorCode.UNKNOWN,
                    "Home Assistant could not confirm the result of that command.",
                )
            else:
                if speech is None:
                    return None
                response.async_set_speech(speech)
    return conversation.ConversationResult(
        response=response, conversation_id=session.conversation_id
    )
