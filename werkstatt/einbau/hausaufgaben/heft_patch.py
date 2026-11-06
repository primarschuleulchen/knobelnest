# Hausaufgabentafel -> Knobelnest (hausaufgaben.html)
import sys
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    assert c == n, ('Anzahl %d statt %d: ' % (c, n)) + a[:90]
    s = s.replace(a, b)

rep('<title>Hausaufgabentafel</title>', '<title>Hausaufgabenheft</title>')

# 1) Verbindung zum Knobelnest
rep('(() => {\n"use strict";\nconst $ = s => document.querySelector(s);', '''(() => {
"use strict";
const $ = s => document.querySelector(s);
// Knobelnest: Kinder, Speicher und Anhänge kommen aus dem Portal. KIDM = Ansicht eines Kindes (nur lesen)
const KN = (() => { try { return window.parent !== window && window.parent.knHeft || null; } catch { return null; } })();
if (KN) window.claude = KN.claude;
const KIDM = !!(KN && KN.mode === "kid");
if (KIDM) document.documentElement.classList.add("kidmode");''')

# 2) Speicher pro Klasse, Kinder immer aus der Klassenkiste
rep('const LS = "hausaufgabentafel1";', 'const LS = "hausaufgabentafel1" + (KN ? "-" + KN.key : "");')
rep('const EMPTY = () => ({ klasse:"Meine Klasse",', 'const EMPTY = () => ({ klasse:(KN && KN.className) || "Meine Klasse",')
rep('let S = EMPTY(), week = monday(new Date()), who = "", beamer = false;',
    'let S = EMPTY(), week = monday(new Date()), who = KIDM ? KN.kidId : "", beamer = false;')
rep('function norm(d){', '''const knSus = d => KN && !KIDM ? KN.roster.map(k => ({ id:k.id, name:k.name })) : d;
function norm(d){''')
rep('sus: Array.isArray(d.sus) ? d.sus : [],', 'sus: knSus(Array.isArray(d.sus) ? d.sus : []),')
# Kinder lesen nur: nichts speichern
rep('function save(){ lsSet(S);', 'function save(){ if (KIDM) return; lsSet(S);')

rep('function render(){\n', 'function render(){\n  if (KN && !KIDM) S.sus = knSus(S.sus);\n  if (KIDM) who = KN.kidId;\n')
rep('  if (!S.sus.some(s => s.id === who)) who = "";', '  if (KIDM) who = KN.kidId; else if (!S.sus.some(s => s.id === who)) who = "";')
# 3) Kinder-Ansicht: nichts bearbeiten
rep('function openEntry(id, date, tab = "eintrag"){', 'function openEntry(id, date, tab = "eintrag"){\n  if (KIDM) return;')
rep('$("#spread").addEventListener("dragstart", e => { const en', '$("#spread").addEventListener("dragstart", e => { if (KIDM) { e.preventDefault(); return; } const en')
rep('function openKlasse(){', 'function openKlasse(){\n  if (KIDM) return;')
rep('function openReport(){', 'function openReport(){\n  if (KIDM) return;')

# 4) Zurück-Knopf
rep('''  <div class="top" id="top">
    <button class="pill ic" id="prev"''', '''  <div class="top" id="top">
    <button class="pill" id="knBack" hidden>← Klassenkiste</button>
    <button class="pill ic" id="prev"''')
rep('$("#prev").onclick = () =>', '''if (KN) { const b = $("#knBack"); b.hidden = !!KN.embed; if (KIDM) b.textContent = "← Zurück"; b.onclick = () => KN.back(); }
$("#prev").onclick = () =>''')

# 5) Klasse und Aussehen: Kinderliste kommt aus der Klassenkiste, dazu Import der alten Hausaufgabentafel
rep('''      <div><label class="lbl" for="sIn">Schülerinnen und Schüler · eine Person pro Zeile</label><textarea class="inp" id="sIn" style="min-height:220px;font-family:var(--ui);font-size:15px">${esc(d.list)}</textarea><div class="hint">Die Reihenfolge ergibt die Nummern. Bereits kontrollierte Aufgaben bleiben erhalten, solange der Name gleich bleibt.</div></div>''',
    '''      ${KN ? `<div><span class="lbl">Schülerinnen und Schüler</span><div class="hint" style="margin-top:0">Die Kinder kommen aus der Klassenkiste (${S.sus.length}). Neue Kinder trägst du dort unter «Kinder» ein.</div></div>
      <div><span class="lbl">Aufgaben übernehmen</span><div class="row"><label class="btn" style="cursor:pointer">Datei importieren …<input type="file" id="impIn" accept=".json,application/json" hidden></label></div><div class="hint" id="impHint">Aufgaben aus der bisherigen Hausaufgabentafel. Kontrollen und Notizen werden über den Vornamen den Kindern zugeordnet.</div></div>` : `<div><label class="lbl" for="sIn">Schülerinnen und Schüler · eine Person pro Zeile</label><textarea class="inp" id="sIn" style="min-height:220px;font-family:var(--ui);font-size:15px">${esc(d.list)}</textarea><div class="hint">Die Reihenfolge ergibt die Nummern. Bereits kontrollierte Aufgaben bleiben erhalten, solange der Name gleich bleibt.</div></div>`}''')
rep('''    pb.querySelector("#sIn").oninput = ev => d.list = ev.target.value;''',
    '''    const sIn = pb.querySelector("#sIn"); if (sIn) sIn.oninput = ev => d.list = ev.target.value;
    const impIn = pb.querySelector("#impIn");
    if (impIn) impIn.onchange = async ev => { const f = ev.target.files[0]; ev.target.value = ""; if (!f) return;
      try { pb.querySelector("#impHint").textContent = importHeft(JSON.parse(await f.text())); }
      catch { pb.querySelector("#impHint").textContent = "Diese Datei konnte nicht gelesen werden."; } };''')
rep('''      const names = d.list.split("\\n")''', '''      if (KN) { S.settings = d.settings; save(); render(); closePanel(); toast("Gespeichert"); return; }
      const names = d.list.split("\\n")''')

# Import: Kinder über den Namen zuordnen, Einträge mit gleicher ID nicht doppelt übernehmen
rep('// ---------- Auswertung ----------', '''// ---------- Import aus der bisherigen Hausaufgabentafel ----------
function importHeft(raw){
  const src = norm(raw && raw.data && raw.data.entries ? raw.data : raw);
  const key = n => String(n || "").normalize("NFC").replace(/^\\s*\\d+\\s*[-–.·)]?\\s*/, "").trim().toLowerCase();
  const byName = {}; S.sus.forEach(k => { byName[key(k.name)] = k.id; });
  const map = {}, miss = [];
  (Array.isArray(raw && raw.data ? raw.data.sus : raw.sus) ? (raw.data ? raw.data.sus : raw.sus) : []).forEach(s0 => { const id = byName[key(s0.name)]; if (id) map[s0.id] = id; else miss.push(s0.name); });
  const remap = o => { const r = {}; if (o && typeof o === "object") Object.keys(o).forEach(k => { if (map[k]) r[map[k]] = o[k]; }); return r; };
  const have = new Set(S.entries.map(e => e.id)); let n = 0;
  src.entries.forEach(e0 => {
    if (have.has(e0.id)) return;
    const e = clone(e0);
    ["status", "notes", "first", "neuAuf"].forEach(k => { if (e[k]) e[k] = remap(e[k]); });
    if (Array.isArray(e.for) && e.for.length) { e.for = e.for.map(x => map[x]).filter(Boolean); if (!e.for.length) return; }
    S.entries.push(e); n++;
  });
  S.kidNotes = Object.assign(S.kidNotes || {}, remap(src.kidNotes));
  if (n && src.settings) S.settings = Object.assign(S.settings, src.settings);
  save(); render();
  return `${n} ${n === 1 ? "Eintrag" : "Einträge"} übernommen · ${Object.keys(map).length} von ${Object.keys(map).length + miss.length} Kindern zugeordnet` + (miss.length ? `. Nicht gefunden: ${miss.join(", ")}` : ".");
}

// ---------- Auswertung ----------''')

# 6) Aussehen der Kinder-Ansicht
rep('</style>\n\n<div class="app" id="app">', '''/* Knobelnest */
#knBack{font-weight:700}
.kidmode #who,.kidmode #repBtn,.kidmode #klasseBtn,.kidmode #beamerBtn,.kidmode #status{display:none!important}
.kidmode .e{cursor:default}
</style>

<div class="app" id="app">''')

# 7) Kinder haken selbst ab: in der Klassenkiste nur in der Ansicht des Kindes, gespeichert wird nur dieser Haken
rep('  if (en && who) { const e0 = S.entries.find(x => x.id === en.dataset.id); if (e0 && e0.type === "aufgabe") {',
    '  if (en && who && (!KN || KIDM)) { const e0 = S.entries.find(x => x.id === en.dataset.id); if (e0 && e0.type === "aufgabe") {')
rep('else e0.selbst[who] = true; save(); render(); return; } }',
    'else e0.selbst[who] = true; if (KIDM) KN.tick(e0.id, !!e0.selbst[who]); else save(); render(); return; } }')

# 8) Eigene Aufgaben der Kinder: nur in der Ansicht des Kindes; gespeichert wird nur dieser eine Eintrag
rep('function openKidEntry(id, date){', 'function openKidEntry(id, date){\n  if (KN && !KIDM) { if (!id) openEntry(null, date); return; }')
rep('      save(); render(); closePanel(); toast(isNew ? "Eingetragen" : "Gespeichert");',
    '      if (KIDM) KN.own(d, false); else save(); render(); closePanel(); toast(isNew ? "Eingetragen" : "Gespeichert");')
rep('S.entries = S.entries.filter(x => x.id !== d.id); save(); render(); closePanel(); toast("Gelöscht");',
    'S.entries = S.entries.filter(x => x.id !== d.id); if (KIDM) KN.own({ id:d.id }, true); else save(); render(); closePanel(); toast("Gelöscht");')

# 9) Kein Nachladen im Hintergrund, solange ein Bearbeitungsfenster offen ist (sonst gehen Haken in der Kontrolle verloren)
rep('if (!s.exists || dirty || flushing) return;', 'if (!s.exists || dirty || flushing || (layer && layer.innerHTML)) return;')

# 10) Als Baustein in der Tagesfolie (KN.embed): keine Leiste oben, nur das Heft; die Knöpfe der Lehrperson
#     öffnen sich über einen kleinen runden Knopf unten rechts
rep('.kidmode .e{cursor:default}\n</style>', """.kidmode .e{cursor:default}
.embed .top{display:none}
.embed .stage{padding-block:10px}
#embTools{display:none}
.embed #embTools{display:flex;position:absolute;right:14px;bottom:14px;z-index:70;width:42px;height:42px;border-radius:50%;border:0;background:#fff;color:#1f2421;font-size:20px;align-items:center;justify-content:center;cursor:pointer;box-shadow:0 0 0 1.5px #d6ad45,0 4px 14px rgba(63,120,168,.25)}
.embed.tools-on #embTools{background:#fbf3dc}
.embed.tools-on .top{display:flex;position:absolute;right:14px;bottom:66px;left:auto;z-index:60;max-width:calc(100% - 28px);background:#fff;border-radius:18px;padding:8px 10px;box-shadow:0 10px 28px rgba(63,120,168,.28)}
.embed.tools-on .top .sp{display:none}
</style>""")
rep('if (KN) { const b = $("#knBack"); b.hidden = !!KN.embed;', """if (KN && KN.embed) {
  const app = document.getElementById("app"); app.classList.add("embed");
  const t = document.createElement("button"); t.id = "embTools"; t.type = "button"; t.title = "Werkzeuge"; t.setAttribute("aria-label", "Werkzeuge für die Lehrperson"); t.textContent = "⚙";
  t.onclick = e => { e.stopPropagation(); app.classList.toggle("tools-on"); }; app.appendChild(t);
  document.addEventListener("click", e => { if (app.classList.contains("tools-on") && !e.target.closest("#top, #embTools, .dd, .menu")) app.classList.remove("tools-on"); });
}
if (KN) { const b = $("#knBack"); b.hidden = !!KN.embed;""")

open(dst, 'w', encoding='utf-8').write(s)
print('ok', len(s))
