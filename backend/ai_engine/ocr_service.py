"""
OCR Service - Image text recognition for product images
Supports PaddleOCR, EasyOCR, and online OCR APIs as fallback
"""
import base64
import io
import json
import logging
import re
import urllib.request
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

# Try to import PaddleOCR
PADDLEOCR_AVAILABLE = False
PADDLEOCR_TESTED = False  # Whether we've tested it works
try:
    from paddleocr import PaddleOCR
    PADDLEOCR_AVAILABLE = True
    PADDLEOCR_TESTED = True  # It's loadable, even if recognition may have issues
    _paddle_ocr = None
    def get_paddle_ocr():
        global _paddle_ocr
        if _paddle_ocr is None:
            _paddle_ocr = PaddleOCR(use_angle_cls=False, lang='ch', show_log=False)
        return _paddle_ocr
except ImportError as e:
    logger.warning(f"PaddleOCR not available: {e}")

# Try to import EasyOCR (may fail due to PyTorch issues)
EASYOCR_AVAILABLE = False
try:
    import easyocr
    EASYOCR_AVAILABLE = True
    _easyocr_reader = None
    def get_easyocr_reader():
        global _easyocr_reader
        if _easyocr_reader is None:
            _easyocr_reader = easyocr.Reader(['ch', 'en'], gpu=False, verbose=False)
        return _easyocr_reader
except Exception as e:
    logger.warning(f"EasyOCR not available: {e}")


class OCRService:
    """OCR Service for extracting text from product images"""

    def __init__(self):
        self.paddle_available = PADDLEOCR_AVAILABLE
        self.easyocr_available = EASYOCR_AVAILABLE
        print(f"OCR Service initialized: PaddleOCR={PADDLEOCR_AVAILABLE}, EasyOCR={EASYOCR_AVAILABLE}")

    def extract_text_from_url(self, image_url: str) -> str:
        """
        Extract text from an image URL

        Args:
            image_url: URL of the image to process

        Returns:
            Extracted text as string
        """
        if not image_url:
            return ""

        try:
            logger.info(f"[OCR] 开始处理图片: {image_url[:80]}...")
            # Download image
            req = urllib.request.Request(
                image_url,
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            with urllib.request.urlopen(req, timeout=15) as response:
                image_data = response.read()
            logger.info(f"[OCR] 图片下载成功，大小: {len(image_data)} bytes")

            result = self.extract_text_from_bytes(image_data)
            logger.info(f"[OCR] 识别结果: {result[:200] if result else '(空)'}")
            return result

        except Exception as e:
            logger.error(f"[OCR] 提取文字失败 {image_url[:50]}: {e}")
            return ""

    def extract_text_from_bytes(self, image_bytes: bytes) -> str:
        """
        Extract text from image bytes

        Args:
            image_bytes: Raw image data

        Returns:
            Extracted text as string
        """
        if not image_bytes:
            return ""

        # Try PaddleOCR first (if properly configured)
        if self.paddle_available:
            try:
                ocr = get_paddle_ocr()
                result = ocr.ocr(image_bytes, cls=False)

                if result and result[0]:
                    texts = []
                    for line in result[0]:
                        if line and len(line) >= 2:
                            text = line[1][0]
                            logger.info(f"[OCR] 识别到文字: {text}")
                            # Filter out garbage results - keep meaningful text
                            if text and len(text.strip()) > 0:
                                texts.append(text)
                    if texts:
                        result_text = " ".join(texts)
                        logger.info(f"[OCR] 最终结果: {result_text}")
                        return result_text
            except Exception as e:
                logger.error(f"PaddleOCR failed: {e}")

        # Try EasyOCR as fallback
        if self.easyocr_available:
            try:
                import numpy as np
                from PIL import Image
                reader = get_easyocr_reader()
                # Convert bytes to numpy array
                img = Image.open(io.BytesIO(image_bytes))
                img_array = np.array(img)
                result = reader.readtext(img_array)
                if result:
                    texts = [item[1] for item in result]
                    return " ".join(texts)
            except Exception as e:
                logger.error(f"EasyOCR failed: {e}")

        # Try online OCR API as final fallback
        try:
            return self._online_ocr(image_bytes)
        except Exception as e:
            logger.error(f"Online OCR failed: {e}")

        return ""

    def _online_ocr(self, image_bytes: bytes) -> str:
        """
        Use free online OCR API as fallback
        Using ocr.space free API
        """
        try:
            # Encode image to base64
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')

            # Use ocr.space API (free tier: 25,000 requests/month)
            # Note: For production, use your own API key
            url = "https://api.ocr.space/parse/image"
            data = {
                "base64Image": f"data:image/png;base64,{image_base64}",
                "language": "chs",  # Chinese Simplified
                "isOverlayRequired": False,
                "detectOrientation": True,
                "scale": True,
                "OCREngine": 2,  # More accurate engine
            }

            # Use anonymous (rate-limited) or your own API key
            # For now, try without key first (limited)
            headers = {
                "Content-Type": "application/json"
            }

            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode('utf-8'),
                headers=headers,
                method="POST"
            )

            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))

            if result.get("ParsedResults"):
                texts = []
                for parsed in result["ParsedResults"]:
                    text = parsed.get("ParsedText", "").strip()
                    if text:
                        texts.append(text)
                return " ".join(texts)

        except Exception as e:
            logger.error(f"ocr.space API error: {e}")

        return ""

    def extract_selling_points_from_image(self, image_url: str) -> List[str]:
        """
        Extract selling points from product image

        Args:
            image_url: URL of product image

        Returns:
            List of selling points
        """
        text = self.extract_text_from_url(image_url)

        if not text:
            return []

        # Clean and parse the text
        points = []
        lines = re.split(r'[，。、\n]', text)
        for line in lines:
            line = line.strip()
            if line and len(line) > 2:
                points.append(line)

        return points


# Singleton instance
_ocr_service = None

def get_ocr_service() -> OCRService:
    """Get or create OCR service instance"""
    global _ocr_service
    if _ocr_service is None:
        _ocr_service = OCRService()
    return _ocr_service
