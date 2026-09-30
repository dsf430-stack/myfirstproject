#!/usr/bin/env python3
"""Verify installed Crawl4AI launches Chromium and returns JavaScript-rendered text."""
from __future__ import annotations

import asyncio
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from crawl4ai import AsyncWebCrawler, BrowserConfig, CacheMode, CrawlerRunConfig


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = b"""<!doctype html><html><head><title>Browser smoke test</title></head><body><main><h1>Static shell</h1><div id='result'></div><script>document.querySelector('#result').textContent='CRAWL4AI_JS_RENDER_OK';</script></main></body></html>"""
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_args):
        pass


async def main():
    server = HTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS, word_count_threshold=1)
        async with AsyncWebCrawler(config=BrowserConfig(headless=True)) as crawler:
            result = await crawler.arun(f"http://127.0.0.1:{server.server_port}/", config=config)
        markdown = getattr(getattr(result, "markdown", ""), "raw_markdown", None) or str(getattr(result, "markdown", ""))
        html = getattr(result, "html", "") or ""
        if not getattr(result, "success", False) or "CRAWL4AI_JS_RENDER_OK" not in html or "CRAWL4AI_JS_RENDER_OK" not in markdown:
            raise RuntimeError(f"JavaScript rendering smoke test failed: success={getattr(result, 'success', None)}")
        print("SUCCESS: Chromium launched and JavaScript-rendered HTML and Markdown were captured")
    finally:
        server.shutdown()
        thread.join(timeout=3)
        server.server_close()


if __name__ == "__main__":
    asyncio.run(main())
