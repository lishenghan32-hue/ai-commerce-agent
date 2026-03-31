import json
import unittest
from unittest.mock import Mock

from backend.services.export_service import ExportService
from backend.services.production_service import ProductionService
from backend.services.sse_service import generate_sse_events


class ProductionServiceTests(unittest.TestCase):
    def test_generate_script_from_comments_uses_single_style_output(self):
        service = ProductionService()
        service.ai_service = Mock()
        service.ai_service.analyze_comments.return_value = {"pain_points": ["cold"]}
        service.ai_service.generate_single_style_script.return_value = {
            "opening_hook": "hook",
            "pain_point": "pain",
            "solution": "solution",
            "proof": "proof",
            "offer": "offer",
        }

        result = service.generate_script_from_comments(
            product_name="coat",
            product_info="warm",
            comments=["good", "nice", "ok"],
            structured={"title": "coat"},
        )

        self.assertEqual(result["opening_hook"], "hook")
        service.ai_service.analyze_comments.assert_called_once_with(["good", "nice", "ok"])
        service.ai_service.generate_single_style_script.assert_called_once_with(
            {"pain_points": ["cold"]},
            structured={"title": "coat"},
        )


class SSEServiceTests(unittest.TestCase):
    def test_generate_sse_events_emits_single_script_completion(self):
        production_service = Mock()
        production_service.generate_script_from_comments.return_value = {
            "opening_hook": "abcdefghijk",
            "pain_point": "pain",
            "solution": "solution",
            "proof": "proof",
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
