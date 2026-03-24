"""
Douyin product parser using Playwright
Uses Playwright locator for precise element extraction
"""
import os
import re
import time
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Try to import playwright
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

# Try to import OCR service
try:
    from backend.ai_engine.ocr_service import get_ocr_service
    OCR_SERVICE = get_ocr_service()
except Exception as e:
    logger.warning(f"OCR service not available: {e}")
    OCR_SERVICE = None


STORAGE_FILE = "storage.json"
TIMEOUT = 15000  # 15 seconds
DEBUG_HTML_FILE = "debug.html"


def parse_douyin_product(url: str) -> Dict[str, Any]:
    """
    Parse Douyin product using Playwright with precise locator extraction

    Args:
        url: Douyin product URL

    Returns:
        Dict with name, selling_points, comments
    """
    if not PLAYWRIGHT_AVAILABLE:
        logger.warning("Playwright not installed")
        return {
            "name": "",
            "selling_points": "",
            "comments": []
        }

    print("正在使用 Playwright 抓取抖音商品...")

    try:
        with sync_playwright() as p:
            # Check if storage file exists
            storage_state = None
            if os.path.exists(STORAGE_FILE):
                storage_state = STORAGE_FILE
                print(f"使用已保存的登录状态: {STORAGE_FILE}")

            # Launch browser (headless for now, easier to debug)
            browser = p.chromium.launch(
                headless=True,
                args=['--disable-blink-features=AutomationControlled']
            )

            context = browser.new_context(
                storage_state=storage_state,
                viewport={'width': 1280, 'height': 720}
            )

            page = context.new_page()

            # If no storage, wait for user to login
            if not storage_state:
                print("请在弹出的浏览器中扫码登录抖音...")
                print("等待30秒...")
                time.sleep(30)

                # Save storage state
                context.storage_state(path=STORAGE_FILE)
                print(f"登录状态已保存到: {STORAGE_FILE}")

            # Navigate to product URL
            print(f"正在打开商品链接: {url}")
            page.goto(url, timeout=TIMEOUT, wait_until="domcontentloaded")

            # Wait for page to fully load
            page.wait_for_timeout(5000)

            # ========== Save HTML for debugging ==========
            html = page.content()
            with open(DEBUG_HTML_FILE, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"HTML已保存到: {DEBUG_HTML_FILE}")

            # ========== Use Playwright locator to extract data ==========
            result = _extract_with_locator(page)

            browser.close()

            return result

    except Exception as e:
        logger.error(f"Playwright parsing failed: {e}")
        print(f"解析失败: {e}")
        return {
            "name": "",
            "selling_points": "",
            "ocr_text": "",
            "comments": []
        }


def _extract_with_ocr(page) -> str:
    """
    Extract text from product images using OCR

    Args:
        page: Playwright page object

    Returns:
        Extracted text from images
    """
    if not OCR_SERVICE:
        print("OCR服务不可用")
        return ""

    try:
        # First, try to find images in product-big-img-list (highest priority)
        image_urls = []

        # Try product-big-img-list first
        try:
            imgs = page.locator(".product-big-img-list img")
            count = imgs.count()
            print(f"找到 product-big-img-list {count} 张图片")
            for i in range(count):
                img = imgs.nth(i)
                src = img.get_attribute("src")
                if src and (src.startswith("http") or src.startswith("//")):
                    if src.startswith("//"):
                        src = "https:" + src
                    image_urls.append(src)
        except Exception as e:
            print(f"product-big-img-list 查询失败: {e}")

        # If not found, try other selectors
        if not image_urls:
            image_selectors = [
                ".product-big-img img",
                ".goods-detail-img img",
                ".goods-image img",
                ".product-image img",
                ".preview-main img",
                ".swiper-wrapper img",
                ".swiper-slide img",
                "img[class*='goods']",
                "img[class*='product']",
                "img[class*='detail']",
                ".main-image img"
            ]

            for selector in image_selectors:
                try:
                    imgs = page.locator(selector)
                    count = imgs.count()
                    for i in range(min(count, 10)):  # Limit to 10 images
                        img = imgs.nth(i)
                        src = img.get_attribute("src")
                        if src and (src.startswith("http") or src.startswith("//")):
                            if src.startswith("//"):
                                src = "https:" + src
                            image_urls.append(src)
                except Exception:
                    continue

        if not image_urls:
            print("未找到商品图片")
            return ""

        print(f"共找到 {len(image_urls)} 张商品图片")

        # Process all images for OCR and combine results
        all_ocr_texts = []
        for i, img_url in enumerate(image_urls[:10]):  # Process up to 10 images
            try:
                ocr_text = OCR_SERVICE.extract_text_from_url(img_url)
                if ocr_text and len(ocr_text) > 2:
                    all_ocr_texts.append(ocr_text)
                    print(f"图片 {i+1} OCR: {ocr_text[:30]}...")
            except Exception as e:
                print(f"图片 {i+1} OCR失败: {e}")

        # Combine all OCR results
        combined_text = " ".join(all_ocr_texts)
        return combined_text

    except Exception as e:
        logger.error(f"OCR extraction failed: {e}")
        return ""


def _extract_with_locator(page) -> Dict[str, Any]:
    """Extract product data using Playwright locators with specific class selectors"""
    name = ""
    price = ""
    selling_points = ""
    ocr_text = ""

    try:
        page.wait_for_timeout(3000)

        # ========= 1. 标题 =========
        try:
            el = page.locator(".title-info__text").first
            if el.count() > 0:
                name = el.inner_text().strip()
                print(f"标题: {name}")
        except Exception as e:
            print(f"标题提取失败: {e}")

        # ========= 2. 价格 =========
        try:
            el = page.locator(".price-line__price_amount").first
            if el.count() > 0:
                price = el.inner_text().strip()
                print(f"价格: {price}")
        except Exception as e:
            print(f"价格提取失败: {e}")

        # ========= 3. 卖点（参数） =========
        try:
            items = page.locator(".label-process__item")
            points = []

            count = items.count()
            for i in range(count):
                item = items.nth(i)

                name_el = item.locator(".label-process__item__name")
                value_el = item.locator(".label-process__item__value")

                if name_el.count() > 0 and value_el.count() > 0:
                    key = name_el.inner_text().strip()
                    val = value_el.inner_text().strip()
                    points.append(f"{key}：{val}")

            selling_points = "，".join(points)
            print(f"卖点: {selling_points}")
        except Exception as e:
            print(f"卖点提取失败: {e}")

        # ========= 4. 商品图片 OCR =========
        try:
            ocr_text = _extract_with_ocr(page)
            if ocr_text:
                print(f"OCR文本: {ocr_text[:100]}...")
        except Exception as e:
            print(f"OCR提取失败: {e}")

        print("=" * 50)
        print(f"商品名称: {name}")
        print(f"价格: {price}")
        print(f"卖点: {selling_points}")
        print("=" * 50)

        return {
            "name": name,
            "price": price,
            "selling_points": selling_points,
            "ocr_text": ocr_text,
            "comments": []
        }

    except Exception as e:
        logger.error(f"Locator extraction failed: {e}")
        return {
            "name": "",
            "selling_points": "",
            "ocr_text": "",
            "comments": []
        }


# Keep backward compatibility
def _extract_from_html(html: str) -> Dict[str, Any]:
    """Legacy function - not used anymore"""
    return {
        "name": "",
        "selling_points": "",
        "comments": []
    }