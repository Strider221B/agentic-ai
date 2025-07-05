from pydantic import BaseModel, Field

from open_ai_02.output_types.web_search_item import WebSearchItem

class WebSearchPlan(BaseModel):
    searches: list[WebSearchItem] = Field(description="A list of web searches to perform to best answer the query.")