// Dental Education Studio — 讀取 articles/articles.json 並渲染文章
// 新增文章只需修改 JSON，不需要改這個檔案（見 AGENTS.md）。

let allArticles = [];
let activeCategory = '全部';

const grid = document.getElementById('articles');
const filters = document.getElementById('filters');
const searchInput = document.getElementById('search');
const dialog = document.getElementById('detail');

function escapeHtml(v) {
  return String(v).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}

function renderFilters() {
  const categories = ['全部', ...new Set(allArticles.map(a => a.category))];
  filters.innerHTML = categories.map(c =>
    `<button class="chip${c === activeCategory ? ' active' : ''}" data-cat="${escapeHtml(c)}">${escapeHtml(c)}</button>`
  ).join('');
}

function render() {
  const q = searchInput.value.trim().toLocaleLowerCase();
  const list = allArticles.filter(a =>
    (activeCategory === '全部' || a.category === activeCategory) &&
    [a.title, a.category, a.summary, ...a.body].join(' ').toLocaleLowerCase().includes(q)
  );
  grid.innerHTML = list.length
    ? list.map(a => `<article class="article"><span class="category">${escapeHtml(a.category)}</span><h3>${escapeHtml(a.title)}</h3><p>${escapeHtml(a.summary)}</p><button data-id="${escapeHtml(a.id)}">閱讀文章 →</button></article>`).join('')
    : '<p>找不到符合條件的文章。</p>';
}

function openArticle(id) {
  const a = allArticles.find(x => x.id === id);
  if (!a) return;
  const statusClass = a.review_status === '醫師已審核' ? 'status ok' : 'status';
  document.getElementById('detail-content').innerHTML =
    `<span class="category">${escapeHtml(a.category)}</span>` +
    `<h2>${escapeHtml(a.title)}</h2>` +
    `<span class="${statusClass}">${escapeHtml(a.review_status)}</span>` +
    (a.updated ? `<span class="updated">更新：${escapeHtml(a.updated)}</span>` : '') +
    a.body.map(p => `<p>${escapeHtml(p)}</p>`).join('') +
    (a.image && typeof a.image.src === 'string' && /^articles\/images\/[a-z0-9-]+\.svg$/.test(a.image.src) && typeof a.image.alt === 'string'
      ? `<figure class="article-figure"><img src="${escapeHtml(a.image.src)}" alt="${escapeHtml(a.image.alt)}" width="840" height="1500" /><figcaption>飲食進階示意圖｜每一步皆依醫師指示</figcaption></figure>` : '') +
    `<div class="refs"><strong>參考資料</strong><ul>${a.references.map(r => `<li>${escapeHtml(r)}</li>`).join('')}</ul></div>`;
  if (!dialog.open) dialog.showModal();
  if (location.hash !== '#' + id) history.replaceState(null, '', '#' + id);
}

function closeArticle() {
  dialog.close();
}

dialog.addEventListener('close', () => {
  if (allArticles.some(a => '#' + a.id === location.hash)) history.replaceState(null, '', location.pathname);
});

grid.addEventListener('click', e => {
  const id = e.target.closest('button[data-id]')?.dataset.id;
  if (id) openArticle(id);
});

filters.addEventListener('click', e => {
  const cat = e.target.closest('button[data-cat]')?.dataset.cat;
  if (!cat) return;
  activeCategory = cat;
  renderFilters();
  render();
});

document.getElementById('close').addEventListener('click', closeArticle);
searchInput.addEventListener('input', render);
window.addEventListener('hashchange', () => openArticle(location.hash.slice(1)));

fetch('articles/articles.json')
  .then(r => { if (!r.ok) throw new Error('無法讀取文章'); return r.json(); })
  .then(data => {
    allArticles = data;
    renderFilters();
    render();
    if (location.hash) openArticle(decodeURIComponent(location.hash.slice(1)));
  })
  .catch(() => { grid.innerHTML = '<p>文章載入失敗，請使用網站伺服器或 GitHub Pages 開啟。</p>'; });
