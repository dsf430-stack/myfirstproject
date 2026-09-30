# 意嘉行 SEO/GEO 專案狀態

- 更新時間：2026-09-30（台灣時間）
- Source of Truth：GitHub `dsf430-stack/myfirstproject` 的 `main`
- 網站：https://dsf430-stack.github.io/myfirstproject/
- 最新確認 main commit：`39fb920215b26d7c6940ec7173430accbe8b3727`（2026-09-30 21:05 台灣時間確認）
- 建立本檔時的基準 commit：`26c40ad362377036d483a3b6af9fb95b83d0f58c`
- 目的：把 Crawl4AI 作為 Evidence Collector，接到既有 Jev SEO 與 SEO/GEO Action Engine，不建立第二套 SEO 系統。

## DONE

- 找到網站 repo：`dsf430-stack/myfirstproject`，預設分支為 `main`。
- 讀取 main 最新樹與首頁、robots.txt、sitemap.xml、Lighthouse workflow、README 和服務頁。main 有 10 個 sitemap URL、允許爬取的 robots.txt、canonical、首頁 JSON-LD/FAQ、服務頁與高雄/台南頁。
- 已確認 repo 最近 commit 更新首頁視覺與可及性；後續 main 又為診所與醫美頁的圖片補上固有尺寸。既有 SEO 結構仍在。沒有發現 `AGENTS.md`；此檔首次建立為跨回合狀態紀錄。
- 找到既有 Jev SEO 工作目錄：`/workspace/scratch/bf88c2814588`。Jev 原始碼副本為 `.jev-seo`，獨立 Python 3.12.14 venv 為 `.venv-jevseo`；上游 Jev repo 工作樹乾淨，HEAD `55a184a`。
- Jev `doctor` 在將既有 venv 加入 PATH 後通過；依賴齊全。未配置 `TYPESAFE_API_KEY`、PageSpeed key、DataForSEO credentials；DataForSEO 未使用。Jev 文件指出沒有 Jev key 時仍可執行技術稽核，內容判讀會明確標為未評估。
- Jev 離線單元測試：38 passed，0 failed（2026-09-30）。
- 已有報告：`jev-seo-reports/initial-2026-09-30/` 含 audit.json、digest.md、report.md、PDF、XLSX；`verified-path-2026-09-30/` 含 audit.json、digest.md。

## FAILED / 已排除的方法

- 目前執行工作目錄不是 Git repo；無法在該目錄直接 clone/pull 網站 repo。
- 執行環境對 GitHub、PyPI 與目標網站的直接網路請求逾時；GitHub MCP 只能讀寫 repo 內容，不能提供本機 clone、pip 套件安裝、Chromium 或實際網站爬取能力。
- 曾把 Jev 的 bash launcher 當 Python 檔執行，得到 SyntaxError。根因是 launcher 使用 bash；有效方式是將既有 `.venv-jevseo/bin` 加到 PATH 後呼叫 launcher。Jev doctor 與單元測試已用有效方式通過。
- Crawl4AI 與 Playwright 在此執行環境尚未安裝。不要宣稱已安裝、跑過 browser smoke test 或抓取網站。

## BLOCKED

- 無法在目前受限網路工作階段下載官方 Crawl4AI、安裝獨立 venv dependencies、安裝 Chromium、執行 Crawl4AI doctor/tests/HTTPS/browser smoke test。
- 因無法從目標網站取得即時頁面，尚不能產生 Crawl4AI crawl_manifest.json、pages.json、Markdown、structured data，或核對線上 HTTP status。
- SEO/GEO Action Engine 在網站 repo 與 Jev repo 中沒有找到獨立程式入口；既有 Jev 內建 52-rule audit 與 ranked actions 已存在。要以此作為整合基底，不可另造重複 audit。
- 不可根據舊 audit 的 broken links/404 直接修改網站：兩份舊 audit 抓取到的 URL 與當前 main 路徑/部署基底不一致，且目標站無法即時驗證。

## Audit evidence 注意事項

- `initial-2026-09-30` 抓取 10 個 pages；`verified-path-2026-09-30` 抓取 20 URLs。後者雖然能識別更多頁，但仍將多個 sitemap/service URL 列成 404，與當前 GitHub main 中確實存在的頁面檔不一致。
- 兩次 report 都標示 Jev judgments、PageSpeed 與 DataForSEO 未完成；整體分數受「HTTPS 未驗證」限制。這些是歷史掃描紀錄，不是本輪即時驗證結果。
- GitHub main 已確認 robots.txt 與 sitemap.xml 存在；首頁有 canonical、JSON-LD（LocalBusiness/WebSite/WebPage/Service/FAQPage）與 FAQ。不要重做這些完成項目。

## NEXT

1. 在可連外的 repo 工作環境續接；先讀取本檔與 main，再沿用 `.venv-jevseo`，不要重裝 Jev。
2. 將 Crawl4AI 官方 repo 安裝於網站 repo 專用 `tools/crawl4ai/.venv` 或同等獨立目錄；不得複用或改動 Jev venv。先鎖定官方版本與 commit，再依官方 doctor / tests / smoke test 驗證。
3. 建立受限深度、同網域、URL 去重、去 query/fragment 的 crawl；以 robots/sitemap/首頁發現頁面，保留原始結果和乾淨 Markdown/metadata/links/schema/images/hash。
4. 先用 Crawl4AI 建立當前 live evidence，再處理 Jev 輸入銜接和現有 Action Engine 對接；保留 COVERED/PARTIAL/MISSING 與 KEEP/MODIFY/CREATE/MERGE/DELETE-NOINDEX/REVIEW 規則。
5. 依新 evidence 重跑 Jev 技術 audit，排除錯誤 base path/舊 audit 假陽性；只對 live evidence 支持且低風險的網站問題修改。
6. 修改後 build/test/crawl/audit/verify 前後差異，更新本檔並只提交已驗證的變更。

## Reproducible environment facts

- OS：Ubuntu 24.04 x86_64；Python：3.12.14；Git：2.51.1。
- Crawl4AI official README currently identifies release v0.9.4 (2026-09-23); local installation status: **BLOCKED / NOT INSTALLED**.
- Avoid DataForSEO and all unconfigured paid/LLM APIs for the first Crawl4AI phase.
