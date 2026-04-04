"""
AI Script Service - Script generation and rewriting
"""
import json
import logging
from typing import Dict, Any

from backend.services.ai.base import BaseAIService
from backend.services.ai import prompts

logger = logging.getLogger(__name__)


class AIServiceScriptMixin(BaseAIService):
    """Mixin with script-related methods"""

    def generate_single_style_script(
        self,
        insights: Dict[str, Any],
        structured: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Generate a single live streaming script (带货型)

        Args:
            insights: User insights from comment analysis
            structured: Structured product data

        Returns:
            Dict with opening_hook, pain_point, solution, proof, offer
        """
        if insights is None:
            insights = {}
        if structured is None:
            structured = {}

        # 检查是否有任何结构化数据（OCR 返回的字段名）
        has_structured = any([
            # 旧字段名
            structured.get("title"),
            structured.get("material"),
            structured.get("function"),
            structured.get("scene"),
            structured.get("target"),
            structured.get("advantage"),
            structured.get("selling_points"),
            # 通用字段（OCR 返回）
            structured.get("product_name"),
            structured.get("product_type"),
            structured.get("features"),
            structured.get("applicable"),
            structured.get("colors"),
            structured.get("season"),
            structured.get("brief_summary"),
            structured.get("detailed_summary"),
            # 服装特有
            structured.get("thickness"),
            structured.get("style"),
            # 食品特有
            structured.get("ingredients"),
            structured.get("shelf_life"),
            structured.get("origin"),
            structured.get("spec"),
            # 电子产品特有
            structured.get("model"),
            structured.get("power"),
            structured.get("battery"),
            structured.get("compatible"),
            # 美妆特有
            structured.get("effect"),
            structured.get("skin_type"),
            structured.get("usage"),
        ])

        if not insights and not has_structured:
            return self._default_script()

        try:
            prompt = prompts.build_single_style_script_prompt(insights, structured)
            logger.info(f"生成话术的prompt长度: {len(prompt)}")
            raw_response = self._call_api(prompt)
            logger.info(f"AI返回的原始响应: {raw_response[:800]}...")
            json_response = self._extract_json_with_llm(raw_response)
            logger.info(f"解析后的JSON: {json_response[:800]}...")
            parsed = json.loads(json_response)

            logger.info(f"解析后的话术字段: {list(parsed.keys())}")

            return {
                "opening": parsed.get("opening") or "",
                "material": parsed.get("material") or "",
                "design": parsed.get("design") or "",
                "details": parsed.get("details") or "",
                "pairing": parsed.get("pairing") or "",
                "offer": parsed.get("offer") or ""
            }
        except Exception as e:
            logger.error(f"Failed to generate script: {e}")
            return self._default_script()

    def rewrite_script(self, script: Dict[str, Any], mode: str) -> Dict[str, Any]:
        """
        Rewrite script based on mode

        Args:
            script: Original script dict
            mode: Rewrite mode

        Returns:
            Dict with rewritten script content
        """
        if not script:
            return self._default_script()

        prompt = prompts.build_rewrite_prompt(script, mode)

        try:
            raw_response = self._call_api(prompt)
            json_response = self._extract_json_with_llm(raw_response)

            parsed = json.loads(json_response)
            return {
                "opening_hook": parsed.get("opening_hook") or "",
                "pain_point": parsed.get("pain_point") or "",
                "solution": parsed.get("solution") or "",
                "proof": parsed.get("proof") or "",
                "offer": parsed.get("offer") or ""
            }
        except Exception as e:
            logger.error(f"Failed to rewrite script: {e}")
            return script
