#!/usr/bin/env python3
"""Bounded Crawl4AI evidence collector for a single static or JS-rendered site."""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import posixpath
import re
import socket
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
import xml.etree.ElementTree as ET
from collections import deque
from datetime import datetime, timezone
from pathlib import Path

from bs4 import BeautifulSoup

DEFAULT_URL = "https://dsf430-stack.github.io/myfirstproject/"
USER_AGENT = "YijiahangEvidenceBot/1.0 (+https://dsf430-stack.github.io/myfirstproject/)"
SKIP_EXT = re.compile(r"\.(?:jpe?g|png|gif|webp|avif|svg|ico|pdf|zip|gz|mp4|mp3|webm|woff2?|ttf|css|js|xml|json|txt|md|docx?|xlsx?|pptx?)$", re.I)
SAFE_RESPONSE_HEADERS = {"content-type", "content-language", "cache-control", "last-modified", "etag", "x-robots-tag"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def safe_response_headers(headers) -> dict[str, str]:
    """Keep useful crawl metadata while excluding cookies and auth headers."""
    return {str(k).lower(): str(v) for k, v in (headers or {}).items() if str(k).lower() in SAFE_RESPONSE_HEADERS}


def normalized_url(url: str, origin: str, path_prefix: str) -> str | None:
    """Strip query/fragment, normalize path, and reject anything outside the project path."""
    p = urllib.parse.urlsplit(urllib.parse.urljoin(origin + path_prefix, url))
    if p.scheme.lower() != "https" or p.netloc.lower() != urllib.parse.urlsplit(origin).netloc.lower():
        return None
    path = urllib.parse.unquote(p.path or "/")
    trailing = path.endswith("/")
    path = posixpath.normpath(path)
    if trailing and path != "/":
        path += "/"
    if path == ".":
        path = "/"
    prefix = path_prefix.rstrip("/")
    if path != prefix and not path.startswith(prefix + "/"):
        return None
    return urllib.parse.urlunsplit(("https", p.netloc.lower(), urllib.parse.quote(path, safe="/%:@-._~!$&'()*+,;="), "", ""))


def public_host(host: str) -> bool:
    """Refuse private or local destinations before making any request."""
    try:
        addresses = socket.getaddrinfo(host, None)
    except OSError:
        return False
    import ipaddress
    return bool(addresses) and all(not (ipaddress.ip_address(row[4][0]).is_private or ipaddress.ip_address(row[4][0]).is_loopback or ipaddress.ip_address(row[4][0]).is_link_local or ipaddress.ip_address(row[4][0]).is_reserved or ipaddress.ip_address(row[4][0]).is_multicast) for row in addresses)


def fetch_text(url: str, timeout: int = 15) -> tuple[int | None, str]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/plain,application/xml,text/xml,*/*"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, response.read(2_000_000).decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        return exc.code, ""
    except (OSError, urllib.error.URLError, TimeoutError) as exc:
        return None, f"{type(exc).__name__}: {exc}"


def read_robots(origin: str, base_url: str, path_prefix: str) -> dict:
    url = origin + path_prefix.rstrip("/") + "/robots.txt"
    status, text = fetch_text(url)
    body = text if status == 200 else ""
    parser = urllib.robotparser.RobotFileParser()
    parser.parse(body.splitlines())
    sitemap_urls = re.findall(r"(?im)^\s*sitemap:\s*(\S+)", body)
    return {
        "url": url, "status": status, "present": status == 200,
        "crawl_delay": parser.crawl_delay(USER_AGENT.split("/")[0]) or parser.crawl_delay("*"),
        "sitemaps": sitemap_urls, "parser": parser,
        "allowed": parser.can_fetch(USER_AGENT, base_url) if status == 200 else None,
        "bytes": len(body.encode("utf-8")),
    }


def sitemap_urls(urls: list[str], origin: str, prefix: str, limit: int = 500) -> tuple[list[str], list[dict]]:
    found: list[str] = []
    files: list[dict] = []
    queue = deque(urls)
    seen: set[str] = set()
    while queue and len(seen) < 10 and len(found) < limit:
        url = queue.popleft()
        if url in seen:
            continue
        seen.add(url)
        status, text = fetch_text(url)
        entry = {"url": url, "status": status, "urls": 0, "error": None}
        if status != 200:
            entry["error"] = text or f"HTTP {status}"
            files.append(entry)
            continue
        try:
            root = ET.fromstring(text)
        except ET.ParseError as exc:
            entry["error"] = f"XML parse error: {exc}"
            files.append(entry)
            continue
        tag = root.tag.rsplit("}", 1)[-1].lower()
        locs = [el.text.strip() for el in root.iter() if el.tag.rsplit("}", 1)[-1].lower() == "loc" and el.text]
        if tag == "sitemapindex":
            queue.extend(locs)
            entry["children"] = len(locs)
        else:
            for loc in locs:
                normalized = normalized_url(loc, origin, prefix)
                if normalized and normalized not in found:
                    found.append(normalized)
                    if len(found) >= limit:
                        break
            entry["urls"] = len(locs)
        files.append(entry)
    return found, files


def plain_text(html: str) -> str:
    soup = BeautifulSoup(html or "", "lxml")
    for node in soup.select("script,style,noscript,template,nav,footer,[aria-hidden='true']"):
        node.decompose()
    return " ".join(soup.stripped_strings)


def result_markdown(result) -> tuple[str, str]:
    md = getattr(result, "markdown", "") or ""
    raw = getattr(md, "raw_markdown", None)
    fit = getattr(md, "fit_markdown", None)
    if isinstance(md, str):
        raw = raw or md
    return (raw or "", fit or "")


def extract_page(html: str, final_url: str, base_origin: str, path_prefix: str) -> dict:
    soup = BeautifulSoup(html or "", "lxml")
    def meta(name: str) -> str | None:
        tag = soup.find("meta", attrs={"name": re.compile(rf"^{re.escape(name)}$", re.I)})
        return (tag.get("content") or "").strip() or None if tag else None
    canon = soup.find("link", attrs={"rel": re.compile(r"canonical", re.I)})
    canonical = urllib.parse.urljoin(final_url, canon.get("href", "").strip()) if canon and canon.get("href") else None
    headings = {f"h{i}": [" ".join(h.stripped_strings) for h in soup.find_all(f"h{i}")] for i in range(1, 4)}
    links = {"internal": [], "external": []}
    for a in soup.find_all("a", href=True):
        href = urllib.parse.urljoin(final_url, a["href"].strip())
        normalized = normalized_url(href, base_origin, path_prefix)
        row = {"href": normalized or href, "anchor": " ".join(a.stripped_strings)}
        links["internal" if normalized else "external"].append(row)
    schema = []
    for script in soup.find_all("script", attrs={"type": re.compile(r"ld\+json", re.I)}):
        raw_json = script.string or script.get_text()
        try:
            schema.append(json.loads(raw_json))
        except (json.JSONDecodeError, TypeError):
            schema.append({"_parse_error": "invalid JSON-LD", "raw": raw_json[:5000]})
    images = []
    for img in soup.find_all("img"):
        images.append({"src": urllib.parse.urljoin(final_url, img.get("src", "")), "alt": img.get("alt"), "width": img.get("width"), "height": img.get("height"), "loading": img.get("loading")})
    return {
        "title": soup.title.get_text(" ", strip=True) if soup.title else None,
        "meta_description": meta("description"),
        "canonical": canonical,
        "headings": headings,
        "links": links,
        "images": images,
        "schema": schema,
        "text": plain_text(html),
    }


async def collect(base_url: str, out_dir: Path, max_pages: int, max_depth: int, delay: float) -> dict:
    from crawl4ai import AsyncWebCrawler, BrowserConfig, CacheMode, CrawlerRunConfig

    base = urllib.parse.urlsplit(base_url)
    if base.scheme != "https" or not base.hostname:
        raise ValueError("Only an absolute HTTPS start URL is accepted")
    if base.username or base.password:
        raise ValueError("Credentials in crawl URLs are not accepted")
    if not public_host(base.hostname):
        raise ValueError("Refusing a private, local, or unresolved host")
    origin = f"https://{base.netloc}"
    prefix = base.path.rstrip("/") or "/"
    start = normalized_url(base_url, origin, prefix)
    if not start:
        raise ValueError("Start URL is outside the requested project path")

    robots = read_robots(origin, start, prefix)
    parser = robots.pop("parser")
    if robots["status"] == 200 and not parser.can_fetch(USER_AGENT, start):
        raise RuntimeError(f"robots.txt disallows the start URL: {start}")
    seed_sitemaps = robots["sitemaps"] or [origin + prefix.rstrip("/") + "/sitemap.xml"]
    seeds, sitemap_files = sitemap_urls(seed_sitemaps, origin, prefix)
    # Home is always first; sitemap pages are depth 1, then links are discovered breadth-first.
    queue = deque([(start, 0)] + [(u, 1) for u in seeds if u != start])
    queued = {u for u, _ in queue}
    visited: set[str] = set()
    pages: list[dict] = []
    out_dir.mkdir(parents=True, exist_ok=True)
    for sub in ("raw", "markdown", "structured"):
        (out_dir / sub).mkdir(exist_ok=True)
    config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS, excluded_tags=["nav", "footer"], word_count_threshold=1, exclude_external_links=False)
    browser = BrowserConfig(headless=True, user_agent=USER_AGENT)
    errors: list[dict] = []
    started = utc_now()
    async with AsyncWebCrawler(config=browser) as crawler:
        while queue and len(visited) < max_pages:
            url, depth = queue.popleft()
            if url in visited or depth > max_depth or SKIP_EXT.search(urllib.parse.urlsplit(url).path):
                continue
            visited.add(url)
            if robots["status"] == 200 and not parser.can_fetch(USER_AGENT, url):
                errors.append({"url": url, "status": None, "error": "blocked by robots.txt", "depth": depth})
                continue
            began = time.monotonic()
            try:
                result = await crawler.arun(url=url, config=config)
            except Exception as exc:  # record per-URL failure and continue bounded crawl
                errors.append({"url": url, "status": None, "error": f"{type(exc).__name__}: {exc}", "depth": depth})
                await asyncio.sleep(max(0.0, delay))
                continue
            status = getattr(result, "status_code", None)
            html = getattr(result, "html", "") or ""
            final_url = getattr(result, "redirected_url", None) or getattr(result, "url", None) or url
            safe_final = normalized_url(final_url, origin, prefix)
            if safe_final is None:
                errors.append({"url": url, "status": status, "error": "redirected outside project scope", "depth": depth})
                continue
            facts = extract_page(html, safe_final, origin, prefix)
            raw_md, fit_md = result_markdown(result)
            digest = hashlib.sha256(html.encode("utf-8", "replace")).hexdigest()
            key = hashlib.sha256(url.encode()).hexdigest()[:20]
            (out_dir / "raw" / f"{key}.html").write_text(html, encoding="utf-8")
            (out_dir / "markdown" / f"{key}.md").write_text(raw_md, encoding="utf-8")
            page = {
                "url": url, "final_url": safe_final, "http_status": status,
                "depth": depth, "fetched_at": utc_now(), "seconds": round(time.monotonic() - began, 3),
                "title": facts["title"], "meta_description": facts["meta_description"], "canonical": facts["canonical"],
                "headings": facts["headings"], "text": facts["text"], "raw_html": f"raw/{key}.html", "markdown": f"markdown/{key}.md",
                "links": facts["links"], "images": facts["images"], "schema": facts["schema"],
                "content_sha256": digest, "html_bytes": len(html.encode("utf-8", "replace")),
                "markdown_chars": len(raw_md), "fit_markdown_chars": len(fit_md),
                "response_headers": safe_response_headers(getattr(result, "response_headers", {}) or {}),
                "crawl_success": bool(getattr(result, "success", False)),
                "error": getattr(result, "error_message", None),
            }
            (out_dir / "structured" / f"{key}.json").write_text(json.dumps(page, ensure_ascii=False, indent=2), encoding="utf-8")
            pages.append(page)
            if status and status < 400:
                candidates = [x["href"] for x in facts["links"]["internal"]]
                for candidate in candidates:
                    normalized = normalized_url(candidate, origin, prefix)
                    if normalized and normalized not in visited and normalized not in queued and depth < max_depth:
                        queue.append((normalized, depth + 1))
                        queued.add(normalized)
            await asyncio.sleep(max(delay, float(robots["crawl_delay"] or 0)))

    manifest = {
        "schema_version": "1.0", "source": "Crawl4AI", "base_url": start,
        "started_at": started, "finished_at": utc_now(), "max_pages": max_pages,
        "max_depth": max_depth, "url_policy": "same origin and project path; query and fragment removed",
        "robots": robots, "sitemaps": sitemap_files, "pages_crawled": len(pages),
        "errors": errors, "pages": [{"url": p["url"], "status": p["http_status"], "sha256": p["content_sha256"], "markdown": p["markdown"]} for p in pages],
    }
    (out_dir / "pages.json").write_text(json.dumps(pages, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "crawl_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default=DEFAULT_URL)
    ap.add_argument("--out", type=Path, default=Path("seo/crawler/raw/latest"))
    ap.add_argument("--max-pages", type=int, default=60)
    ap.add_argument("--max-depth", type=int, default=5)
    ap.add_argument("--delay", type=float, default=0.5)
    args = ap.parse_args()
    if not (1 <= args.max_pages <= 500) or not (0 <= args.max_depth <= 10) or args.delay < 0:
        ap.error("max-pages must be 1–500, max-depth 0–10, and delay non-negative")
    try:
        manifest = asyncio.run(collect(args.url, args.out, args.max_pages, args.max_depth, args.delay))
    except Exception as exc:
        print(f"FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({"status": "SUCCESS", "pages": manifest["pages_crawled"], "errors": len(manifest["errors"]), "out": str(args.out)}, ensure_ascii=False))
    return 0 if manifest["pages_crawled"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
