"""
Base parser interface for multi-platform product parsing
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional


class BaseParser(ABC):
    """Base class for platform-specific product parsers"""

    @abstractmethod
    def get_platform_name(self) -> str:
        """Return platform name (e.g., 'douyin', 'tmall', 'jd')"""
        pass

    @abstractmethod
    def get_url_patterns(self) -> List[str]:
        """Return list of URL patterns this parser can handle"""
        pass

    @abstractmethod
    def extract_name(self, page) -> str:
        """Extract product name from page"""
        pass

    @abstractmethod
    def extract_selling_points(self, page) -> str:
        """Extract selling points from page"""
        pass

    @abstractmethod
    def extract_images(self, page) -> List[str]:
        """Extract product image URLs from page"""
        pass

    def can_handle(self, url: str) -> bool:
        """Check if this parser can handle the given URL"""
        for pattern in self.get_url_patterns():
            if pattern in url.lower():
                return True
        return False

    def parse(self, page) -> Dict:
        """
        Parse product information from page.
        Returns a dict with name, selling_points, images.
        """
        return {
            "name": self.extract_name(page),
            "selling_points": self.extract_selling_points(page),
            "images": self.extract_images(page)
        }
