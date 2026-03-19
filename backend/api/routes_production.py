"""
Production API routes
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

from backend.services.production_service import ProductionService

router = APIRouter()

production_service = ProductionService()


class GenerateScriptFromCommentsRequest(BaseModel):
    """Request model for generating script from comments"""
    comments: List[str]


class GenerateScriptResponse(BaseModel):
    """Response model for script generation"""
    opening_hook: str
    pain_point: str
    solution: str
    proof: str
    offer: str


class ScriptWithStyle(BaseModel):
    """Script with style field"""
    style: str
    opening_hook: str
    pain_point: str
    solution: str
    proof: str
    offer: str


class GenerateMultiStyleScriptsResponse(BaseModel):
    """Response model for multi-style script generation"""
    scripts: List[ScriptWithStyle]


@router.post("/generate-script-from-comments", response_model=GenerateScriptResponse)
def generate_script_from_comments(request: GenerateScriptFromCommentsRequest):
    """
    Generate script from comments - combines analysis and script generation
    """
    comments = request.comments

    if not comments:
        raise HTTPException(status_code=400, detail="Comments list cannot be empty")

    try:
        result = production_service.generate_script_from_comments(comments)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return GenerateScriptResponse(**result)


@router.post("/generate-multi-style-scripts-from-comments", response_model=GenerateMultiStyleScriptsResponse)
def generate_multi_style_scripts_from_comments(request: GenerateScriptFromCommentsRequest):
    """
    Generate scripts in three different styles from comments
    """
    comments = request.comments

    if not comments:
        raise HTTPException(status_code=400, detail="Comments list cannot be empty")

    try:
        result = production_service.generate_multi_style_scripts_from_comments(comments)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return GenerateMultiStyleScriptsResponse(**result)
