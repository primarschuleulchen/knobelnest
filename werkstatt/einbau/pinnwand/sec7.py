# 7) Kommentare entfernen (Lehrperson): am Zettel wird gemerkt, welcher Kommentar welches Kindes ausgeblendet ist
rep('if (x.comment && x.comment.trim()) { a.comments.push({ name: v.name || "Ohne Namen", text: x.comment.trim() }); any = true; }',
    'if (x.comment && x.comment.trim()) { const hd = (S.ideas.get(id) || {}).hide || {}; if (hd[uid] !== x.comment.trim()) a.comments.push({ name: v.name || "Ohne Namen", text: x.comment.trim(), uid }); any = true; }')
rep('<ul class="cm">${a.comments.map(c => `<li>${present ? "" : `<b>${esc(c.name)}:</b> `}${esc(c.text)}</li>`).join("")}</ul>',
    '<ul class="cm">${a.comments.map(c => `<li>${present ? "" : `<b>${esc(c.name)}:</b> `}${esc(c.text)}${present ? "" : `<button class="cmdel ${S.armed === "c:" + id + ":" + c.uid ? "arm" : ""}" type="button" data-act="cmdel" data-id="${id}" data-uid="${esc(c.uid)}" title="Kommentar entfernen">${S.armed === "c:" + id + ":" + c.uid ? "Entfernen?" : "✕"}</button>`}</li>`).join("")}</ul>')
rep('''  else if (act === "tab") {''', '''  else if (act === "cmdel") {
    const key = "c:" + id + ":" + b.dataset.uid;
    if (S.armed !== key) { S.armed = key; render(); setTimeout(() => { if (S.armed === key) { S.armed = null; render(); } }, 4000); return; }
    S.armed = null;
    const v = S.votes.get(b.dataset.uid), txt = v && v.r && v.r[id] && (v.r[id].comment || "").trim();
    if (!txt) return;
    const idea = S.ideas.get(id); if (idea) { idea.hide = { ...(idea.hide || {}), [b.dataset.uid]: txt }; render(); }
    try { await patchIdea(id, { hide: { [b.dataset.uid]: txt } }); toast("Kommentar entfernt."); } catch (err) { failed(err); }
  }
  else if (act === "tab") {''')

# 8) Zur Freigabe: mehrere auswählen, gemeinsam löschen oder freigeben
rep('  my: { name: KN ? KN.name', '  qsel: new Set(),\n  my: { name: KN ? KN.name')
rep('${pend.length ? `<div class="queue">${pend.map(([id, i]) => `<div class="qitem">',
    '''${pend.length ? `${qbulkHTML(pend)}<div class="queue">${pend.map(([id, i]) => `<div class="qitem${S.qsel.has(id) ? " picked" : ""}"><label class="qpick"><input type="checkbox" data-act="qsel" data-id="${id}" ${S.qsel.has(id) ? "checked" : ""}> auswählen</label>''')
rep('function scaleBar(v, note) {', '''function qbulkHTML(pend) {
  for (const id of [...S.qsel]) if (!pend.some(([p]) => p === id)) S.qsel.delete(id);
  const n = S.qsel.size, all = n && n === pend.length;
  return `<div class="row qbulk"><label class="qpick"><input type="checkbox" data-act="qall" ${all ? "checked" : ""}> Alle auswählen</label>
    ${n ? `<span class="sub">${n} ausgewählt</span><button class="btn small" type="button" data-act="qok">Freigeben</button><button class="del ${S.armed === "q" ? "arm" : ""}" type="button" data-act="qdel">${S.armed === "q" ? `Wirklich ${n} löschen?` : "Löschen"}</button>` : ""}</div>`;
}
function scaleBar(v, note) {''')
rep('''document.addEventListener("change", async e => {
  const el = e.target;''', '''document.addEventListener("change", async e => {
  const el = e.target;
  if (el.dataset.act === "qsel") { if (el.checked) S.qsel.add(el.dataset.id); else S.qsel.delete(el.dataset.id); render(); return; }
  if (el.dataset.act === "qall") { S.qsel = new Set(el.checked ? [...S.ideas].filter(([, i]) => i.status === "pending" && inBoard(i)).map(([id]) => id) : []); render(); return; }''')
rep('''  else if (act === "tab") {''', '''  else if (act === "qdel") {
    if (S.armed !== "q") { S.armed = "q"; render(); setTimeout(() => { if (S.armed === "q") { S.armed = null; render(); } }, 4000); return; }
    S.armed = null; const ids = [...S.qsel]; S.qsel.clear();
    ids.forEach(x => S.ideas.delete(x)); render();
    try { await Promise.all(ids.map(x => removeIdea(x))); toast(ids.length === 1 ? "1 Idee gelöscht." : ids.length + " Ideen gelöscht."); } catch (err) { failed(err); }
  }
  else if (act === "qok") {
    const ids = [...S.qsel]; S.qsel.clear(); const now = Date.now();
    ids.forEach(x => { const i = S.ideas.get(x); if (i) Object.assign(i, { status: "ok", tools: { ...S.defaults }, okAt: now }); }); render();
    try { await Promise.all(ids.map(x => patchIdea(x, { status: "ok", tools: { ...S.defaults }, okAt: now }))); toast(ids.length === 1 ? "1 Idee freigegeben." : ids.length + " Ideen freigegeben."); } catch (err) { failed(err); }
  }
  else if (act === "tab") {''')
rep('#knBack{margin-right:4px}', '''#knBack{margin-right:4px}
.cm li{position:relative}
.cmdel{margin-left:8px;border:0;background:rgba(255,255,255,.7);border-radius:999px;padding:1px 8px;font-size:.8rem;color:var(--muted);cursor:pointer;vertical-align:middle}
.cmdel:hover{color:#b23b31;background:#fff}
.cmdel.arm{background:#b23b31;color:#fff}
.qbulk{gap:10px;margin-bottom:10px;align-items:center}
.qpick{display:inline-flex;align-items:center;gap:6px;font-size:.85rem;color:var(--muted);cursor:pointer;user-select:none}
.qpick input{width:18px;height:18px;accent-color:var(--leaf-deep, #4d7a42)}
.qitem.picked{outline:3px solid var(--leaf, #7ea56a);outline-offset:-3px}''')
