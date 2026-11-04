# 14) Mehr wie Padlet: Bilder, Umfragen mit eigenen Antworten, Zeitstrahl ziehen, Äste in der Mindmap anlegen,
#     Zettelgrösse, Schrift, neue Zettel oben oder unten.
#     Neue Felder: idea.img (verkleinertes JPEG als data:-Adresse), idea.poll = [Antworten], Stimme r[id].poll = Nummer der Antwort,
#     board.imgs (Kinder dürfen Bilder anhängen), board.size ("" | "breit"), board.font ("" | "klar"), board.newPos ("" | "oben").
#     Wird nach vorlagen.py von standalone.py ausgeführt.

# --- Hilfen
rep('function noteColor(id, i) {', r'''const imgOk = i => !!(i && typeof i.img === "string" && /^data:image\/(jpeg|png|webp);base64,/.test(i.img));
const imgHTML = (i, cls) => imgOk(i) ? `<img class="${cls || "nimg"}" src="${esc(i.img)}" alt="" loading="lazy">` : "";
const pollOpts = i => Array.isArray(i.poll) && i.poll.length >= 2 ? i.poll : ["Ja", "Ein bisschen", "Nein"];
function shrinkImg(file) {
  return new Promise((res, rej) => {
    const u = URL.createObjectURL(file), im = new Image();
    im.onload = () => {
      const out = (max, q) => { const k = Math.min(1, max / Math.max(im.width, im.height)), c = document.createElement("canvas"); c.width = Math.max(1, Math.round(im.width * k)); c.height = Math.max(1, Math.round(im.height * k)); const x = c.getContext("2d"); x.fillStyle = "#fff"; x.fillRect(0, 0, c.width, c.height); x.drawImage(im, 0, 0, c.width, c.height); return c.toDataURL("image/jpeg", q); };
      let d = out(900, .72); if (d.length > 200000) d = out(640, .62); if (d.length > 200000) d = out(480, .55);
      URL.revokeObjectURL(u); res(d);
    };
    im.onerror = () => { URL.revokeObjectURL(u); rej(new Error("bild")); };
    im.src = u;
  });
}
function imgPickHTML(w) {
  if (w === "kid" && !(curBoard() || {}).imgs) return "";
  const cur = w === "kid" ? S.kidImg : S.lpImg;
  return `<div class="imgpick">${cur ? `<span class="imgprev"><img src="${esc(cur)}" alt="Gewähltes Bild"><button class="del" type="button" data-act="imgclear" data-w="${w}">Bild entfernen</button></span>`
    : `<label class="btn ghost small imgbtn">📷 Bild hinzufügen<input class="vh" type="file" accept="image/*" data-imgin="${w}"></label>`}</div>`;
}
function pollResHTML(id, i, a, present) {
  const o = pollOpts(i), cnt = o.map((_, k) => (a.poll && a.poll[k]) || 0), tot = cnt.reduce((s, n) => s + n, 0), max = Math.max(0, ...cnt);
  if (!present && S.pollEdit === id) return `<div class="tool"><label class="tool-l" for="pe-${id}">Antworten der Umfrage (eine pro Zeile)</label><textarea class="field" id="pe-${id}" data-keep rows="4" maxlength="400">${esc(o.join("\n"))}</textarea>
    <div class="row" style="justify-content:flex-end"><button class="btn ghost small" type="button" data-act="pollcancel">Abbrechen</button><button class="btn small" type="button" data-act="pollsave" data-id="${id}">Speichern</button></div></div>`;
  return `<div class="tool"><span class="tool-l">Umfrage · ${tot} ${tot === 1 ? "Stimme" : "Stimmen"}</span><div class="pollres">${o.map((x, k) => `<div class="pr-r${tot && cnt[k] === max ? " top" : ""}"><span>${esc(x)}</span><b>${cnt[k]}${tot ? ` · ${Math.round(cnt[k] / tot * 100)}%` : ""}</b><span class="pt"><i style="width:${tot ? cnt[k] / tot * 100 : 0}%"></i></span></div>`).join("")}</div>
    ${present ? "" : `<button class="edit-btn" type="button" data-act="polledit" data-id="${id}">Antworten ändern</button>`}</div>`;
}
let tdrag = null;
function tlNumbers() { document.querySelectorAll("#tl .tl-it").forEach((it, k) => { const d = it.querySelector(".tl-dot"); if (d) d.textContent = k + 1; }); }
async function tlSave() {
  const ids = [...document.querySelectorAll("#tl .tl-it")].map(it => it.dataset.tid), jobs = [];
  ids.forEach((id, k) => { const i = S.ideas.get(id); if (i && i.order !== k) { i.order = k; jobs.push([id, k]); } });
  if (!jobs.length) return;
  try { await Promise.all(jobs.map(([id, k]) => patchIdea(id, { order: k }))); toast("Reihenfolge gespeichert."); } catch (err) { failed(err); }
}
document.addEventListener("pointerdown", e => {
  const h = e.target.closest && e.target.closest("[data-tlh]"); if (!h || e.button > 0) return;
  const it = h.closest(".tl-it"), tl = $("#tl"); if (!it || !tl) return;
  e.preventDefault(); h.setPointerCapture?.(e.pointerId);
  tdrag = { it, x: e.clientX, sl: tl.scrollLeft, moved: false }; it.classList.add("tdrag");
});
document.addEventListener("pointermove", e => {
  if (!tdrag) return;
  const { it } = tdrag, tl = $("#tl"); if (!tl) return;
  if (!tdrag.moved && Math.abs(e.clientX - tdrag.x) < 5) return;
  tdrag.moved = true;
  const r = tl.getBoundingClientRect();
  if (e.clientX < r.left + 50) tl.scrollLeft -= 14; else if (e.clientX > r.right - 50) tl.scrollLeft += 14;
  const shift = () => `translateX(${e.clientX - tdrag.x + (tl.scrollLeft - tdrag.sl)}px)`;
  it.style.transform = shift();
  for (const o of tl.querySelectorAll(".tl-it")) {
    if (o === it) continue;
    const q = o.getBoundingClientRect(); if (e.clientX <= q.left || e.clientX >= q.right) continue;
    const before = e.clientX < q.left + q.width / 2;
    if (before ? o.previousElementSibling === it : o.nextElementSibling === it) break;
    const r0 = it.getBoundingClientRect(); tl.insertBefore(it, before ? o : o.nextSibling); const r1 = it.getBoundingClientRect();
    tdrag.x += r1.left - r0.left; it.style.transform = shift(); tlNumbers(); break;
  }
});
function tlEnd() { if (!tdrag) return; const { it, moved } = tdrag; tdrag = null; it.classList.remove("tdrag"); it.style.transform = ""; if (moved) tlSave(); }
document.addEventListener("pointerup", tlEnd);
document.addEventListener("pointercancel", tlEnd);
document.addEventListener("keydown", e => {
  const h = e.target.closest && e.target.closest("[data-tlh]"); if (!h) return;
  const it = h.closest(".tl-it"), prev = it.previousElementSibling, next = it.nextElementSibling;
  if (e.key === "ArrowLeft" && prev) { e.preventDefault(); it.parentNode.insertBefore(it, prev); }
  else if (e.key === "ArrowRight" && next) { e.preventDefault(); it.parentNode.insertBefore(next, it); }
  else return;
  h.focus(); tlNumbers(); clearTimeout(tlSave.t); tlSave.t = setTimeout(tlSave, 700);
});
document.addEventListener("keydown", e => {
  const el = e.target; if (!el.id) return;
  if (el.id.startsWith("ast-") && e.key === "Enter") { e.preventDefault(); $(`[data-act="astsave"][data-id="${el.id.slice(4)}"]`)?.click(); }
  else if (el.id.startsWith("ast-") && e.key === "Escape") { S.astEdit = null; render(); }
  else if (el.id === "newAst" && e.key === "Enter") { e.preventDefault(); $('[data-act="addast"]')?.click(); }
});
document.addEventListener("change", async e => {
  const el = e.target;
  if (el.dataset && el.dataset.imgin) {
    const f = el.files && el.files[0]; if (!f) return;
    if (!/^image\//.test(f.type || "image/")) { toast("Das ist kein Bild."); return; }
    try { const d = await shrinkImg(f); if (el.dataset.imgin === "kid") S.kidImg = d; else S.lpImg = d; render(); }
    catch { toast("Dieses Bild konnte nicht geladen werden. Bitte ein anderes wählen."); }
  }
  else if (el.dataset && el.dataset.act === "leafcat") {
    const i = S.ideas.get(el.dataset.id); if (!i) return; i.cat = el.value || null; render();
    try { await patchIdea(el.dataset.id, { cat: el.value || null }); } catch (err) { failed(err); }
  }
});
function noteColor(id, i) {''')

# --- Neue Zettel oben oder unten
rep('|| ord(a[1]) - ord(b[1]) || (a[1].okAt || a[1].at || 0) - (b[1].okAt || b[1].at || 0));\n}', '|| ord(a[1]) - ord(b[1]) || timeCmp(a[1], b[1]));\n}')
rep('$("#app").dataset.lay = bd ? layoutOf() : "";', '$("#app").dataset.lay = bd ? layoutOf() : ""; $("#app").dataset.size = (bd && bd.size) || ""; $("#app").dataset.font = (bd && bd.font) || "";')

# --- Einstellungen
rep('''      <div><span class="tool-l">Hintergrund</span>${seg("bbg", BGS, b.bg || "")}</div>''',
    '''      <div><span class="tool-l">Hintergrund</span>${seg("bbg", BGS, b.bg || "")}</div>
      <div class="bset-row"><div><span class="tool-l">Zettelgrösse</span>${segK("size", [["", "Standard"], ["breit", "Breit"]], b.size || "")}</div>
        <div><span class="tool-l">Schrift</span>${segK("font", [["", "Handschrift"], ["klar", "Druckschrift"]], b.font || "")}</div>
        <div><span class="tool-l">Neue Zettel</span>${segK("newPos", [["", "unten anhängen"], ["oben", "oben anhängen"]], b.newPos || "")}</div></div>''')
rep('''  const opt = (k, l) =>''', '''  const segK = (k, list, cur) => `<div class="seg">${list.map(([v, l]) => `<button type="button" data-act="bseg" data-k="${k}" data-v="${v}" aria-pressed="${v === cur}">${l}</button>`).join("")}</div>`;
  const opt = (k, l) =>''')
rep('''        ${opt("names", "Namen auf den Zetteln zeigen")}</div>''', '''        ${opt("names", "Namen auf den Zetteln zeigen")}
        ${opt("imgs", "Kinder dürfen ein Bild anhängen")}</div>''')

# --- Mindmap-Äste, Bilder, Umfragen: Klicks
rep('''  else if (act === "tpl") {''', '''  else if (act === "bseg") {
    const bd = curBoard(); if (!bd) return; const k = b.dataset.k, v = b.dataset.v;
    bd[k] = v; render(); try { await patchBoard(S.board, { [k]: v }); } catch (err) { failed(err); }
  }
  else if (act === "addast") {
    const inp = $("#newAst"), t = inp ? inp.value.trim() : ""; if (!t) { inp?.focus(); return; }
    const used = cats().map(c => c.color), col = (CCOL.find(([k]) => !used.includes(k)) || CCOL[cats().length % CCOL.length])[0];
    inp.value = ""; await saveCats([...cats(), { id: newId("c"), title: t, color: col, note: "" }], "Ast hinzugefügt.");
    $("#newAst")?.focus();
  }
  else if (act === "astedit") { S.astEdit = id; render(); const el = document.getElementById("ast-" + id); el?.focus(); el?.select(); }
  else if (act === "astsave") {
    const v = (document.getElementById("ast-" + id)?.value || "").trim(); S.astEdit = null;
    if (v) await saveCats(cats().map(c => c.id === id ? { ...c, title: v } : c)); else render();
  }
  else if (act === "imgclear") { if (b.dataset.w === "kid") S.kidImg = null; else S.lpImg = null; render(); }
  else if (act === "imgdel") {
    const i = S.ideas.get(id); if (!i) return; i.img = null; render();
    try { await patchIdea(id, { img: null }); toast("Bild entfernt."); } catch (err) { failed(err); }
  }
  else if (act === "lppoll") { S.lpPoll = !S.lpPoll; render(); if (S.lpPoll) $("#lpPoll")?.focus(); }
  else if (act === "polledit") { S.pollEdit = id; render(); document.getElementById("pe-" + id)?.focus(); }
  else if (act === "pollcancel") { S.pollEdit = null; render(); }
  else if (act === "pollsave") {
    const o = (document.getElementById("pe-" + id)?.value || "").split("\\n").map(x => x.trim()).filter(Boolean).slice(0, 6);
    if (o.length < 2) { toast("Eine Umfrage braucht mindestens zwei Antworten."); return; }
    S.pollEdit = null; const i = S.ideas.get(id); if (i) i.poll = o; render();
    try { await patchIdea(id, { poll: o, tools: { poll: true } }); toast("Umfrage gespeichert."); } catch (err) { failed(err); }
  }
  else if (act === "pollv") { const v = +b.dataset.v, m = myVote(id); if (S.peek) return; if (m.poll === v) delete m.poll; else m.poll = v; touchMy(400); render(); }
  else if (act === "tpl") {''')

# --- Bilder in den Zetteln
rep('<article class="note ${noteColor(id, i)}"><p class="txt">${esc(i.text)}</p>', '<article class="note ${noteColor(id, i)}"><p class="txt">${esc(i.text)}</p>${imgHTML(i)}')
rep('`<p class="txt">${esc(i.text)}</p>`}${i.by && (!present', '`<p class="txt">${esc(i.text)}</p>`}${imgHTML(i)}${i.by && (!present')
rep('`<p class="txt">${esc(i.text)}</p>`}<p class="by">von', '`<p class="txt">${esc(i.text)}</p>`}${imgHTML(i)}<p class="by">von')
rep('data-act="mmfocus" data-id="${id}">${esc(i.text)}', 'data-act="mmfocus" data-id="${id}">${imgHTML(i, "mm-img")}${esc(i.text)}')
rep('<span>${esc(i.text)}</span>${typeof scoreLine', '${imgHTML(i, "simg")}<span>${esc(i.text)}</span>${typeof scoreLine')
rep('<p class="pc-t">${esc(i.text)}</p>', '<p class="pc-t">${esc(i.text)}</p>${imgHTML(i, "pc-img")}')
rep('Werkzeuge auf diesem Zettel</span>${toolToggles("t-" + id, t, id)}', 'Werkzeuge auf diesem Zettel</span>${toolToggles("t-" + id, t, id)}${imgOk(i) ? `<button class="edit-btn" type="button" data-act="imgdel" data-id="${id}">Bild entfernen</button>` : ""}')
rep('lp: i.lp, at: Date.now()', 'lp: i.lp, img: i.img || null, poll: i.poll || null, at: Date.now()')

# --- Kinder: Bild anhängen
rep('placeholder="Meine Idee ist …">${esc(ls.get("pw-draft", ""))}</textarea>', 'placeholder="Meine Idee ist …">${esc(ls.get("pw-draft", ""))}</textarea>${imgPickHTML("kid")}')
rep('    if (!text) { toast("Schreib zuerst deine Idee auf."); ta.focus(); return; }', '    if (!text && !S.kidImg) { toast("Schreib zuerst deine Idee auf."); ta.focus(); return; }')
rep('    if (wantCat) extra.cat = S.kcat;', '    if (wantCat) extra.cat = S.kcat;\n    if (S.kidImg && bd.imgs) extra.img = S.kidImg;')
rep('b.disabled = false; toast(extra.status === "ok"', 'b.disabled = false; S.kidImg = null; render(); toast(extra.status === "ok"')

# --- Lehrperson: Bild und Umfrage beim Selbst-Anpinnen
rep('placeholder="z. B. Wohin soll die Schulreise gehen?"></textarea>', '''placeholder="z. B. Wohin soll die Schulreise gehen?"></textarea>
    ${imgPickHTML("lp")}
    ${S.lpPoll ? `<label class="tool-l" for="lpPoll">Umfrage: eine Antwort pro Zeile</label><textarea class="field" id="lpPoll" data-keep rows="3" maxlength="400" placeholder="ja, unbedingt\nein bisschen\nnein, passt so"></textarea><button class="linkbtn" type="button" data-act="lppoll" style="align-self:flex-start">Ohne Umfrage</button>`
      : `<button class="btn ghost small" type="button" data-act="lppoll" style="align-self:flex-start">📊 Umfrage hinzufügen</button>`}''')
rep('const inp = $("#lpIdea"), text = inp.value.trim(); if (!text) { inp.focus(); return; }',
    'const inp = $("#lpIdea"), text = inp.value.trim(), poll = S.lpPoll ? (($("#lpPoll") || {}).value || "").split("\\n").map(x => x.trim()).filter(Boolean).slice(0, 6) : [];\n    if (!text && !S.lpImg) { inp.focus(); return; }\n    if (poll.length === 1) { toast("Eine Umfrage braucht mindestens zwei Antworten."); return; }')
rep('status: "ok", tools: { ...curDefaults() }, at: Date.now(), okAt: Date.now() }); inp.value = "";',
    'status: "ok", tools: { ...curDefaults(), ...(poll.length ? { poll: true } : {}) }, ...(poll.length ? { poll } : {}), ...(S.lpImg ? { img: S.lpImg } : {}), at: Date.now(), okAt: Date.now() }); inp.value = ""; S.lpImg = null; S.lpPoll = false; if ($("#lpPoll")) $("#lpPoll").value = ""; render();')

# --- Werkzeug «Umfrage»
rep('agree: "Zustimmung", like:', 'agree: "Zustimmung", poll: "Umfrage", like:')
rep('res[id] = { rate: [], rate2: [], baro: [], like: 0,', 'res[id] = { rate: [], rate2: [], baro: [], like: 0, poll: [],')
rep('      if (x.like === true) { a.like++; any = true; a.voters.add(uid); }',
    '      if (x.like === true) { a.like++; any = true; a.voters.add(uid); }\n      if (typeof x.poll === "number") { a.poll[x.poll] = (a.poll[x.poll] || 0) + 1; any = true; a.voters.add(uid); }')
rep('  if (t.like) h += `<div class="tool"><button type="button" class="heart"',
    '  if (t.poll) h += `<div class="tool"><div class="poll" role="group">${pollOpts(i).map((o, k) => `<button type="button" data-act="pollv" data-id="${id}" data-v="${k}" aria-pressed="${v.poll === k}"><i></i>${esc(o)}</button>`).join("")}</div></div>`;\n  if (t.like) h += `<div class="tool"><button type="button" class="heart"')
rep('  if (t.like && !t.baro) h +=', '  if (t.poll && !t.baro) h += pollResHTML(id, i, a, present);\n  if (t.like && !t.baro) h +=')

# --- Gestaltung
rep('/* Erweiterungen */', r'''/* Erweiterungen */
.nimg{display:block;width:100%;max-height:340px;object-fit:cover;border-radius:10px;background:#fff}
.present-on .nimg{max-height:48vh;object-fit:contain}
.note .txt:empty{display:none}
.mm-img{display:block;width:100%;max-width:200px;max-height:120px;object-fit:cover;border-radius:6px;margin-bottom:4px}
.simg{display:block;width:100%;height:64px;object-fit:cover;border-radius:6px}
.pc-img{display:block;max-width:100%;max-height:30%;min-height:0;object-fit:contain;border-radius:8px;flex:0 1 auto;align-self:flex-start}
.imgpick{display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.imgbtn{position:relative;cursor:pointer;align-self:flex-start}
.imgprev{display:flex;gap:12px;align-items:center}
.imgprev img{height:76px;max-width:160px;object-fit:cover;border-radius:10px;box-shadow:var(--shadow)}
.vh{position:absolute;width:1px;height:1px;opacity:0;overflow:hidden;pointer-events:none}
.poll{display:flex;flex-direction:column;gap:6px}
.poll button{display:flex;align-items:center;gap:10px;text-align:left;border:1px solid var(--line);background:rgba(255,255,255,.85);border-radius:12px;padding:8px 12px;font-weight:700;font-size:1rem;color:var(--ink)}
.poll button i{width:18px;height:18px;border-radius:50%;border:2px solid #9aa39c;flex:none}
.poll button[aria-pressed="true"]{border-color:var(--leaf);background:#fff}
.poll button[aria-pressed="true"] i{border-color:var(--leaf);background:radial-gradient(circle,var(--leaf) 0 42%,transparent 48%)}
.pollres{display:flex;flex-direction:column;gap:7px}
.pr-r{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:3px 10px;font-weight:700;font-size:.95rem}
.pr-r b{font-weight:800;color:var(--muted)}
.pr-r.top b{color:var(--leaf-deep)}
.pr-r .pt{grid-column:1/-1;height:10px;border-radius:99px;background:rgba(255,255,255,.85);overflow:hidden}
.pr-r .pt i{display:block;height:100%;background:linear-gradient(90deg,var(--sky),var(--leaf));border-radius:99px}
.present-on .pr-r{font-size:1.15rem}
.bset-row{display:flex;flex-wrap:wrap;gap:14px 28px}
.tl-h{border:0;cursor:grab;touch-action:none;user-select:none;-webkit-user-select:none}
.tl-h:hover{background:var(--leaf-deep, #4d7a42)}
.tl-it.tdrag{z-index:5}
.tl-it.tdrag .note{box-shadow:0 16px 34px rgba(0,0,0,.24)}
.tl-it.tdrag .tl-h{cursor:grabbing}
.tl-tip{margin:0}
.mm-node{color:var(--ink)}
button.mm-node{cursor:pointer}
button.mm-node:hover,button.mm-node:focus-visible{box-shadow:0 0 0 3px rgba(31,36,33,.12)}
.mm-ed{display:flex;flex-direction:column;gap:6px;max-width:240px}
.mm-ed .field{font:inherit;font-weight:600;padding:4px 10px}
.mm-add{max-width:560px;margin:0 auto;width:100%}
#app[data-size="breit"] .board{grid-template-columns:repeat(auto-fill,minmax(min(420px,100%),1fr))}
#app[data-size="breit"] .col{flex-basis:400px;max-width:600px}
#app[data-size="breit"] .tl-it{flex-basis:420px}
#app[data-font="klar"] .note .txt,#app[data-font="klar"] .mm-leaf,#app[data-font="klar"] .pc-t,#app[data-font="klar"] .sortcard span{font-family:var(--ui);font-weight:600}
#app[data-font="klar"] .note .txt{font-size:1.2rem}''')
