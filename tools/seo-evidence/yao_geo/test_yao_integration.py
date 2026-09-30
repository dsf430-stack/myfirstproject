import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parent

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path); module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module
universe=load("universe",ROOT/"build_universe.py")
page_audit=load("page_audit",ROOT/"page_content_audit.py")
source_compare=load("source_compare",ROOT/"compare_public_sources.py")

class YaoIntegrationTests(unittest.TestCase):
    def test_query_universe_is_deduplicated_and_covers_requested_topics(self):
        data=universe.build()
        self.assertGreaterEqual(len(data["query_seeds"]),40)
        self.assertGreaterEqual(data["count"],100)
        ids={s["id"] for s in data["query_seeds"]}
        self.assertTrue({f"S{i:02}" for i in range(1,45)}.issubset(ids))
        questions=[q["question"] for q in data["questions"]]
        self.assertEqual(len(questions),len(set(questions)))
        self.assertTrue(any("洗鞋" in s["query"] for s in data["query_seeds"]))
        self.assertTrue(any("紅酒" in s["query"] for s in data["query_seeds"]))
        by_id={q["seed_id"]:q["question"] for q in data["questions"] if q["id"].endswith("-Q")}
        self.assertEqual(by_id["S25"],"襯衫清洗前要查看哪些洗標資訊？")
        self.assertEqual(by_id["S33"],"不同布料可以用相同洗滌方式嗎？")
        self.assertEqual(by_id["S37"],"洗衣精有哪些常見化學原料？")
        footwear=[q for q in data["questions"] if q["seed_id"]=="S29"]
        self.assertEqual({q["id"] for q in footwear if q["business_fact_review"]},{"S29-Q3"})

    def test_unconfirmed_service_questions_are_review_not_create(self):
        seed=next(s for s in universe.build()["query_seeds"] if s["id"]=="S03")
        item={"id":"shoe","question":"高雄洗鞋服務","required_terms":["高雄","洗鞋"],"business_fact_review":True}
        r=load("coverage",ROOT.parent/"analyze_coverage.py").analyze([], [item])
        self.assertEqual(r["questions"][0]["coverage"],"MISSING")
        self.assertEqual(r["questions"][0]["action"],"REVIEW")
        false_match=load("coverage_again",ROOT.parent/"analyze_coverage.py").analyze([{"url":"https://x/","title":"高雄洗鞋","text":"高雄洗鞋"}],[item])
        self.assertEqual(false_match["questions"][0]["coverage"],"PARTIAL")
        self.assertEqual(false_match["questions"][0]["action"],"REVIEW")

    def test_existing_stain_page_improvement_has_sources_and_matching_visible_faq_schema(self):
        html=(ROOT.parents[2]/"stain-removal-guide.html").read_text(encoding="utf-8")
        self.assertIn("咖啡",html); self.assertIn("紅酒",html); self.assertIn("油漬",html)
        self.assertIn("洗標",html); self.assertIn("無法保證",html)
        self.assertIn("https://www.cleaninginstitute.org/cleaning-tips/clothes/stain-removal-guide",html)
        self.assertIn("FAQPage",html)
        self.assertIn("咖啡、茶或紅酒沾到衣服，第一步該做什麼？",html)

    def test_page_audit_uses_only_observed_evidence_and_flags_claims_for_review(self):
        pages=[{"url":"https://x/","http_status":200,"title":"洗衣","meta_description":"description","canonical":"https://x/","headings":{"h1":["洗衣"],"h2":["FAQ"],"h3":["Question"]},"text":"我們提供洗鞋服務。"+"文字"*200,"links":{"internal":[{"href":"https://x/a"}],"external":[]},"schema":[{"@type":"FAQPage"}],"html_bytes":1000,"markdown_chars":100}]
        r=page_audit.audit(pages)
        check=next(c for c in r["pages"][0]["checks"] if c["code"]=="UNVERIFIED_SERVICE_CLAIM")
        self.assertEqual(check["decision"],"REVIEW")

    def test_blocked_public_pages_are_uncertain_and_not_assigned_configured_topics(self):
        with tempfile.TemporaryDirectory() as temp:
            base=Path(temp); ext=base/"external"; comp=ext/"competitors"/"blocked"; comp.mkdir(parents=True)
            (comp/"pages.json").write_text(json.dumps([{"url":"https://blocked.example/","http_status":200,"title":"One moment, please...","text":"Loader Please wait while your request is being verified..."}]),encoding="utf-8")
            result=source_compare.compare([],base,{"competitors":[{"id":"blocked","name":"Blocked","url":"https://blocked.example/","observed_topics":["pickup and delivery"]}],"citation_sources":[]},ext)
        self.assertEqual(result["status"],"UNCERTAIN")
        self.assertEqual(result["competitors"][0]["status"],"UNCERTAIN")
        self.assertEqual(result["competitors"][0]["observed_topics"],[])

if __name__=="__main__": unittest.main()
