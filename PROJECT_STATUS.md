# 意嘉行 SEO/GEO 專案狀態

- 更新時間：2026-09-30（台灣時間）
- Source of Truth：GitHub `dsf430-stack/myfirstproject` 的 `main`
- 網站：https://dsf430-stack.github.io/myfirstproject/
- 本次讀取的 main：`89aa10bbbf72e0d25d75e8c5ab8222ca708383fc`
- 最新成功網站部署 commit：`89aa10bbbf72e0d25d75e8c5ab8222ca708383fc`（Pages run `36727453907` SUCCESS）
- 目標：Crawl4AI 作為 Evidence Collector，接續既有 Jev SEO 與 SEO/GEO Action Engine；不建立第二套 SEO 系統。

## DONE

- 網站 repo 為 `dsf430-stack/myfirstproject`，預設分支 `main`。整合程式先在 `codex/crawl4ai-evidence-integration` 隔離分支通過驗證，再由 PR #1 合入 main，commit `89aa10bbbf72e0d25d75e8c5ab8222ca708383fc`。
- 先前網站 SEO 工作保持：圖片 dimensions、Open Graph metadata、sitemap lastmod、canonical、首頁 JSON-LD/FAQ、robots.txt、sitemap、GSC 驗證檔。本 PR 僅修正洗衣成分指南的過碳酸鈉引用網址至中華化學官方 `.com.tw` 頁，並更新 dateModified；未改 CSS/JS 或 GSC 設定。引用頁可正常開啟；main SEO workflow 將再確認 live HTTP 狀態。
- Jev SEO 仍使用獨立環境：`/workspace/scratch/bf88c2814588/.venv-jevseo`，Python 3.12.14；原始碼 `AgriciDaniel/jev-seo` commit `55a184a3b0d09565a4c84268f725a47784e62528`。Jev venv 未修改；先前 doctor 與 38 個離線測試已通過。
- Crawl4AI 官方來源在 workflow runner clone 至 `tools/crawl4ai/source`，獨立 venv 為 `tools/crawl4ai/.venv`。此兩項目錄已加入 `.gitignore`，不會把 source clone 或 venv 放進網站 repo。使用者本機 runner 對外 proxy 連線逾時；GitHub Actions Ubuntu runner 可正常連線，已用作可重現安裝與 live verification 環境。
- Crawl4AI 版本 `0.9.4`，官方 checkout commit `133e1d92e37885dfccc03ea2e3687d06c98b7ceb`。Runner：Ubuntu 24.04 x86_64、Python 3.12.14、Git 2.55.0。Playwright 1.63.0 / Chromium 153.0.8010.12 已安裝並啟動。
- 成功指令：官方 clone `git clone --depth 1 --branch v0.9.4 https://github.com/unclecode/crawl4ai.git tools/crawl4ai/source`；獨立 `python -m venv tools/crawl4ai/.venv`；`pip install -e tools/crawl4ai/source`；`crawl4ai-setup`；`crawl4ai-doctor`。doctor 的官方 HTTPS 抓取測試通過。
- 上游離線測試 `pytest tests/unit/ -q`：128 passed、6 skipped。專案自己的 7 個單元測試通過；Chromium + JavaScript fixture smoke test 通過，確認 rendered HTML 和 Markdown 都含 JS 注入內容。
- 第一次 live crawl：`https://dsf430-stack.github.io/myfirstproject/`，11 個 URL、全部 HTTP 200、0 crawl errors；project-path `robots.txt` HTTP 200；project-path `sitemap.xml` HTTP 200 並列出 10 個 URL。查詢字串與 fragment 已移除。首頁 title、description、canonical、H1/H2/H3、Markdown、22 條內鏈均成功取得。
- Evidence 輸出包含 raw HTML、乾淨 Markdown、structured JSON、`pages.json`、`crawl_manifest.json`、HTTP status、metadata/headings、internal/external links、images/alt、JSON-LD、fetch timestamp、content SHA-256。保留的 response headers 僅含非敏感欄位；cookie/auth headers 有測試排除。附件 artifact 留存 90 天。
- 全站 11 個頁面都有 title、meta description、H1/H2/H3；11 組 JSON-LD、12 張圖片，圖片均有 alt。全站共擷取 121 條內鏈與 23 條外鏈。`index.html` 與首頁 canonical 相同，作為首頁別名保留。
- GEO coverage 使用既有業務問題集，8/8 為 COVERED，0 PARTIAL、0 MISSING；Action Engine 產出 8 個 KEEP。這是可追溯的詞項/頁面 evidence，不代表搜尋排名或 AI 引用保證。
- Jev 0.1.1 audit 使用既有 52-rule technical audit，停用 Jev LLM、PageSpeed 與 DataForSEO；Crawl4AI evidence 以附加欄位寫入既有 Jev `audit.json`，11 個 Jev 頁面附到 11 組 Crawl4AI evidence；Action Engine 同時取得 GEO coverage 與 Jev technical actions。Jev 原生 PDF/XLSX/Markdown 報告流程保留。
- 最終完整成功 Actions run：`36725205003`（PR branch）；上游 tests、專案 tests、Chromium/JS smoke、11 頁 live crawl、Jev audit、Action Engine 均成功。Artifact `11101724274` 含 raw evidence、Markdown/structured pages、GEO audit、Jev `audit.json`/PDF/XLSX/Markdown、Action Engine decisions；到期日 2026-12-29。連結：https://github.com/dsf430-stack/myfirstproject/actions/runs/36725205003
- 兩次成功 crawl 的 11 個 URL 在 status、title、meta、canonical、headings、content hash 上完全一致；新增 0、移除 0、內容變更 0。這次沒有網站 source 修改，故不虛報網站改善；`main` 上已驗證的既有修正保持不變。

## FAILED / 已排除的方法

- 舊 run `36722490726` 因缺少上游測試依賴 `pytest-asyncio` 和 `pypdf` 失敗；於 Crawl4AI 專用 venv 補齊依賴後，成功 run `36725205003` 的完整 job 全綠。根因是 CI 測試環境不完整，不是網站 crawl 或 Jev/Action Engine 故障。
- 本機到 PyPI/目標站的代理連線逾時；改在 GitHub Actions runner 安裝與抓取，已成功完成，不再重試本機外網方法。
- 初次 workflow 缺 pytest；之後官方 unit tests 又指出缺 `pytest-asyncio` 與 `pypdf`。三項已加在 Crawl4AI 專用 venv，128 個上游 unit tests 通過。
- 完整 `pytest tests/` 會收集上游 script-style `tests/test_cloud_bugs_batch.py`，該檔在 import 階段自行執行並 `sys.exit(1)`；因此採官方 `tests/unit/` 子集，不再重跑整個 tests 根目錄。
- 最初的 JS smoke HTML 太短，被 Crawl4AI anti-bot structural check 判為空頁；加上一般靜態正文後，Chromium/JavaScript/Markdown smoke test 通過。
- Jev 以 trailing-slash 首頁 crawl 會正規化掉斜線、造成相對連結誤判；workflow 使用已驗證的 `/myfirstproject/index.html` 作 Jev URL。Jev 對 GitHub Pages 專案子路徑的根目錄 robots/sitemap、root 404、首頁別名仍有已知誤報，依 Crawl4AI 子路徑 evidence 標為 REVIEW，不改網站。

## BLOCKED / 限制

- 沒有使用 DataForSEO、PageSpeed API 或任何付費/LLM API。Jev 內容判讀與 PSI 不執行；不得用這輪資料推論排名、流量、Core Web Vitals 或 AI citations。
- Jev CLI 沒有外部 Crawl4AI evidence import 參數；目前以 adapter 把 evidence 附到 Jev 原有 `audit.json`，Action Engine 再合併 GEO coverage 與 Jev actions，未修改 Jev upstream 原始碼或重寫其 rules。
- Jev 的 11 個 technical actions 全部保留 REVIEW。P1 根目錄 `.html` 404、root robots/sitemap、HTTP probe 和 `/index.html` canonical alias 已由既有狀態與本次 Crawl4AI path evidence 確認為 GitHub Pages 子路徑/正規化誤報；中文薄內容提示亦不能依空白切詞定論。沒有確認到需改網站的 P0/P1。
- 確定的 business facts 及現有服務頁保持不變；不捏造價格、時程、資格或案例。本輪沒有競品 crawl，競品 comparison 是後續工作。

## NEXT

1. PR #1 已合入 main；Pages deployment run `36727453907` 已 SUCCESS。此次 checkpoint commit 會觸發 main SEO evidence workflow，確認 live citation HTTP 狀態及完整 re-audit 後，補記該 run 結果。
2. 以同一 Crawl4AI collector 抓取使用者指定競品與 citation sources；只比較主題、結構、entity/question coverage、citations、schema 和內鏈，不複製文字。
3. 後續每次網站 source 修改前保存 BEFORE evidence；修正後跑 build/test/crawl/Jev/Action Engine，產生可比的 AFTER status/title/meta/headings/schema/links/question coverage/hash。
4. Jev path-aware 誤報維持 REVIEW；若未來改 Jev integration，先加 regression tests，再以 project-path robots/sitemap/live links 驗證。

## Reproducible environment facts

- Crawl4AI / Playwright 的獨立位置：`tools/crawl4ai/source`、`tools/crawl4ai/.venv`；`.gitignore` 排除兩者。
- 執行成功 workflow：`.github/workflows/seo-evidence.yml`；輸出留在 90 天 workflow artifact，不把 raw crawl、cache、venv、credentials、cookies 或 tokens commit。
