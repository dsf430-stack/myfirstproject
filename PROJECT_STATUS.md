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


## UI/UX Pro Max integration（2026-10-01）

- 已將 `nextlevelbuilder/ui-ux-pro-max-skill` 的 UI/UX 原則接入現有網站品質層，不建立第二套網站；參考上游 v2.x 的 accessibility、responsive、interaction、typography 與 pre-delivery anti-pattern checks。
- 首頁已完成第一輪 UI/UX 改善：44px+ 可點擊區、鍵盤 skip link / focus-visible、CTA hover feedback、手機固定「查看服務／LINE 詢價」、手機 safe-area、Hero 服務重點 chips、FAQ 卡片化、連結辨識、版面與字級響應式優化、reduced-motion 保留。
- 未修改既有 SEO title/meta/canonical/schema 內容、服務事實、URL 架構、Crawl4AI/Yao GEO/Jev/Action Engine；乾洗、洗鞋等未確認服務仍維持 REVIEW。
- UI commits：`a0d731c0b9348f7b48d07ff27809f09bebd0aea4`、`1d5d43d0013956d9a07a02059e920759b37a360c`。
- NEXT：等待 GitHub Pages 部署後做 live desktop/mobile smoke；若 CI 或 live render 有問題，僅修 UI 層，不回退已驗證 SEO/GEO。

## 2026-10-02 當日執行 checkpoint

- 商業目標不變：2026-10-15 前至少 1 個有效客戶詢價；尚未確認達標。
- GSC settled through：2026-09-29。15+ 字 query = 0；10+ 字 query = 0，因此依既定規則改優先處理收錄、曝光、頁面可發現性與 CRO。
- GSC page performance（近 28 settled days）：首頁 28 impressions / 0 clicks / avg position 3.79；clinic 8 / 0 / 2.50；kaohsiung-commercial 7 / 0 / 2.43。
- 長照頁 URL Inspection：NEUTRAL；coverage = URL is unknown to Google；last crawl = null。這是目前長照頁主要 SEO 阻塞，非 robots/noindex 或 CI build failure。
- sitemap 已於 2026-10-02 重新提交，0 warnings / 0 errors；本輪不重複提交。
- CRO 修改 commit：`c21cd7ffbcdf1845c4be0043c62bb5c799743cc2`。長照頁首屏新增直接 LINE 詢價入口與「地區＋主要布品＋大約數量＋每天/每週頻率」最小詢價格式；未新增未確認服務、價格、認證、消毒或效果承諾。
- Pages deployment run `36963259202`：SUCCESS。
- SEO evidence run `36963259864`：SUCCESS。
- NEXT：不要重複改長照頁文案或重送 sitemap；優先提升長照 URL 的站內發現訊號與追蹤 GSC 首次 crawl/indexing，待 query 出現後再依 15+ / 10+ 長尾與 position 10–20 規則做下一輪 on-page 修改。

### 2026-10-02 continuation — discovery signal

- Confirmed long-term-care URL already has internal links from homepage, Kaohsiung, Tainan and clinic pages; no missing-link fix was needed.
- Found sitemap freshness mismatch: long-term-care page changed on 2026-10-02 while sitemap lastmod still said 2026-09-30. Fixed only this evidence-backed mismatch in commit `96b5cce6084256d93c12ecb5d5e412ec16adcce5`.
- Public SERP research confirms the target market vocabulary includes 一般護理之家、住宿式長照機構、老人福利機構; official/public sources also show bed/linen storage and laundry-room context. Treat these as market/evidence vocabulary, not as claims that 意嘉行 provides any unconfirmed process or compliance service.
- Do not create extra doorway pages from these terms. Keep the existing long-term-care page as the primary target until Google first crawls/indexes it.
- NEXT: verify Pages deployment for `96b5cce`; after deploy, continue GSC inspection tracking. Do not resubmit sitemap unless evidence changes.

### 2026-10-02 continuation — homepage discovery path

- Latest prior Pages run `36979367475` for checkpoint `9b412b0`: SUCCESS. SEO evidence `36979368366` was still running when this continuation began.
- GSC recheck: long-term-care URL remains `URL is unknown to Google`, last crawl null. Settled through 2026-09-29; query rows remain 0; page rows remain homepage 28 impressions, clinic 8, Kaohsiung commercial 7, all 0 clicks.
- Existing homepage industry card already linked to long-term-care. Found an earlier high-priority audience block stating 長照護家／護理之家 are the priority audience but it was plain text. Added one descriptive first-party link from that priority block to the existing long-term-care canonical URL; no new page and no new service claim. Commit `40ccc782b85c816d30f374acae0dc49a9f44f845`.
- New runs: Pages `36979553647`; SEO evidence `36979554233`. Verify before further on-page changes.
- NEXT: after successful deploy/evidence, re-inspect long-term-care URL. Do not add more internal links unless crawl/index evidence still fails after Google has had time to process the deployed discovery signal.

## SEO Command Center integration — zero-spend mode (2026-10-02)

- Added `testedmedia/seo-command-center` as an optional quantitative intelligence layer, pinned to upstream commit `41b9603968588d9a6175248c653107b82173391a` (MIT).
- Integration contract: `tools/seo-evidence/seo_command_center/integration.json`.
- Mode is explicitly `zero-spend`: `enabled=false`, `paid_api_calls_allowed=false`. No DataForSEO credentials are stored and no DataForSEO API/setup balance call was executed.
- Position in the existing system only: SEO Command Center/DataForSEO → Crawl4AI → Yao GEO → Jev SEO → SEO/GEO Action Engine. It does not create a second SEO system and does not replace GSC/public evidence.
- Intended future capabilities if paid access is explicitly enabled later: rank tracking, keyword research, competitor gap, AI Overview visibility, site health, link gap, local map grid, Site Explorer.
- Integration commit: `5d619571ed99cecfb39e594cd4ed953bf53e26f5`.
- COST STATE: USD 0 incurred by this integration. Do not enable paid DataForSEO calls without an explicit future user instruction.

### 2026-10-02 continuation — validation and conversion measurement audit

- Latest zero-spend integration verification completed: Pages run `36985132566` SUCCESS; SEO evidence run `36985132959` SUCCESS. Earlier SEO evidence runs `36979554233` and `36979368366` also SUCCESS. Cancelled Pages runs were superseded by later commits, not build failures.
- GSC recheck remains settled through 2026-09-29: homepage 28 impressions / 0 clicks / avg position 3.79; clinic 8 / 0 / 2.50; Kaohsiung commercial 7 / 0 / 2.43; query rows 0.
- Long-term-care inspection remains `URL is unknown to Google`, last crawl null. Sitemap remains pending with 0 warnings / 0 errors. Because the 2026-10-02 discovery changes have not yet been processed, do not add more links/content or resubmit the sitemap this round.
- Conversion measurement audit found no repository code for gtag, Google Tag Manager, dataLayer, analytics, or conversion events. Therefore the site currently has no verified first-party event instrumentation for LINE CTA clicks. Do not claim LINE clicks or valid inquiries from SEO without an external verified source.
- No paid SEO API calls were made; SEO Command Center remains zero-spend and disabled for DataForSEO.
- NEXT: wait for new GSC maturity / first crawl signal before further long-term-care on-page changes. Separately, if an existing analytics property/measurement ID becomes available, add privacy-safe LINE CTA click measurement into the existing site rather than creating a second analytics system.

### 2026-10-02 continuation — homepage CTR intent alignment

- Checkpoint `e0118b42` triggered Pages run `36986368637` and SEO evidence run `36986369225`; both were still in progress at the start of this round.
- GSC remains settled through 2026-09-29 with no query rows and no first crawl for long-term-care. No further long-term-care edits or sitemap resubmission were made.
- CTR audit of the three pages with impressions found titles/descriptions already specific. Public SERP evidence repeatedly uses 到府收送 as a core Kaohsiung/Tainan laundry intent, and 意嘉行's Kaohsiung/Tainan pickup/delivery is already a confirmed business fact present in the homepage description.
- Changed homepage title only from `意嘉行｜高雄・台南洗毛巾、洗衣服、床單床巾送洗` to `高雄台南洗衣到府收送｜毛巾、衣物、床單床巾｜意嘉行`. Commit `c8f40edca523f5c2bc96ee71d04385caceffe897`.
- This is a CTR/search-intent alignment change, not a new service claim. Do not change it again until post-change GSC data matures enough to compare impressions/CTR.
- NEXT: verify Pages + SEO evidence for `c8f40ed`; then wait for settled post-change GSC data before judging title performance. Continue long-term-care crawl/index monitoring separately.
