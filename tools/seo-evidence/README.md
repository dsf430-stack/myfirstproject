# SEO evidence collector

Crawl4AI is the bounded **evidence collector** for the existing Jev SEO and SEO/GEO decision process. It does not replace Jev's 52 technical rules, scoring, or PDF/XLSX/Markdown report generation. No LLM or paid crawl API is used by this collector.

## Isolated installation

```bash
git clone --depth 1 --branch v0.9.4 https://github.com/unclecode/crawl4ai.git tools/crawl4ai/source
python3 -m venv tools/crawl4ai/.venv
tools/crawl4ai/.venv/bin/python -m pip install -e tools/crawl4ai/source
tools/crawl4ai/.venv/bin/python -m pip install -r tools/seo-evidence/requirements.txt
tools/crawl4ai/.venv/bin/crawl4ai-setup
tools/crawl4ai/.venv/bin/crawl4ai-doctor
tools/crawl4ai/.venv/bin/python tools/seo-evidence/collector.py --url https://dsf430-stack.github.io/myfirstproject/ --max-pages 60 --max-depth 5
```

The upstream repository is cloned at the pinned v0.9.4 release under `tools/crawl4ai/source`; its dedicated venv is separate from Jev's venv. The default crawl is HTTPS-only, same-host and restricted to the supplied project path, strips query/fragment duplicates, reads robots.txt and sitemap.xml, caps URLs and depth, and pauses between page requests. It saves raw HTML, clean Markdown, structured page data and a manifest under `seo/crawler/raw/latest/`.

The GitHub Actions workflow provides an alternate runner for installation and live validation when a local Work container cannot reach PyPI or the site. It first tests the browser against a local JavaScript fixture, then crawls the production pages, runs Jev's existing technical rules in a separate venv with Jev/PageSpeed/DataForSEO calls disabled, attaches Crawl4AI evidence to the existing Jev `audit.json`, renders Jev's existing report formats, and joins Jev priorities with question coverage. It uses `/myfirstproject/index.html` for Jev's own crawl because Jev normalizes the trailing slash and treats relative links as files at the project subpath. Evidence is retained as a workflow artifact.

Run question coverage on a collected page set:

```bash
tools/crawl4ai/.venv/bin/python tools/seo-evidence/analyze_coverage.py --pages seo/crawler/raw/latest/pages.json --out seo/crawler/reports/latest/question_coverage.json
```

Question matches are deterministic evidence for review; they do not claim that exact strings prove a complete answer. The recommendation maps `COVERED/PARTIAL/MISSING` to the existing `KEEP/MODIFY/CREATE` actions. Jev continues to own technical findings and report formats. First install/live-crawl validation is required before using the collector in production.
