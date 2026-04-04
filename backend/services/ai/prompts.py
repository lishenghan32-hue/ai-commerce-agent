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
            detail = structured['detailed_summary'][:300]
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

    # 构建用户评论内容
    user_comments_text = ""
    if insights:
        original_comments = insights.get("original_comments", [])
        if original_comments and isinstance(original_comments, list):
            sample_comments = original_comments[:10]
            # 用逗号分隔，不加引号
            user_comments_text = "、".join(str(c) for c in sample_comments if c)

    # Prompt
    constraints = """【规则】
1. 只用商品信息中的内容，严禁编造
2. 禁止说"第一"、"最"
3. 口语化表达60%以上

"""

    prompt = f"""是一名电商直播间的资深讲款口播策划，服务对象是鞋服类零售商家。
你的任务是：根据商品结构化信息和用户评论，生成一套适合直播讲解的完整话术。

商品信息：
{struct_info if struct_info else "(无)"}

用户评论：
{user_comments_text if user_comments_text else "(无)"}

{constraints}

【目标】
输出要像主播在直播间边展示边讲款：
1. 信息具体、可信、有画面感
2. 语言自然口语化，但不过分浮夸
3. 不是参数堆砌，也不是说明书复述
4. 要让顾客听完知道：这是什么、好在哪、适合谁、适合什么场景

【硬性约束】
1. 只能使用输入中明确提供的信息，不能编造
2. 禁止编造：价格、折扣、赠品、销量、售后政策、品牌背书、权威认证之外的信息
3. 如果没有库存信息，不要写“最后几单”“马上断码”
4. 如果没有尺码信息，不要写具体尺码推荐
5. 如果没有颜色信息，不要展开颜色推荐
6. 不要使用“最、顶级、全网第一、闭眼入”这类绝对化或低质带货词
7. 不要把字段原样拼成说明书，要把商品事实转译成用户体验
8. 请严格遵守以上所有规则，不要遗漏任何约束。

【写作方式】
每一段都尽量按照这个逻辑写：
先讲事实，再讲这个事实带来的好处，最后落到穿着体验、使用场景或搭配场景。

【品类适配规则】
如果商品属于鞋类：
- design 重点讲设计语言、鞋型轮廓、鞋身风格
- material 重点讲鞋面、内里、鞋底、中底、脚感
- details 重点讲鞋头、走线、拼接、缓震、抓地、防滑、防水透气等细节
- pairing 重点讲搭配风格、通勤/休闲/户外等场景、颜色选择
- offer 可结合尺码提醒、颜色选择、日常高频穿着价值自然收口

如果商品属于服装/内衣/打底/外套类：
- design 重点讲版型、领型、剪裁、穿着逻辑、适合内搭还是外穿
- material 重点讲面料成分、厚薄、弹性、亲肤感、保暖/透气等特性
- details 重点讲缝线、印标、接缝、里料、包裹感、安全等级、功能工艺
- pairing 重点讲季节温度、穿搭层次、上学/通勤/居家/出街等场景、颜色搭配
- offer 结合穿着频率、实用性、基础款价值做自然收口

【风格要求】
1. 像品牌直播间的主播在讲款，不是客服，不是广告标语
2. 可以使用“大家看一下”“你们看这里”“这种细节其实一上手就能感受到”这类展示型表达
3. 每段围绕一个重点，不要重复
4. 少说空话，少说“高级感满满、质感在线”，除非后面马上接具体依据
5. 语言要顺，但不要油腻，不要过度喊麦

【输出字段定义】
opening：
讲清商品身份、核心价值、适合人群或大场景，快速把产品立住，200-300字

design：
讲外观/版型/设计逻辑，让用户理解这个产品的风格与定位+用户评论回答，300-400字

material：
讲材质、成分、工艺和带来的体感或脚感+用户评论回答，300-400字

details：
讲最能体现品质和差异化的细节，强化可信度+做工细节+用户评论回答，300-400字

pairing：
讲穿搭、颜色、温度、场景或使用方式，让用户有代入感+用户评论回答，300-400字

offer：
自然收口，强调实用性、适配人群、购买提醒；不能编优惠和库存，150-200字

【长度要求】
1. 每段200-3000字
2. 每段不要重复上一段内容
3. 全文要有完整讲款感，像一位主播能直接顺着讲下来

【输出格式】
只返回严格的JSON，不要多余文字，格式如下：
{{
    "opening": "...",
    "design": "...",
    "material": "...",
    "details": "...",
    "pairing": "...",
    "offer": "..."
}}"""

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

