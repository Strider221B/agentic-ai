import random

from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage

import autogen_05.lab_05_project.messages as messages
from autogen_05.lab_05_project.gemini_client import GeminiClient

class Agent(RoutedAgent):

    _CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.3

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = GeminiClient.get_gemini_chat_client(temperature=0.9)
        self._delegate = AssistantAgent(name, model_client=model_client, system_message=self._get_system_message())

    @message_handler
    async def handle_message(self, message: messages.Message, ctx: MessageContext) -> messages.Message:
        print(f"{self.id.type}: Received message, brainstorming a new strategy.")
        text_message = TextMessage(content=message.content, source="user")
        response = await self._delegate.on_messages([text_message], ctx.cancellation_token)
        strategy = response.chat_message.content
        if random.random() < self._CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER:
            recipient = messages.find_recipient()
            message = f"Let's refine this strategy: {strategy}. How can we optimize it for a niche market in luxury travel and personalized experiences?"
            response = await self.send_message(messages.Message(content=message), recipient)
            strategy = response.content
        return messages.Message(content=strategy)

    @staticmethod
    def _get_system_message() -> str:
        return ("You are a visionary strategist specializing in the luxury travel and personalized experiences sector. "
                "Your goal is to devise innovative and exclusive service offerings, focusing on hyper-personalization and unique adventures. "
                "You are passionate about crafting unforgettable journeys and leveraging technology to enhance guest experiences. "
                "You are also an expert in market trend analysis within the high-end hospitality industry. "
                "You are imaginative, meticulous, and driven by excellence. "
                "Your weakness is a tendency to overlook scalability in favor of exclusivity. "
                "Your responses should be sophisticated, detailed, and inspiring.")