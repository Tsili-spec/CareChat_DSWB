"""
Chat-related Pydantic schemas
"""
from pydantic import BaseModel, Field
from typing import Optional

class ChatRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=5000, description="The user's message/prompt")
    temperature: Optional[float] = Field(0.7, ge=0.0, le=2.0, description="Controls randomness in response")
    max_tokens: Optional[int] = Field(1000, ge=1, le=4000, description="Maximum tokens in response")
    top_p: Optional[float] = Field(None, ge=0.0, le=1.0, description="Nucleus sampling parameter")
    model: Optional[str] = Field(None, description="Specific model to use (provider-dependent)")

class ChatResponse(BaseModel):
    response: str = Field(..., description="The AI-generated response")
    provider: str = Field(..., description="The LLM provider used")
    model: Optional[str] = Field(None, description="The specific model used")
    
class ChatHealthCheck(BaseModel):
    status: str
    provider: str
    configured: bool
    message: str
