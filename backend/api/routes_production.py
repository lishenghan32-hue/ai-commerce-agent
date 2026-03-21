"""
Production API routes
"""
import os
import json
from urllib.parse import quote
from typing import Generator

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response, StreamingResponse
from pydantic import BaseModel
from typing import List, Optional

from backend.services.production_service import ProductionService
from backend.services.export_service import ExportService

router = APIRouter()

production_service = ProductionService()
export_service = ExportService()


class GenerateScriptFromCommentsRequest(BaseModel):
    """Request model for generating script from comments"""
    product_url: str = ""
    product_name: str = ""
    product_info: str = ""
    selling_points: str = ""
    comments: List[str] = []


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
    try:
        result = production_service.generate_multi_style_scripts_from_comments(
            product_url=request.product_url,
            product_name=request.product_name,
            product_info=request.product_info,
            selling_points=request.selling_points,
            comments=request.comments
        )
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
        file_format = request.format
        if file_format == "md":
            content = export_svc._generate_markdown(best_script_dict, scripts_dicts)
            media_type = "text/markdown"
            ext = "md"
        else:
            content = export_svc._generate_txt(best_script_dict, scripts_dicts)
            media_type = "text/plain; charset=utf-8"
            ext = "txt"

        filename = f"live_script_{file_format}"

        # 使用 RFC 5987 格式支持中文文件名
        encoded_filename = quote(filename)
        content_disposition = f"attachment; filename={filename}.{ext}; filename*=UTF-8''{encoded_filename}.{ext}"

        return Response(
            content=content,
            media_type=media_type,
            headers={"Content-Disposition": content_disposition}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def generate_sse_events(
    product_url: str = "",
    product_name: str = "",
    product_info: str = "",
    selling_points: str = "",
    comments: List[str] = None
) -> Generator[str, None, None]:
    """
    Generate SSE events for script generation with real-time progress
    """
    if comments is None:
        comments = []

    import logging
    logger = logging.getLogger(__name__)

    try:
        # Step 0: Extract info from URL if provided
        yield "event: progress\ndata: {\"step\": 0, \"status\": \"active\", \"message\": \"正在处理输入...\"}\n\n"

        if product_url:
            ai_info = production_service.ai_service.extract_product_info_from_url(product_url)
            logger.info(f"URL提取信息: {ai_info}")

            if not product_name:
                product_name = ai_info.get("product_name", "")

            if not selling_points:
                selling_points = ", ".join(ai_info.get("selling_points", []))

            if not comments or len(comments) < 3:
                ai_comments = ai_info.get("comments", [])
                if ai_comments:
                    comments = list(comments) + ai_comments if comments else ai_comments

        prepared_comments = production_service.prepare_comments(
            product_name=product_name,
            product_info=product_info,
            selling_points=selling_points,
            comments=comments
        )

        logger.info(f"最终商品名: {product_name}")
        logger.info(f"最终卖点: {selling_points}")
        logger.info(f"最终评论: {prepared_comments}")

        if not prepared_comments:
            prepared_comments = production_service.ai_service.generate_comments(product_name, product_info)

        yield "event: progress\ndata: {\"step\": 0, \"status\": \"completed\", \"message\": \"输入处理完成\"}\n\n"

        # Step 1: Analyzing comments
        yield "event: progress\ndata: {\"step\": 1, \"status\": \"active\", \"message\": \"正在分析评论...\"}\n\n"

        insights = production_service.ai_service.analyze_comments(prepared_comments)

        yield "event: progress\ndata: {\"step\": 1, \"status\": \"completed\", \"message\": \"评论分析完成\"}\n\n"

        # Step 2: Generating scripts
        yield "event: progress\ndata: {\"step\": 2, \"status\": \"active\", \"message\": \"正在生成话术...\"}\n\n"

        result = production_service.ai_service.generate_multi_style_scripts(insights)

        yield "event: progress\ndata: {\"step\": 2, \"status\": \"completed\", \"message\": \"话术生成完成\"}\n\n"

        # Step 3: Optimizing and scoring
        yield "event: progress\ndata: {\"step\": 3, \"status\": \"active\", \"message\": \"正在优化话术...\"}\n\n"

        # Final result
        yield "event: progress\ndata: {\"step\": 3, \"status\": \"completed\", \"message\": \"优化完成\"}\n\n"

        # Send final data
        yield f"event: complete\ndata: {json.dumps(result, ensure_ascii=False)}\n\n"

    except Exception as e:
        yield f"event: error\ndata: {json.dumps({'message': str(e)}, ensure_ascii=False)}\n\n"


@router.post("/generate-scripts-sse")
def generate_scripts_sse(request: GenerateScriptFromCommentsRequest):
    """
    Generate scripts with SSE for real-time progress updates
    """
    return StreamingResponse(
        generate_sse_events(
            product_url=request.product_url,
            product_name=request.product_name,
            product_info=request.product_info,
            selling_points=request.selling_points,
            comments=request.comments
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


class RewriteScriptRequest(BaseModel):
    """Request model for rewriting script"""
    script: ScriptWithStyle
    mode: str


@router.post("/rewrite-script")
def rewrite_script(request: RewriteScriptRequest):
    """
    Rewrite existing script based on mode
    """
    try:
        result = production_service.rewrite_script(
            script=request.script.model_dump(),
            mode=request.mode
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
