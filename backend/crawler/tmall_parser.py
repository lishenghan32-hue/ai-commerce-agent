"""
Tmall/淘宝 product parser
"""
import logging

logger = logging.getLogger(__name__)


class TmallParser:
    """Tmall/淘宝 product parser"""

    def get_platform_name(self) -> str:
        return "tmall"

    def get_url_patterns(self) -> list:
        return [
            "detail.tmall.com",
            "detail.tmall.hk",
            "world.tmall.com",
            "taobao.com"
        ]

    def extract_name(self, page) -> str:
        """Extract product name from Tmall page"""
        try:
            # Try main title
            el = page.locator(".tb-detail-hd h1").first
            if el.count() > 0:
                return el.inner_text().strip()
        except Exception:
            pass

        try:
            # Alternative selector
            el = page.locator(".mod-name").first
            if el.count() > 0:
                return el.inner_text().strip()
        except Exception:
            pass

        try:
            # Another alternative
            el = page.locator("h1[class*='title']").first
            if el.count() > 0:
                return el.inner_text().strip()
        except Exception:
            pass

        return ""

    def extract_selling_points(self, page) -> str:
        """Extract selling points from Tmall page"""
        points = []

        try:
            # Try properties list
            items = page.locator(".tb-attr-new-list li, .attributes-list li")
            count = items.count()
            for i in range(min(count, 10)):
                item = items.nth(i)
                text = item.inner_text().strip()
                if text:
                    points.append(text)
        except Exception:
            pass

        if not points:
            try:
                # Try alternative
                items = page.locator(".property-list li, .p-attributes li")
                count = items.count()
                for i in range(min(count, 10)):
                    item = items.nth(i)
                    text = item.inner_text().strip()
                    if text:
                        points.append(text)
            except Exception:
                pass

        return "，".join(points) if points else ""

    def extract_images(self, page) -> list:
        """Extract product images from Tmall page"""
        image_urls = []

        # Try main image
        try:
            imgs = page.locator("#main-img, .tb-main-img")
            count = imgs.count()
            for i in range(count):
                img = imgs.nth(i)
                src = img.get_attribute("src") or img.get_attribute("data-src")
                if src:
                    if src.startswith("//"):
                        src = "https:" + src
                    if src.startswith("/"):
                        src = "https:" + src
                    if src.startswith("http"):
                        image_urls.append(src)
        except Exception:
            pass

        if not image_urls:
            try:
                # Try thumbnail gallery
                imgs = page.locator(".tb-thumb img, .gallery-thumb img")
                count = imgs.count()
                for i in range(min(count, 10)):
                    img = imgs.nth(i)
                    src = img.get_attribute("src") or img.get_attribute("data-src")
                    if src:
                        if src.startswith("//"):
                            src = "https:" + src
                        if src.startswith("http"):
                            image_urls.append(src)
            except Exception:
                pass

        # Remove duplicates
        seen = set()
        unique_images = []
        for url in image_urls:
            if url not in seen:
                seen.add(url)
                unique_images.append(url)

        return unique_images
