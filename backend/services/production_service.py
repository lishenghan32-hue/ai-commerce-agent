"""
Production Service - Combine comment analysis and script generation
"""
from typing import Any, Dict, List

from backend.services.ai import get_ai_service


POSITIVE_COMMENT_KEYWORDS = [
    "舒服", "舒适", "轻", "轻便", "轻盈", "软", "柔软", "保暖", "透气", "耐穿", "百搭",
    "好看", "显瘦", "显高", "稳", "支撑", "抓地", "防滑", "满意", "喜欢", "推荐", "回购",
    "comfortable", "soft", "warm", "light", "breathable", "support", "good", "great", "love",
]

CONCERN_COMMENT_KEYWORDS = [
    "担心", "怕", "会不会", "闷", "扎", "硌", "磨脚", "硬", "重", "厚", "薄", "滑", "累",
    "压脚", "起球", "缩水", "色差", "偏大", "偏小", "显胖", "不够暖", "变形", "洗后", "耐穿",
    "耐用", "稳不稳", "支撑够不够", "itch", "scratch",
    "heavy", "hard", "slip", "tight", "loose", "expensive",
]

CONCERN_MARKERS = ["担心", "不知道", "会不会", "怕", "？", "?", "是否", "能不能"]

SCENE_COMMENT_KEYWORDS = [
    "通勤", "上班", "上学", "日常", "出街", "运动", "跑步", "健身", "户外", "露营", "爬山",
    "开车", "打底", "内搭", "居家", "换季", "秋冬", "春秋", "school", "office", "commute",
    "daily", "outdoor", "gym", "run", "layer", "home",
]


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
        - If comments >= 3: use as-is, but keep a representative mix
        """
        if comments is None:
            comments = []
        if structured is None:
            structured = {}

        comments = self._clean_comments(comments)

        if not comments or self._are_placeholder_comments(comments):
            comments = self.ai_service.generate_comments(product_name, product_info, structured)
            return self._select_representative_comments(comments, limit=10)

        if len(comments) < 3:
            supplemental = self.ai_service.generate_comments(product_name, product_info, structured)
            comments = list(comments) + supplemental
            return self._select_representative_comments(comments, limit=10)

        return self._select_representative_comments(comments, limit=10)

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

        if structured is None:
            structured = {}

        if product_url:
            ai_info = self.ai_service.extract_product_info_from_url(product_url)
            logger.info(f"URL extracted info: {ai_info}")

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

        product_context = self._build_product_context(
            product_name=product_name,
            product_info=product_info,
            selling_points=selling_points,
            structured=structured,
        )
        comment_context = self._build_comment_context(prepared_comments)
        insights = self._extract_insights_from_comments(prepared_comments)

        logger.info(f"Final product name: {product_name}")
        logger.info(f"Final selling points: {selling_points}")
        logger.info(f"Final comments: {prepared_comments}")
        logger.info(f"Built product context keys: {list(product_context.keys())}")
        logger.info(f"Built comment context keys: {list(comment_context.keys())}")

        return self.ai_service.generate_single_style_script(
            insights=insights,
            structured=structured,
            product_context=product_context,
            comment_context=comment_context,
        )

    def _build_product_context(
        self,
        product_name: str = "",
        product_info: str = "",
        selling_points: str = "",
        structured: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Build normalized product facts for prompt assembly."""
        if structured is None:
            structured = {}

        context = {
            "product_name": structured.get("title") or structured.get("product_name") or product_name,
            "product_type": structured.get("product_type", ""),
            "material": structured.get("material", ""),
            "features": self._normalize_list(structured.get("features")),
            "function": structured.get("function") or structured.get("effect") or "",
            "scene": structured.get("scene", ""),
            "applicable": structured.get("applicable") or structured.get("target") or "",
            "colors": structured.get("colors", ""),
            "season": structured.get("season", ""),
            "brief_summary": structured.get("brief_summary") or selling_points or "",
            "detailed_summary": structured.get("detailed_summary") or product_info or "",
            "selling_points": structured.get("selling_points") or selling_points or "",
            "product_info": product_info or "",
        }

        for key in [
            "thickness", "style", "ingredients", "shelf_life", "origin", "spec",
            "model", "power", "battery", "compatible", "effect", "skin_type", "usage"
        ]:
            value = structured.get(key)
            if value:
                context[key] = value

        return {
            key: value for key, value in context.items()
            if self._has_value(value)
        }

    def _build_comment_context(self, comments: List[str]) -> Dict[str, Any]:
        """Build normalized comment insights for prompt assembly."""
        raw_comments = self._clean_comments(comments)
        if not raw_comments:
            return {}

        concern_comments = [comment for comment in raw_comments if self._is_concern_comment(comment)]
        highlights = self._match_comments_by_keywords(
            [comment for comment in raw_comments if not self._is_concern_comment(comment)],
            POSITIVE_COMMENT_KEYWORDS
        )
        concerns = self._match_comments_by_keywords(raw_comments, CONCERN_COMMENT_KEYWORDS)
        scenes = self._match_comments_by_keywords(raw_comments, SCENE_COMMENT_KEYWORDS)

        if not highlights:
            highlights = [comment for comment in raw_comments if not self._is_concern_comment(comment)][:3]
        if not concerns:
            concerns = concern_comments[:3]
        else:
            concerns = self._dedupe_preserve_order(concerns + concern_comments)[:3]

        return {
            "highlights": highlights[:3],
            "concerns": concerns[:3],
            "scenes": scenes[:3],
            "sample_quotes": raw_comments[:4],
            "raw_comments": raw_comments[:10],
        }

    def _extract_insights_from_comments(self, comments: List[str]) -> Dict[str, Any]:
        """Keep legacy insights available while using richer comment context."""
        comment_context = self._build_comment_context(comments)
        if not comment_context:
            return {}

        return {
            "pain_points": comment_context.get("concerns", []),
            "selling_points": comment_context.get("highlights", []),
            "concerns": comment_context.get("concerns", []),
            "use_cases": comment_context.get("scenes", []),
            "sample_quotes": comment_context.get("sample_quotes", []),
        }

    def _match_comments_by_keywords(self, comments: List[str], keywords: List[str], limit: int = 3) -> List[str]:
        matches = []
        for comment in comments:
            lowered = comment.lower()
            if any(keyword.lower() in lowered for keyword in keywords):
                matches.append(comment)
            if len(matches) >= limit:
                break
        return self._dedupe_preserve_order(matches)[:limit]

    def _normalize_list(self, value: Any) -> List[str]:
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        if isinstance(value, str) and value.strip():
            return [value.strip()]
        return []

    def _clean_comments(self, comments: List[str]) -> List[str]:
        cleaned = [comment.strip() for comment in comments or [] if comment and comment.strip()]
        return self._dedupe_preserve_order(cleaned)

    def _select_representative_comments(self, comments: List[str], limit: int = 10) -> List[str]:
        cleaned = self._clean_comments(comments)
        if len(cleaned) <= limit:
            return cleaned

        concern_comments = [comment for comment in cleaned if self._is_concern_comment(comment)]
        scene_comments = self._match_comments_by_keywords(cleaned, SCENE_COMMENT_KEYWORDS, limit=limit)
        highlight_comments = self._match_comments_by_keywords(
            [comment for comment in cleaned if not self._is_concern_comment(comment)],
            POSITIVE_COMMENT_KEYWORDS,
            limit=limit,
        )

        must_keep = self._dedupe_preserve_order(
            concern_comments[:4] + scene_comments[:3] + highlight_comments[:4]
        )
        return self._dedupe_preserve_order(must_keep + cleaned)[:limit]

    def _are_placeholder_comments(self, comments: List[str]) -> bool:
        normalized = [comment.strip() for comment in comments if comment and comment.strip()]
        if not normalized:
            return False

        placeholders = {"质量不错", "性价比高", "值得购买"}
        return set(normalized).issubset(placeholders)

    def _is_concern_comment(self, comment: str) -> bool:
        lowered = comment.lower()
        return any(marker.lower() in lowered for marker in CONCERN_MARKERS) or any(
            keyword.lower() in lowered for keyword in CONCERN_COMMENT_KEYWORDS
        )

    def _dedupe_preserve_order(self, values: List[str]) -> List[str]:
        seen = set()
        output = []
        for value in values:
            if value not in seen:
                seen.add(value)
                output.append(value)
        return output

    def _has_value(self, value: Any) -> bool:
        if value is None:
            return False
        if isinstance(value, str):
            return bool(value.strip())
        if isinstance(value, list):
            return any(self._has_value(item) for item in value)
        return bool(value)

    def rewrite_script(self, script: Dict[str, Any], mode: str) -> Dict[str, Any]:
        """
        Rewrite script based on mode
        """
        return self.ai_service.rewrite_script(script, mode)
