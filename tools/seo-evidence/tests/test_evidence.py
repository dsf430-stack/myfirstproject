import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


collector = load("collector", ROOT / "collector.py")
coverage = load("coverage", ROOT / "analyze_coverage.py")
action_engine = load("action_engine", ROOT / "action_engine.py")


class CollectorTests(unittest.TestCase):
    def test_normalizes_query_fragment_and_rejects_outside_project(self):
        origin = "https://example.github.io"
        prefix = "/myproject"
        self.assertEqual(collector.normalized_url("/myproject/page.html?a=1#faq", origin, prefix), "https://example.github.io/myproject/page.html")
        self.assertIsNone(collector.normalized_url("/other/page.html", origin, prefix))
        self.assertIsNone(collector.normalized_url("https://evil.example/x", origin, prefix))

    def test_github_project_robots_is_scoped_to_repository_path(self):
        with patch.object(collector, "fetch_text", return_value=(200, "User-agent: *\nAllow: /")) as fetch:
            info = collector.read_robots("https://example.github.io", "https://example.github.io/myproject/", "/myproject")
        self.assertEqual(fetch.call_args.args[0], "https://example.github.io/myproject/robots.txt")
        self.assertTrue(info["allowed"])

    def test_extracts_canonical_headings_links_jsonld_images_and_main_text(self):
        html = '''<html lang="zh-Hant"><head><title>測試服務</title><meta name="description" content="說明"><link rel="canonical" href="/myproject/"><script type="application/ld+json">{"@type":"LocalBusiness"}</script></head><body><nav>垃圾導覽</nav><main><h1>服務標題</h1><h2>常見問題</h2><a href="/myproject/page.html#faq">頁面</a><a href="https://outside.example/">外站</a><img src="a.webp" alt="洗衣"><p>正文內容</p></main><footer>重複頁尾</footer></body></html>'''
        facts = collector.extract_page(html, "https://example.github.io/myproject/", "https://example.github.io", "/myproject")
        self.assertEqual(facts["title"], "測試服務")
        self.assertEqual(facts["canonical"], "https://example.github.io/myproject/")
        self.assertEqual(facts["headings"]["h1"], ["服務標題"])
        self.assertEqual(len(facts["links"]["internal"]), 1)
        self.assertEqual(len(facts["links"]["external"]), 1)
        self.assertEqual(facts["schema"][0]["@type"], "LocalBusiness")
        self.assertEqual(facts["images"][0]["alt"], "洗衣")
        self.assertNotIn("垃圾導覽", facts["text"])
        self.assertNotIn("重複頁尾", facts["text"])


class CoverageTests(unittest.TestCase):
    def test_covered_partial_missing_and_recommendations(self):
        pages = [
            {"url": "https://x/a", "title": "高雄台南毛巾收送", "text": "高雄 台南 毛巾 收送 品項 數量 地區"},
            {"url": "https://x/b", "title": "清洗", "text": "毛巾大量洗衣"},
        ]
        questions = [
            {"id": "all", "question": "all", "required_terms": ["高雄", "台南", "毛巾", "收送"], "supporting_terms": []},
            {"id": "part", "question": "part", "required_terms": ["診所", "醫美"], "supporting_terms": ["毛巾"]},
            {"id": "none", "question": "none", "required_terms": ["口紅", "醬油"], "supporting_terms": ["血漬"]},
        ]
        result = coverage.analyze(pages, questions)
        self.assertEqual([row["coverage"] for row in result["questions"]], ["COVERED", "PARTIAL", "MISSING"])
        self.assertEqual([row["action"] for row in result["questions"]], ["KEEP", "MODIFY", "CREATE"])
        self.assertEqual(result["summary"], {"COVERED": 1, "PARTIAL": 1, "MISSING": 1})

    def test_engine_preserves_jev_priority_and_uses_conservative_actions(self):
        coverage_result = {"summary": {"COVERED": 1, "PARTIAL": 0, "MISSING": 1}, "questions": [
            {"id": "covered", "question": "known", "coverage": "COVERED", "best_url": "https://x/a", "evidence_terms": ["known"]},
            {"id": "missing", "question": "new", "coverage": "MISSING", "best_url": None, "evidence_terms": []},
        ]}
        jev = {"actions": [{"action_id": "JEV-001", "id": "broken_links", "priority": "P1", "severity": "high", "title": "Broken links", "fix": "Check destination", "urls": ["https://x/a"], "source": "rule", "heuristic": False}]}
        result = action_engine.decisions(coverage_result, jev)
        self.assertEqual([x["decision"] for x in result["question_actions"]], ["KEEP", "CREATE"])
        self.assertEqual(result["technical_actions"][0]["priority"], "P1")
        self.assertEqual(result["technical_actions"][0]["decision"], "REVIEW")


if __name__ == "__main__":
    unittest.main()
