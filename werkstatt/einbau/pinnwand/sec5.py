# 5) Präsentieren «Einzeln»: ein Zettel gross, die anderen klein unten zum Weitergehen
rep('  const tabs = [["board", "Ergebnisse"]]; if (hasBaro)', '  const tabs = [["board", "Ergebnisse"], ["one", "Einzeln"]]; if (hasBaro)')
rep('  if (S.tab === "rank") return html + rankHTML(items, res);\n  return html + (boardItems.length',
    '  if (S.tab === "rank") return html + rankHTML(items, res);\n  if (S.tab === "one") return html + oneHTML(items, res);\n  return html + (boardItems.length')
rep('function scaleBar(v, note) {', '''function oneHTML(items, res) {
  const n = items.length; S.oneIdx = Math.max(0, Math.min(n - 1, S.oneIdx || 0));
  const [id, i] = items[S.oneIdx];
  return `<section class="one">
    <div class="one-stage"><button class="one-nav" type="button" data-act="oneprev" aria-label="Vorheriger Zettel" ${S.oneIdx ? "" : "disabled"}>‹</button>
      <div class="one-big">${(cats().find(c => c.id === i.cat) || {}).title ? `<p class="one-cat">${esc(cats().find(c => c.id === i.cat).title)}</p>` : ""}${teacherNote(id, i, res[id], true)}</div>
      <button class="one-nav" type="button" data-act="onenext" aria-label="Nächster Zettel" ${S.oneIdx < n - 1 ? "" : "disabled"}>›</button></div>
    <p class="one-count">${S.oneIdx + 1} / ${n}</p>
    <div class="one-strip" id="oneStrip">${items.map(([sid, si], k) => `<button type="button" class="one-mini note ${colorOf(sid)}${k === S.oneIdx ? " cur" : ""}" data-act="onego" data-i="${k}" aria-label="Zettel ${k + 1}" ${k === S.oneIdx ? 'aria-current="true"' : ""}><span>${esc(si.text)}</span></button>`).join("")}</div>
  </section>`;
}
function oneStep(d) { S.oneIdx = (S.oneIdx || 0) + d; render(); const c = document.querySelector(".one-mini.cur"); if (c) c.scrollIntoView({ block: "nearest", inline: "center", behavior: "smooth" }); }
function scaleBar(v, note) {''')
rep('''  else if (act === "tab") {''', '''  else if (act === "onego") { S.oneIdx = +b.dataset.i; oneStep(0); }
  else if (act === "oneprev") oneStep(-1);
  else if (act === "onenext") oneStep(1);
  else if (act === "tab") {''')
rep('''  if (e.key === "Escape" && S.view === "show" && !document.fullscreenElement)''', '''  if (S.view === "show" && S.tab === "one" && !(e.target.closest && e.target.closest("input,textarea,select")) && ["ArrowLeft", "ArrowRight", "PageUp", "PageDown", " "].includes(e.key)) {
    e.preventDefault(); oneStep(e.key === "ArrowLeft" || e.key === "PageUp" ? -1 : 1); return;
  }
  if (e.key === "Escape" && S.view === "show" && !document.fullscreenElement)''')
rep('#knBack{margin-right:4px}', '''#knBack{margin-right:4px}
.one{display:flex;flex-direction:column;gap:12px}
.one-stage{display:grid;grid-template-columns:auto minmax(0,1fr) auto;align-items:center;gap:18px}
.one-big{max-width:920px;width:100%;justify-self:center}
.one-big .note{margin:0;padding:34px 34px 26px;min-height:min(46vh,440px)}
.present-on .one-big .note .txt{font-size:clamp(2.2rem,4.2vw,3.4rem)}
.present-on .one-big .cm li{font-size:1.5rem}
.one-nav{width:64px;height:64px;border-radius:50%;border:0;background:#fff;box-shadow:0 4px 14px rgba(0,0,0,.12);font-size:2.4rem;line-height:1;color:var(--ink);cursor:pointer}
.one-nav:disabled{opacity:.3;cursor:default}
.one-count{text-align:center;margin:0;color:var(--muted);font-weight:700}
.one-strip{display:flex;gap:14px;overflow-x:auto;padding:8px 6px 14px;scroll-snap-type:x proximity}
.one-mini{flex:0 0 150px;height:96px;margin:0;padding:12px 10px;cursor:pointer;border:0;text-align:left;scroll-snap-align:center;opacity:.75;transition:transform .15s,opacity .15s}
.one-mini span{font-family:var(--hand);font-size:1rem;line-height:1.15;display:-webkit-box;-webkit-line-clamp:4;-webkit-box-orient:vertical;overflow:hidden}
.one-mini.cur{opacity:1;transform:translateY(-4px);outline:3px solid var(--leaf, #7ea56a);outline-offset:3px}
.one-mini:hover{opacity:1}
@media (max-width:700px){.one-stage{grid-template-columns:1fr}.one-nav{display:none}}''')
