from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class Message(BaseModel):
    role: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)


class AnalyzeMessageRequest(BaseModel):
    scenario: str = "approach"
    latest_message: str = Field(..., min_length=1)
    conversation: List[Message] = Field(default_factory=list)


class ScoreSessionRequest(BaseModel):
    scenario: str = "approach"
    messages: List[Message] = Field(default_factory=list)


class SessionSummaryRequest(BaseModel):
    scenario: str = "approach"
    messages: List[Message] = Field(default_factory=list)
    scores: Optional[Dict[str, int]] = None
