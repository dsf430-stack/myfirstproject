# 意嘉行 SEO/GEO 專案狀態

- 更新時間：2026-10-01（台灣時間）
- Source of Truth：GitHub `dsf430-stack/myfirstproject` 的 `main` + 本檔
- 網站：https://dsf430-stack.github.io/myfirstproject/
- 最新網站 commit：`c9509f2d1c7129fce76979dd935c7db9c9cc5652`（PR #3）
- Pages 部署：run `36789414029` **SUCCESS**
- SEO evidence integration：run `36789414271` **SUCCESS**；不是失敗。Crawl4AI 初始安裝時間較長，但安裝、上游測試、live crawl、Jev 與 Action Engine 都完成。
- 永久 checkpoint：`tools/seo-evidence/yao_geo/checkpoints/2026-10-01/`

## DONE

- 保留既有 Crawl4AI → Evidence → Yao GEO → Jev SEO → SEO/GEO Action Engine 流程，沒有建立第二套系統。PR #2（Yao 整合）及 PR #3（既有頁面修正）已合併 main。
- PR #3 將已確認的高雄／台南到府收送資訊及路線確認條件放在既有服務頁；加強既有污漬與洗衣成分指南；調整自然中文問題與去重。沒有新建 doorway pages，沒有把乾洗、洗鞋或特殊衣物服務寫成已提供。
- 工具版本：Crawl4AI `0.9.4`（官方 commit `133e1d92e37885dfccc03ea2e3687d06c98b7ceb`）；Jev SEO `0.1.1`；Yao GEO Skills pinned commit `0ab6432d51b5052ef7dbcb388b0a8f1e46c95e6f`。Crawl4AI 與 Jev 均使用隔離 Python venv，未污染系統 Python；DataForSEO、PageSpeed API、TypeSafe/付費 API 未使用。
- GitHub Actions：Crawl4AI 上游測試、專案 evidence 測試、Yao GEO validator/tests、Chromium/JavaScript smoke、Pages build 均 SUCCESS。
- Crawl4AI live crawl：11 個第一方 URL 全為 HTTP 200、0 錯誤；專案路徑 robots.txt 200、sitemap.xml 200（10 URLs）。原始、結構化、Markdown evidence 與 content hashes 已保存於 checkpoint。
- Query / Question Universe：116 題；107 COVERED、9 PARTIAL、0 MISSING。Action Engine：KEEP 107、MODIFY 0、CREATE 0、REVIEW 9。9 題只涉及尚未確認的乾洗／直接洗鞋服務事實；沒有將 PARTIAL 誤當成「未提供」。
- Yao GEO page/content audit：11 頁、0 findings。公開來源比較 **SUCCESS**：3 個競品頁與 4 個引用來源均成功抓取，無抓取失敗；僅比較主題與缺口，沒有複製競品文字。
- Jev audit 使用低成本離線模式：版本 0.1.1，score 60/C，20 個 crawl records、13 findings、11 technical actions。該分數受未使用付費/外部補充資料限制，不能代表搜尋排名、流量、Core Web Vitals 或 AI 引用表現。原生 audit.json、Markdown、HTML、PDF、XLSX 已永久保存在 checkpoint 報告目錄。
- Jev 對 GitHub Pages 專案子路徑以網域根目錄檢查，造成 root robots/sitemap、root .html 404、HTTP redirect、首頁 alias/canonical 等誤報。Action Engine 已把 11 個 Jev technical actions 全部設為 **REVIEW**；保留既有 project-path robots/sitemap、GSC、canonical 與首頁別名，不依這些 root-origin 誤報修改網站。

## FAILED

- 最新 main run 無失敗。歷史 run `36727771301` 曾因 CI 對官方引用頁收到 HTTP 403 而失敗；已改為明確記錄 probe 狀態並由其他證據流程繼續，後續 main run `36728426806` 與最新 run `36789414271` 均成功。不可把 403 偽裝為 HTTP 200。

## BLOCKED / REVIEW

- 尚待業主確認的服務事實：意嘉行是否提供乾洗、是否直接洗鞋、羽絨衣／西裝／絲／羊毛／皮革或麂皮的接件範圍，以及窗簾／制服／旅宿餐飲布品等項目的服務範圍和條件。未確認前維持 REVIEW，不宣稱有或沒有。
- Jev root-origin path mismatch 為工具範圍限制；不破壞既有 GitHub Pages 子路徑、GSC、SEO/GEO 設定來遷就該誤報。
- 本輪沒有 DataForSEO、PageSpeed、GSC performance data，亦沒有測量實際排名或 AI citation 增長。

## NEXT

1. 請業主確認上方列出的服務項目；對方競品提供的服務僅作研究線索，不能推論意嘉行也有或沒有。
2. 只把已確認的項目補進目前既有頁面與 FAQ/schema，沿用同一 Actions pipeline 做 build、crawl、Jev、Yao 與 Action Engine 驗證。
3. 有可用 Search Console 資料時納入後續 evidence；持續將 Jev 子路徑誤報留在 REVIEW，直到 Jev 能正確支援 project path。

## Checkpoint files

`tools/seo-evidence/yao_geo/checkpoints/2026-10-01/` 保存 `checkpoint.json`、Question-to-URL coverage、Action Engine decisions、Crawl4AI manifest/pages、Yao page audit、公開來源比較、Jev summary 及原生報告格式。GitHub Actions artifact `11131755678`（run `36789414271`）另保存完整 raw crawl evidence，artifact 到期日 2026-12-29。


## MarketingSkills integration

- 已接入 `coreyhaines31/marketingskills`，固定上游 commit `5b2c0007766c6a1cf1d53fd8fc73e979e0821022`。
- 啟用 6 個 skills：`seo-audit`、`ai-seo`、`competitor-profiling`、`cro`、`analytics`、`marketing-loops`。
- 定位為既有 pipeline 的 advisory / orchestration layer；不建立第二套 SEO 系統，不取代 Crawl4AI、Yao GEO、Jev SEO 或 Action Engine。
- CI 會 checkout 固定 commit 並驗證 6 個 `SKILL.md` contract 存在；本地 integration contract 另有 unittest。
- 商業目標：2026-10-15 前至少產生 1 個有效詢價；優先市場為長照護家／護理之家／住宿式長照。
