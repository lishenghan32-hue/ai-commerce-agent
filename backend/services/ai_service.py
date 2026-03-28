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

    def generate_multi_style_scripts(self, insights: Dict[str, Any], structured: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate scripts in three different styles
        V3: Structured data has priority over insights

        Args:
            insights: User insights from comment analysis
            structured: Structured product data (title, material, function, scene, target, advantage)

        Returns:
            Dict with scripts array containing style and script content, and best_script
        """
        if insights is None:
            insights = {}
        if structured is None:
            structured = {}

        # V3: If structured data exists and has content, use it as primary source
        has_structured = any([
            structured.get("title"),
            structured.get("material"),
            structured.get("function"),
            structured.get("scene"),
            structured.get("target"),
            structured.get("advantage"),
            structured.get("selling_points")
        ])

        # If no insights but has structured, still generate scripts using structured
        if not insights and not has_structured:
            return {
                "scripts": [self._default_script_with_style(s) for s in ["带货型", "共情型", "理性型"]],
                "best_script": None
            }

        styles = ["带货型", "共情型", "理性型"]
        scripts = []

        for style in styles:
            try:
                prompt = self._build_multi_style_script_prompt(insights, style, structured)
                raw_response = self._call_api(prompt)
                json_response = self._extract_json_with_llm(raw_response)

                parsed = json.loads(json_response)
                script = {
                    "style": style,
                    "opening_hook": parsed.get("opening_hook") or "",
                    "pain_point": parsed.get("pain_point") or "",
                    "solution": parsed.get("solution") or "",
                    "proof": parsed.get("proof") or "",
                    "offer": parsed.get("offer") or ""
                }

                # Step 2: 对每条脚本进行评分
                score_result = self.score_script(script)
                script["score"] = score_result["score"]
                script["reason"] = score_result["reason"]

            except Exception as e:
                logger.error(f"Failed to generate {style} script: {e}")
                script = self._default_script_with_style(style)
                script["score"] = 0
                script["reason"] = "生成失败"

            scripts.append(script)

        # Step 3: 找出最佳脚本
        best_script = max(scripts, key=lambda x: x.get("score", 0))

        return {
            "scripts": scripts,
            "best_script": best_script
        }

    def score_script(self, script: Dict[str, Any]) -> Dict[str, Any]:
        """
        Score a script for viral potential

        Returns:
            Dict with score (0-100) and reason
        """
        if not script:
            return {"score": 0, "reason": "脚本为空"}

        try:
            prompt = self._build_score_prompt(script)
            raw_response = self._call_api(prompt)
            json_response = self._extract_json_with_llm(raw_response)

            parsed = json.loads(json_response)
            return {
                "score": parsed.get("score") or 0,
                "reason": parsed.get("reason") or ""
            }
        except Exception as e:
            logger.error(f"Failed to score script: {e}")
            return {"score": 0, "reason": "评分失败"}

    def generate_comments(self, product_name: str = "", product_info: str = "") -> List[str]:
        """
        Generate 5 realistic user comments when no comments provided

        Returns:
            List of 5 comment strings
        """
        try:
            prompt = f"""生成10条真实用户评论，每条20字以内，口语化，有正有负。

商品名称: {product_name}
商品描述: {product_info}

要求：包含价格、效果、体验相关评论，每条一行，直接返回评论内容，不要编号。"""

            raw_response = self._call_api(prompt)
            comments = [c.strip() for c in raw_response.split('\n') if c.strip()]
            return comments[:5]
        except Exception as e:
            logger.error(f"Failed to generate comments: {e}")
            return [
                "效果挺不错的",
                "价格有点贵",
                "发货速度快",
                "质量很好",
                "会回购"
            ]

    def convert_selling_points_to_comments(self, selling_points: str) -> List[str]:
        """
        Convert selling points to user-like comments

        Returns:
            List of comment strings
        """
        try:
            prompt = f"""把以下产品卖点转换为10条用户评论风格的口语化描述，每条20字以内。

卖点: {selling_points}

要求：模拟用户口吻，每条一行，直接返回评论内容，不要编号。"""

            raw_response = self._call_api(prompt)
            comments = [c.strip() for c in raw_response.split('\n') if c.strip()]
            return comments[:5]
        except Exception as e:
            logger.error(f"Failed to convert selling points: {e}")
            return [
                "确实很好用",
                "品质不错",
                "推荐购买",
                "很满意",
                "符合描述"
            ]

    def summarize_product_info(self, name: str, ocr_text: str, existing_selling_points: str = "") -> Dict[str, Any]:
        """
        Summarize and enhance product info using AI from OCR text
        Now uses V3 structured product info internally

        Args:
            name: Product name
            ocr_text: OCR extracted text from product image
            existing_selling_points: Already extracted selling points

        Returns:
            Dict with product_name, selling_points (legacy format)
        """
        # Use V3 structured product info
        structured = self.build_structured_product_info(name, ocr_text, existing_selling_points)

        return {
            "product_name": structured.get("title") or name,
            "selling_points": structured.get("selling_points") or existing_selling_points
        }

    def build_structured_product_info(
        self,
        name: str,
        ocr_text: str = "",
        selling_points: str = ""
    ) -> Dict[str, Any]:
        """
        Build V3 structured product information by merging OCR + CSS selling points

        Args:
            name: Product name/title
            ocr_text: OCR extracted text from product images
            selling_points: CSS extracted selling points

        Returns:
            Dict with structured fields: title, material, function, scene, target, advantage, selling_points
        """
        if not name and not ocr_text and not selling_points:
            return {
                "title": "",
                "material": "",
                "function": "",
                "scene": "",
                "target": "",
                "advantage": "",
                "selling_points": ""
            }

        try:
            prompt = f"""你是一个电商商品结构化专家。你的任务是将OCR文本和CSS卖点提炼成结构化的商品信息。

【输入信息】
商品名称: {name}
CSS卖点: {selling_points}
OCR文本: {ocr_text}

【输出要求】
请返回JSON格式，必须包含以下字段：
{{
    "title": "优化后的带货标题（简洁有力，能吸引点击）",
    "material": "材质信息（如：纯棉、聚酯纤维、硅胶等，没有则空）",
    "function": "功能卖点（如：保暖、防风、透气、速干等）",
    "scene": "使用场景（如：通勤、户外、冬季、游泳、健身等）",
    "target": "目标人群（如：儿童、宝妈、上班族、户外人群、敏感肌等）",
    "advantage": "核心优势/差异化卖点（2-3句话总结）",
    "selling_points": "整合后的完整卖点总结（用于展示和评论）"
}}

【关键要求】
1. 必须融合 OCR + CSS 卖点信息
2. 每个字段都要尽量有内容，缺失则用AI推理补全
3. title 要优化成"带货标题风格"（简洁、有吸引力）
4. material/material 只填实际有的，不要编造
5. 只返回JSON，不要解释，不要markdown代码块
6. selling_points 要综合所有信息，形成完整的卖点描述"""

            raw_response = self._call_api(prompt)
            json_response = self._extract_json_with_llm(raw_response)
            parsed = json.loads(json_response)

            return {
                "title": parsed.get("title") or name,
                "material": parsed.get("material") or "",
                "function": parsed.get("function") or "",
                "scene": parsed.get("scene") or "",
                "target": parsed.get("target") or "",
                "advantage": parsed.get("advantage") or "",
                "selling_points": parsed.get("selling_points") or selling_points
            }
        except Exception as e:
            logger.error(f"Failed to build structured product info: {e}")
            # Fallback: try to build from existing selling_points
            return {
                "title": name,
                "material": "",
                "function": "",
                "scene": "",
                "target": "",
                "advantage": selling_points[:50] if selling_points else "",
                "selling_points": selling_points
            }

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
            "temperature": 0.3,
            "max_tokens": 2000
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            # Create session without proxy (trust_env=False disables system proxy)
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

    def _default_script_with_style(self, style: str) -> Dict[str, Any]:
        """Return default script response with style"""
        return {
            "style": style,
            "opening_hook": "",
            "pain_point": "",
            "solution": "",
            "proof": "",
            "offer": ""
        }

    def _build_score_prompt(self, script: Dict[str, Any]) -> str:
        """Build prompt for script scoring"""
        prompt = f"""你是一个直播话术评分专家。你的任务是对以下直播带货话术进行"爆款潜力评分"。

话术内容：
- 风格: {script.get('style', '')}
- 开头吸引: {script.get('opening_hook', '')}
- 痛点: {script.get('pain_point', '')}
- 解决方案: {script.get('solution', '')}
- 证明: {script.get('proof', '')}
- 促单: {script.get('offer', '')}

请返回JSON格式:
{{
    "score": 0-100,
    "reason": "评分理由"
}}

【评分标准】：
1. 开头吸引力（0-25分）：是否能3秒内抓住注意力
2. 痛点共鸣（0-20分）：是否能引发用户共鸣
3. 解决方案说服力（0-20分）：产品是否能有效解决问题
4. 证明可信度（0-15分）：证据是否真实可信
5. 促单紧迫感（0-20分）：是否能让用户产生下单冲动

【评分要求】：
- 分数必须是0-100的整数
- 理由要简洁，一句话说明核心优势
- 重点关注转化能力和用户共鸣

只返回JSON。"""

        return prompt

    def _build_multi_style_script_prompt(self, insights: Dict[str, Any], style: str, structured: Dict[str, Any] = None) -> str:
        """Build prompt for multi-style script generation
        V3: Structured data has priority over insights

        Args:
            insights: User insights from comment analysis
            style: Script style (带货型/共情型/理性型)
            structured: Structured product data (title, material, function, scene, target, advantage)
        """
        if structured is None:
            structured = {}

        # Build structured product info for the prompt - PRIORITY SOURCE
        struct_info = ""
        has_structured = False
        if structured:
            struct_parts = []
            if structured.get("title"):
                struct_parts.append(f"商品标题: {structured['title']}")
                has_structured = True
            if structured.get("material"):
                struct_parts.append(f"材质: {structured['material']}")
                has_structured = True
            if structured.get("function"):
                struct_parts.append(f"功能: {structured['function']}")
                has_structured = True
            if structured.get("scene"):
                struct_parts.append(f"使用场景: {structured['scene']}")
                has_structured = True
            if structured.get("target"):
                struct_parts.append(f"目标人群: {structured['target']}")
                has_structured = True
            if structured.get("advantage"):
                struct_parts.append(f"核心优势: {structured['advantage']}")
                has_structured = True
            if structured.get("selling_points"):
                struct_parts.append(f"整合卖点: {structured['selling_points']}")
                has_structured = True
            if struct_parts:
                struct_info = "【商品结构化信息 - 核心参考】\n" + "\n".join(struct_parts) + "\n\n"

        # Insights - secondary source
        insights_content = ""
        if insights:
            insights_content = f"""【用户评论洞察 - 辅助参考】
- 痛点: {insights.get('pain_points', [])}
- 卖点: {insights.get('selling_points', [])}
- 顾虑: {insights.get('concerns', [])}
- 使用场景: {insights.get('use_cases', [])}\n\n"""

        # Build base content - structured data first, then insights
        if has_structured:
            base_content = f"""{struct_info}{insights_content}【重要提示】：优先使用【商品结构化信息】生成话术，【用户评论洞察】仅作辅助参考。"""
        else:
            base_content = f"""{struct_info}{insights_content}【重要提示】：使用【用户评论洞察】生成话术。"""

        # Common constraints for all styles
        common_constraints = """【禁止编造信息（必须严格执行）】
1. 只能使用以下信息来源：
   - 商品结构化数据（structured）
   - 用户评论洞察（insights）
2. 严禁编造以下内容：
   - 售后政策（如7天无理由、30天退换）
   - 价格优惠（除非明确提供）
   - 销量数据（如卖爆、10万+）
   - 品牌背书（如大牌同款、明星推荐）
3. 如果信息来源中没有，不允许补充

【表达风格（核心升级）】
必须像真人直播说话，而不是广告文案：
❌ 禁止：
- 罗列卖点（保暖、透气、舒适…）
- 一句话堆多个形容词
- 官方宣传语
✅ 必须：
- 像聊天
- 有停顿感（短句）
- 有情绪（犹豫/强调/转折）

【说话模板（强制执行）】
opening_hook：
用生活化问题，而不是卖点
❌ 错误：这款衣服保暖又舒适！
✅ 正确：你有没有发现，一到冬天，孩子穿衣服特别麻烦？

pain_point：
必须具体场景
❌ 错误：冬天很冷
✅ 正确：早上出门冷，进教室又热，一会儿脱一会儿穿，特别折腾

solution：
像推荐，而不是介绍
❌ 错误：本产品采用高科技面料
✅ 正确：我最近给孩子换了这种轻薄的，真的方便很多

proof：
必须像"讲故事"，不能喊口号
❌ 错误：卖爆了！
✅ 正确：前两天有个家长买完又回来加了一件，说孩子不愿脱

offer：
不能假信息，只能"轻催单"
❌ 错误：最后50单！
✅ 正确：这波有活动，你现在下单会更划算一点

"""

        if style == "带货型":
            prompt = f"""你是一名抖音/直播带货主播，擅长用"冲动消费"风格逼单。
你的任务是：
根据商品结构和用户评论洞察，生成一段"快节奏、高紧迫感、让人来不及思考就下单"的带货话术。
优先参考【商品结构化信息】来生成话术内容。

{base_content}

{common_constraints}

请返回JSON格式:
{{
    "opening_hook": "",
    "pain_point": "",
    "solution": "",
    "proof": "",
    "offer": ""
}}

【带货型风格要求（必须严格执行）】：
1. 快节奏、短句、干脆利落
2. 强调紧迫感：限时、限量、马上没
3. 催单感强烈，不断施压
4. 用倒计时、库存紧张等手段
5. 每一句都要有"抢"的感觉

opening_hook（必须用生活化问题）：
- 3秒内必须抓住注意力
- 用生活化问题开场，而不是罗列卖点

pain_point（必须具体场景）：
- 快速点出痛点，用具体场景描述

solution（像推荐而不是介绍）：
- 像朋友推荐一样自然

proof（像讲故事不能喊口号）：
- 讲真实的小故事

offer（只能轻催单，禁止假信息）：
- 不能编造销量、优惠
- 可以说"这波有活动"

只返回JSON。"""

        elif style == "共情型":
            prompt = f"""你是一名抖音/直播带货主播，擅长用"理解用户、情感共鸣"风格转化。
你的任务是：
根据商品结构和用户评论洞察，生成一段"真诚、理解、让人感到温暖"的共情话术。
优先参考【商品结构化信息】来生成话术内容。

{base_content}

{common_constraints}

请返回JSON格式:
{{
    "opening_hook": "",
    "pain_point": "",
    "solution": "",
    "proof": "",
    "offer": ""
}}

【共情型风格要求（必须严格执行）】：
1. 真诚、理解、体贴
2. 说出用户的心声，让他们感觉"你懂我"
3. 用第一人称"我理解你"、"我也曾..."
4. 语气温柔但不软弱
5. 让人感到被理解和关心

opening_hook（用理解开场）：
- 让用户感到被看见
- "我知道你..."

pain_point（说出用户的无奈）：
- 具体描述困扰
- 让他们感到被理解

solution（像朋友推荐）：
- 真诚推荐，不夸大

proof（用真实故事）：
- 讲温暖的小故事
- "用户说"、"粉丝反馈"

offer（温柔推荐）：
- 不施压
- "帮你争取"

只返回JSON。"""

        else:  # 理性型
            prompt = f"""你是一名抖音/直播带货主播，擅长用"理性分析、逻辑说服"风格转化。
你的任务是：
根据商品结构和用户评论洞察，生成一段"有理有据、对比分析、让人信服"的理性话术。
优先参考【商品结构化信息】来生成话术内容。

{base_content}

{common_constraints}

请返回JSON格式:
{{
    "opening_hook": "",
    "pain_point": "",
    "solution": "",
    "proof": "",
    "offer": ""
}}

【理性型风格要求（必须严格执行）】：
1. 逻辑清晰、有理有据
2. 善于对比分析、拆解原理
3. 用数据、事实说话（但不能编造）
4. 消除用户理性顾虑
5. 让人"想清楚"后下单

opening_hook（用问题引发思考）：
- "你确定不了解一下？"
- 引起好奇心

pain_point（理性分析代价）：
- 不解决问题有什么损失

solution（拆解原理）：
- 讲原理、成分
- 但不要夸大

proof（用事实但不编造）：
- 用对比、案例
- 不能编造数据

offer（帮你算账）：
- "帮你对比"
- 理性分析后值得买
- 不能编造优惠

只返回JSON。"""

        return prompt

    def rewrite_script(self, script: Dict[str, Any], mode: str) -> Dict[str, Any]:
        """
        Rewrite script based on mode

        Args:
            script: Original script dict
            mode: One of "强化转化", "更口语", "更理性", "更简短"

        Returns:
            Dict with rewritten script content
        """
        if not script:
            return self._default_script()

        prompt = self._build_rewrite_prompt(script, mode)

        try:
            raw_response = self._call_api(prompt)
            json_response = self._extract_json_with_llm(raw_response)

            parsed = json.loads(json_response)
            return {
                "opening_hook": parsed.get("opening_hook") or "",
                "pain_point": parsed.get("pain_point") or "",
                "solution": parsed.get("solution") or "",
                "proof": parsed.get("proof") or "",
                "offer": parsed.get("offer") or ""
            }
        except Exception as e:
            logger.error(f"Failed to rewrite script: {e}")
            return script

    def _build_rewrite_prompt(self, script: Dict[str, Any], mode: str) -> str:
        """Build prompt for script rewriting based on mode"""

        base_script = f"""当前话术：
- 开头吸引: {script.get('opening_hook', '')}
- 痛点: {script.get('pain_point', '')}
- 解决方案: {script.get('solution', '')}
- 证明: {script.get('proof', '')}
- 促单: {script.get('offer', '')}"""

        if mode == "强化转化":
            prompt = f"""你是一名抖音/直播带货主播，擅长优化话术提升转化率。
你的任务是：将现有话术进行"强化转化"改写，让它更具销售力。

{base_script}

请返回JSON格式:
{{
    "opening_hook": "",
    "pain_point": "",
    "solution": "",
    "proof": "",
    "offer": ""
}}

【强化转化要求】：
1. 增强情绪感染力，让用户更激动
2. 加强催单感，增加紧迫感
3. 使用倒计时、库存紧张、限时限量等手段
4. 每一句都要有"必须马上买"的感觉
5. 口语化，像主播在喊麦

示例风格：
"最后50单！抢完恢复原价！"
"家人们，手慢无啊！"
"今天这价格，只给到你们！"

只返回JSON。"""

        elif mode == "更口语":
            prompt = f"""你是一名抖音/直播带货主播，擅长用自然口语风格说话。
你的任务是：将现有话术改写得更自然、更像真人说话。

{base_script}

请返回JSON格式:
{{
    "opening_hook": "",
    "pain_point": "",
    "solution": "",
    "proof": "",
    "offer": ""
}}

【更口语要求】：
1. 像朋友聊天一样自然
2. 减少书面语词汇
3. 增加语气词和感叹
4. 让用户感觉在跟真人对话
5. 减少生硬的推销感

示例风格：
"我跟你说啊..."
"真的，我跟你讲..."
"你试试就知道了..."

只返回JSON。"""

        elif mode == "更理性":
            prompt = f"""你是一名抖音/直播带货主播，擅长用理性分析说服用户。
你的任务是：将现有话术改写得更有逻辑、更有说服力。

{base_script}

请返回JSON格式:
{{
    "opening_hook": "",
    "pain_point": "",
    "solution": "",
    "proof": "",
    "offer": ""
}}

【更理性要求】：
1. 增加数据支撑和证据
2. 增加对比分析
3. 讲原理、讲逻辑
4. 消除用户理性顾虑
5. 让人"想清楚"后下单

示例风格：
"我帮你算一笔账..."
"从科学角度来说..."
"根据数据显示..."

只返回JSON。"""

        else:  # 更简短
            prompt = f"""你是一名抖音/直播带货主播，擅长用简洁有力的话术。
你的任务是：将现有话术精简为最核心的内容。

{base_script}

请返回JSON格式:
{{
    "opening_hook": "",
    "pain_point": "",
    "solution": "",
    "proof": "",
    "offer": ""
}}

【更简短要求】：
1. 每一句控制在10个字以内
2. 删除冗余描述
3. 保留最核心卖点
4. 保持口语化
5. 去掉废话，直击重点

示例风格：
"效果好"
"便宜"
"快抢"

只返回JSON。"""

        return prompt
