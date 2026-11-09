# Baut den Ordner knobelnest/zeitreise aus dem Zeitreise-Projekt (fcbhcd1997/Altsteinzeit).
# Aufruf: python3 build_zeitreise.py <quellordner> <zielordner>
import sys, os, shutil, re
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
from lokal import lokal  # Schriften/Programmteile vom eigenen Server
src, dst = sys.argv[1], sys.argv[2]
READY = ['altsteinzeit', 'jungsteinzeit']          # später einfach weitere Epochen ergänzen
PREFIX = {'altsteinzeit': 'alt-', 'jungsteinzeit': 'jung-', 'bronzezeit': 'bronze-', 'eisenzeit': 'eisen-', 'roemerzeit': 'roemer-', 'mittelalter': 'ma-'}
os.makedirs(os.path.join(dst, 'bilder'), exist_ok=True)

def rep(s, a, b, n=1):
    assert a in s, 'NICHT GEFUNDEN: ' + a[:90]
    return s.replace(a, b, n)

# ---------- Epochen ----------
for era in READY:
    s = open(os.path.join(src, era + '.html'), encoding='utf-8').read()
    s = rep(s, "const ERA = '" + era + "', EMBED = window.parent !== window;",
               "const ERA = '" + era + "', EMBED = window.parent !== window;\nconst KNQ = new URLSearchParams(location.search); // Knobelnest: Stand und Grafik kommen über die Adresse")
    s = re.sub(r"(try \{ const v = localStorage\.getItem\(GKEY\); if \(v === 'hoch' \|\| v === 'schnell'\) QUALITY = v; \} catch\(e\)\{\})",
               r"\1\n{ const v = KNQ.get('q'); if (v === 'hoch' || v === 'schnell') QUALITY = v; }", s, count=1)
    s = rep(s, "function loadVisited(){ try {",
               "function loadVisited(){ if (KNQ.has('kn')) { try { const a = JSON.parse(KNQ.get('kn')); return Array.isArray(a) ? a.filter(id => BY_ID[id]) : []; } catch(e){ return []; } }\n  try {")
    s = rep(s, "function saveVisited(){ try { localStorage.setItem(STORE, JSON.stringify([...visited])); } catch(e){} }",
               "function saveVisited(){ try { localStorage.setItem(STORE, JSON.stringify([...visited])); } catch(e){} tell({ type:'visited', list:[...visited] }); }")
    s = rep(s, "function renderResult(){\n  const n = qorder.length;",
               "function renderResult(){\n  const n = qorder.length; tell({ type:'quiz', score:qscore, n });")
    s = rep(s, "  try { localStorage.setItem(GKEY, HQ ? 'schnell' : 'hoch'); } catch(e){}\n  location.reload();",
               "  try { localStorage.setItem(GKEY, HQ ? 'schnell' : 'hoch'); } catch(e){}\n  if (EMBED) { tell({ type:'quality', v: HQ ? 'schnell' : 'hoch' }); return; }\n  location.reload();")
    open(os.path.join(dst, era + '.html'), 'w', encoding='utf-8').write(lokal(s, '../'))
    for f in os.listdir(os.path.join(src, 'bilder')):
        if f.startswith(PREFIX[era]): shutil.copy(os.path.join(src, 'bilder', f), os.path.join(dst, 'bilder', f))

# ---------- Startseite mit Zeitstrahl, Schlössern und Knobelnest-Verbindung ----------
s = open(os.path.join(src, 'index.html'), encoding='utf-8').read()
s = rep(s, "</style>\n</head>", """/* Knobelnest: Schlösser und Meldungen */
.zs-era.locked{opacity:.6}
.zs-era.locked .zs-ico{filter:grayscale(1)}
.zs-lock{font-size:.85rem;margin-left:-2px}
.kn-toast{position:fixed;left:50%;bottom:calc(env(safe-area-inset-bottom,0px) + 24px);transform:translate(-50%,20px);z-index:60;max-width:min(560px,calc(100vw - 32px));
  background:var(--paper);color:var(--ink);border:2px solid var(--charcoal);border-radius:16px;padding:12px 18px;font-family:var(--font-body);font-size:1rem;line-height:1.35;
  box-shadow:0 10px 30px rgba(0,0,0,.35);opacity:0;pointer-events:none;transition:opacity .25s, transform .25s}
.kn-toast.on{opacity:1;transform:translate(-50%,0)}
.kn-empty{position:fixed;inset:0;display:none;align-items:center;justify-content:center;padding:24px;z-index:5}
.kn-empty.on{display:flex}
.kn-empty div{background:var(--paper);color:var(--ink);border:2px solid var(--charcoal);border-radius:20px;padding:24px 28px;max-width:520px;text-align:center;font-size:1.1rem}
</style>
</head>""")
s = rep(s, '<div id="worlds"></div>', '<div id="worlds"></div>\n<div class="kn-toast" id="knToast" role="status" aria-live="polite"></div>\n<div class="kn-empty" id="knEmpty"><div>🔒 Deine Lehrperson hat noch keine Zeit freigeschaltet.</div></div>')
s = rep(s, "var BY = {}; ERAS.forEach(function(e, i){ e.index = i; BY[e.id] = e; });",
"""var READY = """ + repr(READY).replace("'", '"') + """; // Epochen, die schon eingebaut sind
var BY = {}; ERAS.forEach(function(e, i){ e.index = i; e.ready = READY.indexOf(e.id) >= 0; BY[e.id] = e; });

/* ---------- Knobelnest: Stand pro Kind, Schlösser, Fortschritt ---------- */
var KN = { on:false, teacher:false, set:{ open:['altsteinzeit'], pass:7, auto:true, mine:[] }, st:{ v:1, visited:{}, quiz:{}, tot:{}, q:'', last:'' } };
function knSend(m){ if (window.parent === window) return; try { m.knobelnest = 1; parent.postMessage(m, '*'); } catch(e){} }
function passed(id){ var q = KN.st.quiz[id]; return !!q && q.best >= KN.set.pass; }
function isOpen(id){
  var e = BY[id]; if (!e || !e.ready) return false;
  if (!KN.on || KN.teacher) return true;
  if (KN.set.open.indexOf(id) >= 0 || KN.set.mine.indexOf(id) >= 0) return true;
  if (KN.set.auto !== false && e.index > 0 && passed(ERAS[e.index - 1].id)) return true;
  return false;
}
function lockReason(id){
  var e = BY[id]; if (!e.ready) return '🔒 Die ' + e.name + ' kommt bald.';
  var p = e.index > 0 ? ERAS[e.index - 1] : null;
  if (KN.set.auto !== false && p && isOpen(p.id)) return '🔒 Löse zuerst das Quiz der ' + p.name + ' mit mindestens ' + KN.set.pass + ' von 10 Punkten. Dann öffnet sich die ' + e.name + '.';
  return '🔒 Die ' + e.name + ' schaltet deine Lehrperson frei.';
}
var toastT;
function knToast(t){ var el = document.getElementById('knToast'); el.textContent = t; el.classList.add('on'); clearTimeout(toastT); toastT = setTimeout(function(){ el.classList.remove('on'); }, 5200); }
function award(){
  var zr = {}, stars = 0;
  ERAS.forEach(function(e){ if (!e.ready) return; var q = KN.st.quiz[e.id];
    zr[e.id] = { name:e.name, f:(KN.st.visited[e.id] || []).length, t:KN.st.tot[e.id] || 0, best:q ? q.best : null, n:q ? q.n : 10, tries:q ? q.tries : 0, ok:passed(e.id), open:isOpen(e.id) };
    if (passed(e.id)) stars++; });
  return { zr:zr, stars:stars };
}
function persist(){
  var js = JSON.stringify(KN.st);
  if (KN.on) { knSend({ type:'store', data:{ zeitreise:js } }); knSend({ type:'award', award:award() }); }
  else try { localStorage.setItem('zeitreise-stand', js); } catch(e){}
}
function applyInit(x){
  KN.on = true; KN.teacher = !!x.teacher;
  var s = x.settings || {};
  if (Array.isArray(s.open)) KN.set.open = s.open;
  if (s.pass) KN.set.pass = +s.pass;
  if (s.auto === false) KN.set.auto = false;
  if (Array.isArray(s.mine)) KN.set.mine = s.mine;
  try { var st = x.store && x.store.zeitreise ? JSON.parse(x.store.zeitreise) : null; if (st && st.v) { KN.st = st; KN.st.visited = st.visited || {}; KN.st.quiz = st.quiz || {}; KN.st.tot = st.tot || {}; } } catch(e){}
}""")
# Zeitstrahl: Schloss-Zustand und Klick
s = rep(s, "  b.addEventListener('click', function(){ travel(e.id); });",
           "  b.addEventListener('click', function(){ if (!isOpen(e.id)) { knToast(lockReason(e.id)); return; } travel(e.id); });")
s = rep(s, "function markEra(id){", """function markLocks(){
  [].forEach.call(document.querySelectorAll('.zs-era'), function(b){
    var id = b.dataset.era, open = isOpen(id); b.classList.toggle('locked', !open);
    b.setAttribute('aria-disabled', open ? 'false' : 'true');
    var l = b.querySelector('.zs-lock'); if (!open && !l) { l = document.createElement('span'); l.className = 'zs-lock'; l.textContent = '🔒'; l.setAttribute('aria-hidden', 'true'); b.insertBefore(l, b.children[1]); }
    if (open && l) l.remove();
    b.title = BY[id].name + ' (' + BY[id].date + ')' + (open ? '' : ' – noch gesperrt');
    var q = KN.st.quiz[id], tot = KN.st.tot[id], fe = document.getElementById('found-' + id);
    if (fe && tot) fe.textContent = (KN.st.visited[id] || []).length + ' / ' + tot + ' entdeckt' + (q ? ' · Quiz ' + q.best + '/' + q.n + (passed(id) ? ' ✓' : '') : '');
  });
}
function markEra(id){""")
# Welten mit Stand laden
s = rep(s, "f.allowFullscreen = true; f.src = BY[id].file;", "f.allowFullscreen = true; f.src = srcFor(id);")
s = rep(s, "function makeFrame(id){", """function srcFor(id){
  if (!KN.on) return BY[id].file;
  return BY[id].file + '?kn=' + encodeURIComponent(JSON.stringify(KN.st.visited[id] || [])) + (KN.st.q ? '&q=' + KN.st.q : '');
}
function makeFrame(id){""")
# Meldungen der Welten
s = rep(s, "  if (d.type === 'found') setFound(id, d.found, d.total);",
"""  if (d.type === 'found') setFound(id, d.found, d.total);
  if ((d.type === 'found' || d.type === 'ready') && d.total) {
    var changed = KN.st.tot[id] !== d.total; KN.st.tot[id] = d.total;
    if (id === cur) { knSend({ type:'level', level:BY[id].name }); knSend({ type:'progress', done:d.found, total:d.total }); }
    if (changed) persist();
    markLocks();
  }
  if (d.type === 'visited' && Array.isArray(d.list)) { KN.st.visited[id] = d.list.slice(0, 500); persist(); markLocks(); }
  if (d.type === 'quiz' && isFinite(d.score)) {
    var nx = BY[id].index + 1 < ERAS.length ? ERAS[BY[id].index + 1] : null, before = nx ? isOpen(nx.id) : true;
    var q = KN.st.quiz[id] || { best:0, n:d.n || 10, tries:0 };
    q.tries++; q.last = d.score; q.n = d.n || q.n; if (d.score > q.best) q.best = d.score; KN.st.quiz[id] = q;
    persist(); markLocks();
    if (nx && !before && isOpen(nx.id)) knToast('🔓 Super! Die ' + nx.name + ' ist jetzt offen. Tippe oben im Zeitstrahl darauf.');
    else if (nx && !before && nx.ready && d.score < KN.set.pass && KN.set.auto !== false) knToast('Für die ' + nx.name + ' brauchst du mindestens ' + KN.set.pass + ' von 10 Punkten. Versuch es nochmals!');
  }
  if (d.type === 'quality' && (d.v === 'hoch' || d.v === 'schnell')) {
    KN.st.q = d.v; persist();
    if (!KN.on) try { localStorage.setItem(id + '-grafik', d.v); } catch(e){}
    st.ready = false; st.p = 0; frames[id].src = KN.on ? srcFor(id) : BY[id].file;
  }""")
s = rep(s, "function setFound(id, n, total){ var el = document.getElementById('found-' + id); if (el && total) el.textContent = n + ' / ' + total + ' entdeckt'; }",
           "function setFound(id, n, total){ var el = document.getElementById('found-' + id); if (el && total) el.textContent = n + ' / ' + total + ' entdeckt'; if (total) markLocks(); }")
s = rep(s, "function travel(to){\n  if (busy || to === cur || !BY[to]) return;", "function travel(to){\n  if (busy || to === cur || !BY[to] || !isOpen(to)) return;")
s = rep(s, "    cur = to; try { history.replaceState(null, '', '#' + to); } catch(e){ location.hash = to; }",
           "    cur = to; try { history.replaceState(null, '', '#' + to); } catch(e){ location.hash = to; }\n    KN.st.last = to; persist(); knSend({ type:'level', level:BY[to].name }); if (KN.st.tot[to]) knSend({ type:'progress', done:(KN.st.visited[to] || []).length, total:KN.st.tot[to] });")
# Start erst nach dem Stand aus Knobelnest
start_old = """var first = (location.hash || '').replace('#', '');
cur = BY[first] ? first : ERAS[0].id;
var f0 = makeFrame(cur); f0.classList.add('on'); markEra(cur); updateZs();
f0.addEventListener('load', function(){ try { f0.focus(); } catch(e){} });
window.addEventListener('hashchange', function(){ var h = location.hash.replace('#', ''); if (BY[h] && h !== cur) travel(h); });"""
start_new = """function boot(){
  if (!KN.on) try { var ls = JSON.parse(localStorage.getItem('zeitreise-stand') || 'null'); if (ls && ls.v) KN.st = ls; } catch(e){}
  markLocks();
  var first = (location.hash || '').replace('#', ''), opts = ERAS.filter(function(e){ return isOpen(e.id); });
  if (!opts.length) { document.getElementById('knEmpty').classList.add('on'); return; }
  cur = isOpen(first) ? first : isOpen(KN.st.last) ? KN.st.last : opts[opts.length - 1].id;
  var f0 = makeFrame(cur); f0.classList.add('on'); markEra(cur); updateZs();
  f0.addEventListener('load', function(){ try { f0.focus(); } catch(e){} });
  knSend({ type:'level', level:BY[cur].name });
  window.addEventListener('hashchange', function(){ var h = location.hash.replace('#', ''); if (BY[h] && h !== cur) { if (isOpen(h)) travel(h); else knToast(lockReason(h)); } });
}
if (window.parent !== window) {
  var booted = false;
  window.addEventListener('message', function(ev){
    var d = ev.data; if (booted || ev.source !== parent || !d || !d.knobelnestInit) return;
    booted = true; applyInit(d.knobelnestInit); boot();
  });
  knSend({ type:'hello' });
  setTimeout(function(){ if (!booted) { booted = true; boot(); } }, 2500);
} else boot();"""
s = rep(s, start_old, start_new)
open(os.path.join(dst, 'index.html'), 'w', encoding='utf-8').write(lokal(s, '../'))
print('ok', sorted(os.listdir(dst)), len(os.listdir(os.path.join(dst, 'bilder'))))
