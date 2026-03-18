"""
Analysis schemas
"""
from typing import List
from pydantic import BaseModel


class GenerateScriptRequest(BaseModel):
    """Request model for script generation"""
    pain_points: List[str]
    selling_points: List[str]
    concerns: List[str]
    use_cases: List[str]


class GenerateScriptResponse(BaseModel):
    """Response model for script generation"""
    opening_hook: str
    pain_point: str
    solution: str
    proof: str
    offer: str
