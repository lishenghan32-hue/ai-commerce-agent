"""
AI Base - Singleton and core methods
"""
import json
import logging
import requests
from typing import Dict, Any, List

from backend.config import settings

logger = logging.getLogger(__name__)


class BaseAIService:
    """AI Service base class with core functionality"""

    def __init__(self):
        self.api_key = settings.minimax_api_key or "your-api-key-here"
        self.base_url = "https://api.minimax.chat/v1/text/chatcompletion_pro"
        self.model = "abab5.5-chat"

    # ==================== Core API Methods ====================

    def _call_api(self, prompt: str, max_retries: int = 3) -> str:
        """Call MiniMax API with retry logic"""
        payload = {
            "model": self.model,
            "bot_setting": [
                {
                    "bot_name": "助手",
                    "content": "你是一个电商消费者洞察分析师。请严格按照JSON格式返回,不要返回任何解释文字。"
                }
            ],
            "messages": [
                {
                    "sender_type": "USER",
                    "sender_name": "用户",
                    "text": prompt
                }
            ],
            "reply_constraints": {
                "sender_type": "BOT",
                "sender_name": "助手"
            },
            "temperature": 0.3,
            "max_tokens": 2000
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        last_error = None
        for attempt in range(max_retries):
            try:
                session = requests.Session()
                session.trust_env = False
                response = session.post(
                    self.base_url,
                    headers=headers,
                    json=payload,
                    timeout=30,
                    verify=True
                )
                response.raise_for_status()
                result = response.json()

                content = self._extract_content(result)
                return content

            except requests.exceptions.RequestException as e:
                last_error = e
                logger.warning(f"MiniMax API request failed (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(1 + attempt)

        logger.error(f"MiniMax API request failed after {max_retries} attempts")
        raise Exception(f"AI API 请求失败 (已重试 {max_retries} 次): {str(last_error)}")

    def _extract_json_with_llm(self, raw_response: str) -> str:
        """Extract valid JSON with fallback"""
        # Try direct parse first
        json_content = raw_response.strip()
        if json_content.startswith("```json"):
            json_content = json_content[7:]
        elif json_content.startswith("```"):
            json_content = json_content[3:]
        if json_content.endswith("```"):
            json_content = json_content[:-3]
        json_content = json_content.strip()

        try:
            json.loads(json_content)
            return json_content
        except json.JSONDecodeError:
            pass

        # Try LLM extraction
        extract_prompt = f"""从以下文本中提取出有效的JSON,不要返回任何解释文字。

文本：
{raw_response}

直接返回JSON,不要其他内容。"""

        try:
            json_content = self._call_api(extract_prompt)
            json_content = json_content.strip()
            if json_content.startswith("```json"):
                json_content = json_content[7:]
            elif json_content.startswith("```"):
                json_content = json_content[3:]
            if json_content.endswith("```"):
                json_content = json_content[:-3]
            return json_content.strip()
        except Exception as e:
            logger.error(f"Failed to extract JSON with LLM: {e}")
            return '{"error": "parse_failed"}'

    def _extract_content(self, result: Dict[str, Any]) -> str:
        """Extract content from various API response formats"""
        # OpenAI format
        choices = result.get("choices")
        if isinstance(choices, list) and len(choices) > 0:
            content = choices[0].get("message", {}).get("content")
            if content:
                return content

        # MiniMax reply format
        if isinstance(result.get("reply"), str):
            return result["reply"]

        # data structure
        if isinstance(result.get("data"), dict):
            reply = result["data"].get("reply")
            if isinstance(reply, str):
                return reply

        return ""

    # ==================== Default Values ====================

    def _default_insights(self) -> Dict[str, Any]:
        return {
            "pain_points": [],
            "selling_points": [],
            "concerns": [],
            "use_cases": []
        }

    def _default_script(self) -> Dict[str, Any]:
        return {
            "opening_hook": "",
            "pain_point": "",
            "solution": "",
            "proof": "",
            "offer": ""
        }

# ==================== Import Mixins ====================
# Import at bottom to avoid circular imports
from backend.services.ai.comment import AIServiceCommentMixin
from backend.services.ai.script import AIServiceScriptMixin
from backend.services.ai.product import AIServiceProductMixin


class AIService(AIServiceCommentMixin, AIServiceScriptMixin, AIServiceProductMixin, BaseAIService):
    """Combined AI Service with all capabilities"""
    pass
