# 15) Sortieren nach (wie Padlet): eigene Reihenfolge, Datum, Alphabet, Zufällig (board.sortBy, board.seed)
#     und Kategorisieren direkt am Zettel: Auswahl «In die Spalte / An den Ast / Kategorie» unter den Werkzeugen.
#     Wird nach vorlagen2.py von standalone.py ausgeführt.
rep('function noteColor(id, i) {', r'''function sortCmp(a, b) {
  const bd = curBoard() || {}, m = bd.sortBy || "", ord = i => typeof i.order === "number" ? i.order : 1e9;
  if (m === "datum") return timeCmp(a[1], b[1]);
  if (m === "abc") return String(a[1].text || "").localeCompare(String(b[1].text || ""), "de", { sensitivity: "base", numeric: true }) || timeCmp(a[1], b[1]);
  if (m === "zufall") { const h = s => { let x = 2166136261; for (const c of s) x = Math.imul(x ^ c.charCodeAt(0), 16777619) >>> 0; return x; }; return h(a[0] + (bd.seed || "")) - h(b[0] + (bd.seed || "")); }
  return ord(a[1]) - ord(b[1]) || timeCmp(a[1], b[1]);
}
async function ownOrder() {
  const bd = curBoard(); if (!bd || !bd.sortBy) return;
  bd.sortBy = ""; try { await patchBoard(S.board, { sortBy: "" }); } catch (err) { failed(err); }
}
function catPickHTML(id, i) {
  const cs = cats(); if (!cs.length) return "";
  const lay = layoutOf(), l = lay === "mind" ? "An den Ast" : lay === "spalten" ? "In die Spalte" : "Kategorie";
  return `<label class="row lpcat notecat"><span class="tool-l">${l}</span><select class="field" data-act="leafcat" data-id="${id}"><option value="">${lay === "mind" ? "ohne Ast" : "ohne"}</option>${cs.map(c => `<option value="${c.id}" ${i.cat === c.id ? "selected" : ""}>${esc(c.title)}</option>`).join("")}</select></label>`;
}
function noteColor(id, i) {''')
rep('.sort((a, b) => catIdx(a[1]) - catIdx(b[1]) || ord(a[1]) - ord(b[1]) || timeCmp(a[1], b[1]));', '.sort((a, b) => catIdx(a[1]) - catIdx(b[1]) || sortCmp(a, b));')
rep('const l = list.slice().sort((a, b) => ord(a[1]) - ord(b[1]) || timeCmp(a[1], b[1])), drag = !kid && S.view === "lp";', 'const l = list.slice().sort(sortCmp), drag = !kid && S.view === "lp";')
# Ziehen (Sortieren, Zeitstrahl, automatisch sortieren) heisst: eigene Reihenfolge
rep('async function sortSave(){\n', 'async function sortSave(){\n  ownOrder();\n')
rep('async function tlSave() {\n', 'async function tlSave() {\n  ownOrder();\n')
# Einstellung
rep('''        <div><span class="tool-l">Neue Zettel</span>''', '''        <div><span class="tool-l">Sortieren nach</span>${segK("sortBy", [["", "Eigene Reihenfolge"], ["datum", "Datum"], ["abc", "Alphabet"], ["zufall", "Zufällig"]], b.sortBy || "")}${b.sortBy === "zufall" ? ` <button class="btn ghost small" type="button" data-act="reshuffle">🔀 Neu mischen</button>` : ""}</div>
        <div><span class="tool-l">Neue Zettel</span>''')
rep('''  else if (act === "bseg") {''', '''  else if (act === "reshuffle") {
    const bd = curBoard(); if (!bd) return; bd.seed = newId(""); render();
    try { await patchBoard(S.board, { seed: bd.seed }); } catch (err) { failed(err); }
  }
  else if (act === "bseg") {''')
# Kategorie direkt am Zettel wählen
rep('Werkzeuge auf diesem Zettel</span>${toolToggles("t-" + id, t, id)}', 'Werkzeuge auf diesem Zettel</span>${toolToggles("t-" + id, t, id)}${layoutOf() === "mind" ? "" : catPickHTML(id, i)}')
rep('/* Erweiterungen */', '''/* Erweiterungen */
.notecat{margin-top:8px}
.notecat select{min-height:36px;padding:4px 12px;font-size:.9rem;background:rgba(255,255,255,.85)}''')
