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
attach_jev_evidence = load("attach_jev_evidence", ROOT / "attach_jev_evidence.py")
page_content_audit = load("page_content_audit", ROOT / "yao_geo" / "page_content_audit.py")


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

    def test_response_headers_exclude_cookie_and_auth_material(self):
        headers = collector.safe_response_headers({"Content-Type": "text/html", "Set-Cookie": "session=secret", "Authorization": "Bearer secret", "X-Robots-Tag": "index"})
        self.assertEqual(headers, {"content-type": "text/html", "x-robots-tag": "index"})

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
            {"url": "https://x/a", "title": "高雄台南毛巾收送", "headings":{"h2":["高雄台南毛巾收送"]}, "text": "高雄 台南 毛巾 收送 品項 數量 地區"},
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
        guarded = coverage.analyze([], [{"id":"shoe","question":"shoe service","required_terms":["洗鞋"],"business_fact_review":True}])
        self.assertEqual(guarded["questions"][0]["action"], "REVIEW")

    def test_relevant_heading_beats_homepage_anchor_for_question_coverage(self):
        pages = [
            {"url":"https://x/","title":"洗衣服務","headings":{"h2":["洗衣服務"]},"text":"咖啡污漬可查看相關指南。"},
            {"url":"https://x/stain.html","title":"衣物去漬指南","headings":{"h2":["咖啡污漬怎麼處理"]},"text":"咖啡污漬依洗標與清潔劑標示處理。"},
        ]
        result = coverage.analyze(pages,[{"id":"coffee","question":"咖啡污漬怎麼洗？","required_terms":["咖啡","污漬"]}])
        self.assertEqual(result["questions"][0]["coverage"],"COVERED")
        self.assertEqual(result["questions"][0]["best_url"],"https://x/stain.html")

    def test_local_question_prefers_matching_city_service_page(self):
        pages = [
            {"url":"https://x/","title":"高雄與台南到府收送洗衣","headings":{"h2":["高雄到府收送洗衣"]},"text":"高雄 到府 收送 洗衣 區域 數量 頻率"},
            {"url":"https://x/kaohsiung-commercial-laundry.html","title":"高雄到府收送洗衣","headings":{"h1":["高雄洗衣收送"],"h2":["高雄到府收送洗衣"]},"text":"高雄 到府 收送 洗衣 區域 數量 頻率"},
        ]
        result = coverage.analyze(pages,[{"id":"khh","question":"高雄到府收送洗衣在哪裡？","query":"高雄到府收送洗衣","required_terms":["高雄","到府","收送","洗衣"]}])
        self.assertEqual(result["questions"][0]["best_url"],"https://x/kaohsiung-commercial-laundry.html")

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
        self.assertIn("Discover", result["pipeline"])
        yao = {"summary":{"pages":1,"findings":1},"pages":[{"url":"https://x/a","findings":[{"code":"TITLE","decision":"MODIFY"}]}]}
        comparison = {"status":"SUCCESS","content_gaps":[{"topic":"regional","decision":"REVIEW","coverage":"MISSING","competitor_pages":["competitor"],"first_party_pages":[]}],"citation_gaps":[{"name":"guide","action":"MODIFY","url":"https://source.test/","linked_by":[]}]}
        joined = action_engine.decisions(coverage_result, jev, yao, comparison)
        self.assertEqual(joined["yao_page_actions"][0]["decision"], "MODIFY")
        self.assertEqual([x["decision"] for x in joined["public_source_actions"]], ["REVIEW", "MODIFY"])


class JevEvidenceTests(unittest.TestCase):
    def test_attaches_crawl4ai_evidence_to_jev_pages_without_replacing_findings(self):
        audit = {"pages": [{"url": "https://example.test/project/page/", "title": "Jev title"}], "actions": [{"id": "keep"}]}
        pages = [{"url": "https://example.test/project/page", "final_url": "https://example.test/project/page/", "http_status": 200, "markdown": "markdown/1.md", "raw_html": "raw/1.html", "headings": {"h1": ["標題"]}, "content_sha256": "abc"}]
        result = attach_jev_evidence.attach(audit, pages, {"pages_crawled": 1}, "crawl_manifest.json")
        self.assertEqual(result["pages"][0]["title"], "Jev title")
        self.assertEqual(result["pages"][0]["crawl4ai_evidence"]["content_sha256"], "abc")
        self.assertEqual(result["actions"], [{"id": "keep"}])
        self.assertEqual(result["crawl4ai_evidence"]["matched_jev_pages"], 1)


if __name__ == "__main__":
    unittest.main()
