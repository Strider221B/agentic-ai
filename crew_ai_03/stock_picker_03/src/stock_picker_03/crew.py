import os
from typing import List

from crewai import Agent, Crew, Process, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.memory import LongTermMemory, ShortTermMemory, EntityMemory
from crewai.memory.storage.rag_storage import RAGStorage
from crewai.memory.storage.ltm_sqlite_storage import LTMSQLiteStorage
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool

from common.constants import Constants
from common.response_formats.trending_company_list import TrendingCompanyList
from common.response_formats.trending_company_research_list import TrendingCompanyResearchList
from tools.push_notification_tool import PushNotificationTool

@CrewBase
class StockPicker03():
    """StockPicker03 crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    @agent
    def trending_company_finder(self) -> Agent:
        return Agent(config=self.agents_config['trending_company_finder'], tools=[SerperDevTool()], memory=True)

    @agent
    def financial_researcher(self) -> Agent:
        return Agent(config=self.agents_config['financial_researcher'], tools=[SerperDevTool()])


    @agent
    def stock_picker(self) -> Agent:
        return Agent(config=self.agents_config['stock_picker'], tools=[PushNotificationTool()], memory=True)

    @task
    def find_trending_companies(self) -> Task:
        return Task(config=self.tasks_config['find_trending_companies'], output_pydantic=TrendingCompanyList)

    @task
    def research_trending_companies(self) -> Task:
        return Task(config=self.tasks_config['research_trending_companies'], output_pydantic=TrendingCompanyResearchList)

    @task
    def pick_best_company(self) -> Task:
        return Task(config=self.tasks_config['pick_best_company'])

    @crew
    def crew(self) -> Crew:
        """Creates the StockPicker crew"""

        manager = Agent(
            config=self.agents_config['manager'],
            allow_delegation=True
        )

        embedder_config = {"provider": "google",
                           "config": {"model": "models/gemini-embedding-001",
                                      "api_key": os.getenv(Constants.GOOGLE_API_KEY) }}

        return Crew(agents=self.agents,
                    tasks=self.tasks,
                    process=Process.hierarchical,
                    verbose=True,
                    manager_agent=manager,
                    memory=True,
                    long_term_memory=LongTermMemory(storage=LTMSQLiteStorage('./memory/long_term_memory_storage.db')),
                    short_term_memory=ShortTermMemory(storage=RAGStorage(type='short_term', path='./memory', embedder_config=embedder_config)),
                    entity_memory=EntityMemory(storage=RAGStorage(type='short_term', path='./memory', embedder_config=embedder_config)),
                    embedder=embedder_config)
