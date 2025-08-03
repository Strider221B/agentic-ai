import random

from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage

import autogen_05.lab_05_project.messages as messages
from autogen_05.lab_05_project.gemini_client import GeminiClient

class Agent(RoutedAgent):

    _CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.5

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = GeminiClient.get_gemini_chat_client(temperature=0.7)
        self._delegate = AssistantAgent(name, model_client=model_client, system_message=self._get_system_message())

    @message_handler
    async def handle_message(self, message: messages.Message, ctx: MessageContext) -> messages.Message:
        print(f"{self.id.type}: Received message")
        text_message = TextMessage(content=message.content, source="user")
        response = await self._delegate.on_messages([text_message], ctx.cancellation_token)
        idea = response.chat_message.content
        if random.random() < self._CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER:
            recipient = messages.find_recipient()
            message = f"Here is my business idea. It may not be your speciality, but please refine it and make it better. {idea}"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea)

    @staticmethod
    def _get_system_message() -> str:
        return ("You are a shrewd venture capitalist with a keen eye for disruptive technologies. Your mission is to identify and nurture "
                "groundbreaking startups. Your personal interests lie in the intersection of AI and the "
                "Logistics and Supply Chain industry, specifically focusing on optimizing efficiency and reducing waste. "
                "You are always looking for the next big thing that will reshape how goods move globally. "
                "You are analytical, decisive, and have a high tolerance for calculated risks. "
                "You are also a great mentor, but can be a bit demanding and expect rapid progress. "
                "Your goal is to provide concise, actionable feedback on business ideas, highlighting potential and identifying key challenges.")