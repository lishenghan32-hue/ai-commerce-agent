"""
JD/京东 product parser
"""
import logging

logger = logging.getLogger(__name__)


class JDParser:
    """JD/京东 product parser"""

    def get_platform_name(self) -> str:
        return "jd"

    def get_url_patterns(self) -> list:
        return [
            "item.jd.com",
            "item.m.jd.com",
            "jd.com"
        ]

    def extract_name(self, page) -> str:
        """Extract product name from JD page"""
        try:
            # Main product name
            el = page.locator(".sku-name").first
            if el.count() > 0:
                return el.inner_text().strip()
        except Exception:
            pass

        try:
            # Alternative
            el = page.locator(".item-title").first
            if el.count() > 0:
                return el.inner_text().strip()
        except Exception:
            pass

        try:
            # Another alternative - head title
            el = page.locator("div.head-title").first
            if el.count() > 0:
                return el.inner_text().strip()
        except Exception:
            pass

        return ""

    def extract_selling_points(self, page) -> str:
        """Extract selling points from JD page"""
        points = []

        try:
            # Product specifications
            items = page.locator(".p-params li, .parameter2 li")
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
                # Try alternative selector
                items = page.locator(".spec-list li, .product-detail li")
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
        """Extract product images from JD page"""
        image_urls = []

        # Main image
        try:
            imgs = page.locator("#spec-img, .img-mark")
            count = imgs.count()
            for i in range(count):
                img = imgs.nth(i)
                src = img.get_attribute("src") or img.get_attribute("data-src")
                if src:
                    if src.startswith("//"):
                        src = "https:" + src
                    if src.startswith("http"):
                        image_urls.append(src)
        except Exception:
            pass

        if not image_urls:
            try:
                # Thumbnail gallery
                imgs = page.locator(".thumb-list img, .spec-items img")
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
