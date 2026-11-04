# 13) Vorlagen und Darstellungen (Ideen von Padlet und MindMup)
#     Neue Felder an der Pinnwand (board): tpl, layout ("wand" | "spalten" | "liste" | "zeit" | "mind"), prompt (Auftrag),
#     bg (Hintergrund), kidCat (Kinder wählen die Spalte), direct (ohne Freigabe), names (Namen zeigen), tools (Werkzeuge für neue Zettel),
#     cats[].color (Farbe der Spalte / des Astes). Neues Werkzeug «like» (Herz) in den Stimmen: r[id].like = true.
#     Wird von standalone.py ausgeführt (eigenständige Pinnwand).

# --- Vorlagen, Darstellungen, Hintergründe
rep('const L = () => ({ ...DEF_LABELS, ...(S.labels || {}) });', r'''const L = () => ({ ...DEF_LABELS, ...(S.labels || {}) });
const TPL = [
  { id: "leer", icon: "📌", name: "Leere Pinnwand", desc: "Ideen sammeln, freigeben und abstimmen.", ph: "z. B. Ideen für die Schulreise", layout: "wand" },
  { id: "brain", icon: "💡", name: "Brainstorming", desc: "Alle Gedanken sofort an die Wand, danach ordnen.", ph: "z. B. Was fällt dir zum Wald ein?", layout: "wand", direct: true, tools: { like: true }, prompt: "Was fällt dir dazu ein? Schreib jeden Gedanken auf einen eigenen Zettel." },
  { id: "mind", icon: "🧠", name: "Mindmap", desc: "Ein Thema in der Mitte, Äste rundherum. Jeder Zettel hängt an einem Ast.", ph: "z. B. Der Igel", layout: "mind", kidCat: true,
    cats: [["Aussehen", "c2"], ["Nahrung", "c3"], ["Lebensraum", "c0"], ["Fragen", "c4"]] },
  { id: "kwl", icon: "🔍", name: "Weiss – Will wissen – Gelernt", desc: "Vor, während und nach einem Thema: Vorwissen, Fragen und Gelerntes.", ph: "z. B. Thema Wasser", layout: "spalten", kidCat: true,
    cats: [["Das weiss ich schon", "c2"], ["Das will ich wissen", "c0"], ["Das habe ich gelernt", "c3"]] },
  { id: "procon", icon: "⚖️", name: "Pro und Contra", desc: "Gründe dafür und dagegen sammeln und gewichten.", ph: "z. B. Sollen wir eine Klassenkasse haben?", layout: "spalten", kidCat: true, tools: { agree: true },
    cats: [["Dafür 👍", "c3"], ["Dagegen 👎", "c1"]] },
  { id: "pmi", icon: "➕", name: "Plus – Minus – Interessant", desc: "Eine Idee von drei Seiten anschauen.", ph: "z. B. Hausaufgaben am Wochenende", layout: "spalten", kidCat: true,
    cats: [["Plus: Das ist gut", "c3"], ["Minus: Das ist nicht gut", "c1"], ["Interessant: Das fällt mir auf", "c4"]] },
  { id: "rat", icon: "🗣️", name: "Klassenrat", desc: "Anliegen sammeln, besprechen und Beschlüsse festhalten.", ph: "z. B. Klassenrat im November", layout: "spalten", kidCat: true, tools: { agree: true, comment: true },
    cats: [["Das schätze ich", "c3"], ["Das stört mich", "c1"], ["Ich schlage vor", "c2"]] },
  { id: "exit", icon: "🎟️", name: "Exit-Ticket", desc: "Kurzer Lernrückblick am Ende der Lektion.", ph: "z. B. Mathe: Brüche", layout: "spalten", kidCat: true,
    cats: [["Das habe ich gelernt", "c3"], ["Das ist mir noch unklar", "c0"], ["Das möchte ich noch wissen", "c2"]] },
  { id: "ampel", icon: "🚦", name: "Ampel: Wie läuft es?", desc: "Die Kinder zeigen, wo sie stehen und wer Hilfe braucht.", ph: "z. B. Wochenplan Woche 12", layout: "spalten", kidCat: true,
    cats: [["🟢 Läuft gut", "c3"], ["🟡 Geht so", "c0"], ["🔴 Ich brauche Hilfe", "c1"]] },
  { id: "fragen", icon: "❓", name: "Fragen-Sammlung", desc: "Fragen untereinander, die wichtigsten bekommen Herzen.", ph: "z. B. Fragen an die Försterin", layout: "liste", tools: { like: true, comment: true }, prompt: "Was möchtest du wissen? Schreib deine Frage auf." },
  { id: "zeit", icon: "🕰️", name: "Zeitstrahl", desc: "Ereignisse der Reihe nach: Geschichte, Tagesablauf, Lebenslauf.", ph: "z. B. Die Pfahlbauer", layout: "zeit", bg: "karo" },
  { id: "abst", icon: "🗳️", name: "Abstimmung", desc: "Vorschläge sammeln und mit 1 bis 10 bewerten.", ph: "z. B. Wohin geht die Schulreise?", layout: "wand", tools: { rate: true, agree: true } },
  { id: "buch", icon: "📚", name: "Buchtipps", desc: "Lieblingsbücher empfehlen, mit Namen und Herzen.", ph: "z. B. Unsere Lesetipps", layout: "wand", names: true, tools: { like: true, comment: true }, bg: "linien", prompt: "Welches Buch empfiehlst du? Schreib den Titel und warum es dir gefällt." },
  { id: "hallo", icon: "👋", name: "Wir stellen uns vor", desc: "Steckbriefe der Klasse, mit Namen.", ph: "z. B. Das sind wir", layout: "wand", names: true, tools: { like: true }, bg: "kork", prompt: "Was machst du gern? Was kannst du gut? Was wünschst du dir für dieses Jahr?" },
  { id: "woche", icon: "🌟", name: "Wochenrückblick", desc: "Highlights, Schwieriges und Vorfreude der Woche.", ph: "z. B. Woche 45", layout: "spalten", kidCat: true,
    cats: [["Mein Highlight", "c0"], ["Das war schwierig", "c4"], ["Darauf freue ich mich", "c3"]] }
];
const LAYOUTS = [["wand", "Wand"], ["spalten", "Spalten"], ["liste", "Liste"], ["zeit", "Zeitstrahl"], ["mind", "Mindmap"]];
const BGS = [["", "Aquarell"], ["kork", "Kork"], ["karo", "Karo"], ["linien", "Linien"], ["himmel", "Himmel"], ["wiese", "Wiese"]];
const CCOL = [["c0", "Gelb"], ["c1", "Rosa"], ["c2", "Blau"], ["c3", "Grün"], ["c4", "Lila"]];
const newId = p => p + Math.random().toString(36).slice(2, 9);
const timeCmp = (x, y) => ((x.okAt || x.at || 0) - (y.okAt || y.at || 0)) * ((curBoard() || {}).newPos === "oben" ? -1 : 1);
const layoutOf = () => { const b = curBoard(); return (b && b.layout) || "wand"; };
const tplOf = b => TPL.find(t => t.id === (b && b.tpl)) || null;
const curDefaults = () => (curBoard() && curBoard().tools) || S.defaults;
const structural = () => cats().length > 0 && (layoutOf() === "spalten" || layoutOf() === "mind");
function noteColor(id, i) { const c = cats().find(c => c.id === (i && i.cat)); return (c && c.color) || colorOf(id); }
function fromTpl(t, title) {
  const b = { title, visible: false, at: Date.now(), tpl: t.id, layout: t.layout || "wand" };
  for (const k of ["prompt", "bg", "kidCat", "direct", "names"]) if (t[k]) b[k] = t[k];
  if (t.tools) b.tools = { ...t.tools };
  if (t.cats) b.cats = t.cats.map(([title, color]) => ({ id: newId("c"), title, color, note: "" }));
  return b;
}
function tplSVG(t) {
  const P = { c0: "#f3dc84", c1: "#f4c4bd", c2: "#b9d2ea", c3: "#c3dbb4", c4: "#d6c6ec" }, ks = Object.keys(P);
  const cs = (t.cats || []).map(c => P[c[1]] || P.c0);
  let g = "";
  if (t.layout === "spalten") { const n = cs.length || 3, w = 112 / n; cs.forEach((c, k) => { const x = 4 + k * w; g += `<rect x="${x + 2}" y="3" width="${w - 4}" height="5" rx="2" fill="${c}"/><rect x="${x + 4}" y="11" width="${w - 8}" height="9" rx="2" fill="${c}" opacity=".75"/><rect x="${x + 4}" y="23" width="${w - 8}" height="9" rx="2" fill="${c}" opacity=".75"/>`; }); }
  else if (t.layout === "mind") { const pts = [[20, 8], [20, 32], [100, 8], [100, 32]]; pts.forEach(([x, y], k) => { g += `<path d="M60,20 C${(60 + x) / 2},20 ${(60 + x) / 2},${y} ${x},${y}" stroke="${cs[k] || P[ks[k]]}" stroke-width="3" fill="none"/><rect x="${x - 12}" y="${y - 5}" width="24" height="10" rx="4" fill="${cs[k] || P[ks[k]]}"/>`; }); g += `<ellipse cx="60" cy="20" rx="16" ry="9" fill="#fff" stroke="#3f5f86" stroke-width="2"/>`; }
  else if (t.layout === "liste") { for (let k = 0; k < 3; k++) g += `<rect x="30" y="${3 + k * 12}" width="60" height="9" rx="2" fill="${P[ks[k + 1]]}"/>`; }
  else if (t.layout === "zeit") { g += `<line x1="6" y1="10" x2="114" y2="10" stroke="#3f5f86" stroke-width="2" opacity=".5"/>`; for (let k = 0; k < 4; k++) g += `<circle cx="${18 + k * 28}" cy="10" r="4" fill="#3f5f86"/><rect x="${8 + k * 28}" y="18" width="20" height="16" rx="2" fill="${P[ks[k]]}"/>`; }
  else { for (let k = 0; k < 8; k++) g += `<rect x="${8 + (k % 4) * 27}" y="${3 + Math.floor(k / 4) * 18}" width="22" height="14" rx="2" fill="${P[ks[(k * 3 + t.id.length) % 5]]}" transform="rotate(${k % 2 ? 3 : -3} ${19 + (k % 4) * 27} ${10 + Math.floor(k / 4) * 18})"/>`; }
  return `<svg class="tpl-p" viewBox="0 0 120 40" aria-hidden="true">${g}</svg>`;
}
function newBoardHTML() {
  const t = TPL.find(x => x.id === S.tpl) || TPL[0];
  return `<section class="panel"><div><h2>Neue Pinnwand</h2><p class="sub">Wählen Sie eine Vorlage. Spalten, Fragen und Werkzeuge sind dann schon vorbereitet und lassen sich später ändern. Eine neue Pinnwand ist zuerst versteckt.</p></div>
    <div class="tpls" role="list">${TPL.map(x => `<button type="button" class="tpl" role="listitem" data-act="tpl" data-v="${x.id}" aria-pressed="${x.id === t.id}"><span class="tpl-top"><span class="tpl-i" aria-hidden="true">${x.icon}</span><b>${esc(x.name)}</b></span>${tplSVG(x)}<span class="tpl-d">${esc(x.desc)}</span></button>`).join("")}</div>
    ${t.cats ? `<p class="sub tpl-sel"><b>${esc(t.name)}:</b> ${t.cats.map(c => "«" + esc(c[0]) + "»").join(" · ")}</p>` : ""}
    <div class="row"><input class="field grow" id="newBoard" data-keep maxlength="60" placeholder="${esc(t.ph)}" aria-label="Name der Pinnwand"><button class="btn" type="button" data-act="newboard">${t.id === "leer" ? "Erstellen" : esc(t.icon) + " Erstellen"}</button></div></section>`;
}
function bsetHTML() {
  const b = curBoard(); if (!b) return "";
  const lay = layoutOf(), hasCats = cats().length > 0;
  const seg = (act, list, cur) => `<div class="seg">${list.map(([k, l]) => `<button type="button" data-act="${act}" data-v="${k}" aria-pressed="${k === cur}">${l}</button>`).join("")}</div>`;
  const opt = (k, l) => `<label class="tg"><input type="checkbox" data-act="bopt" data-k="${k}" ${b[k] ? "checked" : ""}>${l}</label>`;
  return `<details class="panel settings" id="bsetBox" ${S.showBset ? "open" : ""}><summary><h2>Darstellung und Einstellungen</h2><span class="sub">Wand, Spalten, Liste, Zeitstrahl oder Mindmap · Auftrag · Hintergrund${tplOf(b) ? " · Vorlage «" + esc(tplOf(b).name) + "»" : ""}</span></summary>
    <div class="bset">
      <div><span class="tool-l">Darstellung</span>${seg("blayout", LAYOUTS, lay)}
        <p class="sub">${{ wand: "Zettel nebeneinander, Kategorien als Übertitel.", spalten: "Jede Kategorie ist eine Spalte. Gut für Pro und Contra, Klassenrat, Exit-Ticket.", liste: "Alle Zettel untereinander, gut für Fragen.", zeit: "Zettel der Reihe nach auf einer Linie. Die Reihenfolge legen Sie unter «Sortieren» fest.", mind: "Der Auftrag (oder der Name) steht in der Mitte, die Kategorien sind die Äste." }[lay]}
        ${(lay === "spalten" || lay === "mind") && !hasCats ? ` <b>Legen Sie unter «Sortieren» Kategorien an, sie werden zu ${lay === "mind" ? "Ästen" : "Spalten"}.</b>` : ""}</p></div>
      <div><span class="tool-l">Hintergrund</span>${seg("bbg", BGS, b.bg || "")}</div>
      <label><span class="tool-l">Auftrag oder Frage für die Kinder</span><textarea class="field" id="bPrompt" data-keep rows="2" maxlength="300" placeholder="z. B. Was weisst du schon über Igel?">${esc(b.prompt || "")}</textarea></label>
      <div><span class="tool-l">Optionen</span><div class="tools-set">
        ${hasCats ? opt("kidCat", lay === "mind" ? "Kinder wählen den Ast selbst" : "Kinder wählen die Spalte selbst") : ""}
        ${opt("direct", "Zettel der Kinder ohne Freigabe anpinnen")}
        ${opt("names", "Namen auf den Zetteln zeigen")}</div>
        <p class="sub">Spalten, Äste und Kategorien benennen, färben und ordnen Sie unter «Sortieren».${b.direct ? " <b>Ohne Freigabe hängen die Zettel der Kinder sofort an der Pinnwand. Sie können sie jederzeit entfernen.</b>" : ""}</p></div>
      <div class="row"><button class="btn ghost small" type="button" data-act="print">🖨️ Drucken</button></div>
    </div></details>`;
}
function kidCatHTML() {
  const b = curBoard(), cs = cats(); if (!b || !b.kidCat || !cs.length) return "";
  if (S.kcat && !cs.some(c => c.id === S.kcat)) S.kcat = null;
  return `<div class="kcat"><span class="tool-l">${layoutOf() === "mind" ? "An welchen Ast gehört dein Zettel?" : "Wohin gehört dein Zettel?"}</span>
    <div class="kcat-b">${cs.map(c => `<button type="button" class="kc ${c.color || ""}" data-act="kcat" data-v="${c.id}" aria-pressed="${S.kcat === c.id}">${esc(c.title)}</button>`).join("")}</div></div>`;
}
function layoutBoard(lay, list, fn, kid) {
  const cs = cats(), b = curBoard() || {};
  const groups = cs.map(c => ({ c, l: list.filter(([, i]) => i.cat === c.id) }));
  const rest = list.filter(([, i]) => catIdx(i) >= 1e6);
  if (lay === "zeit") {
    const ord = i => typeof i.order === "number" ? i.order : 1e9;
    const l = list.slice().sort((a, b) => ord(a[1]) - ord(b[1]) || timeCmp(a[1], b[1])), drag = !kid && S.view === "lp";
    return `${drag && l.length > 1 ? `<p class="sub tl-tip">Zum Verschieben die Nummer eines Zettels anfassen und nach links oder rechts ziehen.</p>` : ""}<div class="tl" id="tl" role="list">${l.map((x, k) => { const c = cs.find(c => c.id === x[1].cat); return `<div class="tl-it" role="listitem" data-tid="${x[0]}">${drag ? `<button type="button" class="tl-dot tl-h" data-tlh="${x[0]}" title="Ziehen, um den Zettel zu verschieben" aria-label="Zettel ${k + 1} verschieben (Pfeiltasten)">${k + 1}</button>` : `<span class="tl-dot">${k + 1}</span>`}<span class="tl-stem"></span>${c ? `<span class="tl-cat">${esc(c.title)}</span>` : ""}${fn(x)}</div>`; }).join("")}</div>`;
  }
  if (lay === "spalten") {
    if (!cs.length) return `<div class="board">${list.map(fn).join("")}</div>`;
    if (rest.length) groups.push({ c: null, l: rest });
    return `<div class="cols">${groups.map(({ c, l }) => `<section class="col" data-c="${(c && c.color) || ""}"><h3 class="colhead">${c ? esc(c.title) : "Weitere"} <small>${l.length}</small></h3>
      <div class="colbody">${l.length ? l.map(fn).join("") : `<p class="colempty">${kid ? "Noch leer" : "Noch kein Zettel"}</p>`}</div>
      ${c && (c.note || "").trim() ? `<div class="catnote"><span class="tool-l">${kid ? "Beschluss" : "Beschluss / Kommentar"}</span><p>${esc(c.note)}</p></div>` : ""}</section>`).join("")}</div>`;
  }
  // Mindmap: Mitte = Auftrag oder Name, Äste = Kategorien, Blätter = Zettel (antippen zeigt den ganzen Zettel)
  const br = cs.length ? groups : [{ c: null, l: list, bare: true }];
  if (cs.length && rest.length) br.push({ c: null, l: rest });
  const one = matchMedia("(max-width:760px)").matches || br.length === 1;
  const half = one ? 0 : Math.floor(br.length / 2), left = br.slice(br.length - half), right = br.slice(0, br.length - half);
  const leaf = ([id, i]) => `<button type="button" class="mm-leaf note ${noteColor(id, i)}${S.mmFocus === id ? " cur" : ""}" data-act="mmfocus" data-id="${id}">${esc(i.text)}${b.names && i.by && (!kid || i.by !== "Lehrperson") ? `<small>${esc(i.by)}</small>` : ""}</button>`;
  const edit = !kid && S.view === "lp";
  const node = c => !c ? `<div class="mm-node">Weitere</div>` : edit && S.astEdit === c.id
    ? `<div class="mm-node mm-ed"><input class="field" id="ast-${c.id}" data-keep maxlength="60" value="${esc(c.title)}" aria-label="Name des Astes"><span class="row"><button class="btn small" type="button" data-act="astsave" data-id="${c.id}">OK</button><button class="del ${S.armed === "k:" + c.id ? "arm" : ""}" type="button" data-act="delcat" data-id="${c.id}">${S.armed === "k:" + c.id ? "Wirklich löschen?" : "Löschen"}</button></span></div>`
    : edit ? `<button type="button" class="mm-node" data-act="astedit" data-id="${c.id}" title="Ast umbenennen oder löschen">${esc(c.title)}</button>` : `<div class="mm-node">${esc(c.title)}</div>`;
  const branch = side => ({ c, l, bare }) => `<div class="mm-br ${side}" data-c="${(c && c.color) || ""}">${bare ? "" : node(c)}<div class="mm-leaves">${l.length ? l.map(leaf).join("") : `<span class="mm-empty">${kid ? "noch leer" : "noch kein Zettel"}</span>`}</div></div>`;
  const f = S.mmFocus && list.find(([id]) => id === S.mmFocus);
  return `<div class="mm-wrap"><div class="mm${one ? " one" : ""}" id="mm"><svg class="mm-svg" id="mmSvg" aria-hidden="true"></svg>
      ${one ? "" : `<div class="mm-side l">${left.map(branch("l")).join("")}</div>`}
      <div class="mm-center">${esc(b.prompt || b.title || "Thema")}</div>
      <div class="mm-side r">${right.map(branch("r")).join("")}</div></div></div>
    ${f ? `<div class="mm-focus"><div class="row" style="justify-content:space-between"><span class="tool-l">Zettel im Detail</span><button class="btn ghost small" type="button" data-act="mmclose">Schliessen</button></div>${edit && cs.length ? `<label class="row lpcat"><span class="tool-l">An den Ast</span><select class="field" data-act="leafcat" data-id="${f[0]}"><option value="">ohne Ast</option>${cs.map(c => `<option value="${c.id}" ${f[1].cat === c.id ? "selected" : ""}>${esc(c.title)}</option>`).join("")}</select></label>` : ""}<div class="board">${fn(f)}</div></div>`
      : list.length ? `<p class="sub mm-hint">Tippe auf einen Zettel, um ihn gross zu sehen${kid ? " und mitzumachen" : ""}.${edit ? " Tippen Sie auf einen Ast, um ihn umzubenennen." : ""}</p>` : ""}
    ${edit ? `<div class="row mm-add"><input class="field grow" id="newAst" data-keep maxlength="60" placeholder="Neuer Ast, z. B. «Feinde»" aria-label="Name des neuen Astes"><button class="btn" type="button" data-act="addast">+ Ast</button></div>` : ""}`;
}
function drawMind() {
  const mm = document.getElementById("mm"), svg = document.getElementById("mmSvg"); if (!mm || !svg) return;
  const R = mm.getBoundingClientRect(), W = mm.offsetWidth, H = mm.offsetHeight;
  svg.setAttribute("width", W); svg.setAttribute("height", H); svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
  const box = el => { const r = el.getBoundingClientRect(); return { l: r.left - R.left, r: r.right - R.left, cx: (r.left + r.right) / 2 - R.left, b: r.bottom - R.top, cy: (r.top + r.bottom) / 2 - R.top }; };
  const one = mm.classList.contains("one");
  const c = box(mm.querySelector(".mm-center"));
  const path = (x1, y1, x2, y2, col, w) => { const mx = (x1 + x2) / 2; return `<path d="M${x1},${y1} C${mx},${y1} ${mx},${y2} ${x2},${y2}" stroke="${col}" stroke-width="${w}" fill="none" stroke-linecap="round"/>`; };
  let d = "";
  mm.querySelectorAll(".mm-br").forEach(brEl => {
    const right = brEl.classList.contains("r"), node = brEl.querySelector(".mm-node"), col = getComputedStyle(brEl).getPropertyValue("--mc").trim() || "#9aa39c";
    const n = node ? box(node) : null;
    if (n && one) d += `<path d="M${c.l + 30},${c.b - 6} Q8,${c.b} 8,${c.b + 24} L8,${n.cy - 12} Q8,${n.cy} 20,${n.cy} L${n.l},${n.cy}" stroke="${col}" stroke-width="4" fill="none" stroke-linecap="round" stroke-linejoin="round"/>`;
    else if (n) d += path(right ? c.r : c.l, c.cy, right ? n.l : n.r, n.cy, col, 5);
    const from = n || c;
    brEl.querySelectorAll(".mm-leaf").forEach(lf => { const x = box(lf); d += path(right ? from.r : from.l, from.cy, right ? x.l : x.r, x.cy, col, 2.5); });
  });
  svg.innerHTML = d;
}
addEventListener("resize", () => { clearTimeout(drawMind.t); drawMind.t = setTimeout(() => { if (layoutOf() === "mind" && document.getElementById("mm")) render(); }, 150); });''')

# --- Darstellung wählen: Wand bleibt wie bisher, die anderen Ansichten übernehmen
rep('function groupedBoard(list, fn, kid) {\n  const cs = cats();', 'function groupedBoard(list, fn, kid) {\n  const lay = layoutOf(); if (lay === "spalten" || lay === "zeit" || lay === "mind") return layoutBoard(lay, list, fn, kid);\n  const cs = cats();')
rep('  layoutTracks();\n', '  layoutTracks(); drawMind();\n')
rep('''  $("#app").classList.toggle("present-on", S.view === "show");''', '''  $("#app").classList.toggle("present-on", S.view === "show");
  { const bd = S.board && curBoard(); document.body.dataset.bg = (bd && bd.bg) || ""; $("#app").dataset.lay = bd ? layoutOf() : ""; }''')

# Präsentieren: bei Spalten, Zeitstrahl und Mindmap zuerst die ganze Pinnwand zeigen
rep('S.tab = b.dataset.v === "show" && cats().length ? "cats" : "board";', 'S.tab = b.dataset.v === "show" && cats().length && (layoutOf() === "wand" || layoutOf() === "liste") ? "cats" : "board";')

# --- Farben: Zettel nehmen die Farbe ihrer Spalte / ihres Astes
rep('<article class="note ${colorOf(id)}"><p class="txt">${esc(i.text)}</p>', '<article class="note ${noteColor(id, i)}"><p class="txt">${esc(i.text)}</p>${curBoard()?.names && i.by ? `<p class="by">– ${esc(i.by)}</p>` : ""}')
rep('<article class="note ${colorOf(id)}">${S.editing === id && !present', '<article class="note ${noteColor(id, i)}">${S.editing === id && !present')
rep('${i.by && !present ? `<p class="by">– ${esc(i.by)}</p>` : ""}', '${i.by && (!present || curBoard()?.names) ? `<p class="by">– ${esc(i.by)}</p>` : ""}')
rep('`<div class="sortcard note ${colorOf(id)}"', '`<div class="sortcard note ${noteColor(id, i)}"')
rep('class="one-mini note ${colorOf(sid)}', 'class="one-mini note ${noteColor(sid, si)}')
rep('<article class="note ${colorOf(id)} pcard"', '<article class="note ${noteColor(id, i)} pcard"')
rep('aria-label="Name der Kategorie">', '''aria-label="Name der Kategorie">
        <span class="ccol" role="group" aria-label="Farbe">${CCOL.map(([k, l]) => `<button type="button" class="${k}" data-act="catcolor" data-id="${c.id}" data-v="${k}" aria-pressed="${c.color === k}" title="${l}" aria-label="${l}"></button>`).join("")}</span>''')

# --- Neue Pinnwand aus einer Vorlage, Vorlage auf der Karte, Kopieren
rep('''  return `<section class="panel"><div><h2>Neue Pinnwand</h2><p class="sub">Eine neue Pinnwand ist zuerst versteckt. So können Sie in Ruhe Zettel vorbereiten und sie dann für die Kinder sichtbar machen.</p></div>
    <div class="row"><input class="field grow" id="newBoard" data-keep maxlength="60" placeholder="z. B. Ideen für die Schulreise"><button class="btn" type="button" data-act="newboard">Erstellen</button></div></section>''',
    '''  return `${newBoardHTML()}''')
rep('''    return `<article class="bcard">${minis(id)}${visPill(b.visible)}${head}''', '''    return `<article class="bcard">${minis(id)}${visPill(b.visible)}${tplOf(b) ? `<span class="btpl">${tplOf(b).icon} ${esc(tplOf(b).name)}</span>` : ""}${head}''')
rep('''<button class="btn ghost small" type="button" data-act="vis" data-id="${id}">${b.visible ? "Verstecken" : "Sichtbar machen"}</button></div>''',
    '''<button class="btn ghost small" type="button" data-act="vis" data-id="${id}">${b.visible ? "Verstecken" : "Sichtbar machen"}</button><button class="btn ghost small" type="button" data-act="copyboard" data-id="${id}" title="Gleiche Spalten, Einstellungen und Ihre eigenen Zettel, ohne die Zettel der Kinder">Kopieren</button></div>''')
rep('try { const nid = await addBoard({ title, visible: false, at: Date.now() });', 'try { const nid = await addBoard(fromTpl(TPL.find(x => x.id === S.tpl) || TPL[0], title)); S.showBset = true;')
rep('''  else if (act === "vis") {''', '''  else if (act === "tpl") { S.tpl = b.dataset.v; render(); $("#newBoard")?.focus(); }
  else if (act === "copyboard") {
    const src = S.boards.get(id); if (!src) return;
    const { visible, at, ...rest } = src;
    try {
      const nid = await addBoard(JSON.parse(JSON.stringify({ ...rest, title: (src.title + " (Kopie)").slice(0, 60), visible: false, at: Date.now() })));
      const mine = [...S.ideas].filter(([, i]) => i.boardId === id && i.status === "ok" && i.by === "Lehrperson");
      for (const [, i] of mine) await addIdea(JSON.parse(JSON.stringify({ text: i.text, by: "Lehrperson", uid: i.uid, boardId: nid, status: "ok", tools: i.tools || {}, cat: i.cat || null, order: i.order, lp: i.lp, at: Date.now(), okAt: i.okAt || Date.now() })));
      toast("Kopie erstellt. Sie ist noch versteckt.");
    } catch (err) { failed(err); }
  }
  else if (act === "blayout" || act === "bbg") {
    const k = act === "blayout" ? "layout" : "bg", bd = curBoard(); if (!bd) return;
    bd[k] = b.dataset.v; S.mmFocus = null; render();
    try { await patchBoard(S.board, { [k]: b.dataset.v }); } catch (err) { failed(err); }
  }
  else if (act === "catcolor") { saveCats(cats().map(c => c.id === id ? { ...c, color: c.color === b.dataset.v ? "" : b.dataset.v } : c)); }
  else if (act === "kcat") { S.kcat = S.kcat === b.dataset.v ? null : b.dataset.v; render(); }
  else if (act === "mmfocus") { S.mmFocus = S.mmFocus === id ? null : id; render(); if (S.mmFocus) document.querySelector(".mm-focus")?.scrollIntoView({ block: "nearest", behavior: "smooth" }); }
  else if (act === "mmclose") { S.mmFocus = null; render(); }
  else if (act === "print") { window.print(); }
  else if (act === "vis") {''')
rep('  else if (act === "open") { S.board = id;', '  else if (act === "open") { S.kcat = null; S.mmFocus = null; S.board = id;')

# --- Auftrag oben an der Pinnwand und beim Präsentieren
rep('''<button class="btn ${b.visible ? "ghost" : ""} small" type="button" data-act="vis" data-id="${S.board}">${b.visible ? "Verstecken" : "Für Kinder sichtbar machen"}</button>` : ""}</div>`;''',
    '''<button class="btn ${b.visible ? "ghost" : ""} small" type="button" data-act="vis" data-id="${S.board}">${b.visible ? "Verstecken" : "Für Kinder sichtbar machen"}</button>` : ""}</div>${(b.prompt || "").trim() && b.layout !== "mind" ? `<p class="bprompt">${esc(b.prompt)}</p>` : ""}`;''')
rep('''<button class="btn" type="button" data-act="role" data-v="lp">Präsentation beenden</button></div>`;''',
    '''<button class="btn" type="button" data-act="role" data-v="lp">Präsentation beenden</button></div>${(curBoard()?.prompt || "").trim() && layoutOf() !== "mind" && S.tab !== "cats" ? `<p class="bprompt">${esc(curBoard().prompt)}</p>` : ""}`;''')

# --- Lehrperson: Einstellungen der Pinnwand, Werkzeuge pro Pinnwand, Spalte beim Selbst-Anpinnen
rep('${toolToggles("def", S.defaults)}', '${toolToggles("def", curDefaults())}')
rep('  ${settingsHTML()}\n  <div class="lp-grid">', '  ${bsetHTML()}\n  ${settingsHTML()}\n  <div class="lp-grid">')
s = s.replace('tools: { ...S.defaults }', 'tools: { ...curDefaults() }')
rep('''  if (el.dataset.act === "deftool") { S.defaults[el.dataset.k] = el.checked; ls.set("pw-tools2", S.defaults); }''',
    '''  if (el.dataset.act === "deftool") {
    S.defaults[el.dataset.k] = el.checked; ls.set("pw-tools2", S.defaults);
    const bd = curBoard(); if (bd) { const t = { ...(bd.tools || S.defaults), [el.dataset.k]: el.checked }; bd.tools = t; try { await patchBoard(S.board, { tools: t }); } catch (err) { failed(err); } }
  }
  else if (el.dataset.act === "bopt") { const bd = curBoard(); if (!bd) return; bd[el.dataset.k] = el.checked; render(); try { await patchBoard(S.board, { [el.dataset.k]: el.checked }); } catch (err) { failed(err); } }
  else if (el.id === "bPrompt") { const bd = curBoard(); if (!bd) return; const v = el.value.trim(); bd.prompt = v; render(); try { await patchBoard(S.board, { prompt: v }); toast("Auftrag gespeichert."); } catch (err) { failed(err); } }''')
rep('''<textarea class="field" id="lpIdea" data-keep maxlength="280" rows="3" placeholder="z. B. Wohin soll die Schulreise gehen?"></textarea>''',
    '''<textarea class="field" id="lpIdea" data-keep maxlength="280" rows="3" placeholder="z. B. Wohin soll die Schulreise gehen?"></textarea>
    ${cats().length ? `<label class="row lpcat"><span class="tool-l">${layoutOf() === "mind" ? "An den Ast" : layoutOf() === "spalten" ? "In die Spalte" : "Kategorie"}</span><select class="field" id="lpCat" data-keep><option value="">ohne</option>${cats().map(c => `<option value="${c.id}">${esc(c.title)}</option>`).join("")}</select></label>` : ""}''')
rep('by: "Lehrperson", uid: myKey(), boardId: S.board, status: "ok",', 'by: "Lehrperson", uid: myKey(), boardId: S.board, cat: ($("#lpCat") && $("#lpCat").value) || null, status: "ok",')
rep('document.addEventListener("toggle", e => { if (e.target.id === "settingsBox") S.showSettings = e.target.open; }, true);',
    'document.addEventListener("toggle", e => { if (e.target.id === "settingsBox") S.showSettings = e.target.open; if (e.target.id === "bsetBox") S.showBset = e.target.open; }, true);')

# --- Leere Spalten und Äste schon zeigen, bevor Zettel hängen
rep('''  if (!items.length) return html + tabsHTML([["board", "Pinnwand"]]) + `<div class="empty"><h3>Noch keine Zettel an der Pinnwand</h3>''',
    '''  if (!items.length && !structural()) return html + tabsHTML([["board", "Pinnwand"]]) + `<div class="empty"><h3>Noch keine Zettel an der Pinnwand</h3>''')
rep('''  if (S.tab === "board" && !boardItems.length) S.tab = "baro";
  const tabs = []; if (boardItems.length) tabs.push(["board", "Pinnwand"]);''',
    '''  if (S.tab === "board" && !boardItems.length && hasBaro && !structural()) S.tab = "baro";
  const tabs = []; if (boardItems.length || structural()) tabs.push(["board", "Pinnwand"]);''')
rep('''  if (!items.length) return html + `<div class="empty"><h3>Die Pinnwand ist noch leer</h3>''',
    '''  if (!items.length && !(structural() && S.tab === "board")) return html + `<div class="empty"><h3>Die Pinnwand ist noch leer</h3>''')
rep('''    (boardItems.length ? `${groupedBoard(boardItems, ([id, i]) => teacherNote(id, i, res[id]))}`''',
    '''    (boardItems.length || structural() ? `${groupedBoard(boardItems, ([id, i]) => teacherNote(id, i, res[id]))}`''')

# --- Kinder: Spalte wählen, ohne Freigabe anpinnen
rep('''    <label for="ideaIn" class="sub">Schreib deine Idee auf. Die Lehrperson schaut sie an und hängt sie dann an die Pinnwand.</label>''',
    '''    ${kidCatHTML()}<label for="ideaIn" class="sub">${curBoard()?.direct ? "Schreib deine Idee auf. Sie hängt dann gleich an der Pinnwand." : "Schreib deine Idee auf. Die Lehrperson schaut sie an und hängt sie dann an die Pinnwand."}</label>''')
rep('''    if (!S.my.name) { toast("Schreib oben zuerst deinen Namen."); $("#nameIn")?.focus(); return; }''',
    '''    if (!S.my.name) { toast("Schreib oben zuerst deinen Namen."); $("#nameIn")?.focus(); return; }
    const bd = curBoard() || {}, wantCat = bd.kidCat && cats().length;
    if (wantCat && !S.kcat) { toast(layoutOf() === "mind" ? "Wähle zuerst, an welchen Ast dein Zettel gehört." : "Wähle zuerst, wohin dein Zettel gehört."); return; }
    const extra = { status: bd.direct ? "ok" : "pending" };
    if (wantCat) extra.cat = S.kcat;
    if (bd.direct) { extra.tools = { ...(bd.tools || {}) }; extra.okAt = Date.now(); }''')
rep('await addIdea({ text, by: S.my.name, uid: myKey(), boardId: S.board, status: "pending", at: Date.now() });',
    'await addIdea({ text, by: S.my.name, uid: myKey(), boardId: S.board, ...extra, at: Date.now() });')
rep('toast("Danke! Deine Idee ist bei der Lehrperson.");', 'b.disabled = false; toast(extra.status === "ok" ? "Danke! Dein Zettel hängt jetzt an der Pinnwand." : "Danke! Deine Idee ist bei der Lehrperson.");')

# --- Werkzeug «Herz»: Kinder tippen ein Herz, die Lehrperson sieht, wie viele
rep('agree: "Zustimmung", comment: "Kommentar",', 'agree: "Zustimmung", like: "Herz ❤️", comment: "Kommentar",')
rep('res[id] = { rate: [], rate2: [], baro: [],', 'res[id] = { rate: [], rate2: [], baro: [], like: 0,')
rep('      if (typeof x.rate2 === "number") { a.rate2.push(x.rate2); any = true; a.voters.add(uid); }',
    '      if (typeof x.rate2 === "number") { a.rate2.push(x.rate2); any = true; a.voters.add(uid); }\n      if (x.like === true) { a.like++; any = true; a.voters.add(uid); }')
rep('  h += lpcHTML(id, i, true, true);', '  if (t.like) h += `<div class="tool"><button type="button" class="heart" data-act="like" data-id="${id}" aria-pressed="${!!v.like}">${v.like ? "❤️" : "🤍"} Gefällt mir</button></div>`;\n  h += lpcHTML(id, i, true, true);')
rep('  h += lpcHTML(id, i, present);', '  if (t.like && !t.baro) h += `<div class="tool"><span class="hearts" aria-label="${a.like} Herzen">❤️ ${a.like}</span></div>`;\n  h += lpcHTML(id, i, present);')
rep('''  else if (act === "rate2") {''', '''  else if (act === "like") { const m = myVote(id); if (S.peek) return; if (m.like) delete m.like; else m.like = true; touchMy(400); render(); }
  else if (act === "rate2") {''')
rep('["agree", "nach Zustimmung"], ["baro", "nach Barometer"]];', '["agree", "nach Zustimmung"], ["like", "nach Herzen"], ["baro", "nach Barometer"]];')
rep('  if (by === "rate2") return a.rate2Avg;', '  if (by === "rate2") return a.rate2Avg;\n  if (by === "like") return a.like || null;')
rep('  if (a && a.rate2Avg != null) p.push("Ø2 " + fmt(a.rate2Avg));', '  if (a && a.rate2Avg != null) p.push("Ø2 " + fmt(a.rate2Avg));\n  if (a && a.like) p.push("❤️ " + a.like);')

# --- Gestaltung
rep('/* Erweiterungen */', r'''/* Erweiterungen */
.tpls{display:grid;grid-template-columns:repeat(auto-fill,minmax(168px,1fr));gap:10px}
.tpl{all:unset;box-sizing:border-box;cursor:pointer;display:flex;flex-direction:column;gap:6px;padding:10px 12px 12px;border:2px solid var(--line);border-radius:16px;background:#fff;transition:border-color .15s,box-shadow .15s}
.tpl:hover{border-color:var(--leaf)}
.tpl:focus-visible{outline:2px solid var(--rose);outline-offset:2px}
.tpl[aria-pressed="true"]{border-color:var(--leaf);background:var(--leaf-soft);box-shadow:0 0 0 3px rgba(126,165,106,.22)}
.tpl-top{display:flex;align-items:center;gap:8px}
.tpl-top b{font-weight:800;line-height:1.15;font-size:.95rem}
.tpl-i{font-size:1.45rem;line-height:1}
.tpl-p{width:100%;height:38px;display:block}
.tpl-d{font-size:.8rem;color:var(--muted);line-height:1.3}
.tpl-sel{margin:0}
.btpl{align-self:flex-start;font-size:.78rem;font-weight:800;color:var(--muted);background:var(--paper);border-radius:999px;padding:2px 10px}
.bprompt{margin:0;font-family:var(--hand);font-size:1.55rem;line-height:1.25;background:#fff;border-radius:16px;border-left:6px solid var(--sky);padding:10px 16px;box-shadow:var(--shadow);overflow-wrap:anywhere}
.present-on .bprompt{font-size:2rem}
.bset{display:flex;flex-direction:column;gap:14px;margin-top:12px}
.bset .seg{margin-top:4px}
.bset .sub{margin:6px 0 0}
.bset textarea{border-radius:14px;margin-top:4px}
.ccol{display:inline-flex;gap:4px}
.ccol button{width:24px;height:24px;border-radius:50%;border:2px solid rgba(0,0,0,.12);padding:0}
.ccol button[aria-pressed="true"]{border-color:var(--ink);box-shadow:0 0 0 2px #fff inset}
.lpcat{gap:8px;flex-wrap:nowrap}
.lpcat select{flex:1;min-height:40px}
.kcat{display:flex;flex-direction:column;gap:6px}
.kcat-b{display:flex;flex-wrap:wrap;gap:8px}
.kc{border:2px solid transparent;border-radius:14px;padding:8px 14px;font-weight:800;font-size:1rem;color:var(--ink);box-shadow:0 2px 6px rgba(40,60,45,.12)}
.kc:not([class*=" c"]){background:#fff;border-color:var(--line)}
.kc[aria-pressed="true"]{border-color:var(--ink);box-shadow:0 0 0 3px rgba(31,36,33,.15)}
.heart{border:1px solid var(--line);background:rgba(255,255,255,.85);border-radius:999px;padding:5px 14px;font-weight:800;font-size:.95rem;align-self:flex-start}
.heart[aria-pressed="true"]{border-color:#e07a70;background:#fff}
.hearts{font-weight:800;font-size:1.05rem}
/* Spalten */
.cols{display:flex;gap:16px;overflow-x:auto;align-items:flex-start;padding:4px 2px 14px;scroll-snap-type:x proximity}
.col{flex:1 0 290px;max-width:440px;background:rgba(255,255,255,.6);border-radius:18px;padding:0 0 14px;display:flex;flex-direction:column;gap:12px;scroll-snap-align:start;border-top:10px solid var(--mc,#c9cfca);box-shadow:var(--shadow)}
.present-on .col{max-width:none;flex-basis:320px}
.colhead{margin:0;padding:10px 14px 0;font-family:var(--bubble);font-weight:600;font-size:1.35rem;display:flex;gap:8px;align-items:baseline}
.present-on .colhead{font-size:1.8rem}
.colhead small{font-family:var(--ui);font-size:.8rem;color:var(--muted);font-weight:800}
.colbody{display:flex;flex-direction:column;gap:20px;padding:8px 12px 0}
.colbody>.note{margin:0}
.colempty{font-family:var(--hand);font-size:1.15rem;color:#a7ada8;margin:0}
.col .catnote{margin:0 12px}
[data-c="c0"]{--mc:#e2bd4a;--mb:var(--n1)}[data-c="c1"]{--mc:#e0948a;--mb:var(--n2)}[data-c="c2"]{--mc:#86a9cc;--mb:var(--n3)}[data-c="c3"]{--mc:#8db27a;--mb:var(--n4)}[data-c="c4"]{--mc:#a98fcf;--mb:var(--n5)}
/* Liste */
#app[data-lay="liste"] .board{grid-template-columns:minmax(0,1fr)!important;max-width:760px;margin-inline:auto;width:100%}
#app[data-lay="liste"] .note:nth-child(n){transform:none}
/* Zeitstrahl */
.tl{display:flex;gap:0;overflow-x:auto;padding:6px 4px 16px;align-items:flex-start;scroll-snap-type:x proximity}
.tl-it{flex:0 0 300px;display:flex;flex-direction:column;align-items:stretch;position:relative;padding:0 10px;scroll-snap-align:start}
.tl-it::before{content:"";position:absolute;top:19px;left:0;right:0;height:4px;background:#3f5f86;opacity:.3}
.tl-it:first-child::before{left:50%}.tl-it:last-child::before{right:50%}.tl-it:only-child::before{display:none}
.tl-dot{align-self:center;width:40px;height:40px;border-radius:50%;background:#3f5f86;color:#fff;display:grid;place-items:center;font-weight:700;font-family:var(--bubble);font-size:1.1rem;position:relative;z-index:1;box-shadow:0 0 0 5px #fff}
.tl-stem{align-self:center;width:3px;height:22px;background:#3f5f86;opacity:.3}
.tl-cat{align-self:center;font-size:.75rem;font-weight:800;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);margin:0 0 4px;text-align:center}
.tl .note{margin:0;transform:none!important}
.present-on .tl-it{flex-basis:340px}
/* Mindmap */
.mm-wrap{overflow-x:auto;padding:4px 0 8px}
.mm{position:relative;display:grid;grid-template-columns:minmax(0,1fr) auto minmax(0,1fr);align-items:center;gap:0 64px;min-width:820px;padding:18px 8px}
.mm.one{display:flex;flex-direction:column;align-items:stretch;min-width:0;gap:30px;padding:12px 4px}
.mm.one .mm-center{align-self:center}
.mm.one .mm-side{padding-left:18px;gap:18px}
.mm.one .mm-br{gap:22px}
.mm-svg{position:absolute;left:0;top:0;pointer-events:none;overflow:visible}
.mm-side{display:flex;flex-direction:column;gap:24px;position:relative;z-index:1;min-width:0}
.mm-center{position:relative;z-index:1;background:#fff;border:4px solid #3f5f86;border-radius:40px;padding:18px 24px;max-width:250px;text-align:center;font-family:var(--bubble);font-weight:700;font-size:1.5rem;line-height:1.15;color:#3f5f86;box-shadow:0 6px 18px rgba(40,60,45,.16);overflow-wrap:anywhere}
.present-on .mm-center{font-size:2rem;max-width:320px}
.mm-br{display:flex;align-items:center;gap:40px;min-width:0}
.mm-br.l{flex-direction:row-reverse}
.mm-node{flex:none;background:var(--mb,#fff);border:3px solid var(--mc,#c9cfca);border-radius:16px;padding:7px 14px;font-weight:600;font-family:var(--bubble);font-size:1.15rem;line-height:1.15;max-width:190px;overflow-wrap:anywhere}
.mm-leaves{display:flex;flex-direction:column;gap:10px;align-items:flex-start;min-width:0}
.mm-br.l .mm-leaves{align-items:flex-end}
.mm-leaf{all:unset;box-sizing:border-box;cursor:pointer;margin:0;padding:8px 12px;max-width:250px;font-family:var(--hand);font-size:1.15rem;line-height:1.15;border-radius:6px 6px 14px 6px;box-shadow:var(--note-shadow);overflow-wrap:anywhere;display:flex;flex-direction:column;gap:2px}
.mm-leaf::before{display:none}
.mm-leaf small{font-family:var(--ui);font-size:.72rem;color:var(--muted);font-weight:700}
.mm-leaf:hover,.mm-leaf:focus-visible{box-shadow:0 0 0 3px var(--mc,#c9cfca),var(--note-shadow)}
.mm-leaf.cur{box-shadow:0 0 0 3px var(--ink),var(--note-shadow)}
.present-on .mm-leaf{font-size:1.4rem;max-width:300px}
.mm-empty{font-family:var(--hand);color:#a7ada8;font-size:1.05rem}
.mm-hint{text-align:center;margin:0}
.mm-focus{display:flex;flex-direction:column;gap:8px;background:rgba(255,255,255,.6);border-radius:18px;padding:12px 14px}
.mm-focus .board{grid-template-columns:minmax(0,560px);justify-content:center}
/* Hintergründe */
body[data-bg="kork"]{background:radial-gradient(circle at 30% 40%,rgba(90,55,20,.18) 0 1px,transparent 1.6px) 0 0/7px 7px,radial-gradient(circle at 70% 70%,rgba(255,240,210,.22) 0 1px,transparent 1.8px) 0 0/11px 11px,linear-gradient(135deg,#cfa576,#bf925f);background-attachment:fixed}
body[data-bg="karo"]{background:linear-gradient(#dfe8f1 1px,transparent 1px) 0 0/26px 26px,linear-gradient(90deg,#dfe8f1 1px,transparent 1px) 0 0/26px 26px,#fdfdfb;background-attachment:fixed}
body[data-bg="linien"]{background:linear-gradient(transparent 33px,#d8e3ee 34px) 0 0/100% 34px,#fffdf6;background-attachment:fixed}
body[data-bg="himmel"]{background:radial-gradient(ellipse 40% 18% at 20% 12%,#fff 0,transparent 70%),radial-gradient(ellipse 30% 14% at 75% 22%,#fff 0,transparent 70%),linear-gradient(180deg,#cfe5f8,#eef6fc 65%,#f6fbf1);background-attachment:fixed}
body[data-bg="wiese"]{background:radial-gradient(ellipse 70% 30% at 50% 105%,#bcdca6,transparent 70%),linear-gradient(180deg,#fbfdf6,#e4f1d8);background-attachment:fixed}
body[data-bg="kork"] .bhead h2{flex:0 1 auto;background:rgba(255,255,255,.88);border-radius:14px;padding:2px 14px}
body[data-bg="kork"] .tl-cat,body[data-bg="kork"] .mm-hint,body[data-bg="kork"] .colempty{background:rgba(255,255,255,.85);border-radius:999px;padding:1px 10px}
body[data-bg="kork"] #app>.sub{background:rgba(255,255,255,.85);border-radius:999px;padding:2px 12px;align-self:flex-start}
@media print{
  header.top,.tools-bar,.settings,.lp-grid,.tabs,.bhead .btn,.bhead .vis,.note .foot,.note .tools-set,.lpc .edit-btn,.mm-hint,.mm-focus,.toast{display:none!important}
  body{background:#fff!important;padding:0}
  .note{box-shadow:none;border:1px solid #ccc;break-inside:avoid}
  .cols,.tl,.mm-wrap{overflow:visible}
}''')
