"""
AI Prompts - All prompt building functions (pure functions)
"""
from typing import List, Dict, Any


def build_single_style_script_prompt(insights: Dict[str, Any], structured: Dict[str, Any] = None) -> str:
    """Build prompt for single-style script generation (带货型)

    Args:
        insights: User insights from comment analysis
        structured: Structured product data
    """
    if structured is None:
        structured = {}

    # 构建商品结构化信息
    struct_info = ""
    if structured:
        struct_parts = []
        # 商品基本信息
        if structured.get("title"):
            struct_parts.append(f"商品名称: {structured['title']}")
        if structured.get("product_type"):
            struct_parts.append(f"商品类型: {structured['product_type']}")
        # 材质相关信息
        if structured.get("material"):
            struct_parts.append(f"材质: {structured['material']}")
        if structured.get("ingredients"):
            struct_parts.append(f"成分/配料: {structured['ingredients']}")
        # 功能特性
        if structured.get("function"):
            struct_parts.append(f"功能: {structured['function']}")
        if structured.get("effect"):
            struct_parts.append(f"功效: {structured['effect']}")
        if structured.get("features"):
            features = structured.get("features")
            if isinstance(features, list):
                features = "、".join(features)
            if features:
                struct_parts.append(f"特点: {features}")
        # 版型设计
        if structured.get("style"):
            struct_parts.append(f"款式: {structured['style']}")
        if structured.get("thickness"):
            struct_parts.append(f"厚度: {structured['thickness']}")
        if structured.get("scene"):
            struct_parts.append(f"使用场景: {structured['scene']}")
        if structured.get("applicable"):
            struct_parts.append(f"适用人群: {structured['applicable']}")
        # 外观
        if structured.get("colors"):
            struct_parts.append(f"颜色: {structured['colors']}")
        if structured.get("season"):
            struct_parts.append(f"适用季节: {structured['season']}")
        # 其他信息
        if structured.get("brief_summary"):
            struct_parts.append(f"核心卖点: {structured['brief_summary']}")
        if structured.get("detailed_summary"):
            # 只取前200字，避免过长
            detail = structured['detailed_summary'][:200]
            struct_parts.append(f"详细描述: {detail}")
        # 商品特有字段
        if structured.get("shelf_life"):
            struct_parts.append(f"保质期: {structured['shelf_life']}")
        if structured.get("origin"):
            struct_parts.append(f"产地: {structured['origin']}")
        if structured.get("spec"):
            struct_parts.append(f"规格: {structured['spec']}")
        if structured.get("model"):
            struct_parts.append(f"型号: {structured['model']}")
        if structured.get("power"):
            struct_parts.append(f"功率: {structured['power']}")
        if structured.get("battery"):
            struct_parts.append(f"续航: {structured['battery']}")
        if structured.get("compatible"):
            struct_parts.append(f"兼容系统: {structured['compatible']}")
        if structured.get("skin_type"):
            struct_parts.append(f"适用肤质: {structured['skin_type']}")
        if structured.get("usage"):
            struct_parts.append(f"使用方法: {structured['usage']}")
        if structured.get("selling_points"):
            struct_parts.append(f"卖点: {structured['selling_points']}")

        if struct_parts:
            struct_info = "【商品详细信息】\n" + "\n".join(f"- {p}" for p in struct_parts) + "\n\n"

    # 合并 insights 中的关键词作为补充
    insights_content = ""
    if insights:
        extra_parts = []
        if insights.get("selling_points"):
            extra_parts.append(f"用户认可的卖点: {insights['selling_points']}")
        if insights.get("pain_points"):
            extra_parts.append(f"用户关心的点: {insights['pain_points']}")
        if extra_parts:
            insights_content = "【用户反馈参考】\n" + "\n".join(f"- {p}" for p in extra_parts) + "\n\n"

    base_content = f"{struct_info}{insights_content}"

    # 禁止编造规则
    constraints = """【禁止编造信息（必须严格执行）】
1. 只能使用商品详情页或结构化数据中明确有的信息
2. 严禁编造：售后政策、价格优惠、销量数据、品牌背书
3. 不能说"第一"、"最"等绝对化表述
4. 如果信息中没有材质成分，不能编造
5. 如果信息中没有具体功能，不能编造

【话术风格要求】
✅ 开头直接介绍产品，不是问问题
✅ 像产品说明书一样专业讲解，不是情感共鸣
✅ 用具体材质、工艺、技术术语，不是模糊形容
✅ 有展示感（"大家看"、"先看看"），不是自说自话
❌ 禁止问问题式开头（"你有没有觉得..."）
❌ 禁止罗列卖点式介绍
❌ 禁止编造数据或功能

"""

    prompt = f"""你是一名专业的抖音直播带货主播，擅长产品讲解和卖点输出。
你的任务是：根据商品详细信息，生成专业的直播带货话术。

{base_content}

{constraints}

请返回JSON格式:
{{
    "opening": "开头引入，直接介绍产品（不是问问题）",
    "material": "材质/面料介绍，具体材质名称和工艺特点",
    "design": "版型/设计介绍，款式特点和适用场景",
    "details": "细节介绍，做工、品质、对比等",
    "pairing": "搭配建议，适用场景和颜色选择",
    "offer": "促单话术，库存、尺码、优惠等"
}}

【输出要求】
1. opening：直接介绍产品本身或设计灵感，比如"今天给大家带来的是..."、"各位老板有没有..."，要详细展开产品特点和使用场景，多用口语化表达
2. material：具体材质名称，如"牛剖层皮革"、"EVA+橡胶双底"、"吸湿速干面料"等，需要详细描述材质特性、工艺优点和穿着体验，多用大白话解释
3. design：专业版型说明+适用场景，详细介绍剪裁设计、风格特点和适合的穿搭场合，用通俗易懂的语言描述
4. details：对比说明+展示感话术，如"大家看一下这个走线..."、"真的，我跟你讲..."，要详细描述细节做工、品质对比和独特设计，多用口语化表达
5. pairing：场景适用+颜色搭配建议，结合商品特性给出具体的搭配方案、场合推荐和风格建议，用朋友聊天的语气
6. offer：库存有限、尺码提醒、断码风险等自然促单，要有紧迫感并给出具体的优惠或限时信息，多用"家人们"、"最后"、"抓紧"等口语

每一部分200-300字，要充分展开，多用具体描述和数据支撑。口语化表达占比60%以上，像真的主播在直播间跟观众聊天一样。
只返回JSON，不要有其他内容。"""

    return prompt


def build_rewrite_prompt(script: Dict[str, Any], mode: str) -> str:
    """Build prompt for script rewriting based on mode"""

    base_script = f"""当前话术：
- 开头: {script.get('opening', '')}
- 材质: {script.get('material', '')}
- 版型: {script.get('design', '')}
- 细节: {script.get('details', '')}
- 搭配: {script.get('pairing', '')}
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
    prompt = f"""你是电商商品详情页分析专家。请从以下商品详情页OCR文字中提取结构化信息。

【重要规则】
1. 只提取OCR中明确有的信息，禁止编造
2. 如果某个字段OCR中没有相关内容，返回空字符串
3. 根据商品类型，填充对应类型的特有字段
4. detailed_summary 必须分段表述，用\\n分隔不同主题内容

【商品类型参考】
- 服装/鞋帽：重点提取面料、厚度、款式、适用季节
- 食品/饮料：重点提取配料、保质期、产地、规格
- 电子产品：重点提取型号、参数、功率、续航
- 美妆护肤：重点提取成分、功效、适用肤质
- 家居用品：重点提取材质、尺寸、颜色

【输出字段】
通用字段（所有商品类型）：
- material：材质成分
- features：特点数组（不超过8个，每个不超过20字）
- function：功能
- scene：使用场景
- applicable：适用人群
- colors：颜色
- season：适用季节

服装特有：
- thickness：厚度
- style：款式

食品特有：
- ingredients：配料表
- shelf_life：保质期
- origin：产地
- spec：规格

电子产品特有：
- model：型号
- power：功率
- battery：续航
- compatible：兼容系统

美妆特有：
- ingredients：成分
- effect：功效
- skin_type：适用肤质
- usage：使用方法

输出格式：
{{
  "product_type": "根据内容判断商品类型",
  "material": "",
  "features": [],
  "function": "",
  "scene": "",
  "applicable": "",
  "colors": "",
  "season": "",
  "brief_summary": "30字以内的核心卖点",
  "detailed_summary": "800-1200字详细描述，必须包含以下维度：①材质面料（具体成分含量）②工艺特点（制作工艺/技术）③穿着/使用体验（舒适度/口感/效果）④适用场景（场合/人群）⑤与其他产品的差异化优势。每一维度至少50字，分段表述用\\n分隔",
  "thickness": "",
  "style": "",
  "ingredients": "",
  "shelf_life": "",
  "origin": "",
  "spec": "",
  "model": "",
  "power": "",
  "battery": "",
  "compatible": "",
  "effect": "",
  "skin_type": "",
  "usage": ""
}}
只返回JSON，不要解释。

输入的OCR文字：
{ocr_text}

只返回JSON。"""
    return prompt


def build_comment_generation_prompt(product_name: str, product_info: str = "", structured: dict = None) -> str:
    """Build prompt for generating comments"""
    if structured is None:
        structured = {}

    # 构建商品信息上下文
    info_parts = []
    if product_name:
        info_parts.append(f"商品名称: {product_name}")
    if structured.get("product_type"):
        info_parts.append(f"商品类型: {structured.get('product_type')}")
    if structured.get("material"):
        info_parts.append(f"材质/成分: {structured.get('material')}")
    if structured.get("features"):
        features = structured.get("features")
        if isinstance(features, list):
            features = "、".join(features)
        info_parts.append(f"功能特点: {features}")
    if structured.get("function"):
        info_parts.append(f"功能: {structured.get('function')}")
    if structured.get("scene"):
        info_parts.append(f"使用场景: {structured.get('scene')}")
    if structured.get("applicable"):
        info_parts.append(f"适用人群: {structured.get('applicable')}")
    if structured.get("brief_summary"):
        info_parts.append(f"核心卖点: {structured.get('brief_summary')}")
    if structured.get("detailed_summary"):
        info_parts.append(f"详细描述: {structured.get('detailed_summary')}")
    if product_info:
        info_parts.append(f"商品描述: {product_info}")

    # 其他特有字段
    for key, label in [("thickness", "厚度"), ("style", "款式"), ("ingredients", "配料"),
                        ("shelf_life", "保质期"), ("origin", "产地"), ("spec", "规格"),
                        ("model", "型号"), ("power", "功率"), ("battery", "续航"),
                        ("effect", "功效"), ("skin_type", "适用肤质"), ("usage", "使用方法")]:
        if structured.get(key):
            info_parts.append(f"{label}: {structured.get(key)}")

    product_context = "\n".join(info_parts) if info_parts else "无"

    prompt = f"""你是电商用户评论生成专家。根据以下商品信息，生成真实用户评论。

{product_context}

要求：
1. 生成10条评论，每条15-25字
2. 口语化，像真实用户说话
3. 包含正负评价（6:4比例）
4. 评论要围绕商品的材质、功能、体验、价格等方面
5. 每条一行，不要编号，直接返回评论内容"""
    return prompt

