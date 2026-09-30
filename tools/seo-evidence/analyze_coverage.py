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
            heading_text = " ".join([str(page.get("title") or "")] + [str(value) for level in (page.get("headings") or {}).values() for value in (level or [])])
            heading_hits = sorted(term for term in required if term in heading_text)
            if len(hits_required) == len(required) and required and heading_hits:
                state = "PARTIAL" if question.get("business_fact_review") else "COVERED"
            elif hits_required or hits_support:
                state = "PARTIAL"
            else:
                state = "MISSING"
            url = page.get("url") or ""
            city = "tainan" if "台南" in (question.get("query", "") + question.get("question", "")) else "kaohsiung" if "高雄" in (question.get("query", "") + question.get("question", "")) else None
            local_match = bool(city and city in url.lower())
            candidates.append({"url": page.get("url"), "status": state, "required_hits": hits_required, "supporting_hits": hits_support, "heading_hits": heading_hits, "keyword_occurrences": sum(text.count(term) for term in required), "local_url_match": local_match})
        candidates.sort(key=lambda x: (x["status"] != "COVERED", x["status"] != "PARTIAL", not x["local_url_match"], -len(x["heading_hits"]), -x["keyword_occurrences"], -(len(x["required_hits"]) + len(x["supporting_hits"])), x["url"] or ""))
        best = candidates[0] if candidates else {"url": None, "status": "MISSING", "required_hits": [], "supporting_hits": []}
        decision = "REVIEW" if question.get("business_fact_review") else {"COVERED": "KEEP", "PARTIAL": "MODIFY", "MISSING": "CREATE"}[best["status"]]
        rows.append({"id": question["id"], "seed_id": question.get("seed_id"), "topic": question.get("topic"), "question": question["question"], "query": question.get("query"), "intents": question.get("intent", []), "priority": question.get("priority", "P2"), "business_fact_review": question.get("business_fact_review", False), "coverage": best["status"], "best_url": best["url"], "action": decision, "evidence_terms": best["required_hits"] + best["supporting_hits"], "per_page": candidates, "heading_evidence": best.get("heading_hits", [])})
    return {"schema_version": "1.0", "method": "deterministic content term evidence plus at least one required term in title/headings for COVERED; substring matching is not a claim of complete semantic response; business claims requiring confirmation are capped at PARTIAL and routed to REVIEW", "summary": {state: sum(row["coverage"] == state for row in rows) for state in ("COVERED", "PARTIAL", "MISSING")}, "questions": rows, "action_summary": {action: sum(row["action"] == action for row in rows) for action in ("KEEP", "MODIFY", "CREATE", "REVIEW")}}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pages", type=Path, required=True)
    ap.add_argument("--questions", type=Path, default=Path(__file__).with_name("questions.json"))
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    pages = json.loads(args.pages.read_text(encoding="utf-8"))
    question_payload = json.loads(args.questions.read_text(encoding="utf-8"))
    questions = question_payload["questions"]
    result = analyze(pages, questions)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status": "SUCCESS", "summary": result["summary"], "out": str(args.out)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
