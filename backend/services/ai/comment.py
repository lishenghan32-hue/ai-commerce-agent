"""
AI Comment Service - Comment analysis and generation
"""
import json
import logging
from typing import Dict, Any, List

from backend.services.ai.base import BaseAIService
from backend.services.ai import prompts

logger = logging.getLogger(__name__)


class AIServiceCommentMixin(BaseAIService):
    """Mixin with comment-related methods"""

    def analyze_comments(self, comments: List[str]) -> Dict[str, Any]:
        """
        Analyze comments to extract user insights

        Returns:
            Dict with pain_points, selling_points, concerns, use_cases
        """
        if not comments:
            return self._default_insights()

        prompt = prompts.build_insights_prompt(comments)
        raw_response = self._call_api(prompt)
        json_response = self._extract_json_with_llm(raw_response)

        try:
            parsed = json.loads(json_response)
            return {
                "pain_points": parsed.get("pain_points") or [],
                "selling_points": parsed.get("selling_points") or [],
                "concerns": parsed.get("concerns") or [],
                "use_cases": parsed.get("use_cases") or []
            }
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON: {json_response}")
            return self._default_insights()

    def generate_comments(self, product_name: str = "", product_info: str = "") -> List[str]:
        """
        Generate realistic user comments when no comments provided

        Returns:
            List of 5 comment strings
        """
        try:
            prompt = prompts.build_comment_generation_prompt(product_name, product_info)
            raw_response = self._call_api(prompt)
            comments = [c.strip() for c in raw_response.split('\n') if c.strip()]
            return comments[:5]
        except Exception as e:
            logger.error(f"Failed to generate comments: {e}")
            return [
                "效果挺不错的",
                "价格有点贵",
                "发货速度快",
                "质量很好",
                "会回购"
            ]

    def convert_selling_points_to_comments(self, selling_points: str) -> List[str]:
        """
        Convert selling points to user-like comments

        Returns:
            List of comment strings
        """
        try:
            prompt = prompts.build_selling_points_to_comments_prompt(selling_points)
            raw_response = self._call_api(prompt)
            comments = [c.strip() for c in raw_response.split('\n') if c.strip()]
            return comments[:5]
        except Exception as e:
            logger.error(f"Failed to convert selling points: {e}")
            return [
                "确实很好用",
                "品质不错",
                "推荐购买",
                "很满意",
                "符合描述"
            ]
