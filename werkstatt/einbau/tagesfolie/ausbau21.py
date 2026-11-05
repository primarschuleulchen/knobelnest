# 21) Ausbau Herbst 2026 (Teil von patch.py, nach hintergruende.py). Gilt auch für die Eulenkiste,
#     die ihre Tagesfolie aus der fertigen tagesfolie.html der Klassenkiste baut.
#   a) Bildschirm wechselt von selbst nach Uhrzeit (pro Bildschirm «⏰ Automatisch zeigen …», S.screens[].at, S.autoOff)
#   b) Stundenplan: «jetzt» läuft nach den Zeiten mit, vorbei = blasser (d.autoNow, manuelles «jetzt» hat Vorrang)
#   c) Hausaufgaben als Baustein (nur Klassenkiste, KN.heft liest das Hausaufgabenheft der Klasse)
#   d) Timer: Gong am Ende, Aussehen Ring/Kreis/Sanduhr, «⛶ Gross» füllt den Bildschirm (d.look, d.ton)
#   e) Zufallsname: wer dran war, kommt erst wieder, wenn alle dran waren (d.drawn)
#   f) Sanfter Übergang beim Wechseln der Bildschirme

# ---------- gemeinsame Helfer ----------
rep('function goScreen(id){ S.active = id; selId = null; save(); closeMenus(); renderAll(); }', r'''function goScreen(id){ const neu = id !== S.active; S.active = id; selId = null; save(); closeMenus(); renderAll(); if (neu) boardFade(); }
// f) Sanfter Übergang
function boardFade(){ ["#board", "#bg"].forEach(q => { const b = $(q); if (!b) return; b.classList.remove("fade"); void b.offsetWidth; b.classList.add("fade"); }); }
const hm = t => { const m = String(t || "").match(/^\s*(\d{1,2})[:.](\d{2})/); return m ? +m[1] * 60 + +m[2] : null; };
const nowMin = () => { const n = new Date(); return n.getHours() * 60 + n.getMinutes(); };''')

# ---------- a) Bildschirm nach Uhrzeit ----------
rep('<button data-a="music">🎵 Musik …</button>', '<button data-a="music">🎵 Musik …</button><button data-a="auto">⏰ Automatisch zeigen …</button>')
rep('    if (a === "music") { closeMenus(); openMusic(s); return; }', '''    if (a === "music") { closeMenus(); openMusic(s); return; }
    if (a === "auto") { closeMenus(); openAuto(s); return; }''')
rep('''<button class="ddrow ${x.id === S.active ? "on" : ""}" data-go="${x.id}">${esc(x.name)}</button>''',
    '''<button class="ddrow ${x.id === S.active ? "on" : ""}" data-go="${x.id}">${esc(x.name)}${x.at && !S.autoOff ? ` <small class="dd-at">⏰ ${esc(x.at)}</small>` : ""}</button>''')
rep('function openMusic(s){', r'''function openAuto(s){
  const list = () => S.screens.filter(x => hm(x.at) != null).sort((a, b) => hm(a.at) - hm(b.at));
  const html = () => `<p class="hint">Zur gewählten Zeit erscheint «${esc(s.name)}» von selbst – jeden Tag. Du kannst danach jederzeit selber wechseln; bis zur nächsten Zeit bleibt dann dein Bildschirm.</p>
    <div class="addrow"><label for="auto-at" style="font-size:18px">Zeigen ab</label><input type="time" id="auto-at" value="${esc(s.at ? String(s.at).padStart(5, "0") : "")}" style="font-size:18px;border:1.5px solid var(--eline,#dbe7f1);border-radius:12px;padding:6px 10px"><button class="sbtn rose" data-asave>Speichern</button>${s.at ? `<button class="sbtn" data-aoff>Nicht automatisch</button>` : ""}</div>
    <h3 class="sh3" style="margin-top:18px">So läuft dein Tag</h3>
    ${list().length ? `<div class="auto-list">${list().map(x => `<div class="${x.id === s.id ? "on" : ""}"><b>${esc(x.at)}</b><span>${esc(x.name)}</span></div>`).join("")}</div>` : `<p class="hint">Noch kein Bildschirm hat eine Zeit.</p>`}
    <label style="display:flex;align-items:center;gap:10px;margin-top:16px;font-size:17px"><input type="checkbox" data-aall ${S.autoOff ? "" : "checked"} style="width:22px;height:22px"> Bildschirme automatisch wechseln</label>`;
  const bg = sheet("Automatisch zeigen", html(), (e, bg) => {
    const body = bg.querySelector(".body");
    if (e.target.closest("[data-asave]")) { const v = $("#auto-at").value; if (!v) { toast("Bitte eine Zeit wählen"); return; } s.at = v.replace(/^0(\d:)/, "$1"); S.autoOff = false; save(); AUTO_KEY = null; toast(`«${s.name}» erscheint um ${s.at}`); body.innerHTML = html(); return; }
    if (e.target.closest("[data-aoff]")) { delete s.at; save(); body.innerHTML = html(); return; }
    if (e.target.matches("[data-aall]")) { S.autoOff = !e.target.checked; save(); AUTO_KEY = null; }
  });
}
let AUTO_KEY = null;
function autoScreen(){
  if (!S || S.autoOff) return;
  const now = nowMin(); let best = null;
  S.screens.forEach(x => { const t = hm(x.at); if (t != null && t <= now && (!best || t > best.t)) best = { s: x, t }; });
  if (!best) return;
  const key = new Date().toDateString() + "|" + best.s.id + "|" + best.t;
  if (key === AUTO_KEY) return;
  const ae = document.activeElement;
  if (document.querySelector(".sheet-bg, .dd, .menu") || (ae && ae.matches && ae.matches('[contenteditable="true"],input,textarea'))) return; // gerade am Arbeiten: etwas später
  AUTO_KEY = key;
  if (best.s.id !== S.active) goScreen(best.s.id);
}
setInterval(autoScreen, 15000);
setTimeout(autoScreen, 2500);
document.addEventListener("visibilitychange", () => { if (!document.hidden) autoScreen(); });
function openMusic(s){''')

# ---------- b) Stundenplan: «jetzt» automatisch ----------
rep('''<div class="pl-item ${it.now ? "now" : ""}" data-it="${it.id}"''', '''<div class="pl-item ${planCls(d, pi, it)}" data-it="${it.id}"''')
rep('<button class="sbtn" data-nowclear>«jetzt» entfernen</button>', '<button class="sbtn" data-nowclear>«jetzt» entfernen</button><button class="sbtn" data-pauto>${d.autoNow === false ? "«jetzt» automatisch: aus" : "«jetzt» automatisch: an"}</button>')
rep('  if (e.target.closest("[data-nowclear]")) {', '''  if (e.target.closest("[data-pauto]")) { d.autoNow = d.autoNow === false; save(); rerender(w); return; }
  if (e.target.closest("[data-nowclear]")) {''')
rep('const closeSheet = bg => { bg.remove(); renderBoard(); };', r'''const closeSheet = bg => { bg.remove(); renderBoard(); };
// Stundenplan: welche Lektion läuft gerade? (nach den Zeiten; eine von Hand markierte hat Vorrang)
function planAuto(d){
  if (d.autoNow === false || d.items.some(i => i.now)) return null;
  const now = nowMin(), ts = d.items.map((it, i) => hm(it.time || lessonAt(d, i)));
  let cur = -1; ts.forEach((t, i) => { if (t != null && t <= now) cur = i; });
  if (cur < 0) return -1;
  if (!ts.slice(cur + 1).some(t => t != null) && now - ts[cur] >= 50) return d.items.length; // alles vorbei
  return cur;
}
function planCls(d, i, it){
  if (it.now) return "now";
  const c = planAuto(d); if (c == null || c < 0) return "";
  return i < c ? "vorbei" : i === c ? "now auto" : "";
}
const PLAN_K = new Map();
setInterval(() => { if (!S) return; screen().widgets.filter(w => w.type === "plan").forEach(w => {
  const k = String(planAuto(w.data)); if (PLAN_K.get(w.id) === k) return;
  const el = document.querySelector(`[data-w="${w.id}"]`); if (el && el.contains(document.activeElement) && document.activeElement !== document.body) return;
  const first = !PLAN_K.has(w.id); PLAN_K.set(w.id, k); if (!first) rerender(w); }); }, 20000);''')

# ---------- c) Hausaufgaben (nur Klassenkiste) ----------
HEFT_ICON = ('<rect x="7" y="4" width="18" height="24" rx="2.5" fill="none" stroke="currentColor" stroke-width="2.4"/>'
             '<path d="M11 10h10M11 15h10M11 20h6" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/>')
rep('  note:    { lab: "Text",', '  heft:    { lab: "Hausaufgaben", w: 30, h: 44, d: () => ({ heading: "Hausaufgaben" }), icon: `' + HEFT_ICON + '` },\n  note:    { lab: "Text",')
rep('.concat(KN ? ["|","stand"].concat(KN.otterUrl ? ["otter"] : []) : []);', '.concat(KN ? ["|","stand"].concat(KN.otterUrl ? ["otter"] : []).concat(KN.heft ? ["heft"] : []) : []);')
rep('    case "image": return `<div class="t-img">', '    case "heft": return heftHTML(w);\n    case "image": return `<div class="t-img">')
rep('title: ["Farbe", "Farbe des Titels"],', 'title: ["Farbe", "Farbe des Titels"], heft: ["↻", "Hausaufgaben neu laden"], timer: ["⚙", "Ton und Aussehen"],')
rep('    if (w.type === "clock") { d.sec = !d.sec; save(); rerender(w); }', '''    if (w.type === "clock") { d.sec = !d.sec; save(); rerender(w); }
    if (w.type === "heft") { heftLoad(true); toast("Hausaufgaben werden neu geladen"); }
    if (w.type === "timer") openTimerSet(w);''')
rep('function roll(w){', r'''// Hausaufgaben aus dem Hausaufgabenheft der Klasse (nur für die ganze Klasse, nichts von einzelnen Kindern)
const HEFT = { data: null, at: 0, busy: false };
function heftLoad(force){
  if (!KN || !KN.heft || HEFT.busy) return;
  if (!force && HEFT.at && Date.now() - HEFT.at < 120000) return;
  HEFT.busy = true;
  Promise.resolve().then(() => KN.heft()).then(x => { HEFT.data = x && Array.isArray(x.entries) ? x : { entries: [] }; HEFT.err = false; })
    .catch(() => { HEFT.err = true; HEFT.data = HEFT.data || { entries: [] }; })
    .finally(() => { HEFT.busy = false; HEFT.at = Date.now(); if (S) screen().widgets.filter(w => w.type === "heft").forEach(rerender); });
}
setInterval(() => { if (S && screen().widgets.some(w => w.type === "heft")) heftLoad(); }, 30000);
const isoDay = t => `${t.getFullYear()}-${String(t.getMonth() + 1).padStart(2, "0")}-${String(t.getDate()).padStart(2, "0")}`;
const HF_ART = { aufgabe: "", lernkontrolle: "Lernkontrolle", termin: "Termin", ferien: "Ferien", schulfrei: "schulfrei", geburtstag: "Geburtstag" };
const HF_ZEICHEN = { aufgabe: "✎", lernkontrolle: "★", termin: "◷", ferien: "☀", schulfrei: "☾", geburtstag: "♥" };
function heftHTML(w){
  const d = w.data, head = `<div class="whead${d.heading ? "" : " empty"}" contenteditable="true" spellcheck="false" data-f="heading" data-ph="Überschrift">${esc(d.heading || "")}</div>`;
  if (!KN || !KN.heft) return head + `<div class="emptyhint">${KN ? "Das Hausaufgabenheft ist für dich noch nicht freigegeben." : "Die Hausaufgaben gibt es nur in der Klassenkiste."}</div>`;
  if (!HEFT.data) { heftLoad(); return head + `<div class="emptyhint">Hausaufgaben werden geladen …</div>`; }
  const all = HEFT.data.entries.filter(e => e && !e.by && (!Array.isArray(e.for) || !e.for.length) && /^\d{4}-\d{2}-\d{2}$/.test(e.date || ""));
  const frei = new Set(all.filter(e => e.type === "ferien" || e.type === "schulfrei").map(e => e.date));
  const t0 = new Date(); t0.setHours(12, 0, 0, 0); const heute = isoDay(t0);
  const nx = new Date(t0); do nx.setDate(nx.getDate() + 1); while (nx.getDay() === 0 || nx.getDay() === 6 || frei.has(isoDay(nx)));
  const naechst = isoDay(nx), morgen = new Date(t0); morgen.setDate(morgen.getDate() + 1);
  const txt = e => { const el = document.createElement("template"); el.innerHTML = String(e.title || ""); const t = (el.content.textContent || "").trim();
    return `${e.fach ? `<b>${esc(e.fach)}</b> ` : ""}${esc(t || HF_ART[e.type] || "")}${e.type === "lernkontrolle" && t ? ` <em>(${HF_ART.lernkontrolle})</em>` : ""}`; };
  const li = e => `<li class="hf-${esc(e.type || "aufgabe")}"><span class="hf-z" aria-hidden="true">${HF_ZEICHEN[e.type] || "✎"}</span><span>${txt(e)}</span></li>`;
  const tag = (lab, iso) => { const l = all.filter(e => e.date === iso).sort((a, b) => (a.order ?? 0) - (b.order ?? 0));
    return `<div class="hf-tag"><div class="hf-t">${lab}</div>${l.length ? `<ul>${l.map(li).join("")}</ul>` : `<div class="hf-leer">nichts eingetragen</div>`}</div>`; };
  const bis = new Date(t0); bis.setDate(bis.getDate() + 14);
  const bald = all.filter(e => (e.type === "lernkontrolle" || e.type === "termin") && e.date > naechst && e.date <= isoDay(bis)).sort((a, b) => a.date < b.date ? -1 : 1).slice(0, 4);
  const kurz = iso => { const x = new Date(iso + "T12:00:00"); return `${WD[x.getDay()].slice(0, 2)} ${x.getDate()}.${x.getMonth() + 1}.`; };
  return head + `<div class="t-heft">${tag("Heute", heute)}${tag(isoDay(morgen) === naechst ? "Morgen" : WD[nx.getDay()], naechst)}
    ${bald.length ? `<div class="hf-tag bald"><div class="hf-t">Bald</div><ul>${bald.map(e => `<li><span class="hf-z" aria-hidden="true">${HF_ZEICHEN[e.type]}</span><span><i>${kurz(e.date)}</i> ${txt(e)}</span></li>`).join("")}</ul></div>` : ""}
    ${HEFT.err ? `<div class="hf-leer">Das Heft konnte gerade nicht geladen werden.</div>` : ""}</div>`;
}
function roll(w){''')

# ---------- d) Timer ----------
rep('''      return `<div class="t-timer"><svg class="ring" viewBox="0 0 100 100"><circle cx="50" cy="50" r="42" stroke="#f3dcd8"/><circle data-arc cx="50" cy="50" r="42" stroke="#ec9d95" stroke-linecap="round" transform="rotate(-90 50 50)" stroke-dasharray="263.9" stroke-dashoffset="${(263.9 * (1 - (d.total ? left / d.total : 0))).toFixed(1)}"/></svg>''',
    '''      return `<div class="t-timer">${timerVis(d, left, w.id)}''')
rep('''<button class="tbtn" data-t="reset">Zurück</button>''', '''<button class="tbtn" data-t="reset">Zurück</button><button class="tbtn" data-t="big" aria-label="Timer gross zeigen">⛶</button>''')
rep('function timerAction(w, t){\n  const d = w.data;', '''function timerAction(w, t){
  if (t === "big") { openBig(w); return; }
  const d = w.data;''')
rep('''    el.querySelector("[data-arc]").setAttribute("stroke-dashoffset", (263.9 * (1 - left / (w.data.total || 1))).toFixed(1));''',
    '''    timerSet(el, left / (w.data.total || 1)); bigSet(w, left);''')
rep('''    if (left <= 0) { w.data.endAt = 0; w.data.left = 0; save(); rerender(w); beep();''', '''    if (left <= 0) { w.data.endAt = 0; w.data.left = 0; save(); rerender(w); timerTon(w.data.ton); bigSet(w, 0, true);''')
rep('function beep(){', r'''// Timer: Aussehen (Ring, Kreis, Sanduhr) und Ton (Gong, Piepsen, kein Ton)
function timerVis(d, left, id){
  const f = d.total ? left / d.total : 0, off = (263.9 * (1 - f)).toFixed(1);
  if (d.look === "kreis") return `<svg class="ring" viewBox="0 0 100 100"><circle cx="50" cy="50" r="46" style="fill:#fbeeec;stroke:none"/><circle data-arc cx="50" cy="50" r="23" pathLength="263.9" style="stroke-width:46" stroke="#ec9d95" transform="rotate(-90 50 50)" stroke-dasharray="263.9" stroke-dashoffset="${off}"/></svg>`;
  if (d.look === "sanduhr") { const k = "s" + String(id).replace(/\W/g, "");
    return `<svg class="ring sand" viewBox="0 0 60 100" aria-hidden="true"><defs><clipPath id="${k}o"><path d="M10 9H50Q50 30 32 49H28Q10 30 10 9Z"/></clipPath><clipPath id="${k}u"><path d="M28 51H32Q50 70 50 91H10Q10 70 28 51Z"/></clipPath></defs>
      <rect data-sando x="0" y="${(9 + (1 - f) * 40).toFixed(1)}" width="60" height="${(40 * f).toFixed(1)}" fill="#e9bf62" clip-path="url(#${k}o)"/>
      <rect data-sandu x="0" y="${(91 - (1 - f) * 40).toFixed(1)}" width="60" height="${((1 - f) * 40).toFixed(1)}" fill="#e9bf62" clip-path="url(#${k}u)"/>
      ${d.endAt ? `<path class="sand-fall" d="M30 49V89" stroke="#e9bf62" stroke-width="1.6"/>` : ""}
      <path d="M10 9H50Q50 30 32 49V51Q50 70 50 91H10Q10 70 28 51V49Q10 30 10 9Z" fill="none" stroke="#a08560" stroke-width="2.2" stroke-linejoin="round"/>
      <rect x="5" y="4" width="50" height="5" rx="2.5" fill="#a07c5c"/><rect x="5" y="91" width="50" height="5" rx="2.5" fill="#a07c5c"/></svg>`; }
  return `<svg class="ring" viewBox="0 0 100 100"><circle cx="50" cy="50" r="42" stroke="#f3dcd8"/><circle data-arc cx="50" cy="50" r="42" stroke="#ec9d95" stroke-linecap="round" transform="rotate(-90 50 50)" stroke-dasharray="263.9" stroke-dashoffset="${off}"/></svg>`;
}
function timerSet(el, f){
  f = Math.max(0, Math.min(1, f));
  el.querySelectorAll("[data-arc]").forEach(a => a.setAttribute("stroke-dashoffset", (263.9 * (1 - f)).toFixed(1)));
  el.querySelectorAll("[data-sando]").forEach(r => { r.setAttribute("y", (9 + (1 - f) * 40).toFixed(1)); r.setAttribute("height", (40 * f).toFixed(1)); });
  el.querySelectorAll("[data-sandu]").forEach(r => { r.setAttribute("y", (91 - (1 - f) * 40).toFixed(1)); r.setAttribute("height", ((1 - f) * 40).toFixed(1)); });
}
function timerTon(ton){
  if (ton === "aus") return;
  if (ton === "piep") { beep(); return; }
  try { audio = audio || new (window.AudioContext || window.webkitAudioContext)(); audio.resume?.();
    [0, 1.6].forEach(o => [[392, .32], [587.3, .2], [784, .12], [1174.7, .05]].forEach(([fq, v]) => {
      const os = audio.createOscillator(), g = audio.createGain(); os.type = "sine"; os.frequency.value = fq; os.connect(g); g.connect(audio.destination);
      const t0 = audio.currentTime + o; g.gain.setValueAtTime(.0001, t0); g.gain.exponentialRampToValueAtTime(v, t0 + .015); g.gain.exponentialRampToValueAtTime(.0001, t0 + 2.6); os.start(t0); os.stop(t0 + 2.7); }));
  } catch {}
}
function openTimerSet(w){
  const d = w.data;
  const opt = (k, v, lab, cur) => `<button class="chip ${cur === v ? "added" : ""}" data-${k}="${v}">${lab}</button>`;
  const html = () => `<h3 class="sh3">Aussehen</h3><div class="chips">${opt("tlook", "ring", "Ring", d.look || "ring")}${opt("tlook", "kreis", "Kreis, der sich leert", d.look || "ring")}${opt("tlook", "sanduhr", "Sanduhr", d.look || "ring")}</div>
    <h3 class="sh3" style="margin-top:16px">Ton am Ende</h3><div class="chips">${opt("tton", "gong", "Gong", d.ton || "gong")}${opt("tton", "piep", "Piepsen", d.ton || "gong")}${opt("tton", "aus", "Kein Ton", d.ton || "gong")}</div>
    <div style="margin-top:12px"><button class="sbtn" data-tprobe>▶ Probehören</button></div>`;
  sheet("Timer", html(), (e, bg) => {
    const l = e.target.closest("[data-tlook]"), t = e.target.closest("[data-tton]");
    if (l) { d.look = l.dataset.tlook; save(); rerender(w); }
    if (t) { d.ton = t.dataset.tton; save(); }
    if (e.target.closest("[data-tprobe]")) timerTon(d.ton || "gong");
    if (l || t) bg.querySelector(".body").innerHTML = html();
  });
}
// Timer gross: füllt den ganzen Bildschirm
let BIG = null;
function openBig(w){
  closeBig();
  const d = w.data, el = document.createElement("div"); el.className = "tbig"; el.setAttribute("role", "dialog"); el.setAttribute("aria-label", "Timer gross");
  const paint = () => { const left = timerLeft(d);
    el.innerHTML = `<div class="tbig-in"><div class="tbig-vis">${timerVis(d, left, w.id + "big")}</div><div class="tbig-num" data-bignum>${fmt(left)}</div>
      <div class="tbig-ctl"><button class="tbtn go" data-bg="go">${d.endAt ? "Pause" : "Start"}</button><button class="tbtn" data-bg="reset">Zurück</button><button class="tbtn" data-bg="x">Schliessen</button></div></div>`; };
  paint(); APP.appendChild(el); BIG = { id: w.id, el, paint };
  el.addEventListener("click", e => { const b = e.target.closest("[data-bg]"); if (!b) return;
    if (b.dataset.bg === "x") { closeBig(); return; }
    timerAction(w, b.dataset.bg); el.classList.remove("done"); paint(); });
}
function closeBig(){ if (BIG) { BIG.el.remove(); BIG = null; } }
function bigSet(w, left, done){
  if (!BIG || BIG.id !== w.id) return;
  if (done) { BIG.paint(); BIG.el.classList.add("done"); return; }
  const n = BIG.el.querySelector("[data-bignum]"); if (n) n.textContent = fmt(left);
  timerSet(BIG.el, left / (w.data.total || 1));
}
document.addEventListener("keydown", e => { if (e.key === "Escape" && BIG) closeBig(); });
function beep(){''')

# ---------- e) Zufallsname ohne Wiederholung ----------
rep('''function roll(w){
  let names = w.data.names.split("\\n").map(s => s.trim()).filter(Boolean);
  if (!names.length) { const abs = absentToday(); names = S.roster.filter(n => !abs.has(n)); }
  if (!names.length) { w.data.editing = true; rerender(w); return; }
  const el = document.querySelector(`[data-w="${w.id}"] [data-pick]`);
  let n = 0; const steps = 14 + Math.floor(Math.random() * 6);
  const tick = () => { el.textContent = names[Math.floor(Math.random() * names.length)]; if (++n < steps) setTimeout(tick, 40 + n * 12); else { w.data.pick = el.textContent; save(); } };
  tick();
}''', r'''function randNames(w){
  let names = (w.data.names || "").split("\n").map(s => s.trim()).filter(Boolean);
  if (!names.length) { const abs = absentToday(); names = S.roster.filter(n => !abs.has(n)); }
  return names;
}
// Wer dran war, kommt erst wieder, wenn alle dran waren
const ROLLING = new Set();
function roll(w){
  if (ROLLING.has(w.id)) return; // läuft schon
  const names = randNames(w), d = w.data;
  if (!names.length) { d.editing = true; rerender(w); return; }
  d.drawn = (d.drawn || []).filter(n => names.includes(n));
  let pool = names.filter(n => !d.drawn.includes(n));
  if (!pool.length) { d.drawn = []; pool = names.slice(); toast("Alle waren dran – es geht von vorne los"); }
  const pickN = pool[Math.floor(Math.random() * pool.length)];
  const el = document.querySelector(`[data-w="${w.id}"] [data-pick]`); if (!el) return;
  ROLLING.add(w.id);
  let n = 0; const steps = 14 + Math.floor(Math.random() * 6);
  const tick = () => { if (++n < steps) { el.textContent = names[Math.floor(Math.random() * names.length)]; setTimeout(tick, 40 + n * 12); }
    else { ROLLING.delete(w.id); el.textContent = pickN; d.pick = pickN; d.drawn.push(pickN); save(); rerender(w); } };
  tick();
}
function randInfo(w){
  const names = randNames(w); if (names.length < 2) return "";
  const rest = names.filter(n => !(w.data.drawn || []).includes(n)).length;
  return `<div class="rinfo">${rest ? `noch ${rest} von ${names.length}` : "alle waren dran"}${(w.data.drawn || []).length ? ` · <button class="rreset" data-rreset>von vorne</button>` : ""}</div>`;
}''')
rep('''<button class="tbtn" data-redit>Namen ändern</button></div></div>`;''', '''<button class="tbtn" data-redit>Namen ändern</button></div>${randInfo(w)}</div>`;''')
rep('  if (e.target.closest("[data-roll]")) roll(w);', '''  if (e.target.closest("[data-roll]")) roll(w);
  if (e.target.closest("[data-rreset]")) { w.data.drawn = []; save(); rerender(w); return; }''')

# ---------- CSS ----------
rep('.t-plan.h{flex-direction:row;flex-wrap:wrap;justify-content:center}', r'''.t-plan.h{flex-direction:row;flex-wrap:wrap;justify-content:center}
.pl-item.vorbei{opacity:.42;filter:saturate(.6)}
.pl-item{transition:opacity .6s}
#board.fade,#bg.fade{animation:bfade .45s ease-out}
@keyframes bfade{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
#bg.fade{animation-name:bgfade}
@keyframes bgfade{from{opacity:.3}to{opacity:1}}
.dd-at{font-size:.8em;color:#9a7a25;margin-left:4px;white-space:nowrap}
.auto-list{display:flex;flex-direction:column;gap:4px}
.auto-list div{display:flex;gap:14px;align-items:baseline;padding:6px 12px;border-radius:12px;background:#f6f9fc;font-size:18px}
.auto-list div.on{background:#fbf3dc;box-shadow:inset 0 0 0 1.5px #d6ad45}
.auto-list b{font-weight:400;color:#3f78a8;min-width:3.2em;font-variant-numeric:tabular-nums}
.t-heft{flex:1;min-height:0;overflow:auto;padding:0 6cqw 3cqh;font-family:var(--hand);font-size:clamp(14px,min(6.2cqw,7cqh),40px);line-height:1.18;display:flex;flex-direction:column;gap:.5em}
.hf-t{font-size:.72em;letter-spacing:.06em;text-transform:uppercase;color:#3f78a8;border-bottom:1.5px dashed rgba(214,173,69,.6);padding-bottom:.1em;margin-bottom:.25em}
.t-heft ul{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:.25em}
.t-heft li{display:flex;gap:.45em;align-items:baseline;color:var(--tc,inherit)}
.t-heft b{font-weight:400;color:#3f78a8}
.t-heft em,.t-heft i{font-style:normal;color:#8a918c;font-size:.85em}
.hf-z{color:#d6ad45;flex:none;width:1em;text-align:center}
.hf-lernkontrolle .hf-z{color:#e07a70}
.hf-leer{color:#a7ada8;font-size:.85em}
.hf-tag.bald{font-size:.82em}
.rinfo{font-size:clamp(12px,4cqh,17px);color:#8a918c;font-family:var(--hand)}
.rreset{border:0;background:none;padding:0;color:#3f78a8;text-decoration:underline;font:inherit;cursor:pointer}
.ring.sand{aspect-ratio:.6}
.sand-fall{stroke-dasharray:3 3;animation:sandfall .5s linear infinite}
@keyframes sandfall{to{stroke-dashoffset:-6}}
.tbig{position:fixed;inset:0;z-index:150;background:#fbfaf6;display:flex;align-items:center;justify-content:center;padding:4vh 4vw}
.tbig-in{display:flex;flex-direction:column;align-items:center;gap:2vh;width:100%;height:100%;justify-content:center}
.tbig-vis{height:52vh;display:flex;justify-content:center}
.tbig-vis .ring{height:100%;width:auto}
.tbig-num{font-weight:800;font-variant-numeric:tabular-nums;font-size:min(22vh,18vw);line-height:1}
.tbig-ctl{display:flex;gap:10px}
.tbig-ctl .tbtn{font-size:22px;padding:8px 22px;font-family:"Patrick Hand",cursive;font-weight:400}
.tbig.done .tbig-num{color:#e07a70;animation:flash 1s ease-in-out 3}''')
