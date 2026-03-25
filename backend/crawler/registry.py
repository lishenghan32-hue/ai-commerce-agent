"""
Parser registry for managing platform-specific parsers
"""
from typing import Dict, List, Optional
from backend.crawler.base import BaseParser


class ParserRegistry:
    """Registry for platform-specific product parsers"""

    _parsers: Dict[str, BaseParser] = {}

    @classmethod
    def register(cls, parser: BaseParser):
        """Register a parser for a platform"""
        platform_name = parser.get_platform_name()
        cls._parsers[platform_name] = parser
        print(f"Registered parser for platform: {platform_name}")

    @classmethod
    def get_parser(cls, url: str) -> Optional[BaseParser]:
        """Get the appropriate parser for a URL"""
        for platform_name, parser in cls._parsers.items():
            if parser.can_handle(url):
                return parser
        return None

    @classmethod
    def get_parser_by_platform(cls, platform_name: str) -> Optional[BaseParser]:
        """Get parser by platform name"""
        return cls._parsers.get(platform_name)

    @classmethod
    def get_all_platforms(cls) -> List[str]:
        """Get list of all registered platforms"""
        return list(cls._parsers.keys())

    @classmethod
    def register_default_parsers(cls):
        """Register all default parsers"""
        from backend.crawler.douyin_parser import DouyinParser
        from backend.crawler.tmall_parser import TmallParser
        from backend.crawler.jd_parser import JDParser

        cls.register(DouyinParser())
        cls.register(TmallParser())
        cls.register(JDParser())
