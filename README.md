# Dental Education Studio

第九週「換你當老闆」作業：用 `AGENTS.md` 規範一個可以持續新增牙科衛教文章的網站。

## 專案內容
- `AGENTS.md`：AI 員工手冊，寫明網站架構、可修改範圍、文章資料格式、類別清單、寫作與視覺風格、醫療內容安全規則、新增文章流程與驗收標準。
- `CLAUDE.md`：指向 `AGENTS.md`，讓 Claude 也讀同一份規則。
- `index.html`、`styles.css`、`script.js`：靜態網站，有搜尋、類別篩選，也可以用 `#文章id` 直接開啟某一篇。
- `articles/articles.json`：文章資料，含文章、選填封面及多張內文示意圖；審核狀態依資料紀錄。
- `tools/check_articles.py`：依照 AGENTS.md 檢查文章格式。

## 本機預覽
```bash
python3 tools/check_articles.py     # 檢查文章格式
python3 -m http.server 8000         # 開啟 http://localhost:8000
```

## 圖片與本機審閱

每篇文章可有獨立 `cover` 及 `images` 陣列。專屬封面缺少、未核准或載入失敗時使用統一封面；預設封面也不可用時顯示 CSS 文字底圖。正式顯示只採用已核准圖片。內文圖完整縮放，不裁切；載入失敗以替代文字說明。

以 `python3 -m http.server 8000` 啟動後，在本機網址加入 `?review=1` 可查看有清楚待審核標記的圖片草稿。此開關限 loopback 主機，不能用於對外發布。統一封面及 IMF 圖片已依 Codex 對話的明確確認記錄審核；其餘圖片仍須逐張確認。

圖片資料範例（核准前 reviewed_by、reviewed_on 為 null）：

```json
{
  "src": "articles/images/example.svg",
  "alt": "以病人能理解的方式描述圖中重點",
  "caption": "圖片說明",
  "width": 960,
  "height": 600,
  "source": "作者／機構、原始來源或本專案原創說明",
  "license": "已確認的使用授權與範圍",
  "sha256": "以 sha256sum 計算的檔案雜湊",
  "review_status": "待醫師審核",
  "reviewed_by": null,
  "reviewed_on": null
}
```

圖檔存放於 `articles/images/`，統一封面設定在 `articles/image-settings.json`。審核須同時確認圖片、替代文字與圖說；修改後重新審核。圖片來源與授權不得留空，不使用任意網路圖片或外部 CDN。

## GitHub Pages 部署

沿用 Repository → Settings → Pages → Build and deployment → **Deploy from a branch → main → /(root)**。合併到 main 後由既有 GitHub Pages 流程更新網站，不需改為 GitHub Actions，也不需另行建置。

```bash
python3 tools/check_articles.py
python3 -m unittest discover -s tools -p 'test_*.py'
```

`.github/workflows/checks.yml` 僅執行格式與測試，不負責發布。審核狀態供醫師確認，不是整站發布的強制檢查；待審核文章保持原標示，不自動認定通過。未核准專屬圖片不對外顯示，改用已核准的預設封面；未核准的內文圖僅供本機審閱。若預設封面也無法使用，以 CSS 文字底圖替代。

合併與發布依當次使用者授權進行，並在 Actions 查看 pages build and deployment 的結果。

## 重複使用驗收
交辦給 AI 的指令：
> 先讀 AGENTS.md，新增一篇「拔牙後如何照護」的衛教文章，遵守現有資料格式，保留舊文章，新增內容標示待醫師審核，完成後執行檢查工具並確認頁面。

第 4 篇〈拔牙後，回家要注意什麼？〉就是照這個流程新增的：只修改了 `articles/articles.json`，沒有改任何程式。

## 注意
本站內容為作業示範草稿，未經醫師審核及文獻查證，不可當作正式醫療建議。
