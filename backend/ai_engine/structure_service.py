"""
Product Structure Service - Extract structured product information using AI
"""
import json
import logging
from typing import Dict, Any, List

from backend.config import settings
from backend.services.ai import get_ai_service
from backend.services.ai import prompts

logger = logging.getLogger(__name__)


def extract_ocr_summary(ocr_texts: List[str], product_name: str = "") -> Dict[str, Any]:
    """
    Extract structured information from all OCR texts using AI.

    Args:
        ocr_texts: List of OCR texts from all product images
        product_name: Original product name

    Returns:
        Dict with structured fields: material, features, applicable, colors, season, raw_summary, product_name
    """
    if not ocr_texts:
        return {
            "product_name": product_name,
            "material": "",
            "features": [],
            "applicable": "",
            "colors": "",
            "season": "",
            "raw_summary": ""
        }

    combined_text = " ".join(ocr_texts)

    try:
        ai_service = get_ai_service()
        prompt = prompts.build_ocr_summary_prompt(combined_text)
        raw_response = ai_service._call_api(prompt)
        logger.info(f"OCR summary raw response: {raw_response[:200]}")
        json_response = ai_service._extract_json_with_llm(raw_response)
        logger.info(f"OCR summary json response: {json_response[:200]}")
        parsed = json.loads(json_response)

        return {
            "product_name": product_name,
            "material": parsed.get("material", ""),
            "features": parsed.get("features", []),
            "function": parsed.get("function", ""),
            "scene": parsed.get("scene", ""),
            "applicable": parsed.get("applicable", ""),
            "colors": parsed.get("colors", ""),
            "season": parsed.get("season", ""),
            "raw_summary": parsed.get("raw_summary", "")[:500] if parsed.get("raw_summary") else ""
        }
    except Exception as e:
        logger.error(f"Failed to extract OCR summary: {e}")
        return {
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
        ai_service = get_ai_service()
        prompt = prompts.build_structure_prompt(name, selling_points, ocr_text)
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
