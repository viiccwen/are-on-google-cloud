from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Error response model"""

    success: bool = Field(default=False, description="Whether the operation was successful")
    error: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Error details")


class HealthResponse(BaseModel):
    """Health check response model"""

    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    timestamp: str = Field(..., description="Check time")
    services: Dict[str, str] = Field(..., description="Status of each service")


class SuccessResponse(BaseModel):
    """Success response model"""

    success: bool = Field(default=True, description="Whether the operation was successful")
    message: str = Field(..., description="Success message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")
