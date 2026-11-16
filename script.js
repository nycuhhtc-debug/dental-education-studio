let allArticles=[];
const grid=document.getElementById('articles');
const dialog=document.getElementById('detail');
function escapeHtml(v){return String(v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
function render(list){grid.innerHTML=list.length?list.map(a=>`<article class="article"><span class="category">${escapeHtml(a.category)}</span><h3>${escapeHtml(a.title)}</h3><p>${escapeHtml(a.summary)}</p><button data-id="${escapeHtml(a.id)}">閱讀文章 →</button></article>`).join(''):'<p>找不到符合條件的文章。</p>';}
grid.addEventListener('click',e=>{const id=e.target.closest('button[data-id]')?.dataset.id;if(!id)return;const a=allArticles.find(x=>x.id===id);if(!a)return;document.getElementById('detail-content').innerHTML=`<span class="category">${escapeHtml(a.category)}</span><h2>${escapeHtml(a.title)}</h2><span class="status">${escapeHtml(a.review_status)}</span>${a.body.map(p=>`<p>${escapeHtml(p)}</p>`).join('')}<div class="refs"><strong>參考資料</strong><ul>${a.references.map(r=>`<li>${escapeHtml(r)}</li>`).join('')}</ul></div>`;dialog.showModal();});
document.getElementById('close').addEventListener('click',()=>dialog.close());
document.getElementById('search').addEventListener('input',e=>{const q=e.target.value.trim().toLocaleLowerCase();render(allArticles.filter(a=>[a.title,a.category,a.summary,...a.body].join(' ').toLocaleLowerCase().includes(q)));});
fetch('articles/articles.json').then(r=>{if(!r.ok)throw new Error('無法讀取文章');return r.json();}).then(data=>{allArticles=data;render(data);}).catch(()=>grid.innerHTML='<p>文章載入失敗，請使用網站伺服器或 GitHub Pages 開啟。</p>');
