"""
Production API routes
"""
import json
import logging
from urllib.parse import quote
from typing import Dict, List

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response, StreamingResponse
from pydantic import BaseModel

from backend.schemas.production import (
    GenerateScriptFromCommentsRequest,
    GenerateMultiStyleScriptsResponse,
    ExportScriptsRequest,
    RewriteScriptRequest,
    ParseProductRequest,
    ParseProductResponse,
    ParseProductStreamRequest,
    ScriptWithStyle,
)
from backend.services.production_service import ProductionService
from backend.services.export_service import ExportService
from backend.services.sse_service import generate_sse_events, generate_parse_ocr_stream_events
from backend.crawler.simple_parser import parse_product as crawl_product, detect_platform
from backend.crawler.douyin_parser import parse_douyin_product
from backend.ai_engine.structure_service import extract_product_structure, extract_ocr_summary
from backend.ai_engine.ocr_service import get_ocr_service
from backend.data.mock_data import get_mock_data


router = APIRouter()

logger = logging.getLogger(__name__)

production_service = ProductionService()
export_service = ExportService()
ocr_service = get_ocr_service()


# ===== 路由端点 =====


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


@router.get("/generate-scripts-sse")
def generate_scripts_sse(
    product_url: str = "",
    product_name: str = "",
    product_info: str = "",
    selling_points: str = "",
    structured: str = "{}",
    comments: str = "[]"
):
    """
    Generate scripts with SSE for real-time progress updates
    """
    comment_list = json.loads(comments) if comments else []
    structured_data = json.loads(structured) if structured else {}

    return StreamingResponse(
        generate_sse_events(
            production_service,
            product_url=product_url,
            product_name=product_name,
            product_info=product_info,
            selling_points=selling_points,
            structured=structured_data,
            comments=comment_list
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


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


@router.post("/parse-product", response_model=ParseProductResponse)
def parse_product(request: ParseProductRequest):
    """
    Parse product URL - V3/V4 implementation
    V4: Use Playwright for Douyin URLs
    """
    url = request.url

    # V4: Use Playwright for Douyin URLs (including jinritemai haohuo)
    if "douyin" in url.lower() or "抖音" in url or "jinritemai.com" in url or "haohuo" in url:
        logger.info("Detected Douyin URL, using Playwright...")
        try:
            parsed = parse_douyin_product(url)
            logger.info(f"parse_douyin_product 返回: name={parsed.get('name')}")

            # If Playwright returns empty result, it likely means user is not logged in
            # Fall back to simple parser
            if not parsed.get("name"):
                logger.warning("Playwright 解析结果为空，可能未登录，使用简单解析")
            else:
                # 名称和卖点都使用原始提取的，不经过 AI
                # Extract structured product info
                try:
                    structured = extract_product_structure(
                        parsed.get("name", ""),
                        parsed.get("selling_points", ""),
                        parsed.get("ocr_text", "")
                    )
                    parsed["structured"] = structured
                except Exception as e:
                    logger.error(f"Structure extraction failed: {e}")
                    parsed["structured"] = {}

                # Generate comments with AI
                if not parsed.get("comments"):
                    comments = production_service.ai_service.generate_comments(
                        parsed.get("name", ""),
                        parsed.get("selling_points", "")
                    )
                    parsed["comments"] = comments if comments else []

                logger.info(f"Playwright parsed: name={parsed.get('name')}")
                return {
                    "name": parsed.get("name", ""),
                    "selling_points": parsed.get("selling_points", ""),
                    "ocr_text": parsed.get("ocr_text", ""),
                    "structured": parsed.get("structured", {}),
                    "comments": parsed.get("comments", []),
                    "images": parsed.get("images", [])
                }
        except Exception as e:
            logger.error(f"Playwright parsing failed: {e}")

    # V3: Try simple HTML parsing first (for non-Douyin URLs, or when Douyin Playwright failed)
    parsed = crawl_product(url)

    # If parsing is weak, use AI to generate comments only (not name)
    # 名称和卖点都使用原始提取的，不经过 AI
    if not parsed.get("comments"):
        try:
            comments = production_service.ai_service.generate_comments(
                parsed.get("name", ""),
                parsed.get("product_info", "")
            )
            parsed["comments"] = comments if comments else []
        except Exception as e:
            logger.error(f"Comment generation failed: {e}")
            parsed["comments"] = []

    # If still empty, use mock data based on platform
    if not parsed.get("name"):
        platform = detect_platform(url)
        mock_data = get_mock_data(platform)
        parsed = {**parsed, **mock_data}

    # Clean up selling_points
    if parsed.get("selling_points") and isinstance(parsed["selling_points"], str):
        # Truncate if too long
        if len(parsed["selling_points"]) > 200:
            parsed["selling_points"] = parsed["selling_points"][:200]

    logger.info(f"Final parsed result: name={parsed.get('name')}, comments_count={len(parsed.get('comments', []))}")

    # Extract structured info for non-Douyin URLs
    if not parsed.get("structured"):
        try:
            structured = extract_product_structure(
                parsed.get("name", ""),
                parsed.get("selling_points", ""),
                parsed.get("ocr_text", "")
            )
            parsed["structured"] = structured
        except Exception as e:
            logger.error(f"Structure extraction failed: {e}")
            parsed["structured"] = {}

    return {
        "name": parsed.get("name", ""),
        "selling_points": parsed.get("selling_points", ""),
        "ocr_text": parsed.get("ocr_text", ""),
        "structured": parsed.get("structured", {}),
        "comments": parsed.get("comments", []),
        "images": parsed.get("images", [])
    }


@router.post("/parse-product-stream")
def parse_product_stream(request: ParseProductStreamRequest):
    """
    Streaming product parsing with progressive OCR and script generation.
    Returns SSE stream for real-time UI updates.
    """
    return StreamingResponse(
        generate_parse_ocr_stream_events(
            production_service,
            ocr_service,
            product_name=request.name,
            selling_points=request.selling_points,
            images=request.images,
            comments=request.comments
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
