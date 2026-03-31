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

    def generate_single_style_script(
        self,
        insights: Dict[str, Any],
        structured: Dict[str, Any] = None,
        style: str = "带货型"
    ) -> Dict[str, Any]:
        """
        Generate a single live streaming script in one style

        Args:
            insights: User insights from comment analysis
            structured: Structured product data
            style: Script style to use

        Returns:
            Dict with opening_hook, pain_point, solution, proof, offer
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
            return self._default_script()

        try:
            prompt = prompts.build_single_style_script_prompt(insights, style, structured)
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
            logger.error(f"Failed to generate {style} script: {e}")
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
