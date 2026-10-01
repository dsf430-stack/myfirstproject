import importlib.util
from pathlib import Path
import unittest

P=Path(__file__).resolve().parents[1]/"open_seo_evidence.py"
spec=importlib.util.spec_from_file_location("open_seo_evidence",P)
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

class OpenSEOEvidenceTests(unittest.TestCase):
    def test_not_configured_is_explicit(self):
        r=m.normalize({"status":"NOT_CONFIGURED","site":"https://dsf430-stack.github.io/myfirstproject/"})
        self.assertEqual(r["status"],"NOT_CONFIGURED")
        self.assertIn("no SEO metric",r["note"])
        self.assertTrue(all(k in r["sections"] for k in m.SECTIONS))
    def test_success_preserves_market_data(self):
        r=m.normalize({"status":"SUCCESS","keywords":[{"keyword":"高雄 洗毛巾","volume":10}],"rank_tracking":{"items":[]}})
        self.assertEqual(r["sections"]["keywords"][0]["volume"],10)
    def test_rejects_fake_state(self):
        with self.assertRaises(ValueError): m.normalize({"status":"OK"})

if __name__=="__main__": unittest.main()
