# 12) Zweite Bewertung 1–10 mit eigener Frage (Werkzeug «rate2», Frage «rate2Q»)
rep('const TOOL_NAMES = { rate: "Bewertung 1–10", agree:', 'const TOOL_NAMES = { rate: "Bewertung 1–10", rate2: "Bewertung 2", agree:')
rep('  rateQ: "Wie gut findest du das? 1 bis 10", agreeQ:', '  rateQ: "Wie gut findest du das? 1 bis 10", rate2Q: "Wie wichtig ist dir das? 1 bis 10", agreeQ:')
rep('  ["rateQ", "Frage zur Bewertung 1–10"], ["agreeQ",', '  ["rateQ", "Frage zur Bewertung 1–10"], ["rate2Q", "Frage zur Bewertung 2"], ["agreeQ",')
rep('res[id] = { rate: [], baro: [],', 'res[id] = { rate: [], rate2: [], baro: [],')
rep('      if (typeof x.rate === "number") { a.rate.push(x.rate); any = true; a.voters.add(uid); }',
    '      if (typeof x.rate === "number") { a.rate.push(x.rate); any = true; a.voters.add(uid); }\n      if (typeof x.rate2 === "number") { a.rate2.push(x.rate2); any = true; a.voters.add(uid); }')
rep('a.rateAvg = avg(a.rate); a.baroAvg', 'a.rateAvg = avg(a.rate); a.rate2Avg = avg(a.rate2); a.baroAvg')
# Kinder: zweite Skala
rep('''aria-pressed="${v.rate === k + 1}" aria-label="${k + 1} von 10">${k + 1}</button>`).join("")}</div></div>`;''',
    '''aria-pressed="${v.rate === k + 1}" aria-label="${k + 1} von 10">${k + 1}</button>`).join("")}</div></div>`;
  if (t.rate2) h += `<div class="tool"><span class="tool-l">${esc(L().rate2Q)}</span><div class="scale">${Array.from({ length: 10 }, (_, k) => `<button type="button" data-act="rate2" data-id="${id}" data-v="${k + 1}" aria-pressed="${v.rate2 === k + 1}" aria-label="${k + 1} von 10">${k + 1}</button>`).join("")}</div></div>`;''')
rep('''  else if (act === "rate") {''', '''  else if (act === "rate2") { const v = +b.dataset.v, m = myVote(id); if (m.rate2 === v) delete m.rate2; else m.rate2 = v; touchMy(400); render(); }
  else if (act === "rate") {''')
# Lehrperson und Präsentieren
rep('''  if (t.rate) h += `<div class="tool"><span class="tool-l">Bewertung 1–10</span>${scaleBar(a.rateAvg, a.rate.length + (a.rate.length === 1 ? " Stimme" : " Stimmen"))}</div>`;''',
    '''  if (t.rate) h += `<div class="tool"><span class="tool-l">${t.rate2 ? esc(shortQ(L().rateQ)) : "Bewertung 1–10"}</span>${scaleBar(a.rateAvg, a.rate.length + (a.rate.length === 1 ? " Stimme" : " Stimmen"))}</div>`;
  if (t.rate2) h += `<div class="tool"><span class="tool-l">${esc(shortQ(L().rate2Q))}</span>${scaleBar(a.rate2Avg, a.rate2.length + (a.rate2.length === 1 ? " Stimme" : " Stimmen"))}</div>`;''')
rep('function scaleBar(v, note) {', '''function shortQ(q) { return String(q || "").replace(/\\s*1\\s*(bis|–|-)\\s*10\\.?\\s*$/i, "").trim(); }
function scaleBar(v, note) {''')
# Sortieren
rep('const AUTOSORT = [["rate", "nach Bewertung"], ["agree", "nach Zustimmung"], ["baro", "nach Barometer"]];',
    'const AUTOSORT = [["rate", "nach Bewertung"], ["rate2", "nach Bewertung 2"], ["agree", "nach Zustimmung"], ["baro", "nach Barometer"]];')
rep('  if (by === "rate") return a.rateAvg;', '  if (by === "rate") return a.rateAvg;\n  if (by === "rate2") return a.rate2Avg;')
rep('  if (a && a.rateAvg != null) p.push("Ø " + fmt(a.rateAvg));', '  if (a && a.rateAvg != null) p.push("Ø " + fmt(a.rateAvg));\n  if (a && a.rate2Avg != null) p.push("Ø2 " + fmt(a.rate2Avg));')
# Kategorien-Folien
rep('''      if (t.rate && !t.baro) row.push(a.rateAvg == null ? `<span class="pc-none">Bewertung: noch keine Stimmen</span>` : bar("Ø", a.rateAvg, "", a.rate.length));''',
    '''      if (t.rate && !t.baro) row.push(a.rateAvg == null ? `<span class="pc-none">Bewertung: noch keine Stimmen</span>` : bar(t.rate2 ? esc(shortQ(L().rateQ)) : "Ø", a.rateAvg, "", a.rate.length));
      if (t.rate2 && !t.baro) row.push(a.rate2Avg == null ? `<span class="pc-none">${esc(shortQ(L().rate2Q))} noch keine Stimmen</span>` : bar(esc(shortQ(L().rate2Q)), a.rate2Avg, "", a.rate2.length));''')
