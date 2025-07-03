from dotenv import load_dotenv
from agents import Agent, Runner, trace, function_tool
from openai.types.responses import ResponseTextDeltaEvent
from typing import Dict
import os
import asyncio

from common.constants import Constants
from common.open_ai_gemini_client import OpenAIGeminiClient
from common.tools.send_grid_email import SendGridEmail

class SalesAgent:

    def __init__(self):
        self._prof_agent = Agent(name='Professional Sales Agent',
                                 instructions=self._get_professional_instruction(),
                                 model=OpenAIGeminiClient.get_model())
        self._witty_agent = Agent(name="Engaging Sales Agent",
                                  instructions=self._get_witty_instruction(),
                                  model=OpenAIGeminiClient.get_model())

        self._concise_agent = Agent(name="Busy Sales Agent",
                                    instructions=self._get_concise_instruction(),
                                    model=OpenAIGeminiClient.get_model())

    @staticmethod
    def _get_professional_instruction() -> str:
        return ("You are a sales agent working for ComplAI, a company that provides "
                "a SaaS tool for ensuring SOC2 compliance and preparing for audits, powered by AI. "
                "You write professional, serious cold emails.")

    @staticmethod
    def _get_witty_instruction() -> str:
        return ("You are a humorous, engaging sales agent working for ComplAI, a company that "
                "provides a SaaS tool for ensuring SOC2 compliance and preparing for audits, powered by AI. "
                "You write witty, engaging cold emails that are likely to get a response.")

    @staticmethod
    def _get_concise_instruction() -> str:
        return ("You are a busy sales agent working for ComplAI, a company that provides a SaaS tool "
                "for ensuring SOC2 compliance and preparing for audits, powered by AI. "
                "You write concise, to the point cold emails.")
