# 6) Sortieren: kleine Übersicht, nach Wichtigkeit ziehen; dazu Kategorien (Übertitel) mit Beschluss-Feld.
#    Reihenfolge im Feld «order», Kategorie im Feld «cat» des Zettels; Kategorien an der Pinnwand: board.cats = [{ id, title, note }]
rep('''  return [...S.ideas].filter(([, i]) => i.status === "ok" && inBoard(i)).sort((a, b) => (a[1].okAt || a[1].at || 0) - (b[1].okAt || b[1].at || 0));''',
    '''  const ord = i => typeof i.order === "number" ? i.order : 1e9;
  return [...S.ideas].filter(([, i]) => i.status === "ok" && inBoard(i)).sort((a, b) => catIdx(a[1]) - catIdx(b[1]) || ord(a[1]) - ord(b[1]) || (a[1].okAt || a[1].at || 0) - (b[1].okAt || b[1].at || 0));''')
rep('''  html += tabsHTML([["board", "Pinnwand"], ["baro", "Barometer"], ["rank", "Rangliste"]]);''',
    '''  html += tabsHTML([["board", "Pinnwand"], ["sort", "Sortieren"], ["baro", "Barometer"], ["rank", "Rangliste"]]);''')
rep('''  if (S.tab === "rank") return html + rankHTML(items, res);
  const boardItems = items.filter(([, i]) => !toolsOf(i).baro), nb''', '''  if (S.tab === "rank") return html + rankHTML(items, res);
  if (S.tab === "sort") return html + sortHTML(items);
  const boardItems = items.filter(([, i]) => !toolsOf(i).baro), nb''')
# Pinnwand nach Kategorien gruppiert (Lehrperson, Präsentieren, Kinder)
rep('<div class="board">${boardItems.map(([id, i]) => kidNote(id, i)).join("")}</div>', '${groupedBoard(boardItems, ([id, i]) => kidNote(id, i), true)}')
rep('<div class="board">${boardItems.map(([id, i]) => teacherNote(id, i, res[id])).join("")}</div>', '${groupedBoard(boardItems, ([id, i]) => teacherNote(id, i, res[id]))}')
rep('<div class="board">${boardItems.map(([id, i]) => teacherNote(id, i, res[id], true)).join("")}</div>', '${groupedBoard(boardItems, ([id, i]) => teacherNote(id, i, res[id], true))}')
rep('function scaleBar(v, note) {', '''function cats() { const b = curBoard(); return b && Array.isArray(b.cats) ? b.cats : []; }
function catIdx(i) { const k = cats().findIndex(c => c.id === i.cat); return k < 0 ? 1e6 : k; }
function groupedBoard(list, fn, kid) {
  const cs = cats();
  if (!cs.length) return `<div class="board">${list.map(fn).join("")}</div>`;
  let h = "";
  for (const c of cs) {
    const l = list.filter(([, i]) => i.cat === c.id); if (!l.length && !(c.note || "").trim()) continue;
    h += `<section class="catsec"><h3 class="cathead">${esc(c.title)}</h3>${l.length ? `<div class="board">${l.map(fn).join("")}</div>` : ""}${(c.note || "").trim() ? `<div class="catnote"><span class="tool-l">${kid ? "Beschluss" : "Beschluss / Kommentar"}</span><p>${esc(c.note)}</p></div>` : ""}</section>`;
  }
  const rest = list.filter(([, i]) => catIdx(i) >= 1e6);
  if (rest.length) h += `<section class="catsec"><h3 class="cathead">Weitere</h3><div class="board">${rest.map(fn).join("")}</div></section>`;
  return h;
}
function sortHTML(items) {
  const cs = cats();
  const card = ([id, i], k) => `<div class="sortcard note ${colorOf(id)}" data-sid="${id}" tabindex="0" role="listitem" aria-label="${esc(i.text)}"><b class="snum">${k + 1}</b><span>${esc(i.text)}</span>${typeof scoreLine === "function" ? scoreLine(id, i) : ""}${toolsOf(i).baro ? `<em>Barometer</em>` : ""}</div>`;
  let k = 0; const cards = l => l.length ? l.map(x => card(x, k++)).join("") : `<p class="sortempty">Zettel hierher ziehen</p>`;
  const none = items.filter(([, i]) => catIdx(i) >= 1e6);
  const grid = (cid, l) => `<div class="sortgrid" data-cat="${cid}">${cards(l)}</div>`;
  const pre = cs.length ? "" : grid("", none);
  const secs = cs.map((c, ci) => `<section class="sortsec" data-catsec="${c.id}">
      <div class="row cathead-edit"><input class="field cat-title" id="ct-${c.id}" data-keep data-cattitle="${c.id}" maxlength="60" value="${esc(c.title)}" aria-label="Name der Kategorie">
        <button class="btn ghost small" type="button" data-act="catmove" data-id="${c.id}" data-d="-1" ${ci ? "" : "disabled"} aria-label="Kategorie nach oben">↑</button><button class="btn ghost small" type="button" data-act="catmove" data-id="${c.id}" data-d="1" ${ci < cs.length - 1 ? "" : "disabled"} aria-label="Kategorie nach unten">↓</button>
        <button class="del ${S.armed === "k:" + c.id ? "arm" : ""}" type="button" data-act="delcat" data-id="${c.id}">${S.armed === "k:" + c.id ? "Kategorie wirklich löschen?" : "Kategorie löschen"}</button></div>
      ${grid(c.id, items.filter(([, i]) => i.cat === c.id))}
      <label class="tool-l" for="cn-${c.id}">Beschluss / Kommentar</label><textarea class="field catnote-in" id="cn-${c.id}" data-keep data-catnote="${c.id}" rows="2" maxlength="1000" placeholder="z. B. Lösung, auf die sich die Klasse geeinigt hat">${esc(c.note || "")}</textarea>
    </section>`).join("");
  return `<section class="panel" id="sortArea"><div><h2>Sortieren</h2><p class="sub">Ziehen Sie die Zettel in die gewünschte Reihenfolge: der wichtigste zuerst. Mit Kategorien gruppieren Sie die Zettel unter Übertiteln, darunter ist Platz für einen Beschluss. So erscheint es an der Pinnwand, beim Präsentieren und bei den Kindern.</p></div>
    ${typeof AUTOSORT !== "undefined" ? `<div class="row autosort"><span class="tool-l">Automatisch sortieren</span>${AUTOSORT.map(([a, l]) => `<button class="btn ghost small" type="button" data-act="autosort" data-by="${a}">${l}</button>`).join("")}</div>` : ""}
    <div class="row newcat"><input class="field grow" id="newCat" data-keep maxlength="60" placeholder="Neue Kategorie, z. B. «Das stört uns»"><button class="btn small" type="button" data-act="addcat">Kategorie hinzufügen</button></div>
    ${cs.length ? `<section class="sortsec pool"><h3 class="sorth">Noch ohne Kategorie</h3>${grid("", none)}</section>` : pre}
    ${secs}
    <p class="sub">Auf dem iPad: Zettel antippen, halten und ziehen, auch in eine andere Kategorie. Mit der Tastatur: Zettel anwählen, dann Pfeiltasten.</p></section>`;
}
let sdrag = null;
function sortNumbers(){ document.querySelectorAll("#sortArea .sortcard").forEach((c, k) => { c.querySelector(".snum").textContent = k + 1; }); document.querySelectorAll("#sortArea .sortgrid").forEach(g => { const e = g.querySelector(".sortempty"); if (e) e.hidden = !!g.querySelector(".sortcard"); }); }
async function sortSave(){
  const jobs = [];
  document.querySelectorAll("#sortArea .sortcard").forEach((c, k) => {
    const id = c.dataset.sid, i = S.ideas.get(id), cat = c.closest(".sortgrid").dataset.cat || null;
    if (i && (i.order !== k || (i.cat || null) !== cat)) { i.order = k; i.cat = cat; jobs.push([id, { order: k, cat }]); }
  });
  if (!jobs.length) return;
  try { await Promise.all(jobs.map(([id, p]) => patchIdea(id, p))); toast("Reihenfolge gespeichert."); } catch (err) { failed(err); }
}
async function saveCats(cs, msg) {
  const b = curBoard(); if (!b) return; b.cats = cs; render();
  try { await patchBoard(S.board, { cats: cs }); if (msg) toast(msg); } catch (err) { failed(err); }
}
document.addEventListener("pointerdown", e => {
  const c = e.target.closest && e.target.closest("#sortArea .sortcard"); if (!c || e.button > 0) return;
  e.preventDefault(); c.setPointerCapture?.(e.pointerId);
  sdrag = { c, x: e.clientX, y: e.clientY, moved: false }; c.classList.add("sdrag");
});
document.addEventListener("pointermove", e => {
  if (!sdrag) return;
  const { c } = sdrag, dx = e.clientX - sdrag.x, dy = e.clientY - sdrag.y;
  if (!sdrag.moved && Math.abs(dx) + Math.abs(dy) < 5) return;
  sdrag.moved = true; c.style.transform = `translate(${dx}px,${dy}px) rotate(-2deg)`;
  c.style.pointerEvents = "none"; const over = document.elementFromPoint(e.clientX, e.clientY); c.style.pointerEvents = "";
  const t = over && over.closest && over.closest("#sortArea .sortcard"), g = over && over.closest && over.closest("#sortArea .sortgrid");
  const r0 = c.getBoundingClientRect();
  if (t && t !== c) {
    const r = t.getBoundingClientRect(), before = e.clientY < r.top || (e.clientY <= r.bottom && e.clientX < r.left + r.width / 2);
    t.parentNode.insertBefore(c, before ? t : t.nextSibling);
  } else if (!t && g && g !== c.parentNode) { g.appendChild(c); }
  else return;
  const r1 = c.getBoundingClientRect(); sdrag.x += r1.left - r0.left; sdrag.y += r1.top - r0.top;
  c.style.transform = `translate(${e.clientX - sdrag.x}px,${e.clientY - sdrag.y}px) rotate(-2deg)`;
  sortNumbers();
});
function sortEnd(){ if (!sdrag) return; const { c, moved } = sdrag; sdrag = null; c.classList.remove("sdrag"); c.style.transform = ""; if (moved) sortSave(); }
document.addEventListener("pointerup", sortEnd);
document.addEventListener("pointercancel", sortEnd);
document.addEventListener("keydown", e => {
  const c = e.target.closest && e.target.closest("#sortArea .sortcard"); if (!c) return;
  const all = [...document.querySelectorAll("#sortArea .sortcard")], k = all.indexOf(c);
  const prev = all[k - 1], next = all[k + 1];
  if ((e.key === "ArrowLeft" || e.key === "ArrowUp") && prev) { e.preventDefault(); if (prev.parentNode === c.parentNode) c.parentNode.insertBefore(c, prev); else prev.parentNode.insertBefore(c, prev.nextSibling); }
  else if ((e.key === "ArrowRight" || e.key === "ArrowDown") && next) { e.preventDefault(); if (next.parentNode === c.parentNode) c.parentNode.insertBefore(next, c); else next.parentNode.insertBefore(c, next); }
  else return;
  c.focus(); sortNumbers(); clearTimeout(sortSave.t); sortSave.t = setTimeout(sortSave, 700);
});
document.addEventListener("change", e => {
  const el = e.target, id = el.dataset && el.dataset.cattitle; if (!id) return;
  const v = el.value.trim(); if (!v) { render(); return; }
  saveCats(cats().map(c => c.id === id ? { ...c, title: v } : c));
});
document.addEventListener("input", e => {
  const el = e.target, id = el.dataset && el.dataset.catnote; if (!id) return;
  const b = curBoard(); if (!b) return; b.cats = cats().map(c => c.id === id ? { ...c, note: el.value } : c);
  clearTimeout(saveCats.t); const cs = b.cats; saveCats.t = setTimeout(async () => { try { await patchBoard(S.board, { cats: cs }); } catch (err) { failed(err); } }, 900);
});
function scaleBar(v, note) {''')
rep('''  else if (act === "tab") {''', '''  else if (act === "addcat") {
    const inp = $("#newCat"), t = inp ? inp.value.trim() : ""; if (!t) { inp?.focus(); return; }
    inp.value = ""; saveCats([...cats(), { id: "c" + Math.random().toString(36).slice(2, 9), title: t, note: "" }], "Kategorie hinzugefügt. Ziehen Sie die Zettel hinein.");
  }
  else if (act === "catmove") {
    const cs = cats().slice(), k = cs.findIndex(c => c.id === id), j = k + +b.dataset.d; if (k < 0 || j < 0 || j >= cs.length) return;
    [cs[k], cs[j]] = [cs[j], cs[k]]; saveCats(cs);
  }
  else if (act === "delcat") {
    const key = "k:" + id;
    if (S.armed !== key) { S.armed = key; render(); setTimeout(() => { if (S.armed === key) { S.armed = null; render(); } }, 4000); return; }
    S.armed = null;
    const moved = [...S.ideas].filter(([, i]) => i.cat === id && inBoard(i)); moved.forEach(([, i]) => { i.cat = null; });
    await saveCats(cats().filter(c => c.id !== id), "Kategorie gelöscht. Ihre Zettel sind jetzt ohne Kategorie.");
    try { await Promise.all(moved.map(([iid]) => patchIdea(iid, { cat: null }))); } catch (err) { failed(err); }
  }
  else if (act === "tab") {''')
rep('#knBack{margin-right:4px}', '''#knBack{margin-right:4px}
.sortgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(170px,1fr));gap:14px;padding:10px 4px;min-height:80px;border-radius:14px}
.sortsec{border:2px dashed var(--line, #e3e6df);border-radius:18px;padding:12px 14px;display:flex;flex-direction:column;gap:8px;margin-top:6px}
.sortsec.pool{background:rgba(255,255,255,.5)}
.sorth{margin:0;font-size:1.1rem}
.cathead-edit{gap:8px;align-items:center}
.cathead-edit .cat-title{flex:1 1 220px;font-weight:700;font-size:1.15rem}
.sortempty{margin:0;align-self:center;color:var(--muted);font-family:var(--hand);font-size:1.1rem;grid-column:1/-1;text-align:center}
.newcat{gap:8px}
.sortcard{margin:0;padding:12px;min-height:96px;cursor:grab;touch-action:none;user-select:none;-webkit-user-select:none;display:flex;flex-direction:column;gap:6px}
.sortcard span{font-family:var(--hand);font-size:1.1rem;line-height:1.15;display:-webkit-box;-webkit-line-clamp:4;-webkit-box-orient:vertical;overflow:hidden}
.sortcard em{font-style:normal;font-size:.75rem;color:var(--muted)}
.sortcard .snum{position:absolute;top:-10px;left:-8px;width:28px;height:28px;border-radius:50%;background:var(--ink);color:#fff;display:grid;place-items:center;font-size:.85rem}
.sortcard.sdrag{cursor:grabbing;z-index:5;box-shadow:0 14px 30px rgba(0,0,0,.22);transition:none}
.sortcard:focus-visible{outline:3px solid var(--leaf, #7ea56a);outline-offset:3px}
.catsec{display:flex;flex-direction:column;gap:10px;margin-bottom:18px}
.cathead{margin:6px 0 0;font-family:var(--bubble, inherit);font-size:1.6rem;color:var(--ink);border-bottom:3px solid var(--leaf, #7ea56a);padding-bottom:4px}
.present-on .cathead{font-size:2.2rem}
.catnote{background:#fff;border-radius:14px;border-left:6px solid var(--leaf, #7ea56a);padding:10px 14px;box-shadow:0 4px 14px rgba(0,0,0,.06)}
.catnote p{margin:4px 0 0;font-family:var(--hand);font-size:1.3rem;white-space:pre-wrap}
.present-on .catnote p{font-size:1.7rem}
.one-cat{margin:0 0 8px;font-weight:800;color:var(--leaf-deep, #4d7a42);text-transform:uppercase;letter-spacing:.06em;font-size:.9rem}''')
