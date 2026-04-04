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
        comments: List[str] = None,
        structured: Dict[str, Any] = None
    ) -> List[str]:
        """
        Prepare and augment comments based on input.
        Strategy:
        - If no comments provided: generate from product info
        - If comments < 3: supplement with generated comments
        - If comments >= 3: use as-is, truncate to 5
        """
        if comments is None:
            comments = []
        if structured is None:
            structured = {}

        # Case 1: No comments - generate from product info
        if not comments:
            comments = self.ai_service.generate_comments(product_name, product_info, structured)
            return comments[:10]

        # Case 2: Has comments but less than 3 - supplement
        if len(comments) < 3:
            supplemental = self.ai_service.generate_comments(product_name, product_info, structured)
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
            comments=comments,
            structured=structured
        )

        logger.info(f"最终商品名: {product_name}")
        logger.info(f"最终卖点: {selling_points}")
        logger.info(f"最终评论: {prepared_comments}")

        # 从评论中提取 insights（简单的关键词提取作为洞察）
        insights = self._extract_insights_from_comments(prepared_comments)

        # 融合 structured 和 insights 生成话术
        return self.ai_service.generate_single_style_script(
            insights=insights,
            structured=structured
        )

    def _extract_insights_from_comments(self, comments: List[str]) -> Dict[str, Any]:
        """
        从评论中提取洞察，同时保留原始评论供话术融入
        """
        if not comments:
            return {}

        # 简单的关键词统计和情感倾向判断
        pain_keywords = []
        positive_keywords = []
        negative_keywords = []

        pain_words = ['贵', '慢', '差', '不好', '失望', '坑', '后悔', '难', '不舒服', '小', '褪色', '起球']
        positive_words = ['好', '不错', '喜欢', '满意', '推荐', '回购', '快', '漂亮', '舒服', '值', '赞']
        negative_words = ['贵', '慢', '差', '失望', '后悔', '不值', '麻烦']

        all_text = ' '.join(comments)

        for word in pain_words:
            if word in all_text:
                pain_keywords.append(word)
        for word in positive_words:
            if word in all_text:
                positive_keywords.append(word)
        for word in negative_words:
            if word in all_text:
                negative_keywords.append(word)

        return {
            "pain_points": list(set(pain_keywords))[:5],
            "selling_points": list(set(positive_keywords))[:5],
            "concerns": list(set(negative_keywords))[:3],
            "use_cases": [],
            "original_comments": comments[:5]  # 保留原始评论供话术融入
        }

    def rewrite_script(self, script: Dict[str, Any], mode: str) -> Dict[str, Any]:
        """
        Rewrite script based on mode
        """
        return self.ai_service.rewrite_script(script, mode)
