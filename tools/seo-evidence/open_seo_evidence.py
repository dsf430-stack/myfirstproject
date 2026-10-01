#!/usr/bin/env python3
"""Normalize OpenSEO market data for the existing SEO/GEO Action Engine.

This adapter deliberately does not replace Crawl4AI, Jev SEO, or Yao GEO.
It accepts a JSON snapshot produced by OpenSEO/MCP and preserves explicit
NOT_CONFIGURED/UNCERTAIN states when live credentials are unavailable.
"""
from __future__ import annotations
import argparse, json
from datetime import datetime, timezone
from pathlib import Path

ALLOWED = {"SUCCESS", "NOT_CONFIGURED", "UNCERTAIN", "FAILED"}
SECTIONS = ("keywords", "rank_tracking", "backlinks", "serp_competitors", "gsc")

def normalize(payload: dict) -> dict:
    status = payload.get("status", "UNCERTAIN")
    if status not in ALLOWED:
        raise ValueError(f"invalid OpenSEO status: {status}")
    result = {
        "schema_version": "1.0",
        "provider": "OpenSEO",
        "status": status,
        "generated_at": payload.get("generated_at") or datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "site": payload.get("site"),
        "source": payload.get("source", "OpenSEO MCP / DataForSEO"),
        "sections": {},
    }
    for name in SECTIONS:
        value = payload.get(name)
        if value is not None and not isinstance(value, (list, dict)):
            raise ValueError(f"{name} must be a list or object")
        result["sections"][name] = value
    if status != "SUCCESS":
        result["note"] = payload.get("note") or "Live OpenSEO data is unavailable; no SEO metric is inferred or fabricated."
    return result

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args=ap.parse_args()
    result=normalize(json.loads(args.input.read_text(encoding="utf-8")))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status":"SUCCESS","openseo_status":result["status"],"out":str(args.out)},ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
