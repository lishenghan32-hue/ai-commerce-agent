"""
AI Script Service - Script generation, scoring and rewriting
"""
import json
import logging
from typing import Dict, Any, List

from backend.services.ai.base import BaseAIService
from backend.services.ai import prompts

logger = logging.getLogger(__name__)


class AIServiceScriptMixin(BaseAIService):
    """Mixin with script-related methods"""

    def generate_script(self, insights: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate live streaming script based on insights

        Returns:
            Dict with opening_hook, pain_point, solution, proof, offer
        """
        if not insights:
            return self._default_script()

        prompt = prompts.build_script_prompt(insights)
        raw_response = self._call_api(prompt)
        json_response = self._extract_json_with_llm(raw_response)

        try:
            parsed = json.loads(json_response)
            return {
                "opening_hook": parsed.get("opening_hook") or "",
                "pain_point": parsed.get("pain_point") or "",
                "solution": parsed.get("solution") or "",
                "proof": parsed.get("proof") or "",
                "offer": parsed.get("offer") or ""
            }
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON: {json_response}")
            return self._default_script()

    def generate_multi_style_scripts(
        self,
        insights: Dict[str, Any],
        structured: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Generate scripts in three different styles

        Args:
            insights: User insights from comment analysis
            structured: Structured product data

        Returns:
            Dict with scripts array and best_script
        """
        if insights is None:
            insights = {}
        if structured is None:
            structured = {}

        has_structured = any([
            structured.get("title"),
            structured.get("material"),
            structured.get("function"),
            structured.get("scene"),
            structured.get("target"),
            structured.get("advantage"),
            structured.get("selling_points")
        ])

        if not insights and not has_structured:
            return {
                "scripts": [self._default_script_with_style(s) for s in ["带货型", "共情型", "理性型"]],
                "best_script": None
            }

        styles = ["带货型", "共情型", "理性型"]
        scripts = []

        for style in styles:
            try:
                prompt = prompts.build_multi_style_script_prompt(insights, style, structured)
                raw_response = self._call_api(prompt)
                json_response = self._extract_json_with_llm(raw_response)

                parsed = json.loads(json_response)
                script = {
                    "style": style,
                    "opening_hook": parsed.get("opening_hook") or "",
                    "pain_point": parsed.get("pain_point") or "",
                    "solution": parsed.get("solution") or "",
                    "proof": parsed.get("proof") or "",
                    "offer": parsed.get("offer") or ""
                }

                score_result = self.score_script(script)
                script["score"] = score_result["score"]
                script["reason"] = score_result["reason"]

            except Exception as e:
                logger.error(f"Failed to generate {style} script: {e}")
                script = self._default_script_with_style(style)
                script["score"] = 0
                script["reason"] = "生成失败"

            scripts.append(script)

        best_script = max(scripts, key=lambda x: x.get("score", 0))

        return {
            "scripts": scripts,
            "best_script": best_script
        }

    def score_script(self, script: Dict[str, Any]) -> Dict[str, Any]:
        """
        Score a script for viral potential

        Returns:
            Dict with score (0-100) and reason
        """
        if not script:
            return {"score": 0, "reason": "脚本为空"}

        try:
            prompt = prompts.build_score_prompt(script)
            raw_response = self._call_api(prompt)
            json_response = self._extract_json_with_llm(raw_response)

            parsed = json.loads(json_response)
            return {
                "score": parsed.get("score") or 0,
                "reason": parsed.get("reason") or ""
            }
        except Exception as e:
            logger.error(f"Failed to score script: {e}")
            return {"score": 0, "reason": "评分失败"}

    def rewrite_script(self, script: Dict[str, Any], mode: str) -> Dict[str, Any]:
        """
        Rewrite script based on mode

        Args:
            script: Original script dict
            mode: One of "强化转化", "更口语", "更理性", "更简短"

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
