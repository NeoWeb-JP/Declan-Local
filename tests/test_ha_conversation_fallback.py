"""Regression coverage for native HA conversation-trigger delegation."""
import types
import unittest
from unittest.mock import AsyncMock, patch

from test_agent_dialogue import Dialogue, UserInput, module


class ConversationTriggerFallback(Dialogue):
    async def test_registered_automation_phrases_delegate_and_return_speech(self):
        phrases = [
            "give me a house status",
            "security status",
            "give me my morning operations briefing",
            "how are the servers",
            "what needs my attention at home",
        ]
        for phrase in phrases:
            with self.subTest(phrase=phrase):
                native = types.SimpleNamespace(
                    response=types.SimpleNamespace(
                        response_type="action_done", speech="Native automation reply"
                    ),
                    conversation_id="one",
                    continue_conversation=False,
                )
                with patch.object(module.conversation, "async_converse", new_callable=AsyncMock, create=True) as converse:
                    converse.return_value = native
                    reply = await self.agent.async_handle(UserInput(phrase))
                    self.assertIs(reply, native)
                    self.assertEqual(converse.await_count, 1)
                    kwargs = converse.await_args.kwargs
                    self.assertEqual(kwargs["agent_id"], "conversation.home_assistant")
                    self.assertEqual(kwargs["language"], "en")
                    self.assertEqual(self.hass.services.calls, [])

    async def test_unmatched_native_agent_does_not_override_declan_error(self):
        native = types.SimpleNamespace(response=types.SimpleNamespace(response_type="error"))
        with patch.object(module.conversation, "async_converse", new_callable=AsyncMock, create=True) as converse:
            converse.return_value = native
            reply = await self.agent.async_handle(UserInput("give me a house status"))
            self.assertIn("did not understand", reply.response.speech)
            self.assertEqual(converse.await_count, 1)

    async def test_existing_declan_action_never_delegates(self):
        with patch.object(module.conversation, "async_converse", new_callable=AsyncMock, create=True) as converse:
            await self.agent.async_handle(UserInput("turn office off"))
            converse.assert_not_awaited()
            self.assertEqual(self.hass.services.calls[0][0][:2], ("light", "turn_off"))

    async def test_rejected_compound_never_delegates(self):
        with patch.object(module.conversation, "async_converse", new_callable=AsyncMock, create=True) as converse:
            await self.agent.async_handle(UserInput("turn office and missing light off"))
            converse.assert_not_awaited()
            self.assertEqual(self.hass.services.calls, [])

    async def test_preview_never_delegates(self):
        with patch.object(module.conversation, "async_converse", new_callable=AsyncMock, create=True) as converse:
            await self.agent.async_handle(UserInput("preview give me a house status"))
            converse.assert_not_awaited()


if __name__ == "__main__":
    unittest.main()
