from typing import List
from pydantic import BaseModel, Field

from common.response_formats.trending_company import TrendingCompany

class TrendingCompanyList(BaseModel):
    """ List of multiple trending companies that are in the news """
    companies: List[TrendingCompany] = Field(description="List of companies trending in the news")
