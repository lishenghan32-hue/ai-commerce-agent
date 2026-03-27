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
from pydantic import BaseModel, Field
from typing import List, Optional
from typing import Dict, Generator

from backend.services.production_service import ProductionService
from backend.services.export_service import ExportService
from backend.crawler.simple_parser import parse_product as crawl_product, detect_platform
from backend.crawler.douyin_parser import parse_douyin_product
from backend.ai_engine.structure_service import extract_product_structure, extract_ocr_summary
from backend.ai_engine.ocr_service import get_ocr_service
from backend.data.mock_data import get_mock_data

# Platform detection based on URL
PLATFORM_PATTERNS = {
    "douyin": ["douyin.com", "jinritemai.com", "haohuo", "抖音"],
    "tmall": ["detail.tmall.com", "tmall.hk", "world.tmall.com", "taobao.com"],
    "jd": ["item.jd.com", "jd.com", "京东"],
    "pinduoduo": ["pinduoduo.com", "yangkeduo.com", "拼多多"]
}


def detect_platform_from_url(url: str) -> str:
    """Detect platform from URL"""
    url_lower = url.lower()
    for platform, patterns in PLATFORM_PATTERNS.items():
        for pattern in patterns:
            if pattern.lower() in url_lower:
                return platform
    return "unknown"


router = APIRouter()

logger = logging.getLogger(__name__)

production_service = ProductionService()
export_service = ExportService()
ocr_service = get_ocr_service()


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
    structured: Dict = None,
    comments: List[str] = None
) -> Generator[str, None, None]:
    """
    Generate SSE events for script generation with real-time streaming
    """
    if comments is None:
        comments = []
    if structured is None:
        structured = {}

    import logging
    logger = logging.getLogger(__name__)

    try:
        # Step 0: Process input (now handled by frontend parse-product)
        yield "event: progress\ndata: {\"step\": 0, \"status\": \"active\", \"message\": \"正在处理输入...\"}\n\n"

        # V2: Frontend already parsed the URL, directly use the passed parameters
        # V3: Use structured data for script generation
        logger.info(f"直接使用前端数据 - 商品名: {product_name}, 卖点: {selling_points}, 结构化: {structured}, 评论数: {len(comments)}")

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
        logger.info(f"结构化数据: {structured}")
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

        # Stream the best script content - pass structured data to AI service
        result = production_service.ai_service.generate_multi_style_scripts(insights, structured=structured)

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
    structured: str = "{}",
    comments: str = "[]"
):
    """
    Generate scripts with SSE for real-time progress updates
    """
    import json
    comment_list = json.loads(comments) if comments else []
    structured_data = json.loads(structured) if structured else {}

    return StreamingResponse(
        generate_sse_events(
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
    ocr_text: str = ""
    structured: dict = {}
    comments: List[str]
    images: List[str] = []


class ParseProductStreamRequest(BaseModel):
    """Request model for streaming product parsing with OCR"""
    name: str = ""
    selling_points: str = ""
    images: List[str] = []
    comments: List[str] = []


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
            # 名称和卖点都使用原始提取的，不经过 AI
            # AI 汇总在后续流程中会有详细结构化信息

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

    # V3: Try simple HTML parsing first
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


def generate_parse_ocr_stream_events(
    product_name: str = "",
    selling_points: str = "",
    images: List[str] = None,
    comments: List[str] = None
) -> Generator[str, None, None]:
    """
    Generate SSE events for streaming OCR and script generation.
    Progressive rendering: parse -> OCR per image -> structure -> script
    """
    if images is None:
        images = []
    if comments is None:
        comments = []

    logger = logging.getLogger(__name__)

    try:
        # Step 0: Start - receive product info
        product_name = product_name or "通用商品"
        logger.info(f"开始流式处理 - 商品名: {product_name}, 图片数: {len(images)}")

        yield "event: parse_start\ndata: {}\n\n"

        # Step 1: Send initial product info (already parsed by frontend)
        parse_data = json.dumps({
            'name': product_name,
            'selling_points': selling_points,
            'images': images
        }, ensure_ascii=False)
        yield f"event: parse_complete\ndata: {parse_data}\n\n"

        # Step 2: OCR per image (stream each image result)
        all_ocr_texts = []

        if images:
            ocr_start_data = json.dumps({'total': len(images)}, ensure_ascii=False)
            yield f"event: ocr_start\ndata: {ocr_start_data}\n\n"

            for i, img_url in enumerate(images):
                logger.info(f"OCR 处理图片 {i+1}/{len(images)}: {img_url[:50]}...")
                ocr_text = ""

                try:
                    if ocr_service:
                        ocr_text = ocr_service.extract_text_from_url(img_url)
                except Exception as e:
                    logger.error(f"OCR failed for image {i+1}: {e}")

                all_ocr_texts.append(ocr_text)

                # Send each image OCR result
                ocr_image_data = json.dumps({
                    'index': i + 1,
                    'total': len(images),
                    'image_url': img_url,
                    'ocr_text': ocr_text
                }, ensure_ascii=False)
                yield f"event: ocr_image\ndata: {ocr_image_data}\n\n"

            # Combine all OCR texts
            combined_ocr_text = " ".join(all_ocr_texts)
            ocr_complete_data = json.dumps({
                'total': len(images),
                'combined_text': combined_ocr_text
            }, ensure_ascii=False)
            yield f"event: ocr_complete\ndata: {ocr_complete_data}\n\n"

            # Step 2.5: AI 提取 OCR 汇总结构化信息
            logger.info(f"开始 OCR 汇总处理，图片数: {len(all_ocr_texts)}, 内容: {all_ocr_texts[:100]}")
            yield "event: ocr_summary_start\ndata: {}\n\n"

            try:
                ocr_summary = extract_ocr_summary(all_ocr_texts)
                logger.info(f"OCR 汇总结果: {ocr_summary}")
            except Exception as e:
                logger.error(f"OCR summary extraction failed: {e}")
                ocr_summary = {
                    "material": "",
                    "features": [],
                    "applicable": "",
                    "colors": "",
                    "season": "",
                    "raw_summary": ""
                }

            ocr_summary_data = json.dumps(ocr_summary, ensure_ascii=False)
            yield f"event: ocr_summary_complete\ndata: {ocr_summary_data}\n\n"
        else:
            ocr_complete_data = json.dumps({'total': 0, 'combined_text': ''}, ensure_ascii=False)
            yield f"event: ocr_complete\ndata: {ocr_complete_data}\n\n"

            # 无图片时也发送空汇总
            ocr_summary = {
                "material": "",
                "features": [],
                "applicable": "",
                "colors": "",
                "season": "",
                "raw_summary": ""
            }
            ocr_summary_data = json.dumps(ocr_summary, ensure_ascii=False)
            yield f"event: ocr_summary_complete\ndata: {ocr_summary_data}\n\n"

        # Step 3: Extract structured info
        yield "event: structure_start\ndata: {}\n\n"

        try:
            structured = extract_product_structure(
                product_name,
                selling_points,
                " ".join(all_ocr_texts)
            )
        except Exception as e:
            logger.error(f"Structure extraction failed: {e}")
            structured = {}

        structure_data = json.dumps(structured, ensure_ascii=False)
        yield f"event: structure_complete\ndata: {structure_data}\n\n"

        # Step 4: Prepare comments and generate script
        yield "event: script_start\ndata: {}\n\n"

        # Prepare comments if not provided
        if not comments:
            if selling_points:
                comments = production_service.ai_service.convert_selling_points_to_comments(selling_points)
            else:
                comments = production_service.ai_service.generate_comments(product_name, selling_points)

        # Analyze comments
        insights = production_service.ai_service.analyze_comments(comments)
        insights_data = json.dumps({
            'pain_points': insights.get('pain_points', []),
            'selling_points': insights.get('selling_points', []),
            'concerns': insights.get('concerns', []),
            'use_cases': insights.get('use_cases', [])
        }, ensure_ascii=False)
        yield f"event: insights_complete\ndata: {insights_data}\n\n"

        # Generate scripts
        result = production_service.ai_service.generate_multi_style_scripts(insights, structured=structured)

        # Stream script content
        if result.get("best_script"):
            script = result["best_script"]
            for field, label in [
                ("opening_hook", "开头吸引"),
                ("pain_point", "痛点描述"),
                ("solution", "解决方案"),
                ("proof", "证明案例"),
                ("offer", "促单话术")
            ]:
                content = script.get(field, "")
                if content:
                    section_data = json.dumps({'label': label, 'field': field}, ensure_ascii=False)
                    yield f"event: script_section\ndata: {section_data}\n\n"
                    # Stream in chunks
                    chunk_size = 8
                    for i in range(0, len(content), chunk_size):
                        chunk = content[i:i+chunk_size]
                        chunk_data = json.dumps({'content': chunk, 'field': field}, ensure_ascii=False)
                        yield f"event: script_chunk\ndata: {chunk_data}\n\n"

        yield "event: script_complete\ndata: {}\n\n"

        # Send final complete data
        complete_data = json.dumps(result, ensure_ascii=False)
        yield f"event: complete\ndata: {complete_data}\n\n"

    except Exception as e:
        logger.error(f"Stream processing failed: {e}")
        error_data = json.dumps({'message': str(e)}, ensure_ascii=False)
        yield f"event: error\ndata: {error_data}\n\n"


@router.post("/parse-product-stream")
def parse_product_stream(request: ParseProductStreamRequest):
    """
    Streaming product parsing with progressive OCR and script generation.
    Returns SSE stream for real-time UI updates.
    """
    return StreamingResponse(
        generate_parse_ocr_stream_events(
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


