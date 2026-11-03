# 9) Sortieren automatisch: nach Bewertung, Zustimmung oder Barometer (ohne Stimmen ans Ende)
rep('''let sdrag = null;''', '''const AUTOSORT = [["rate", "nach Bewertung"], ["agree", "nach Zustimmung"], ["baro", "nach Barometer"]];
function scoreOf(a, by) {
  if (!a) return null;
  if (by === "rate") return a.rateAvg;
  if (by === "baro") return a.baroAvg;
  const t = a.agree.ja + a.agree.teils + a.agree.nein; return t ? (a.agree.ja + a.agree.teils * .5) / t * 100 : null;
}
function scoreLine(id, i) {
  const a = aggregate().res[id], t = toolsOf(i), p = [];
  if (a && a.rateAvg != null) p.push("Ø " + fmt(a.rateAvg));
  const z = scoreOf(a, "agree"); if (z != null) p.push(Math.round(z) + "% Zustimmung");
  if (a && a.baroAvg != null) p.push("Barometer " + fmt(a.baroAvg));
  return p.length ? `<em class="score">${p.join(" · ")}</em>` : "";
}
async function autoSort(by) {
  const res = aggregate().res, items = approved();
  const list = items.map(([id], k) => ({ id, k, v: scoreOf(res[id], by) }));
  if (!list.some(x => x.v != null)) { toast("Noch keine Stimmen für diese Sortierung."); return; }
  list.sort((x, y) => (x.v == null) - (y.v == null) || (y.v ?? 0) - (x.v ?? 0) || x.k - y.k);
  // innerhalb jeder Kategorie sortieren, die Kategorien bleiben
  document.querySelectorAll("#sortArea .sortgrid").forEach(grid => list.forEach(x => { const c = grid.querySelector(`[data-sid="${x.id}"]`); if (c) grid.appendChild(c); }));
  sortNumbers(); await sortSave();
}
let sdrag = null;''')
rep('''  else if (act === "cmdel") {''', '''  else if (act === "autosort") { autoSort(b.dataset.by); }
  else if (act === "cmdel") {''')
rep('#knBack{margin-right:4px}', '''#knBack{margin-right:4px}
.autosort{gap:8px;align-items:center;margin:4px 0 8px}
.sortcard .score{font-style:normal;font-size:.75rem;font-weight:700;color:var(--ink);opacity:.7}''')
