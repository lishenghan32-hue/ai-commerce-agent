import json
import unittest
from unittest.mock import Mock

from backend.services.ai.base import BaseAIService
from backend.services.ai.script import AIServiceScriptMixin
from backend.services.export_service import ExportService
from backend.services.production_service import ProductionService
from backend.services.sse_service import generate_sse_events


class FakeScriptService(AIServiceScriptMixin, BaseAIService):
    def __init__(self, responses):
        super().__init__()
        self.responses = list(responses)
        self.prompts = []

    def _call_api(self, prompt: str, max_retries: int = 3, max_tokens: int = 2000) -> str:
        self.prompts.append((prompt, max_tokens))
        return self.responses.pop(0)


class ProductionServiceTests(unittest.TestCase):
    def test_generate_script_from_comments_builds_product_and_comment_context(self):
        service = ProductionService()
        service.ai_service = Mock()
        service.ai_service.generate_single_style_script.return_value = {
            "opening": "opening",
            "design": "design",
            "material": "material",
            "details": "details",
            "pairing": "pairing",
            "offer": "offer",
        }

        result = service.generate_script_from_comments(
            product_name="coat",
            product_info="soft fabric",
            selling_points="light and warm",
            comments=[
                "soft and warm",
                "great for daily commute",
                "a bit heavy for long walks",
            ],
            structured={"title": "coat", "product_type": "服装"},
        )

        self.assertEqual(result["opening"], "opening")

        kwargs = service.ai_service.generate_single_style_script.call_args.kwargs
        self.assertEqual(kwargs["structured"], {"title": "coat", "product_type": "服装"})
        self.assertEqual(kwargs["product_context"]["product_name"], "coat")
        self.assertEqual(kwargs["product_context"]["brief_summary"], "light and warm")
        self.assertIn("soft and warm", kwargs["comment_context"]["highlights"])
        self.assertIn("great for daily commute", kwargs["comment_context"]["scenes"])
        self.assertIn("a bit heavy for long walks", kwargs["comment_context"]["concerns"])
        self.assertIn("soft and warm", kwargs["insights"]["selling_points"])

    def test_prepare_comments_replaces_placeholder_comments(self):
        service = ProductionService()
        service.ai_service = Mock()
        service.ai_service.generate_comments.return_value = [
            "面料很软",
            "通勤穿着舒服",
            "轻暖不臃肿",
        ]

        prepared = service.prepare_comments(
            product_name="shoe",
            product_info="soft",
            comments=["质量不错", "性价比高", "值得购买"],
            structured={"title": "shoe"},
        )

        self.assertEqual(prepared, ["面料很软", "通勤穿着舒服", "轻暖不臃肿"])
        service.ai_service.generate_comments.assert_called_once()

    def test_prepare_comments_keeps_concerns_beyond_first_five_comments(self):
        service = ProductionService()
        service.ai_service = Mock()

        comments = [
            "面料柔软，孩子穿着舒服",
            "版型贴身，活动起来很自在",
            "图案可爱，孩子自己也喜欢",
            "透气感不错，日常穿挺合适",
            "腰头不勒肚子，穿着很稳",
            "担心孩子活动量大，会不会容易变形",
            "不知道洗了之后会不会缩水",
            "有点担心颜色会不会容易褪色",
        ]

        prepared = service.prepare_comments(
            product_name="内裤",
            product_info="soft",
            comments=comments,
            structured={"title": "内裤"},
        )

        self.assertEqual(len(prepared), 8)
        self.assertIn("担心孩子活动量大，会不会容易变形", prepared)
        self.assertIn("不知道洗了之后会不会缩水", prepared)
        self.assertIn("有点担心颜色会不会容易褪色", prepared)


class ScriptGenerationTests(unittest.TestCase):
    def test_generate_single_style_script_auto_expands_short_draft(self):
        short_response = json.dumps(
            {
                "opening": "今天给大家带来的是这款儿童内裤，穿着舒服。",
                "design": "版型贴身，活动方便。",
                "material": "莫代尔柔软透气，里裆是棉。",
                "details": "无骨缝制更舒适。",
                "pairing": "日常上学居家都能穿。",
                "offer": "喜欢可以看看。",
            },
            ensure_ascii=False,
        )
        long_response = json.dumps(
            {
                "opening": "今天给大家带来的是一款给孩子日常高频穿的贴身内裤，大家先别把它只当成基础款，真正贴身穿的东西，舒服不舒服、勒不勒、活动起来顺不顺，孩子一上身就能感觉出来。它是给3到12岁孩子做的人体工学分阶设计，所以不是简单把成人版缩小，而是围绕孩子跑跳蹲这些动作去做得更贴合、更自在，家长给孩子选这种贴身衣物时，一开始最看重的，往往就是这种日常一整天都能穿得住的舒服感。",
                "design": "你们看这条内裤的版型逻辑，它不是单纯追求好看，而是先解决孩子活动时容易夹、容易勒、容易跑位这些实际问题。人体工学版型配合定制松紧腰头，穿上之后腰部位置更稳，孩子弯腰、蹲下、跑动的时候不容易觉得束缚。很多家长会担心中腰设计会不会卡肚子，但它这里做的是更高一点的中腰包裹，重点不是勒得更紧，而是让小肚子位置更服帖、更安心，孩子日常穿着活动也会更自在。",
                "material": "材质这块大家看一下，主体是91%莫代尔加9%氨纶，里裆是100%棉，这个组合的重点不是把参数报给大家听，而是把贴肤感、弹性和透气感都兼顾起来。莫代尔本身摸起来更柔软，孩子贴身穿不容易觉得糙，氨纶提供的是活动时需要的回弹和包裹，所以跑跳蹲的时候不容易紧绷。很多人会担心这种贴身裤洗后会不会缩水、会不会越穿越没型，至少从材质结构上看，它考虑的是日常反复穿着后的舒适度和伸展性，不是那种一上身还行、动起来就卡的路线。",
                "details": "细节部分你们一定要看，这种贴身单品最怕的其实不是外观，而是后腰标签磨不磨、接缝硌不硌、腿围会不会卷边。它用了无感标签和无骨缝制，等于把容易扎、容易磨的点尽量往下压，孩子贴身穿着时接受度会高很多。再往下看，全裤3A抗菌这件事，对很多家长来说是很重要的安心感，尤其是比较在意私处健康、怕夏天闷汗的，会更关注这一类细节。包括男宝无侧缝、女宝侧缝前移这种处理，也是在回应大家常担心的卡裆、勒腿和走线不稳的问题。",
                "pairing": "这类产品虽然不是外穿单品，但使用场景非常高频。像平时上学、放学回家、居家活动、晚上睡觉，甚至夏天比较热的时候，都需要这种透气又不勒的贴身内裤去兜底。大家给孩子选这种日常贴身衣物，往往会担心一条裤子是不是只能在某个场景穿，其实越是基础款，越要看它能不能高频轮换、穿着省心。白底炫彩心印花这种设计也不是浮夸路线，看着有童趣，孩子自己接受度高，家长日常搭配和整理也比较省心。",
                "offer": "所以这类商品我一直觉得，不能只看它是不是基础款，而是要看它能不能真正解决孩子贴身穿的舒服和家长下单时的顾虑。你如果比较在意的是腰头会不会勒、活动时会不会夹、洗后会不会容易缩水变形、贴身穿会不会闷，那这条内裤的版型、材质和工艺细节其实都在围绕这些问题去做。给孩子贴身穿的东西，本来就是家里会高频轮换的单品，只要你正准备补这类基础款，就值得认真看一下。",
            },
            ensure_ascii=False,
        )

        service = FakeScriptService([short_response, long_response])
        result = service.generate_single_style_script(
            product_context={"product_name": "内裤", "material": "91%莫代尔，9%氨纶"},
            comment_context={"concerns": ["担心洗后会不会缩水", "担心活动量大容易变形"]},
        )

        self.assertGreaterEqual(sum(len(value) for value in result.values()), 900)
        self.assertIn("很多家长会担心", result["design"])
        self.assertEqual(len(service.prompts), 2)


class SSEServiceTests(unittest.TestCase):
    def test_generate_sse_events_emits_single_script_completion(self):
        production_service = Mock()
        production_service.generate_script_from_comments.return_value = {
            "opening": "abcdefghijk",
            "design": "design",
            "material": "material",
            "details": "details",
            "pairing": "pairing",
            "offer": "offer",
        }

        events = list(
            generate_sse_events(
                production_service,
                product_name="coat",
                product_info="warm",
                selling_points="light",
                structured={"title": "coat"},
                comments=["a", "b", "c"],
            )
        )

        text = "".join(events)
        self.assertIn("event: script_section", text)
        self.assertIn("event: script_chunk", text)
        self.assertIn("event: script_complete", text)
        self.assertIn('"completed": true', text)
        self.assertIn('event: complete', text)
        self.assertIn('"script"', text)


class ExportServiceTests(unittest.TestCase):
    def test_export_formats_single_script_without_score(self):
        service = ExportService()
        script = {
            "opening_hook": "hook",
            "pain_point": "pain",
            "solution": "solution",
            "proof": "proof",
            "offer": "offer",
        }

        markdown = service._generate_markdown(script)
        text = service._generate_txt(script)

        self.assertIn("hook", markdown)
        self.assertIn("pain", text)
        self.assertNotIn("score", markdown.lower())
        self.assertNotIn("style", text.lower())


if __name__ == "__main__":
    unittest.main()
