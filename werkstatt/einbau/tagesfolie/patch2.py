# 8) Stundenplan: Lektionszeiten einmal eingeben, pro Stundenplan ein-/ausblenden
rep('plan:    { lab: "Stundenplan", w: 24, h: 40, d: () => ({ heading: "Heute", orient: "v", items: [] }),',
    'plan:    { lab: "Stundenplan", w: 24, h: 40, d: () => ({ heading: "Heute", orient: "v", items: [], showTimes: true, from: 0 }),')
rep('${d.items.length ? `<div class="t-plan ${d.orient === "h" ? "h" : ""}">${d.items.map(it => { const s = subjById(it.subj); return',
    '${d.items.length ? `<div class="t-plan ${d.orient === "h" ? "h" : ""}">${d.items.map((it, pi) => { const s = subjById(it.subj), tm = it.time || lessonAt(d, pi); return')
rep('<span class="pl-time" contenteditable="true" spellcheck="false" data-ptime data-ph="Zeit">${esc(it.time)}</span>',
    '${d.showTimes === false ? "" : `<span class="pl-time" contenteditable="true" spellcheck="false" data-ptime data-ph="Zeit">${esc(tm)}</span>`}')
rep('<button class="sbtn" data-nowclear>«jetzt» entfernen</button></div>`;',
    '<button class="sbtn" data-nowclear>«jetzt» entfernen</button><button class="sbtn" data-ptoggle>${d.showTimes === false ? "Zeiten zeigen" : "Zeiten ausblenden"}</button><button class="sbtn" data-ptimes>Lektionszeiten …</button></div>`;')
rep('  if (e.target.closest("[data-nowclear]")) {', '''  if (e.target.closest("[data-ptoggle]")) { d.showTimes = d.showTimes === false; save(); rerender(w); return; }
  if (e.target.closest("[data-ptimes]")) { openLessons(w); return; }
  if (e.target.closest("[data-nowclear]")) {''')
rep('  if (e.target.hasAttribute("data-ptime")) { const it = w.data.items.find(i => i.id === e.target.closest("[data-it]").dataset.it); it.time = e.target.innerText.trim(); save(); return; }',
    '  if (e.target.hasAttribute("data-ptime")) { const pi = w.data.items.findIndex(i => i.id === e.target.closest("[data-it]").dataset.it), it = w.data.items[pi], v = e.target.innerText.trim(); it.time = v === lessonAt(w.data, pi) ? "" : v; save(); return; }')
rep('const closeSheet = bg => { bg.remove(); renderBoard(); };', '''const closeSheet = bg => { bg.remove(); renderBoard(); };
// Lektionszeiten: gelten für alle Stundenpläne, der Reihe nach ab der gewählten Lektion
const showTime = t => (t || "").replace(/^0(\\d:)/, "$1");
const lessonAt = (d, i) => showTime((S.lessons || [])[(d.from || 0) + i] || "");
function openLessons(w){
  const d = w.data;
  const html = () => `<p class="hint">Einmal eintragen, wann die Lektionen beginnen. Die Zeiten gelten für alle Stundenpläne und werden den Einträgen der Reihe nach zugeordnet. Steht eine Pause im Stundenplan, gib ihr hier auch eine Zeile.</p>
    <div class="lesgrid">${Array.from({ length: 12 }, (_, i) => `<label><span>${i + 1}.</span><input type="time" data-les="${i}" value="${esc((S.lessons || [])[i] ? String(S.lessons[i]).padStart(5, "0") : "")}"></label>`).join("")}</div>
    <h3 style="margin:18px 0 6px;font-size:15px">Dieser Stundenplan beginnt bei</h3>
    <div class="chips">${(S.lessons || []).map((t, i) => t ? `<button class="chip ${(d.from || 0) === i ? "added" : ""}" data-lfrom="${i}">${i + 1}. · ${esc(showTime(t))}</button>` : "").join("")}</div>
    <label style="display:flex;align-items:center;gap:10px;margin-top:16px;font-size:15px"><input type="checkbox" data-lshow ${d.showTimes === false ? "" : "checked"} style="width:22px;height:22px"> Zeiten in diesem Stundenplan anzeigen</label>`;
  const read = () => { const v = [...document.querySelectorAll("[data-les]")].map(x => x.value); while (v.length && !v[v.length - 1]) v.pop(); return v; };
  const bg = sheet("Lektionszeiten", html(), (e, bg) => {
    const f = e.target.closest("[data-lfrom]");
    if (f) { S.lessons = read(); d.from = +f.dataset.lfrom; save(); bg.querySelector(".body").innerHTML = html(); return; }
    if (e.target.matches("[data-lshow]")) { d.showTimes = e.target.checked; save(); }
  });
  bg.addEventListener("change", e => { if (e.target.matches("[data-les]")) { S.lessons = read(); save(); const b = bg.querySelector(".body"), sc = b.scrollTop; b.innerHTML = html(); b.scrollTop = sc; } });
}''')
rep('  s.customFonts = s.customFonts || []; s.groups = s.groups || [];', '''  s.customFonts = s.customFonts || []; s.groups = s.groups || [];
  if (!s.lessons) s.lessons = ["08:20","09:10","10:00","10:20","11:10","13:30","14:20","15:10"];''')
rep('items: [["deutsch","8:20"],["mathe","9:10"],["pause","10:00"],["nmg","10:20"],["sport","11:10"]].map(([s, t]) => ({ id: uid(), subj: s, time: t,',
    'items: [["deutsch",""],["mathe",""],["pause",""],["nmg",""],["sport",""]].map(([s, t]) => ({ id: uid(), subj: s, time: t,')
rep('.t-plan.h{flex-direction:row;flex-wrap:wrap;justify-content:center}', '''.t-plan.h{flex-direction:row;flex-wrap:wrap;justify-content:center}
.lesgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:8px}
.lesgrid label{display:flex;align-items:center;gap:8px;font-size:15px}
.lesgrid span{width:2em;text-align:right;color:var(--muted);font-weight:700}
.lesgrid input{flex:1;min-width:0;border:1px solid var(--line);border-radius:10px;padding:7px 8px;font-size:16px;background:var(--paper);font-family:inherit}''')

# 9) Vorlage: Beispiel-Bildschirme für alle Lehrpersonen (aus der Klassenkiste)
rep('function defaults(){\n  return {', 'function defaults(){\n  if (KN && KN.template && KN.template.screens && KN.template.screens.length) { const t = JSON.parse(JSON.stringify(KN.template)); t.active = t.screens[0].id; t.tplGot = t.screens.map(x => x.id); return t; }\n  return {')
rep('    <button class="pill" id="libBtn">Meine Bausteine</button>', '''    <button class="pill" id="libBtn">Meine Bausteine</button>
    <button class="pill" id="tplBtn" style="display:none">Vorlagen</button>''')
rep('if (KN) { const b = $("#knBack");', '''if (KN && (KN.isAdmin || (KN.template && KN.template.screens))) { const b = $("#tplBtn"); b.style.display = ""; b.addEventListener("click", openTemplates); }
function openTemplates(){
  const tpl = KN.template && KN.template.screens ? KN.template : null;
  const WANT = ["guten morgen", "gruppen", "trainingszeit"], hit = S.screens.filter(x => WANT.includes(x.name.trim().toLowerCase()));
  const pick = new Set((hit.length ? hit : S.screens).map(x => x.id));
  const html = () => `${tpl ? `<h3 style="margin:0 0 6px;font-size:15px">Beispiel-Bildschirme einfügen</h3><p class="hint">Mit diesen Bildschirmen starten alle Lehrpersonen. Antippen fügt eine Kopie bei Ihnen hinzu.</p>
    <div class="chips">${tpl.screens.map(x => `<button class="chip" data-tadd="${esc(x.id)}">+ ${esc(x.name)}</button>`).join("")}</div>` : ""}
    ${KN.isAdmin ? `<h3 style="margin:${tpl ? 22 : 0}px 0 6px;font-size:15px">Als Vorlage für alle Lehrpersonen speichern</h3><p class="hint">Wählen Sie die Bildschirme, mit denen neue Lehrpersonen starten. Klassenliste und Abwesenheiten werden nicht mitgegeben.</p>
    <div class="chips">${S.screens.map(x => `<button class="chip ${pick.has(x.id) ? "added" : ""}" data-tpick="${esc(x.id)}">${pick.has(x.id) ? "✓ " : ""}${esc(x.name)}</button>`).join("")}</div>
    <div style="margin-top:12px"><button class="sbtn rose" data-tsave>Vorlage speichern</button></div>` : ""}`;
  const bg = sheet("Vorlagen", html(), async (e, bg) => {
    const body = bg.querySelector(".body");
    const tp = e.target.closest("[data-tpick]");
    if (tp) { const id = tp.dataset.tpick; if (pick.has(id)) pick.delete(id); else pick.add(id); body.innerHTML = html(); return; }
    const ta = e.target.closest("[data-tadd]");
    if (ta) { const src = tpl.screens.find(x => x.id === ta.dataset.tadd); if (!src) return; const c = JSON.parse(JSON.stringify(src)); c.id = uid(); c.group = ""; c.widgets.forEach(w => { w.id = uid(); (w.data.items || []).forEach(it => it.id = uid()); });
      (tpl.subjects || []).forEach(x => { if (!S.subjects.some(y => y.id === x.id)) S.subjects.push(x); });
      (tpl.bgs || []).forEach(x => { if (!S.bgs.some(y => y.src === x.src)) S.bgs.push(x); });
      S.screens.push(c); save(); renderTabs(); toast(`«${src.name}» hinzugefügt`); return; }
    if (e.target.closest("[data-tsave]")) {
      if (!pick.size) { toast("Bitte mindestens einen Bildschirm wählen"); return; }
      const t = JSON.parse(JSON.stringify(S)); t.screens = t.screens.filter(x => pick.has(x.id)); t.screens.forEach(x => x.group = ""); t.groups = [];
      t.roster = []; t.absent = { date: "", names: [] }; t.groupSets = []; t.active = t.screens[0].id;
      try { await KN.saveTemplate(t); KN.template = t; toast("Vorlage gespeichert ✓"); body.innerHTML = html(); } catch (err) { toast("Speichern ging nicht: " + (err && err.message || "")); }
    }
  });
}
if (KN) { const b = $("#knBack");''')

# 10) Vorlage-Folien kommen auch bei Lehrpersonen dazu, die die Tagesfolie schon benutzen (je Vorlage-Folie nur einmal)
rep('''  if (!s.lessons) s.lessons = ["08:20","09:10","10:00","10:20","11:10","13:30","14:20","15:10"];''', '''  if (!s.lessons) s.lessons = ["08:20","09:10","10:00","10:20","11:10","13:30","14:20","15:10"];
  s.tplGot = s.tplGot || [];
  if (KN && KN.template && KN.template.screens) {
    const tpl = KN.template; let n = 0;
    tpl.screens.forEach(src => {
      if (s.tplGot.includes(src.id)) return;
      s.tplGot.push(src.id);
      if (KN.isAdmin && s.screens.some(x => x.id === src.id)) return; // eigene Folien der Admin-Person (Vorlage von ihr)
      const c = JSON.parse(JSON.stringify(src)); c.id = uid(); c.group = ""; c.widgets.forEach(w => { w.id = uid(); (w.data.items || []).forEach(it => it.id = uid()); });
      s.screens.push(c); n++;
    });
    if (n) {
      (tpl.subjects || []).forEach(x => { if (!s.subjects.some(y => y.id === x.id)) s.subjects.push(x); });
      (tpl.bgs || []).forEach(x => { if (!s.bgs.some(y => y.src === x.src)) s.bgs.push(x); });
      s._tplAdded = n;
    }
  }''')
rep('S = migrate(lsGet() || defaults());', 'S = migrate(lsGet() || defaults()); delete S._tplAdded;')
rep('if (snap.exists && snap.data()?.screens) { S = migrate(snap.data()); if (!S.screens.some(s => s.id === S.active)) S.active = S.screens[0].id; lsSet(S); renderAll(); }',
    'if (snap.exists && snap.data()?.screens) { S = migrate(snap.data()); if (!S.screens.some(s => s.id === S.active)) S.active = S.screens[0].id; const nAdd = S._tplAdded; delete S._tplAdded; lsSet(S); renderAll(); if (nAdd) { save(); toast(nAdd === 1 ? "1 Beispiel-Folie aus der Vorlage hinzugefügt" : nAdd + " Beispiel-Folien aus der Vorlage hinzugefügt"); } }')
# Admin: beim Speichern der Vorlage eigene Folien als «erhalten» markieren
rep('try { await KN.saveTemplate(t); KN.template = t;', 't.tplGot = []; try { await KN.saveTemplate(t); KN.template = t; S.tplGot = [...new Set((S.tplGot || []).concat(t.screens.map(x => x.id)))]; save();')
# Lektionszeiten aus der Vorlage übernehmen
rep('''    <div class="chips">${tpl.screens.map(x => `<button class="chip" data-tadd="${esc(x.id)}">+ ${esc(x.name)}</button>`).join("")}</div>` : ""}''',
    '''    <div class="chips">${tpl.screens.map(x => `<button class="chip" data-tadd="${esc(x.id)}">+ ${esc(x.name)}</button>`).join("")}</div>
    ${!KN.isAdmin && tpl.lessons && tpl.lessons.length ? `<h3 style="margin:22px 0 6px;font-size:15px">Lektionszeiten</h3><p class="hint">Vorlage: ${tpl.lessons.filter(Boolean).map(showTime).join(" · ")}</p><button class="sbtn rose" data-tles>Lektionszeiten aus der Vorlage übernehmen</button>` : ""}` : ""}''')
rep('''    const ta = e.target.closest("[data-tadd]");''', '''    if (e.target.closest("[data-tles]")) { S.lessons = tpl.lessons.slice(); save(); renderBoard(); toast("Lektionszeiten übernommen ✓"); return; }
    const ta = e.target.closest("[data-tadd]");''')

# 11) Bildschirme (und Gruppen) im Dropdown frei verschieben: am Griff ziehen
rep('''  const row = x => `<button class="ddrow ${x.id === S.active ? "on" : ""}" data-go="${x.id}">${esc(x.name)}</button>`;''',
    '''  const row = x => `<div class="ddr" data-sid="${x.id}"><span class="ddgrip" aria-hidden="true" title="Ziehen zum Verschieben">⠿</span><button class="ddrow ${x.id === S.active ? "on" : ""}" data-go="${x.id}">${esc(x.name)}</button></div>`;''')
rep('''${loose.length ? `${S.groups.length ? `<div class="ddhead"><span>Ohne Gruppe</span></div>` : ""}${loose.map(row).join("")}` : ""}''',
    '''${S.groups.length ? `<div class="ddhead" data-loose><span>Ohne Gruppe</span></div>` : ""}${loose.map(row).join("")}''')
rep('''<div class="ddhead" data-gid="${g.id}"><button class="ddfold"''', '''<div class="ddhead" data-gid="${g.id}"><span class="ddgrip ddggrip" aria-hidden="true" title="Gruppe verschieben">⠿</span><button class="ddfold"''')
rep('''  dd.innerHTML = html(); APP.appendChild(dd);''', '''  dd.innerHTML = html(); APP.appendChild(dd);
  // Ziehen mit Finger, Stift oder Maus
  dd.addEventListener("pointerdown", e => {
    const grip = e.target.closest(".ddgrip"); if (!grip) return;
    e.preventDefault(); e.stopPropagation();
    const list = dd.querySelector(".ddlist"), isGroup = grip.classList.contains("ddggrip");
    const el = isGroup ? grip.closest(".ddhead") : grip.closest(".ddr");
    el.classList.add("dragging"); if (isGroup) list.classList.add("gdrag");
    let moved = false, scrollT = null;
    const move = ev => {
      const r = list.getBoundingClientRect();
      clearInterval(scrollT); scrollT = null;
      if (ev.clientY < r.top + 30) scrollT = setInterval(() => list.scrollTop -= 8, 16);
      else if (ev.clientY > r.bottom - 30) scrollT = setInterval(() => list.scrollTop += 8, 16);
      el.style.pointerEvents = "none";
      const over = document.elementFromPoint(r.left + 40, ev.clientY); el.style.pointerEvents = "";
      if (!over || !list.contains(over)) return;
      if (isGroup) {
        const hd = over.closest(".ddhead[data-gid]"); if (!hd || hd === el) return;
        const b = hd.getBoundingClientRect(), after = ev.clientY > b.top + b.height / 2;
        list.insertBefore(el, after ? hd.nextSibling : hd); moved = true; return;
      }
      const t = over.closest(".ddr, .ddhead, .ddempty"); if (!t || t === el) return;
      const b = t.getBoundingClientRect(), after = ev.clientY > b.top + b.height / 2;
      if (t.classList.contains("ddhead")) list.insertBefore(el, t.nextSibling);
      else if (t.classList.contains("ddempty")) list.insertBefore(el, t);
      else list.insertBefore(el, after ? t.nextSibling : t);
      moved = true;
    };
    const up = () => {
      window.removeEventListener("pointermove", move); window.removeEventListener("pointerup", up); window.removeEventListener("pointercancel", up);
      clearInterval(scrollT); el.classList.remove("dragging"); list.classList.remove("gdrag");
      if (!moved) return;
      if (isGroup) {
        const ids = [...list.querySelectorAll(".ddhead[data-gid]")].map(x => x.dataset.gid);
        S.groups.sort((a, b) => ids.indexOf(a.id) - ids.indexOf(b.id));
      } else {
        let grp = ""; const order = [];
        [...list.children].forEach(c => {
          if (c.classList.contains("ddhead")) { grp = c.dataset.gid || ""; return; }
          if (c.classList.contains("ddr")) { const sc = S.screens.find(x => x.id === c.dataset.sid); if (sc) { sc.group = grp; order.push(sc); } }
        });
        S.screens = order.concat(S.screens.filter(x => !order.includes(x))); // Bildschirme in zugeklappten Gruppen bleiben
      }
      save(); const st = list.scrollTop; dd.innerHTML = html(); dd.querySelector(".ddlist").scrollTop = st; renderTabs();
    };
    window.addEventListener("pointermove", move); window.addEventListener("pointerup", up); window.addEventListener("pointercancel", up);
  });''')
rep('.ddrow:hover{background:var(--leaf-soft)}', '''.ddrow:hover{background:var(--leaf-soft)}
.ddr{display:flex;align-items:center}
.ddr .ddrow{flex:1;min-width:0;padding-left:8px}
.ddgrip{flex:none;width:26px;height:34px;display:flex;align-items:center;justify-content:center;color:#b3bab4;cursor:grab;touch-action:none;user-select:none;-webkit-user-select:none;font-size:16px}
.ddhead .ddgrip{height:26px;width:20px}
.ddr.dragging,.ddhead.dragging{background:#fff;box-shadow:0 6px 20px rgba(0,0,0,.18);border-radius:10px;position:relative;z-index:2}
.ddlist.gdrag .ddr,.ddlist.gdrag .ddempty{display:none}''')

# 12) Datenschutz: keine Kindernamen in Vorlagen; fremde Namen in Gruppen/Zufallsname durch die eigene Klasse ersetzen
rep('''  s.tplGot = s.tplGot || [];''', '''  s.tplGot = s.tplGot || [];
  knClean(s.screens);''')
rep('''t.roster = []; t.absent = { date: "", names: [] }; t.groupSets = []; t.active = t.screens[0].id;''',
    '''t.roster = []; t.absent = { date: "", names: [] }; t.groupSets = []; t.active = t.screens[0].id;
      t.screens.forEach(x => x.widgets.forEach(w => { if (w.type === "groups") { w.data.groups = []; w.data.source = "random"; } if (w.type === "random") { w.data.pick = ""; w.data.names = ""; w.data.editing = false; } }));''')
rep('Leer – über ⋯ einen Bildschirm hierher verschieben', 'Leer – einen Bildschirm am ⠿ hierher ziehen')

rep('function migrate(s){', 'function knClean(screens){\n  if (!(KN && KN.roster.length)) return;\n    const own = new Set(KN.roster);\n    const shuffle = a => { a = a.slice(); for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; };\n    screens.forEach(sc => sc.widgets.forEach(w => {\n      const d = w.data || {};\n      if (w.type === "random") {\n        if (d.pick && !own.has(d.pick)) d.pick = "";\n        if (d.names && d.names.split("\\n").map(x => x.trim()).filter(Boolean).some(n => !own.has(n))) { d.names = ""; d.editing = false; }\n      }\n      if (w.type === "groups" && Array.isArray(d.groups) && d.groups.some(g => g.some(n => !own.has(n)))) {\n        d.source = "random";\n        const names = shuffle(KN.roster), size = d.size || 2;\n        const k = names.length ? Math.max(1, size === 2 ? Math.floor(names.length / 2) : Math.round(names.length / size)) : 0;\n        const out = Array.from({ length: k }, () => []); names.forEach((n, i) => out[i % k].push(n)); d.groups = out;\n      }\n    }));\n}\nfunction migrate(s){')
rep('S.screens.push(c); save(); renderTabs(); toast(`«${src.name}» hinzugefügt`); return; }', 'knClean([c]); S.screens.push(c); save(); renderTabs(); toast(`«${src.name}» hinzugefügt`); return; }')

# 13) Rückgängig / Wiederholen (Knopf oben und ⌘Z / Ctrl+Z)
rep('if (KN) window.claude = KN.claude;', '''if (KN) window.claude = KN.claude;
// Rückgängig: vor jeder gespeicherten Änderung wird der vorherige Stand gemerkt (der gerade gezeigte Bildschirm zählt nicht als Änderung)
const UNDO = { back:[], fwd:[], last:null, t:0, size:0, inputAt:0 };
document.addEventListener("input", () => { UNDO.inputAt = Date.now(); }, true);''')
rep('function save(){ lsSet(S); dirty = true;', '''function undoSnap(){ return JSON.stringify(Object.assign({}, S, { active:"" })); }
function undoBase(){ try { UNDO.last = undoSnap(); UNDO.back = []; UNDO.fwd = []; UNDO.size = 0; updUndo(); } catch {} }
function undoTrack(){
  try {
    const cur = undoSnap(); if (UNDO.last === null) { UNDO.last = cur; return; }
    if (cur === UNDO.last) return;
    const now = Date.now(), typing = now - (UNDO.inputAt || 0) < 400; // Tippen in Texten zählt als ein Schritt
    if (!(typing && now - UNDO.t < 1500 && UNDO.back.length)) { UNDO.back.push(UNDO.last); UNDO.size += UNDO.last.length; }
    while (UNDO.back.length > 40 || (UNDO.size > 30e6 && UNDO.back.length > 1)) UNDO.size -= UNDO.back.shift().length;
    UNDO.fwd = []; UNDO.last = cur; UNDO.t = now; updUndo();
  } catch {}
}
function updUndo(){ const u = document.getElementById("undoBtn"), r = document.getElementById("redoBtn"); if (u) u.disabled = !UNDO.back.length; if (r) r.disabled = !UNDO.fwd.length; }
function undoRestore(js, msg){
  const act = S.active, n = JSON.parse(js);
  n.active = n.screens.some(s => s.id === act) ? act : n.screens[0].id;
  S = n; UNDO.last = js; selId = null;
  lsSet(S); dirty = true; setStatus("Speichert …"); clearTimeout(save.t); save.t = setTimeout(flush, 700);
  closeMenus(); document.querySelectorAll(".sheet-bg").forEach(x => x.remove());
  renderAll(); updUndo(); toast(msg);
}
function doUndo(){ if (!UNDO.back.length) return; const prev = UNDO.back.pop(); UNDO.size -= prev.length; UNDO.fwd.push(UNDO.last); undoRestore(prev, "Rückgängig gemacht"); }
function doRedo(){ if (!UNDO.fwd.length) return; const nx = UNDO.fwd.pop(); UNDO.back.push(UNDO.last); UNDO.size += UNDO.last.length; undoRestore(nx, "Wiederhergestellt"); }
function save(){ undoTrack(); lsSet(S); dirty = true;''')
rep('S = migrate(lsGet() || defaults()); delete S._tplAdded;', 'S = migrate(lsGet() || defaults()); delete S._tplAdded; undoBase();')
rep('const nAdd = S._tplAdded; delete S._tplAdded; lsSet(S); renderAll();', 'const nAdd = S._tplAdded; delete S._tplAdded; lsSet(S); undoBase(); renderAll();')
rep('    <span class="status" id="status">Wird geladen …</span>', '''    <button class="pill undo" id="undoBtn" title="Rückgängig (⌘Z)" aria-label="Rückgängig" disabled>↶ Rückgängig</button>
    <button class="pill undo" id="redoBtn" title="Wiederholen (⇧⌘Z)" aria-label="Wiederholen" disabled>↷</button>
    <span class="status" id="status">Wird geladen …</span>''')
rep('$("#fsBtn").addEventListener("click", async () => {', '''$("#undoBtn").addEventListener("click", doUndo);
$("#redoBtn").addEventListener("click", doRedo);
document.addEventListener("keydown", e => {
  if (!(e.metaKey || e.ctrlKey) || e.key.toLowerCase() !== "z") return;
  const ae = document.activeElement; if (ae && ae.matches && ae.matches('[contenteditable="true"],input,textarea')) return; // im Textfeld: normales Rückgängig
  e.preventDefault(); if (e.shiftKey) doRedo(); else doUndo();
});
updUndo();
$("#fsBtn").addEventListener("click", async () => {''')
rep('.kn-back{font-weight:700}', '.kn-back{font-weight:700}\n.pill.undo:disabled{opacity:.4;cursor:default}')

# 14) Ablauf/Checkliste: Farben, Untertitel, Beschreibungen, mehr Platz · Material durchstreichen + Anmerkung · Text: Grösse und Farbe
LIST_OLD = '''      ${d.items.length ? `<ul class="t-list">${d.items.map((it, i) => `<li class="${it.done ? "done" : ""}" data-it="${it.id}"><button class="blob" data-tick style="background:${T.blobs[i % 6]};border-radius:${SHAPES[i % 4]}" aria-label="Abhaken"></button><span class="txt" contenteditable="true" spellcheck="false" data-itxt>${esc(it.text)}</span><button class="mv" data-mvit aria-label="Verschieben" title="Zum Verschieben ziehen">⠿</button><button class="ix" data-rm aria-label="Entfernen">✕</button></li>`).join("")}</ul>` : `<div class="emptyhint">Noch leer – füge Bausteine hinzu</div>`}
      <div class="lfoot"><button class="sbtn rose" data-lib>+ Bausteine</button><input type="text" id="add-${w.id}" placeholder="Eigener Text + Enter" aria-label="Eigenen Punkt hinzufügen"></div>`;'''
LIST_NEW = '''      ${d.items.length ? `<ul class="t-list" style="${d.tc ? `--tc:${d.tc}` : ""}">${listRows(w, T)}</ul>` : `<div class="emptyhint">Noch leer – füge Bausteine hinzu</div>`}
      <div class="lfoot"><button class="sbtn rose" data-lib>+ Bausteine</button><input type="text" id="add-${w.id}" placeholder="Eigener Text + Enter" aria-label="Eigenen Punkt hinzufügen"><button class="sbtn" data-addk="sub">+ Untertitel</button><button class="sbtn" data-addk="desc">+ Beschreibung</button></div>`;'''
rep(LIST_OLD, LIST_NEW)
CHECK_OLD = '''      ${d.items.length ? `<ul class="t-list check">${d.items.map(it => `<li class="${it.done ? "done" : ""}" data-it="${it.id}"><button class="blob ring" data-tick aria-label="Abhaken"></button><span class="txt" contenteditable="true" spellcheck="false" data-itxt>${esc(it.text)}</span><button class="mv" data-mvit aria-label="Verschieben" title="Zum Verschieben ziehen">⠿</button><button class="ix" data-rm aria-label="Entfernen">✕</button></li>`).join("")}</ul>` : `<div class="emptyhint">Noch leer – schreib unten etwas hinein</div>`}
      <div class="lfoot"><input type="text" id="add-${w.id}" placeholder="Neuer Punkt + Enter" aria-label="Punkt hinzufügen"></div>`;'''
CHECK_NEW = '''      ${d.items.length ? `<ul class="t-list check" style="${d.tc ? `--tc:${d.tc}` : ""}">${listRows(w, T)}</ul>` : `<div class="emptyhint">Noch leer – schreib unten etwas hinein</div>`}
      <div class="lfoot"><input type="text" id="add-${w.id}" placeholder="Neuer Punkt + Enter" aria-label="Punkt hinzufügen"><button class="sbtn" data-addk="sub">+ Untertitel</button><button class="sbtn" data-addk="desc">+ Beschreibung</button></div>`;'''
rep(CHECK_OLD, CHECK_NEW)
rep('function widgetInner(w){', '''// Zeilen für Ablauf und Checkliste: normale Punkte, Untertitel und Beschreibungen
function listRows(w, T){
  const d = w.data, chk = w.type === "check"; let n = 0;
  const tools = `<span class="itools"><button class="mv" data-mvit aria-label="Verschieben" title="Zum Verschieben ziehen">⠿</button><button class="ix" data-rm aria-label="Entfernen">✕</button></span>`;
  return d.items.map(it => {
    const txt = `<span class="txt" contenteditable="true" spellcheck="false" data-itxt>${esc(it.text)}</span>`;
    if (it.kind === "sub" || it.kind === "desc") return `<li class="${it.kind}" data-it="${it.id}">${txt}${tools}</li>`;
    const i = n++, c = it.cc || d.cc;
    const blob = chk ? `<button class="blob ring" data-tick aria-label="Abhaken"${c ? ` style="background:${c};border-color:${c}"` : ""}></button>`
      : `<button class="blob" data-tick style="background:${c || T.blobs[i % 6]};border-radius:${SHAPES[i % 4]}" aria-label="Abhaken"></button>`;
    return `<li class="${it.done ? "done" : ""}" data-it="${it.id}">${blob}${txt}${tools}</li>`;
  }).join("");
}
const TEXT_COLS = ["#1f2421","#c0463c","#d0731f","#b8920f","#2e8b57","#2f6fb3","#7a4fb0","#6c766f"];
const DOT_COLS = ["#f4d35e","#9fd18b","#8fc1e8","#f4a7b9","#f6b77c","#c7b2e8","#7ccfc3","#d6dbd7"];
function openStyle(w){
  const d = w.data, hasDots = w.type === "list" || w.type === "check";
  const sw = (attr, val, cur, label) => `<button class="swatch ${cur === val ? "on" : ""}" ${attr}="${val}" style="background:${val || "#fff"}" aria-label="${label}">${val ? "" : "–"}</button>`;
  const html = () => `<h3 class="sh3">Schriftfarbe</h3><div class="swrow">${sw("data-tc", "", d.tc || "", "Standard")}${TEXT_COLS.map(c => sw("data-tc", c, d.tc, "Schriftfarbe")).join("")}</div>
    ${hasDots ? `<h3 class="sh3">Farbe der Kreise (alle)</h3><div class="swrow">${sw("data-cc", "", d.cc || "", w.type === "list" ? "Bunt" : "Standard")}${DOT_COLS.map(c => sw("data-cc", c, d.cc, "Kreisfarbe")).join("")}</div>
    <h3 class="sh3">Einzelne Punkte färben</h3>${d.items.filter(it => !it.kind).map(it => `<div class="switem"><span>${esc(it.text || "…")}</span><div class="swrow sm">${sw("data-icc", "", it.cc || "", "wie alle")}${DOT_COLS.map(c => `<button class="swatch ${it.cc === c ? "on" : ""}" data-icc="${c}" data-iid="${it.id}" style="background:${c}" aria-label="Kreisfarbe"></button>`).join("")}</div></div>`).join("").replace(/data-icc="" /g, (m) => m)}` : ""}`;
  const fix = body => body.querySelectorAll('.switem').forEach((row, k) => { const it = d.items.filter(x => !x.kind)[k]; row.querySelector('[data-icc=""]')?.setAttribute("data-iid", it.id); });
  const bg = sheet("Farben", html(), (e, bg) => {
    const body = bg.querySelector(".body"), b = e.target.closest("[data-tc],[data-cc],[data-icc]"); if (!b) return;
    if (b.hasAttribute("data-tc")) d.tc = b.dataset.tc || undefined;
    else if (b.hasAttribute("data-cc")) d.cc = b.dataset.cc || undefined;
    else { const it = d.items.find(x => x.id === b.dataset.iid); if (it) it.cc = b.dataset.icc || undefined; }
    save(); rerender(w); const st = body.scrollTop; body.innerHTML = html(); fix(body); body.scrollTop = st;
  });
  fix(bg.querySelector(".body"));
}
function widgetInner(w){''')
# Material: durchstreichen und Anmerkung
rep('''${d.keys.filter(k => MAT[k]).map(k => `<div class="mat" title="${MAT[k][0]}">${MAT[k][1]}<span>${MAT[k][0]}</span></div>`).join("")}</div>` : `<div class="emptyhint">Noch kein Material gewählt</div>`}''',
    '''${d.keys.filter(k => MAT[k]).map(k => `<button class="mat${(d.crossed || []).includes(k) ? " crossed" : ""}" data-mk="${k}" title="${MAT[k][0]} – antippen zum Durchstreichen">${MAT[k][1]}<span>${MAT[k][0]}</span></button>`).join("")}</div>` : `<div class="emptyhint">Noch kein Material gewählt</div>`}
      <div class="mnote${d.note ? "" : " empty"}" contenteditable="true" spellcheck="false" data-f="note" data-ph="Anmerkung (optional)" style="${d.tc ? `color:${d.tc}` : ""}">${esc(d.note || "")}</div>''')
rep('''  if (e.target.closest("[data-mat]")) { openMaterial(w); return; }''', '''  if (e.target.closest("[data-mat]")) { openMaterial(w); return; }
  const mk = w.type === "material" && e.target.closest(".mat[data-mk]");
  if (mk) { const k = mk.dataset.mk, c = d.crossed || []; d.crossed = c.includes(k) ? c.filter(x => x !== k) : [...c, k]; mk.classList.toggle("crossed"); save(); return; }
  if (e.target.closest("[data-style]")) { openStyle(w); return; }
  const ak = e.target.closest("[data-addk]");
  if (ak) { const inp = document.getElementById("add-" + w.id), v = (inp?.value || "").trim(), kind = ak.dataset.addk;
    const it = { id: uid(), text: v || (kind === "sub" ? "Untertitel" : "Beschreibung"), done: false, kind }; d.items.push(it); save(); rerender(w);
    const el = document.querySelector(`[data-w="${w.id}"] [data-it="${it.id}"] .txt`); if (el) { el.focus(); if (!v) { const r = document.createRange(); r.selectNodeContents(el); const s = getSelection(); s.removeAllRanges(); s.addRange(r); } }
    return; }''')
rep('''<p class="hint">Antippen wählt das Material aus oder ab.</p>''', '''<p class="hint">Antippen wählt das Material aus oder ab. Im Feld selbst streichst du ein Material durch, indem du es antippst (z. B. Radiergummi beim Korrigieren).</p>''')
# Checkliste: erledigte nur nach oben schieben, wenn keine Untertitel/Beschreibungen da sind
rep('''    if (w.type === "check") { // erledigte nach oben, offene rutschen nach unten''', '''    if (w.type === "check" && !d.items.some(i => i.kind)) { // erledigte nach oben, offene rutschen nach unten''')
# Text-Widget: feste Schriftgrösse mit A−/A+, Farbe
rep('''${auto ? `<button data-fsz="-1" aria-label="Schrift kleiner">A−</button><button data-fsz="1" aria-label="Schrift grösser">A+</button>` : ""}''',
    '''${STYLED.has(w.type) ? `<button data-style aria-label="Farben">🎨</button>` : ""}${auto || w.type === "note" ? `<button data-fsz="-1" aria-label="Schrift kleiner">A−</button><button data-fsz="1" aria-label="Schrift grösser">A+</button>` : ""}''')
rep('''style="left:${w.x}%;top:${w.y}%;width:${w.w}%;${auto ?''', '''style="left:${w.x}%;top:${w.y}%;width:${w.w}%;${w.type === "note" ? `--fs:${w.fs || FS_DEFAULT.note};` : ""}${auto ?''')
rep('const FS_DEFAULT = { list: 3.6, check: 3.6, plan: 2.5, material: 3.4, groups: 2.8 };', 'const FS_DEFAULT = { list: 3.6, check: 3.6, plan: 2.5, material: 3.4, groups: 2.8, note: 3.2 };\nconst STYLED = new Set(["list", "check", "note", "material"]);')
rep('''<div class="t-note" contenteditable="true" spellcheck="false" data-f="body"''', '''<div class="t-note" style="${d.tc ? `color:${d.tc}` : ""}" contenteditable="true" spellcheck="false" data-f="body"''')
rep('''(e.target.dataset.f && e.target.dataset.f !== "body")''', '''(e.target.dataset.f && e.target.dataset.f !== "body" && e.target.dataset.f !== "note")''')
rep('.t-list .txt{flex:1;min-width:0;overflow-wrap:break-word;hyphens:auto}', '''.t-list .txt{flex:1;min-width:0;overflow-wrap:break-word;hyphens:auto;color:var(--tc,inherit)}
/* Werkzeuge schweben rechts über dem Text, damit der Text die ganze Breite nutzt */
.t-list li{position:relative}
.t-list .itools{position:absolute;right:-.2em;top:50%;transform:translateY(-50%);display:flex;align-items:center;gap:2px;background:rgba(255,255,255,.95);border-radius:10px;box-shadow:0 2px 8px rgba(0,0,0,.12);opacity:0;pointer-events:none;transition:opacity .15s;z-index:2}
.t-list li:hover>.itools,.t-list li:focus-within>.itools,.t-list li.dragging>.itools{opacity:1;pointer-events:auto}
.t-list .itools .mv,.t-list .itools .ix{opacity:1}
.t-list li.sub .txt{font-weight:700;font-size:.8em;letter-spacing:.01em;padding-top:.25em}
.t-list li.sub{margin-top:.15em}
.t-list li.desc{padding-left:calc(1.25em + var(--fs) * .7vh)}
.t-list li.desc .txt{font-size:.62em;line-height:1.25;color:var(--tc,var(--muted));opacity:.9}
.t-list.check li.desc{padding-left:calc(1.08em + var(--fs) * .7vh)}
.mat{all:unset;box-sizing:border-box;cursor:pointer;position:relative}
.mat.crossed svg{opacity:.55}
.mat.crossed::after{content:"";position:absolute;left:50%;top:0;width:min(100%,120px);aspect-ratio:1;transform:translateX(-50%);pointer-events:none;
  background:linear-gradient(to top right,transparent calc(50% - 3px),#d23a2f calc(50% - 3px),#d23a2f calc(50% + 3px),transparent calc(50% + 3px)),linear-gradient(to top left,transparent calc(50% - 3px),#d23a2f calc(50% - 3px),#d23a2f calc(50% + 3px),transparent calc(50% + 3px))}
.mat.crossed span{text-decoration:line-through;text-decoration-color:#d23a2f;text-decoration-thickness:2px}
.mnote{font-family:var(--hand);font-size:calc(var(--fs) * .62vh);line-height:1.2;padding:2px 5cqw 14px;outline:none;white-space:pre-wrap;text-align:center}
.mnote:empty::before{content:attr(data-ph);color:#b5bcb6}
.mnote.empty:not(:focus){display:none}
.w.sel .mnote.empty{display:block}
.swrow{display:flex;flex-wrap:wrap;gap:8px;margin:4px 0 6px}
.swrow.sm .swatch{width:26px;height:26px}
.swatch{width:34px;height:34px;border-radius:50%;border:2px solid rgba(0,0,0,.12);cursor:pointer;padding:0;font-size:14px;color:#6c766f}
.swatch.on{box-shadow:0 0 0 3px #fff,0 0 0 5px #1f2421}
.sh3{margin:14px 0 2px;font-size:15px}
.switem{display:flex;align-items:center;justify-content:space-between;gap:10px;flex-wrap:wrap;padding:4px 0;border-bottom:1px solid var(--line)}
.switem>span{font-size:14px;max-width:50%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}''')
rep('.t-note{flex:1;overflow:auto;padding:1cqh 7cqw 4cqh;font-family:var(--hand);font-size:clamp(16px,min(9cqh,7cqw),52px);line-height:1.2;white-space:pre-wrap}',
    '.t-note{flex:1;overflow:auto;padding:1cqh 7cqw 4cqh;font-family:var(--hand);font-size:calc(var(--fs) * 1vh);line-height:1.2;white-space:pre-wrap}')

# 15) Hintergrund-Vorlagen (Mathe, Deutsch, Klassenrat) und Musik pro Bildschirm
rep('function drawBg(){', r'''// ---------- Hintergrund-Vorlagen in Pastell ----------
const rngOf = s => () => (s = (s * 16807) % 2147483647) / 2147483647;
function edgeSpots(W, H, n, seed, cx = .2, cy = .17){
  const r = rngOf(seed), out = []; let g = 0;
  while (out.length < n && g++ < n * 60) {
    const x = r() * W, y = r() * H;
    if (x > W * cx && x < W * (1 - cx) && y > H * cy && y < H * (1 - cy)) continue;
    if (out.some(p => Math.hypot(p[0] - x, p[1] - y) < Math.min(W, H) * .085)) continue;
    out.push([x, y, r()]);
  }
  return out;
}
const softBlobs = (W, H, list) => `<defs><filter id="wc" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="${Math.round(Math.min(W, H) / 22)}"/></filter></defs><g filter="url(#wc)">${list.map(([x, y, rx, ry, c, o]) => `<ellipse cx="${x * W}" cy="${y * H}" rx="${rx * W}" ry="${ry * H}" fill="${c}" opacity="${o}"/>`).join("")}</g>`;
const HAND = `font-family="Patrick Hand,Comic Sans MS,cursive"`;
const BG_TPL = {
  mathe: { name: "Mathe", base: "radial-gradient(ellipse at 45% 35%,#fdfdfb,#f1f5fa)", fill: "#f4f7fb",
    theme: { title: "#4f7fb5", blobs: ["#8fb8e2", "#f2cd6b", "#a5cf98", "#eba7a0", "#c4a9e2", "#f3b37c"], cal: ["#4f7fb5", "#e3edf8"] },
    draw(W, H){
      const C = ["#8fb8e2", "#eba7a0", "#a5cf98", "#efc75e", "#c4a9e2", "#f3b37c", "#7fcabd"];
      const T = ["7", "3", "½", "¾", "⅓", "2 · 3", "7 × 8", "+", "−", "=", "÷", "9", "1×1", "4", "0", "5 + 5", "8", "%", "6 : 2", "¼", "1", "100"];
      const sp = edgeSpots(W, H, 30, 7), s = Math.min(W, H);
      const shapes = `<g fill="none" stroke-width="${s * .006}" opacity=".55" stroke-linejoin="round">
        <rect x="${W * .9}" y="${H * .42}" width="${s * .07}" height="${s * .07}" rx="${s * .008}" stroke="#8fb8e2" transform="rotate(12 ${W * .93} ${H * .46})"/>
        <path d="M${W * .05} ${H * .44}l${s * .05} ${-s * .085}l${s * .05} ${s * .085}z" stroke="#a5cf98"/>
        <circle cx="${W * .5}" cy="${H * .07}" r="${s * .028}" stroke="#eba7a0"/></g>`;
      const grid = `<g opacity=".35" stroke="#8fb8e2" stroke-width="1">${Array.from({ length: 9 }, (_, i) => `<path d="M${W - s * .3 + i * s * .03} ${H} v${-s * .24}"/><path d="M${W - s * .3} ${H - i * s * .03} h${s * .3}"/>`).join("")}</g>`;
      return softBlobs(W, H, [[0, 1, .26, .32, "#bcd6ef", .55], [1, 0, .24, .3, "#cfe6c4", .5], [1, 1, .2, .26, "#f6dcb4", .45], [0, 0, .18, .2, "#efd2e4", .45]]) + grid + shapes +
        sp.map(([x, y, r], i) => { const t = T[i % T.length], f = s * (.045 + r * .05) * (t.length > 3 ? .7 : 1);
          return `<text x="${x.toFixed(0)}" y="${y.toFixed(0)}" ${HAND} font-size="${f.toFixed(0)}" fill="${C[i % C.length]}" opacity=".78" text-anchor="middle" transform="rotate(${(r * 40 - 20).toFixed(0)} ${x.toFixed(0)} ${y.toFixed(0)})">${t}</text>`; }).join("");
    } },
  deutsch: { name: "Deutsch", base: "radial-gradient(ellipse at 45% 35%,#fffdf9,#f8f1ea)", fill: "#faf5ef",
    theme: { title: "#c0675a", blobs: ["#eba7a0", "#a5cf98", "#efc75e", "#8fb8e2", "#d7b3e0", "#f3b37c"], cal: ["#c0675a", "#f8e6e1"] },
    draw(W, H){
      const s = Math.min(W, H), C = ["#eba7a0", "#8fb8e2", "#a5cf98", "#efc75e", "#c4a9e2", "#f3b37c"];
      const L = "AbCdEfGhIjKlMnOpQrStUvWz".split(""), sp = edgeSpots(W, H, 24, 13, .22, .2);
      const book = (x, y, w, h, c, rot = 0) => `<g transform="rotate(${rot} ${x} ${y})"><rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${s * .006}" fill="${c}"/><rect x="${x + w * .08}" y="${y + h * .2}" width="${w * .84}" height="${h * .12}" rx="2" fill="#fff" opacity=".55"/><rect x="${x + w * .08}" y="${y + h * .68}" width="${w * .84}" height="${h * .08}" rx="2" fill="#fff" opacity=".4"/></g>`;
      const bw = s * .09, by = H - s * .02;
      const stack = [["#eba7a0", .32, 0], ["#8fb8e2", .26, .01], ["#a5cf98", .3, -.012], ["#efc75e", .24, .006]].map(([c, w, dx], i) =>
        `<rect x="${s * (.04 + dx)}" y="${by - (i + 1) * s * .045}" width="${s * w}" height="${s * .042}" rx="${s * .008}" fill="${c}"/><rect x="${s * (.04 + dx) + s * w * .82}" y="${by - (i + 1) * s * .045 + s * .008}" width="${s * .02}" height="${s * .026}" rx="2" fill="#fff" opacity=".6"/>`).join("");
      const row = ["#c4a9e2", "#8fb8e2", "#eba7a0", "#efc75e", "#a5cf98"].map((c, i) => book(W - s * .06 - (5 - i) * bw * .62, H - s * .02 - s * (.2 + (i % 3) * .025), bw * .55, s * (.2 + (i % 3) * .025), c, i === 4 ? 8 : 0)).join("");
      const open = (cx, cy, w) => `<g transform="rotate(-8 ${cx} ${cy})" opacity=".9"><path d="M${cx} ${cy}c${-w * .25} ${-w * .12} ${-w * .45} ${-w * .1} ${-w * .55} ${-w * .02}v${w * .42}c${w * .1} ${-w * .08} ${w * .3} ${-w * .1} ${w * .55} ${w * .02}z" fill="#fff" stroke="#e5c9b8" stroke-width="3"/><path d="M${cx} ${cy}c${w * .25} ${-w * .12} ${w * .45} ${-w * .1} ${w * .55} ${-w * .02}v${w * .42}c${-w * .1} ${-w * .08} ${-w * .3} ${-w * .1} ${-w * .55} ${w * .02}z" fill="#fff" stroke="#e5c9b8" stroke-width="3"/>${[0, 1, 2, 3].map(k => `<path d="M${cx - w * .45} ${cy + w * (.06 + k * .07)}q${w * .2} ${-w * .06} ${w * .38} 0M${cx + w * .07} ${cy + w * (.06 + k * .07)}q${w * .2} ${-w * .06} ${w * .38} 0" stroke="#d9c6bb" stroke-width="2" fill="none"/>`).join("")}</g>`;
      const pencil = `<g transform="rotate(-35 ${s * .12} ${s * .14})"><rect x="${s * .02}" y="${s * .12}" width="${s * .2}" height="${s * .032}" rx="4" fill="#efc75e"/><path d="M${s * .22} ${s * .12}l${s * .045} ${s * .016}l${-s * .045} ${s * .016}z" fill="#f2d8b8"/><path d="M${s * .255} ${s * .132}l${s * .01} ${s * .004}l${-s * .01} ${s * .004}z" fill="#555"/><rect x="${s * .005}" y="${s * .12}" width="${s * .022}" height="${s * .032}" rx="4" fill="#eba7a0"/></g>`;
      return softBlobs(W, H, [[0, 1, .26, .3, "#f3cfc6", .55], [1, 0, .22, .28, "#d6e8c9", .5], [1, 1, .22, .25, "#d6e2f3", .45], [0, 0, .2, .22, "#f6e3b5", .45]]) +
        stack + row + open(W - s * .2, s * .14, s * .26) + pencil +
        sp.map(([x, y, r], i) => `<text x="${x.toFixed(0)}" y="${y.toFixed(0)}" ${HAND} font-size="${(s * (.05 + r * .05)).toFixed(0)}" fill="${C[i % C.length]}" opacity=".75" text-anchor="middle" transform="rotate(${(r * 36 - 18).toFixed(0)} ${x.toFixed(0)} ${y.toFixed(0)})">${L[i % L.length]}</text>`).join("");
    } },
  klassenrat: { name: "Klassenrat", base: "radial-gradient(ellipse at 50% 40%,#fffefb,#f5f1f7)", fill: "#f8f5f8",
    theme: { title: "#8a6fb8", blobs: ["#c4a9e2", "#efc75e", "#8fb8e2", "#eba7a0", "#a5cf98", "#f3b37c"], cal: ["#8a6fb8", "#efe8f8"] },
    draw(W, H){
      const s = Math.min(W, H), C = ["#eba7a0", "#efc75e", "#a5cf98", "#8fb8e2", "#c4a9e2", "#f3b37c"];
      // Wimpelkette oben
      const sag = s * .09, y0 = s * .03, n = Math.max(9, Math.round(W / (s * .085)));
      const yAt = t => y0 + 4 * sag * t * (1 - t);
      let flags = "";
      for (let i = 0; i < n; i++) { const t0 = (i + .15) / n, t1 = (i + .85) / n, tm = (t0 + t1) / 2, x0 = t0 * W, x1 = t1 * W, xm = tm * W, ya = yAt(t0), yb = yAt(t1), ym = yAt(tm) + s * .085;
        flags += `<path d="M${x0} ${ya}L${x1} ${yb}L${xm} ${ym}Z" fill="${C[i % C.length]}" opacity=".9"/><path d="M${x0 + (x1 - x0) * .3} ${(ya + yb) / 2 + s * .012}L${x1 - (x1 - x0) * .3} ${(ya + yb) / 2 + s * .012}" stroke="#fff" stroke-width="3" opacity=".5"/>`; }
      const string = `<path d="M0 ${y0}Q${W / 2} ${y0 + 2 * sag} ${W} ${y0}" stroke="#b8a99a" stroke-width="3" fill="none"/>`;
      // Kissen unten im Kreis
      const cw = s * .22, ch = s * .15, m = Math.ceil(W / (cw * .82)) + 1;
      let cush = "";
      for (let i = 0; i < m; i++) { const cx = i * cw * .82 - cw * .1, cy = H - ch * 1.02 + (i % 2) * ch * .14, c = C[(i * 2 + 1) % C.length];
        cush += `<g transform="rotate(${(i % 3 - 1) * 4} ${cx + cw / 2} ${cy + ch / 2})"><path d="M${cx} ${cy + ch * .15}Q${cx + cw / 2} ${cy - ch * .05} ${cx + cw} ${cy + ch * .15}Q${cx + cw * 1.04} ${cy + ch / 2} ${cx + cw} ${cy + ch * .85}Q${cx + cw / 2} ${cy + ch * 1.05} ${cx} ${cy + ch * .85}Q${cx - cw * .04} ${cy + ch / 2} ${cx} ${cy + ch * .15}Z" fill="${c}"/>
          <path d="M${cx + cw * .08} ${cy + ch * .5}Q${cx + cw / 2} ${cy + ch * .42} ${cx + cw * .92} ${cy + ch * .5}" stroke="#fff" stroke-width="2.5" stroke-dasharray="7 6" fill="none" opacity=".7"/><circle cx="${cx + cw / 2}" cy="${cy + ch * .47}" r="${ch * .06}" fill="#fff" opacity=".7"/></g>`; }
      const bubble = (x, y, w, c) => `<path d="M${x} ${y}h${w}q${w * .12} 0 ${w * .12} ${w * .12}v${w * .3}q0 ${w * .12} ${-w * .12} ${w * .12}h${-w * .55}l${-w * .14} ${w * .14}v${-w * .14}h${-w * .19}q${-w * .12} 0 ${-w * .12} ${-w * .12}v${-w * .3}q0 ${-w * .12} ${w * .12} ${-w * .12}z" fill="${c}" opacity=".55"/>`;
      return softBlobs(W, H, [[0, .55, .2, .3, "#e6dbf3", .5], [1, .5, .2, .3, "#f6e3c4", .5], [.5, 1, .45, .18, "#f3d6dc", .35]]) +
        string + flags + bubble(s * .05, H * .38, s * .12, "#c4a9e2") + bubble(W - s * .2, H * .45, s * .12, "#8fb8e2") + cush;
    } }
};
for (const k in BG_TPL) { const t = BG_TPL[k], inner = t.draw(1600, 900);
  t.thumb = `url("data:image/svg+xml,${encodeURIComponent(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 900"><rect width="1600" height="900" fill="${t.fill}"/>${inner}</svg>`)}") center/cover`; }
function drawBg(){''')
rep('''  const bg = $("#bg"), src = S && screen().bg;
  if (src) { bg.className = "bg custom";''', '''  const bg = $("#bg"), src = S && screen().bg;
  bg.style.background = "";
  if (src && src.startsWith("tpl:") && BG_TPL[src.slice(4)]) { const t = BG_TPL[src.slice(4)], W = window.innerWidth, H = window.innerHeight;
    bg.className = "bg tpl"; bg.style.background = t.base; bg.innerHTML = `<svg viewBox="0 0 ${W} ${H}" aria-hidden="true">${t.draw(W, H)}</svg>`; return; }
  if (src) { bg.className = "bg custom";''')
rep('''function ensurePalette(src){
  if (!src) return Promise.resolve();''', '''function ensurePalette(src){
  if (!src || src.startsWith("tpl:")) return Promise.resolve();''')
rep('''function theme(){
  const src = screen().bg, pal''', '''function theme(){
  const tk = (screen().bg || "").startsWith("tpl:") && BG_TPL[screen().bg.slice(4)]; if (tk) return tk.theme;
  const src = screen().bg, pal''')
rep('''<span class="lab">Aquarell (Standard)</span></button>''', '''<span class="lab">Aquarell (Standard)</span></button>
    ${Object.entries(BG_TPL).map(([k, t]) => `<button data-bgtpl="${k}" class="${sc.bg === "tpl:" + k ? "on" : ""}" style='background:${t.thumb}'><span class="lab">${t.name}</span></button>`).join("")}''')
rep('''    const sel = e.target.closest("[data-bgsel]");
    if (sel) { apply(''', '''    const tp = e.target.closest("[data-bgtpl]");
    if (tp) { apply("tpl:" + tp.dataset.bgtpl); refresh(); return; }
    const sel = e.target.closest("[data-bgsel]");
    if (sel) { apply(''')

# Musik pro Bildschirm (Upload oder YouTube), läuft solange der Bildschirm offen ist
rep('''<button data-a="reset">Alle Häkchen zurücksetzen</button>''', '''<button data-a="reset">Alle Häkchen zurücksetzen</button><button data-a="music">🎵 Musik …</button>''')
rep('''    if (a === "move") { closeMenus(); openMove(s); return; }''', '''    if (a === "move") { closeMenus(); openMove(s); return; }
    if (a === "music") { closeMenus(); openMusic(s); return; }''')
rep('''function renderAll(){ applyFont();''', r'''// ---------- Musik ----------
const MUS = { key: "", el: null, kind: "", playing: false };
const ytId = u => { const m = String(u || "").match(/(?:youtu\.be\/|youtube(?:-nocookie)?\.com\/(?:watch\?(?:.*&)?v=|embed\/|shorts\/|live\/))([\w-]{11})/); return m ? m[1] : (/^[\w-]{11}$/.test(String(u || "").trim()) ? String(u).trim() : null); };
function musicChip(){
  let c = document.getElementById("musicChip");
  if (!c) { c = document.createElement("div"); c.id = "musicChip"; c.className = "music-chip"; APP.appendChild(c);
    c.addEventListener("click", e => { if (e.target.closest("[data-mtoggle]")) musicToggle(); if (e.target.closest("[data-medit]")) openMusic(screen()); }); }
  return c;
}
function musicRender(){
  const m = screen().music, c = musicChip();
  if (!m) { c.hidden = true; return; }
  c.hidden = false;
  c.innerHTML = `<button data-mtoggle aria-label="${MUS.playing ? "Pause" : "Abspielen"}">${MUS.playing ? "⏸" : "▶"}</button><span class="mt" data-medit title="Musik ändern">♪ ${esc(m.name || "Musik")}</span>`;
  if (MUS.kind === "yt" && MUS.el && !c.contains(MUS.el)) c.appendChild(MUS.el);
}
function ytCmd(func){ try { MUS.el.contentWindow.postMessage(JSON.stringify({ event: "command", func, args: [] }), "*"); } catch {} }
function musicStop(){
  if (MUS.el) { try { if (MUS.kind === "file") { MUS.el.pause(); MUS.el.src = ""; } } catch {} MUS.el.remove?.(); }
  MUS.el = null; MUS.key = ""; MUS.kind = ""; MUS.playing = false;
}
function musicToggle(){
  if (!MUS.el) { syncMusic(true); return; }
  if (MUS.kind === "file") { if (MUS.el.paused) MUS.el.play().then(() => { MUS.playing = true; musicRender(); }).catch(() => {}); else { MUS.el.pause(); MUS.playing = false; musicRender(); } return; }
  if (MUS.playing) { ytCmd("pauseVideo"); MUS.playing = false; } else { ytCmd("playVideo"); MUS.playing = true; }
  musicRender();
}
function syncMusic(force){
  const m = screen().music, key = m ? (m.type + ":" + (m.id || m.src)) : "";
  if (key === MUS.key && !force) { musicRender(); return; }
  musicStop();
  if (m) {
    MUS.key = key; MUS.kind = m.type;
    if (m.type === "file") {
      const a = new Audio(m.src); a.loop = true; MUS.el = a;
      a.play().then(() => { MUS.playing = true; musicRender(); }).catch(() => { MUS.playing = false; musicRender(); });
    } else {
      const f = document.createElement("iframe");
      f.className = "yt"; f.allow = "autoplay; encrypted-media"; f.title = "Musik";
      f.src = `https://www.youtube-nocookie.com/embed/${m.id}?autoplay=1&loop=1&playlist=${m.id}&controls=0&enablejsapi=1&playsinline=1`;
      MUS.el = f; MUS.playing = true;
    }
  }
  musicRender();
}
function openMusic(s){
  const html = () => `<p class="hint">Die Musik läuft im Hintergrund, solange dieser Bildschirm offen ist. Unten links kannst du sie pausieren.</p>
    ${s.music ? `<p style="margin:0 0 10px"><b>Jetzt:</b> ♪ ${esc(s.music.name || "Musik")} <button class="sbtn" data-mrm>Musik entfernen</button></p>` : ""}
    <h3 class="sh3">YouTube-Link</h3><div class="addrow"><input type="text" id="mus-yt" placeholder="https://www.youtube.com/watch?v=…" aria-label="YouTube-Link"><button class="sbtn rose" data-myt>Übernehmen</button></div>
    <h3 class="sh3">Oder Audiodatei hochladen</h3><div class="addrow"><button class="sbtn" data-mup>🎵 Datei wählen (MP3, M4A …)</button></div>
    <input type="file" id="mus-file" accept="audio/*" hidden>`;
  const set = mus => { s.music = mus; save(); if (s.id === S.active) syncMusic(true); };
  sheet("Musik für «" + s.name + "»", html(), async (e, bg) => {
    const body = bg.querySelector(".body");
    if (e.target.closest("[data-mrm]")) { delete s.music; save(); if (s.id === S.active) syncMusic(true); body.innerHTML = html(); return; }
    if (e.target.closest("[data-myt]")) { const id = ytId($("#mus-yt").value); if (!id) { toast("Das ist kein YouTube-Link"); return; } set({ type: "yt", id, name: "YouTube" }); toast("Musik gespeichert ♪"); body.innerHTML = html(); return; }
    if (e.target.closest("[data-mup]")) {
      const inp = $("#mus-file"); inp.value = "";
      inp.onchange = async () => { const f = inp.files[0]; if (!f) return;
        if (f.size > 25e6) { toast("Die Datei ist zu gross (höchstens 25 MB)"); return; }
        toast("Musik wird hochgeladen …");
        let src = null;
        if (assets) { try { const up = await assets.upload(f); src = up.url; } catch {} }
        if (!src) { if (f.size > 6e6) { toast("Hochladen ging nicht. Bitte eine kleinere Datei wählen."); return; } src = await new Promise(r => { const fr = new FileReader(); fr.onload = () => r(fr.result); fr.readAsDataURL(f); }); }
        set({ type: "file", src, name: f.name.replace(/\.[^.]+$/, "").slice(0, 40) }); toast("Musik gespeichert ♪"); body.innerHTML = html(); };
      inp.click(); return; }
  });
}
function renderAll(){ syncMusic(); applyFont();''')
rep('.kn-back{font-weight:700}', '''.kn-back{font-weight:700}
.music-chip{position:absolute;left:14px;bottom:96px;z-index:40;display:flex;align-items:center;gap:6px;background:rgba(255,255,255,.92);border:1px solid var(--line);border-radius:999px;padding:4px 12px 4px 4px;box-shadow:0 4px 14px rgba(0,0,0,.1);font-size:14px}
.music-chip[hidden]{display:none}
.music-chip button{width:34px;height:34px;border-radius:50%;border:0;background:var(--rose);color:#fff;font-size:15px;cursor:pointer}
.music-chip .mt{cursor:pointer;max-width:220px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.music-chip .yt{position:absolute;width:2px;height:2px;opacity:.01;left:0;top:0;border:0;pointer-events:none}
.app.idle .music-chip{opacity:.25}''')

# ===== 16) Beschreibung näher am Punkt, Material «Trennwand» =====
rep('.t-list li.desc{padding-left:calc(1.25em + var(--fs) * .7vh)}',
    '.t-list li.desc{padding-left:calc(1.25em + var(--fs) * .7vh);padding-top:0!important;margin-top:calc(clamp(4px,2.2cqw,20px) * -1)}\n.t-list li:has(+ li.desc){padding-bottom:0!important}\n.t-list li.desc .txt{line-height:1.18}')
rep('''</svg>`]
};
const MAT_ORDER''', '''</svg>`],
  trennwand: ["Trennwand", `<svg viewBox="0 0 64 64"><path d="M10 12L38 9V41L16 45Z" fill="#dfe6ec" stroke="#8d99a4" stroke-width="2" stroke-linejoin="round"/><path d="M16 45L10 12L7 44Z" fill="#c3ccd4" stroke="#8d99a4" stroke-width="1.6" stroke-linejoin="round"/><path d="M22 20L56 17V52L26 57Z" fill="#f7f9fb" stroke="#7f8b96" stroke-width="2.2" stroke-linejoin="round"/><path d="M26 57L22 20L18 55Z" fill="#ccd4db" stroke="#7f8b96" stroke-width="1.8" stroke-linejoin="round"/><path d="M29 24L50 22" stroke="#dde3e8" stroke-width="2" stroke-linecap="round"/></svg>`]
};
const MAT_ORDER''')

# ===== 17) Verschieben: Bearbeitungsleiste zählt nicht zur Höhe; Material-Feld schmaler machbar =====
rep('''  const hh = AUTO.has(w.type) ? el.offsetHeight / r.height * 100 : w.h;''',
    '''  // Teile, die nur beim Bearbeiten sichtbar sind (Eingabeleiste, leere Anmerkung), zählen beim Verschieben nicht mit
  const edPx = [...el.querySelectorAll(".lfoot, .mnote.empty")].reduce((n, x) => n + x.offsetHeight, 0);
  const hh = AUTO.has(w.type) ? el.offsetHeight / r.height * 100 : w.h;
  const vh = AUTO.has(w.type) ? Math.max(4, (el.offsetHeight - edPx) / r.height * 100) : w.h;''')
rep('''w.y = Math.max(-1, Math.min(101 - Math.min(drag.hh, 30), drag.y + dy));''',
    '''w.y = Math.max(-1, Math.min(101 - Math.min(drag.vh, 30), drag.y + dy));''')
rep('''x: w.x, y: w.y, ww: w.w, hh, bw: r.width''', '''x: w.x, y: w.y, ww: w.w, hh, vh, bw: r.width''')
rep('''.t-mat{display:grid;grid-template-columns:repeat(auto-fill,minmax(calc(var(--fs) * 3.4vh),1fr));''',
    '''.t-mat{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(calc(var(--fs) * 3.4vh),28cqw),1fr));''')
exec(open(__file__.replace('patch.py','sec18.py'), encoding='utf-8').read())
