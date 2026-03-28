"""
SSE event generators for streaming responses
"""
import json
import logging
from typing import Generator, Dict, List, Optional


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

    # Import here to avoid circular dependency
    from backend.ai_engine.structure_service import extract_product_structure, extract_ocr_summary

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
