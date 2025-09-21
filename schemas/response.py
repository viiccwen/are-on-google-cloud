from typing import Optional
from pydantic import BaseModel, Field


class UserResponse(BaseModel):
    """User response model"""

    message: str = Field(..., description="Response message for user")
    success: bool = Field(default=True, description="Whether the operation was successful")


class FunctionCallResponse(UserResponse):
    """Function call response"""

    pass


class RAGResponse(UserResponse):
    """RAG query response"""

    documents_count: Optional[int] = Field(None, description="Number of documents found")
