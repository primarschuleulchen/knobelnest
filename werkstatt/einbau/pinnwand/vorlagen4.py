# 16) Leinwand (wie Padlet «Freiform»): Zettel frei verschieben, Hintergrund-Vorlagen Venn-Diagramm, zwei Seiten, vier Felder, Zielscheibe.
#     Beim Loslassen bekommt der Zettel die Kategorie des Feldes. idea.pos = {x, y} (Mitte, 0..1), board.canvas.
#     Mindmap: Zettel auf einen anderen Ast ziehen, Äste auch beim Präsentieren umbenennen.
#     Lehrperson: Werkzeuge und Einstellungen in einer Seitenleiste rechts (ein- und ausblendbar), die Pinnwand links.
#     Wird nach vorlagen3.py von standalone.py ausgeführt.

# --- Leinwand: Vorlagen, Felder, Darstellung
rep('function noteColor(id, i) {', r'''const CANVAS = {
  leer: { name: "Leer", defs: [] },
  venn: { name: "Venn-Diagramm", defs: [["Links", "c0"], ["Rechts", "c2"], ["Beides", "c3"]] },
  tabelle: { name: "Zwei Seiten", defs: [["Links", "c3"], ["Rechts", "c1"]] },
  felder: { name: "Vier Felder", defs: [["Feld 1", "c0"], ["Feld 2", "c2"], ["Feld 3", "c3"], ["Feld 4", "c4"]] },
  ziel: { name: "Zielscheibe", defs: [["Sehr wichtig", "c1"], ["Wichtig", "c0"], ["Weniger wichtig", "c2"]] }
};
const CHEX = { c0: ["#fdf1c2", "#e2bd4a"], c1: ["#fcefed", "#e0948a"], c2: ["#e3eef8", "#86a9cc"], c3: ["#e9f1e3", "#8db27a"], c4: ["#efe8f7", "#a98fcf"] };
const canvasOf = () => { const t = (curBoard() || {}).canvas; return CANVAS[t] ? t : "leer"; };
const canMove = () => isTeacher && !S.peek && (S.view === "lp" || S.view === "show");
const pendN = () => { let n = 0; for (const [, i] of S.ideas) if (i.status === "pending" && inBoard(i)) n++; return n; };
function cvRegion(t, x, y) {
  const X = x * 1600, Y = y * 1000, d = (cx, cy) => Math.hypot(X - cx, Y - cy);
  if (t === "venn") { const l = d(576, 500) < 464, r = d(1024, 500) < 464; return l && r ? 2 : l ? 0 : r ? 1 : -1; }
  if (t === "tabelle") return x < .5 ? 0 : 1;
  if (t === "felder") return (y < .5 ? 0 : 2) + (x < .5 ? 0 : 1);
  if (t === "ziel") { const k = d(800, 500); return k < 160 ? 0 : k < 320 ? 1 : k < 480 ? 2 : -1; }
  return -1;
}
const CV_ANCHOR = { venn: [[.2, .45], [.8, .45], [.5, .45]], tabelle: [[.25, .3], [.75, .3]], felder: [[.22, .25], [.72, .25], [.22, .75], [.72, .75]], ziel: [[.5, .5], [.36, .5], [.2, .5]] };
const CV_LABEL = { venn: [[.22, .12], [.78, .12], [.5, .15]], tabelle: [[.25, .05], [.75, .05]], felder: [[.25, .05], [.75, .05], [.25, .55], [.75, .55]], ziel: [[.5, .37], [.5, .21], [.5, .05]] };
const CV_STEP = [[0, 0], [0, .17], [0, -.17], [0, .34], [-.11, .085], [.11, .085], [-.11, -.085], [.11, -.085], [-.11, .255], [.11, .255]];
function cvSVG(t, cs) {
  const col = k => CHEX[(cs[k] && cs[k].color) || ["c0", "c2", "c3", "c4"][k % 4]] || CHEX.c0;
  if (t === "venn") return `<defs><clipPath id="cvL"><circle cx="576" cy="500" r="464"/></clipPath></defs>
    <circle cx="576" cy="500" r="464" fill="${col(0)[0]}" stroke="${col(0)[1]}" stroke-width="5"/><circle cx="1024" cy="500" r="464" fill="${col(1)[0]}" stroke="${col(1)[1]}" stroke-width="5"/>
    <circle cx="1024" cy="500" r="464" clip-path="url(#cvL)" fill="${col(2)[0]}" stroke="${col(2)[1]}" stroke-width="5" stroke-dasharray="16 12"/><circle cx="576" cy="500" r="464" fill="none" stroke="${col(2)[1]}" stroke-width="5" stroke-dasharray="16 12" clip-path="url(#cvR)"/>
    <defs><clipPath id="cvR"><circle cx="1024" cy="500" r="464"/></clipPath></defs>`;
  if (t === "tabelle") return `<rect x="20" y="20" width="770" height="960" rx="28" fill="${col(0)[0]}"/><rect x="810" y="20" width="770" height="960" rx="28" fill="${col(1)[0]}"/><line x1="800" y1="40" x2="800" y2="960" stroke="#3f5f86" stroke-width="6" opacity=".4"/><line x1="60" y1="120" x2="1540" y2="120" stroke="#3f5f86" stroke-width="6" opacity=".4"/>`;
  if (t === "felder") return [[20, 20], [810, 20], [20, 510], [810, 510]].map(([x, y], k) => `<rect x="${x}" y="${y}" width="770" height="470" rx="28" fill="${col(k)[0]}" stroke="${col(k)[1]}" stroke-width="4"/>`).join("");
  if (t === "ziel") return `<circle cx="800" cy="500" r="480" fill="${col(2)[0]}" stroke="${col(2)[1]}" stroke-width="5"/><circle cx="800" cy="500" r="320" fill="${col(1)[0]}" stroke="${col(1)[1]}" stroke-width="5"/><circle cx="800" cy="500" r="160" fill="${col(0)[0]}" stroke="${col(0)[1]}" stroke-width="5"/>`;
  return "";
}
function canvasHTML(list, fn, kid) {
  const b = curBoard() || {}, t = canvasOf(), cs = cats(), mv = canMove(), edit = !kid && (S.view === "lp" || S.view === "show");
  const seen = {}, place = (id, i) => {
    if (i.pos && typeof i.pos.x === "number") return [i.pos.x, i.pos.y];
    const k = cs.findIndex(c => c.id === i.cat), key = t !== "leer" && k >= 0 && (CV_ANCHOR[t] || [])[k] ? "r" + k : "x", n = seen[key] = (seen[key] ?? -1) + 1;
    if (key === "x") return t === "leer" ? [.1 + (n % 6) * .16, .14 + Math.floor(n / 6) * .26] : [.07 + (n % 7) * .14, .9];
    const [ax, ay] = CV_ANCHOR[t][k], [dx, dy] = CV_STEP[n % CV_STEP.length];
    return [ax + dx, ay + dy + Math.floor(n / CV_STEP.length) * .05];
  };
  const clamp = v => Math.max(.07, Math.min(.93, v));
  const notes = list.map(([id, i]) => { const [x, y] = place(id, i); return `<button type="button" class="cv-note note ${mv ? "mv " : ""}${noteColor(id, i)}${S.mmFocus === id ? " cur" : ""}" data-act="mmfocus" data-id="${id}" style="left:${clamp(x) * 100}%;top:${clamp(y) * 100}%">${imgHTML(i, "mm-img")}<span>${esc(i.text)}</span>${b.names && i.by && i.by !== "Lehrperson" ? `<small>${esc(i.by)}</small>` : ""}</button>`; }).join("");
  const labels = (CV_LABEL[t] || []).map(([x, y], k) => { const c = cs[k]; if (!c) return "";
    const inner = edit && S.astEdit === c.id
      ? `<span class="mm-ed"><input class="field" id="ast-${c.id}" data-keep maxlength="60" value="${esc(c.title)}" aria-label="Name des Feldes"><span class="row"><button class="btn small" type="button" data-act="astsave" data-id="${c.id}">OK</button></span></span>`
      : edit ? `<button type="button" class="cv-lt" data-act="astedit" data-id="${c.id}" title="Umbenennen">${esc(c.title)}</button>` : `<span class="cv-lt">${esc(c.title)}</span>`;
    return `<div class="cv-lab" style="left:${x * 100}%;top:${y * 100}%">${inner}</div>`; }).join("");
  const f = S.mmFocus && list.find(([id]) => id === S.mmFocus);
  return `<div class="cv-wrap"><div class="cv" id="cv" data-t="${t}"><svg class="cv-bg" viewBox="0 0 1600 1000" aria-hidden="true">${cvSVG(t, cs)}</svg>${labels}${notes}
      ${!list.length ? `<p class="cv-empty">${kid ? "Noch keine Zettel" : "Noch keine Zettel. Heften Sie rechts unter «Selbst anpinnen» einen an."}</p>` : ""}</div></div>
    ${f ? `<div class="mm-focus"><div class="row" style="justify-content:space-between"><span class="tool-l">Zettel im Detail</span><button class="btn ghost small" type="button" data-act="mmclose">Schliessen</button></div><div class="board">${fn(f)}</div></div>`
      : list.length ? `<p class="sub mm-hint">${mv ? "Ziehen Sie die Zettel, wohin Sie wollen. Antippen zeigt einen Zettel gross." + (t !== "leer" ? " Tippen Sie auf eine Überschrift, um sie umzubenennen." : "") : "Tippe auf einen Zettel, um ihn gross zu sehen" + (kid ? " und mitzumachen." : ".")}</p>` : ""}`;
}
// Ziehen: Zettel auf der Leinwand und Blätter der Mindmap
let mvd = null, noClick = false;
document.addEventListener("click", e => { if (noClick) { noClick = false; e.stopPropagation(); e.preventDefault(); } }, true);
document.addEventListener("pointerdown", e => {
  const el = e.target.closest && e.target.closest(".mv"); if (!el || e.button > 0 || !canMove()) return;
  const r = el.getBoundingClientRect();
  mvd = { el, id: el.dataset.id, x0: e.clientX, y0: e.clientY, ox: e.clientX - (r.left + r.width / 2), oy: e.clientY - (r.top + r.height / 2), moved: false, cv: el.classList.contains("cv-note"), pid: e.pointerId };
});
document.addEventListener("pointermove", e => {
  if (!mvd) return;
  const { el } = mvd;
  if (!mvd.moved) { if (Math.hypot(e.clientX - mvd.x0, e.clientY - mvd.y0) < 6) return; mvd.moved = true; el.classList.add("dragging"); el.setPointerCapture?.(mvd.pid); }
  e.preventDefault();
  if (mvd.cv) {
    const cv = $("#cv"); if (!cv) return; const r = cv.getBoundingClientRect();
    mvd.x = Math.max(.04, Math.min(.96, (e.clientX - mvd.ox - r.left) / r.width)); mvd.y = Math.max(.04, Math.min(.96, (e.clientY - mvd.oy - r.top) / r.height));
    el.style.left = mvd.x * 100 + "%"; el.style.top = mvd.y * 100 + "%";
  } else {
    el.style.transform = `translate(${e.clientX - mvd.x0}px,${e.clientY - mvd.y0}px)`;
    el.style.pointerEvents = "none"; const over = document.elementFromPoint(e.clientX, e.clientY); el.style.pointerEvents = "";
    const br = over && over.closest && over.closest(".mm-br:not([data-bare])");
    document.querySelectorAll(".mm-br.drop").forEach(x => x !== br && x.classList.remove("drop")); if (br) br.classList.add("drop");
    mvd.br = br || null;
  }
});
async function mvEnd() {
  if (!mvd) return; const d = mvd; mvd = null;
  if (!d.moved) return;
  noClick = true; setTimeout(() => { noClick = false; }, 0);
  d.el.classList.remove("dragging"); document.querySelectorAll(".mm-br.drop").forEach(x => x.classList.remove("drop"));
  const i = S.ideas.get(d.id); if (!i) { render(); return; }
  if (d.cv && typeof d.x === "number") {
    const t = canvasOf(), k = cvRegion(t, d.x, d.y), patch = { pos: { x: +d.x.toFixed(4), y: +d.y.toFixed(4) } };
    if (t !== "leer") patch.cat = k >= 0 && cats()[k] ? cats()[k].id : null;
    Object.assign(i, patch); render();
    try { await patchIdea(d.id, patch); } catch (err) { failed(err); }
  } else if (!d.cv && d.br) {
    const cid = d.br.dataset.cid || null; d.el.style.transform = "";
    if ((i.cat || null) === cid) { render(); return; }
    i.cat = cid; render();
    try { await patchIdea(d.id, { cat: cid }); toast("Zettel verschoben."); } catch (err) { failed(err); }
  } else { d.el.style.transform = ""; render(); }
}
document.addEventListener("pointerup", mvEnd);
document.addEventListener("pointercancel", mvEnd);
function noteColor(id, i) {''')
rep('const LAYOUTS = [["wand", "Wand"], ["spalten", "Spalten"], ["liste", "Liste"], ["zeit", "Zeitstrahl"], ["mind", "Mindmap"]];',
    'const LAYOUTS = [["wand", "Wand"], ["spalten", "Spalten"], ["liste", "Liste"], ["zeit", "Zeitstrahl"], ["mind", "Mindmap"], ["frei", "Leinwand"]];')
rep('if (lay === "spalten" || lay === "zeit" || lay === "mind") return layoutBoard(lay, list, fn, kid);', 'if (lay === "frei") return canvasHTML(list, fn, kid);\n  if (lay === "spalten" || lay === "zeit" || lay === "mind") return layoutBoard(lay, list, fn, kid);')
rep('const structural = () => cats().length > 0 && (layoutOf() === "spalten" || layoutOf() === "mind");', 'const structural = () => layoutOf() === "frei" || (cats().length > 0 && (layoutOf() === "spalten" || layoutOf() === "mind"));')
rep('mind: "Der Auftrag (oder der Name) steht in der Mitte, die Kategorien sind die Äste." }[lay]}',
    'mind: "Der Auftrag (oder der Name) steht in der Mitte, die Kategorien sind die Äste. Zettel lassen sich auf einen anderen Ast ziehen.", frei: "Zettel frei hinschieben, wie auf einem Tisch. Mit einer Vorlage (z. B. Venn-Diagramm) kommt der Zettel beim Loslassen automatisch in das richtige Feld." }[lay]}')
rep('      <div><span class="tool-l">Hintergrund</span>${seg("bbg"', '''      ${lay === "frei" ? `<div><span class="tool-l">Vorlage der Leinwand</span>${seg("bcanvas", Object.entries(CANVAS).map(([k, v]) => [k, v.name]), canvasOf())}</div>` : ""}
      <div><span class="tool-l">Hintergrund</span>${seg("bbg"''')
rep('  for (const k of ["prompt", "bg", "kidCat", "direct", "names"]) if (t[k]) b[k] = t[k];', '  for (const k of ["prompt", "bg", "kidCat", "direct", "names", "canvas"]) if (t[k]) b[k] = t[k];')
rep('  { id: "woche", icon: "🌟"', '''  { id: "venn", icon: "⭕", name: "Venn-Diagramm", desc: "Zwei Dinge vergleichen: Was gehört nur zum einen, was zu beiden?", ph: "z. B. Kindheit früher und heute", layout: "frei", canvas: "venn", kidCat: true,
    cats: [["Früher", "c0"], ["Heute", "c2"], ["Beides", "c3"]] },
  { id: "felder", icon: "🔲", name: "Vier Felder", desc: "Zettel in vier Felder ordnen, z. B. für eine Selbsteinschätzung.", ph: "z. B. Mein Lernstand in Mathe", layout: "frei", canvas: "felder", kidCat: true,
    cats: [["Das kann ich gut", "c3"], ["Das übe ich noch", "c0"], ["Das macht mir Freude", "c4"], ["Da brauche ich Hilfe", "c1"]] },
  { id: "ziel", icon: "🎯", name: "Zielscheibe", desc: "Was ist am wichtigsten? Je näher an der Mitte, desto wichtiger.", ph: "z. B. Was brauchen wir für das Lager?", layout: "frei", canvas: "ziel", kidCat: true,
    cats: [["Sehr wichtig", "c1"], ["Wichtig", "c0"], ["Weniger wichtig", "c2"]] },
  { id: "frei", icon: "🎨", name: "Freie Leinwand", desc: "Zettel überall hinschieben, wie auf einem Tisch.", ph: "z. B. Unsere Ideen-Wolke", layout: "frei" },
  { id: "woche", icon: "🌟"''')
rep('  else if (t.layout === "liste") {', '''  else if (t.layout === "frei" && t.canvas === "venn") g += `<circle cx="48" cy="20" r="17" fill="${P.c0}" opacity=".9"/><circle cx="72" cy="20" r="17" fill="${P.c2}" opacity=".8"/>`;
  else if (t.layout === "frei" && t.canvas === "felder") [[8, 2], [62, 2], [8, 21], [62, 21]].forEach(([x, y], k) => { g += `<rect x="${x}" y="${y}" width="50" height="17" rx="3" fill="${P[["c3", "c0", "c4", "c1"][k]]}"/>`; });
  else if (t.layout === "frei" && t.canvas === "ziel") g += `<circle cx="60" cy="20" r="19" fill="${P.c2}"/><circle cx="60" cy="20" r="12" fill="${P.c0}"/><circle cx="60" cy="20" r="5" fill="${P.c1}"/>`;
  else if (t.layout === "frei") { [[14, 6], [44, 20], [78, 4], [96, 22], [30, 24]].forEach(([x, y], k) => { g += `<rect x="${x}" y="${y}" width="18" height="13" rx="2" fill="${P[ks[k]]}" transform="rotate(${k % 2 ? 6 : -5} ${x + 9} ${y + 6})"/>`; }); }
  else if (t.layout === "liste") {''')
rep('''  else if (act === "reshuffle") {''', '''  else if (act === "bcanvas") {
    const bd = curBoard(); if (!bd) return; const t = b.dataset.v, defs = (CANVAS[t] || CANVAS.leer).defs, cs = cats().slice();
    for (let k = cs.length; k < defs.length; k++) cs.push({ id: newId("c"), title: defs[k][0], color: defs[k][1], note: "" });
    bd.canvas = t; if (cs.length !== cats().length) await saveCats(cs); else render();
    try { await patchBoard(S.board, { canvas: t }); } catch (err) { failed(err); }
  }
  else if (act === "side") { S.side = !S.side; render(); }
  else if (act === "reshuffle") {''')

# --- Mindmap: Blätter ziehen, Äste auch beim Präsentieren umbenennen
rep('class="mm-leaf note ${noteColor(id, i)}', 'class="mm-leaf note ${canMove() ? "mv " : ""}${noteColor(id, i)}')
rep('  const edit = !kid && S.view === "lp";\n  const node = c =>', '  const edit = !kid && (S.view === "lp" || S.view === "show");\n  const node = c =>')
rep('<div class="mm-br ${side}" data-c="${(c && c.color) || ""}">', '<div class="mm-br ${side}" data-c="${(c && c.color) || ""}" data-cid="${c ? c.id : ""}"${bare ? " data-bare" : ""}>')
rep('    ${edit ? `<div class="row mm-add">', '    ${edit && S.view === "lp" ? `<div class="row mm-add">')
rep('${edit ? " Tippen Sie auf einen Ast, um ihn umzubenennen." : ""}', '${edit ? " Ziehen Sie einen Zettel auf einen anderen Ast, um ihn zu verschieben. Tippen Sie auf einen Ast, um ihn umzubenennen." : ""}')

# --- Lehrperson: Seitenleiste rechts
rep('S.view === "lp" ? teacherHTML() :', 'S.view === "lp" ? teacherHTML() + "</main></div>" :')
rep('  { const bd = S.board && curBoard(); document.body.dataset.bg', '  if (S.side == null) S.side = innerWidth >= 1100;\n  { const bd = S.board && curBoard(); document.body.dataset.bg')
rep('let html = boardHead() + `<section class="panel tools-bar">', 'let html = boardHead() + `<div class="lpwrap${S.side ? "" : " closed"}"><aside class="lpside" aria-label="Werkzeuge und Einstellungen"><div class="side-top"><b>Werkzeuge und Einstellungen</b><button class="btn ghost small" type="button" data-act="side">Ausblenden ✕</button></div><section class="panel tools-bar">')
rep('''<button class="btn" type="button" data-act="lpadd">Anpinnen</button></div>
  </section>
  </div>`;''', '''<button class="btn" type="button" data-act="lpadd">Anpinnen</button></div>
  </section>
  </div></aside><main class="lpmain">`;''')
rep('return `<div class="bhead"><button class="btn ghost" type="button" data-act="home">← Alle Pinnwände</button><h2>${esc(b.title)}</h2>${teacher ? `${visPill(b.visible)}',
    'return `<div class="bhead"><button class="btn ghost" type="button" data-act="home">← Alle Pinnwände</button><h2>${esc(b.title)}</h2>${teacher ? `${visPill(b.visible)}<button class="btn ${S.side ? "ghost " : ""}small sidebtn" type="button" data-act="side" aria-expanded="${!!S.side}">${S.side ? "Seitenleiste ausblenden" : "☰ Werkzeuge und Einstellungen"}${pendN() ? ` <span class="badge">${pendN()} neu</span>` : ""}</button>')

# --- Gestaltung
rep('/* Erweiterungen */', r'''/* Erweiterungen */
body:has(.lpwrap:not(.closed)) .wrap{max-width:1640px}
.lpwrap{display:grid;grid-template-columns:minmax(0,1fr) 400px;gap:22px;align-items:start}
.lpwrap.closed{grid-template-columns:minmax(0,1fr)}
.lpmain{grid-column:1;grid-row:1;min-width:0;display:flex;flex-direction:column;gap:18px}
.lpside{grid-column:2;grid-row:1;display:flex;flex-direction:column;gap:14px;position:sticky;top:10px;max-height:calc(100vh - 20px);overflow:auto;overscroll-behavior:contain;padding:2px 4px 24px}
.lpwrap.closed .lpside{display:none}
.side-top .btn{white-space:nowrap}
.side-top{order:-2;display:flex;justify-content:space-between;align-items:center;gap:8px;font-weight:800;color:var(--muted);font-size:.9rem;text-transform:uppercase;letter-spacing:.05em}
.lpside .lp-grid{order:-1;display:flex;flex-direction:column;gap:14px}
.lpside .panel{padding:14px 16px;border-radius:18px}
.lpside .panel h2{font-size:1.45rem}
.lpside .bset-row{flex-direction:column;gap:10px}
.lpside .queue{grid-template-columns:minmax(0,1fr)}
.lpside .settings summary .sub{display:block}
.sidebtn .badge{margin-left:4px}
@media (max-width:1099px){
  .lpwrap,.lpwrap.closed{grid-template-columns:minmax(0,1fr)}
  .lpside{position:fixed;grid-column:auto;grid-row:auto;right:0;top:0;bottom:0;width:min(430px,94vw);max-height:none;z-index:60;background:var(--paper);box-shadow:-12px 0 34px rgba(0,0,0,.22);padding:14px 14px 30px}
}
/* Leinwand */
.cv-wrap{overflow-x:auto;padding:2px 0 8px}
.cv{position:relative;width:100%;min-width:760px;aspect-ratio:16/10;container-type:inline-size;background:rgba(255,255,255,.55);border-radius:22px;box-shadow:var(--shadow);overflow:hidden}
.present-on .cv{max-width:calc((100vh - 120px) * 1.6);margin:0 auto}
.cv-bg{position:absolute;inset:0;width:100%;height:100%}
.cv-lab{position:absolute;transform:translate(-50%,0);z-index:1;text-align:center;max-width:34%}
.cv-lt{all:unset;font-family:var(--bubble);font-weight:700;font-size:clamp(15px,2.3cqw,40px);line-height:1.1;color:var(--ink);overflow-wrap:anywhere}
button.cv-lt{cursor:pointer;border-radius:10px;padding:0 6px}
button.cv-lt:hover,button.cv-lt:focus-visible{background:rgba(255,255,255,.7)}
.cv-note{all:unset;box-sizing:border-box;position:absolute;z-index:2;width:12.5%;min-height:8cqw;padding:.8cqw;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:2px;text-align:center;font-family:var(--hand);font-size:clamp(12px,1.35cqw,24px);line-height:1.15;border-radius:3px;box-shadow:0 2px 0 rgba(0,0,0,.04),0 8px 18px -6px rgba(40,60,45,.35);cursor:pointer;overflow-wrap:anywhere}
.cv .cv-note.note:nth-of-type(2n){transform:translate(-50%,-50%) rotate(1.2deg)}
.cv-note::before{display:none}
.cv .cv-note.note{transform:translate(-50%,-50%) rotate(-1deg)}
.cv-note small{font-family:var(--ui);font-size:.6em;color:var(--muted);font-weight:700}
.cv-note .mm-img{max-height:6cqw;margin:0}
.cv-note.cur{outline:3px solid var(--ink)}
.mv{touch-action:none;cursor:grab;user-select:none;-webkit-user-select:none}
.mv.dragging{cursor:grabbing;z-index:20;box-shadow:0 18px 36px rgba(0,0,0,.28)}
.cv .cv-note.note.dragging{transform:translate(-50%,-50%) scale(1.06) rotate(-2deg)}
.mm-leaf.dragging{position:relative}
.mm-br.drop .mm-node{box-shadow:0 0 0 4px var(--mc,#9aa39c);transform:scale(1.06)}
.mm-br.drop .mm-leaves{outline:3px dashed var(--mc,#9aa39c);outline-offset:6px;border-radius:10px}
.cv-empty{position:absolute;left:50%;bottom:6%;transform:translateX(-50%);margin:0;font-family:var(--hand);font-size:1.2rem;color:var(--muted);background:rgba(255,255,255,.8);border-radius:999px;padding:4px 14px;z-index:1}
.cv-lab .mm-ed{display:inline-flex;flex-direction:column;gap:6px;background:#fff;border-radius:12px;padding:6px;box-shadow:var(--shadow)}''')
