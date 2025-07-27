from typing import List, Tuple

from langchain.agents import Tool
from langchain_community.agent_toolkits import FileManagementToolkit, PlayWrightBrowserToolkit
from langchain_community.tools.wikipedia.tool import WikipediaQueryRun
from langchain_community.utilities.wikipedia import WikipediaAPIWrapper
from langchain_core.tools import BaseTool
from langchain_experimental.tools import PythonREPLTool
from playwright.async_api import async_playwright, Browser, Playwright

from common.tools.pushover import Pushover
from common.tools.serper import Serper

class SidekickTools:

    @staticmethod
    async def playwright_tools() -> Tuple[List[BaseTool], Browser, Playwright]:
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=False)
        toolkit = PlayWrightBrowserToolkit.from_browser(async_browser=browser)
        return toolkit.get_tools(), browser, playwright

    @classmethod
    async def other_tools(cls):
        push_tool = Tool(name="send_push_notification", func=cls._push, description="Use this tool when you want to send a push notification")
        file_tools = cls._get_file_tools()

        tool_search =Tool(
            name="search",
            func=Serper.run,
            description="Use this tool when you want to get the results of an online web search"
        )

        wikipedia = WikipediaAPIWrapper()
        wiki_tool = WikipediaQueryRun(api_wrapper=wikipedia)

        python_repl = PythonREPLTool()

        return file_tools + [push_tool, tool_search, python_repl,  wiki_tool]

    @staticmethod
    def _push(text: str):
        """Send a push notification to the user"""
        Pushover.push(text)
        return "success"

    @staticmethod
    def _get_file_tools():
        toolkit = FileManagementToolkit(root_dir="sandbox")
        return toolkit.get_tools()
