"""
Production Service - Combine comment analysis and script generation
"""
from typing import List, Dict, Any, Optional

from backend.services.ai_service import AIService


class ProductionService:
    """Service for combining AI services"""

    def __init__(self):
        self.ai_service = AIService()

    def prepare_comments(
        self,
        product_name: str = "",
        product_info: str = "",
        selling_points: str = "",
        comments: List[str] = None
    ) -> List[str]:
        """
        Prepare and augment comments based on input

        Args:
            product_name: Product name
            product_info: Product description
            selling_points: Product selling points
            comments: Existing comments (can be empty or partial)

        Returns:
            List of at least 5 comments
        """
        if comments is None:
            comments = []

        # Case 1: No comments at all - generate from AI
        if not comments:
            if selling_points:
                # Convert selling points to comments
                comments = self.ai_service.convert_selling_points_to_comments(selling_points)
            else:
                # Generate random comments based on product info
                comments = self.ai_service.generate_comments(product_name, product_info)
            return comments[:5]

        # Case 2: Less than 3 comments - supplement to 5
        if len(comments) < 3:
            if selling_points:
                # Convert selling points and supplement
                converted = self.ai_service.convert_selling_points_to_comments(selling_points)
                comments = list(comments) + converted
            # Supplement with generated comments
            supplemental = self.ai_service.generate_comments(product_name, product_info)
            comments = list(comments) + supplemental
            return comments[:5]

        # Case 3: Has selling_points but no comments
        if selling_points and not comments:
            comments = self.ai_service.convert_selling_points_to_comments(selling_points)
            return comments[:5]

        # Already has enough comments
        return comments[:5]

    def generate_script_from_comments(self, comments: List[str]) -> Dict[str, Any]:
        """
        Generate script from comments - combines analysis and script generation

        Args:
            comments: List of comment strings

        Returns:
            Dict with opening_hook, pain_point, solution, proof, offer

        Raises:
            Exception: If any step fails
        """
        # Step 1: Analyze comments to get insights
        insights = self.ai_service.analyze_comments(comments)

        # Step 2: Generate script from insights
        script = self.ai_service.generate_script(insights)

        return script

    def generate_multi_style_scripts_from_comments(
        self,
        product_name: str = "",
        product_info: str = "",
        selling_points: str = "",
        comments: List[str] = None
    ) -> Dict[str, Any]:
        """
        Generate scripts in three different styles from comments

        Args:
            product_name: Product name
            product_info: Product description
            selling_points: Product selling points
            comments: List of comment strings (can be empty or partial)

        Returns:
            Dict with scripts array containing three styles

        Raises:
            Exception: If any step fails
        """
        # Prepare comments
        prepared_comments = self.prepare_comments(
            product_name=product_name,
            product_info=product_info,
            selling_points=selling_points,
            comments=comments
        )

        # Step 1: Analyze comments to get insights
        insights = self.ai_service.analyze_comments(prepared_comments)

        # Step 2: Generate multi-style scripts from insights
        result = self.ai_service.generate_multi_style_scripts(insights)

        return result

    def rewrite_script(self, script: Dict[str, Any], mode: str) -> Dict[str, Any]:
        """
        Rewrite script based on mode

        Args:
            script: Original script dict
            mode: One of "强化转化", "更口语", "更理性", "更简短"

        Returns:
            Dict with rewritten script content
        """
        return self.ai_service.rewrite_script(script, mode)
