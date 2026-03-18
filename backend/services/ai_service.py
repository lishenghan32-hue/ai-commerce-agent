"""
AI Service - MiniMax API integration
"""
import json
import requests
from typing import Dict, Any, List

from backend.config import settings


class AIService:
    """AI Service for comment analysis using MiniMax API"""

    def __init__(self):
        self.api_key = settings.minimax_api_key or "your-api-key-here"
        self.base_url = "https://api.minimax.chat/v1/text/chatcompletion_pro"
        self.model = "abab5.5-chat"

    def analyze_comments(self, comments: List[str]) -> Dict[str, Any]:
        """
        Analyze comments to extract pain points, selling points, and generate script
        """
        prompt = self._build_prompt(comments)

        payload = {
            "model": self.model,
            "bot_setting":[
                {
                    "bot_name":"助手",
                    "content":"你是一个电商消费者洞察分析师和直播带货话术编剧。"
                }
            ],
            "messages":[
                {
                    "sender_type":"USER",
                    "sender_name":"用户",
                    "text":prompt
                }
            ],
            "reply_constraints":{
                "sender_type":"BOT",
                "sender_name":"助手"
            },
            "temperature":0.7,
            "max_tokens":2000
        }
      
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # ✅ 请求 + JSON解析 一起包住（避免崩）
        try:
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()

        except requests.exceptions.RequestException as e:
            return {
                "pain_points": [],
                "selling_points": [],
                "script": f"请求失败: {str(e)}"
            }

        except json.JSONDecodeError as e:
            return {
                "pain_points": [],
                "selling_points": [],
                "script": f"JSON解析失败: {str(e)}"
            }

        # ✅ 打印原始返回（调试用）
        print("==== MiniMax 原始返回 ====")
        print(result)
        print("=========================")

        content = None

        # 情况1：OpenAI格式
        choices = result.get("choices")
        if isinstance(choices, list) and len(choices) > 0:
            content = choices[0].get("message", {}).get("content")

        # 情况2：MiniMax reply
        elif isinstance(result.get("reply"), str):
            raw_reply = result["reply"]
            if "```" in raw_reply:
                parts = raw_reply.split("```")
                if len(parts) >= 2:
                    content = parts[1]
                else:
                    content = raw_reply
            else:
                content = raw_reply

        # 情况3：data 结构
        elif isinstance(result.get("data"), dict):
            content = result["data"].get("reply")

        # 兜底（不报错）
        if not content:
            return {
                "pain_points": [],
                "selling_points": [],
                "script": f"AI返回异常: {result}"
            }

        return self._parse_response(content)

    def _build_prompt(self, comments: List[str]) -> str:
        """Build prompt for comment analysis"""
        comments_text = "\n".join([f"- {c}" for c in comments])

        prompt = f"""分析以下小红书评论，提取用户痛点和产品卖点，并生成直播带货话术。

评论内容：
{comments_text}

请以JSON格式返回分析结果：
{{
    "pain_points": ["痛点1", "痛点2"],
    "selling_points": ["卖点1", "卖点2"],
    "script": "直播带货话术（300-500字）"
}}

只返回JSON，不要其他内容。"""

        return prompt

    def _parse_response(self, content: str) -> Dict[str, Any]:
        """Parse JSON from AI response"""
        content = content.strip()

        # 去掉 ```json 包裹
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]

        content = content.strip()

        try:
            result = json.loads(content)
        except json.JSONDecodeError:
            return {
                "pain_points": [],
                "selling_points": [],
                "script": f"解析失败，原始内容: {content}"
            }

        # 防止 None 报错
        result["pain_points"] = result.get("pain_points") or []
        result["selling_points"] = result.get("selling_points") or []
        result["script"] = result.get("script") or ""

        return result