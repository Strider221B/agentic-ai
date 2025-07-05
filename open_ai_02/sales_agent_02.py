from dotenv import load_dotenv
from agents import Agent, Runner, Tool, trace, function_tool
from openai.types.responses import ResponseTextDeltaEvent
from typing import Dict, List
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
        self._sales_picker = Agent(name='Sales Picker',
                                   instructions=self._get_sales_picker_instructions(),
                                   model=OpenAIGeminiClient.get_model())

    def print_best_email_from_all_agent(self, message: str):
        print(asyncio.run(self._select_best_email_for(message)))

    def print_sample_email_for_all_agents(self, message: str):
        # Note!! You can only have one asyncio run in your class.
        results = asyncio.run(self._generate_email_using_all_agents(message))
        for result in results:
            print(result + "\n\n")

    def send_email_as_tools(self):
        result = asyncio.run(self._send_email_as_tools_async())
        print(result)

    async def _send_email_as_tools_async(self):
        tools = self._get_agents_and_email_tools()
        sales_manager = Agent(name="Sales Manager",
                              instructions=self._get_send_email_instructions_using_tool(),
                              tools=tools,
                              model=OpenAIGeminiClient.get_model())
        message = "Send a cold sales email addressed to 'Dear CEO'"
        result = await Runner.run(sales_manager, message)
        return result

    def _get_agents_and_email_tools(self) -> List[Tool]:
        description = "Write a cold sales email"
        tool1 = self._prof_agent.as_tool(tool_name="sales_agent1", tool_description=description)
        tool2 = self._witty_agent.as_tool(tool_name="sales_agent2", tool_description=description)
        tool3 = self._concise_agent.as_tool(tool_name="sales_agent3", tool_description=description)
        return [tool1, tool2, tool3, SendGridEmail.send_email_tool]

    async def _select_best_email_for(self, message: str):
        all_emails = await self._generate_email_using_all_agents(message)
        emails = "Cold sales emails:\n\n".join(all_emails)
        best = await Runner.run(self._sales_picker, emails)
        return best.final_output

    async def _generate_email_using_all_agents(self, message: str):
        results = await asyncio.gather(Runner.run(self._prof_agent, message),
                                       Runner.run(self._witty_agent, message),
                                       Runner.run(self._concise_agent, message))
        results = [result.final_output for result in results]
        return results

    @staticmethod
    def _get_send_email_instructions_using_tool():
        return ("You are a sales manager working for ComplAI. You use the tools given to you to generate cold sales emails. "
                "You never generate sales emails yourself; you always use the tools. "
                "You try all 3 sales_agent tools once before choosing the best one. "
                "Do not worry on the exact content of the emails, the sales_agent tools already have the instructions to draft the email. "
                "Just ask the sales_agent tools to come up with the email. "
                "You pick the single best email and use the send_email tool to send the best email (and only the best email) to the user.")

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

    @staticmethod
    def _get_sales_picker_instructions() -> str:
        return ("You pick the best cold sales email from the given options. Imagine you are a "
                "customer and pick the one you are most likely to respond to. Do not give "
                "an explanation; reply with the selected email only.")

if __name__ == '__main__':
    sales_agent = SalesAgent()
    # sales_agent.print_sample_email_for_all_agents("Write a cold sales email")
    # sales_agent.print_best_email_from_all_agent("Write a cold sales email")
    sales_agent.send_email_as_tools()

# Output:
# sales_agent.send_email_as_tools() -->
# OPENAI_API_KEY is not set, skipping trace export
# Email sent to: <email address specified> - Response Code: 202
# RunResult:
# - Last agent: Agent(name="Sales Manager", ...)
# - Final output (str):
#     I have sent the email to the CEO.
# - 9 new item(s)
# - 3 raw response(s)
# - 0 input guardrail result(s)
# - 0 output guardrail result(s)
# (See `RunResult` for more details)
# OPENAI_API_KEY is not set, skipping trace export
