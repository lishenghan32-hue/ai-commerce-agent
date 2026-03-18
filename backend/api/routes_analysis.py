"""
Analysis API routes
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.services.ai_service import AIService
from backend.schemas.analysis import GenerateScriptRequest, GenerateScriptResponse

router = APIRouter()

ai_service = AIService()


class AnalyzeCommentsRequest(BaseModel):
    """Request model for comment analysis"""
    comments: list[str]


class AnalyzeCommentsResponse(BaseModel):
    """Response model for comment analysis"""
    pain_points: list[str]
    selling_points: list[str]
    concerns: list[str]
    use_cases: list[str]


@router.post("/analyze-comments", response_model=AnalyzeCommentsResponse)
async def analyze_comments(request: AnalyzeCommentsRequest):
    """
    Analyze comments to extract user insights
    """
    comments = request.comments

    if not comments:
        raise HTTPException(status_code=400, detail="Comments list cannot be empty")

    try:
        result = ai_service.analyze_comments(comments)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")

    return AnalyzeCommentsResponse(**result)


@router.post("/generate-script", response_model=GenerateScriptResponse)
def generate_script(request: GenerateScriptRequest):
    """
    Generate live streaming script based on insights
    """
    try:
        insights = {
            "pain_points": request.pain_points,
            "selling_points": request.selling_points,
            "concerns": request.concerns,
            "use_cases": request.use_cases
        }
        result = ai_service.generate_script(insights)
        return GenerateScriptResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
