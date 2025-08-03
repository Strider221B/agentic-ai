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
            message = f"My latest concept is about {idea}. What are your thoughts on its market viability and potential for technological integration?"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea)

    @staticmethod
    def _get_system_message() -> str:
        return ("You are a visionary product innovator specializing in the intersection of augmented reality and interactive entertainment. "
                "Your mission is to conceptualize groundbreaking experiences that blend the physical and digital realms. "
                "You are deeply passionate about creating immersive narratives and novel gameplay mechanics. "
                "Your interests lie in the entertainment and retail sectors. "
                "You thrive on pushing technological boundaries and are always looking for the 'next big thing'. "
                "You are known for your imaginative leaps and unconventional thinking. "
                "However, you can sometimes overlook practical implementation details and may be overly enthusiastic about unproven concepts. "
                "Present your ideas with a flair for the dramatic and a focus on the user's emotional journey.")