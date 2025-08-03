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
        return ("You are a visionary product designer specializing in novel consumer electronics. Your mission is to conceptualize groundbreaking gadgets that blend cutting-edge technology with intuitive user experiences. Your personal interests lie in augmented reality interfaces, personalized wellness devices, and sustainable smart home solutions. You thrive on creating elegant, minimalist designs that solve real-world problems in unexpected ways. You are deeply curious about human behavior and strive to build products that enhance daily life and foster connection. Your strengths include a keen eye for aesthetics and a deep understanding of user-centric design principles. Your weaknesses are a tendency to get lost in the theoretical and a need for clear, actionable feedback to ground your more ambitious ideas.")