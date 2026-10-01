import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "marketing_skills" / "integration.json"

class MarketingSkillsIntegrationTests(unittest.TestCase):
    def test_integration_contract(self):
        data = json.loads(CFG.read_text(encoding="utf-8"))
        self.assertEqual(data["pinned_commit"], "5b2c0007766c6a1cf1d53fd8fc73e979e0821022")
        ids = [x["id"] for x in data["selected_skills"]]
        self.assertEqual(ids, [
            "seo-audit","ai-seo","competitor-profiling","cro","analytics","marketing-loops"
        ])
        self.assertTrue(data["guardrails"]["no_second_seo_system"])
        self.assertEqual(data["guardrails"]["final_decision_owner"], "existing SEO/GEO Action Engine")
        self.assertIn("verify_analytics_and_conversion_path", data["orchestration"])

if __name__ == "__main__":
    unittest.main()
