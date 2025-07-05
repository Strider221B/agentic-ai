import asyncio
from dotenv import load_dotenv
from typing import Dict, List

from agents import Agent, RunResult, WebSearchTool, Runner
from agents.model_settings import ModelSettings

from common.open_ai_gemini_client import OpenAIGeminiClient
from common.tools.send_grid_email import SendGridEmail
from open_ai_02.output_types.report_data import ReportData
from open_ai_02.output_types.web_search_item import WebSearchItem
from open_ai_02.output_types.web_search_plan import WebSearchPlan

load_dotenv(override=True)

class DeepResearch:

    _HOW_MANY_SEARCHES = 3

    @classmethod
    def run_search_and_print(cls, search_term: str):
        result = asyncio.run(cls._run_search_agent(search_term))
        print(result)

    @classmethod
    def run_planner_and_print(cls, search_term: str):
        result = asyncio.run(cls._get_planner_output_for(search_term))
        print(result)

    @classmethod
    def run_and_print_end_to_end_research(cls, search_term: str):
        result = cls._run_end_to_end_research(search_term)
        print(result)

    @classmethod
    async def _run_end_to_end_research(cls, query: str) -> RunResult:
        print("Starting research...")
        search_plan = await cls._plan_searches(query)
        search_results = await cls._perform_searches(search_plan)
        report = await cls._write_report(query, search_results)
        final_output = await cls._send_email(report)
        print("Hooray!")
        return final_output

    @classmethod
    async def _get_planner_output_for(cls, search_term: str):
        return await Runner.run(cls._get_planner_agent(), search_term)

    @classmethod
    async def _run_search_agent(cls, search_term: str):
        return await Runner.run(cls._get_seach_agent(), search_term)

    @classmethod
    async def _plan_searches(cls, query: str) -> WebSearchPlan:
        """ Use the planner_agent to plan which searches to run for the query """
        print("Planning searches...")
        result = await Runner.run(cls._get_planner_agent(), f"Query: {query}")
        print(f"Will perform {len(result.final_output.searches)} searches")
        return result.final_output

    @classmethod
    async def _perform_searches(cls, search_plan: WebSearchPlan) -> List[str]:
        """ Call search() for each item in the search plan """
        print("Searching...")
        tasks = [asyncio.create_task(cls._search(item)) for item in search_plan.searches]
        results = await asyncio.gather(*tasks)
        print("Finished searching")
        return results

    @classmethod
    async def _search(cls, item: WebSearchItem) -> str:
        """ Use the search agent to run a web search for each item in the search plan """
        input = f"Search term: {item.query}\nReason for searching: {item.reason}"
        result = await Runner.run(cls._get_seach_agent(), input)
        return result.final_output

    @classmethod
    async def _write_report(cls, query: str, search_results: List[str]) -> ReportData:
        """ Use the writer agent to write a report based on the search results"""
        print("Thinking about report...")
        input = f"Original query: {query}\nSummarized search results: {search_results}"
        result = await Runner.run(cls._get_writer_agent(), input)
        print("Finished writing report")
        return result.final_output

    async def _send_email(cls, report: ReportData) -> RunResult:
        """ Use the email agent to send an email with the report """
        print("Writing email...")
        result = await Runner.run(cls._get_email_agent(), report.markdown_report)
        print("Email sent")
        return result

    @classmethod
    def _get_writer_agent(cls) -> Agent:
        return Agent(name="WriterAgent",
                     instructions=cls._get_writer_agent_instructions(),
                     model=OpenAIGeminiClient.get_model(),
                     output_type=ReportData)

    @classmethod
    def _get_email_agent(cls) -> Agent:
        return Agent(name="Email agent",
                     instructions=cls._get_email_agent_instructions(),
                     tools=[SendGridEmail.send_email_tool_html],
                     model=OpenAIGeminiClient.get_model())

    @classmethod
    def _get_planner_agent(cls) -> Agent:
        return Agent(name="PlannerAgent",
                     instructions=cls._get_planner_agent_instructions(),
                     model=OpenAIGeminiClient.get_model(),
                     output_type=WebSearchPlan)

    @classmethod
    def _get_seach_agent(cls) -> Agent:
        # Web search tool is open ai hosted and therefore won't work unless you are using open ai model.
        return Agent(name="Search agent",
                     instructions=cls._get_search_agent_instructions(),
                     tools=[WebSearchTool(search_context_size="low")],
                     model=OpenAIGeminiClient.get_model(),
                     model_settings=ModelSettings(tool_choice="required")) # tool_choice="required" means the agent must use the tool.

    @staticmethod
    def _get_search_agent_instructions() -> str:
        return ("You are a research assistant. Given a search term, you search the web for that term and "
                "produce a concise summary of the results. The summary must 2-3 paragraphs and less than 300 "
                "words. Capture the main points. Write succintly, no need to have complete sentences or good "
                "grammar. This will be consumed by someone synthesizing a report, so it's vital you capture the "
                "essence and ignore any fluff. Do not include any additional commentary other than the summary itself.")

    @classmethod
    def _get_planner_agent_instructions(cls) -> str:
        return (f"You are a helpful research assistant. Given a query, come up with a set of web searches "
                f"to perform to best answer the query. Output {cls._HOW_MANY_SEARCHES} terms to query for.")

    @staticmethod
    def _get_email_agent_instructions() -> str:
        return ("You are able to send a nicely formatted HTML email based on a detailed report. "
                "You will be provided with a detailed report. You should use your tool to send one email, providing the "
                "report converted into clean, well presented HTML with an appropriate subject line.")

    @staticmethod
    def _get_writer_agent_instructions() -> str:
        return ("You are a senior researcher tasked with writing a cohesive report for a research query. "
                "You will be provided with the original query, and some initial research done by a research assistant.\n"
                "You should first come up with an outline for the report that describes the structure and "
                "flow of the report. Then, generate the report and return that as your final output.\n"
                "The final output should be in markdown format, and it should be lengthy and detailed. Aim "
                "for 5-10 pages of content, at least 1000 words.")

if __name__ == '__main__':
    # DeepResearch.run_search_and_print("Latest AI Agent frameworks in 2025")
    DeepResearch.run_planner_and_print("Latest AI Agent frameworks in 2025")

#Output:
# DeepResearch.run_search_and_print("Latest AI Agent frameworks in 2025") -->
# Throws an error because we are trying to use non open ai model with open ai hosted tool.
# Traceback (most recent call last):
#   File "/home/somesh/Git/agentic-ai/open_ai_02/deep_research_03.py", line 44, in <module>
#     DeepResearch.run_search_and_print("Latest AI Agent frameworks in 2025")
#   File "/home/somesh/Git/agentic-ai/open_ai_02/deep_research_03.py", line 20, in run_search_and_print
#     result = asyncio.run(cls._run_search_agent(search_term))
#              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/lib/python3.12/asyncio/runners.py", line 194, in run
#     return runner.run(main)
#            ^^^^^^^^^^^^^^^^
#   File "/usr/lib/python3.12/asyncio/runners.py", line 118, in run
#     return self._loop.run_until_complete(task)
#            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/lib/python3.12/asyncio/base_events.py", line 687, in run_until_complete
#     return future.result()
#            ^^^^^^^^^^^^^^^
#   File "/home/somesh/Git/agentic-ai/open_ai_02/deep_research_03.py", line 25, in _run_search_agent
#     return await Runner.run(cls._get_seach_agent(), search_term)
#            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/home/somesh/PythonEnvs/P3.12_LLM/lib/python3.12/site-packages/agents/run.py", line 218, in run
#     input_guardrail_results, turn_result = await asyncio.gather(
#                                            ^^^^^^^^^^^^^^^^^^^^^
#   File "/home/somesh/PythonEnvs/P3.12_LLM/lib/python3.12/site-packages/agents/run.py", line 760, in _run_single_turn
#     new_response = await cls._get_new_response(
#                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/home/somesh/PythonEnvs/P3.12_LLM/lib/python3.12/site-packages/agents/run.py", line 919, in _get_new_response
#     new_response = await model.get_response(
#                    ^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/home/somesh/PythonEnvs/P3.12_LLM/lib/python3.12/site-packages/agents/models/openai_chatcompletions.py", line 61, in get_response
#     response = await self._fetch_response(
#                ^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/home/somesh/PythonEnvs/P3.12_LLM/lib/python3.12/site-packages/agents/models/openai_chatcompletions.py", line 216, in _fetch_response
#     converted_tools = [Converter.tool_to_openai(tool) for tool in tools] if tools else []
#                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/home/somesh/PythonEnvs/P3.12_LLM/lib/python3.12/site-packages/agents/models/chatcmpl_converter.py", line 452, in tool_to_openai
#     raise UserError(
# agents.exceptions.UserError: Hosted tools are not supported with the ChatCompletions API. Got tool type: <class 'agents.tool.WebSearchTool'>, tool: WebSearchTool(user_location=None, search_context_size='low')
# OPENAI_API_KEY is not set, skipping trace export

# DeepResearch.run_planner_and_print("Latest AI Agent frameworks in 2025") -->
# RunResult:
# - Last agent: Agent(name="PlannerAgent", ...)
# - Final output (WebSearchPlan):
#     {
#       "searches": [
#         {
#           "reason": "This search aims to find forward-looking articles and analyses that discuss anticipated AI agent frameworks for the upcoming year.",
#           "query": "AI agent frameworks 2025 predictions"
#         },
#         {
#           "reason": "This query focuses on identifying new tools and platforms that are likely to be important for building AI agents in 2025.",
#           "query": "emerging AI agent development tools 2025"
#         },
#         {
#           "reason": "This search targets research papers and industry reports that highlight the latest advancements and future directions in AI agent technology.",
#           "query": "trends in autonomous AI agent research 2025"
#         }
#       ]
#     }
# - 1 new item(s)
# - 1 raw response(s)
# - 0 input guardrail result(s)
# - 0 output guardrail result(s)
# (See `RunResult` for more details)