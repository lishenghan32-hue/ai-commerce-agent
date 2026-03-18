"""
Production Service - Combine comment analysis and script generation
"""
from typing import List, Dict, Any

from backend.services.ai_service import AIService


class ProductionService:
    """Service for combining AI services"""

    def __init__(self):
        self.ai_service = AIService()

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
