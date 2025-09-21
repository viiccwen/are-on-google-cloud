from typing import List, Dict, Any
from pydantic import BaseModel, Field


class AvailableToolsResponse(BaseModel):
    """Available tools list response model"""

    tools: List[Dict[str, Any]] = Field(..., description="List of available tools")
    total_count: int = Field(..., description="Total number of tools")
