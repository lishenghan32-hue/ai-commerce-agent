"""
AI Service - MiniMax API integration
"""
import json
import logging
import requests
from typing import Dict, Any, List

from backend.config import settings

logger = logging.getLogger(__name__)


class AIService:
    """AI Service for comment analysis and script generation using MiniMax API"""

    def __init__(self):
        self.api_key = settings.minimax_api_key or "your-api-key-here"
        self.base_url = "https://api.minimax.chat/v1/text/chatcompletion_pro"
        self.model = "abab5.5-chat"

    def analyze_comments(self, comments: List[str]) -> Dict[str, Any]:
        """
        Analyze comments to extract user insights using LLM

        Returns:
            Dict with pain_points, selling_points, concerns, use_cases
        """
        if not comments:
            return self._default_insights()

        # Step 1: Get analysis from LLM
        prompt = self._build_insights_prompt(comments)
        raw_response = self._call_api(prompt)

        # Step 2: Use LLM to extract valid JSON from the response
        json_response = self._extract_json_with_llm(raw_response)

        # Step 3: Parse and return
        try:
            parsed = json.loads(json_response)
            return {
                "pain_points": parsed.get("pain_points") or [],
                "selling_points": parsed.get("selling_points") or [],
                "concerns": parsed.get("concerns") or [],
                "use_cases": parsed.get("use_cases") or []
            }
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON: {json_response}")
            return self._default_insights()

    def generate_script(self, insights: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate live streaming script based on insights using LLM

        Returns:
            Dict with opening_hook, pain_point, solution, proof, offer
        """
        if not insights:
            return self._default_script()

        # Step 1: Get script from LLM
        prompt = self._build_script_prompt(insights)
        raw_response = self._call_api(prompt)

        # Step 2: Use LLM to extract valid JSON
        json_response = self._extract_json_with_llm(raw_response)

        # Step 3: Parse and return
        try:
            parsed = json.loads(json_response)
            return {
                "opening_hook": parsed.get("opening_hook") or "",
                "pain_point": parsed.get("pain_point") or "",
                "solution": parsed.get("solution") or "",
                "proof": parsed.get("proof") or "",
                "offer": parsed.get("offer") or ""
            }
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON: {json_response}")
            return self._default_script()

    # ==================== 内部方法 ====================

    def _call_api(self, prompt: str) -> str:
        """Call MiniMax API and return raw response text"""
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
            "temperature": 0.7,
            "max_tokens": 2000
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=30,
                proxies={"http": "http://127.0.0.1:4780", "https": "http://127.0.0.1:4780"}
            )
            response.raise_for_status()
            result = response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"MiniMax API request failed: {e}")
            raise Exception(f"AI API 请求失败: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse API response: {e}")
            raise Exception(f"AI API 响应解析失败: {str(e)}")

        # Extract content from response
        content = self._extract_content(result)
        return content

    def _extract_json_with_llm(self, raw_response: str) -> str:
        """
        Use LLM to extract valid JSON from raw response
        """
        extract_prompt = f"""从以下文本中提取出有效的JSON,不要返回任何解释文字。

文本：
{raw_response}

直接返回JSON,不要其他内容。"""

        try:
            json_content = self._call_api(extract_prompt)
            # Clean the response
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
            raise Exception(f"JSON 提取失败: {str(e)}")

    def _build_insights_prompt(self, comments: List[str]) -> str:
        """Build prompt for user insights analysis"""
        comments_text = "\n".join([f"- {c}" for c in comments])

        prompt = f"""你是一个顶级电商转化策略专家，擅长从用户评论中提炼"可直接用于广告投放和直播带货的话术级洞察"。
        你的任务是：
        从用户评论中提炼“可以用于营销、转化、产品优化”的高价值洞察。

评论内容：
{comments_text}

请返回JSON格式:
{{
    "pain_points": [],
    "selling_points": [],
    "concerns": [],
    "use_cases": []
}}
【分类定义（必须严格遵守）】

pain_points(痛点):
= 用户当前正在经历的不爽/问题
例如：效果慢、味道差、坚持困难

concerns(顾虑):
= 用户在购买前的担心/风险感
例如：怕反弹、怕副作用、怕没效果

selling_points(卖点):
= 可以用于打动用户的产品价值点（必须具备吸引力）

use_cases(使用场景):
= 适合什么人/什么情况使用（要有人群画像）

【关键要求】：
1. 不要复述原评论
2. 必须进行“归纳 + 抽象 + 提炼”
3. 每一条都要具备商业价值（能用于卖点或投放）
4. 用更通用表达，而不是具体句子
5. 输出必须“像广告文案”，而不是简单总结

【示例】：
❌ "三天见效"
✅ "短期快速见效，适合追求速效减重人群"

❌ "味道不好"
✅ "口感不佳，影响用户持续使用和复购"

❌ "上班族没时间运动"
✅ "适用于时间紧张、缺乏运动条件的上班人群"

5. 每个字段最多输出3条
6. 必须返回纯JSON(不要解释,不要markdown)

只返回JSON。"""

        return prompt

    def _build_script_prompt(self, insights: Dict[str, Any]) -> str:
        """Build prompt for script generation"""
        prompt = f"""你是一名抖音/直播带货主播，而不是写广告文案的人。
        你的任务是：
        根据用户评论洞察，生成一段“可以直接说出来”的带货话术。

用户洞察：
- 痛点: {insights.get('pain_points', [])}
- 卖点: {insights.get('selling_points', [])}
- 顾虑: {insights.get('concerns', [])}
- 使用场景: {insights.get('use_cases', [])}

请返回JSON格式:
{{
    "opening_hook": "",
    "pain_point": "",
    "solution": "",
    "proof": "",
    "offer": ""
}}

【风格要求（必须严格执行）】：
1. 必须口语化，像真人在说话，而不是写文章
2. 要有“对话感”，像在跟用户聊天
3. 多用：
   - “你是不是也有这种情况？”
   - “很多人一开始都这样”
   - “我跟你说实话”
4. 每一段控制在1-2句话,不能太长
5. 禁止使用书面语词汇，例如：
   - “解决方案”
   - “用户见证”
   - “产品优势”

【结构要求】：

opening_hook:
- 前3秒必须抓人
- 可以用反问 / 共鸣 / 夸张

pain_point:
- 描述用户真实困扰
- 要让人有代入感

solution:
- 自然引出产品
- 不要生硬推销

proof:
 必须体现“别人用了有效”的感觉（像真实用户反馈）
- 必须有真实感，避免夸张描述或虚假数据
- 必须加入具体场景细节（时间 + 行为 + 情绪）
例如：
- 昨天 / 刚刚 / 前两天
- 没抢到 / 又回来买 / 连着下单
- 后悔 / 着急 / 一直追问
- 表达要像主播在讲真实经历，而不是总结

示例（参考风格）：
昨天有个粉丝没抢到，今天一开播就冲回来下单，还一直问我还有没有

offer:
1.必须包含:
- 限时（今天 / 现在）
- 限量（数量有限 / 很快卖完）
- 错过损失（不买会后悔）
2. 禁止使用弱引导：
- “可以试试”
- “欢迎购买”
3. 必须有“催单感”，像主播在逼单

示例风格：

错误：
现在有优惠，可以试试

正确:
今天这波价格只到现在，库存也不多了，你再犹豫真的就没了！

【关键】：
输出必须“像主播在说话”，而不是像广告文案

只返回JSON。"""

        return prompt

    def _extract_content(self, result: Dict[str, Any]) -> str:
        """Extract content from various API response formats"""
        # 情况1：OpenAI 格式
        choices = result.get("choices")
        if isinstance(choices, list) and len(choices) > 0:
            content = choices[0].get("message", {}).get("content")
            if content:
                return content

        # 情况2：MiniMax reply
        if isinstance(result.get("reply"), str):
            return result["reply"]

        # 情况3：data 结构
        if isinstance(result.get("data"), dict):
            reply = result["data"].get("reply")
            if isinstance(reply, str):
                return reply

        return ""

    def _default_insights(self) -> Dict[str, Any]:
        """Return default insights response"""
        return {
            "pain_points": [],
            "selling_points": [],
            "concerns": [],
            "use_cases": []
        }

    def _default_script(self) -> Dict[str, Any]:
        """Return default script response"""
        return {
            "opening_hook": "",
            "pain_point": "",
            "solution": "",
            "proof": "",
            "offer": ""
        }
