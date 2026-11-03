# 10) Kommentare der Lehrperson: am Zettel im Feld «lp» = [{ t, at }], für alle sichtbar (als «Lehrperson»)
rep('  if (present) return h + `</article>`;', '  h += lpcHTML(id, i, present);\n  if (present) return h + `</article>`;')
rep('''  if (t.comment) h += `<div class="tool"><label class="tool-l" for="c-${id}">''', '''  h += lpcHTML(id, i, true, true);
  if (t.comment) h += `<div class="tool"><label class="tool-l" for="c-${id}">''')
rep('function scaleBar(v, note) {', '''function lpcHTML(id, i, readOnly, kid) {
  const list = Array.isArray(i.lp) ? i.lp : [];
  if (readOnly && !list.length) return "";
  const head = `<span class="tool-l">${kid ? "Von deiner Lehrperson" : "Kommentar der Lehrperson"}</span>`;
  const items = list.map((c, k) => `<p class="lpc-t">${esc(c.t)}${readOnly ? "" : `<button class="cmdel ${S.armed === "l:" + id + ":" + k ? "arm" : ""}" type="button" data-act="lpcdel" data-id="${id}" data-k="${k}" title="Kommentar löschen">${S.armed === "l:" + id + ":" + k ? "Löschen?" : "✕"}</button>`}</p>`).join("");
  if (readOnly) return `<div class="tool lpc">${head}${items}</div>`;
  const open = S.lpcOpen === id;
  return `<div class="tool lpc">${list.length ? head + items : ""}${open
    ? `<label class="tool-l" for="lpc-${id}">Ihr Kommentar</label><textarea class="field" id="lpc-${id}" data-keep rows="2" maxlength="400" placeholder="z. B. Gute Idee, das schauen wir an!"></textarea>
       <div class="row" style="justify-content:flex-end"><button class="btn ghost small" type="button" data-act="lpcclose">Abbrechen</button><button class="btn small" type="button" data-act="lpcadd" data-id="${id}">Kommentieren</button></div>`
    : `<button class="edit-btn" type="button" data-act="lpcopen" data-id="${id}">+ Kommentar der Lehrperson</button>`}</div>`;
}
function scaleBar(v, note) {''')
rep('''  else if (act === "cmdel") {''', '''  else if (act === "lpcopen") { S.lpcOpen = id; render(); document.getElementById("lpc-" + id)?.focus(); }
  else if (act === "lpcclose") { S.lpcOpen = null; render(); }
  else if (act === "lpcadd") {
    const el = document.getElementById("lpc-" + id), t = el ? el.value.trim() : "";
    if (!t) { el?.focus(); return; }
    const idea = S.ideas.get(id); if (!idea) return;
    const lp = [...(Array.isArray(idea.lp) ? idea.lp : []), { t, at: Date.now() }];
    el.value = ""; S.lpcOpen = null; idea.lp = lp; render();
    try { await patchIdea(id, { lp }); toast("Kommentar gespeichert. Die Kinder sehen ihn."); } catch (err) { failed(err); }
  }
  else if (act === "lpcdel") {
    const key = "l:" + id + ":" + b.dataset.k;
    if (S.armed !== key) { S.armed = key; render(); setTimeout(() => { if (S.armed === key) { S.armed = null; render(); } }, 4000); return; }
    S.armed = null; const idea = S.ideas.get(id); if (!idea) return;
    const lp = (Array.isArray(idea.lp) ? idea.lp : []).filter((_, k) => k !== +b.dataset.k); idea.lp = lp; render();
    try { await patchIdea(id, { lp }); toast("Kommentar gelöscht."); } catch (err) { failed(err); }
  }
  else if (act === "cmdel") {''')
rep('#knBack{margin-right:4px}', '''#knBack{margin-right:4px}
.lpc .lpc-t{margin:0;font-family:var(--hand);font-size:1.15rem;line-height:1.25;background:rgba(255,255,255,.75);border-left:4px solid var(--leaf, #7ea56a);border-radius:8px;padding:6px 10px}
.present-on .lpc .lpc-t{font-size:1.4rem}
.present-on .one-big .lpc .lpc-t{font-size:1.7rem}
.lpc textarea{min-height:56px}''')
