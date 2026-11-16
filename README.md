# Dental Education Studio

第九週「換你當老闆」作業：用 `AGENTS.md` 規範一個可以持續新增牙科衛教文章的網站。

## 專案內容
- `AGENTS.md`：AI 員工手冊，寫明網站架構、可修改範圍、文章資料格式、類別清單、寫作與視覺風格、醫療內容安全規則、新增文章流程與驗收標準。
- `CLAUDE.md`：指向 `AGENTS.md`，讓 Claude 也讀同一份規則。
- `index.html`、`styles.css`、`script.js`：靜態網站，有搜尋、類別篩選，也可以用 `#文章id` 直接開啟某一篇。
- `articles/articles.json`：文章資料，目前 4 篇，全部標示「待醫師審核」。
- `tools/check_articles.py`：依照 AGENTS.md 檢查文章格式。

## 本機預覽
```bash
python3 tools/check_articles.py     # 檢查文章格式
python3 -m http.server 8000         # 開啟 http://localhost:8000
```

## GitHub Pages 部署
1. 建立公開的 GitHub Repository，例如 `dental-education-studio`。
2. 上傳本專案所有檔案，保留 `articles`、`tools` 資料夾結構。
3. 到 Repository 的 **Settings → Pages → Build and deployment**，選擇 **Deploy from a branch**、`main`、`/(root)`，然後儲存。
4. 大約 1–2 分鐘後，網站網址會是 `https://你的帳號.github.io/dental-education-studio/`。

## 重複使用驗收
交辦給 AI 的指令：
> 先讀 AGENTS.md，新增一篇「拔牙後如何照護」的衛教文章，遵守現有資料格式，保留舊文章，新增內容標示待醫師審核，完成後執行檢查工具並確認頁面。

第 4 篇〈拔牙後，回家要注意什麼？〉就是照這個流程新增的：只修改了 `articles/articles.json`，沒有改任何程式。

## 注意
本站內容為作業示範草稿，未經醫師審核及文獻查證，不可當作正式醫療建議。
