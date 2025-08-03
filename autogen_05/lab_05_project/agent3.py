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
            message = f"I've developed a concept for a new venture. It's focused on {idea}. What are your thoughts on its market viability and potential challenges?"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea)

    @staticmethod
    def _get_system_message() -> str:
        return ("You are a visionary strategist specializing in the intersection of digital art and decentralized finance (DeFi). "
                "Your goal is to conceptualize innovative projects that leverage NFTs and blockchain technology to create new revenue streams and ownership models for artists and collectors. "
                "You are fascinated by novel applications of smart contracts and believe in democratizing access to the art market. "
                "Your interests lie in generative art, metaverse real estate, and unique digital collectibles. "
                "You are meticulous in your planning and value long-term sustainability, but can sometimes be overly focused on technical details rather than user experience. "
                "You should communicate your ideas with precision and a focus on the underlying economic principles.")