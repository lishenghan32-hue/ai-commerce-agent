"""
AI Script Service - Script generation and rewriting
"""
import json
import logging
from typing import Any, Dict, List

from backend.services.ai.base import BaseAIService
from backend.services.ai import prompts

logger = logging.getLogger(__name__)

SCRIPT_FIELDS = ("opening", "design", "material", "details", "pairing", "offer")
CONCERN_RESPONSE_MARKERS = (
    "担心", "会不会", "怕", "顾虑", "比较在意", "很多人会关心", "很多人会担心", "放心",
)
CONCERN_SIGNAL_KEYWORDS = (
    "闷", "扎", "硌", "磨脚", "重", "厚", "累", "缩水", "变形", "褪色", "耐穿", "耐用",
    "不够暖", "保暖", "透气", "防水", "支撑", "抓地", "夹裆", "卷边", "勒", "掉跟", "压脚",
)
SIZE_OUTPUT_MARKERS = ("尺码", "码数", "偏大", "偏小", "拍大", "拍小", "选大", "选小", "号码")
PROMO_OUTPUT_MARKERS = ("优惠", "折扣", "活动价", "库存", "断码", "补货", "最后几单", "手慢无")
SIZE_SOURCE_MARKERS = ("尺码", "码数", "S", "M", "L", "XL", "34", "35", "36", "37", "38", "39", "40")
PROMO_SOURCE_MARKERS = ("优惠", "折扣", "活动价", "库存", "断码", "补货", "现货")


class AIServiceScriptMixin(BaseAIService):
    """Mixin with script-related methods"""

    def generate_single_style_script(
        self,
        insights: Dict[str, Any] = None,
        structured: Dict[str, Any] = None,
        product_context: Dict[str, Any] = None,
        comment_context: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Generate a single live streaming script (带货型)

        Args:
            insights: User insights from comment analysis
            structured: Structured product data

        Returns:
            Dict with opening_hook, pain_point, solution, proof, offer
        """
        if insights is None:
            insights = {}
        if structured is None:
            structured = {}
        if product_context is None:
            product_context = {}
        if comment_context is None:
            comment_context = {}

        # 检查是否有任何结构化数据（OCR 返回的字段名）
        has_structured = any([
            # 旧字段名
            structured.get("title"),
            structured.get("material"),
            structured.get("function"),
            structured.get("scene"),
            structured.get("target"),
            structured.get("advantage"),
            structured.get("selling_points"),
            # 通用字段（OCR 返回）
            structured.get("product_name"),
            structured.get("product_type"),
            structured.get("features"),
            structured.get("applicable"),
            structured.get("colors"),
            structured.get("season"),
            structured.get("brief_summary"),
            structured.get("detailed_summary"),
            # 服装特有
            structured.get("thickness"),
            structured.get("style"),
            # 食品特有
            structured.get("ingredients"),
            structured.get("shelf_life"),
            structured.get("origin"),
            structured.get("spec"),
            # 电子产品特有
            structured.get("model"),
            structured.get("power"),
            structured.get("battery"),
            structured.get("compatible"),
            # 美妆特有
            structured.get("effect"),
            structured.get("skin_type"),
            structured.get("usage"),
        ])

        has_product_context = any(product_context.values())
        has_comment_context = any(comment_context.values())

        if not insights and not has_structured and not has_product_context and not has_comment_context:
            return self._default_script()

        try:
            prompt = prompts.build_single_style_script_prompt(
                product_context=product_context,
                comment_context=comment_context,
                insights=insights,
                structured=structured,
            )
            logger.info(f"生成话术的prompt长度: {len(prompt)}")
            raw_response = self._call_api(prompt, max_tokens=3200)
            logger.info(f"AI返回的原始响应: {raw_response[:200]}...")
            parsed_script = self._parse_script_response(raw_response)
            reasons = self._script_revision_reasons(
                parsed_script,
                product_context=product_context,
                comment_context=comment_context,
                structured=structured,
            )

            if reasons:
                logger.info(f"话术触发自动补写: {reasons}")
                expansion_prompt = prompts.build_script_expansion_prompt(
                    script=parsed_script,
                    product_context=product_context,
                    comment_context=comment_context,
                    reasons=reasons,
                )
                expanded_raw_response = self._call_api(expansion_prompt, max_tokens=3600)
                logger.info(f"补写后的原始响应: {expanded_raw_response[:200]}...")
                expanded_script = self._parse_script_response(expanded_raw_response)
                if self._is_better_script(
                    expanded_script,
                    parsed_script,
                    product_context=product_context,
                    comment_context=comment_context,
                    structured=structured,
                ):
                    parsed_script = expanded_script

            return parsed_script
        except Exception as e:
            logger.error(f"Failed to generate script: {e}")
            return self._default_script()

    def _parse_script_response(self, raw_response: str) -> Dict[str, str]:
        json_response = self._extract_json_with_llm(raw_response)
        logger.info(f"解析后的JSON: {json_response[:200]}...")
        parsed = json.loads(json_response)
        logger.info(f"解析后的话术字段: {list(parsed.keys())}")
        return {
            field: (parsed.get(field) or "").strip()
            for field in SCRIPT_FIELDS
        }

    def _script_revision_reasons(
        self,
        script: Dict[str, str],
        product_context: Dict[str, Any],
        comment_context: Dict[str, Any],
        structured: Dict[str, Any],
    ) -> List[str]:
        reasons: List[str] = []
        total_chars = self._script_total_chars(script)
        if total_chars < 900:
            reasons.append(f"当前总字数只有 {total_chars} 字，明显偏短，更像简介而不是 5-7 分钟循环口播。")

        nonempty_sections = sum(1 for field in SCRIPT_FIELDS if script.get(field, "").strip())
        if nonempty_sections < len(SCRIPT_FIELDS):
            reasons.append("有的段落内容过短或接近空白，需要补齐完整讲款结构。")

        concern_sections = self._concern_response_sections(script, comment_context)
        expected_concern_sections = min(4, max(0, len(comment_context.get("concerns", []))))
        if expected_concern_sections and concern_sections < expected_concern_sections:
            reasons.append(
                f"当前只有 {concern_sections} 个段落明显回应了用户顾虑，顾虑覆盖不够。"
            )

        if self._mentions_unprovided_size(script, product_context, structured):
            reasons.append("出现了商品事实里没有提供的尺码/号码建议，需要删掉或改成更泛化的购买提醒。")

        if self._mentions_unprovided_promo(script, product_context, structured):
            reasons.append("出现了商品事实里没有提供的优惠或库存提醒，需要删掉或改成自然收口。")

        return reasons

    def _is_better_script(
        self,
        candidate: Dict[str, str],
        baseline: Dict[str, str],
        product_context: Dict[str, Any],
        comment_context: Dict[str, Any],
        structured: Dict[str, Any],
    ) -> bool:
        candidate_reasons = self._script_revision_reasons(
            candidate,
            product_context=product_context,
            comment_context=comment_context,
            structured=structured,
        )
        baseline_reasons = self._script_revision_reasons(
            baseline,
            product_context=product_context,
            comment_context=comment_context,
            structured=structured,
        )
        if len(candidate_reasons) < len(baseline_reasons):
            return True
        if len(candidate_reasons) == len(baseline_reasons):
            return self._script_total_chars(candidate) >= self._script_total_chars(baseline)
        return False

    def _script_total_chars(self, script: Dict[str, str]) -> int:
        return sum(len((script.get(field) or "").strip()) for field in SCRIPT_FIELDS)

    def _concern_response_sections(self, script: Dict[str, str], comment_context: Dict[str, Any]) -> int:
        topic_tokens = self._extract_concern_tokens(comment_context.get("concerns", []))
        markers = set(CONCERN_RESPONSE_MARKERS) | set(topic_tokens)
        count = 0
        for field in SCRIPT_FIELDS:
            text = (script.get(field) or "").strip()
            if text and any(marker in text for marker in markers):
                count += 1
        return count

    def _extract_concern_tokens(self, concerns: List[str]) -> List[str]:
        tokens: List[str] = []
        for concern in concerns or []:
            for keyword in CONCERN_SIGNAL_KEYWORDS:
                if keyword in concern:
                    tokens.append(keyword)
        return list(dict.fromkeys(tokens))

    def _mentions_unprovided_size(
        self,
        script: Dict[str, str],
        product_context: Dict[str, Any],
        structured: Dict[str, Any],
    ) -> bool:
        source_text = self._context_text(product_context, structured)
        if any(marker in source_text for marker in SIZE_SOURCE_MARKERS):
            return False
        script_text = self._script_text(script)
        return any(marker in script_text for marker in SIZE_OUTPUT_MARKERS)

    def _mentions_unprovided_promo(
        self,
        script: Dict[str, str],
        product_context: Dict[str, Any],
        structured: Dict[str, Any],
    ) -> bool:
        source_text = self._context_text(product_context, structured)
        if any(marker in source_text for marker in PROMO_SOURCE_MARKERS):
            return False
        script_text = self._script_text(script)
        return any(marker in script_text for marker in PROMO_OUTPUT_MARKERS)

    def _context_text(self, product_context: Dict[str, Any], structured: Dict[str, Any]) -> str:
        values: List[str] = []
        for item in list(product_context.values()) + list(structured.values()):
            if isinstance(item, list):
                values.extend(str(value) for value in item)
            elif item:
                values.append(str(item))
        return "\n".join(values)

    def _script_text(self, script: Dict[str, str]) -> str:
        return "\n".join((script.get(field) or "").strip() for field in SCRIPT_FIELDS)

    def rewrite_script(self, script: Dict[str, Any], mode: str) -> Dict[str, Any]:
        """
        Rewrite script based on mode

        Args:
            script: Original script dict
            mode: Rewrite mode

        Returns:
            Dict with rewritten script content
        """
        if not script:
            return self._default_script()

        prompt = prompts.build_rewrite_prompt(script, mode)

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
