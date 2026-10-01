#!/usr/bin/env python3
"""Join Jev's ranked technical actions with Crawl4AI-backed GEO coverage."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def decisions(coverage: dict, jev_audit: dict, yao_audit: dict | None = None, source_comparison: dict | None = None, openseo: dict | None = None) -> dict:
    question_decision = {"COVERED": "KEEP", "PARTIAL": "MODIFY", "MISSING": "CREATE"}
    questions = []
    for row in coverage.get("questions", []):
        status = row.get("coverage")
        if status not in question_decision:
            raise ValueError(f"unknown coverage state for {row.get('id')}: {status}")
        questions.append({
            "id": row["id"], "question": row["question"], "coverage": status,
            "decision": row.get("action", question_decision[status]), "url": row.get("best_url"), "topic": row.get("topic"), "intents": row.get("intents", []), "priority": row.get("priority", "P2"),
            "evidence_terms": row.get("evidence_terms", []),
            "evidence_pages": [p for p in row.get("per_page", []) if p.get("status") != "MISSING"],
        })
    technical = []
    for action in jev_audit.get("actions", []):
        if action.get("severity") == "info":
            continue
        # A noindex finding alone does not prove the page should be indexed;
        # keep this a human review until the page's intent is confirmed.
        tech_decision = "REVIEW"
        technical.append({
            "id": action.get("action_id") or action.get("id"), "source_finding": action.get("id"),
            "priority": action.get("priority"), "category": action.get("category"),
            "decision": tech_decision, "title": action.get("title"),
            "fix": action.get("fix"), "urls": action.get("urls", []),
            "source": action.get("source"), "heuristic": action.get("heuristic", False),
        })
    allowed = {"KEEP", "MODIFY", "CREATE", "MERGE", "DELETE-NOINDEX", "REVIEW"}
    if any(row["decision"] not in allowed for row in questions):
        raise ValueError("unknown Action Engine decision")
    page_actions = []
    for page in (yao_audit or {}).get("pages", []):
        for finding in page.get("findings", []):
            page_actions.append({"page_url": page["url"], **finding})
    public_source_actions = []
    comparison = source_comparison or {}
    for gap in comparison.get("content_gaps", []):
        public_source_actions.append({"kind":"content_gap","topic":gap.get("topic"),"decision":gap.get("decision","REVIEW"),"coverage":gap.get("coverage"),"evidence_pages":gap.get("competitor_pages",[])+gap.get("first_party_pages",[])})
    for gap in comparison.get("citation_gaps", []):
        public_source_actions.append({"kind":"citation_gap","topic":gap.get("name"),"decision":gap.get("action","REVIEW"),"url":gap.get("url"),"evidence_pages":gap.get("linked_by",[])})
    return {
        "schema_version": "1.2", "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "pipeline": ["Crawl4AI", "Evidence Collection", "Yao GEO Research / Intent / Question Mining", "Jev SEO", "SEO/GEO Action Engine", "Discover", "Compare", "Decide", "Fix", "Publish", "Verify", "Repeat"],
        "policy": "Jev keeps priority and evidence for technical actions. Technical fixes remain REVIEW until verified against source and business intent. Question coverage maps COVERED/PARTIAL/MISSING to KEEP/MODIFY/CREATE.",
        "decision_vocabulary": ["KEEP", "MODIFY", "CREATE", "MERGE", "DELETE-NOINDEX", "REVIEW"],
        "coverage_summary": coverage.get("summary", {}), "action_summary": coverage.get("action_summary", {}), "question_actions": questions,
        "technical_actions": technical, "yao_page_actions": page_actions, "page_audit_summary": (yao_audit or {}).get("summary", {}),
        "public_source_actions": public_source_actions, "public_source_status": comparison.get("status", "NOT_RUN"),\n        "market_data": openseo or {"provider": "OpenSEO", "status": "NOT_CONFIGURED", "sections": {}},
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--coverage", type=Path, required=True)
    ap.add_argument("--jev-audit", type=Path, required=True)
    ap.add_argument("--yao-audit", type=Path)
    ap.add_argument("--source-comparison", type=Path)\n    ap.add_argument("--openseo", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    coverage = json.loads(args.coverage.read_text(encoding="utf-8"))
    audit = json.loads(args.jev_audit.read_text(encoding="utf-8"))
    yao_audit = json.loads(args.yao_audit.read_text(encoding="utf-8")) if args.yao_audit else None
    source_comparison = json.loads(args.source_comparison.read_text(encoding="utf-8")) if args.source_comparison else None
    openseo = json.loads(args.openseo.read_text(encoding="utf-8")) if args.openseo else None\n    result = decisions(coverage, audit, yao_audit, source_comparison, openseo)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status": "SUCCESS", "question_actions": len(result["question_actions"]), "technical_actions": len(result["technical_actions"]), "out": str(args.out)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
