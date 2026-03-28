"""
AI Prompts - All prompt building functions (pure functions)
"""
from typing import List, Dict, Any


def build_insights_prompt(comments: List[str]) -> str:
    """Build prompt for user insights analysis"""
    comments_text = "\n".join([f"- {c}" for c in comments])

    prompt = f"""你是一个顶级电商转化策略专家，擅长从用户评论中提炼"可直接用于广告投放和直播带货的话术级洞察"。
    你的任务是：
    从用户评论中提炼"可以用于营销、转化、产品优化"的高价值洞察。

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
2. 必须进行"归纳 + 抽象 + 提炼"
3. 每一条都要具备商业价值（能用于卖点或投放）
4. 用更通用表达，而不是具体句子
5. 输出必须"像广告文案"，而不是简单总结

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


def build_script_prompt(insights: Dict[str, Any]) -> str:
    """Build prompt for script generation"""
    prompt = f"""你是一名抖音/直播带货主播，而不是写广告文案的人。
    你的任务是：
    根据用户评论洞察，生成一段"可以直接说出来"的带货话术。

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
2. 要有"对话感"，像在跟用户聊天
3. 多用：
   - "你是不是也有这种情况？"
   - "很多人一开始都这样"
   - "我跟你说实话"
4. 每一段控制在1-2句话,不能太长
5. 禁止使用书面语词汇，例如：
   - "解决方案"
   - "用户见证"
   - "产品优势"

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
 必须体现"别人用了有效"的感觉（像真实用户反馈）
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
- "可以试试"
- "欢迎购买"
3. 必须有"催单感"，像主播在逼单

示例风格：

错误：
现在有优惠，可以试试

正确:
今天这波价格只到现在，库存也不多了，你再犹豫真的就没了！

【关键】：
输出必须"像主播在说话"，而不是像广告文案

只返回JSON。"""

    return prompt


def build_score_prompt(script: Dict[str, Any]) -> str:
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


def build_multi_style_script_prompt(insights: Dict[str, Any], style: str, structured: Dict[str, Any] = None) -> str:
    """Build prompt for multi-style script generation

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


def build_rewrite_prompt(script: Dict[str, Any], mode: str) -> str:
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
        prompt = f"""你一名抖音/直播带货主播，擅长用理性分析说服用户。
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


def build_ocr_summary_prompt(ocr_text: str) -> str:
    """Build prompt for extracting OCR summary"""
    prompt = f"""你是电商商品详情页分析专家。
请从以下商品详情页OCR文字中提取结构化信息，返回JSON：
要求：
1. 不允许编造，没有就填空字符串
2. features数组不超过8个，每个不超过20字
3. raw_summary为500字以内的详细汇总，包含材质、面料特点、穿着体验、适用场景、工艺卖点等
4. 必须返回JSON，不要解释

字段：
- material（材质，如：面料：100%纯棉、聚酯纤维；里料：100%棉等）
- features（特点数组，如：透气吸汗、不起球、柔软舒适等）
- function（功能，如：防晒、保暖、防水等）
- scene（使用场景，如：日常通勤、户外运动、旅行等）
- applicable（适用人群/场景，如：3-8岁儿童、日常上学穿）
- colors（颜色，如：多色可选）
- season（季节，如：夏季、四季通用）
- raw_summary（500字以内的详细汇总）

输入：
{ocr_text}

输出格式：
{{
  "material": "",
  "features": [],
  "function": "",
  "scene": "",
  "applicable": "",
  "colors": "",
  "season": "",
  "raw_summary": ""
}}
只返回JSON。"""
    return prompt


def build_structure_prompt(name: str, selling_points: str, ocr_text: str) -> str:
    """Build prompt for extracting structured product information"""
    prompt = f"""你是电商商品结构化专家。
请从以下信息中提取商品结构，返回JSON：
要求：
1. 不允许编造，没有就填空字符串
2. 每个字段不超过50字
3. 必须返回JSON，不要解释
字段：
- title（商品标题）
- material（材质）
- function（功能）
- scene（使用场景）
- target（人群）
- advantage（核心优势）

商品名称: {name}
卖点: {selling_points}
OCR文字: {ocr_text}

输出格式：
{{
  "title": "",
  "material": "",
  "function": "",
  "scene": "",
  "target": "",
  "advantage": ""
}}
只返回JSON。"""
    return prompt


def build_comment_generation_prompt(product_name: str, product_info: str) -> str:
    """Build prompt for generating comments"""
    prompt = f"""生成10条真实用户评论，每条20字以内，口语化，有正有负。

商品名称: {product_name}
商品描述: {product_info}

要求：包含价格、效果、体验相关评论，每条一行，直接返回评论内容，不要编号。"""
    return prompt


def build_selling_points_to_comments_prompt(selling_points: str) -> str:
    """Build prompt for converting selling points to comments"""
    prompt = f"""把以下产品卖点转换为10条用户评论风格的口语化描述，每条20字以内。

卖点: {selling_points}

要求：模拟用户口吻，每条一行，直接返回评论内容，不要编号。"""
    return prompt
