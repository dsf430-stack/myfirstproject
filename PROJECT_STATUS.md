# 意嘉行 SEO/GEO 專案狀態

- 更新時間：2026-09-30（台灣時間）
- Source of Truth：GitHub `dsf430-stack/myfirstproject` 的 `main`
- 網站：https://dsf430-stack.github.io/myfirstproject/
- 最新成功網站部署 commit：`63b9bd0a4072de33b6e4664829daf9f52a54d224`（2026-09-30；此後只更新此 checkpoint）
- 建立本檔時的基準 commit：`26c40ad362377036d483a3b6af9fb95b83d0f58c`
- 目的：把 Crawl4AI 作為 Evidence Collector，接到既有 Jev SEO 與 SEO/GEO Action Engine，不建立第二套 SEO 系統。

## DONE

- 找到網站 repo：`dsf430-stack/myfirstproject`，預設分支為 `main`。
- 讀取 main 最新樹與首頁、robots.txt、sitemap.xml、Lighthouse workflow、README 和服務頁。main 有 10 個 sitemap URL、允許爬取的 robots.txt、canonical、首頁 JSON-LD/FAQ、服務頁與高雄/台南頁。
- 已確認既有首頁視覺、GSC 驗證檔、canonical、JSON-LD、robots.txt 與 sitemap；沒有發現 `AGENTS.md`。本次加入圖片 dimensions、兩頁 Open Graph metadata，並同步 7 個修改頁面的 sitemap lastmod；GitHub Pages 部署成功。
- 找到既有 Jev SEO 工作目錄：`/workspace/scratch/bf88c2814588`。Jev 原始碼副本為 `.jev-seo`，獨立 Python 3.12.14 venv 為 `.venv-jevseo`；上游 Jev repo 工作樹乾淨，HEAD `55a184a`。
- Jev `doctor` 在將既有 venv 加入 PATH 後通過；依賴齊全。未配置 `TYPESAFE_API_KEY`、PageSpeed key、DataForSEO credentials；DataForSEO 未使用。Jev 文件指出沒有 Jev key 時仍可執行技術稽核，內容判讀會明確標為未評估。
- Jev 版本 `0.1.1`、上游 HEAD `55a184a3b0d0`；安裝在 `/workspace/scratch/bf88c2814588/.venv-jevseo`，原始碼位於 `.jev-seo`，venv 未污染系統 Python。
- Jev `doctor` 通過；38 個離線測試通過，0 失敗。
- 最終免費 audit 使用 `--no-jev --no-psi`；未使用 DataForSEO，花費 $0。因缺少 `TYPESAFE_API_KEY` 和 PageSpeed key，Jev 內容判讀與 PageSpeed 未評估；整體分數是 partial。
- 最終報告位於 `jev-seo-reports/final-2026-09-30/`：`audit.json`、`digest.md`、`report.md`、`report.pdf`、`report.xlsx`、`SEO_GEO_Action_Engine_Review.md`。PDF 共 14 頁，已抽查版面。

## FAILED / 已排除的方法

- 目前執行工作目錄不是 Git repo；無法在該目錄直接 clone/pull 網站 repo。
- 系統 DNS 對 GitHub Pages 主機無法解析；但 GitHub API、git clone 和 PyPI 可經環境代理使用。本次 live crawl 在單一 Jev 程序中，僅對精確主機 `dsf430-stack.github.io` 暫時使用 GitHub 官方 Pages 公開 IP 通過 SSRF DNS guard；實際 HTTP 仍經代理。未改系統 DNS 或 Jev 原始碼。
- 曾把 Jev 的 bash launcher 當 Python 檔執行，得到 SyntaxError。根因是 launcher 使用 bash；有效方式是將既有 `.venv-jevseo/bin` 加到 PATH 後呼叫 launcher。Jev doctor 與單元測試已用有效方式通過。
- Crawl4AI 與 Playwright 在此執行環境尚未安裝。不要宣稱已安裝、跑過 browser smoke test 或抓取網站。

## BLOCKED

- Crawl4AI 尚未安裝或測試；本次依使用者明確指定範圍完成 Jev SEO 安裝與 audit，Crawl4AI 保留為獨立後續階段。
- 本次沒有 Jev 內容判讀、PageSpeed/Core Web Vitals 或 DataForSEO 排名資料；不可從此報告推論搜尋排名、自然流量或 GEO 引用改善。
- SEO/GEO Action Engine 未發現獨立程式入口；已將 Jev 52-rule audit 作為 evidence source，並透過本次審核紀錄接入既有 Discover → Compare → Decide → Fix → Verify → Repeat 循環，不另造 audit。
- Jev 0.1.1 對 GitHub Pages 專案子路徑有 base-path / 尾斜線誤報；本次已用 live path 檢查辨識並標記，不依原始假陽性修改 GSC 或 SEO 結構.

## Audit evidence 注意事項

- 最終 crawl 使用 `/myfirstproject/index.html` 讓內頁相對連結保留 project path；記錄 20 個 URL，其中 10 個網站正確子路徑頁面均為 HTTP 200。另有 9 個根網域 `.html` 404、主機根目錄 robots/sitemap 未找到及 canonical/首頁別名重複，均為 Jev 子路徑/斜線正規化誤報。
- 以 live fetcher 獨立確認 `/myfirstproject/robots.txt` 與 `/myfirstproject/sitemap.xml` 為 HTTP 200；sitemap 有 10 個 URL。網站子路徑的 HTTP 首頁回傳 301 並轉到 HTTPS。
- 初版有 6 張首頁/服務圖缺 intrinsic dimensions；補齊全站 7 張未定尺寸圖片後，final audit 不再出現 `images_dimensions`。去漬指南與洗衣成分指南補 OG tags 後，final audit 不再出現 `og_missing`。
- final audit：60 / C / partial、12 actions；缺 Jev judgments 與 PageSpeed。分數和以下指標都不作排名或流量預測。`slow_ttfb` 受代理測量延遲影響；中文「薄內容」以空白切詞不可靠；P1 根網域 404 不能代表專案路徑頁面故障。
- GSC 驗證 HTML 檔、canonical 與主要 JSON-LD 未改；sitemap 日期已依 7 個修改頁面更新.

## NEXT

1. 續接時先讀取本檔與 main；若仍在目前 workspace，沿用 `.venv-jevseo`，不要重裝 Jev。後續 audit 使用本次子路徑審核規則，DataForSEO 維持不用。
2. 將 Crawl4AI 官方 repo 安裝於網站 repo 專用 `tools/crawl4ai/.venv` 或同等獨立目錄；不得複用或改動 Jev venv。先鎖定官方版本與 commit，再依官方 doctor / tests / smoke test 驗證。
3. 建立受限深度、同網域、URL 去重、去 query/fragment 的 crawl；以 robots/sitemap/首頁發現頁面，保留原始結果和乾淨 Markdown/metadata/links/schema/images/hash。
4. 先用 Crawl4AI 建立當前 live evidence，再處理 Jev 輸入銜接和現有 Action Engine 對接；保留 COVERED/PARTIAL/MISSING 與 KEEP/MODIFY/CREATE/MERGE/DELETE-NOINDEX/REVIEW 規則。
5. 若新增 Jev path-aware 支援，先補離線回歸測試，再重跑 technical audit；GSC 和 sitemap 根目錄檢查仍須按 GitHub Pages 子路徑核對。
6. 如使用者要求 Crawl4AI 階段，裝在獨立 venv，不修改 Jev venv；之後依 live evidence 接入 Action Engine。修改後 build/test/crawl/audit/verify 前後差異，更新本檔並只提交已驗證的變更。

## Reproducible environment facts

- OS：Ubuntu 24.04 x86_64；Python：3.12.14；Git：2.51.1。
- Crawl4AI official README currently identifies release v0.9.4 (2026-09-23); local installation status: **BLOCKED / NOT INSTALLED**.
- Avoid DataForSEO and all unconfigured paid/LLM APIs for the first Crawl4AI phase.
