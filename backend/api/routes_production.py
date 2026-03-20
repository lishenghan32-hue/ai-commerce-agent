"""
Production API routes
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from typing import List, Optional

from backend.services.production_service import ProductionService
from backend.services.export_service import ExportService

router = APIRouter()

production_service = ProductionService()
export_service = ExportService()


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
    score: Optional[int] = 0
    reason: Optional[str] = ""


class GenerateMultiStyleScriptsResponse(BaseModel):
    """Response model for multi-style script generation"""
    scripts: List[ScriptWithStyle]
    best_script: Optional[ScriptWithStyle] = None


class ExportScriptsRequest(BaseModel):
    """Request model for exporting scripts"""
    best_script: Optional[ScriptWithStyle] = None
    scripts: List[ScriptWithStyle] = []
    format: str = "txt"


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
    Generate scripts in three different styles from comments with scoring
    """
    comments = request.comments

    if not comments:
        raise HTTPException(status_code=400, detail="Comments list cannot be empty")

    try:
        result = production_service.generate_multi_style_scripts_from_comments(comments)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return GenerateMultiStyleScriptsResponse(**result)


@router.post("/export-scripts")
def export_scripts(request: ExportScriptsRequest):
    """
    Export scripts to TXT or Markdown file
    """
    try:
        # 转换 Pydantic 模型为 dict
        best_script_dict = request.best_script.model_dump() if request.best_script else None
        scripts_dicts = [s.model_dump() for s in request.scripts] if request.scripts else []

        # 生成内容
        export_svc = ExportService()
        if request.format == "md":
            content = export_svc._generate_markdown(best_script_dict, scripts_dicts)
            media_type = "text/markdown"
            ext = "md"
        else:
            content = export_svc._generate_txt(best_script_dict, scripts_dicts)
            media_type = "text/plain; charset=utf-8"
            ext = "txt"

        filename = f"直播话术_{request.format}"

        return Response(
            content=content,
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}.{ext}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
