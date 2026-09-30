#!/usr/bin/env python3
"""Compare public competitor/source observations with first-party Crawl4AI evidence."""
import argparse, json
from pathlib import Path

TOPICS={
 "commercial_towel_laundry":["毛巾","浴巾","商用洗衣","大量洗衣"],
 "pickup_delivery":["收送","收送服務","到府"],
 "bedding_linen":["床單","床巾","床包","被套","寢具"],
 "business_customer_types":["診所","醫美","長照","髮廊","spa","復健","飯店","民宿","餐廳"],
 "pricing_and_turnaround":["價格","報價","包月","按件","交件","完成時間"],
 "special_garments_and_shoes":["乾洗","洗鞋","羽絨衣","西裝"],
 "stain_and_care_evidence":["污漬","洗標","血漬","咖啡","油漬"]
}
BUSINESS_FACT_TOPICS={"business_customer_types","pricing_and_turnaround","special_garments_and_shoes"}

def read_pages(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def page_text(page, root):
    value=" ".join(str(page.get(k) or "") for k in ("title","meta_description","text"))
    rel=page.get("markdown")
    if rel:
        try: value += " " + (Path(root)/rel).read_text(encoding="utf-8")
        except OSError: pass
    return value

def observed_topics(content):
    return [topic for topic, terms in TOPICS.items() if any(term.lower() in content.lower() for term in terms)]

def evidence_status(page, content):
    if not page or page.get("http_status") != 200:
        return "FAILED"
    title=(page.get("title") or "").strip().lower()
    text=content.strip().lower()
    challenge_titles={"one moment, please...", "just a moment...", "attention required! | cloudflare"}
    challenge=title in challenge_titles or "please wait while your request is being verified" in text or "enable javascript and cookies to continue" in text
    if challenge or len(text) < 120:
        return "UNCERTAIN"
    return "SUCCESS"

def compare(first_party, first_root, config, external_root):
    own=[(p,page_text(p,first_root)) for p in first_party]
    topic_rows=[]
    competitor_details=[]
    for competitor in config.get("competitors",[]):
        slug=competitor["name"]
        safe=competitor.get("id") or "competitor"
        folder=Path(external_root)/"competitors"/safe
        path=folder/"pages.json"
        if not path.exists():
            competitor_details.append({"name":slug,"url":competitor["url"],"status":"FAILED","reason":"Crawl4AI pages.json missing; no competitor content inferred"}); continue
        crawled=read_pages(path)
        page=next((p for p in crawled if p.get("url")==competitor["url"] or p.get("final_url")==competitor["url"]),crawled[0] if crawled else None)
        content=page_text(page,folder) if page else ""
        status=evidence_status(page,content)
        competitor_details.append({"name":slug,"url":competitor["url"],"status":status,"http_status":page.get("http_status") if page else None,"title":page.get("title") if page else None,"headings":(page.get("headings") or {}).get("h2",[]) if page else [],"observed_topics":observed_topics(content) if status=="SUCCESS" else [],"content_sha256":page.get("content_sha256") if page else None})
        if status!="SUCCESS": continue
        for topic,terms in TOPICS.items():
            if any(term.lower() in content.lower() for term in terms):
                row=next((r for r in topic_rows if r["topic"]==topic),None)
                if not row: row={"topic":topic,"competitor_pages":[],"first_party_pages":[]}; topic_rows.append(row)
                row["competitor_pages"].append(slug)
    for topic,terms in TOPICS.items():
        row=next((r for r in topic_rows if r["topic"]==topic),{"topic":topic,"competitor_pages":[],"first_party_pages":[]})
        row["first_party_pages"]=[p.get("url") for p,text in own if any(term.lower() in text.lower() for term in terms)]
        row["coverage"]="COVERED" if row["first_party_pages"] else ("MISSING" if row["competitor_pages"] else "UNCERTAIN")
        row["decision"]="KEEP" if row["coverage"]=="COVERED" else ("REVIEW" if topic in BUSINESS_FACT_TOPICS or row["coverage"]=="UNCERTAIN" else "CREATE")
        if row not in topic_rows: topic_rows.append(row)
    source_rows=[]
    all_external={link.get("href","").rstrip("/") for page,_ in own for link in (page.get("links",{}).get("external",[]) or [])}
    source_failures=[]
    for source in config.get("citation_sources",[]):
        url=source["url"].rstrip("/")
        linked=[p.get("url") for p,_ in own if any(link.get("href","").rstrip("/")==url for link in p.get("links",{}).get("external",[]) or [])]
        source_path=Path(external_root)/"citations"/(source.get("id") or "")/"pages.json"
        crawled=read_pages(source_path) if source_path.exists() else []
        source_page=next((p for p in crawled if p.get("url")==source["url"] or p.get("final_url")==source["url"]),crawled[0] if crawled else None)
        source_content=page_text(source_page,Path(external_root)/"citations"/(source.get("id") or "")) if source_page else ""
        source_status=evidence_status(source_page,source_content)
        if source_status!="SUCCESS": source_failures.append(source["name"])
        source_rows.append({"name":source["name"],"url":source["url"],"topics":source.get("topics",[]),"crawl_status":source_status,"http_status":source_page.get("http_status") if source_page else None,"linked_by":linked,"action":"REVIEW" if source_status!="SUCCESS" else ("KEEP" if linked else "MODIFY")})
    failed=[x["name"] for x in competitor_details if x["status"]!="SUCCESS"]
    all_failures=failed+source_failures
    return {"schema_version":"1.0","status":"SUCCESS" if not all_failures else "UNCERTAIN","method":"Topical/entity comparison of public Crawl4AI page evidence; no competitor wording or business claims copied","competitors":competitor_details,"competitor_crawl_failures":failed,"citation_source_crawl_failures":source_failures,"content_gaps":topic_rows,"citation_gaps":source_rows,"policy":"Unverified business/service, pricing, turnaround, medical or special-garment claims remain REVIEW; missing market facts are never invented. Failed crawls remain explicit and are never replaced with assumed success."}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--pages",required=True); ap.add_argument("--first-root",required=True); ap.add_argument("--sources",required=True); ap.add_argument("--external-root",required=True); ap.add_argument("--out",required=True); a=ap.parse_args()
    result=compare(read_pages(a.pages),a.first_root,json.loads(Path(a.sources).read_text(encoding="utf-8")),a.external_root); Path(a.out).parent.mkdir(parents=True,exist_ok=True); Path(a.out).write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); print(json.dumps({"status":result["status"],"competitors":len(result["competitors"]),"crawl_failures":result["competitor_crawl_failures"],"content_gaps":len(result["content_gaps"]),"citation_gaps":len(result["citation_gaps"]),"out":a.out},ensure_ascii=False))
if __name__=="__main__": main()
