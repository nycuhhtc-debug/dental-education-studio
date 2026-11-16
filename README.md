# Dental Education Studio

第九週「換你當老闆」Agentic Work 作業示範：使用 `AGENTS.md` 規範一個可持續新增牙科衛教文章的網站。

## 專案內容
- `AGENTS.md`：AI 員工手冊，規定網站架構、醫療內容安全與新增文章流程。
- `index.html`、`styles.css`、`script.js`：靜態網站。
- `articles/articles.json`：三篇示範衛教文章，均標示「待醫師審核」。

## 本機預覽
在專案資料夾執行 `python -m http.server 8000`，然後開啟 `http://localhost:8000`。

## GitHub Pages 部署
1. 建立公開 GitHub Repository，例如 `dental-education-studio`。
2. 上傳本專案所有檔案，保持 `articles` 資料夾結構。
3. 到 Repository **Settings → Pages → Build and deployment**，選擇 **Deploy from a branch**、`main`、`/(root)`，儲存。
4. 等待部署完成，網站網址通常為 `https://你的帳號.github.io/dental-education-studio/`。

## 重複使用驗收
交辦 AI：「先讀 AGENTS.md，新增一篇『拔牙後如何照護』的衛教文章，遵守現有資料格式、保留舊文章，新增內容標示待醫師審核，完成後檢查 JSON 與頁面。」

## 注意
本站內容為作業示範草稿，未經醫師審核及文獻查證，不可當作正式醫療建議。
