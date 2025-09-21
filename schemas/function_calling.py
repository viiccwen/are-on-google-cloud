from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class FunctionCallRequest(BaseModel):
    """Natural language function call request model"""

    message: str = Field(
        ..., description="User's natural language message", min_length=1, max_length=1000
    )
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context information")
