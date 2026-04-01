"""
Production Service - Combine comment analysis and script generation
"""
from typing import List, Dict, Any

from backend.services.ai import get_ai_service


class ProductionService:
    """Service for combining AI services"""

    def __init__(self):
        self.ai_service = get_ai_service()

    def prepare_comments(
        self,
        product_name: str = "",
        product_info: str = "",
        selling_points: str = "",
        comments: List[str] = None
    ) -> List[str]:
        """
        Prepare and augment comments based on input.
        Strategy:
        - If no comments provided: generate from selling_points or product info
        - If comments < 3: supplement with generated comments to reach 3-5
        - If comments >= 3: use as-is, truncate to 5
        """
        if comments is None:
            comments = []

        # Case 1: No comments - generate from selling_points or product info
        if not comments:
            if selling_points:
                comments = self.ai_service.convert_selling_points_to_comments(selling_points)
            else:
                comments = self.ai_service.generate_comments(product_name, product_info)
            return comments[:10]

        # Case 2: Has comments but less than 3 - supplement
        if len(comments) < 3:
            supplemental = []
            if selling_points:
                supplemental.extend(self.ai_service.convert_selling_points_to_comments(selling_points))
            supplemental.extend(self.ai_service.generate_comments(product_name, product_info))
            comments = list(comments) + supplemental
            return comments[:10]

        # Case 3: Already has 3+ comments - use as-is
        return comments[:5]

    def generate_script_from_comments(
        self,
        product_url: str = "",
        product_name: str = "",
        product_info: str = "",
        selling_points: str = "",
        comments: List[str] = None,
        structured: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Generate a single script from comments and product context
        """
        import logging
        logger = logging.getLogger(__name__)

        if product_url:
            ai_info = self.ai_service.extract_product_info_from_url(product_url)
            logger.info(f"URL提取信息: {ai_info}")

            if not product_name:
                product_name = ai_info.get("product_name", "")

            if not selling_points:
                selling_points = ", ".join(ai_info.get("selling_points", []))

            if not comments or len(comments) < 3:
                ai_comments = ai_info.get("comments", [])
                if ai_comments:
                    comments = list(comments) + ai_comments if comments else ai_comments

        prepared_comments = self.prepare_comments(
            product_name=product_name,
            product_info=product_info,
            selling_points=selling_points,
            comments=comments
        )

        logger.info(f"最终商品名: {product_name}")
        logger.info(f"最终卖点: {selling_points}")
        logger.info(f"最终评论: {prepared_comments}")

        if not prepared_comments:
            prepared_comments = self.ai_service.generate_comments(product_name, product_info)

        insights = self.ai_service.analyze_comments(prepared_comments)
        return self.ai_service.generate_single_style_script(insights, structured=structured)

    def rewrite_script(self, script: Dict[str, Any], mode: str) -> Dict[str, Any]:
        """
        Rewrite script based on mode
        """
        return self.ai_service.rewrite_script(script, mode)
