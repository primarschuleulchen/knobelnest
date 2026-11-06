# Eigene Vorlagen (nur Klassenkiste): Die Lehrperson kann Vorlagen bearbeiten, löschen und eigene erstellen,
# auch «Als Vorlage speichern» aus einer fertigen Pinnwand. Gespeichert im Pinnwand-Speicher der Klasse
# als settings/vorlagen = { own: [Vorlage …], hide: [IDs der ausgeblendeten mitgelieferten Vorlagen], edit: { ID: Änderungen } }.
# Die Kinder bekommen settings/vorlagen nie (kid_pin gibt nur settings/main.labels weiter).
# In der Eulenkiste und im Artefakt gibt es stattdessen den Hinweis «Hol dir jetzt den Zugang».
# Wird von pin6_patch.py nach pin_stil.py ausgeführt.

rep('const TPL = [\n', 'const TPL0 = [\n')
rep('const LAYOUTS = [["wand", "Wand"],', '''let TPL = TPL0.slice();
const VL_MAX = 30;
function vlState() { const v = S.vl || {}; return { own: Array.isArray(v.own) ? v.own : [], hide: Array.isArray(v.hide) ? v.hide : [], edit: v.edit && typeof v.edit === "object" ? v.edit : {} }; }
function applyVl() {
  const v = vlState();
  TPL = [...TPL0.filter(t => !v.hide.includes(t.id)).map(t => ({ ...t, ...(v.edit[t.id] || {}), id: t.id })), ...v.own.filter(t => t && t.id && t.name)];
  if (!TPL.length) TPL = [TPL0[0]];
}
async function saveVl(v, msg) {
  if (JSON.stringify(v).length > 19000) { toast("Zu viele eigene Vorlagen. Bitte zuerst eine löschen."); return false; }
  S.vl = v; applyVl(); render();
  try { await db.doc("settings/vorlagen").set(JSON.parse(JSON.stringify(v))); if (msg) toast(msg); return true; } catch (err) { failed(err); return false; }
}
function vlBarHTML() {
  const v = vlState(), n = v.hide.length;
  return `<div class="row vl-bar"><button class="btn ${S.vlEdit ? "" : "ghost "}small" type="button" data-act="vledit" aria-pressed="${!!S.vlEdit}">${S.vlEdit ? "✓ Fertig mit Bearbeiten" : "✎ Vorlagen bearbeiten"}</button>
    ${S.vlEdit ? `<span class="sub">Tippen Sie auf eine Vorlage, um sie zu ändern oder zu löschen.</span>${n ? `<button class="linkbtn" type="button" data-act="vlrestore">${n === 1 ? "1 gelöschte Vorlage" : n + " gelöschte Vorlagen"} zurückholen</button>` : ""}` : ""}</div>`;
}
function vlEditorHTML() {
  if (!S.vlEdit || !S.vlOpen) return "";
  const isNew = S.vlOpen === "neu", t = isNew ? { icon: "⭐", name: "", desc: "", ph: "", layout: "spalten", cats: [["Spalte 1", "c0"], ["Spalte 2", "c2"]] } : TPL.find(x => x.id === S.vlOpen);
  if (!t) return "";
  const own = !isNew && !TPL0.some(x => x.id === t.id), changed = !isNew && !own && vlState().edit[t.id];
  const sel = (id, list, cur) => `<select class="field" id="${id}">${list.map(([k, l]) => `<option value="${k}" ${k === cur ? "selected" : ""}>${esc(l)}</option>`).join("")}</select>`;
  const chk = (k, l) => `<label class="tg"><input type="checkbox" id="vl-${k}" ${t[k] ? "checked" : ""}>${l}</label>`;
  return `<section class="vl-ed" aria-label="Vorlage bearbeiten"><h3>${isNew ? "Neue Vorlage" : "Vorlage «" + esc(t.name) + "» bearbeiten"}</h3>
    <div class="vl-grid">
      <div class="vl-wide vl-row"><label class="vl-ico"><span class="tool-l">Symbol</span><input class="field" id="vl-icon" maxlength="4" value="${esc(t.icon || "⭐")}"></label>
      <label class="vl-name"><span class="tool-l">Name</span><input class="field" id="vl-name" maxlength="40" value="${esc(t.name)}" placeholder="z. B. Lesekonferenz"></label></div>
      <label class="vl-wide"><span class="tool-l">Kurze Beschreibung</span><input class="field" id="vl-desc" maxlength="90" value="${esc(t.desc || "")}" placeholder="Wofür ist die Vorlage?"></label>
      <label><span class="tool-l">Darstellung</span>${sel("vl-layout", LAYOUTS, t.layout || "wand")}</label>
      <label><span class="tool-l">Vorlage der Leinwand</span>${sel("vl-canvas", Object.entries(CANVAS).map(([k, v]) => [k, v.name]), t.canvas || "leer")}</label>
      <label class="vl-wide"><span class="tool-l">Spalten, Äste oder Felder (eine pro Zeile)</span><textarea class="field" id="vl-cats" rows="4" maxlength="600" placeholder="leer lassen für keine">${esc((t.cats || []).map(c => c[0]).join("\\n"))}</textarea></label>
      <label class="vl-wide"><span class="tool-l">Auftrag für die Kinder</span><textarea class="field" id="vl-prompt" rows="2" maxlength="300" placeholder="freiwillig">${esc(t.prompt || "")}</textarea></label>
      <label class="vl-wide"><span class="tool-l">Beispiel-Name für neue Pinnwände</span><input class="field" id="vl-ph" maxlength="60" value="${esc(t.ph || "")}" placeholder="z. B. Lesekonferenz Woche 3"></label>
      <div class="vl-wide"><span class="tool-l">Optionen</span><div class="tools-set">${chk("kidCat", "Kinder wählen die Spalte selbst")}${chk("direct", "Ohne Freigabe anpinnen")}${chk("names", "Namen zeigen")}${chk("imgs", "Bilder erlauben")}</div></div>
    </div>
    <div class="row vl-act"><button class="btn" type="button" data-act="vlsave">Speichern</button><button class="btn ghost" type="button" data-act="vlclose">Abbrechen</button>
      ${changed ? `<button class="linkbtn" type="button" data-act="vlreset">Original wiederherstellen</button>` : ""}
      ${isNew ? "" : `<button class="del ${S.armed === "vl:" + t.id ? "arm" : ""}" type="button" data-act="vldel">${S.armed === "vl:" + t.id ? "Wirklich löschen?" : "Vorlage löschen"}</button>`}</div>
  </section>`;
}
function vlRead(old) {
  const val = id => (document.getElementById(id) || {}).value || "", on = id => !!(document.getElementById(id) || {}).checked;
  const cols = ["c0", "c2", "c3", "c4", "c1"], oldCats = (old && old.cats) || [];
  const cats = val("vl-cats").split("\\n").map(x => x.trim()).filter(Boolean).slice(0, 8).map((x, k) => [x.slice(0, 60), (oldCats[k] && oldCats[k][1]) || cols[k % cols.length]]);
  const t = { icon: val("vl-icon").trim() || "⭐", name: val("vl-name").trim().slice(0, 40), desc: val("vl-desc").trim().slice(0, 90), ph: val("vl-ph").trim().slice(0, 60),
    layout: val("vl-layout") || "wand", prompt: val("vl-prompt").trim().slice(0, 300), cats };
  const cv = val("vl-canvas"); if (t.layout === "frei" && cv && cv !== "leer") t.canvas = cv;
  for (const k of ["kidCat", "direct", "names", "imgs"]) if (on("vl-" + k)) t[k] = true;
  if (old && old.tools) t.tools = old.tools;
  if (old && old.bg) t.bg = old.bg;
  return t;
}
const LAYOUTS = [["wand", "Wand"],''')
# Galerie: Bearbeiten-Leiste, «+ Neue Vorlage», Editor
rep('    <div class="tpls" role="list">${TPL.map(', '    ${vlBarHTML()}<div class="tpls${S.vlEdit ? " vl-on" : ""}" role="list">${TPL.map(')
rep('<span class="tpl-d">${esc(x.desc)}</span></button>`).join("")}</div>',
    '<span class="tpl-d">${esc(x.desc)}</span>${S.vlEdit ? `<span class="tpl-ed" aria-hidden="true">✎</span>` : ""}</button>`).join("")}${S.vlEdit && vlState().own.length < VL_MAX ? `<button type="button" class="tpl tpl-neu" data-act="tpl" data-v="neu" aria-pressed="${S.vlOpen === "neu"}"><span class="tpl-i" aria-hidden="true">＋</span><b>Neue Vorlage</b><span class="tpl-d">Eigene Spalten, Äste oder Felder festlegen.</span></button>` : ""}</div>\n    ${vlEditorHTML()}')
rep('  else if (act === "tpl") {', '''  else if (act === "tpl" && S.vlEdit) { S.vlOpen = S.vlOpen === b.dataset.v ? null : b.dataset.v; S.armed = null; render(); document.querySelector(".vl-ed")?.scrollIntoView({ block: "nearest", behavior: "smooth" }); }
  else if (act === "vledit") { S.vlEdit = !S.vlEdit; S.vlOpen = null; render(); }
  else if (act === "vlclose") { S.vlOpen = null; render(); }
  else if (act === "vlrestore") { const v = vlState(); await saveVl({ ...v, hide: [] }, "Gelöschte Vorlagen sind wieder da."); }
  else if (act === "vlreset") { const v = vlState(), e = { ...v.edit }; delete e[S.vlOpen]; await saveVl({ ...v, edit: e }, "Original wiederhergestellt."); }
  else if (act === "vlsave") {
    const v = vlState(), id = S.vlOpen, isNew = id === "neu", base = TPL0.find(x => x.id === id), old = TPL.find(x => x.id === id);
    const t = vlRead(old); if (!t.name) { toast("Bitte geben Sie der Vorlage einen Namen."); document.getElementById("vl-name")?.focus(); return; }
    let nv;
    if (isNew) { const nid = "eigen-" + newId(""); nv = { ...v, own: [...v.own, { id: nid, ...t }] }; S.tpl = nid; }
    else if (base) nv = { ...v, edit: { ...v.edit, [id]: t } };
    else nv = { ...v, own: v.own.map(x => x.id === id ? { id, ...t } : x) };
    if (await saveVl(nv, isNew ? "Vorlage erstellt." : "Vorlage gespeichert.")) { S.vlOpen = null; render(); }
  }
  else if (act === "vldel") {
    const id = S.vlOpen, key = "vl:" + id;
    if (S.armed !== key) { S.armed = key; render(); setTimeout(() => { if (S.armed === key) { S.armed = null; render(); } }, 4000); return; }
    S.armed = null; const v = vlState(), base = TPL0.some(x => x.id === id);
    const nv = base ? { ...v, hide: [...new Set([...v.hide, id])] } : { ...v, own: v.own.filter(x => x.id !== id) };
    if (S.tpl === id) S.tpl = null; S.vlOpen = null;
    await saveVl(nv, base ? "Vorlage gelöscht. Sie können sie jederzeit zurückholen." : "Vorlage gelöscht.");
  }
  else if (act === "vlfromboard") {
    const bd = curBoard(); if (!bd) return; const v = vlState();
    if (v.own.length >= VL_MAX) { toast("Es gibt schon " + VL_MAX + " eigene Vorlagen. Bitte zuerst eine löschen."); return; }
    const t = { id: "eigen-" + newId(""), icon: "⭐", name: String(bd.title || "Eigene Vorlage").slice(0, 40), desc: "Eigene Vorlage", ph: String(bd.title || "").slice(0, 60), layout: bd.layout || "wand",
      cats: cats().slice(0, 8).map(c => [String(c.title || "").slice(0, 60), c.color || "c0"]) };
    for (const k of ["prompt", "canvas", "bg", "kidCat", "direct", "names", "imgs", "size", "font", "newPos", "sortBy"]) if (bd[k]) t[k] = bd[k];
    if (bd.tools) t.tools = { ...bd.tools };
    await saveVl({ ...v, own: [...v.own, t] }, "Als Vorlage gespeichert. Sie finden sie bei «Neue Pinnwand».");
  }
  else if (act === "tpl") {''')
# Pinnwand als Vorlage speichern (Einstellungen der Pinnwand)
rep('      <div class="row"><button class="btn ghost small" type="button" data-act="print">🖨️ Drucken</button></div>',
    '      <div class="row"><button class="btn ghost small" type="button" data-act="vlfromboard">⭐ Als Vorlage speichern</button><button class="btn ghost small" type="button" data-act="print">🖨️ Drucken</button></div>')
# Neue Pinnwände übernehmen alle Einstellungen der Vorlage
rep('  for (const k of ["prompt", "bg", "kidCat", "direct", "names", "canvas"]) if (t[k]) b[k] = t[k];',
    '  for (const k of ["prompt", "bg", "kidCat", "direct", "names", "canvas", "imgs", "size", "font", "newPos", "sortBy"]) if (t[k]) b[k] = t[k];')
# Laden (nur die Lehrperson)
rep('  db.doc("settings/main").onSnapshot(', '  if (isTeacher) db.doc("settings/vorlagen").onSnapshot(d => { S.vl = d.exists ? (d.data() || {}) : {}; applyVl(); render(); }, () => {});\n  db.doc("settings/main").onSnapshot(')
rep('/* ===== Klassenkiste-Stil ===== */', '''/* ===== Klassenkiste-Stil ===== */
.vl-bar{gap:10px}
.tpls.vl-on .tpl{border-style:dashed;border-color:var(--gold)}
.tpl{position:relative}
.tpls.vl-on .tpl-top{padding-right:18px}
.tpl-ed{position:absolute;top:8px;right:10px;color:var(--gold-d);font-size:1.1rem}
.tpl-neu{align-items:center;justify-content:center;text-align:center;border:2px dashed var(--gold)!important;background:var(--sun-soft)}
.tpl-neu .tpl-i{font-size:2rem}
.vl-ed{display:flex;flex-direction:column;gap:12px;background:var(--sun-soft);border:1.5px dashed var(--gold);border-radius:22px;padding:14px 18px}
.vl-ed h3{font-size:1.5rem}
.vl-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px 14px}
.vl-row{flex-direction:row!important;gap:12px!important}
.vl-ico{width:90px;flex:none}
.vl-name{flex:1}
.vl-grid label,.vl-grid>div{display:flex;flex-direction:column;gap:4px;min-width:0}
.vl-wide{grid-column:span 2}
.vl-grid .vl-ico input{text-align:center;font-size:1.4rem}
.vl-act{gap:10px}
@media (max-width:640px){.vl-grid{grid-template-columns:minmax(0,1fr)}.vl-wide{grid-column:auto}}''')
