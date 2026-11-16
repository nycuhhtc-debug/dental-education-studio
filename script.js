// Dental Education Studio — 讀取 articles/articles.json 並渲染文章
// 新增文章只需修改 JSON，不需要改這個檔案（見 AGENTS.md）。

let allArticles = [];
let activeCategory = '全部';
let defaultCover = null;
// Draft images are visible only in explicitly requested local review sessions.
const reviewMode = ['localhost', '127.0.0.1', '[::1]'].includes(location.hostname) &&
  new URLSearchParams(location.search).get('review') === '1';

const grid = document.getElementById('articles');
const filters = document.getElementById('filters');
const searchInput = document.getElementById('search');
const dialog = document.getElementById('detail');

function escapeHtml(v) {
  return String(v).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}

function validImage(image) {
  return image && typeof image.src === 'string' &&
    /^articles\/images\/[a-z0-9-]+\.(svg|png|webp|jpg|jpeg)$/.test(image.src) &&
    typeof image.alt === 'string' && image.alt.trim() &&
    Number.isInteger(image.width) && image.width > 0 && image.width <= 20000 &&
    Number.isInteger(image.height) && image.height > 0 && image.height <= 20000 &&
    (image.review_status === '醫師已審核' || reviewMode);
}

function imageMarkup(image, cover = false, fallback = false) {
  if (!validImage(image)) return '';
  const pending = image.review_status !== '醫師已審核';
  return `<img src="${escapeHtml(image.src)}" alt="${escapeHtml(image.alt)}" width="${image.width}" height="${image.height}" loading="lazy" decoding="async" data-kind="${cover ? 'cover' : 'figure'}"${fallback ? ' data-fallback="true"' : ''} />` +
    (pending ? '<span class="image-review">圖片待醫師審核（本機預覽）</span>' : '');
}

function coverMarkup(article) {
  const chosen = validImage(article.cover) ? article.cover : defaultCover;
  const picture = imageMarkup(chosen, true, chosen === defaultCover);
  return `<div class="article-cover">${picture || '<span class="cover-placeholder">牙科衛教</span>'}</div>`;
}

function figuresMarkup(article) {
  return (Array.isArray(article.images) ? article.images : []).filter(validImage).map(image =>
    `<figure class="article-figure">${imageMarkup(image)}${image.caption ? `<figcaption>${escapeHtml(image.caption)}</figcaption>` : ''}</figure>`
  ).join('');
}

// Capture load failures, including cached failures, without inline event handlers.
document.addEventListener('error', event => {
  const img = event.target;
  if (!(img instanceof HTMLImageElement) || !img.dataset.kind) return;
  if (img.dataset.kind === 'cover') {
    if (!img.dataset.fallback && validImage(defaultCover)) {
      img.parentElement.innerHTML = imageMarkup(defaultCover, true, true);
    } else {
      img.parentElement.innerHTML = '<span class="cover-placeholder">牙科衛教</span>';
    }
  } else {
    const note = document.createElement('p');
    note.className = 'image-unavailable';
    note.textContent = `示意圖暫時無法顯示。${img.alt}`;
    img.replaceWith(note);
  }
}, true);

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
    ? list.map(a => `<article class="article">${coverMarkup(a)}<span class="category">${escapeHtml(a.category)}</span><h3>${escapeHtml(a.title)}</h3><p>${escapeHtml(a.summary)}</p><button data-id="${escapeHtml(a.id)}">閱讀文章 →</button></article>`).join('')
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
    figuresMarkup(a) +
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

Promise.all([
  fetch('articles/articles.json').then(r => { if (!r.ok) throw new Error('無法讀取文章'); return r.json(); }),
  fetch('articles/image-settings.json').then(r => { if (!r.ok) throw new Error('無法讀取圖片設定'); return r.json(); }).catch(() => null)
])
  .then(([data, settings]) => {
    defaultCover = settings?.default_cover;
    allArticles = data;
    renderFilters();
    render();
    if (location.hash) openArticle(decodeURIComponent(location.hash.slice(1)));
  })
  .catch(() => { grid.innerHTML = '<p>文章載入失敗，請使用網站伺服器或 GitHub Pages 開啟。</p>'; });
