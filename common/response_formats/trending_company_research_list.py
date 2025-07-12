from typing import List
from pydantic import BaseModel, Field

from common.response_formats.trending_company_research import TrendingCompanyResearch

class TrendingCompanyResearchList(BaseModel):
    """ A list of detailed research on all the companies """
    research_list: List[TrendingCompanyResearch] = Field(description="Comprehensive research on all trending companies")
