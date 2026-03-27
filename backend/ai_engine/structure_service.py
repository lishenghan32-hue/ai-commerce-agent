"""
Product Structure Service - Extract structured product information using AI
"""
import json
import logging
from typing import Dict, Any, List

from backend.config import settings
from backend.services.ai_service import AIService

logger = logging.getLogger(__name__)


def extract_ocr_summary(ocr_texts: List[str]) -> Dict[str, Any]:
    """
    Extract structured information from all OCR texts using AI.

    Args:
        ocr_texts: List of OCR texts from all product images

    Returns:
        Dict with structured fields: material, features, applicable, colors, season, raw_summary
    """
    if not ocr_texts:
        return {
            "material": "",
            "features": [],
            "applicable": "",
            "colors": "",
            "season": "",
            "raw_summary": ""
        }

    combined_text = " ".join(ocr_texts)

    try:
        ai_service = AIService()
        prompt = _build_ocr_summary_prompt(combined_text)
        raw_response = ai_service._call_api(prompt)
        json_response = ai_service._extract_json_with_llm(raw_response)
        parsed = json.loads(json_response)

        return {
            "material": parsed.get("material", ""),
            "features": parsed.get("features", []),
            "applicable": parsed.get("applicable", ""),
            "colors": parsed.get("colors", ""),
            "season": parsed.get("season", ""),
            "raw_summary": parsed.get("raw_summary", "")[:500] if parsed.get("raw_summary") else ""
        }
    except Exception as e:
        logger.error(f"Failed to extract OCR summary: {e}")
        return {
            "material": "",
            "features": [],
            "applicable": "",
            "colors": "",
            "season": "",
            "raw_summary": ""
        }


def _build_ocr_summary_prompt(ocr_text: str) -> str:
    """Build prompt for extracting OCR summary"""
    prompt = f"""你是电商商品详情页分析专家。
请从以下商品详情页OCR文字中提取结构化信息，返回JSON：
要求：
1. 不允许编造，没有就填空字符串
2. features数组不超过5个，每个不超过20字
3. raw_summary为500字以内的详细汇总，包含材质、面料特点、穿着体验、适用场景等
4. 必须返回JSON，不要解释

字段：
- material（材质，如：100%纯棉、聚酯纤维等）
- features（特点数组，如：透气吸汗、不起球、柔软舒适等）
- applicable（适用人群/场景，如：3-8岁儿童、日常上学穿）
- colors（颜色，如：多色可选）
- season（季节，如：夏季、四季通用）
- raw_summary（500字以内的详细汇总）

输入：
{ocr_text}

输出格式：
{{
  "material": "",
  "features": [],
  "applicable": "",
  "colors": "",
  "season": "",
  "raw_summary": ""
}}
只返回JSON。"""
    return prompt


def extract_product_structure(name: str, selling_points: str, ocr_text: str) -> Dict[str, str]:
    """
    Extract structured product information from name, selling_points and ocr_text

    Args:
        name: Product name
        selling_points: Selling points from CSS selector
        ocr_text: OCR text from product images

    Returns:
        Dict with structured fields: title, material, function, scene, target, advantage
    """
    if not name and not selling_points and not ocr_text:
        return {
            "title": "",
            "material": "",
            "function": "",
            "scene": "",
            "target": "",
            "advantage": ""
        }

    try:
        ai_service = AIService()
        prompt = _build_structure_prompt(name, selling_points, ocr_text)
        raw_response = ai_service._call_api(prompt)
        json_response = ai_service._extract_json_with_llm(raw_response)
        parsed = json.loads(json_response)

        return {
            "title": parsed.get("title", "") or name,
            "material": parsed.get("material", ""),
            "function": parsed.get("function", ""),
            "scene": parsed.get("scene", ""),
            "target": parsed.get("target", ""),
            "advantage": parsed.get("advantage", "")
        }
    except Exception as e:
        logger.error(f"Failed to extract product structure: {e}")
        return {
            "title": name,
            "material": "",
            "function": "",
            "scene": "",
            "target": "",
            "advantage": ""
        }


def _build_structure_prompt(name: str, selling_points: str, ocr_text: str) -> str:
    """Build prompt for extracting structured product information"""
    prompt = f"""你是电商商品结构化专家。
请从以下信息中提取商品结构，返回JSON：
要求：
1. 不允许编造，没有就填空字符串
2. 每个字段不超过50字
3. 必须返回JSON，不要解释
字段：
- title（商品标题）
- material（材质）
- function（功能）
- scene（使用场景）
- target（人群）
- advantage（核心优势）
输入：
【标题】
{name}
【基础卖点】
{selling_points}
【详情文案】
{ocr_text}
输出格式：
{{
  "title": "",
  "material": "",
  "function": "",
  "scene": "",
  "target": "",
  "advantage": ""
}}
只返回JSON。"""
    return prompt
