# Baut die Knobelspiele der Klassenkiste: Rechen-Rakete, Wort-Raten, Bilderrätsel, Eulen-Weg, weitere (weitere.py) und Im Museum (museum.py).
# Aufruf im Repo-Hauptordner:  python3 werkstatt/spiele/knobelspiele/bauen.py
#
# Ergebnis:
#   knobelspiele/<spiel>.html   die Spiele (liegen auf GitHub Pages, Stil der Eulenkiste)
#   knobelspiele/knobelspiele-spielpaket.json   Paket zum Importieren (Verwaltung → «Spielpaket importieren», nur kurze Verweise)
#
# Wie die Gedächtniskiste: In der Tabelle «games» steht pro Spiel nur ein Verweis (<meta name="knobelnest-url" content="knobelspiele/…">).
# Verbesserungen kommen also über GitHub (dann KS_VER in app.js erhöhen), ohne neues Hochladen.
# Rahmen (Stufen-Menü, Sterne, Ton, Meldungen an das Portal) und Stil kommen aus werkstatt/spiele/gedaechtnis/bauen.py.
import importlib.util, json, os, sys
sys.dont_write_bytecode = True

HIER = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HIER, '..', '..', '..'))
ZIEL = os.path.join(REPO, 'knobelspiele')

_spec = importlib.util.spec_from_file_location('gd_bauen', os.path.join(REPO, 'werkstatt', 'spiele', 'gedaechtnis', 'bauen.py'))
GD = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(GD)
sys.path.insert(0, HIER)
from bilder import BILDER

# Spielstand unter eigenem Namen («ks» statt «gd»)
FRAME = GD.FRAME.replace("data: { gd: s }", "data: { ks: s }").replace("localStorage.setItem('gd', s)", "localStorage.setItem('ks', s)") \
    .replace("x.store && x.store.gd", "x.store && x.store.ks").replace("localStorage.getItem('gd')", "localStorage.getItem('ks')")
assert FRAME.count("ks") >= 4
# Mehr Stufenfarben (Kleiderschrank hat 8 Stufen)
FRAME = FRAME.replace("var LV_COL = ['#e9f1e3', '#dcf0fd', '#fbf3dc', '#fcefed', '#efe7f7'];", "var LV_COL = ['#e9f1e3', '#dcf0fd', '#fbf3dc', '#fcefed', '#efe7f7', '#fdebd8', '#e3f1f0', '#f3e9dc'];")
assert "'#fdebd8'" in FRAME

SPIELE = []

def spiel(**s):
    SPIELE.append(s)


# ================================================================== Rechen-Rakete
spiel(id='rechen-rakete', titel='Rechen-Rakete', icon='🚀', fach='Mathematik', thema='Kopfrechnen', stufe='1.–6. Klasse', sort=1, n=10,
      sterne={'modus': 'runde', 'n': 10},
      kurz='Rechnen und mit der Rakete zum Mond fliegen.',
      intro='Tippe auf das richtige Ergebnis. Bei jeder Rechnung fliegt die Rakete ein Stück höher, bis zum Mond!',
      levels=[dict(name='Leicht', info='Plus und Minus bis 10', t=0),
              dict(name='Gut', info='Plus und Minus bis 20', t=1),
              dict(name='Mittel', info='Einmaleins', t=2),
              dict(name='Schwer', info='Plus und Minus bis 100', t=3),
              dict(name='Profi', info='Mal, geteilt und bis 1000', t=4)],
      css=r"""
.rk{display:flex;gap:22px;align-items:center;justify-content:center;width:100%;max-width:860px}
.all{position:relative;flex:none;width:150px;height:min(58vh,470px);border-radius:28px;overflow:hidden;border:3px solid var(--gold);box-shadow:var(--sch);
  background:radial-gradient(2px 2px at 20% 30%,#fff 50%,transparent 51%),radial-gradient(2px 2px at 70% 15%,#fff 50%,transparent 51%),radial-gradient(1.5px 1.5px at 40% 60%,#fff 50%,transparent 51%),
  radial-gradient(2px 2px at 80% 50%,#fff 50%,transparent 51%),radial-gradient(1.5px 1.5px at 30% 85%,#fff 50%,transparent 51%),linear-gradient(180deg,#1d3557 0%,#2f5f8f 60%,#8ec5ec 100%)}
.mond{position:absolute;top:8px;left:50%;transform:translateX(-50%);font-size:46px;line-height:1}
.rakete{position:absolute;left:50%;bottom:calc(8px + var(--p,0) * (100% - 112px));transform:translateX(-50%) rotate(-45deg);font-size:46px;line-height:1;transition:bottom .7s cubic-bezier(.3,1.3,.5,1)}
.rakete.wackel{animation:wk .5s}
@keyframes wk{25%{transform:translateX(-62%) rotate(-55deg)}75%{transform:translateX(-38%) rotate(-35deg)}}
.spur i{position:absolute;left:14px;bottom:calc(26px + var(--p) * (100% - 112px));width:12px;height:12px;border-radius:50%;background:rgba(255,255,255,.3);transition:background .3s}
.spur i.ok{background:var(--gold);box-shadow:0 0 10px #ffd76a}.spur i.no{background:#e58b84}
.pult{display:flex;flex-direction:column;align-items:center;gap:16px;flex:1;max-width:520px}
.uhr{color:var(--soft);font-size:20px}
.auf{font-size:clamp(46px,9vw,76px);background:#fff;border:2px solid var(--line);border-radius:26px;padding:8px 30px;box-shadow:var(--sch);text-align:center;white-space:nowrap;line-height:1.25}
.auf b{font-weight:400;color:var(--sky-d)}
.opts{display:grid;grid-template-columns:1fr 1fr;gap:14px;width:100%}
.opts button{font-size:clamp(34px,7vw,54px);min-height:86px;border-radius:22px;background:#fff;border:2px solid var(--ink);box-shadow:var(--sch-k);transition:transform .12s}
.opts button:active{transform:scale(.96)}
.opts button.ok{background:#e7f3df;border-color:var(--ok)}.opts button.no{background:#fbe5e2;border-color:var(--no)}.opts button.hint{background:var(--sun);border-color:var(--gold)}
@media (max-width:640px){.rk{flex-direction:column;gap:14px}.all{width:100%;height:96px}
  .mond{top:50%;left:auto;right:10px;transform:translateY(-50%)}
  .rakete{bottom:50%;left:calc(8px + var(--p,0) * (100% - 112px));transform:translateY(50%) rotate(45deg);transition:left .7s cubic-bezier(.3,1.3,.5,1)}
  @keyframes wk{25%{transform:translateY(40%) rotate(35deg)}75%{transform:translateY(60%) rotate(55deg)}}
  .spur i{left:calc(26px + var(--p) * (100% - 112px));bottom:8px}.opts button{min-height:72px}}
""",
      js=r"""
// Eine Aufgabe für die Stufe: { q: Text, a: Ergebnis, near: ähnliche falsche Ergebnisse }
function aufgabe(t) {
  var a, b, r, near = [];
  function plus(max, min) { do { a = rnd(min || 1, max - 1); b = rnd(1, max - a); } while (a + b < (min || 2)); return { q: a + ' + ' + b, a: a + b }; }
  function minus(max, min) { a = rnd(min || 2, max); b = rnd(1, a - 1); return { q: a + ' − ' + b, a: a - b }; }
  function mal(x, y) { return { q: x + ' · ' + y, a: x * y, near: [(x + 1) * y, (x - 1) * y, x * (y + 1), x * (y - 1)] }; }
  function durch(x, y) { return { q: (x * y) + ' : ' + y, a: x, near: [x + 1, x - 1, x + 2, y] }; }
  if (t === 0) r = Math.random() < .55 ? plus(10) : minus(10);
  else if (t === 1) { do { r = Math.random() < .5 ? plus(20, 11) : minus(20, 11); } while (r.a > 20); }
  else if (t === 2) r = mal(rnd(2, 10), rnd(2, 10));
  else if (t === 3) {
    if (Math.random() < .5) { a = rnd(12, 88); b = rnd(5, 99 - a); r = { q: a + ' + ' + b, a: a + b }; }
    else { a = rnd(25, 100); b = rnd(5, a - 3); r = { q: a + ' − ' + b, a: a - b }; }
    near = [r.a + 10, r.a - 10, r.a + 1, r.a - 1];
  } else {
    var w = rnd(0, 3);
    if (w === 0) r = mal(rnd(3, 10), rnd(3, 10));
    else if (w === 1) r = durch(rnd(2, 10), rnd(3, 10));
    else if (w === 2) { a = rnd(11, 19); b = rnd(2, 5); r = mal(a, b); }
    else { a = rnd(12, 88) * 10; b = rnd(5, 40) * 10; if (Math.random() < .5 && a + b <= 1000) r = { q: a + ' + ' + b, a: a + b }; else { if (b > a) { var z = a; a = b; b = z; } r = { q: a + ' − ' + b, a: a - b }; } near = [r.a + 100, r.a - 100, r.a + 10, r.a - 10]; }
  }
  r.near = (r.near || []).concat(near, [r.a + 1, r.a - 1, r.a + 2, r.a - 2, r.a + 10, r.a - 10]);
  return r;
}
function wahl(r) {
  var o = [r.a], cand = shuffle(r.near.slice(0, 4)).concat(r.near.slice(4));
  cand.forEach(function (x) { if (o.length < 4 && x >= 0 && o.indexOf(x) < 0) o.push(x); });
  var k = 3; while (o.length < 4) { if (o.indexOf(r.a + k) < 0) o.push(r.a + k); k++; }
  return shuffle(o);
}
G.play = function (lv, api, li) {
  var n = G.n, k = 0, right = 0, lock = false, t0 = Date.now(), fertig = false, last = '';
  var w = document.createElement('div'); w.className = 'rk';
  var marks = ''; for (var i = 0; i < n; i++) marks += '<i style="--p:' + ((i + 1) / n) + '"></i>';
  w.innerHTML = '<div class="all"><span class="mond">🌕</span><div class="spur">' + marks + '</div><span class="rakete" style="--p:0">🚀</span></div>' +
    '<div class="pult"><div class="uhr"></div><div class="auf"></div><div class="opts"></div></div>';
  api.stage.appendChild(w);
  var rak = w.querySelector('.rakete'), uhr = w.querySelector('.uhr'), auf = w.querySelector('.auf'), opts = w.querySelector('.opts'), dots = w.querySelectorAll('.spur i');
  var rec = (ST.best || {})['rakete' + li];
  function zeit(ms) { var s = Math.round(ms / 1000); return Math.floor(s / 60) + ':' + ('0' + s % 60).slice(-2); }
  function tick() { if (fertig) return; uhr.textContent = '⏱ Flugzeit ' + zeit(Date.now() - t0) + (rec ? ' · Rekord ' + zeit(rec) : ''); api.later(tick, 500); }
  tick();
  api.msg('<span class="em">🧑‍🚀</span> Rechne und flieg zum Mond!');
  function next() {
    var r; do { r = aufgabe(lv.t); } while (r.q === last); last = r.q;
    auf.innerHTML = h(r.q) + ' = <b>?</b>'; opts.innerHTML = '';
    wahl(r).forEach(function (x) {
      var b = document.createElement('button'); b.textContent = x;
      b.onclick = function () {
        if (lock) return; lock = true;
        var ok = x === r.a;
        b.classList.add(ok ? 'ok' : 'no');
        if (!ok) { Array.prototype.forEach.call(opts.children, function (c) { if (+c.textContent === r.a) c.classList.add('hint'); }); rak.classList.remove('wackel'); void rak.offsetWidth; rak.classList.add('wackel'); }
        auf.innerHTML = h(r.q) + ' = <b>' + r.a + '</b>';
        dots[k].classList.add(ok ? 'ok' : 'no'); k++; if (ok) right++;
        rak.style.setProperty('--p', k / n);
        api.msg(ok ? '<span class="em">' + pick(['🚀', '✨', '🌟', '💫'], 1)[0] + '</span> ' + pick(['Richtig!', 'Super!', 'Toll!', 'Genau!'], 1)[0] : '<span class="em">💡</span> Fast! Richtig ist <b>' + r.a + '</b>.');
        var weiter = api.answer(ok);
        if (!weiter) {
          fertig = true; var ms = Date.now() - t0, line = '';
          if (right === n) { var b2 = api.best('rakete' + li, ms, true); line = b2.rec && b2.old ? ' Neuer Rekord: ' + zeit(ms) + '!' : ' Flugzeit ' + zeit(ms) + '.'; }
          api.msg('<span class="em">🌕</span> Gelandet!' + line);
          return;
        }
        api.later(function () { lock = false; next(); }, ok ? 700 : 1700);
      };
      opts.appendChild(b);
    });
  }
  next();
};
""")


# ================================================================== Wort-Raten
W4 = [('BALL','⚽'),('BAUM','🌳'),('HAUS','🏠'),('HUND','🐶'),('MAUS','🐭'),('BOOT','⛵'),('BROT','🍞'),('BUCH','📖'),('EULE','🦉'),('HAHN','🐓'),
      ('HASE','🐰'),('HERZ','❤️'),('HOSE','👖'),('IGEL','🦔'),('KÄSE','🧀'),('LAMM','🐑'),('LÖWE','🦁'),('MOND','🌙'),('NASE','👃'),('PILZ','🍄'),
      ('RING','💍'),('ROSE','🌹'),('ZAHN','🦷'),('ZELT','⛺'),('AUTO','🚗'),('AFFE','🐒'),('BETT','🛏️'),('HAND','✋'),('KIWI','🥝'),('NUSS','🌰'),
      ('ENTE','🦆'),('WOLF','🐺'),('GELD','💰'),('HUHN','🐔'),('FUSS','🦶'),('BEIN','🦵'),('KUSS','😘'),('KUCHEN','')]
W4 = [w for w in W4 if len(w[0]) == 4]
W4X = ['GRAS','WALD','BERG','GELB','BLAU','KALT','WARM','LAUT','ZEIT','WORT','BILD','LIED','TANZ','MUND','KOPF','SAND','WIND','HAAR','LUFT','WEIT',
       'FROH','BUNT','FELD','HOLZ','GLAS','KORB','MEER','REIS','TIER','BACH','TURM','HEFT','SPUR','KERN','DACH','ZAUN','TOPF','SEIL','HELM','PARK']
W5 = [('APFEL','🍎'),('BIRNE','🍐'),('SONNE','☀️'),('STERN','⭐'),('TIGER','🐯'),('KATZE','🐱'),('FUCHS','🦊'),('FISCH','🐟'),('SCHAF','🐑'),('ZEBRA','🦓'),
      ('PFERD','🐴'),('BIENE','🐝'),('KRONE','👑'),('KERZE','🕯️'),('LAMPE','💡'),('MILCH','🥛'),('BLUME','🌸'),('BLATT','🍃'),('REGEN','🌧️'),('SCHUH','👟'),
      ('GABEL','🍴'),('PIZZA','🍕'),('TORTE','🎂'),('GEIGE','🎻'),('KÄFER','🐞'),('KAMEL','🐫'),('PANDA','🐼'),('KOALA','🐨'),('HONIG','🍯'),('KREBS','🦀'),
      ('WOLKE','☁️'),('BLITZ','⚡'),('JACKE','🧥'),('MÜTZE','🧢'),('SOCKE','🧦'),('STUHL','🪑'),('SCHAL','🧣'),('BRIEF','✉️'),('VOGEL','🐦'),('TASSE','☕')]
W5X = ['LESEN','MALEN','SPIEL','PAUSE','KREIS','NACHT','ABEND','WOCHE','FARBE','LEISE','STARK','KLEIN','NEBEL','INSEL','STEIN','PLATZ','STADT','KISTE',
       'TEICH','OTTER','FEDER','ZWERG','RIESE','KÖNIG','STIFT','TISCH','TAFEL','LACHE','FREUD','DRACHE','TRAUM','HÖHLE','PIRAT','PRINZ','GURKE','FEUER','WIESE','SCHAU','FLUSS','BRÜLL']
W5X = [w for w in W5X if len(w) == 5 and w not in ('FREUD', 'BRÜLL', 'SCHAU', 'LACHE')]
W6 = ['GARTEN','SCHULE','FREUND','BANANE','RAKETE','DRACHE','SCHIFF','BRILLE','GLOCKE','KUCHEN','MORGEN','LUSTIG','BRÜCKE','KREIDE','WINTER','SOMMER',
      'HERBST','PINSEL','SCHERE','KOFFER','KISSEN','HIMMEL','WASSER','SCHNEE','ZAUBER','RITTER','SCHATZ','TUNNEL','ZIRKUS','LÖFFEL','MESSER','TELLER',
      'KÜRBIS','TOMATE','BUTTER','RÄTSEL','LACHEN','SINGEN','TANZEN','ROLLER','PAPIER','KÄSTLI']
W6 = [w for w in W6 if len(w) == 6 and w != 'KÄSTLI']
for _w in [x[0] for x in W4] + W4X + [x[0] for x in W5] + W5X + W6:
    assert 'ß' not in _w and _w.isupper(), _w

spiel(id='wort-raten', titel='Wort-Raten', icon='🔤', fach='Deutsch', thema='Wörter', stufe='2.–6. Klasse', sort=1, n=5,
      sterne={'modus': 'runde', 'n': 5},
      kurz='Ein geheimes Wort in sechs Versuchen erraten.',
      intro='Errate das geheime Wort! Nach jedem Versuch zeigen die Farben: <b style="color:#4c8a37">grün</b> = richtiger Platz, <b style="color:#b8892a">gelb</b> = kommt vor, aber an einem anderen Platz.',
      levels=[dict(name='Leicht', info='4 Buchstaben, mit Bild', L=4, bild=True),
              dict(name='Gut', info='4 Buchstaben', L=4, bild=False),
              dict(name='Mittel', info='5 Buchstaben, mit Bild', L=5, bild=True),
              dict(name='Schwer', info='5 Buchstaben', L=5, bild=False),
              dict(name='Profi', info='6 Buchstaben', L=6, bild=False)],
      daten={'W4': W4, 'W4X': W4X, 'W5': W5, 'W5X': W5X, 'W6': W6},
      css=r"""
.wr{display:flex;flex-direction:column;align-items:center;gap:10px;width:100%}
.wr .bild{font-size:52px;line-height:1;background:#fff;border:3px solid var(--gold);border-radius:50%;width:84px;height:84px;display:grid;place-items:center;box-shadow:inset 0 0 0 5px #fff,var(--sch-k)}
.brett{display:grid;gap:6px}
.zeile{display:grid;gap:6px}
.zeile.shake{animation:sh .35s}
.fe{display:grid;place-items:center;background:#fff;border:2px solid var(--line2);border-radius:12px;font-family:system-ui,-apple-system,sans-serif;font-weight:700;text-transform:uppercase;line-height:1}
.fe.voll{border-color:#7d8a96;animation:pp .15s}
.fe.g,.fe.y,.fe.x{color:#fff;animation:dreh .45s backwards}
.fe.g{background:#5f9a4a;border-color:#4c8a37}.fe.y{background:#d6ad45;border-color:#b8892a}.fe.x{background:#9aa5ad;border-color:#87929a}
@keyframes dreh{0%{transform:rotateX(90deg)}100%{transform:rotateX(0)}}
.tast{display:flex;flex-direction:column;gap:6px;width:100%;max-width:620px;margin-top:4px}
.tast div{display:flex;gap:5px;justify-content:center}
.tast button{flex:1;max-width:52px;min-width:0;height:52px;border-radius:10px;background:#fff;border:1.5px solid var(--line2);box-shadow:0 2px 0 var(--line2);font:700 19px system-ui,-apple-system,sans-serif;padding:0}
.tast button.w{max-width:84px;flex:1.6;font-size:16px}
.tast button.g{background:#5f9a4a;color:#fff;border-color:#4c8a37}.tast button.y{background:#d6ad45;color:#fff;border-color:#b8892a}.tast button.x{background:#c9d1d6;color:#fff;border-color:#b5bec4}
.tast button:active{transform:translateY(2px);box-shadow:none}
@media (max-height:760px){.wr .bild{width:64px;height:64px;font-size:38px}.tast button{height:46px}}
""",
      js=r"""
G.play = function (lv, api) {
  var L = lv.L, list, MAXV = 6, myRun = RUN;
  if (L === 4) list = lv.bild ? D.W4 : D.W4.concat(D.W4X.map(function (w) { return [w, '']; }));
  else if (L === 5) list = lv.bild ? D.W5 : D.W5.concat(D.W5X.map(function (w) { return [w, '']; }));
  else list = D.W6.map(function (w) { return [w, '']; });
  var runde = pick(list, G.n), idx = 0;
  var wrap = document.createElement('div'); wrap.className = 'wr'; api.stage.appendChild(wrap);
  var KEYS = ['QWERTZUIOPÜ', 'ASDFGHJKLÖÄ', '⏎YXCVBNM⌫'];
  function wort() {
    var w = runde[idx][0].split(''), em = runde[idx][1], v = 0, cur = [], lock = false, stat = {};
    var avW = Math.min(window.innerWidth - 32, 520), avH = window.innerHeight - (lv.bild ? 400 : 310);
    var s = Math.max(34, Math.floor(Math.min(64, (avW - (L - 1) * 6) / L, (avH - 5 * 6) / MAXV)));
    wrap.innerHTML = (lv.bild ? '<div class="bild" aria-label="Bild-Tipp">' + em + '</div>' : '') + '<div class="brett"></div><div class="tast"></div>';
    var brett = wrap.querySelector('.brett'), tast = wrap.querySelector('.tast'), rows = [];
    for (var r = 0; r < MAXV; r++) {
      var z = document.createElement('div'); z.className = 'zeile'; z.style.gridTemplateColumns = 'repeat(' + L + ',' + s + 'px)';
      for (var c = 0; c < L; c++) { var f = document.createElement('div'); f.className = 'fe'; f.style.cssText = 'width:' + s + 'px;height:' + s + 'px;font-size:' + Math.round(s * .55) + 'px'; z.appendChild(f); }
      brett.appendChild(z); rows.push(z);
    }
    tast.innerHTML = KEYS.map(function (row) { return '<div>' + row.split('').map(function (k) {
      return k === '⏎' ? '<button class="w" data-k="ok">Prüfen</button>' : k === '⌫' ? '<button class="w" data-k="del" aria-label="Löschen">⌫</button>' : '<button data-k="' + k + '">' + k + '</button>'; }).join('') + '</div>'; }).join('');
    api.msg('<span class="em">🔎</span> Wort ' + (idx + 1) + ' von ' + G.n + ': Welches Wort mit ' + L + ' Buchstaben ist es?');
    function show() { var f = rows[v].children; for (var c = 0; c < L; c++) { f[c].textContent = cur[c] || ''; f[c].classList.toggle('voll', !!cur[c]); } }
    function score(g) {
      var res = [], rest = {};
      for (var i = 0; i < L; i++) { if (g[i] === w[i]) res[i] = 'g'; else { res[i] = 'x'; rest[w[i]] = (rest[w[i]] || 0) + 1; } }
      for (i = 0; i < L; i++) if (res[i] !== 'g' && rest[g[i]] > 0) { res[i] = 'y'; rest[g[i]]--; }
      return res;
    }
    function key(k) {
      if (lock || RUN !== myRun) return;
      if (k === 'del') { cur.pop(); show(); return; }
      if (k === 'ok') {
        if (cur.length < L) { rows[v].classList.remove('shake'); void rows[v].offsetWidth; rows[v].classList.add('shake'); api.msg('<span class="em">✏️</span> Es braucht ' + L + ' Buchstaben.'); return; }
        var res = score(cur), f = rows[v].children, rank = { x: 1, y: 2, g: 3 };
        for (var i = 0; i < L; i++) { f[i].style.animationDelay = (i * 0.12) + 's'; f[i].classList.add(res[i]); var o = stat[cur[i]]; if (!o || rank[res[i]] > rank[o]) stat[cur[i]] = res[i]; }
        lock = true;
        api.later(function () {
          Array.prototype.forEach.call(tast.querySelectorAll('[data-k]'), function (b) { var st = stat[b.dataset.k]; if (st) { b.classList.remove('g', 'y', 'x'); b.classList.add(st); } });
          var won = res.every(function (x) { return x === 'g'; });
          v++; cur = [];
          if (won || v >= MAXV) {
            var lob = ['Super!', 'Toll!', 'Genial!', 'Bravo!', 'Klasse!', 'Stark!'][v - 1] || 'Geschafft!';
            api.msg(won ? '<span class="em">🎉</span> ' + lob + ' Das Wort heisst <b>' + w.join('') + '</b> ' + (em ? '<span class="em">' + em + '</span>' : '') :
              '<span class="em">💡</span> Das Wort heisst <b>' + w.join('') + '</b> ' + (em ? '<span class="em">' + em + '</span>' : ''));
            if (!won) { var z = rows[MAXV - 1]; z.classList.remove('shake'); void z.offsetWidth; z.classList.add('shake'); }
            if (api.answer(won)) {
              var nb = document.createElement('button'); nb.className = 'go sun'; nb.textContent = 'Nächstes Wort →';
              nb.onclick = function () { idx++; wort(); };
              tast.className = 'row'; tast.innerHTML = ''; tast.appendChild(nb);
            } else tast.innerHTML = '';
            return;
          }
          lock = false;
          api.msg('<span class="em">🤔</span> Noch ' + (MAXV - v) + (MAXV - v === 1 ? ' Versuch.' : ' Versuche.'));
        }, L * 120 + 450);
        return;
      }
      if (cur.length < L) { cur.push(k); show(); tone(560 + cur.length * 40, 0.05, 'sine', 0.08); }
    }
    tast.onclick = function (e) { var b = e.target.closest('[data-k]'); if (b) key(b.dataset.k); };
    function phys(e) {
      if (RUN !== myRun) { document.removeEventListener('keydown', phys); return; }
      if (e.metaKey || e.ctrlKey || e.altKey) return;
      var k = e.key;
      if (k === 'Enter') key('ok'); else if (k === 'Backspace') key('del');
      else if (k && k.length === 1 && /[a-zäöü]/i.test(k)) key(k.toUpperCase());
    }
    document.removeEventListener('keydown', window.__wrKey || function () {}); window.__wrKey = phys;
    document.addEventListener('keydown', phys);
  }
  wort();
};
""")


# ================================================================== Bilderrätsel (Nonogramm)
def nono_level(n):
    return [{'n': b[0], 'e': b[1], 'c': b[2], 'p': b[3].split('\n')} for b in BILDER[n]]

spiel(id='bilderraetsel', titel='Bilderrätsel', icon='🖼️', fach='Knobeln', thema='Logik', stufe='2.–6. Klasse', sort=1, n=3,
      sterne={'modus': 'runde', 'n': 3},
      kurz='Felder nach Zahlen ausmalen, bis ein Bild erscheint.',
      intro='Die Zahlen sagen, wie viele Felder in einer Reihe nebeneinander ausgemalt sind. «2 1» heisst: zuerst 2 Felder, dann eine Lücke, dann 1 Feld. Male so lange, bis ein Bild erscheint!',
      levels=[dict(name='Leicht', info='5 × 5 Felder', s=5, hilfe=True, bilder=nono_level(5)),
              dict(name='Gut', info='6 × 6 Felder', s=6, hilfe=True, bilder=nono_level(6)),
              dict(name='Mittel', info='8 × 8 Felder', s=8, hilfe=True, bilder=nono_level(8)),
              dict(name='Schwer', info='10 × 10 Felder', s=10, hilfe=True, bilder=nono_level(10)),
              dict(name='Profi', info='10 × 10 Felder, ohne Hilfe', s=10, hilfe=False, bilder=nono_level(10))],
      css=r"""
.nn-werk{display:flex;gap:10px;align-items:center;flex-wrap:wrap;justify-content:center}
.nn-werk .go{min-height:50px;font-size:21px;padding:4px 18px}
.nn-werk .go[aria-pressed="true"]{background:var(--sun);border-color:var(--gold-d);box-shadow:inset 0 0 0 2px var(--gold)}
.nn-werk .go[aria-pressed="false"]{background:#fff;box-shadow:none;opacity:.8}
.herzen{font-size:26px;letter-spacing:2px}
.nn{display:grid;touch-action:none;background:#fff;border:2px solid var(--line);border-radius:18px;padding:8px;box-shadow:var(--sch)}
.nn .hz{display:flex;flex-direction:column;justify-content:flex-end;align-items:center;color:var(--sky-d);line-height:1.05;padding-bottom:4px}
.nn .hs{display:flex;justify-content:flex-end;align-items:center;gap:.35em;color:var(--sky-d);padding-right:6px;white-space:nowrap}
.nn .hz.fertig,.nn .hs.fertig{color:#c3ccd3}
.nn .hz:nth-of-type(even){background:#f4f9fd;border-radius:8px 8px 0 0}
.nn .z{border:1px solid #c5d8e8;background:#fff;display:grid;place-items:center;color:#9aa5ad;line-height:1;transition:background .15s}
.nn .z.v{background:#2c3e50}
.nn .z.k::after{content:"✕"}
.nn .z.f{background:#fbe5e2;color:var(--no)}.nn .z.f::after{content:"✕"}
.nn .z.r5{border-right:2px solid #7d8a96}.nn .z.b5{border-bottom:2px solid #7d8a96}
.nn.fertig .z{border-color:transparent;transition:background .5s,border-color .5s}
.nn.fertig .z.k::after,.nn.fertig .z.f::after{content:""}
.nn.fertig .z.f{background:#fff}
.nn .z.lz{background:#e9f1e3}
""",
      js=r"""
G.play = function (lv, api) {
  var bilder = pick(lv.bilder, G.n), idx = 0, modus = 'malen';
  function runs(a) { var r = [], c = 0; a.forEach(function (x) { if (x) c++; else if (c) { r.push(c); c = 0; } }); if (c) r.push(c); return r.length ? r : [0]; }
  function raetsel() {
    var B = bilder[idx], n = B.p.length, sol = B.p.map(function (r) { return r.split('').map(function (c) { return c === '#'; }); });
    var st = sol.map(function (r) { return r.map(function () { return 0; }); }); // 0 leer, 1 richtig gemalt, 2 Kreuz, 3 Fehler
    var rc = sol.map(runs), cc = range(n).map(function (j) { return runs(sol.map(function (r) { return r[j]; })); });
    var mr = Math.max.apply(null, rc.map(function (x) { return x.length; })), mc = Math.max.apply(null, cc.map(function (x) { return x.length; }));
    var fehler = 0, fertig = false;
    var avW = Math.min(window.innerWidth - 40, 760), avH = window.innerHeight - 250;
    var s = Math.floor(Math.min(58, avW / (n + mr * .62 + .4), avH / (n + mc * .78 + .4)));
    s = Math.max(24, s);
    var fs = Math.max(14, Math.round(s * .5));
    api.stage.innerHTML = '';
    var werk = document.createElement('div'); werk.className = 'nn-werk';
    werk.innerHTML = '<button class="go" data-m="malen" aria-pressed="true">■ Malen</button><button class="go" data-m="kreuz" aria-pressed="false">✕ Kreuzchen</button><span class="herzen" aria-label="Herzen"></span>';
    api.stage.appendChild(werk);
    var her = werk.querySelector('.herzen');
    function herzen() { var o = ''; for (var i = 0; i < 3; i++) o += i < 3 - fehler ? '❤️' : '🤍'; her.textContent = o; }
    herzen();
    function setM(m) { modus = m; Array.prototype.forEach.call(werk.querySelectorAll('[data-m]'), function (b) { b.setAttribute('aria-pressed', String(b.dataset.m === m)); }); }
    werk.onclick = function (e) { var b = e.target.closest('[data-m]'); if (b) setM(b.dataset.m); };
    setM(modus);
    var g = document.createElement('div'); g.className = 'nn';
    g.style.gridTemplateColumns = 'auto repeat(' + n + ',' + s + 'px)'; g.style.gridTemplateRows = 'auto repeat(' + n + ',' + s + 'px)'; g.style.fontSize = fs + 'px';
    var o = '<div></div>';
    cc.forEach(function (c, j) { o += '<div class="hz" data-hz="' + j + '">' + c.map(function (x) { return '<span>' + x + '</span>'; }).join('') + '</div>'; });
    for (var i = 0; i < n; i++) {
      o += '<div class="hs" data-hs="' + i + '">' + rc[i].map(function (x) { return '<span>' + x + '</span>'; }).join('') + '</div>';
      for (var j = 0; j < n; j++) o += '<div class="z' + ((j + 1) % 5 === 0 && j < n - 1 ? ' r5' : '') + ((i + 1) % 5 === 0 && i < n - 1 ? ' b5' : '') + '" data-i="' + i + '" data-j="' + j + '" style="font-size:' + Math.round(s * .55) + 'px"></div>';
    }
    g.innerHTML = o;
    api.stage.appendChild(g);
    api.msg('<span class="em">🖼️</span> Bild ' + (idx + 1) + ' von ' + G.n + (lv.hilfe ? '' : ' · <small>ohne Hilfe: Kreuzchen setzt du selbst</small>'));
    function cell(i, j) { return g.querySelector('[data-i="' + i + '"][data-j="' + j + '"]'); }
    function paint(i, j) { var c = cell(i, j), v = st[i][j]; c.className = c.className.replace(/ (v|k|f)\b/g, ''); if (v === 1) c.classList.add('v'); if (v === 2) c.classList.add('k'); if (v === 3) c.classList.add('f'); }
    function zeileFertig(i) { return sol[i].every(function (x, j) { return !x || st[i][j] === 1; }); }
    function spalteFertig(j) { return sol.every(function (r, i) { return !r[j] || st[i][j] === 1; }); }
    function pruef(i, j) {
      if (!lv.hilfe) return;
      if (zeileFertig(i)) { g.querySelector('[data-hs="' + i + '"]').classList.add('fertig'); for (var x = 0; x < n; x++) if (st[i][x] === 0) { st[i][x] = 2; paint(i, x); } }
      if (spalteFertig(j)) { g.querySelector('[data-hz="' + j + '"]').classList.add('fertig'); for (var y = 0; y < n; y++) if (st[y][j] === 0) { st[y][j] = 2; paint(y, j); } }
    }
    var zug = null; // { art: 'malen' | 'kreuz+' | 'kreuz-' }
    function tun(el) {
      if (!el || fertig || !el.dataset || el.dataset.i == null) return;
      var i = +el.dataset.i, j = +el.dataset.j, v = st[i][j];
      if (zug.art === 'malen') {
        if (v !== 0) return;
        if (sol[i][j]) { st[i][j] = 1; paint(i, j); tone(520 + rnd(0, 6) * 30, 0.05, 'sine', 0.07); pruef(i, j); fertigCheck(); }
        else { st[i][j] = 3; paint(i, j); fehler++; herzen(); bad(); el.classList.remove('shake'); void el.offsetWidth; el.classList.add('shake'); zug = null;
          api.msg(fehler < 3 ? '<span class="em">🙈</span> Hoppla, dieses Feld bleibt leer.' : '<span class="em">💪</span> Keine Herzen mehr, aber mal das Bild trotzdem fertig!'); }
      } else if (zug.art === 'kreuz+') { if (v === 0) { st[i][j] = 2; paint(i, j); } }
      else if (zug.art === 'kreuz-') { if (v === 2) { st[i][j] = 0; paint(i, j); } }
    }
    g.addEventListener('pointerdown', function (e) {
      var el = e.target.closest('.z'); if (!el || fertig) return;
      e.preventDefault();
      var v = st[+el.dataset.i][+el.dataset.j];
      zug = { art: modus === 'malen' ? 'malen' : v === 2 ? 'kreuz-' : 'kreuz+' };
      tun(el);
    });
    g.addEventListener('pointermove', function (e) {
      if (!zug) return;
      var el = document.elementFromPoint(e.clientX, e.clientY); if (el && el.closest) el = el.closest('.z');
      if (el && g.contains(el)) tun(el);
    });
    function ende() { zug = null; }
    window.addEventListener('pointerup', ende); window.addEventListener('pointercancel', ende);
    function fertigCheck() {
      for (var i = 0; i < n; i++) for (var j = 0; j < n; j++) if (sol[i][j] && st[i][j] !== 1) return;
      fertig = true; zug = null;
      g.classList.add('fertig');
      Array.prototype.forEach.call(g.querySelectorAll('.hz,.hs'), function (x) { x.classList.add('fertig'); });
      api.later(function () {
        Array.prototype.forEach.call(g.querySelectorAll('.z.v'), function (c) { c.style.background = B.c; });
        api.msg('<span class="em">' + B.e + '</span> Das ist ' + h(B.n) + '!' + (fehler === 0 ? ' Ganz ohne Fehler!' : ''));
        if (api.answer(fehler <= 2)) {
          var nb = document.createElement('button'); nb.className = 'go sun'; nb.textContent = 'Nächstes Bild →';
          nb.onclick = function () { idx++; raetsel(); };
          werk.innerHTML = ''; werk.appendChild(nb);
        } else werk.innerHTML = '';
      }, 350);
    }
  }
  raetsel();
};
""")


# ================================================================== Eulen-Weg (Programmieren)
spiel(id='eulen-weg', titel='Eulen-Weg', icon='🦉', fach='Knobeln', thema='Programmieren', stufe='1.–6. Klasse', sort=2, n=5,
      sterne={'modus': 'runde', 'n': 5},
      kurz='Pfeile legen, damit die Eule nach Hause findet.',
      intro='Lege Pfeil-Karten hintereinander. Dann tippe auf «▶ Los!» und die Eule läuft genau so, wie du es programmiert hast. Findet sie nach Hause?',
      levels=[dict(name='Leicht', info='Pfeile, kleiner Wald', s=4, rel=False, o=2, nuts=0, min=3, max=5, umweg=False),
              dict(name='Gut', info='Pfeile, um Bäume herum', s=5, rel=False, o=6, nuts=0, min=5, max=8, umweg=True),
              dict(name='Mittel', info='Pfeile, Nüsse sammeln', s=5, rel=False, o=4, nuts=2, min=7, max=11, umweg=False),
              dict(name='Schwer', info='Vorwärts und drehen', s=5, rel=True, o=4, nuts=0, min=5, max=9, umweg=False),
              dict(name='Profi', info='Drehen, Nüsse, wenige Karten', s=6, rel=True, o=7, nuts=1, min=8, max=13, umweg=False, knapp=True)],
      css=r"""
.ew{display:flex;gap:22px;align-items:flex-start;justify-content:center;flex-wrap:wrap;width:100%;max-width:1000px}
.wald{position:relative;background:#e9f1e3;border:3px solid #9cc28a;border-radius:20px;box-shadow:var(--sch);flex:none}
.wald .fd{position:absolute;display:grid;place-items:center;line-height:1}
.wald .fd::before{content:"";position:absolute;inset:3px;border-radius:10px;background:rgba(255,255,255,.45)}
.wald .fd span{position:relative}
.wald .eule{position:absolute;display:grid;place-items:center;line-height:1;transition:transform .38s ease;z-index:2;filter:drop-shadow(0 3px 3px rgba(0,0,0,.2))}
.wald .eule.bump{animation:bump .4s}
@keyframes bump{50%{translate:var(--bx) var(--by)}}
.wald .blick{position:absolute;right:-4px;bottom:-4px;width:46%;height:46%;border-radius:50%;background:var(--gold);color:#fff;display:grid;place-items:center;font-size:.42em;font-family:system-ui,sans-serif;font-weight:700;transition:transform .3s}
.wald .weg{opacity:.15;transition:opacity .3s}
.prog{display:flex;flex-direction:column;gap:12px;width:min(100%,400px)}
.streifen{min-height:76px;background:#fff;border:2px dashed var(--line2);border-radius:18px;padding:8px;display:flex;flex-wrap:wrap;gap:6px;align-content:flex-start}
.streifen:empty::before{content:"Hier entsteht dein Programm. Tippe unten auf die Karten.";color:var(--soft);font-size:18px;padding:12px 6px}
.ka{width:54px;height:54px;border-radius:12px;background:var(--sky);border:2px solid var(--sky-d);display:grid;place-items:center;font:700 28px system-ui,sans-serif;color:#1f2421;position:relative}
.ka small{position:absolute;top:1px;left:4px;font-size:11px;color:var(--sky-d)}
.ka.jetzt{background:var(--sun);border-color:var(--gold-d);transform:scale(1.1)}
.ka.falsch{background:#fbe5e2;border-color:var(--no)}
.palette{display:flex;gap:8px;flex-wrap:wrap;justify-content:center}
.palette button{min-width:70px;height:70px;border-radius:16px;background:#fff;border:2px solid var(--ink);box-shadow:var(--sch-k);font:700 30px system-ui,sans-serif;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:0 10px}
.palette button small{font:400 16px "Patrick Hand",cursive}
.palette button:active{transform:translateY(1px)}
.steuer{display:flex;gap:8px;flex-wrap:wrap;justify-content:center}
.steuer .go{min-height:52px;font-size:21px;padding:4px 16px}
.steuer .los{background:#e7f3df;border-color:#3f6b2e;font-size:24px}
.zaehler{text-align:center;color:var(--soft);font-size:18px}
.go:disabled{opacity:.45;cursor:default;transform:none}
""",
      js=r"""
var DX = [0, 1, 0, -1], DY = [-1, 0, 1, 0], PF = ['↑', '→', '↓', '←'];
// Kürzestes Programm suchen (Breitensuche). Gibt die Befehle zurück oder null.
function loese(W) {
  var N = W.s, full = (1 << W.nuts.length) - 1, start = { p: W.start, d: W.rel ? W.dir : 0, m: 0 }, seen = {}, q = [[start, []]];
  function key(x) { return x.p + ',' + x.d + ',' + x.m; }
  seen[key(start)] = 1;
  while (q.length) {
    var it = q.shift(), x = it[0], path = it[1];
    var acts = W.rel ? ['F', 'l', 'r'] : ['U', 'R', 'D', 'L'];
    for (var a = 0; a < acts.length; a++) {
      var y = schritt(W, x, acts[a]); if (!y) continue;
      var np = path.concat([acts[a]]);
      if (y.p === W.goal && y.m === full) return np;
      var k = key(y); if (seen[k]) continue; seen[k] = 1; q.push([y, np]);
    }
  }
  return null;
}
// Ein Befehl: neuer Zustand oder null (Baum, Rand)
function schritt(W, x, a) {
  var N = W.s, d = x.d;
  if (a === 'l') return { p: x.p, d: (d + 3) % 4, m: x.m };
  if (a === 'r') return { p: x.p, d: (d + 1) % 4, m: x.m };
  if (a !== 'F') d = 'URDL'.indexOf(a);
  var cx = x.p % N + DX[d], cy = Math.floor(x.p / N) + DY[d];
  if (cx < 0 || cy < 0 || cx >= N || cy >= N) return null;
  var p = cy * N + cx; if (W.obst.indexOf(p) >= 0) return null;
  var m = x.m, ni = W.nuts.indexOf(p); if (ni >= 0) m |= 1 << ni;
  return { p: p, d: W.rel ? d : 0, m: m };
}
function wald(lv) {
  for (var t = 0; t < 3000; t++) {
    var N = lv.s, sh = shuffle(range(N * N)), W = { s: N, rel: lv.rel, start: sh[0], goal: sh[1], obst: sh.slice(2, 2 + lv.o), nuts: sh.slice(2 + lv.o, 2 + lv.o + lv.nuts), dir: rnd(0, 3) };
    var sp = loese(W); if (!sp || sp.length < lv.min || sp.length > lv.max) continue;
    var man = Math.abs(W.start % N - W.goal % N) + Math.abs(Math.floor(W.start / N) - Math.floor(W.goal / N));
    if (lv.umweg && !lv.rel && sp.length <= man) continue;
    W.best = sp; W.deko = W.obst.map(function () { return Math.random() < .75 ? '🌲' : '🪨'; });
    return W;
  }
  return null;
}
G.play = function (lv, api) {
  var idx = 0;
  function aufgabe() {
    var W = wald(lv), N = W.s, prog = [], laeuft = false, fehl = 0, hilfe = false, gut = false;
    var limit = lv.knapp ? W.best.length + 2 : 24;
    var avW = Math.min(window.innerWidth - 40, 1000), avH = window.innerHeight - 200;
    var s = Math.floor(Math.min(84, avH / N, (avW > 760 ? avW - 440 : avW) / N)); s = Math.max(44, s);
    api.stage.innerHTML = '';
    var box = document.createElement('div'); box.className = 'ew';
    var o = '<div class="wald" style="width:' + (s * N + 6) + 'px;height:' + (s * N + 6) + 'px;font-size:' + Math.round(s * .62) + 'px">';
    for (var p = 0; p < N * N; p++) {
      var ob = W.obst.indexOf(p), nu = W.nuts.indexOf(p), inh = ob >= 0 ? W.deko[ob] : nu >= 0 ? '🌰' : p === W.goal ? '🏠' : '';
      o += '<div class="fd" data-p="' + p + '" style="left:' + (p % N * s) + 'px;top:' + (Math.floor(p / N) * s) + 'px;width:' + s + 'px;height:' + s + 'px"><span>' + inh + '</span></div>';
    }
    o += '<div class="eule" style="width:' + s + 'px;height:' + s + 'px"><span>🦉</span>' + (W.rel ? '<span class="blick">➜</span>' : '') + '</div></div>';
    var pal = W.rel ? [['F', '↑', 'Vor'], ['l', '↶', 'Links'], ['r', '↷', 'Rechts']] : [['U', '↑', ''], ['R', '→', ''], ['D', '↓', ''], ['L', '←', '']];
    o += '<div class="prog"><div class="zaehler"></div><div class="streifen" aria-label="Programm"></div>' +
      '<div class="palette">' + pal.map(function (x) { return '<button data-c="' + x[0] + '" aria-label="' + (x[2] || 'Pfeil ' + x[1]) + '">' + x[1] + (x[2] ? '<small>' + x[2] + '</small>' : '') + '</button>'; }).join('') + '</div>' +
      '<div class="steuer"><button class="go alt" data-x="del">⌫ Zurück</button><button class="go alt" data-x="weg">🗑 Alles weg</button><button class="go los" data-x="los">▶ Los!</button></div></div>';
    box.innerHTML = o; api.stage.appendChild(box);
    var eule = box.querySelector('.eule'), blick = box.querySelector('.blick'), streifen = box.querySelector('.streifen'), zaehler = box.querySelector('.zaehler');
    var Z;
    function zeige(x, sofort) {
      if (sofort) eule.style.transition = 'none';
      eule.style.transform = 'translate(' + (x.p % N * s) + 'px,' + (Math.floor(x.p / N) * s) + 'px)';
      if (blick) blick.style.transform = 'rotate(' + ((x.d + 3) % 4 * 90) + 'deg)';
      if (sofort) { void eule.offsetWidth; eule.style.transition = ''; }
      W.nuts.forEach(function (np, i) { box.querySelector('[data-p="' + np + '"]').classList.toggle('weg', !!(x.m & (1 << i))); });
    }
    function reset() { Z = { p: W.start, d: W.dir, m: 0 }; zeige(Z, true); }
    reset();
    function label(c) { return W.rel ? { F: '↑', l: '↶', r: '↷' }[c] : PF['URDL'.indexOf(c)]; }
    function zeichne() {
      streifen.innerHTML = prog.map(function (c, i) { return '<button class="ka" data-i="' + i + '" aria-label="Karte ' + (i + 1) + ' entfernen"><small>' + (i + 1) + '</small>' + label(c) + '</button>'; }).join('');
      zaehler.textContent = lv.knapp ? 'Karten: ' + prog.length + ' von höchstens ' + limit : prog.length ? prog.length + (prog.length === 1 ? ' Karte' : ' Karten') : '';
    }
    zeichne();
    var ziel = W.nuts.length ? 'Sammle ' + (W.nuts.length === 1 ? 'die Nuss 🌰' : 'alle Nüsse 🌰') + ' und bring die Eule nach Hause 🏠.' : 'Bring die Eule nach Hause 🏠.';
    api.msg('<span class="em">🗺️</span> Weg ' + (idx + 1) + ' von ' + G.n + ': ' + ziel + (W.rel ? ' <small>Der gelbe Pfeil zeigt, wohin die Eule schaut.</small>' : ''));
    function knoepfe() { Array.prototype.forEach.call(box.querySelectorAll('.prog button'), function (b) { b.disabled = laeuft || gut; }); }
    box.querySelector('.prog').onclick = function (e) {
      var b = e.target.closest('button'); if (!b || laeuft || gut) return;
      if (b.dataset.c) { if (prog.length >= limit) { api.msg('<span class="em">✋</span> Mehr Karten gehen nicht. Geht es auch kürzer?'); return; } prog.push(b.dataset.c); tone(600, 0.05, 'sine', 0.08); zeichne(); reset(); }
      else if (b.dataset.i != null) { prog.splice(+b.dataset.i, 1); zeichne(); reset(); }
      else if (b.dataset.x === 'del') { prog.pop(); zeichne(); reset(); }
      else if (b.dataset.x === 'weg') { prog = []; zeichne(); reset(); }
      else if (b.dataset.x === 'los') los();
      else if (b.dataset.x === 'tipp') { hilfe = true; prog = W.best.slice(); zeichne(); reset(); b.remove(); api.msg('<span class="em">💡</span> So geht es. Tippe auf «▶ Los!».'); }
    };
    function los() {
      if (!prog.length) { api.msg('<span class="em">👇</span> Lege zuerst Karten.'); return; }
      laeuft = true; knoepfe(); reset();
      var full = (1 << W.nuts.length) - 1, i = 0;
      function weiter() {
        var ks = streifen.children;
        Array.prototype.forEach.call(ks, function (k) { k.classList.remove('jetzt'); });
        if (i >= prog.length) return fertig(false, Z.p === W.goal ? 'nuss' : 'kurz');
        ks[i].classList.add('jetzt');
        var y = schritt(W, Z, prog[i]);
        if (!y) {
          ks[i].classList.add('falsch');
          var d = prog[i] === 'F' ? Z.d : 'URDL'.indexOf(prog[i]);
          eule.style.setProperty('--bx', (DX[d] * s * .3) + 'px'); eule.style.setProperty('--by', (DY[d] * s * .3) + 'px');
          eule.classList.remove('bump'); void eule.offsetWidth; eule.classList.add('bump'); tone(160, 0.25, 'triangle', 0.18);
          return fertig(false, 'bumm');
        }
        Z = y; zeige(Z); tone(440 + i * 20, 0.06, 'sine', 0.06); i++;
        if (Z.p === W.goal && Z.m === full) return api.later(function () { fertig(true); }, 420);
        api.later(weiter, 470);
      }
      api.later(weiter, 200);
    }
    function fertig(ok, warum) {
      if (ok) {
        gut = true; laeuft = false; knoepfe();
        var richtig = fehl <= 1 && !hilfe;
        api.msg(hilfe ? '<span class="em">🏠</span> Die Eule ist zu Hause. Beim nächsten Weg schaffst du es selbst!' :
          '<span class="em">🎉</span> Die Eule ist zu Hause!' + (fehl === 0 ? ' Beim ersten Versuch!' : ''));
        box.querySelector('.fd[data-p="' + W.goal + '"] span').textContent = '🏡';
        if (api.answer(richtig)) {
          var nb = document.createElement('button'); nb.className = 'go sun'; nb.textContent = 'Nächster Weg →';
          nb.onclick = function () { idx++; aufgabe(); };
          box.querySelector('.steuer').innerHTML = ''; box.querySelector('.steuer').appendChild(nb);
        } else box.querySelector('.steuer').innerHTML = '';
        return;
      }
      fehl++;
      api.msg(warum === 'bumm' ? '<span class="em">💥</span> Autsch! Da geht es nicht weiter. Ändere die rote Karte.' :
        warum === 'nuss' ? '<span class="em">🌰</span> Zu Hause, aber es fehlen noch Nüsse!' : '<span class="em">🤔</span> Die Eule ist noch nicht zu Hause. Es fehlen Karten.');
      api.later(function () {
        laeuft = false; reset(); knoepfe();
        if (fehl >= 3 && !hilfe && !box.querySelector('[data-x="tipp"]')) {
          var t = document.createElement('button'); t.className = 'go alt'; t.dataset.x = 'tipp'; t.textContent = '💡 Lösung zeigen';
          box.querySelector('.steuer').appendChild(t);
        }
      }, 1300);
    }
  }
  aufgabe();
};
""")


# ================================================================== Zweite Lieferung (weitere.py)
import weitere
weitere.alle(spiel)

# ================================================================== Kleiderschrank (Englisch, kleider.py)
import kleider
kleider.alle(spiel)


# ================================================================== Im Museum (Englisch, museum.py)
import museum
museum.alle(spiel)


# ------------------------------------------------------------------ Prüfen und bauen
def runs(line):
    r, c = [], 0
    for x in line:
        if x: c += 1
        elif c: r.append(c); c = 0
    if c: r.append(c)
    return r


def placements(clue, n):
    def rec(i, pos):
        if i == len(clue): yield []; return
        rest = sum(clue[i + 1:]) + len(clue) - i - 1
        for s in range(pos, n - rest - clue[i] + 1):
            for tail in rec(i + 1, s + clue[i] + 1): yield [(s, clue[i])] + tail
    for p in rec(0, 0):
        l = [0] * n
        for s, k in p:
            for j in range(s, s + k): l[j] = 1
        yield l


def ohne_raten(rows):
    # Lässt sich das Bild nur mit Zeilen- und Spaltenlogik lösen (eindeutig, ohne Raten)?
    g = [[c == '#' for c in r] for r in rows]; n = len(g)
    rc = [runs(r) for r in g]; cc = [runs([g[i][j] for i in range(n)]) for j in range(n)]
    st = [[None] * n for _ in range(n)]
    neu = True
    while neu:
        neu = False
        for lines, get, put in ((rc, lambda i, j: st[i][j], lambda i, j, v: st[i].__setitem__(j, v)),
                                (cc, lambda j, i: st[i][j], lambda j, i, v: st[i].__setitem__(j, v))):
            for a in range(n):
                cur = [get(a, b) for b in range(n)]
                ps = [p for p in placements(lines[a], n) if all(cur[b] is None or cur[b] == p[b] for b in range(n))]
                for b in range(n):
                    v = set(p[b] for p in ps)
                    if len(v) == 1 and cur[b] is None: put(a, b, v.pop()); neu = True
    return all(st[i][j] is not None for i in range(n) for j in range(n))


def pruefen():
    for n, liste in BILDER.items():
        for b in liste:
            rows = b[3].split('\n')
            assert len(rows) == n and all(len(r) == n for r in rows), ('Grösse stimmt nicht', b[0])
            assert ohne_raten(rows), ('Bild nicht ohne Raten lösbar', b[0])


def game_html(s):
    meta = json.dumps(s['sterne'], ensure_ascii=False).replace('"', '&quot;')
    g = {'title': s['titel'], 'icon': s['icon'], 'intro': s['intro'], 'n': s['n'], 'levels': s['levels']}
    daten = 'var D = ' + json.dumps(s.get('daten', {}), ensure_ascii=False) + ';\n'
    return ('<!doctype html>\n<html lang="de-CH">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
            f'<meta name="knobelnest-sterne" content="{meta}">\n'
            f'<title>{s["titel"]}</title>\n<style>{GD.CSS.replace("__SCHRIFT__", GD.schrift())}{s.get("css", "")}</style>\n</head>\n<body>\n<div id="app"></div>\n'
            f'<script>\n{GD.POOL}\n{daten}var G = {json.dumps(g, ensure_ascii=False)};\n{s["js"]}\n{FRAME}\n</script>\n</body>\n</html>\n')


def stub_html(s):
    meta = json.dumps(s['sterne'], ensure_ascii=False).replace('"', '&quot;')
    return ('<!doctype html><html lang="de-CH"><head><meta charset="utf-8">'
            f'<meta name="knobelnest-url" content="knobelspiele/{s["id"]}.html">'
            f'<meta name="knobelnest-sterne" content="{meta}">'
            f'<title>{s["titel"]}</title></head><body><p>{s["titel"]}: Dieses Spiel liegt in der Klassenkiste im Ordner knobelspiele/.</p></body></html>')


if __name__ == '__main__':
    pruefen()
    os.makedirs(ZIEL, exist_ok=True)
    for s in SPIELE:
        with open(os.path.join(ZIEL, s['id'] + '.html'), 'w', encoding='utf-8') as f: f.write(game_html(s))
    paket = {'format': 'knobelnest-spielpaket', 'games': [
        {'title': s['titel'], 'description': s['kurz'], 'fach': s['fach'], 'thema': s['thema'], 'stufe': s['stufe'], 'sort': s['sort'], 'html': stub_html(s)} for s in SPIELE]}
    with open(os.path.join(ZIEL, 'knobelspiele-spielpaket.json'), 'w', encoding='utf-8') as f: json.dump(paket, f, ensure_ascii=False, indent=1)
    print(len(SPIELE), 'Knobelspiele gebaut (Ordner knobelspiele/)')
