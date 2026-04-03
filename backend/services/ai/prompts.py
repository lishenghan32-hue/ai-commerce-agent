"""
AI Prompts - All prompt building functions (pure functions)
"""
from typing import Any, Dict, List


def _append_line(parts: List[str], label: str, value: Any) -> None:
    if value is None:
        return
    if isinstance(value, list):
        normalized = [str(item).strip() for item in value if str(item).strip()]
        if not normalized:
            return
        value = "、".join(normalized)
    elif isinstance(value, str):
        value = value.strip()
        if not value:
            return
    parts.append(f"- {label}: {value}")


def _build_product_context_block(product_context: Dict[str, Any]) -> str:
    parts: List[str] = []
    labels = [
        ("product_name", "商品名称"),
        ("product_type", "商品类型"),
        ("material", "材质/成分"),
        ("features", "特点"),
        ("function", "功能"),
        ("scene", "使用场景"),
        ("applicable", "适用人群"),
        ("colors", "颜色"),
        ("season", "季节"),
        ("brief_summary", "核心卖点"),
        ("detailed_summary", "详细描述"),
        ("selling_points", "补充卖点"),
        ("product_info", "商品描述"),
        ("thickness", "厚度"),
        ("style", "款式"),
        ("ingredients", "配料/成分"),
        ("shelf_life", "保质期"),
        ("origin", "产地"),
        ("spec", "规格"),
        ("model", "型号"),
        ("power", "功率"),
        ("battery", "续航"),
        ("compatible", "兼容系统"),
        ("effect", "功效"),
        ("skin_type", "适用肤质"),
        ("usage", "使用方式"),
    ]
    for key, label in labels:
        _append_line(parts, label, product_context.get(key))

    if not parts:
        parts.append("- 无")

    return "【商品事实】\n" + "\n".join(parts) + "\n\n"


def _build_comment_context_block(comment_context: Dict[str, Any]) -> str:
    parts: List[str] = []
    for key, label in [
        ("highlights", "高频认可"),
        ("concerns", "高频顾虑"),
        ("scenes", "高频场景"),
        ("sample_quotes", "典型原话"),
    ]:
        value = comment_context.get(key)
        if isinstance(value, list):
            normalized = [str(item).strip() for item in value if str(item).strip()]
            if normalized:
                parts.append(f"- {label}: {'；'.join(normalized)}")
        elif isinstance(value, str) and value.strip():
            parts.append(f"- {label}: {value.strip()}")

    if not parts:
        parts.append("- 无")

    return "【用户反馈】\n" + "\n".join(parts) + "\n\n"


def _legacy_product_context(structured: Dict[str, Any]) -> Dict[str, Any]:
    if structured is None:
        structured = {}

    return {
        "product_name": structured.get("title") or structured.get("product_name", ""),
        "product_type": structured.get("product_type", ""),
        "material": structured.get("material", ""),
        "features": structured.get("features", []),
        "function": structured.get("function") or structured.get("effect") or "",
        "scene": structured.get("scene", ""),
        "applicable": structured.get("applicable") or structured.get("target") or "",
        "colors": structured.get("colors", ""),
        "season": structured.get("season", ""),
        "brief_summary": structured.get("brief_summary") or structured.get("selling_points", ""),
        "detailed_summary": structured.get("detailed_summary") or structured.get("advantage", ""),
        "selling_points": structured.get("selling_points", ""),
        "thickness": structured.get("thickness", ""),
        "style": structured.get("style", ""),
        "ingredients": structured.get("ingredients", ""),
        "shelf_life": structured.get("shelf_life", ""),
        "origin": structured.get("origin", ""),
        "spec": structured.get("spec", ""),
        "model": structured.get("model", ""),
        "power": structured.get("power", ""),
        "battery": structured.get("battery", ""),
        "compatible": structured.get("compatible", ""),
        "effect": structured.get("effect", ""),
        "skin_type": structured.get("skin_type", ""),
        "usage": structured.get("usage", ""),
    }


def _legacy_comment_context(insights: Dict[str, Any]) -> Dict[str, Any]:
    if insights is None:
        insights = {}

    return {
        "highlights": insights.get("selling_points", []),
        "concerns": insights.get("concerns", []) or insights.get("pain_points", []),
        "scenes": insights.get("use_cases", []),
        "sample_quotes": insights.get("sample_quotes", []),
    }


def build_single_style_script_prompt(
    product_context: Dict[str, Any] = None,
    comment_context: Dict[str, Any] = None,
    insights: Dict[str, Any] = None,
    structured: Dict[str, Any] = None,
) -> str:
    """Build prompt for single-style script generation."""
    if product_context is None:
        product_context = {}
    if comment_context is None:
        comment_context = {}
    if insights is None:
        insights = {}
    if structured is None:
        structured = {}

    if not product_context:
        product_context = _legacy_product_context(structured)
    if not comment_context:
        comment_context = _legacy_comment_context(insights)

    product_block = _build_product_context_block(product_context)
    comment_block = _build_comment_context_block(comment_context)

    constraints = """【写作规则】
1. 【商品事实】是唯一的事实来源，所有确定性表达都必须来自商品事实。
2. 【用户反馈】只能帮助判断讲述重点、顾虑回应和场景优先级，不能当成新增事实来源。
3. 禁止编造价格、折扣、赠品、库存数量、销量、售后政策、品牌背书、权威结论、医疗功效。
4. 如果没有尺码、库存、颜色等信息，不要主动编造相关提醒。
5. 语言要像品牌直播间主播边展示边讲款，不是说明书，也不是硬广标语，更不能写成商品简介。
6. 每一段尽量按照“事实 -> 好处 -> 场景/体验”展开，避免只罗列参数。
7. 少说“高级感满满”“质感在线”“闭眼入”这类空词，必须用具体细节支撑。
8. 促单段要自然收口，可以强调实用性、适配场景、值得入手，但不要编造优惠和紧迫库存。
9. 至少在 4 个段落里自然回应用户顾虑，例如闷不闷、扎不扎、磨不磨脚、会不会厚重、耐不耐穿、适不适合长时间站立、够不够暖、好不好打理等，但要像主播顺带解释，不要写成客服问答。
10. 整体要有直播间循环讲款的节奏：每段先一句总领，再展开 2-4 句，段与段之间要有自然衔接，不能像六条独立简介。

【品类适配】
1. 如果商品属于休闲鞋、运动鞋、护士鞋等鞋类，重点讲设计语言、鞋型轮廓、鞋面与鞋底材质、脚感、做工细节、抓地缓震、久站久走体验和搭配场景。
2. 如果商品属于冲锋衣、滑雪服、羽绒服等功能型外套，重点讲防风、防水、透气、保暖、分层穿搭、活动灵活度、天气场景和细节工艺。
3. 如果商品属于儿童保暖、儿童贴身衣物等贴身类目，重点讲面料、贴肤感、安全等级、工艺细节、换季/日常场景，以及家长最在意的舒适和安心感。
4. 如果商品属于普通服装/内衣/打底/外套类，重点讲版型、面料、贴肤感、保暖/透气、工艺细节、季节温度和穿搭层次。"""

    prompt = f"""你是一名服务于鞋服类零售商家的资深直播讲款口播策划。
你的任务是：根据商品事实和用户反馈，生成一套适合直播间 5-7 分钟循环讲解的完整讲款话术。

{product_block}{comment_block}{constraints}

【输出要求】
1. opening：先把商品身份、核心价值、适合人群或大场景讲清楚，开头直接进入商品本身，不要寒暄。
2. design：讲外观/版型/设计逻辑，让用户快速理解这件商品的风格与定位；如果是功能型商品，也要讲“为什么这么设计”。
3. material：讲材质、成分、工艺和带来的体感或脚感，要把参数翻译成真实体验，不能只报成分表。
4. details：讲最能体现品质和差异化的细节，并自然回应用户高频顾虑；这一段要有明显展示感。
5. pairing：讲穿搭、颜色、温度、通勤/上学/居家/出街/户外等场景，让用户有代入感；如果是功能型产品，可以把这一段写成“场景适配”。
6. offer：自然收口，强调实用性、使用频率和适配场景，不要突然跳成硬广；可以提醒用户按自己的需求尽快选款，但不能编优惠和库存。
7. 每一段 160-220 字，整体总字数控制在 1000-1300 字，更像一套可循环讲的直播口播，而不是简介。
8. 至少有 4 个段落要能看出你吸收了用户反馈中的关注点，尤其是顾虑类反馈。
9. 多使用“大家看这里”“你们看这个位置”“这种细节其实一上手就能感觉到”“很多人会担心……但这件商品在这点上……”这类直播讲款表达。
10. 语气要自然、可信、细节丰富，像专业主播在讲款，不要写成模板化参数介绍。

请返回 JSON 格式：
{{
    "opening": "",
    "design": "",
    "material": "",
    "details": "",
    "pairing": "",
    "offer": ""
}}

只返回 JSON，不要有其他内容。"""

    return prompt


def build_script_expansion_prompt(
    script: Dict[str, Any],
    product_context: Dict[str, Any] = None,
    comment_context: Dict[str, Any] = None,
    reasons: List[str] = None,
) -> str:
    """Build prompt for expanding or repairing a weak script draft."""
    if product_context is None:
        product_context = {}
    if comment_context is None:
        comment_context = {}
    if reasons is None:
        reasons = []

    product_block = _build_product_context_block(product_context)
    comment_block = _build_comment_context_block(comment_context)
    reason_lines = "\n".join(f"- {reason}" for reason in reasons) if reasons else "- 当前初稿还不够完整"
    draft_block = f"""【当前初稿】
- opening: {script.get("opening", "")}
- design: {script.get("design", "")}
- material: {script.get("material", "")}
- details: {script.get("details", "")}
- pairing: {script.get("pairing", "")}
- offer: {script.get("offer", "")}
"""

    return f"""你是一名服务于鞋服类零售商家的资深直播讲款口播策划。
你的任务是：在不编造商品事实的前提下，把当前初稿补写成更完整、更像直播讲款的 5-7 分钟循环口播。

{product_block}{comment_block}{draft_block}
【当前初稿存在的问题】
{reason_lines}

【补写要求】
1. 只能使用【商品事实】中的确定性信息，不能编造价格、折扣、赠品、库存、销量、尺码建议、售后政策、权威背书和额外功能。
2. 把当前初稿扩充成完整讲稿，每一段 160-220 字，整体总字数控制在 1000-1300 字。
3. 至少 4 个段落要自然回应【用户反馈】里的顾虑，写法要像主播顺带解释，不要写成客服问答。
4. 每一段都按“事实 -> 好处 -> 场景/体验”展开，多补展示感、体验转译、使用场景，不要重复空话。
5. 如果商品事实里没有尺码、优惠、库存信息，绝对不要补写这些内容。
6. 语气要像专业主播在镜头前边展示边讲款，内容要比当前初稿明显更丰富、更完整，而不是简单同义改写。

请返回 JSON：
{{
    "opening": "",
    "design": "",
    "material": "",
    "details": "",
    "pairing": "",
    "offer": ""
}}

只返回 JSON，不要有其他内容。"""


def build_rewrite_prompt(script: Dict[str, Any], mode: str) -> str:
    """Build prompt for script rewriting based on mode."""
    base_script = f"""当前话术：
- 开头: {script.get('opening', '')}
- 材质: {script.get('material', '')}
- 设计: {script.get('design', '')}
- 细节: {script.get('details', '')}
- 搭配: {script.get('pairing', '')}
- 促单: {script.get('offer', '')}"""

    if mode == "强化转化":
        prompt = f"""你是一名抖音直播带货主播，擅长优化话术提升转化率。
你的任务是：将现有话术改写得更有行动感和购买推动力，但不能编造价格、库存和优惠。

{base_script}

请返回 JSON 格式：
{{
    "opening_hook": "",
    "pain_point": "",
    "solution": "",
    "proof": "",
    "offer": ""
}}

只返回 JSON。"""
    elif mode == "更口语":
        prompt = f"""你是一名抖音直播带货主播，擅长把话术改写得更自然、更像真人直播时说的话。

{base_script}

请返回 JSON 格式：
{{
    "opening_hook": "",
    "pain_point": "",
    "solution": "",
    "proof": "",
    "offer": ""
}}

只返回 JSON。"""
    elif mode == "更理性":
        prompt = f"""你是一名抖音直播带货主播，擅长用更清晰的逻辑说服用户。

{base_script}

请返回 JSON 格式：
{{
    "opening_hook": "",
    "pain_point": "",
    "solution": "",
    "proof": "",
    "offer": ""
}}

只返回 JSON。"""
    else:
        prompt = f"""你是一名抖音直播带货主播，擅长把话术精简成最核心、最有力的表达。

{base_script}

请返回 JSON 格式：
{{
    "opening_hook": "",
    "pain_point": "",
    "solution": "",
    "proof": "",
    "offer": ""
}}

只返回 JSON。"""

    return prompt


def build_ocr_summary_prompt(ocr_text: str) -> str:
    """Build prompt for extracting OCR summary."""
    prompt = f"""你是电商商品详情页分析专家。请从以下商品详情页 OCR 文字中提取结构化信息。

【重要规则】
1. 只能提取 OCR 中明确出现的信息，禁止编造。
2. 如果某个字段没有对应内容，返回空字符串或空数组。
3. 根据商品类型补充对应的特有字段。
4. detailed_summary 需要分段描述，用 \\n 分隔不同主题。

【商品类型参考】
- 服装/鞋帽：重点提取面料、厚度、款式、适用季节
- 食品/饮料：重点提取配料、保质期、产地、规格
- 电子产品：重点提取型号、参数、功率、续航
- 美妆护肤：重点提取成分、功效、适用肤质
- 家居用品：重点提取材质、尺寸、颜色

【输出格式】
{{
  "product_type": "根据内容判断商品类型",
  "material": "",
  "features": [],
  "function": "",
  "scene": "",
  "applicable": "",
  "colors": "",
  "season": "",
  "brief_summary": "",
  "detailed_summary": "",
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

输入 OCR 文字：
{ocr_text}

只返回 JSON。"""
    return prompt


def build_comment_generation_prompt(product_name: str, product_info: str = "", structured: dict = None) -> str:
    """Build prompt for generating comments."""
    if structured is None:
        structured = {}

    product_context = _build_product_context_block({
        "product_name": product_name,
        "product_info": product_info,
        **structured,
    })

    prompt = f"""你是电商用户评论生成专家。根据以下商品信息，生成真实、口语化的用户评论。

{product_context}
【生成要求】
1. 一共生成 10 条评论。
2. 其中 6 条是正向认可，4 条是下单前顾虑或犹豫点。
3. 顾虑型评论要写成真实用户的担心或犹豫，不要写成恶意差评。
4. 评论重点围绕材质、功能、舒适度、场景、搭配、做工等方面。
5. 如果商品信息里没有价格、尺码、库存等内容，不要主动评论这些内容。
6. 每条 15-28 字，口语化、自然，不要编号。
7. 每条单独一行。

只返回评论内容，不要有其他解释。"""
    return prompt
