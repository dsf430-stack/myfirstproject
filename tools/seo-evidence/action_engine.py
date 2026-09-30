#!/usr/bin/env python3
"""Join Jev's ranked technical actions with Crawl4AI-backed GEO coverage."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def decisions(coverage: dict, jev_audit: dict) -> dict:
    question_decision = {"COVERED": "KEEP", "PARTIAL": "MODIFY", "MISSING": "CREATE"}
    questions = []
    for row in coverage.get("questions", []):
        status = row.get("coverage")
        if status not in question_decision:
            raise ValueError(f"unknown coverage state for {row.get('id')}: {status}")
        questions.append({
            "id": row["id"], "question": row["question"], "coverage": status,
            "decision": question_decision[status], "url": row.get("best_url"),
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
    return {
        "schema_version": "1.0", "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "pipeline": ["Crawl4AI evidence", "Jev SEO audit", "SEO/GEO Action Engine"],
        "policy": "Jev keeps priority and evidence for technical actions. Technical fixes remain REVIEW until verified against source and business intent. Question coverage maps COVERED/PARTIAL/MISSING to KEEP/MODIFY/CREATE.",
        "coverage_summary": coverage.get("summary", {}), "question_actions": questions,
        "technical_actions": technical,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--coverage", type=Path, required=True)
    ap.add_argument("--jev-audit", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    coverage = json.loads(args.coverage.read_text(encoding="utf-8"))
    audit = json.loads(args.jev_audit.read_text(encoding="utf-8"))
    result = decisions(coverage, audit)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status": "SUCCESS", "question_actions": len(result["question_actions"]), "technical_actions": len(result["technical_actions"]), "out": str(args.out)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
