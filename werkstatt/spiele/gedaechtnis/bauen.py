# Baut die Gedächtniskiste der Klassenkiste.
# Aufruf im Repo-Hauptordner:  python3 werkstatt/spiele/gedaechtnis/bauen.py
#
# Ergebnis:
#   gedaechtnis/<spiel>.html   die Spiele (liegen auf GitHub Pages, Stil der Eulenkiste)
#   gedaechtnis/index.html     das Werkzeug «Gedächtniskiste» für Lehrpersonen (Vorschau, Ausprobieren, Freigeben)
#   werkstatt/spiele/gedaechtnis/gedaechtnis-spielpaket.json   Paket zum Importieren (nur kurze Verweise)
#
# In der Tabelle «games» steht pro Spiel nur ein kurzer Verweis (<meta name="knobelnest-url" content="gedaechtnis/…">).
# Das Portal öffnet dann die Datei aus dem Ordner gedaechtnis/. Verbesserungen kommen so über GitHub, ohne neues Hochladen.
# Die Admin-Lehrperson nimmt die Spiele im Werkzeug mit «Spiele in die Klassenkiste aufnehmen» auf (knGd.install in app.js).
#
# Ein Spiel läuft auf vier Arten (MODE):
#   url      im Spieler der Klassenkiste (Kinder): Nachrichten hello/knobelnestInit/answer/level/round/store an das Portal
#   srcdoc   alte Version (ganzes HTML in der Datenbank): window.knobelnest vom Portal
#   vorschau im Werkzeug (?vorschau&stufe=N): nichts wird gemeldet
#   solo     direkt geöffnet
# Spielstand: ein Eintrag «gd» (JSON als Text) mit Ton aus/ein und Rekorden. Sterne: Level «Stufe 1» … «Stufe 5».
import json, os

HIER = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HIER, '..', '..', '..'))
ZIEL = os.path.join(REPO, 'gedaechtnis')

BEREICHE = [
    ('Bilder merken', '#fbf3dc'),
    ('Orte merken', '#e9f1e3'),
    ('Reihenfolgen merken', '#dcf0fd'),
    ('Namen merken', '#fcefed'),
]

# ------------------------------------------------------------------ Stil (wie die Eulenkiste)
CSS = r"""
@font-face{font-family:"Patrick Hand";src:url(__SCHRIFT__) format("woff2");font-display:swap}
*{box-sizing:border-box}
:root{--bg:#f4f9fd;--ink:#1f2421;--soft:#5f6963;--line:#e1edf7;--line2:#c5d8e8;--gold:#d6ad45;--gold-d:#c4952f;
  --sky:#dcf0fd;--sky-d:#3f78a8;--leaf:#e9f1e3;--rose:#fcefed;--sun:#fbf3dc;--lila:#efe7f7;--ok:#5f9a4a;--no:#c8574e;
  --sch:0 10px 26px rgba(63,120,168,.18),0 2px 6px rgba(63,120,168,.10);--sch-k:0 4px 12px rgba(63,120,168,.14)}
html,body{margin:0;min-height:100%}
body{background:radial-gradient(1200px 600px at 10% -10%,#e3f1fc 0%,transparent 60%),radial-gradient(900px 500px at 110% 110%,#fbf3dc 0%,transparent 60%),var(--bg);
  color:var(--ink);font-family:"Patrick Hand","Segoe Print","Comic Sans MS",cursive;font-size:21px;line-height:1.3;
  -webkit-tap-highlight-color:transparent;user-select:none;-webkit-user-select:none;touch-action:manipulation}
button{font:inherit;color:inherit;cursor:pointer;border:0;background:none}
#app{min-height:100vh;display:flex;flex-direction:column;align-items:center;padding:12px 16px 28px}
.top{width:100%;max-width:960px;display:flex;align-items:center;gap:10px;margin-bottom:6px}
.top .t{flex:1;text-align:center;font-size:23px}
.top .t::after{content:" ✦";color:var(--gold);font-size:.6em;vertical-align:super}
.pill{background:#fff;border:2px solid var(--ink);border-radius:14px;padding:6px 14px;min-height:46px;box-shadow:var(--sch-k);transition:transform .15s}
.pill:hover{transform:translateY(-2px)}.pill:active{transform:translateY(1px)}
.kopf{text-align:center;margin:6px 0 4px}
.ring{width:104px;height:104px;border-radius:50%;display:inline-grid;place-items:center;font-size:54px;background:var(--sun);border:3px solid var(--gold);
  box-shadow:inset 0 0 0 6px #fff,0 8px 18px rgba(63,120,168,.18)}
.kopf h1{margin:10px 0 2px;font-size:42px;font-weight:400;line-height:1}
.kopf h1::after{content:" ✦";color:var(--gold);font-size:.5em;vertical-align:super}
.kopf p{margin:6px auto 0;max-width:540px;color:var(--soft);font-size:20px}
.deko{color:var(--gold);letter-spacing:.35em;font-size:13px;margin-top:8px}
.lvs{width:100%;max-width:600px;display:grid;gap:12px;margin-top:16px}
.lv{display:flex;align-items:center;gap:14px;background:linear-gradient(180deg,#fff 0%,#fff 70%,#f7fbfe 100%);border:1.5px solid var(--line);border-radius:24px;
  padding:12px 18px;text-align:left;min-height:78px;box-shadow:var(--sch);transition:transform .15s,box-shadow .15s}
.lv:hover{transform:translateY(-3px);box-shadow:0 16px 34px rgba(63,120,168,.26),0 3px 8px rgba(63,120,168,.14)}
.lv:active{transform:translateY(1px)}
.lv .n{flex:none;width:54px;height:54px;border-radius:50%;display:grid;place-items:center;font-size:26px;border:3px solid var(--gold);box-shadow:inset 0 0 0 4px #fff}
.lv .tx{flex:1}.lv .tx b{display:block;font-weight:400;font-size:25px;line-height:1.1}.lv .tx span{color:var(--soft);font-size:18px}
.stars{color:var(--gold);font-size:24px;letter-spacing:2px;white-space:nowrap}.stars .off{color:#e6dcc2}
.msg{min-height:60px;font-size:25px;text-align:center;margin:2px 0 10px;max-width:760px;line-height:1.35}
.msg .em{font-size:42px;vertical-align:middle;margin:0 4px;line-height:1}
.msg small{color:var(--soft);font-size:19px}
.dots{display:flex;gap:6px;justify-content:center;margin:2px 0 4px}
.dots i{width:13px;height:13px;border-radius:50%;background:#fff;border:2px solid var(--line2);display:block}.dots i.ok{background:var(--ok);border-color:var(--ok)}.dots i.no{background:var(--no);border-color:var(--no)}
.stage{width:100%;max-width:960px;display:flex;flex-direction:column;align-items:center;gap:14px}
.bar{width:min(420px,90%);height:14px;border-radius:99px;background:#fff;border:2px solid var(--line2);overflow:hidden}
.bar i{display:block;height:100%;background:linear-gradient(90deg,#e8c56a,var(--gold));width:100%;transition:width linear}
.go{background:var(--sky);border:2px solid var(--ink);border-radius:16px;padding:8px 22px;font-size:23px;min-height:54px;box-shadow:var(--sch);transition:transform .15s}
.go:hover{transform:translateY(-2px)}.go:active{transform:translateY(1px)}
.go.alt{background:#fff}.go.sun{background:var(--sun)}
.row{display:flex;gap:10px;flex-wrap:wrap;justify-content:center}
.card{background:#fff;border:2px solid var(--line);border-radius:18px;display:grid;place-items:center;aspect-ratio:1;font-size:clamp(28px,7vw,54px);line-height:1;
  box-shadow:var(--sch-k);transition:background .2s,border-color .2s,transform .12s;position:relative}
button.card:active{transform:scale(.96)}
.grid{display:grid;gap:clamp(6px,1.6vw,12px);width:100%;margin:0 auto}
.grid .card{font-size:inherit}
.card.cover{background:linear-gradient(135deg,#e6f3fd,#c4e2f8);color:var(--gold);border-color:#b9d6ee}
.card.cover::after{content:"✧";font-size:.45em;opacity:.9}
.card.ok{border-color:var(--ok);background:#f1f7ec}
.card.no{border-color:var(--no);background:#fbefed}
.card.hint{border-color:var(--gold);background:var(--sun)}
.card.zahl{color:var(--sky-d)}
.end{background:linear-gradient(180deg,#fff 0%,#fff 70%,#fbf3dc 100%);border:1.5px solid var(--line);border-radius:30px;padding:26px 22px;text-align:center;max-width:480px;width:100%;box-shadow:var(--sch)}
.end .big{font-size:64px}.end h2{margin:6px 0;font-weight:400;font-size:36px}.end p{color:var(--soft);margin:4px 0 18px;font-size:22px}
.shake{animation:sh .35s}@keyframes sh{25%{transform:translateX(-6px)}75%{transform:translateX(6px)}}
.pop{animation:pp .3s}@keyframes pp{50%{transform:scale(1.1)}}
.szene{position:relative;width:min(100%,600px);aspect-ratio:3/2;max-height:52vh;background:#fff;border:2px solid var(--line);border-radius:24px;box-shadow:var(--sch)}
.szene span{position:absolute;transform:translate(-50%,-50%);font-size:clamp(26px,6vw,46px);line-height:1}
.szene.zu{background:linear-gradient(135deg,#e6f3fd,#c4e2f8)}
.nm{position:absolute;left:4px;right:4px;bottom:6%;font-size:clamp(15px,3.2vw,20px);text-align:center;background:var(--sun);border-radius:10px;padding:1px 2px}
.karte{padding-bottom:22%}
@media (max-height:640px){.ring{width:80px;height:80px;font-size:40px}.kopf h1{font-size:32px}.msg{min-height:50px;font-size:21px}}
"""

# ------------------------------------------------------------------ Rahmen für alle Spiele
FRAME = r"""
var MODE = window.knobelnest ? 'srcdoc' : window.parent !== window ? (/[?&]vorschau/.test(location.search) ? 'vorschau' : 'url') : 'solo';
var ST = {}, AW = { lv: {}, max: 0 }, booted = false;
function loadST(s) { try { ST = JSON.parse(s || '{}') || {}; } catch (e) { ST = {}; } }
function send(m) { if (MODE !== 'url') return; m.knobelnest = 1; try { parent.postMessage(m, '*'); } catch (e) {} }
var KN = MODE === 'srcdoc' ? window.knobelnest : {
  answer: function (ok) { send({ type: 'answer', ok: !!ok }); },
  level: function (n) { send({ type: 'level', level: n == null ? null : String(n) }); },
  round: function () { send({ type: 'round' }); },
  sterne: function (k) { return { have: +((AW.lv || {})[k]) || 0, max: +AW.max || 3 }; }
};
function save() {
  var s = JSON.stringify(ST);
  if (MODE === 'url') send({ type: 'store', data: { gd: s } }); else try { localStorage.setItem('gd', s); } catch (e) {}
}
var app = document.getElementById('app'), TM = [], RUN = 0, AC = null, CUR = -1;
var LV_COL = ['#e9f1e3', '#dcf0fd', '#fbf3dc', '#fcefed', '#efe7f7'];
function h(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
function shuffle(a) { a = a.slice(); for (var i = a.length - 1; i > 0; i--) { var j = Math.floor(Math.random() * (i + 1)), t = a[i]; a[i] = a[j]; a[j] = t; } return a; }
function pick(a, n) { return shuffle(a).slice(0, n); }
function rnd(a, b) { return a + Math.floor(Math.random() * (b - a + 1)); }
function range(n) { var a = []; for (var i = 0; i < n; i++) a.push(i); return a; }
function anyCat() { var k = Object.keys(BILD); return BILD[k[rnd(0, k.length - 1)]]; }
function stopAll() { TM.forEach(clearTimeout); TM = []; }
function pop(el) { el.classList.remove('pop'); void el.offsetWidth; el.classList.add('pop'); }
// Raster, das auf den Bildschirm passt (reserve = Platz für Kopf und Text)
function grid(cols, rows, maxPx, reserve) {
  var g = document.createElement('div'); g.className = 'grid'; g.style.gridTemplateColumns = 'repeat(' + cols + ',1fr)';
  var w = Math.min(window.innerWidth - 32, (window.innerHeight - (reserve || 210)) * cols / rows, cols * (maxPx || 130));
  g.style.maxWidth = Math.max(160, w) + 'px'; g.style.fontSize = Math.max(22, Math.min(64, w / cols * 0.5)) + 'px';
  return g;
}
function bigBox() { var b = document.createElement('div'); b.className = 'card'; b.style.cssText = 'width:min(46vw,200px);font-size:min(24vw,112px)'; return b; }
function optBtn(t, wide) { var b = document.createElement('button'); b.className = 'card'; b.style.cssText = wide ? 'aspect-ratio:auto;padding:10px 18px;font-size:26px;min-height:58px' : 'width:clamp(60px,15vw,92px);font-size:clamp(32px,7.5vw,52px)'; b.innerHTML = t; return b; }
function tone(f, d, type, vol) {
  if (ST.mute) return;
  try {
    AC = AC || new (window.AudioContext || window.webkitAudioContext)();
    if (AC.state === 'suspended') AC.resume();
    var o = AC.createOscillator(), g = AC.createGain(), t = AC.currentTime;
    o.type = type || 'sine'; o.frequency.value = f;
    g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(vol || 0.2, t + 0.02); g.gain.exponentialRampToValueAtTime(0.0001, t + d);
    o.connect(g); g.connect(AC.destination); o.start(t); o.stop(t + d + 0.05);
  } catch (e) {}
}
function good() { tone(660, 0.12); setTimeout(function () { tone(990, 0.2); }, 110); }
function bad() { tone(200, 0.3, 'triangle', 0.16); }
function stars(have, max) { var o = ''; for (var i = 0; i < max; i++) o += i < have ? '★' : '<span class="off">★</span>'; return '<span class="stars">' + o + '</span>'; }
function sndBtn() { return '<button class="pill" data-snd aria-label="Ton ein oder aus">' + (ST.mute ? '🔇' : '🔊') + '</button>'; }
app.addEventListener('click', function (e) {
  var b = e.target.closest('[data-snd]'); if (!b) return;
  ST.mute = !ST.mute; save(); b.textContent = ST.mute ? '🔇' : '🔊';
});
var showStars = MODE === 'url' || MODE === 'srcdoc';

function menu() {
  stopAll(); RUN++; CUR = -1; KN.level(null);
  var o = '<div class="top"><span style="flex:1"></span>' + sndBtn() + '</div><div class="kopf"><span class="ring">' + G.icon + '</span><h1>' + h(G.title) + '</h1><p>' + G.intro + '</p><div class="deko">✦ ✧ ✦</div></div><div class="lvs">';
  G.levels.forEach(function (lv, i) {
    var s = KN.sterne('Stufe ' + (i + 1)), mx = s.max || 3;
    o += '<button class="lv" data-lv="' + i + '"><span class="n" style="background:' + LV_COL[i] + '">' + (i + 1) + '</span><span class="tx"><b>' + h(lv.name) + '</b><span>' + h(lv.info) + '</span></span>' +
      (showStars ? stars(Math.min(s.have, mx), mx) : '') + '</button>';
  });
  app.innerHTML = o + '</div>';
  Array.prototype.forEach.call(app.querySelectorAll('[data-lv]'), function (b) { b.onclick = function () { tone(520, 0.08); start(+b.dataset.lv); }; });
}

function start(i) {
  stopAll(); var run = ++RUN, lv = G.levels[i], res = [], N = G.n || 0; CUR = i;
  KN.level('Stufe ' + (i + 1));
  app.innerHTML = '<div class="top"><button class="pill" data-back>← Stufen</button><span class="t">Stufe ' + (i + 1) + ' · ' + h(lv.name) + '</span>' + sndBtn() + '</div>' +
    (N && MODE !== 'url' && MODE !== 'srcdoc' ? '<div class="dots" id="dots"></div>' : '') + '<div class="msg" id="msg"></div><div class="stage" id="stage"></div>';
  app.querySelector('[data-back]').onclick = menu;
  var stage = document.getElementById('stage'), msgEl = document.getElementById('msg');
  function dots() { var d = document.getElementById('dots'); if (!N || !d) return; var o = ''; for (var k = 0; k < N; k++) o += '<i class="' + (k < res.length ? (res[k] ? 'ok' : 'no') : '') + '"></i>'; d.innerHTML = o; }
  dots();
  var api = {
    stage: stage,
    msg: function (t) { msgEl.innerHTML = t; },
    later: function (fn, ms) { TM.push(setTimeout(function () { if (run === RUN) fn(); }, ms)); },
    // Antwort melden. Gibt false zurück, wenn die Runde fertig ist.
    answer: function (ok, quiet) {
      KN.answer(!!ok);
      if (!quiet) { if (ok) good(); else bad(); }
      if (!N) return true;
      res.push(!!ok); dots();
      if (res.length >= N) { var c = res.filter(Boolean).length; api.later(function () { end(i, c + ' von ' + N + ' richtig', c / N); }, 1600); return false; }
      return true;
    },
    // Für Spiele ohne feste Anzahl Aufgaben (Paare finden)
    done: function (line, q) { KN.round(); end(i, line, q); },
    best: function (key, v, lower) {
      ST.best = ST.best || {}; var old = ST.best[key], rec = old == null || (lower ? v < old : v > old);
      if (rec) { ST.best[key] = v; save(); } return { old: old, rec: rec };
    },
    // Merkzeit mit Balken und Knopf «Ich bin bereit»
    watch: function (ms, after) {
      var w = document.createElement('div'); w.className = 'stage'; w.style.gap = '10px';
      w.innerHTML = '<div class="bar"><i></i></div><button class="go alt">Ich bin bereit ✓</button>';
      stage.appendChild(w);
      var bar = w.querySelector('i'), fired = false;
      function fire() { if (fired || run !== RUN) return; fired = true; w.remove(); after(); }
      requestAnimationFrame(function () { requestAnimationFrame(function () { bar.style.transitionDuration = ms + 'ms'; bar.style.width = '0%'; }); });
      w.querySelector('button').onclick = fire;
      api.later(fire, ms);
    }
  };
  G.play(lv, api, i);
}

function end(i, line, q) {
  stopAll(); RUN++;
  var em = q >= 0.9 ? '🏆' : q >= 0.7 ? '🌟' : q >= 0.5 ? '👍' : '💪', t = q >= 0.9 ? 'Super gemacht!' : q >= 0.7 ? 'Gut gemacht!' : q >= 0.5 ? 'Geschafft!' : 'Weiter üben!';
  var next = i + 1 < G.levels.length;
  app.innerHTML = '<div class="top"><span style="flex:1"></span>' + sndBtn() + '</div><div class="stage" style="margin-top:30px"><div class="end"><div class="big">' + em + '</div><h2>' + t + '</h2><p>' + line + '</p><div class="row">' +
    '<button class="go" data-again>Nochmal</button>' + (next && q >= 0.7 ? '<button class="go sun" data-next>Nächste Stufe →</button>' : '') + '<button class="go alt" data-menu>Stufen</button></div><div class="deko" style="margin-top:16px">✦ ✧ ✦</div></div></div>';
  app.querySelector('[data-again]').onclick = function () { start(i); };
  if (app.querySelector('[data-next]')) app.querySelector('[data-next]').onclick = function () { start(i + 1); };
  app.querySelector('[data-menu]').onclick = menu;
  if (q >= 0.7) { good(); setTimeout(function () { tone(1320, 0.25); }, 260); }
}

function boot() {
  if (booted) return; booted = true;
  var m = /[?&]stufe=(\d)/.exec(location.search), s = m ? +m[1] - 1 : -1;
  if (s >= 0 && s < G.levels.length) start(s); else menu();
}
if (MODE === 'url') {
  window.addEventListener('message', function (e) {
    var d = e.data; if (e.source !== parent || !d) return;
    if (d.knobelnestInit && !booted) { var x = d.knobelnestInit; loadST(x.store && x.store.gd); if (x.award && typeof x.award === 'object') AW = x.award; boot(); }
    if (d.knobelnestAward) { AW = d.knobelnestAward; if (booted && CUR < 0) menu(); }
  });
  send({ type: 'hello' });
  setTimeout(boot, 2500);
} else {
  try { loadST(localStorage.getItem('gd')); } catch (e) {}
  if (MODE === 'srcdoc') window.addEventListener('knobelnest-sterne', function () { if (CUR < 0) menu(); });
  boot();
}
"""

POOL = r"""
var BILD = {
  tiere: ['🐶','🐱','🐭','🐰','🦊','🐻','🐼','🐨','🐯','🦁','🐮','🐷','🐸','🐵','🐔','🐧','🦉','🐢','🐙','🦋','🐝','🐞','🐟','🐘'],
  essen: ['🍎','🍐','🍊','🍋','🍌','🍉','🍇','🍓','🍒','🥕','🌽','🥦','🍄','🧀','🥨','🍕','🍦','🍪','🥚','🍞'],
  sachen: ['⚽','🎈','✏️','🔑','🎒','⏰','📚','🧸','🚲','☂️','🎁','🔔','🪁','🎨','✂️','🧦','👓','🎩','🕯️','🧩'],
  natur: ['🌞','🌙','⭐','☁️','🌈','❄️','🔥','🌵','🌲','🌻','🌷','🍁','🌍','⛄','🌊','🐚']
};
var ALLE = [].concat(BILD.tiere, BILD.essen, BILD.sachen, BILD.natur);
var GESICHTER = ['🐶','🐱','🐭','🐰','🦊','🐻','🐼','🐨','🐯','🦁','🐮','🐷','🐵','🐸'];
"""

SPIELE = []

def spiel(**s):
    s.setdefault('n', 10)
    s.setdefault('sterne', {'modus': 'runde', 'n': 10})
    SPIELE.append(s)

# ================================================================== Bilder merken
spiel(id='paare-finden', titel='Paare finden', icon='🃏', thema='Bilder merken', sort=1, n=0,
      sterne={'modus': 'sammeln', 'pro': 'runde', 'max': 3, 'proLevel': True},
      kurz='Karten aufdecken und gleiche Bilder finden.',
      uebt='Bild und Ort zusammen merken',
      intro='Deck zwei Karten auf. Sind es gleiche Bilder? Merk dir, wo die Bilder liegen!',
      levels=[dict(name='Leicht', info='3 Paare', p=3, c=3, set='essen'),
              dict(name='Gut', info='4 Paare', p=4, c=4, set='tiere'),
              dict(name='Mittel', info='6 Paare', p=6, c=4, set='sachen'),
              dict(name='Schwer', info='8 Paare', p=8, c=4, set='mix'),
              dict(name='Profi', info='10 Paare, ähnliche Tiergesichter', p=10, c=5, set='gesichter')],
      js=r"""
G.play = function (lv, api, li) {
  var set = lv.set === 'mix' ? ALLE : lv.set === 'gesichter' ? GESICHTER : BILD[lv.set], pics = pick(set, lv.p), cards = shuffle(pics.concat(pics));
  var rows = Math.ceil(cards.length / lv.c), first = null, lock = false, moves = 0, found = 0, key = 'paare' + li;
  var best = (ST.best || {})[key];
  api.msg('Finde alle Paare! <small id="mv">Züge: 0' + (best ? ' · Rekord: ' + best : '') + '</small>');
  var g = grid(lv.c, rows, 130, 190);
  cards.forEach(function (p, k) {
    var b = document.createElement('button'); b.className = 'card cover'; b.dataset.p = p; b.setAttribute('aria-label', 'Karte ' + (k + 1));
    b.onclick = function () { turn(b); };
    g.appendChild(b);
  });
  api.stage.appendChild(g);
  function show(b, on) { b.classList.toggle('cover', !on); b.textContent = on ? b.dataset.p : ''; if (on) pop(b); }
  function turn(b) {
    if (lock || b.dataset.open) return;
    b.dataset.open = 1; show(b, true); tone(520 + (first ? 120 : 0), 0.08);
    if (!first) { first = b; return; }
    moves++; document.getElementById('mv').textContent = 'Züge: ' + moves + (best ? ' · Rekord: ' + best : '');
    var a = first; first = null;
    if (a.dataset.p === b.dataset.p) {
      found++; api.answer(true); a.classList.add('ok'); b.classList.add('ok');
      if (found === lv.p) {
        var r = api.best(key, moves, true), q = moves <= lv.p * 1.5 ? 1 : moves <= lv.p * 2.2 ? 0.8 : 0.6;
        api.later(function () { api.done('Alle Paare gefunden in ' + moves + ' Zügen.' + (r.rec && r.old ? ' Neuer Rekord!' : ''), q); }, 900);
      }
    } else {
      api.answer(false, true); lock = true;
      api.later(function () { delete a.dataset.open; delete b.dataset.open; show(a, false); show(b, false); lock = false; }, 950);
    }
  }
};
""")

spiel(id='was-fehlt', titel='Was fehlt?', icon='🔍', thema='Bilder merken', sort=2,
      kurz='Bilder anschauen. Dann ist eines weg: Welches fehlt?',
      uebt='Viele Bilder auf einmal merken',
      intro='Schau dir die Bilder gut an. Dann verschwindet eines. Weisst du, welches fehlt?',
      levels=[dict(name='Leicht', info='3 Bilder, gleicher Platz', k=3, ms=5000, opt=3, mix=False, same=False),
              dict(name='Gut', info='4 Bilder, gleicher Platz', k=4, ms=6000, opt=4, mix=False, same=False),
              dict(name='Mittel', info='5 Bilder, sie werden gemischt', k=5, ms=7000, opt=4, mix=True, same=False),
              dict(name='Schwer', info='6 ähnliche Bilder, gemischt', k=6, ms=8000, opt=6, mix=True, same=True),
              dict(name='Profi', info='8 ähnliche Bilder, gemischt', k=8, ms=9000, opt=6, mix=True, same=True)],
      js=r"""
G.play = function (lv, api) {
  function task() {
    api.stage.innerHTML = '';
    var cat = anyCat(), src = lv.same ? cat : ALLE, shown = pick(src, lv.k), miss = rnd(0, lv.k - 1), gone = shown[miss];
    var cols = lv.k <= 4 ? lv.k : Math.ceil(lv.k / 2), g = grid(cols, Math.ceil(lv.k / cols), 120, 330);
    g.innerHTML = shown.map(function (p) { return '<div class="card">' + p + '</div>'; }).join('');
    api.stage.appendChild(g);
    api.msg('<span class="em">👀</span> Merk dir alle Bilder!');
    api.watch(lv.ms, function () {
      g.innerHTML = shown.map(function () { return '<div class="card cover"></div>'; }).join('');
      api.msg('<span class="em">🙈</span> Augen zu …');
      api.later(function () {
        var rest = shown.slice(); rest[miss] = null; if (lv.mix) rest = shuffle(rest);
        g.innerHTML = rest.map(function (p) { return p ? '<div class="card pop">' + p + '</div>' : '<div class="card hint" data-gap style="border-style:dashed;color:var(--gold-d)">?</div>'; }).join('');
        api.msg('<span class="em">🤔</span> Welches Bild fehlt?');
        var others = shuffle(src.filter(function (p) { return shown.indexOf(p) < 0; })).slice(0, lv.opt - 1);
        var r = document.createElement('div'); r.className = 'row';
        shuffle(others.concat([gone])).forEach(function (p) {
          var b = optBtn(p);
          b.onclick = function () {
            if (r.dataset.done) return; r.dataset.done = 1;
            var ok = p === gone, gap = g.querySelector('[data-gap]');
            gap.textContent = gone; gap.style.borderStyle = 'solid'; gap.className = 'card pop ' + (ok ? 'ok' : 'hint');
            b.classList.add(ok ? 'ok' : 'no'); if (!ok) b.classList.add('shake');
            api.msg(ok ? '<span class="em">🎉</span> Richtig!' : '<span class="em">💡</span> Es fehlte: <span class="em">' + gone + '</span>');
            if (api.answer(ok)) api.later(task, ok ? 1300 : 2300);
          };
          r.appendChild(b);
        });
        api.stage.appendChild(r);
      }, 700);
    });
  }
  task();
};
""")

spiel(id='was-ist-anders', titel='Was ist anders?', icon='🕵️', thema='Bilder merken', sort=3,
      kurz='Ein Bild ist neu oder zwei haben getauscht. Was hat sich verändert?',
      uebt='Genau hinschauen und vergleichen',
      intro='Merk dir die Bilder und ihre Plätze. Danach hat sich etwas verändert. Findest du es?',
      levels=[dict(name='Leicht', info='4 Bilder, eines ist neu', k=4, c=2, ms=5000, swap=False, same=False),
              dict(name='Gut', info='6 Bilder, eines ist neu', k=6, c=3, ms=6000, swap=False, same=False),
              dict(name='Mittel', info='8 ähnliche Bilder, eines ist neu', k=8, c=4, ms=7000, swap=False, same=True),
              dict(name='Schwer', info='6 Bilder, zwei haben getauscht', k=6, c=3, ms=7000, swap=True, same=False),
              dict(name='Profi', info='9 Bilder, zwei haben getauscht', k=9, c=3, ms=9000, swap=True, same=True)],
      js=r"""
G.play = function (lv, api) {
  function task() {
    api.stage.innerHTML = '';
    var src = lv.same ? anyCat() : ALLE, pics = pick(src, lv.k), g = grid(lv.c, Math.ceil(lv.k / lv.c), 120, 270);
    function draw(arr) { g.innerHTML = arr.map(function (p, i) { return '<button class="card" data-i="' + i + '">' + p + '</button>'; }).join(''); }
    draw(pics); api.stage.appendChild(g);
    api.msg('<span class="em">👀</span> Merk dir die Bilder und ihre Plätze!');
    api.watch(lv.ms, function () {
      Array.prototype.forEach.call(g.children, function (c) { c.className = 'card cover'; c.textContent = ''; });
      api.msg('<span class="em">🙈</span> Augen zu …');
      api.later(function () {
        var now = pics.slice(), changed, a = rnd(0, lv.k - 1);
        if (lv.swap) {
          var b; do { b = rnd(0, lv.k - 1); } while (b === a);
          now[a] = pics[b]; now[b] = pics[a]; changed = [a, b];
          api.msg('<span class="em">🔄</span> Zwei Bilder haben den Platz getauscht. Tippe eines davon an!');
        } else {
          now[a] = shuffle(src.filter(function (p) { return pics.indexOf(p) < 0; }))[0]; changed = [a];
          api.msg('<span class="em">🔎</span> Ein Bild ist neu. Welches?');
        }
        draw(now);
        var over = false;
        Array.prototype.forEach.call(g.children, function (btn) {
          pop(btn);
          btn.onclick = function () {
            if (over) return; over = true;
            var i = +btn.dataset.i, ok = changed.indexOf(i) >= 0;
            changed.forEach(function (k) { g.children[k].classList.add(ok ? 'ok' : 'hint'); });
            if (!ok) btn.classList.add('no', 'shake');
            api.msg(ok ? '<span class="em">🎉</span> Richtig gesehen!' : lv.swap ? '<span class="em">💡</span> Diese zwei haben getauscht.' : '<span class="em">💡</span> Dieses Bild war neu. Vorher war hier: <span class="em">' + pics[changed[0]] + '</span>');
            if (api.answer(ok)) api.later(task, ok ? 1300 : 2700);
          };
        });
      }, 800);
    });
  }
  task();
};
""")

spiel(id='wie-viele', titel='Wie viele?', icon='🍎', thema='Bilder merken', sort=4,
      kurz='Ein Bild blitzt kurz auf. Wie viele Äpfel waren es?',
      uebt='Mengen schnell erfassen und merken',
      intro='Ein Bild erscheint nur kurz. Schau genau hin! Danach fragt die Eule, wie viele es von etwas waren.',
      levels=[dict(name='Leicht', info='2 Sorten, je 1 bis 3', s=2, mx=3, ms=5000),
              dict(name='Gut', info='2 Sorten, je 1 bis 4', s=2, mx=4, ms=4000),
              dict(name='Mittel', info='3 Sorten, je 1 bis 4', s=3, mx=4, ms=5000),
              dict(name='Schwer', info='3 Sorten, je 1 bis 5', s=3, mx=5, ms=4000),
              dict(name='Profi', info='4 Sorten, je 1 bis 5', s=4, mx=5, ms=4000)],
      js=r"""
G.play = function (lv, api) {
  function scene(sc, items, mark) {
    sc.className = 'szene';
    sc.innerHTML = items.map(function (it) { return '<span style="left:' + it.x + '%;top:' + it.y + '%' + (mark && it.p !== mark ? ';opacity:.25' : '') + '">' + it.p + '</span>'; }).join('');
  }
  function task() {
    api.stage.innerHTML = '';
    var kinds = pick(ALLE, lv.s), cnt = kinds.map(function () { return rnd(1, lv.mx); }), slots = shuffle(range(24)), items = [], k = 0;
    kinds.forEach(function (p, i) { for (var j = 0; j < cnt[i]; j++) { var s = slots[k++]; items.push({ p: p, x: ((s % 6) + 0.5) / 6 * 100 + rnd(-4, 4), y: (Math.floor(s / 6) + 0.5) / 4 * 100 + rnd(-6, 6) }); } });
    var sc = document.createElement('div'); scene(sc, items); api.stage.appendChild(sc);
    api.msg('<span class="em">👀</span> Schau genau hin!');
    api.watch(lv.ms, function () {
      sc.className = 'szene zu'; sc.innerHTML = '';
      var ask = rnd(0, kinds.length - 1);
      api.msg('Wie viele <span class="em">' + kinds[ask] + '</span> waren es?');
      var r = document.createElement('div'); r.className = 'row'; var over = false;
      for (var v = 1; v <= lv.mx; v++) (function (v) {
        var b = optBtn(String(v)); b.style.color = 'var(--sky-d)';
        b.onclick = function () {
          if (over) return; over = true;
          var ok = v === cnt[ask]; b.classList.add(ok ? 'ok' : 'no'); if (!ok) { b.classList.add('shake'); r.children[cnt[ask] - 1].classList.add('hint'); }
          scene(sc, items, kinds[ask]);
          api.msg(ok ? '<span class="em">🎉</span> Genau, ' + v + '!' : '<span class="em">💡</span> Es waren ' + cnt[ask] + '.');
          if (api.answer(ok)) api.later(task, ok ? 1500 : 2600);
        };
        r.appendChild(b);
      })(v);
      api.stage.appendChild(r);
    });
  }
  task();
};
""")

# ================================================================== Orte merken
spiel(id='wo-war-es', titel='Wo war es?', icon='📍', thema='Orte merken', sort=5,
      kurz='Bilder werden zugedeckt. Wo lag der Fuchs?',
      uebt='Orte und Plätze merken',
      intro='Schau dir gut an, wo die Bilder liegen. Dann werden sie zugedeckt. Findest du sie wieder?',
      levels=[dict(name='Leicht', info='2 Bilder auf 4 Feldern', r=2, c=2, k=2, ms=5000),
              dict(name='Gut', info='3 Bilder auf 9 Feldern', r=3, c=3, k=3, ms=6000),
              dict(name='Mittel', info='4 Bilder auf 9 Feldern', r=3, c=3, k=4, ms=7000),
              dict(name='Schwer', info='5 Bilder auf 16 Feldern', r=4, c=4, k=5, ms=8000),
              dict(name='Profi', info='7 Bilder auf 16 Feldern', r=4, c=4, k=7, ms=10000)],
      js=r"""
G.play = function (lv, api) {
  function board() {
    api.stage.innerHTML = '';
    var n = lv.r * lv.c, cells = pick(range(n), lv.k), pics = pick(ALLE, lv.k), at = {};
    cells.forEach(function (c, i) { at[c] = pics[i]; });
    var g = grid(lv.c, lv.r, 130, 260), btns = [];
    for (var i = 0; i < n; i++) { var b = document.createElement('button'); b.className = 'card'; b.dataset.i = i; b.textContent = at[i] || ''; g.appendChild(b); btns.push(b); }
    api.stage.appendChild(g);
    api.msg('<span class="em">👀</span> Merk dir, wo die Bilder liegen!');
    api.watch(lv.ms, function () {
      btns.forEach(function (b) { b.textContent = ''; b.className = 'card cover'; });
      var q = shuffle(cells), lock = false;
      function ask() {
        if (!q.length) { api.later(board, 900); return; }
        var c = q[0]; lock = false;
        api.msg('Wo war <span class="em">' + at[c] + '</span> ?');
        btns.forEach(function (b) { b.onclick = function () {
          if (lock || b.dataset.done) return; lock = true;
          var i = +b.dataset.i, ok = i === c, right = btns[c];
          right.textContent = at[c]; right.className = 'card pop ' + (ok ? 'ok' : 'hint'); right.dataset.done = 1;
          if (!ok) { b.classList.add('no', 'shake'); api.later(function () { b.classList.remove('no', 'shake'); }, 800); }
          api.msg(ok ? '<span class="em">🎉</span> Genau dort!' : '<span class="em">💡</span> Es war hier.');
          q.shift();
          if (api.answer(ok)) api.later(ask, ok ? 900 : 1700);
        }; });
      }
      ask();
    });
  }
  board();
};
""")

spiel(id='weg-merken', titel='Weg merken', icon='🦉', thema='Orte merken', sort=6,
      kurz='Die Eule hüpft über das Feld. Den Weg merken und nachtippen.',
      uebt='Wege und Richtungen merken',
      intro='Die Eule hüpft von Feld zu Feld. Schau gut zu und tippe danach ihren Weg nach!',
      levels=[dict(name='Leicht', info='3 × 3 Felder, 2 bis 3 Schritte', s=3, a=2, b=3, ms=950),
              dict(name='Gut', info='3 × 3 Felder, 3 bis 4 Schritte', s=3, a=3, b=4, ms=850),
              dict(name='Mittel', info='4 × 4 Felder, 4 bis 5 Schritte', s=4, a=4, b=5, ms=800),
              dict(name='Schwer', info='4 × 4 Felder, 5 bis 7 Schritte', s=4, a=5, b=7, ms=700),
              dict(name='Profi', info='5 × 5 Felder, 7 bis 9 Schritte', s=5, a=7, b=9, ms=620)],
      js=r"""
G.play = function (lv, api) {
  var t = 0, S = lv.s;
  function path(n) {
    for (var tries = 0; tries < 300; tries++) {
      var p = [rnd(0, S * S - 1)], ok = true;
      while (p.length < n + 1) {
        var c = p[p.length - 1], r = Math.floor(c / S), q = c % S, nb = [];
        if (r > 0) nb.push(c - S); if (r < S - 1) nb.push(c + S); if (q > 0) nb.push(c - 1); if (q < S - 1) nb.push(c + 1);
        nb = nb.filter(function (x) { return p.indexOf(x) < 0; });
        if (!nb.length) { ok = false; break; }
        p.push(nb[rnd(0, nb.length - 1)]);
      }
      if (ok) return p;
    }
  }
  function task() {
    api.stage.innerHTML = '';
    var steps = lv.a + Math.floor(t * (lv.b - lv.a + 1) / 10); t++;
    var p = path(steps), g = grid(S, S, 115, 230), cells = [];
    for (var i = 0; i < S * S; i++) { var b = document.createElement('button'); b.className = 'card'; b.dataset.i = i; g.appendChild(b); cells.push(b); }
    api.stage.appendChild(g);
    function owl(i) { cells.forEach(function (c) { if (c.textContent === '🦉') c.textContent = ''; }); cells[i].textContent = '🦉'; pop(cells[i]); }
    owl(p[0]); cells[p[0]].classList.add('hint');
    api.msg('<span class="em">👀</span> Schau, wohin die Eule hüpft!');
    p.slice(1).forEach(function (c, k) {
      api.later(function () { owl(c); tone(440 + k * 50, 0.1); }, 1000 + k * lv.ms);
    });
    api.later(function () { owl(p[0]); input(); }, 1000 + steps * lv.ms + 200);
    function input() {
      var pos = 1, over = false;
      api.msg('<span class="em">👆</span> Jetzt du! Tippe den Weg der Eule nach. <small>(' + steps + ' Schritte)</small>');
      cells.forEach(function (b) { b.onclick = function () {
        if (over) return; var i = +b.dataset.i;
        if (i === p[pos]) {
          b.classList.add('ok'); b.textContent = '🐾'; pos++; tone(500 + pos * 40, 0.08);
          if (pos === p.length) { over = true; b.textContent = '🦉'; api.msg('<span class="em">🎉</span> Genau so ist die Eule gehüpft!'); if (api.answer(true)) api.later(task, 1400); }
        } else if (i !== p[0] && !b.classList.contains('ok')) {
          over = true; b.classList.add('no', 'shake');
          var more = api.answer(false), rest = p.slice(pos);
          api.msg('<span class="em">💡</span> So ist die Eule gehüpft:');
          rest.forEach(function (c, k) { api.later(function () { cells[c].classList.add('hint'); cells[c].textContent = k === rest.length - 1 ? '🦉' : '🐾'; pop(cells[c]); }, 500 + k * 380); });
          if (more) api.later(task, 1700 + rest.length * 380);
        }
      }; });
    }
  }
  task();
};
""")

spiel(id='zahlen-verstecken', titel='Zahlen verstecken', icon='🔢', thema='Orte merken', sort=7,
      kurz='Zahlen stehen kurz auf dem Feld. Dann der Reihe nach antippen: 1, 2, 3 …',
      uebt='Orte und Reihenfolge zusammen merken',
      intro='Merk dir, wo die Zahlen stehen. Dann werden sie zugedeckt. Tippe sie der Reihe nach an: 1, 2, 3 …',
      levels=[dict(name='Leicht', info='3 Zahlen auf 9 Feldern', s=3, k=3, ms=6000, alle=False),
              dict(name='Gut', info='4 Zahlen auf 9 Feldern', s=3, k=4, ms=6000, alle=False),
              dict(name='Mittel', info='5 Zahlen auf 16 Feldern', s=4, k=5, ms=6000, alle=False),
              dict(name='Schwer', info='6 Zahlen, alle Felder zugedeckt', s=4, k=6, ms=6000, alle=True),
              dict(name='Profi', info='8 Zahlen auf 25 Feldern, alle zugedeckt', s=5, k=8, ms=7000, alle=True)],
      js=r"""
G.play = function (lv, api) {
  function task() {
    api.stage.innerHTML = '';
    var n = lv.s * lv.s, cells = pick(range(n), lv.k), g = grid(lv.s, lv.s, 115, 260), bs = [];
    for (var i = 0; i < n; i++) { var b = document.createElement('button'); b.className = 'card zahl'; b.dataset.i = i; g.appendChild(b); bs.push(b); }
    cells.forEach(function (c, k) { bs[c].textContent = k + 1; });
    api.stage.appendChild(g);
    api.msg('<span class="em">👀</span> Merk dir, wo die Zahlen stehen!');
    api.watch(lv.ms, function () {
      bs.forEach(function (b, i) { b.textContent = ''; if (lv.alle || cells.indexOf(i) >= 0) b.classList.add('cover'); });
      api.msg('<span class="em">👆</span> Tippe der Reihe nach: 1, 2, 3 …');
      var pos = 0, over = false;
      bs.forEach(function (b, i) { b.onclick = function () {
        if (over || b.classList.contains('ok')) return;
        if (i === cells[pos]) {
          b.classList.remove('cover'); b.classList.add('ok'); b.textContent = pos + 1; pop(b); pos++; tone(480 + pos * 50, 0.08);
          if (pos === lv.k) { over = true; api.msg('<span class="em">🎉</span> Alle Zahlen gefunden!'); if (api.answer(true)) api.later(task, 1300); }
        } else {
          over = true; b.classList.add('no', 'shake');
          cells.forEach(function (c, k) { if (k >= pos) { bs[c].classList.remove('cover'); bs[c].classList.add('hint'); bs[c].textContent = k + 1; } });
          api.msg('<span class="em">💡</span> Hier wäre die ' + (pos + 1) + ' gewesen.');
          if (api.answer(false)) api.later(task, 2600);
        }
      }; });
    });
  }
  task();
};
""")

# ================================================================== Reihenfolgen merken
spiel(id='farben-reihe', titel='Farben-Reihe', icon='🚦', thema='Reihenfolgen merken', sort=8,
      kurz='Felder leuchten nacheinander auf. Die Reihenfolge nachtippen.',
      uebt='Reihenfolgen sehen und hören',
      intro='Die Felder leuchten nacheinander auf. Schau gut zu und tippe sie danach in der gleichen Reihenfolge an.',
      levels=[dict(name='Leicht', info='4 Felder, 2 bis 3 Mal leuchten', k=4, c=2, a=2, b=3, ms=900),
              dict(name='Gut', info='4 Felder, 3 bis 4 Mal leuchten', k=4, c=2, a=3, b=4, ms=800),
              dict(name='Mittel', info='6 Felder, 4 bis 5 Mal leuchten', k=6, c=3, a=4, b=5, ms=720),
              dict(name='Schwer', info='9 Felder, 5 bis 6 Mal leuchten', k=9, c=3, a=5, b=6, ms=650),
              dict(name='Profi', info='9 Felder, 6 bis 8 Mal, schneller', k=9, c=3, a=6, b=8, ms=560)],
      js=r"""
var PADS = [
  { c: '#e46f63', s: '♥', f: 262 }, { c: '#4f93d1', s: '●', f: 330 }, { c: '#e2b43c', s: '★', f: 392 }, { c: '#6aa95a', s: '▲', f: 440 },
  { c: '#9a74c4', s: '◆', f: 523 }, { c: '#e58c45', s: '■', f: 587 }, { c: '#3fb0a0', s: '✿', f: 659 }, { c: '#de6fa6', s: '☾', f: 698 }, { c: '#8d6e5a', s: '✚', f: 784 }
];
G.play = function (lv, api) {
  var t = 0, pads = PADS.slice(0, lv.k), btns = [], seq = [], pos = 0, input = false;
  var g = grid(lv.c, Math.ceil(lv.k / lv.c), 150, 210);
  pads.forEach(function (p, k) {
    var b = document.createElement('button'); b.className = 'card'; b.setAttribute('aria-label', 'Feld ' + (k + 1));
    b.style.cssText = 'background:' + p.c + ';border:3px solid #fff;color:#fff;opacity:.42;transition:opacity .12s,transform .12s;box-shadow:0 0 0 2px ' + p.c;
    b.innerHTML = '<span style="font-size:.8em;text-shadow:0 2px 4px #0003">' + p.s + '</span>';
    b.onclick = function () { tap(k); };
    g.appendChild(b); btns.push(b);
  });
  api.stage.appendChild(g);
  function flash(k, ms) { var b = btns[k]; b.style.opacity = 1; b.style.transform = 'scale(1.06)'; tone(pads[k].f, ms / 1000 * 0.9, 'sine', 0.2);
    api.later(function () { b.style.opacity = .42; b.style.transform = ''; }, ms); }
  function task() {
    var len = lv.a + Math.floor(t * (lv.b - lv.a + 1) / 10); t++;
    seq = []; for (var i = 0; i < len; i++) { var x; do { x = rnd(0, lv.k - 1); } while (i > 1 && x === seq[i - 1] && x === seq[i - 2]); seq.push(x); }
    pos = 0; input = false; api.msg('<span class="em">👀</span> Schau gut zu!');
    play(seq, 900, function () { input = true; api.msg('<span class="em">👆</span> Jetzt du! <small>(' + len + ' Mal)</small>'); });
  }
  function play(s, wait, after) {
    s.forEach(function (k, i) { api.later(function () { flash(k, lv.ms * 0.7); }, wait + i * lv.ms); });
    api.later(after, wait + s.length * lv.ms);
  }
  function tap(k) {
    if (!input) return;
    if (k === seq[pos]) {
      flash(k, 260); pos++;
      if (pos === seq.length) { input = false; api.later(function () { api.msg('<span class="em">🎉</span> Richtig!'); if (api.answer(true)) api.later(task, 1200); }, 300); }
    } else {
      input = false; btns[k].classList.add('shake'); api.later(function () { btns[k].classList.remove('shake'); }, 400);
      var more = api.answer(false);
      api.msg('<span class="em">🙈</span> Hoppla! So wäre es richtig gewesen:');
      play(seq, 700, function () { if (more) api.later(task, 900); });
    }
  }
  task();
};
""")

spiel(id='bilder-reihe', titel='Bilder-Reihe', icon='🎞️', thema='Reihenfolgen merken', sort=9,
      kurz='Bilder erscheinen nacheinander. In der richtigen Reihenfolge antippen.',
      uebt='Reihenfolgen merken, auch rückwärts',
      intro='Die Bilder kommen eines nach dem anderen. Tippe sie danach in der gleichen Reihenfolge an.',
      levels=[dict(name='Leicht', info='2 bis 3 Bilder', a=2, b=3, x=0, ms=1400),
              dict(name='Gut', info='3 bis 4 Bilder, 2 zum Verwechseln', a=3, b=4, x=2, ms=1300),
              dict(name='Mittel', info='4 bis 5 Bilder, 3 zum Verwechseln', a=4, b=5, x=3, ms=1200),
              dict(name='Schwer', info='5 bis 6 Bilder, 3 zum Verwechseln', a=5, b=6, x=3, ms=1100),
              dict(name='Profi', info='Rückwärts! 4 bis 5 Bilder', a=4, b=5, x=3, ms=1200, back=True)],
      js=r"""
G.play = function (lv, api) {
  var t = 0;
  function task() {
    api.stage.innerHTML = '';
    var len = lv.a + Math.floor(t * (lv.b - lv.a + 1) / 10); t++;
    var all = pick(anyCat(), len + lv.x), seq = all.slice(0, len), want = lv.back ? seq.slice().reverse() : seq;
    var box = bigBox(), cnt = document.createElement('div'); cnt.className = 'dots';
    api.stage.appendChild(box); api.stage.appendChild(cnt);
    api.msg('<span class="em">👀</span> Schau gut zu!');
    seq.forEach(function (p, i) {
      api.later(function () {
        box.textContent = p; pop(box); tone(440 + i * 60, 0.1);
        cnt.innerHTML = seq.map(function (_, k) { return '<i class="' + (k <= i ? 'ok' : '') + '"></i>'; }).join('');
      }, 600 + i * lv.ms);
      api.later(function () { box.textContent = ''; }, 600 + i * lv.ms + lv.ms * 0.75);
    });
    api.later(answer, 700 + len * lv.ms);
    function answer() {
      api.stage.innerHTML = '';
      api.msg(lv.back ? '<span class="em">🔙</span> Jetzt <u>rückwärts</u>: vom letzten zum ersten Bild!' : '<span class="em">👆</span> In welcher Reihenfolge kamen die Bilder?');
      var slots = document.createElement('div'); slots.className = 'row';
      slots.innerHTML = want.map(function () { return '<div class="card" style="width:clamp(52px,13vw,84px);font-size:clamp(28px,7vw,46px);border-style:dashed"></div>'; }).join('');
      var pool = document.createElement('div'); pool.className = 'row'; pool.style.marginTop = '12px';
      var pos = 0, over = false;
      shuffle(all).forEach(function (p) {
        var b = optBtn(p);
        b.onclick = function () {
          if (over || b.disabled) return;
          var s = slots.children[pos];
          if (p === want[pos]) {
            s.textContent = p; s.style.borderStyle = 'solid'; s.classList.add('ok'); pop(s); b.disabled = true; b.style.opacity = .3; pos++; tone(520 + pos * 50, 0.08);
            if (pos === want.length) { over = true; api.msg('<span class="em">🎉</span> Richtig!'); if (api.answer(true)) api.later(task, 1300); }
          } else {
            over = true; b.classList.add('no', 'shake');
            want.forEach(function (w, k) { var c = slots.children[k]; if (k >= pos) { c.textContent = w; c.style.borderStyle = 'solid'; c.classList.add('hint'); } });
            api.msg('<span class="em">💡</span> So wäre es richtig gewesen.');
            if (api.answer(false)) api.later(task, 2600);
          }
        };
        pool.appendChild(b);
      });
      api.stage.appendChild(slots); api.stage.appendChild(pool);
    }
  }
  task();
};
""")

spiel(id='koffer-packen', titel='Koffer packen', icon='🧳', thema='Reihenfolgen merken', sort=10,
      kurz='Ich packe in meinen Koffer … Jedes Mal kommt etwas dazu.',
      uebt='Eine wachsende Liste merken',
      intro='Ich packe in meinen Koffer … Jedes Mal kommt etwas Neues dazu. Tippe immer alles in der richtigen Reihenfolge an!',
      levels=[dict(name='Leicht', info='Start mit 1 Sache, 8 zur Auswahl', start=1, pool=8, same=False),
              dict(name='Gut', info='Start mit 2 Sachen, 10 zur Auswahl', start=2, pool=10, same=False),
              dict(name='Mittel', info='Start mit 3 Sachen, 12 zur Auswahl', start=3, pool=12, same=False),
              dict(name='Schwer', info='Start mit 4 Sachen, 14 zur Auswahl', start=4, pool=14, same=False),
              dict(name='Profi', info='Start mit 5 ähnlichen Sachen', start=5, pool=14, same=True)],
      js=r"""
G.play = function (lv, api, li) {
  var pool, seq, key = 'koffer' + li;
  function fresh() { pool = pick(lv.same ? (Math.random() < .5 ? BILD.tiere : BILD.sachen) : ALLE, lv.pool); seq = pool.slice(0, lv.start); pool = shuffle(pool); }
  function show(items, first) {
    api.stage.innerHTML = '';
    var box = bigBox(); api.stage.appendChild(box);
    api.msg(first ? '<span class="em">🧳</span> Ich packe in meinen Koffer …' : '<span class="em">🧳</span> … und dazu noch:');
    items.forEach(function (p, i) {
      api.later(function () { box.textContent = p; pop(box); tone(520 + i * 40, 0.1); }, 500 + i * 1300);
      api.later(function () { box.textContent = ''; }, 500 + i * 1300 + 1000);
    });
    api.later(ask, 600 + items.length * 1300);
  }
  function ask() {
    api.stage.innerHTML = '';
    var best = (ST.best || {})[key];
    api.msg('<span class="em">👆</span> Was ist im Koffer? Tippe alles der Reihe nach! <small>(' + seq.length + (seq.length === 1 ? ' Sache' : ' Sachen') + (best ? ' · Rekord: ' + best : '') + ')</small>');
    var slots = document.createElement('div'); slots.className = 'row';
    slots.innerHTML = seq.map(function () { return '<div class="card" style="width:clamp(40px,10vw,66px);font-size:clamp(22px,5.5vw,36px);border-style:dashed"></div>'; }).join('');
    var pl = document.createElement('div'); pl.className = 'row'; pl.style.marginTop = '10px';
    var pos = 0, over = false;
    pool.forEach(function (p) {
      var b = optBtn(p);
      b.onclick = function () {
        if (over || b.disabled) return;
        var s = slots.children[pos];
        if (p === seq[pos]) {
          s.textContent = p; s.style.borderStyle = 'solid'; s.classList.add('ok'); b.disabled = true; b.style.opacity = .3; pos++; tone(500 + pos * 30, 0.07);
          if (pos === seq.length) {
            over = true; api.best(key, seq.length);
            var more = api.answer(true);
            var rest = pool.filter(function (x) { return seq.indexOf(x) < 0; });
            if (!rest.length) { api.msg('<span class="em">🎉</span> Der Koffer ist voll! Super!'); fresh(); if (more) api.later(function () { show(seq, true); }, 1800); return; }
            api.msg('<span class="em">🎉</span> Richtig! Es kommt noch etwas dazu …');
            var nu = rest[rnd(0, rest.length - 1)]; seq.push(nu);
            if (more) api.later(function () { show([nu], false); }, 1300);
          }
        } else {
          over = true; b.classList.add('no', 'shake');
          seq.forEach(function (w, k) { var c = slots.children[k]; if (k >= pos) { c.textContent = w; c.style.borderStyle = 'solid'; c.classList.add('hint'); } });
          api.msg('<span class="em">💡</span> So war der Koffer gepackt. Wir packen einen neuen!');
          var more2 = api.answer(false); fresh();
          if (more2) api.later(function () { show(seq, true); }, 2800);
        }
      };
      pl.appendChild(b);
    });
    api.stage.appendChild(slots); api.stage.appendChild(pl);
  }
  fresh(); show(seq, true);
};
""")

spiel(id='zahlen-merken', titel='Zahlen merken', icon='🧮', thema='Reihenfolgen merken', sort=11,
      kurz='Ziffern erscheinen nacheinander. Merken und eintippen, auch rückwärts.',
      uebt='Zahlenfolgen merken',
      intro='Die Ziffern erscheinen eine nach der anderen. Merk sie dir und tippe sie dann ein.',
      levels=[dict(name='Leicht', info='3 Ziffern', a=3, b=3, ms=1100),
              dict(name='Gut', info='4 Ziffern', a=4, b=4, ms=1000),
              dict(name='Mittel', info='5 Ziffern', a=5, b=5, ms=1000),
              dict(name='Schwer', info='6 bis 7 Ziffern', a=6, b=7, ms=950),
              dict(name='Profi', info='Rückwärts! 4 bis 5 Ziffern', a=4, b=5, ms=1000, back=True)],
      js=r"""
G.play = function (lv, api) {
  var t = 0;
  function task() {
    api.stage.innerHTML = '';
    var len = lv.a + Math.floor(t * (lv.b - lv.a + 1) / 10); t++;
    var seq = []; for (var i = 0; i < len; i++) { var d; do { d = rnd(0, 9); } while (d === seq[i - 1]); seq.push(d); }
    var want = lv.back ? seq.slice().reverse() : seq;
    var box = bigBox(); box.style.color = 'var(--sky-d)';
    api.stage.appendChild(box);
    api.msg('<span class="em">👀</span> Merk dir die Zahlen!');
    seq.forEach(function (d, i) {
      api.later(function () { box.textContent = d; pop(box); tone(400 + d * 40, 0.1); }, 600 + i * lv.ms);
      api.later(function () { box.textContent = ''; }, 600 + i * lv.ms + lv.ms * 0.75);
    });
    api.later(input, 700 + len * lv.ms);
    function input() {
      api.stage.innerHTML = '';
      api.msg(lv.back ? '<span class="em">🔙</span> Tippe die Zahlen <u>rückwärts</u> ein!' : '<span class="em">⌨️</span> Tippe die Zahlen ein!');
      var out = document.createElement('div'); out.className = 'row'; var got = [], over = false;
      function draw() { out.innerHTML = want.map(function (_, k) { return '<div class="card zahl" style="width:clamp(40px,11vw,64px);font-size:clamp(26px,7vw,40px);' + (k < got.length ? '' : 'border-style:dashed') + '">' + (k < got.length ? got[k] : '') + '</div>'; }).join(''); }
      draw();
      var pad = document.createElement('div'); pad.className = 'grid'; pad.style.cssText = 'grid-template-columns:repeat(3,1fr);max-width:290px;margin-top:6px';
      [1, 2, 3, 4, 5, 6, 7, 8, 9, '⌫', 0, ''].forEach(function (k) {
        var b = document.createElement('button'); b.className = 'card'; b.style.cssText = 'aspect-ratio:1.4;font-size:32px' + (k === '' ? ';visibility:hidden' : '');
        b.textContent = k;
        b.onclick = function () {
          if (over) return;
          if (k === '⌫') { got.pop(); draw(); return; }
          got.push(k); tone(500 + k * 30, 0.06); draw();
          if (got.length === want.length) {
            over = true; var ok = got.join('') === want.join('');
            Array.prototype.forEach.call(out.children, function (c, j) { c.classList.add(got[j] === want[j] ? 'ok' : 'no'); });
            api.msg(ok ? '<span class="em">🎉</span> Richtig!' : '<span class="em">💡</span> Richtig wäre: <span style="font-size:34px;letter-spacing:6px;color:var(--sky-d)">' + want.join(' ') + '</span>');
            if (api.answer(ok)) api.later(task, ok ? 1300 : 2600);
          }
        };
        pad.appendChild(b);
      });
      api.stage.appendChild(out); api.stage.appendChild(pad);
    }
  }
  task();
};
""")

# ================================================================== Namen merken
spiel(id='namen-merken', titel='Namen merken', icon='🐾', thema='Namen merken', sort=12,
      kurz='Tiere stellen sich mit Namen vor. Wie heisst der Hase?',
      uebt='Namen und Gesichter verbinden',
      intro='Neue Tierfreunde stellen sich vor. Merk dir ihre Namen! Danach fragt die Eule nach.',
      levels=[dict(name='Leicht', info='2 Tiere mit Namen', k=2, ms=6000, beide=False, same=False),
              dict(name='Gut', info='3 Tiere mit Namen', k=3, ms=8000, beide=False, same=False),
              dict(name='Mittel', info='4 Tiere mit Namen', k=4, ms=10000, beide=False, same=False),
              dict(name='Schwer', info='5 Tiere, auch umgekehrt gefragt', k=5, ms=12000, beide=True, same=False),
              dict(name='Profi', info='6 ähnliche Tiere, auch umgekehrt', k=6, ms=14000, beide=True, same=True)],
      js=r"""
var NAMEN = ['Knöpfli', 'Wuschel', 'Pünktli', 'Zottel', 'Krümel', 'Flocke', 'Brummi', 'Hüpfer', 'Schnuffel', 'Fridolin', 'Lulu', 'Bobo', 'Tiki', 'Pipo', 'Rübli', 'Sternli', 'Murmel', 'Zwirbel'];
G.play = function (lv, api) {
  function board() {
    api.stage.innerHTML = '';
    var tiere = pick(lv.same ? GESICHTER : BILD.tiere, lv.k), namen = pick(NAMEN, lv.k);
    var cols = lv.k <= 3 ? lv.k : Math.ceil(lv.k / 2), g = grid(cols, Math.ceil(lv.k / cols), 150, 300);
    g.innerHTML = tiere.map(function (p, i) { return '<div class="card karte">' + p + '<span class="nm">' + namen[i] + '</span></div>'; }).join('');
    api.stage.appendChild(g);
    api.msg('<span class="em">👋</span> Das sind neue Freunde. Merk dir ihre Namen!');
    api.watch(lv.ms, function () {
      var q = shuffle(range(lv.k));
      function ask() {
        if (!q.length) { api.later(board, 600); return; }
        var i = q.shift(), rev = lv.beide && Math.random() < .5, over = false;
        api.stage.innerHTML = '';
        var r = document.createElement('div'); r.className = 'row';
        if (!rev) {
          var box = bigBox(); box.textContent = tiere[i]; api.stage.appendChild(box);
          api.msg('Wie heisst dieses Tier?');
          shuffle(range(lv.k)).forEach(function (j) { var b = optBtn(namen[j], true); b.dataset.j = j; r.appendChild(b); });
        } else {
          api.msg('Wer ist <span style="background:var(--sun);border-radius:10px;padding:0 10px">' + namen[i] + '</span> ?');
          shuffle(range(lv.k)).forEach(function (j) { var b = optBtn(tiere[j]); b.dataset.j = j; r.appendChild(b); });
        }
        Array.prototype.forEach.call(r.children, function (b) {
          b.onclick = function () {
            if (over) return; over = true;
            var ok = +b.dataset.j === i;
            b.classList.add(ok ? 'ok' : 'no'); if (!ok) { b.classList.add('shake'); r.querySelector('[data-j="' + i + '"]').classList.add('hint'); }
            api.msg(ok ? '<span class="em">🎉</span> Richtig, das ist ' + namen[i] + '!' : '<span class="em">💡</span> Das ist ' + namen[i] + ' <span class="em">' + tiere[i] + '</span>');
            if (api.answer(ok)) api.later(ask, ok ? 1200 : 2300);
          };
        });
        api.stage.appendChild(r);
      }
      ask();
    });
  }
  board();
};
""")


# Die Schrift steckt direkt in jedem Spiel: Das Spielfenster der Kinder ist abgeschottet und darf keine Schrift nachladen.
def schrift():
    import base64
    with open(os.path.join(REPO, 'schriften', 'patrick-hand.woff2'), 'rb') as f: return 'data:font/woff2;base64,' + base64.b64encode(f.read()).decode()


def game_html(s):
    meta = json.dumps(s['sterne'], ensure_ascii=False).replace('"', '&quot;')
    g = {'title': s['titel'], 'icon': s['icon'], 'intro': s['intro'], 'n': s['n'], 'levels': s['levels']}
    return ('<!doctype html>\n<html lang="de-CH">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
            f'<meta name="knobelnest-sterne" content="{meta}">\n'
            f'<title>{s["titel"]}</title>\n<style>{CSS.replace("__SCHRIFT__", schrift())}</style>\n</head>\n<body>\n<div id="app"></div>\n'
            f'<script>\n{POOL}\nvar G = {json.dumps(g, ensure_ascii=False)};\n{s["js"]}\n{FRAME}\n</script>\n</body>\n</html>\n')


def stub_html(s):
    # Kurzer Eintrag für die Tabelle «games»: das Portal öffnet gedaechtnis/<id>.html
    meta = json.dumps(s['sterne'], ensure_ascii=False).replace('"', '&quot;')
    return ('<!doctype html><html lang="de-CH"><head><meta charset="utf-8">'
            f'<meta name="knobelnest-url" content="gedaechtnis/{s["id"]}.html">'
            f'<meta name="knobelnest-sterne" content="{meta}">'
            f'<title>{s["titel"]}</title></head><body><p>{s["titel"]}: Dieses Spiel liegt in der Klassenkiste im Ordner gedaechtnis/.</p></body></html>')


def katalog():
    return [{'id': s['id'], 'title': s['titel'], 'icon': s['icon'], 'thema': s['thema'], 'kurz': s['kurz'], 'uebt': s['uebt'],
             'sort': s['sort'], 'levels': [{'name': l['name'], 'info': l['info']} for l in s['levels']],
             'pack': {'title': s['titel'], 'description': s['kurz'], 'fach': 'Gedächtnis', 'thema': s['thema'], 'stufe': '1.–6. Klasse',
                      'sort': s['sort'], 'html': stub_html(s)}} for s in SPIELE]


# ------------------------------------------------------------------ Werkzeug «Gedächtniskiste»
TOOL = r"""<!doctype html>
<html lang="de-CH">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Gedächtniskiste</title>
<style>
@font-face{font-family:"Patrick Hand";src:url(../schriften/patrick-hand.woff2) format("woff2");font-display:swap}
*{box-sizing:border-box}
:root{--bg:#f4f9fd;--ink:#1f2421;--soft:#5f6963;--line:#e1edf7;--line2:#c5d8e8;--gold:#d6ad45;--gold-d:#c4952f;
  --sky:#dcf0fd;--sky-d:#3f78a8;--leaf:#e9f1e3;--rose:#fcefed;--sun:#fbf3dc;--ok:#5f9a4a;
  --sch:0 10px 26px rgba(63,120,168,.18),0 2px 6px rgba(63,120,168,.10);--sch-h:0 16px 34px rgba(63,120,168,.26),0 3px 8px rgba(63,120,168,.14)}
html,body{margin:0}
body{background:radial-gradient(1200px 600px at 0% -10%,#e3f1fc 0%,transparent 60%),radial-gradient(900px 600px at 110% 100%,#fbf3dc 0%,transparent 60%),var(--bg);
  color:var(--ink);font-family:"Patrick Hand","Segoe Print","Comic Sans MS",cursive;font-size:19px;line-height:1.35;min-height:100vh}
button{font:inherit;color:inherit;cursor:pointer}
.top{position:sticky;top:0;z-index:5;background:rgba(244,249,253,.92);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);box-shadow:0 1px 0 rgba(214,173,69,.35)}
.top-in{max-width:1180px;margin:0 auto;display:flex;align-items:center;gap:14px;padding:10px 24px;min-height:84px}
.marke{display:flex;align-items:center;gap:12px;flex:1}
.marke img{width:58px;height:58px;border-radius:50%;border:3px solid var(--gold);box-shadow:inset 0 0 0 3px #fff,var(--sch);background:#fff;object-fit:cover}
.marke b{display:block;font-weight:400;font-size:28px;line-height:1}
.marke b i{font-style:normal;color:var(--gold);font-size:.55em;vertical-align:super;margin-left:4px}
.marke small{color:var(--soft);font-size:16px}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:46px;padding:0 18px;border:2px solid var(--ink);border-radius:14px;background:#fff;font-size:18px;
  box-shadow:var(--sch);transition:transform .15s,box-shadow .15s;text-decoration:none;color:var(--ink)}
.btn:hover{transform:translateY(-2px);box-shadow:var(--sch-h)}.btn:active{transform:translateY(1px)}
.btn.primary{background:var(--sky)}.btn.sun{background:var(--sun)}.btn.sm{min-height:40px;font-size:16px;border-radius:11px;padding:0 14px;box-shadow:0 4px 12px rgba(63,120,168,.14)}
.btn:disabled{opacity:.55;cursor:default;transform:none}
main{max-width:1180px;margin:0 auto;padding:24px 24px 60px}
.banner{display:flex;flex-wrap:wrap;gap:22px 30px;align-items:center;background:linear-gradient(180deg,#fff 0%,#f3faff 100%);border:1.5px solid var(--line);border-radius:32px;padding:26px 30px;box-shadow:var(--sch)}
.ring{flex:none;width:130px;height:130px;border-radius:50%;display:grid;place-items:center;font-size:68px;background:var(--sun);border:3px solid var(--gold);box-shadow:inset 0 0 0 7px #fff,0 8px 18px rgba(63,120,168,.18)}
.banner .txt{flex:1 1 340px}
.klein{font-size:16px;letter-spacing:.1em;text-transform:uppercase;color:var(--sky-d)}
.banner h1{margin:2px 0 6px;font-weight:400;font-size:46px;line-height:1}
.banner h1::after{content:" ✦";color:var(--gold);font-size:.5em;vertical-align:super}
.banner p{margin:0;color:var(--soft)}
.zahlen{display:flex;gap:10px;flex-wrap:wrap;margin-top:12px}
.zahlen span{background:#fff;border:1.5px solid var(--line2);border-radius:999px;padding:3px 14px;font-size:17px}
.zahlen b{font-weight:400;color:var(--sky-d)}
.frei{display:flex;flex-direction:column;gap:8px;align-items:flex-start;min-width:230px}
.frei .stand{font-size:20px}
.note{margin-top:18px;background:var(--sun);border:1.5px dashed var(--gold);border-radius:20px;padding:14px 18px;color:#4a3d1a;display:flex;flex-wrap:wrap;gap:10px 16px;align-items:center}
.note p{margin:0;flex:1 1 300px}
.deko{text-align:center;color:var(--gold);letter-spacing:.4em;font-size:14px;margin:26px 0 8px}
.filter{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin-bottom:20px}
.chip{border:1.5px solid var(--line2);background:#fff;border-radius:999px;padding:6px 16px;font-size:18px;min-height:42px}
.chip[aria-pressed="true"]{background:var(--sky);border-color:var(--ink)}
.spiele{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:20px}
.sp{display:flex;flex-direction:column;gap:10px;background:linear-gradient(180deg,#fff 0%,#fff 70%,#f7fbfe 100%);border:1.5px solid var(--line);border-radius:28px;padding:20px 20px 16px;box-shadow:var(--sch);transition:transform .2s,box-shadow .2s}
.sp:hover{transform:translateY(-4px);box-shadow:var(--sch-h)}
.sp-kopf{display:flex;gap:14px;align-items:center}
.sp .ic{flex:none;width:76px;height:76px;border-radius:50%;display:grid;place-items:center;font-size:40px;border:3px solid var(--gold);box-shadow:inset 0 0 0 5px #fff,0 6px 14px rgba(63,120,168,.15);transition:transform .35s}
.sp:hover .ic{transform:rotate(-6deg) scale(1.05)}
.sp h3{margin:0;font-weight:400;font-size:27px;line-height:1.05}
.sp h3::after{content:"✦ ✧ ✦";display:block;font-size:10px;letter-spacing:.3em;color:var(--gold);margin-top:5px}
.bereich{font-size:15px;color:var(--sky-d);letter-spacing:.05em}
.sp p{margin:0}
.sp .uebt{color:var(--soft);font-size:17px}
.stufen{list-style:none;margin:2px 0 0;padding:0;display:flex;flex-direction:column;gap:4px}
.stufen button{width:100%;display:flex;align-items:center;gap:10px;text-align:left;border:1.5px solid transparent;background:none;border-radius:12px;padding:3px 8px;font-size:17px}
.stufen button:hover{background:var(--sky);border-color:var(--line2)}
.stufen .n{flex:none;width:28px;height:28px;border-radius:50%;display:grid;place-items:center;font-size:16px;border:2px solid var(--gold);background:#fff}
.stufen .nm{width:62px;flex:none}
.stufen .inf{color:var(--soft)}
.sp-fuss{display:flex;flex-wrap:wrap;gap:8px;margin-top:auto;padding-top:10px;border-top:1.5px dashed rgba(214,173,69,.6)}
.rel{flex:1 1 180px;border:1.5px solid var(--line2);border-radius:12px;background:#f7fbfe;min-height:40px;font-size:16px;padding:0 10px}
.rel.on{background:var(--leaf);border-color:#7ea56a;color:#3f6b2e}
.rel[disabled]{cursor:default;opacity:.75}
.tipps{margin-top:30px;display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:16px}
.tipp{background:#fff;border:1.5px solid var(--line);border-radius:24px;padding:18px 20px;box-shadow:var(--sch)}
.tipp b{display:block;font-weight:400;font-size:22px;margin-bottom:4px}
.tipp p{margin:0;color:var(--soft)}
.ov{position:fixed;inset:0;z-index:20;background:var(--bg);display:flex;flex-direction:column}
.ov[hidden]{display:none}
.ov-bar{display:flex;flex-wrap:wrap;align-items:center;gap:10px;padding:10px 16px;background:#fff;box-shadow:0 1px 0 rgba(214,173,69,.45)}
.ov-bar b{font-weight:400;font-size:24px;margin-right:auto}
.ov-bar .lvb{min-width:40px;min-height:40px;border-radius:50%;border:2px solid var(--gold);background:#fff;font-size:17px}
.ov-bar .lvb[aria-pressed="true"]{background:var(--sun)}
.ov iframe{flex:1;border:0;width:100%}
.toast{position:fixed;left:50%;bottom:24px;transform:translateX(-50%);background:var(--ink);color:#fff;border-radius:14px;padding:10px 18px;z-index:30;font-size:18px}
@media (max-width:640px){.top-in{padding:8px 14px;min-height:70px}.marke img{width:46px;height:46px}.marke b{font-size:23px}main{padding:16px 14px 40px}
  .banner{padding:20px}.banner h1{font-size:36px}.ring{width:96px;height:96px;font-size:50px}.spiele{grid-template-columns:1fr}.ov-bar b{font-size:20px;width:100%}}
</style>
</head>
<body>
<header class="top"><div class="top-in">
  <div class="marke"><img src="../bilder/eule.webp" alt=""><span><b>Gedächtniskiste<i>✦</i></b><small id="kl">für Lehrpersonen</small></span></div>
  <button class="btn sm" id="zur">← Klassenkiste</button>
</div></header>
<main>
  <section class="banner">
    <span class="ring" aria-hidden="true">🧠</span>
    <div class="txt">
      <span class="klein">Werkzeug</span>
      <h1>Gedächtniskiste</h1>
      <p>Spiele, die das Gedächtnis der Kinder fördern: Bilder, Orte, Reihenfolgen und Namen merken. Jedes Spiel hat fünf Stufen, von leicht bis Profi. Probieren Sie die Spiele hier selbst aus oder spielen Sie sie mit der ganzen Klasse an der Wandtafel.</p>
      <div class="zahlen" id="zahlen"></div>
    </div>
    <div class="frei" id="frei"></div>
  </section>
  <div id="note"></div>
  <div class="deko">✦ ✧ ✦</div>
  <nav class="filter" id="filter" aria-label="Bereiche"></nav>
  <section class="spiele" id="spiele"></section>
  <div class="deko">✦ ✧ ✦</div>
  <section class="tipps">
    <div class="tipp"><b>🧑‍🏫 An der Wandtafel</b><p>Öffnen Sie ein Spiel mit «Ausprobieren» und tippen Sie auf «Vollbild». Die Klasse ruft die Antworten, ein Kind tippt.</p></div>
    <div class="tipp"><b>📈 Stufe für Stufe</b><p>Kinder sehen ihre Sterne pro Stufe. Ab 7 von 10 richtig erscheint der Knopf «Nächste Stufe».</p></div>
    <div class="tipp"><b>⏱️ Kurz und oft</b><p>Eine Runde dauert 2 bis 4 Minuten. Am meisten bringt es, mehrmals pro Woche kurz zu üben.</p></div>
  </section>
</main>
<div class="ov" id="ov" hidden>
  <div class="ov-bar"><button class="btn sm" id="ovZu">✕ Schliessen</button><b id="ovT"></b><span id="ovLv"></span><button class="btn sm" id="ovVoll">Vollbild</button></div>
  <iframe id="ovF" title="Spiel" allow="fullscreen; autoplay"></iframe>
</div>
<script>
var KAT = __KATALOG__, FARBE = __FARBEN__;
var B = null; try { B = window.parent !== window && window.parent.knGd ? window.parent.knGd : null; } catch (e) {}
var DBG = {}, FIL = 'alle', BUSY = false, CUR = null;
function $(id) { return document.getElementById(id); }
function h(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
function toast(t) { var d = document.createElement('div'); d.className = 'toast'; d.textContent = t; document.body.appendChild(d); setTimeout(function () { d.remove(); }, 2600); }
$('zur').onclick = function () { if (B && B.back) B.back(); else location.href = '../'; };
if (B && B.className) $('kl').textContent = 'Klasse ' + B.className;
var bereiche = []; KAT.forEach(function (g) { if (bereiche.indexOf(g.thema) < 0) bereiche.push(g.thema); });
$('zahlen').innerHTML = '<span><b>' + KAT.length + '</b> Spiele</span><span><b>' + (KAT.length * 5) + '</b> Stufen</span><span><b>' + bereiche.length + '</b> Bereiche</span>';

function filter() {
  $('filter').innerHTML = ['alle'].concat(bereiche).map(function (b) {
    var n = b === 'alle' ? KAT.length : KAT.filter(function (g) { return g.thema === b; }).length;
    return '<button class="chip" aria-pressed="' + (FIL === b) + '" data-f="' + h(b) + '">' + (b === 'alle' ? 'Alle Spiele' : h(b)) + ' · ' + n + '</button>';
  }).join('');
}
function relBtn(g) {
  if (!B) return '';
  var d = DBG[g.title.toLowerCase()];
  if (!d) return '<button class="rel" disabled>' + (B.admin ? 'Noch nicht in der Klassenkiste' : 'Für Sie noch nicht freigeschaltet') + '</button>';
  return '<button class="rel' + (d.on ? ' on' : '') + '" data-rel="' + h(d.id) + '">' + (d.on ? '✓ Für die Klasse freigegeben' : 'Für die Klasse gesperrt · freigeben') + '</button>';
}
function cards() {
  $('spiele').innerHTML = KAT.filter(function (g) { return FIL === 'alle' || g.thema === FIL; }).map(function (g) {
    return '<article class="sp"><div class="sp-kopf"><span class="ic" style="background:' + (FARBE[g.thema] || '#dcf0fd') + '">' + g.icon + '</span><div><span class="bereich">' + h(g.thema) + '</span><h3>' + h(g.title) + '</h3></div></div>' +
      '<p>' + h(g.kurz) + '</p><p class="uebt">Übt: ' + h(g.uebt) + '</p>' +
      '<ol class="stufen">' + g.levels.map(function (l, i) { return '<li><button data-play="' + g.id + '" data-lv="' + (i + 1) + '" title="Stufe ' + (i + 1) + ' ausprobieren"><span class="n">' + (i + 1) + '</span><span class="nm">' + h(l.name) + '</span><span class="inf">' + h(l.info) + '</span></button></li>'; }).join('') + '</ol>' +
      '<div class="sp-fuss"><button class="btn sm primary" data-play="' + g.id + '">▶ Ausprobieren</button>' + relBtn(g) + '</div></article>';
  }).join('');
}
function freiBox() {
  if (!B) { $('frei').innerHTML = ''; return; }
  var have = KAT.filter(function (g) { return DBG[g.title.toLowerCase()]; }), on = have.filter(function (g) { return DBG[g.title.toLowerCase()].on; });
  $('frei').innerHTML = have.length ? '<span class="stand">' + on.length + ' von ' + have.length + ' Spielen für die Klasse freigegeben</span>' +
    '<button class="btn sun" data-all="1"' + (on.length === have.length ? ' disabled' : '') + '>✦ Alle freigeben</button>' +
    (on.length ? '<button class="btn sm" data-all="0">Alle sperren</button>' : '') : '';
  var miss = KAT.length - have.length, o = '';
  if (B.admin && miss) o = '<div class="note"><p><b>Admin:</b> ' + miss + (miss === 1 ? ' Spiel ist' : ' Spiele sind') + ' noch nicht in der Klassenkiste. Mit einem Tipp nehmen Sie ' + (miss === 1 ? 'es' : 'sie') + ' auf (Fach «Gedächtnis»). Danach können Sie sie wie alle Spiele den Lehrpersonen zuteilen.</p><button class="btn primary" data-inst>Spiele in die Klassenkiste aufnehmen</button></div>';
  else if (!B.admin && miss === KAT.length) o = '<div class="note"><p>Die Spiele können Sie hier ausprobieren. Damit Ihre Kinder sie spielen können, muss die Administratorin sie Ihnen noch freischalten.</p></div>';
  $('note').innerHTML = o;
}
function draw() { filter(); cards(); freiBox(); }
async function load() {
  if (!B) return draw();
  try { var list = await B.games(); DBG = {}; list.forEach(function (g) { DBG[String(g.title).toLowerCase()] = g; }); } catch (e) { console.warn(e); }
  draw();
}
function open(id, lv) {
  var g = KAT.filter(function (x) { return x.id === id; })[0]; if (!g) return; CUR = g;
  $('ovT').textContent = g.icon + ' ' + g.title;
  $('ovLv').innerHTML = '<span style="color:var(--soft);font-size:16px;margin-right:6px">Stufe</span>' + g.levels.map(function (l, i) { return '<button class="lvb" data-ovlv="' + (i + 1) + '" title="' + h(l.name + ': ' + l.info) + '" aria-pressed="' + (lv === i + 1) + '">' + (i + 1) + '</button>'; }).join(' ');
  $('ovF').src = g.id + '.html?vorschau' + (lv ? '&stufe=' + lv : '') + '&t=' + Date.now();
  $('ov').hidden = false; document.body.style.overflow = 'hidden';
}
function close() { $('ov').hidden = true; $('ovF').src = 'about:blank'; document.body.style.overflow = ''; try { if (document.fullscreenElement) document.exitFullscreen(); } catch (e) {} }
$('ovZu').onclick = close;
$('ovVoll').onclick = function () { var e = $('ov'); try { (e.requestFullscreen || e.webkitRequestFullscreen).call(e); } catch (x) {} };
document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !$('ov').hidden && !document.fullscreenElement) close(); });
document.addEventListener('click', async function (e) {
  var t = e.target.closest('button'); if (!t) return;
  if (t.dataset.f) { FIL = t.dataset.f; filter(); cards(); return; }
  if (t.dataset.play) { open(t.dataset.play, t.dataset.lv ? +t.dataset.lv : 0); return; }
  if (t.dataset.ovlv) { open(CUR.id, +t.dataset.ovlv); return; }
  if (BUSY || !B) return;
  if (t.dataset.rel) {
    var d = null; Object.keys(DBG).forEach(function (k) { if (DBG[k].id === t.dataset.rel) d = DBG[k]; });
    if (!d) return; d.on = !d.on; cards(); freiBox();
    try { await B.rel(d.id, d.on); } catch (x) { d.on = !d.on; cards(); freiBox(); toast('Das hat nicht geklappt.'); }
    return;
  }
  if (t.dataset.all) {
    var on = t.dataset.all === '1', todo = Object.keys(DBG).map(function (k) { return DBG[k]; }).filter(function (d) { return d.on !== on; });
    BUSY = true; todo.forEach(function (d) { d.on = on; }); draw();
    try { for (var i = 0; i < todo.length; i++) await B.rel(todo[i].id, on); toast(on ? 'Alle Spiele freigegeben' : 'Alle Spiele gesperrt'); }
    catch (x) { toast('Das hat nicht geklappt.'); await load(); }
    BUSY = false; return;
  }
  if (t.hasAttribute('data-inst')) {
    BUSY = true; t.disabled = true; t.textContent = 'Wird aufgenommen …';
    try { var r = await B.install(KAT.map(function (g) { return g.pack; })); toast(r.neu + ' Spiele aufgenommen' + (r.aktualisiert ? ', ' + r.aktualisiert + ' aktualisiert' : '')); }
    catch (x) { console.warn(x); toast('Das hat nicht geklappt.'); }
    BUSY = false; await load();
  }
});
load();
</script>
</body>
</html>
"""


if __name__ == '__main__':
    os.makedirs(ZIEL, exist_ok=True)
    for s in SPIELE:
        with open(os.path.join(ZIEL, s['id'] + '.html'), 'w', encoding='utf-8') as f: f.write(game_html(s))
    kat = katalog()
    tool = TOOL.replace('__KATALOG__', json.dumps(kat, ensure_ascii=False).replace('</', '<\\/')).replace('__FARBEN__', json.dumps(dict(BEREICHE), ensure_ascii=False))
    with open(os.path.join(ZIEL, 'index.html'), 'w', encoding='utf-8') as f: f.write(tool)
    paket = {'format': 'knobelnest-spielpaket', 'games': [k['pack'] for k in kat]}
    with open(os.path.join(HIER, 'gedaechtnis-spielpaket.json'), 'w', encoding='utf-8') as f: json.dump(paket, f, ensure_ascii=False, indent=1)
    print(len(SPIELE), 'Spiele und die Gedächtniskiste gebaut (Ordner gedaechtnis/)')
