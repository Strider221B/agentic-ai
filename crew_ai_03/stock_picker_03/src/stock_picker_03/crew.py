from typing import List

from crewai import Agent, Crew, Process, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool

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
        return Agent(config=self.agents_config['trending_company_finder'], tools=[SerperDevTool()])

    @agent
    def financial_researcher(self) -> Agent:
        return Agent(config=self.agents_config['financial_researcher'], tools=[SerperDevTool()])


    @agent
    def stock_picker(self) -> Agent:
        return Agent(config=self.agents_config['stock_picker'], tools=[PushNotificationTool()])

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

        return Crew(agents=self.agents,
                    tasks=self.tasks,
                    process=Process.hierarchical,
                    verbose=True,
                    manager_agent=manager)
