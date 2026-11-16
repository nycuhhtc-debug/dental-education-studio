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

## GitHub Pages 部署（需審核）

目前線上站台仍是從 main 根目錄直接發布。**合併本功能前**，先將 Repository → Settings → Pages → Build and deployment → Source 改為 **GitHub Actions**；否則舊的分支發布會繞過新檢查。這個 PR 不會自動修改線上設定或發布。

`.github/workflows/pages.yml` 在 PR 執行格式與測試，在 main 執行審核檢查後才建置和部署。未核准的文章、圖片或預設封面會阻擋產物，不上傳或部署；既有站台不因失敗而被新內容覆蓋。啟用前需核對每篇的實際核准紀錄，不能批次假定通過。

```bash
python3 tools/check_articles.py
python3 -m unittest discover -s tools -p 'test_*.py'
python3 tools/check_articles.py --publish
python3 tools/build_site.py --output _site
```

`_site` 須是不存在的目錄；發布檢查不通過時不產生目錄。產物只包含網站必要檔案及資料實際引用的已核准圖片，不包含未引用的圖稿、規則或測試。不要再手動部署儲存庫根目錄。

## 重複使用驗收
交辦給 AI 的指令：
> 先讀 AGENTS.md，新增一篇「拔牙後如何照護」的衛教文章，遵守現有資料格式，保留舊文章，新增內容標示待醫師審核，完成後執行檢查工具並確認頁面。

第 4 篇〈拔牙後，回家要注意什麼？〉就是照這個流程新增的：只修改了 `articles/articles.json`，沒有改任何程式。

## 注意
本站內容為作業示範草稿，未經醫師審核及文獻查證，不可當作正式醫療建議。
