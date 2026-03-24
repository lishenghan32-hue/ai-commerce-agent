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
            "comments": []
        }


def _extract_with_locator(page) -> Dict[str, Any]:
    """
    Extract product data using Playwright locators
    """
    name = ""
    price = ""
    selling_points = ""

    try:
        # Wait for dynamic content to load
        page.wait_for_timeout(3000)

        # ========== 1. 商品标题 ==========
        # The product name is in the page text - find it by pattern
        try:
            body_text = page.inner_text("body")

            # Find product name pattern - look for text after price "起"
            # Pattern: "起" followed by product name, then specs like "6-12岁"
            patterns = [
                r'起\s+([^\n]{10,50}?)(?:\s+(?:6-12岁|适用年龄|适用性别|面料材质|A类|莫代尔|岁|件|条))',
                r'[\n\r]([^\n\r]{15,50})(?:适用年龄|面料材质|适用性别|A类|莫代尔)',
                r'([^\n]{20,50})(?:6-12岁|适用年龄|莫代尔|A类)',
            ]

            for pattern in patterns:
                match = re.search(pattern, body_text)
                if match:
                    candidate = match.group(1).strip()
                    # Clean up trailing specs
                    candidate = re.sub(r'\s+(?:6-12岁|适用年龄|适用性别|面料材质|A类|莫代尔)\s*\w*\s*$', '', candidate)
                    if len(candidate) >= 10:
                        name = candidate.strip()
                        print(f"标题: {name}")
                        break
        except Exception as e:
            print(f"标题提取失败: {e}")

        # ========== 2. 价格 ==========
        try:
            body_text = page.inner_text("body")
            # Find price - look for patterns like "¥39" or "￥39.9 起"
            price_patterns = [
                r'[¥￥]\s*(\d+\.?\d*)',
                r'¥(\d+\.?\d*)',
                r'(\d+\.?\d*)\s*起',
            ]
            for pattern in price_patterns:
                matches = re.findall(pattern, body_text)
                if matches:
                    price = matches[0]
                    print(f"价格: ¥{price}")
                    break
        except Exception as e:
            print(f"价格提取失败: {e}")

        # ========== 3. 卖点 ==========
        # Get body text and clean it
        try:
            body_text = page.inner_text("body")

            # Clean up common UI elements - more aggressive cleaning
            # Remove app banner and opening text
            body_text = re.sub(r'打开抖音APP\s*购物实惠又有趣\s*立即打开\s*', '', body_text)
            # Remove pagination like "1/5"
            body_text = re.sub(r'\d+/\d+\s*', '', body_text)
            # Remove price indicators (¥39.9 起 etc)
            body_text = re.sub(r'[¥￥$]\s*\d+\??\s*起\s*', '', body_text)
            # Remove JS fragments
            body_text = re.sub(r'!function\(\).*', '', body_text)
            body_text = re.sub(r'Hi,.*前往抖音APP.*', '', body_text)

            # Remove common UI text - more patterns
            ui_patterns = [
                '去抢购', '加入购物车', '购物车', '店铺', '客服',
                '商品评价', '店铺评分', '销量', '配送', '支付',
                '立即购买', '看相似', '联系客服', '进店逛逛',
                '产品参数', '品牌', '面料材质', '适用性别',
                '安全等级', '更多详细参数', '价格说明', '销量说明',
                '协议', '前往抖音APP', '可查看完整价格', '去抖音APP'
            ]
            for pattern in ui_patterns:
                body_text = body_text.replace(pattern, '')

            # Remove evaluation keywords
            eval_patterns = ['回头客', '尺码合适', '非常舒服', '穿着很舒适', '面料柔软', '品质非常好', '轻薄']
            for pattern in eval_patterns:
                body_text = body_text.replace(pattern, '')

            # Clean up extra spaces
            body_text = ' '.join(body_text.split())

            # Get meaningful text after product name
            # Find product name and get text after it
            if name and name in body_text:
                idx = body_text.find(name)
                if idx >= 0:
                    # Get text after product name
                    body_text = body_text[idx + len(name):]

            # Get first 200 chars as selling points
            selling_points = body_text[:200].strip()

            print(f"卖点 (前100字): {selling_points[:100]}")

        except Exception as e:
            print(f"卖点提取失败: {e}")

        # Debug: Print all extracted data
        print("=" * 50)
        print(f"商品名称: {name}")
        print(f"价格: {price}")
        print(f"卖点: {selling_points[:100]}...")
        print("=" * 50)

        return {
            "name": name,
            "price": price,
            "selling_points": selling_points,
            "comments": []  # Comments will be generated by AI
        }

    except Exception as e:
        logger.error(f"Locator extraction failed: {e}")
        print(f"提取失败: {e}")
        return {
            "name": "",
            "selling_points": "",
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