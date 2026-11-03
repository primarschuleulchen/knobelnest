# 11) Präsentieren «Kategorien»: eine Kategorie pro Bildschirm, alle Zettel ohne Scrollen, Beschluss-Feld darunter
rep('const tabs = [["board", "Ergebnisse"], ["one", "Einzeln"]];', 'const tabs = cats().length ? [["cats", "Kategorien"], ["board", "Ergebnisse"], ["one", "Einzeln"]] : [["board", "Ergebnisse"], ["one", "Einzeln"]];')
rep('if (S.tab === "one") return html + oneHTML(items, res);', 'if (S.tab === "one") return html + oneHTML(items, res);\n  if (S.tab === "cats") return html + catsHTML(items, res);')
rep('S.view = b.dataset.v; S.tab = "board";', 'S.view = b.dataset.v; S.tab = b.dataset.v === "show" && cats().length ? "cats" : "board";')
rep('if (S.view === "show" && S.tab === "one" && ', 'if (S.view === "show" && S.tab === "cats" && !(e.target.closest && e.target.closest("input,textarea,select")) && ["ArrowLeft", "ArrowRight", "PageUp", "PageDown"].includes(e.key)) {\n    e.preventDefault(); catStep(e.key === "ArrowLeft" || e.key === "PageUp" ? -1 : 1); return;\n  }\n  if (S.view === "show" && S.tab === "one" && ')
rep('function scaleBar(v, note) {', '''function catSlides(items) {
  const cs = cats(), out = cs.map(c => ({ c, list: items.filter(([, i]) => i.cat === c.id) }));
  const rest = items.filter(([, i]) => catIdx(i) >= 1e6); if (rest.length) out.push({ c: null, list: rest });
  if (cs.length) out.unshift({ overview: true, list: [] });
  return out;
}
function catsHTML(items, res) {
  const slides = catSlides(items); if (!slides.length) return `<div class="empty"><h3>Noch keine Kategorien</h3></div>`;
  S.catIdx = Math.max(0, Math.min(slides.length - 1, S.catIdx || 0));
  const nav = (title) => `<div class="pc-head"><button class="one-nav" type="button" data-act="catprev" aria-label="Zurück" ${S.catIdx ? "" : "disabled"}>‹</button>
      <h2 class="pc-title">${title}</h2><span class="pc-count">${S.catIdx + 1} / ${slides.length}</span>
      <button class="one-nav" type="button" data-act="catnext" aria-label="Weiter" ${S.catIdx < slides.length - 1 ? "" : "disabled"}>›</button></div>`;
  const chips = `<div class="pc-chips">${slides.map((s, k) => `<button type="button" class="pc-chip${k === S.catIdx ? " cur" : ""}" data-act="catgo" data-i="${k}">${s.overview ? "Übersicht" : s.c ? esc(s.c.title) : "Weitere"}${s.overview ? "" : ` <small>${s.list.length}</small>`}</button>`).join("")}</div>`;
  if (slides[S.catIdx].overview) {
    const real = slides.filter(x => x.c), m = real.length, oc = m <= 1 ? 1 : m <= 6 ? 2 : m <= 9 ? 3 : 4, orow = Math.ceil(m / oc);
    return `<section class="pcats">${nav("Übersicht")}
      <div class="pc-over" style="--c:${oc};--r:${orow}">${real.map(x => `<button type="button" class="pc-ocat" data-act="catgo" data-i="${slides.indexOf(x)}">
        <span class="pc-oh">${esc(x.c.title)} <small>${x.list.length} ${x.list.length === 1 ? "Zettel" : "Zettel"}</small></span>
        ${(x.c.note || "").trim() ? `<span class="pc-ob"><em>Beschluss</em>${esc(x.c.note)}</span>` : `<span class="pc-ob none">Noch kein Beschluss</span>`}</button>`).join("")}</div>
      ${chips}</section>`;
  }
  const { c, list } = slides[S.catIdx], n = list.length;
  const cols = n <= 4 ? Math.max(1, n) : n <= 6 ? 3 : n <= 8 ? 4 : n <= 12 ? 4 : n <= 15 ? 5 : n <= 20 ? 5 : 6, rows = Math.max(1, Math.ceil(n / cols));
  const bar = (label, v, cls, n) => v == null ? "" : `<div class="pc-bar ${cls || ""}"><span class="pc-lab">${label} <b>${fmt(v)}</b>${n ? ` · ${n} ${n === 1 ? "Stimme" : "Stimmen"}` : ""}</span><div class="pc-track"><i style="width:${Math.max(0, Math.min(10, v)) * 10}%"></i></div></div>`;
  const card = ([id, i]) => { const a = res[id], t = toolsOf(i), L = (i.text || "").length, k = L > 110 ? .58 : L > 75 ? .7 : L > 45 ? .85 : 1;
    let h = `<article class="note ${colorOf(id)} pcard" style="--k:${k}"><p class="pc-t">${esc(i.text)}</p>`;
    if (a) {
      const row = [];
      if (t.baro) row.push(bar("Barometer", a.baroAvg, "", a.baro.length));
      if (t.rate && !t.baro) row.push(a.rateAvg == null ? `<span class="pc-none">Bewertung: noch keine Stimmen</span>` : bar("Ø", a.rateAvg, "", a.rate.length));
      if (t.agree && !t.baro) { const tot = a.agree.ja + a.agree.teils + a.agree.nein, q = x => tot ? a.agree[x] / tot * 100 : 0;
        if (tot) row.push(`<div class="pc-agree"><span class="pc-lab"><b style="color:var(--ja)">●</b>${a.agree.ja} <b style="color:var(--teils)">●</b>${a.agree.teils} <b style="color:var(--nein)">●</b>${a.agree.nein}</span><div class="stack"><span style="width:${q("ja")}%;background:var(--ja)"></span><span style="width:${q("teils")}%;background:var(--teils)"></span><span style="width:${q("nein")}%;background:var(--nein)"></span></div></div>`); }
      if (row.length) h += `<div class="pc-row">${row.join("")}</div>`;
      const lp = Array.isArray(i.lp) ? i.lp : [];
      if (lp.length || (t.comment && a.comments.length)) h += `<ul class="pc-cm">${lp.map(c => `<li class="lpc">${esc(c.t)}</li>`).join("")}${t.comment ? a.comments.map(c => `<li>${esc(c.text)}</li>`).join("") : ""}</ul>`;
    }
    return h + `</article>`; };
  return `<section class="pcats">${nav(c ? esc(c.title) : "Weitere")}
    <div class="pc-grid" style="--c:${cols};--r:${rows}">${n ? list.map(card).join("") : `<p class="sortempty">In dieser Kategorie hängt noch kein Zettel.</p>`}</div>
    ${c ? `<div class="pc-note"><label class="tool-l" for="pcn-${c.id}">Beschluss</label><textarea class="field" id="pcn-${c.id}" data-keep data-catnote="${c.id}" rows="2" maxlength="1000" placeholder="Hier den Beschluss der Klasse festhalten …">${esc(c.note || "")}</textarea></div>` : ""}
    ${chips}
  </section>`;
}
function fitCats() {
  const box = document.querySelector(".pcats .pc-grid"); if (!box) return;
  const cards = [...box.querySelectorAll(".pcard")], n = cards.length; if (!n) return;
  const ok = need => cards.every(c => {
    if (c.scrollHeight > c.clientHeight + 1 || c.scrollWidth > c.clientWidth + 1) return false;
    const u = c.querySelector(".pc-cm"); if (!u) return true;
    const r = u.getBoundingClientRect(), lis = [...u.children];
    return lis.slice(0, Math.min(need, lis.length)).every(li => li.getBoundingClientRect().bottom <= r.bottom + 1);
  });
  const search = need => {
    const best = { tf: 0, c: Math.min(n, 4) };
    for (let c = 1; c <= Math.min(n, 6); c++) {
      const r = Math.ceil(n / c); if (c > 1 && Math.ceil(n / (c - 1)) === r) continue; // gleiche Zeilenzahl mit weniger Spalten ist breiter
      if (c > 1 && box.clientWidth / c < 270) continue; // zu schmale Zettel lesen sich schlecht
      box.style.setProperty("--c", c); box.style.setProperty("--r", r);
      let lo = 12, hi = 76;
      box.style.setProperty("--tf", lo + "px"); if (!ok(need)) continue;
      while (hi - lo > 1) { const m = (lo + hi) >> 1; box.style.setProperty("--tf", m + "px"); if (ok(need)) lo = m; else hi = m; }
      if (lo > best.tf) { best.tf = lo; best.c = c; }
    }
    return best;
  };
  // Zuerst 4 Kommentare ganz sichtbar; wird die Aussage dafür zu klein, weniger Kommentare (der Rest scrollt im Zettel)
  let best = search(4);
  if (best.tf < 24) { const b2 = search(2); if (b2.tf > best.tf) best = b2; }
  if (best.tf < 20) { const b0 = search(0); if (b0.tf > best.tf) best = b0; }
  if (!best.tf) best.tf = 12;
  box.style.setProperty("--c", best.c); box.style.setProperty("--r", Math.ceil(n / best.c)); box.style.setProperty("--tf", best.tf + "px");
}
addEventListener("resize", () => { clearTimeout(fitCats.t); fitCats.t = setTimeout(fitCats, 150); });
function catStep(d) { S.catIdx = (S.catIdx || 0) + d; render(); }
function scaleBar(v, note) {''')
rep('''  else if (act === "tab") {''', '''  else if (act === "catgo") { S.catIdx = +b.dataset.i; render(); }
  else if (act === "catprev") catStep(-1);
  else if (act === "catnext") catStep(1);
  else if (act === "tab") {''')
rep('#knBack{margin-right:4px}', '''#knBack{margin-right:4px}
.present-on .note{transform:none!important}
html{min-height:100%}body{min-height:100vh;box-sizing:border-box}
.pcats{display:flex;flex-direction:column;gap:12px;height:calc(100vh - 150px);min-height:420px}
@media (max-width:1180px){.pcats{height:calc(100vh - 200px)}}
.pc-head{display:flex;align-items:center;gap:16px}
.pc-title{flex:1;margin:0;font-family:var(--bubble, inherit);font-size:clamp(24px,3.4vw,42px);color:var(--ink);border-bottom:4px solid var(--leaf, #7ea56a);padding-bottom:4px}
.pc-count{color:var(--muted);font-weight:700}
.pc-grid{flex:1;min-height:0;display:grid;grid-template-columns:repeat(var(--c),minmax(0,1fr));grid-template-rows:repeat(var(--r),minmax(0,1fr));gap:clamp(8px,1.4vw,18px)}
.pcard{margin:0;min-height:0;overflow:hidden;padding:clamp(10px,1.6vh,20px) clamp(12px,1.4vw,20px);justify-content:flex-start;gap:clamp(4px,.8vh,8px)}
.pc-row{display:flex;gap:clamp(8px,1vw,16px);flex:none}
.pc-row>*{flex:1 1 0;min-width:0}
.pc-bar{display:flex;flex-direction:column;gap:2px}
.pc-lab,.pc-n,.pc-none{font-size:max(12px, calc(var(--tf, 28px) * .48));font-weight:700;opacity:.8}
.pc-none{margin:0;font-weight:600}
.pc-track{height:max(6px, calc(var(--tf, 28px) * .3));border-radius:99px;background:rgba(255,255,255,.85);overflow:hidden}
.pc-track i{display:block;height:100%;border-radius:99px;background:linear-gradient(90deg,var(--sky),var(--leaf))}
.pc-agree{display:flex;flex-direction:column;gap:2px}
.pc-agree .stack{height:max(6px, calc(var(--tf, 28px) * .3))}
.pc-cm{flex:1 1 auto;min-height:0;overflow:auto;margin:2px 0 0;padding:0;list-style:none;display:flex;flex-direction:column;gap:4px}
.pc-cm{gap:3px}
.pc-cm li{font-family:var(--hand);font-size:max(13px, calc(var(--tf, 28px) * .62));line-height:1.15;background:rgba(255,255,255,.65);border-radius:8px;padding:2px 7px}
.pc-cm li.lpc{border-left:4px solid var(--leaf, #7ea56a);font-weight:700}
.pc-t{margin:0;flex:none;font-family:var(--hand);line-height:1.15;font-size:var(--tf, 28px);overflow-wrap:anywhere}
.pc-s{margin:0;font-weight:700;font-size:min(calc(3.4vh / var(--r) + .5rem), 1.1rem);opacity:.7}
.pc-l{margin:0;font-family:var(--hand);font-size:min(calc(4vh / var(--r) + .5rem), 1.3rem);border-left:4px solid var(--leaf, #7ea56a);padding-left:8px;background:rgba(255,255,255,.6);border-radius:6px}
.pc-note{display:flex;align-items:center;gap:12px;background:#fff;border-radius:16px;border-left:6px solid var(--leaf, #7ea56a);padding:6px 12px;box-shadow:0 4px 14px rgba(0,0,0,.06)}
.pc-note .tool-l{flex:none}
.pc-note textarea{flex:1;width:100%;font-family:var(--hand);font-size:clamp(1.05rem,2.1vh,1.5rem);min-height:1.6em;height:2.6em;border:0;background:#fbfaf6}
.pc-chips{display:flex;gap:8px;flex-wrap:wrap;justify-content:center}
.pc-chip{border:1.5px solid var(--line, #e3e6df);background:#fff;border-radius:999px;padding:3px 12px;font-size:.85rem;font-weight:700;cursor:pointer;color:var(--ink)}
.pc-chip small{opacity:.6;margin-left:4px}
.pc-over{flex:1;min-height:0;overflow:auto;display:grid;grid-template-columns:repeat(var(--c),minmax(0,1fr));grid-auto-rows:auto;align-content:start;gap:clamp(10px,1.4vw,18px);padding:2px}
.pc-ocat{all:unset;box-sizing:border-box;cursor:pointer;display:flex;flex-direction:column;gap:8px;min-height:0;overflow:hidden;background:#fff;border-radius:18px;border-left:8px solid var(--leaf, #7ea56a);padding:clamp(12px,1.8vh,22px) clamp(14px,1.6vw,24px);box-shadow:0 6px 18px rgba(0,0,0,.07)}
.pc-ocat:hover,.pc-ocat:focus-visible{box-shadow:0 8px 22px rgba(0,0,0,.14)}
.pc-oh{font-family:var(--bubble, inherit);font-weight:700;font-size:clamp(1.2rem, calc(5vw / var(--c)), 2.4rem);line-height:1.1;color:var(--ink)}
.pc-oh small{font-family:var(--ui);font-size:.45em;font-weight:700;color:var(--muted);margin-left:6px}
.pc-ob{font-family:var(--hand);font-size:clamp(1rem, calc(3.4vw / var(--c)), 1.9rem);line-height:1.25;white-space:pre-wrap}
.pc-ob em{display:block;font-family:var(--ui);font-style:normal;font-size:.55em;font-weight:800;letter-spacing:.08em;text-transform:uppercase;color:var(--leaf-deep, #4d7a42);margin-bottom:2px}
.pc-ob.none{color:var(--muted);font-style:italic}
@media (max-height:820px){.pcats .pc-chips{display:none}.pcats{gap:8px}}
.pc-chip.cur{background:var(--leaf, #7ea56a);border-color:var(--leaf, #7ea56a);color:#fff}''')
rep('  layoutTracks();\n', '  layoutTracks();\n  if (S.view === "show" && S.tab === "cats") fitCats();\n')
