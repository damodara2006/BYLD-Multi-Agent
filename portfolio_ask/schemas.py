from typing import List
from pydantic import BaseModel, Field

class GeneralQA(BaseModel):
    """Schema for general queries regarding portfolio and financial terms."""
    query_type: str = Field(description="The type of the query (e.g., 'portfolio', 'general')")
    summary: str = Field(description="The final answer to the user's query.")
    ranked_items: list[dict[str, object]] = Field(default_factory=list, description="Ranked holdings data when available.")
    sources: List[str] = Field(description="List of source files or items used.")
    trace: List[str] = Field(description="Internal reasoning steps indicating how the answer was reached.")

class NewsImpactItem(BaseModel):
    """Detailed rationale and weight for a specific ticker's exposure to news."""
    ticker: str
    rationale: str
    exposure_weight: float
    risk_level: str = Field(description="The risk category: Low, Medium, or High")

class NewsImpact(BaseModel):
    """Schema for assessing the impact of news on the user's portfolio."""
    query_type: str = Field(description="The type of the query, usually 'news_impact'")
    summary: str = Field(description="A brief summary of the news and its overall impact.")
    ranked_items: List[NewsImpactItem] = Field(description="List of impacted assets ranked by relevance/weight.")
    sources: List[str] = Field(description="List of source files used.")
    trace: List[str] = Field(description="Internal reasoning steps indicating how the answer was reached.")
