#!/usr/bin/env python3
"""Attach Crawl4AI page evidence to Jev's existing audit.json by URL."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit


def url_key(value: str) -> str:
    parts = urlsplit(value)
    path = parts.path or "/"
    if path != "/":
        path = path.rstrip("/")
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), path, "", ""))


def attach(audit: dict, pages: list[dict], manifest: dict, manifest_path: str) -> dict:
    by_url = {}
    for page in pages:
        evidence = {
            "source": "Crawl4AI",
            "url": page.get("url"),
            "final_url": page.get("final_url"),
            "http_status": page.get("http_status"),
            "title": page.get("title"),
            "meta_description": page.get("meta_description"),
            "canonical": page.get("canonical"),
            "headings": page.get("headings", {}),
            "markdown": page.get("markdown"),
            "raw_html": page.get("raw_html"),
            "links": page.get("links", {}),
            "images": page.get("images", []),
            "schema": page.get("schema", []),
            "content_sha256": page.get("content_sha256"),
            "fetched_at": page.get("fetched_at"),
        }
        for candidate in (page.get("url"), page.get("final_url")):
            if candidate:
                by_url[url_key(candidate)] = evidence

    matched = 0
    for page in audit.get("pages", []):
        evidence = by_url.get(url_key(page.get("url", "")))
        if evidence:
            page["crawl4ai_evidence"] = evidence
            matched += 1
    audit["crawl4ai_evidence"] = {
        "source": "Crawl4AI",
        "manifest": manifest_path,
        "pages_crawled": manifest.get("pages_crawled", len(pages)),
        "matched_jev_pages": matched,
        "total_jev_pages": len(audit.get("pages", [])),
        "content_hashes": {item["url"]: item["content_sha256"] for item in by_url.values() if item.get("url") and item.get("content_sha256")},
    }
    if matched == 0:
        raise ValueError("Crawl4AI evidence did not match any Jev audit page URLs")
    return audit


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--audit", type=Path, required=True)
    ap.add_argument("--pages", type=Path, required=True)
    ap.add_argument("--manifest", type=Path, required=True)
    args = ap.parse_args()
    audit = json.loads(args.audit.read_text(encoding="utf-8"))
    pages = json.loads(args.pages.read_text(encoding="utf-8"))
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    attach(audit, pages, manifest, args.manifest.as_posix())
    args.audit.write_text(json.dumps(audit, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(audit["crawl4ai_evidence"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
