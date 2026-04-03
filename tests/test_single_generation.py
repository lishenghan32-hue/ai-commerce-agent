import unittest
from unittest.mock import Mock

from backend.services.export_service import ExportService
from backend.services.production_service import ProductionService
from backend.services.sse_service import generate_sse_events


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
