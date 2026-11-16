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

## Google Search Console 與 Sitemap

發布後的 Sitemap：
`https://nycuhhtc-debug.github.io/dental-education-studio/sitemap.xml`

目前網站只有首頁是獨立 HTML 頁面。文章透過 `script.js` 讀取 JSON，再以 `#文章ID` 開啟同一頁的視窗；片段不是另一個 HTTP 頁面。Google 可能經 JavaScript 渲染讀取首頁中的內容，但不能因此把八個 hash 網址當成八個獨立文章頁。因此 Sitemap 目前只收錄首頁，不列入 hash、圖片、JSON、Google 驗證檔、查詢參數或不存在的頁面。Sitemap 不保證 Google 收錄。

首頁已設定指向正式 HTTPS 網址（含專案路徑及結尾斜線）的 canonical，以及 `index, follow`；既有標題、描述、繁體中文語系與手機 viewport 均保留。不增加虛構作者、醫師資格或結構化醫療宣稱。

### 維護方式

```bash
python3 tools/update_sitemap.py
python3 tools/update_sitemap.py --check
python3 -m unittest discover -s tools -p 'test_*.py'
```

新增 JSON 文章時，仍屬於首頁內容，Sitemap 不會假造新的文章 URL。若未來另行實作獨立靜態文章頁，採 `articles/<id>/index.html`，頁面需包含完整標題及內文、指向自己的 canonical，且不能有 noindex。上述生成工具確認檔案存在及符合條件後才自動列入 `articles/<id>/`；有 noindex 的文章頁不收錄。這次不建立任何獨立文章頁、不更改既有 hash 路由。

新增、移除獨立文章頁後執行生成指令，將更新後的 sitemap.xml 一起提交。CI 的 `--check` 會檢查是否同步，漏更新時回報錯誤，不自行推送或合併。未使用無法確認的 lastmod 日期，亦未填入任意 priority 或 changefreq。

### robots.txt 的限制

Google 使用的是主機根目錄 `https://nycuhhtc-debug.github.io/robots.txt`。放在本專案子目錄的 `/dental-education-studio/robots.txt` 不會成為這個主機的爬蟲規則，因此本次不新增無效的子目錄 robots.txt。

本次開發環境向主機根 robots.txt 發送請求時，連線代理回覆 403，無法讀取實際內容；這不代表 Googlebot 被網站封鎖。仍須在公開環境或 Search Console 的網址檢查確認 robots 與 HTTP 層級是否允許抓取。若你能管理主機根 robots.txt，可保留原有規則並附加：

```text
Sitemap: https://nycuhhtc-debug.github.io/dental-education-studio/sitemap.xml
```

無法管理主機根 robots.txt 也能直接在 Search Console 提交 Sitemap，不需因此建立新的 GitHub repository。robots.txt 不存在不等於禁止抓取；禁止規則若存在則需由主機管理者處理。

### 提交 Google Search Console

1. 等本 PR 經確認、合併且 Pages 部署成功後，先確認公開 sitemap.xml 可開啟，回傳 XML 而非 404 頁。
2. 在 Search Console 選擇或新增「網址前置字元」資源：`https://nycuhhtc-debug.github.io/dental-education-studio/`。本專案已有 Google HTML 驗證檔，本次保留不動；是否已驗證仍以 Search Console 為準。
3. 進入「Sitemap」，在新增欄位填 `sitemap.xml`（若欄位沒有預填網站前綴，則填完整 Sitemap URL），按提交。
4. 查看讀取狀態；目前預期發現 1 個網頁。再以「網址檢查 → 測試實際網址」檢查首頁抓取、渲染及 canonical，必要時要求建立索引。
5. 未來有真實獨立文章頁並更新 Sitemap 後，Google 可重新讀取；可在 Search Console 確認新頁的發現與索引狀態。

參考：Google Search Central 的 [建立與提交 Sitemap](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap)、[JavaScript SEO 基本概念](https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics) 及 [robots.txt 位置與範圍](https://developers.google.com/search/docs/crawling-indexing/robots/intro)。
