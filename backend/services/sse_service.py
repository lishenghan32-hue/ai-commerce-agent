"""
SSE event generators for streaming responses
"""
import json
import logging
from typing import Generator, Dict, List


def _stream_script(script: Dict[str, str], chunk_size: int) -> Generator[str, None, None]:
    """Stream script sections in small chunks."""
    for field, label in [
        ("opening_hook", "开头吸引"),
        ("pain_point", "痛点描述"),
        ("solution", "解决方案"),
        ("proof", "证明案例"),
        ("offer", "促单话术")
    ]:
        content = script.get(field, "")
        if content:
            yield f"event: script_section\ndata: {json.dumps({'label': label, 'field': field}, ensure_ascii=False)}\n\n"
            for i in range(0, len(content), chunk_size):
                chunk = content[i:i + chunk_size]
                yield f"event: script_chunk\ndata: {json.dumps({'content': chunk, 'field': field}, ensure_ascii=False)}\n\n"


def generate_sse_events(
    production_service,
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

    logger = logging.getLogger(__name__)

    try:
        yield "event: progress\ndata: {\"step\": 0, \"status\": \"active\", \"message\": \"正在处理输入...\"}\n\n"

        logger.info(
            f"直接使用前端数据 - 商品名: {product_name}, 卖点: {selling_points}, 结构化: {structured}, 评论数: {len(comments)}"
        )

        if not product_name:
            product_name = "通用商品"
            logger.warning("product_name 为空，使用默认值")
        if not comments:
            comments = ["质量不错", "性价比高", "值得购买"]
            logger.warning("comments 为空，使用默认评论")

        script = production_service.generate_script_from_comments(
            product_url=product_url,
            product_name=product_name,
            product_info=product_info,
            selling_points=selling_points,
            comments=comments,
            structured=structured
        )

        yield "event: progress\ndata: {\"step\": 0, \"status\": \"completed\", \"message\": \"输入处理完成\"}\n\n"
        yield "event: progress\ndata: {\"step\": 1, \"status\": \"completed\", \"message\": \"评论分析完成\"}\n\n"
        yield "event: progress\ndata: {\"step\": 2, \"status\": \"active\", \"message\": \"正在生成话术...\"}\n\n"

        yield from _stream_script(script, chunk_size=10)

        yield "event: progress\ndata: {\"step\": 2, \"status\": \"completed\", \"message\": \"话术生成完成\"}\n\n"
        yield f"event: script_complete\ndata: {json.dumps({'completed': True}, ensure_ascii=False)}\n\n"
        yield f"event: complete\ndata: {json.dumps({'script': script}, ensure_ascii=False)}\n\n"

    except Exception as e:
        yield f"event: error\ndata: {json.dumps({'message': str(e)}, ensure_ascii=False)}\n\n"


def generate_parse_ocr_stream_events(
    production_service,
    ocr_service,
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

    from backend.ai_engine.structure_service import extract_ocr_summary

    try:
        product_name = product_name or "通用商品"
        logger.info(f"开始流式处理 - 商品名: {product_name}, 图片数: {len(images)}")

        yield "event: parse_start\ndata: {}\n\n"

        parse_data = json.dumps({
            "name": product_name,
            "selling_points": selling_points,
            "images": images
        }, ensure_ascii=False)
        yield f"event: parse_complete\ndata: {parse_data}\n\n"

        all_ocr_texts = []

        if images:
            ocr_start_data = json.dumps({"total": len(images)}, ensure_ascii=False)
            yield f"event: ocr_start\ndata: {ocr_start_data}\n\n"

            for i, img_url in enumerate(images):
                logger.info(f"OCR 处理图片 {i + 1}/{len(images)}: {img_url[:50]}...")
                ocr_text = ""

                try:
                    if ocr_service:
                        ocr_text = ocr_service.extract_text_from_url(img_url)
                except Exception as e:
                    logger.error(f"OCR failed for image {i + 1}: {e}")

                all_ocr_texts.append(ocr_text)
                ocr_image_data = json.dumps({
                    "index": i + 1,
                    "total": len(images),
                    "image_url": img_url,
                    "ocr_text": ocr_text
                }, ensure_ascii=False)
                yield f"event: ocr_image\ndata: {ocr_image_data}\n\n"

            combined_ocr_text = " ".join(all_ocr_texts)
            ocr_complete_data = json.dumps({
                "total": len(images),
                "combined_text": combined_ocr_text
            }, ensure_ascii=False)
            yield f"event: ocr_complete\ndata: {ocr_complete_data}\n\n"

            yield "event: ocr_summary_start\ndata: {}\n\n"

            try:
                ocr_summary = extract_ocr_summary(all_ocr_texts, product_name)
                logger.info(f"OCR summary: {ocr_summary}")
            except Exception as e:
                logger.error(f"OCR summary extraction failed: {e}")
                ocr_summary = {
                    "product_name": product_name,
                    "material": "",
                    "features": [],
                    "function": "",
                    "scene": "",
                    "applicable": "",
                    "colors": "",
                    "season": "",
                    "raw_summary": ""
                }

            ocr_summary_data = json.dumps(ocr_summary, ensure_ascii=False)
            yield f"event: ocr_summary_complete\ndata: {ocr_summary_data}\n\n"
        else:
            ocr_complete_data = json.dumps({"total": 0, "combined_text": ""}, ensure_ascii=False)
            yield f"event: ocr_complete\ndata: {ocr_complete_data}\n\n"

            ocr_summary = {
                "product_name": product_name,
                "material": "",
                "features": [],
                "function": "",
                "scene": "",
                "applicable": "",
                "colors": "",
                "season": "",
                "raw_summary": ""
            }
            ocr_summary_data = json.dumps(ocr_summary, ensure_ascii=False)
            yield f"event: ocr_summary_complete\ndata: {ocr_summary_data}\n\n"

        yield "event: structure_start\ndata: {}\n\n"

        structured = {
            "title": ocr_summary.get("product_name", ""),
            "material": ocr_summary.get("material", ""),
            "features": ocr_summary.get("features", []),
            "function": ocr_summary.get("function", ""),
            "scene": ocr_summary.get("scene", ""),
            "target": ocr_summary.get("applicable", ""),  # Map applicable to target for script generation
            "advantage": ocr_summary.get("raw_summary", ""),
            "applicable": ocr_summary.get("applicable", ""),
            "colors": ocr_summary.get("colors", ""),
            "season": ocr_summary.get("season", ""),
            "raw_summary": ocr_summary.get("raw_summary", "")
        }

        structure_data = json.dumps(structured, ensure_ascii=False)
        yield f"event: structure_complete\ndata: {structure_data}\n\n"

        yield "event: script_start\ndata: {}\n\n"

        script = production_service.generate_script_from_comments(
            product_name=product_name,
            product_info=selling_points,
            selling_points=selling_points,
            comments=comments,
            structured=structured
        )

        yield from _stream_script(script, chunk_size=8)
        yield f"event: script_complete\ndata: {json.dumps({'completed': True}, ensure_ascii=False)}\n\n"
        yield f"event: complete\ndata: {json.dumps({'script': script}, ensure_ascii=False)}\n\n"

    except Exception as e:
        logger.error(f"Stream processing failed: {e}")
        error_data = json.dumps({"message": str(e)}, ensure_ascii=False)
        yield f"event: error\ndata: {error_data}\n\n"
