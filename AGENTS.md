# 專案 AI Agent 協作規範

## AI Agent 省額度與工程防錯規範

- GitHub 最新 main 為程式與文件的權威來源；先核對現有 README.md、AGENTS.md（若存在）、PROJECT_STATUS.md（若存在）及與任務相關的檔案、Log、checkpoint。缺失時如實記錄，不得假裝已讀取。
- 只讀取當前任務必要的檔案與範圍；避免重複全庫掃描、重做 DONE 工作、重複安裝依賴、無目的搜尋與無限重試。不得為了省額度省略必要的官方文件查證與測試。
- 除錯先分析原始 Log、定位根因、核對官方語法或實測證據，再提出最小修復方案；未獲授權不得擴大修改。一次只變更一個核心邏輯，保護已正常運作功能。
- 優先沿用專案既有架構、快取、工具與 GitHub Actions；不重建平行系統，不擅自改用其他引擎或付費服務。
- 不自動執行付費 API、付費生成或無明確終止條件的工作；費用未知時先確認。文字規範不能替代執行環境真正的額度硬限制。
- 每個階段以可驗證證據記錄 DONE、FAILED（根因與證據）、BLOCKED、NEXT；存在 PROJECT_STATUS.md 時更新該檔，缺少時先回報並在適當授權範圍建立 checkpoint。中斷後從最後有效進度接續。
- 回報精簡列出目前狀態、實際驗證結果、阻礙與下一個最小步驟；不把計畫、提交或未執行的測試冒充完成。
- 優先順序：正確性與安全性 > 保留既有功能 > 必要驗證 > 節省額度 > 執行速度。



## GitHub × GPT × Codex/Work 接力規則

- GitHub 的最新 `main` 是唯一 Source of Truth。每次接手先讀 README.md、AGENTS.md、PROJECT_STATUS.md，再檢查任務相關程式、Actions 與測試；不得以舊對話或本機舊版本覆蓋 GitHub 現況。
- 新功能先理解既有架構與依賴，再作最小必要修改；禁止 Mock、假資料、假 API、Silent Fallback、隱藏 Default 或以假成功掩蓋失敗。
- 完成後執行專案適用的測試、Type Check、Lint、Build 與部署驗證；只回報實際執行的結果。修復錯誤前先定位根因與失敗節點。
- 每次工作更新 PROJECT_STATUS.md，記錄 DONE、FAILED（根因與證據）、BLOCKED、測試狀態及 NEXT。經授權且驗證後才 Commit / Push。
- 小型修正可直接更新 main；大型修改使用獨立 Branch，測試完成後再合併。GPT、Codex、Work 不得同時修改同一 Branch。
- 中斷或額度不足時，停止擴張任務，保存有效修改、執行可完成的測試、更新 PROJECT_STATUS.md，記錄錯誤與下一步，再 Commit / Push，讓下一個 Agent 可直接接手。
- 切換工具或新對話時，重新從 GitHub 取得最新版本與 PROJECT_STATUS.md，不依賴聊天記憶作為專案狀態。
