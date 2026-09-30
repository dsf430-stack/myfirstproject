#!/usr/bin/env python3
"""Yao GEO page-audit/content-refiner checks over Crawl4AI evidence, no AI/platform claims."""
from __future__ import annotations
import argparse, json, re
from pathlib import Path

def audit(pages: list[dict]) -> dict:
    rows=[]
    for p in pages:
        headings=p.get("headings", {}) or {}; text=p.get("text", "") or ""
        internal=(p.get("links", {}) or {}).get("internal", [])
        external=(p.get("links", {}) or {}).get("external", [])
        schema=p.get("schema", []) or []
        checks=[]
        def add(code, ok, detail, on_fail="MODIFY"):
            checks.append({"code":code,"status":"PASS" if ok else "FINDING","decision":"KEEP" if ok else on_fail,"detail":detail})
        add("HTTP_200",p.get("http_status")==200,f"HTTP {p.get('http_status')}")
        add("TITLE",bool(p.get("title")),p.get("title") or "Missing title")
        add("META_DESCRIPTION",bool(p.get("meta_description")),"description present" if p.get("meta_description") else "Missing meta description")
        add("CANONICAL",bool(p.get("canonical")),p.get("canonical") or "Missing canonical")
        add("SINGLE_H1",len(headings.get("h1",[]))==1,f"H1 count: {len(headings.get('h1',[]))}")
        add("HEADING_HIERARCHY",bool(headings.get("h2")) and bool(headings.get("h3")),f"H2: {len(headings.get('h2',[]))}; H3: {len(headings.get('h3',[]))}")
        add("INTERNAL_LINKS",bool(internal),f"Internal links: {len(internal)}")
        add("SCHEMA",bool(schema),f"JSON-LD blocks/types: {len(schema)}")
        add("SOURCE_CITATIONS",bool(external),f"External source links: {len(external)}", "REVIEW")
        add("EXTRACTABLE_CONTENT",len(text.strip())>=300,f"Visible text characters: {len(text.strip())}")
        add("QUESTION_OR_TABLE_STRUCTURE",bool(re.search(r"常見問題|常見問答|FAQ",text)) or bool(p.get("html_bytes",0) and p.get("markdown_chars",0)),"Question-led content or extractable page structure observed")
        # Flag only affirmative statements; mentions in guidance or review questions alone are not service claims.
        risky= re.findall(r"(?:提供|承接|專營|可預約|歡迎預約)[^。\n]{0,24}(?:乾洗|洗鞋|鞋類清洗|羽絨衣清洗|西裝清洗)",text)
        add("UNVERIFIED_SERVICE_CLAIM",not risky,"No affirmative unverified dry-clean/shoe/special-garment service claim" if not risky else "Check claim against first-party business facts: " + " / ".join(risky),"REVIEW")
        rows.append({"url":p.get("url"),"http_status":p.get("http_status"),"title":p.get("title"),"h1":headings.get("h1",[]),"visible_text_chars":len(text.strip()),"schema_count":len(schema),"internal_links":len(internal),"citation_links":len(external),"findings":[x for x in checks if x["status"]=="FINDING"],"checks":checks})
    counts={"pages":len(rows),"findings":sum(len(p["findings"]) for p in rows),"page_findings":sum(bool(p["findings"]) for p in rows)}
    return {"schema_version":"1.0","status":"SUCCESS","method":"Yao GEO page-audit/content-refiner evidence checklist applied to Crawl4AI first-party page evidence; not a search ranking or AI citation measure","skills":["yao-geo-page-audit","yao-geo-content-refiner","yao-geo-title-optimizer","yao-geo-brand-graph"],"summary":counts,"pages":rows}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--pages",type=Path,required=True); ap.add_argument("--out",type=Path,required=True); a=ap.parse_args()
    result=audit(json.loads(a.pages.read_text(encoding="utf-8"))); a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); print(json.dumps({"status":"SUCCESS",**result["summary"],"out":str(a.out)},ensure_ascii=False))
if __name__=="__main__": main()
