"""
Douyin product parser using Playwright
"""
import os
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

# Try to import BeautifulSoup, fallback to html.parser
try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    try:
        from html.parser import HTMLParser
        BS4_AVAILABLE = False
    except ImportError:
        BS4_AVAILABLE = False


STORAGE_FILE = "storage.json"
TIMEOUT = 15000  # 15 seconds


def parse_douyin_product(url: str) -> Dict[str, Any]:
    """
    Parse Douyin product using Playwright

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

            # Launch browser (visible, not headless)
            browser = p.chromium.launch(
                headless=False,
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

            # Wait for page to load
            page.wait_for_timeout(5000)

            # Get HTML content
            html = page.content()
            print(f"HTML长度: {len(html)}")

            # Extract data using BeautifulSoup
            result = _extract_from_html(html)

            browser.close()

            return result

    except Exception as e:
        logger.error(f"Playwright parsing failed: {e}")
        print(f"解析失败: {e}")
        return {
            "name": "",
            "selling_points": "",
            "comments": []
        }


def _extract_from_html(html: str) -> Dict[str, Any]:
    """Extract product info from HTML"""
    name = ""
    selling_points = ""

    try:
        if BS4_AVAILABLE:
            # Use BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')

            # Extract title
            og_title = soup.find("meta", property="og:title")
            if og_title and og_title.get("content"):
                name = og_title["content"].strip()

            if not name:
                title = soup.find("title")
                if title:
                    name = title.get_text().strip()
                    name = name.split('|')[0].split('-')[0].strip()

            if not name:
                h1 = soup.find("h1")
                if h1:
                    name = h1.get_text().strip()

            body = soup.find("body")
            if body:
                text = body.get_text()
                text = ' '.join(text.split())
                selling_points = text[:500]
        else:
            # Use built-in html.parser and regex
            import re

            # Try to find product name from title tag
            title_match = re.search(r'<title[^>]*>([^<]*)</title>', html, re.I)
            if title_match and title_match.group(1).strip():
                name = title_match.group(1).strip()
                # Clean up common suffixes
                name = re.split(r'[\|\-\–\-]', name)[0].strip()

            # Try og:title
            if not name:
                og_title_match = re.search(r'<meta[^>]*property=[\'"]og:title[\'"][^>]*content=[\'"]([^\'"]*)', html, re.I)
                if og_title_match:
                    name = og_title_match.group(1).strip()

            # If still no name, get it from body text (for dynamic pages like Jinritemai)
            if not name or name in ["打开抖音APP", ""]:
                # Get page text content
                body_match = re.search(r'<body[^>]*>([\s\S]*?)</body>', html, re.I)
                if body_match:
                    body_text = re.sub(r'<[^>]+>', ' ', body_match.group(1))
                    body_text = ' '.join(body_text.split())

                    # Split by common separators and look for product name
                    # Product names in this page appear after \"起 \" or price patterns
                    import re
                    # Look for text between price and specs
                    patterns = [
                        r'起\s+([^\n]{15,50})(?:[\s\n]+(?:适用|面料|尺码|年龄|性别|保障))',  # After price \"起\"
                        r'[\n\r]([^\n\r]{15,50})(?:适用年龄|面料材质|适用性别|A类)',  # Before specs
                        r'([^\n]{20,50})(?:6-12岁|适用年龄|莫代尔|A类)',  # Contains specs
                    ]
                    for pattern in patterns:
                        match = re.search(pattern, body_text)
                        if match:
                            candidate = match.group(1).strip()
                            # Validate it's a product name (not too short, contains Chinese chars)
                            if len(candidate) >= 15 and re.search(r'[\u4e00-\u9fff]', candidate):
                                # Clean up trailing specs like "6-12岁 适用年龄 男"
                                candidate = re.sub(r'\s+(?:6-12岁|适用年龄|适用性别|面料材质|A类|莫代尔)\s*\w*\s*$', '', candidate)
                                name = candidate.strip()
                                break

                    # Fallback: find longest text segment
                    if not name:
                        # Split by common delimiters
                        import re
                        parts = re.split(r'[\s]{2,}', body_text)
                        for part in parts:
                            part = part.strip()
                            # Skip short lines and common UI elements
                            if len(part) >= 15 and not any(skip in part for skip in ['打开抖音', '立即打开', '购物车', '客服', '商品评价', '店铺']):
                                if re.search(r'[\u4e00-\u9fff]', part):  # Has Chinese
                                    name = part
                                    break

            # Get body text for selling points
            body_match = re.search(r'<body[^>]*>([\s\S]*?)</body>', html, re.I)
            if body_match:
                body_text = re.sub(r'<[^>]+>', ' ', body_match.group(1))
                body_text = ' '.join(body_text.split())
                # Clean up: remove app banner patterns more carefully
                # Pattern: \"打开抖音APP\" followed by some text, then \"立即打开\"
                body_text = re.sub(r'打开抖音APP\s*购物实惠又有趣\s*立即打开\s*', '', body_text)
                # Remove price line like \"1/5\" or \"1/3\"
                body_text = re.sub(r'\d+/\d+\s*', '', body_text)
                # Remove leading price indicator
                body_text = re.sub(r'^[￥\$¥]\s*\d+\??\s*起\s*', '', body_text)
                # Get a reasonable portion
                if len(body_text.strip()) > 0:
                    # Remove JavaScript fragments
                    body_text = re.sub(r'!function\(\).*$', '', body_text)
                    body_text = re.sub(r'Hi,.*前往抖音APP.*$', '', body_text)
                    selling_points = body_text[:600].strip()

        return {
            "name": name,
            "selling_points": selling_points,
            "comments": []  # Comments will be generated by AI
        }

    except Exception as e:
        logger.error(f"HTML extraction failed: {e}")
        return {
            "name": "",
            "selling_points": "",
            "comments": []
        }
