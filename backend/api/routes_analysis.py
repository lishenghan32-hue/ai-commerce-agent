"""
Analysis API routes
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.services.ai_service import AIService

router = APIRouter()

ai_service = AIService()


class AnalyzeCommentsRequest(BaseModel):
    """Request model for comment analysis"""
    comments: list[str]


class AnalyzeCommentsResponse(BaseModel):
    """Response model for comment analysis"""
    pain_points: list[str]
    selling_points: list[str]
    script: str


@router.post("/analyze-comments", response_model=AnalyzeCommentsResponse)
async def analyze_comments(request: AnalyzeCommentsRequest):
    """
    Analyze comments to extract insights and generate marketing script
    """
    comments = request.comments

    if not comments:
        raise HTTPException(status_code=400, detail="Comments list cannot be empty")

    try:
        result = ai_service.analyze_comments(comments)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")

    return AnalyzeCommentsResponse(**result)
