#!/usr/bin/env python3
"""Deterministic, source-cited question coverage over a Crawl4AI pages.json."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def analyze(pages: list[dict], questions: list[dict]) -> dict:
    rows = []
    for question in questions:
        required = set(question.get("required_terms", []))
        support = set(question.get("supporting_terms", []))
        candidates = []
        for page in pages:
            text = " ".join(str(page.get(k) or "") for k in ("title", "meta_description", "text", "markdown_text"))
            hits_required = sorted(term for term in required if term in text)
            hits_support = sorted(term for term in support if term in text)
            if len(hits_required) == len(required) and required:
                state = "COVERED"
            elif hits_required or hits_support:
                state = "PARTIAL"
            else:
                state = "MISSING"
            candidates.append({"url": page.get("url"), "status": state, "required_hits": hits_required, "supporting_hits": hits_support})
        candidates.sort(key=lambda x: (x["status"] != "COVERED", x["status"] != "PARTIAL", -(len(x["required_hits"]) + len(x["supporting_hits"])), x["url"] or ""))
        best = candidates[0] if candidates else {"url": None, "status": "MISSING", "required_hits": [], "supporting_hits": []}
        decision = {"COVERED": "KEEP", "PARTIAL": "MODIFY", "MISSING": "CREATE"}[best["status"]]
        rows.append({"id": question["id"], "question": question["question"], "coverage": best["status"], "best_url": best["url"], "action": decision, "evidence_terms": best["required_hits"] + best["supporting_hits"], "per_page": candidates})
    return {"schema_version": "1.0", "method": "deterministic substring coverage; review before any content change", "summary": {state: sum(row["coverage"] == state for row in rows) for state in ("COVERED", "PARTIAL", "MISSING")}, "questions": rows}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pages", type=Path, required=True)
    ap.add_argument("--questions", type=Path, default=Path(__file__).with_name("questions.json"))
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    pages = json.loads(args.pages.read_text(encoding="utf-8"))
    questions = json.loads(args.questions.read_text(encoding="utf-8"))["questions"]
    result = analyze(pages, questions)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status": "SUCCESS", "summary": result["summary"], "out": str(args.out)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
