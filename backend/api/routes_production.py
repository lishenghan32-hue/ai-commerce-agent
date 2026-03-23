"""
Production API routes
"""
import os
import json
from urllib.parse import quote
from typing import Generator, Dict
import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response, StreamingResponse
from pydantic import BaseModel
from typing import List, Optional

from backend.services.production_service import ProductionService
from backend.services.export_service import ExportService
from backend.crawler.simple_parser import parse_product as crawl_product, detect_platform

router = APIRouter()

logger = logging.getLogger(__name__)

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
    Generate SSE events for script generation with real-time streaming
    """
    if comments is None:
        comments = []

    import logging
    logger = logging.getLogger(__name__)

    try:
        # Step 0: Process input (now handled by frontend parse-product)
        yield "event: progress\ndata: {\"step\": 0, \"status\": \"active\", \"message\": \"正在处理输入...\"}\n\n"

        # V2: Frontend already parsed the URL, directly use the passed parameters
        logger.info(f"直接使用前端数据 - 商品名: {product_name}, 卖点: {selling_points}, 评论数: {len(comments)}")

        # Fallback protection
        if not product_name:
            product_name = "通用商品"
            logger.warning("product_name 为空，使用默认值")
        if not comments:
            comments = ["质量不错", "性价比高", "值得购买"]
            logger.warning("comments 为空，使用默认评论")

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

        # Step 2: Generating scripts with streaming
        yield "event: progress\ndata: {\"step\": 2, \"status\": \"active\", \"message\": \"正在生成话术...\"}\n\n"

        # Stream the best script content
        result = production_service.ai_service.generate_multi_style_scripts(insights)

        if result.get("best_script"):
            script = result["best_script"]
            # Stream each section
            for field, label in [
                ("opening_hook", "开头吸引"),
                ("pain_point", "痛点描述"),
                ("solution", "解决方案"),
                ("proof", "证明案例"),
                ("offer", "促单话术")
            ]:
                content = script.get(field, "")
                if content:
                    yield f"event: section\ndata: {json.dumps({'label': label, 'field': field}, ensure_ascii=False)}\n\n"
                    # Stream content in chunks
                    chunk_size = 10
                    for i in range(0, len(content), chunk_size):
                        chunk = content[i:i+chunk_size]
                        yield f"event: chunk\ndata: {json.dumps({'content': chunk, 'field': field}, ensure_ascii=False)}\n\n"

        yield "event: progress\ndata: {\"step\": 2, \"status\": \"completed\", \"message\": \"话术生成完成\"}\n\n"

        # Step 3: Scoring
        yield "event: progress\ndata: {\"step\": 3, \"status\": \"active\", \"message\": \"正在评分...\"}\n\n"

        yield "event: progress\ndata: {\"step\": 3, \"status\": \"completed\", \"message\": \"评分完成\"}\n\n"

        # Send final complete data
        yield f"event: complete\ndata: {json.dumps(result, ensure_ascii=False)}\n\n"

    except Exception as e:
        yield f"event: error\ndata: {json.dumps({'message': str(e)}, ensure_ascii=False)}\n\n"


@router.get("/generate-scripts-sse")
def generate_scripts_sse(
    product_url: str = "",
    product_name: str = "",
    product_info: str = "",
    selling_points: str = "",
    comments: str = "[]"
):
    """
    Generate scripts with SSE for real-time progress updates
    """
    import json
    comment_list = json.loads(comments) if comments else []

    return StreamingResponse(
        generate_sse_events(
            product_url=product_url,
            product_name=product_name,
            product_info=product_info,
            selling_points=selling_points,
            comments=comment_list
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


class ParseProductRequest(BaseModel):
    """Request model for parsing product URL"""
    url: str


class ParseProductResponse(BaseModel):
    """Response model for product parsing"""
    name: str
    selling_points: str
    comments: List[str]


@router.post("/parse-product", response_model=ParseProductResponse)
def parse_product(request: ParseProductRequest):
    """
    Parse product URL - V3 implementation
    Uses simple HTML parser first, then AI fallback
    """
    url = request.url

    # Try simple HTML parsing first
    parsed = crawl_product(url)

    # If parsing is weak, use AI to enhance
    if not parsed.get("name") or not parsed.get("selling_points"):
        logger.info("HTML parsing weak, using AI fallback")
        try:
            ai_result = production_service.ai_service.extract_product_info_from_url(url)
            if not parsed.get("name") and ai_result.get("product_name"):
                parsed["name"] = ai_result["product_name"]
            if not parsed.get("selling_points") and ai_result.get("selling_points"):
                if isinstance(ai_result["selling_points"], list):
                    parsed["selling_points"] = ", ".join(ai_result["selling_points"])
                else:
                    parsed["selling_points"] = ai_result["selling_points"]
        except Exception as e:
            logger.error(f"AI fallback failed: {e}")

    # Generate comments using AI
    if not parsed.get("comments"):
        try:
            comments = production_service.ai_service.generate_comments(
                parsed.get("name", ""),
                parsed.get("product_info", "") + " " + parsed.get("selling_points", "")
            )
            parsed["comments"] = comments if comments else []
        except Exception as e:
            logger.error(f"Comment generation failed: {e}")
            parsed["comments"] = []

    # If still empty, use mock data based on platform
    if not parsed.get("name"):
        platform = detect_platform(url)
        mock_data = _get_mock_data(platform)
        parsed = {**parsed, **mock_data}

    # Clean up selling_points
    if parsed.get("selling_points") and isinstance(parsed["selling_points"], str):
        # Truncate if too long
        if len(parsed["selling_points"]) > 200:
            parsed["selling_points"] = parsed["selling_points"][:200]

    logger.info(f"Final parsed result: name={parsed.get('name')}, comments_count={len(parsed.get('comments', []))}")

    return {
        "name": parsed.get("name", ""),
        "selling_points": parsed.get("selling_points", ""),
        "comments": parsed.get("comments", [])
    }


def _get_mock_data(platform: str) -> Dict:
    """Get mock data based on platform"""
    mock_data = {
        "taobao": {
            "name": "美白精华液",
            "selling_points": "美白提亮，28天见效，温和不刺激",
            "comments": ["用了皮肤确实变白了", "就是价格有点贵", "包装很高大上", "用了一周效果不明显", "会回购的"]
        },
        "tmall": {
            "name": "美白精华液",
            "selling_points": "美白提亮，28天见效，温和不刺激",
            "comments": ["用了皮肤确实变白了", "就是价格有点贵", "包装很高大上", "用了一周效果不明显", "会回购的"]
        },
        "douyin": {
            "name": "无线蓝牙耳机",
            "selling_points": "主动降噪，30小时续航，Hi-Fi音质",
            "comments": ["音质真的很不错", "电池续航一般般", "操作很简单", "比实体店便宜", "售后态度很好"]
        },
        "jd": {
            "name": "智能手环",
            "selling_points": "心率监测，睡眠追踪，防水设计",
            "comments": ["功能很全面", "续航一周没问题", "佩戴舒服", "数据不太准", "性价比高"]
        },
        "pinduoduo": {
            "name": "实用小商品",
            "selling_points": "性价比高，实用性强",
            "comments": ["价格实惠", "质量一般", "物流很快", "包装简陋", "值得购买"]
        },
        "unknown": {
            "name": "通用商品",
            "selling_points": "高品质，性价比高，实用性强",
            "comments": ["质量很好", "发货速度快", "包装完好", "性价比不错", "会推荐给朋友"]
        }
    }
    return mock_data.get(platform, mock_data["unknown"])
