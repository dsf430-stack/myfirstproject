# MarketingSkills integration

This directory connects Corey Haines' `marketingskills` repository to the existing 意嘉行 SEO/GEO pipeline as an advisory skill layer. It does **not** create a second SEO system.

Pinned upstream commit: `5b2c0007766c6a1cf1d53fd8fc73e979e0821022`

Selected skills:
- seo-audit
- ai-seo
- competitor-profiling
- cro
- analytics
- marketing-loops

Operational order:
GSC / Google SERP → competitor-profiling → seo-audit → ai-seo → existing SEO/GEO Action Engine → cro → analytics → publish/verify → marketing-loop repeat.

The existing Action Engine remains the decision point. Crawl4AI, Yao GEO and Jev SEO remain unchanged. Paid APIs are not required for this integration.
