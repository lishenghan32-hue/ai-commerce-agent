"""
AI Product Service - Product structure and OCR summary
"""
import json
import logging
from typing import Dict, Any, List

from backend.services.ai.base import BaseAIService
from backend.services.ai import prompts

logger = logging.getLogger(__name__)


class AIServiceProductMixin(BaseAIService):
    """Mixin with product-related methods"""

    def summarize_product_info(
        self,
        name: str,
        ocr_text: str,
        existing_selling_points: str = ""
    ) -> Dict[str, Any]:
        """
        Summarize and enhance product info using AI from OCR text

        Args:
            name: Product name
            ocr_text: OCR extracted text
            existing_selling_points: Already extracted selling points

        Returns:
            Dict with product_name, selling_points
        """
        structured = self.build_structured_product_info(name, ocr_text, existing_selling_points)

        return {
            "product_name": structured.get("title") or name,
            "selling_points": structured.get("selling_points") or existing_selling_points
        }

    def build_structured_product_info(
        self,
        name: str,
        ocr_text: str = "",
        selling_points: str = ""
    ) -> Dict[str, Any]:
        """
        Build structured product information by merging OCR + selling points

        Args:
            name: Product name
            ocr_text: OCR extracted text
            selling_points: Selling points

        Returns:
            Dict with structured fields
        """
        if not name and not ocr_text and not selling_points:
            return {
                "title": "",
                "material": "",
                "function": "",
                "scene": "",
                "target": "",
                "advantage": "",
                "selling_points": ""
            }

        try:
            prompt = prompts.build_structure_prompt(name, selling_points, ocr_text)
            raw_response = self._call_api(prompt)
            json_response = self._extract_json_with_llm(raw_response)
            parsed = json.loads(json_response)

            return {
                "title": parsed.get("title") or name,
                "material": parsed.get("material") or "",
                "function": parsed.get("function") or "",
                "scene": parsed.get("scene") or "",
                "target": parsed.get("target") or "",
                "advantage": parsed.get("advantage") or "",
                "selling_points": parsed.get("selling_points") or selling_points
            }
        except Exception as e:
            logger.error(f"Failed to build structured product info: {e}")
            return {
                "title": name,
                "material": "",
                "function": "",
                "scene": "",
                "target": "",
                "advantage": selling_points[:50] if selling_points else "",
                "selling_points": selling_points
            }

    def summarize_ocr(self, ocr_texts: List[str]) -> Dict[str, Any]:
        """
        Extract structured information from OCR texts

        Args:
            ocr_texts: List of OCR texts from product images

        Returns:
            Dict with material, features, applicable, colors, season, raw_summary
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
            prompt = prompts.build_ocr_summary_prompt(combined_text)
            raw_response = self._call_api(prompt)
            json_response = self._extract_json_with_llm(raw_response)
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
            logger.error(f"Failed to summarize OCR: {e}")
            return {
                "material": "",
                "features": [],
                "applicable": "",
                "colors": "",
                "season": "",
                "raw_summary": ""
            }
