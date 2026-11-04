# Baut die Gedächtnisspiele der Klassenkiste und das Spielpaket zum Hochladen.
# Aufruf im Repo-Hauptordner:  python3 werkstatt/spiele/gedaechtnis/bauen.py
# Ergebnis: werkstatt/spiele/gedaechtnis/<spiel>.html und gedaechtnis-spielpaket.json
# Das Paket lädt die Lehrerin in der Verwaltung unter «Spielpaket importieren» hoch.
# In der Klassenkiste zeigt das Portal die Punkte oben an, darum dort keine eigenen Punkte.
# Spielprotokoll: window.knobelnest (answer, level, round, sterne), siehe shimMain() in app.js.
import json, os

HIER = os.path.dirname(os.path.abspath(__file__))

CSS = r"""
*{box-sizing:border-box}
:root{--bg:#fdf8ee;--card:#fff;--ink:#2b2a33;--muted:#6b6878;--gold:#e0a526;--teal:#2a7f8f;--ok:#2e9e5b;--no:#d9534f;--line:#ece3cf}
html,body{margin:0;height:100%}
body{background:var(--bg);color:var(--ink);font-family:"Fredoka","Andika","Nunito","Comic Sans MS",system-ui,sans-serif;font-size:18px;
  -webkit-tap-highlight-color:transparent;user-select:none;-webkit-user-select:none;touch-action:manipulation}
button{font:inherit;color:inherit;cursor:pointer;border:0;background:none}
#app{min-height:100%;display:flex;flex-direction:column;align-items:center;padding:12px 16px 24px}
.top{width:100%;max-width:900px;display:flex;align-items:center;gap:10px;margin-bottom:8px}
.top .t{flex:1;font-weight:700;font-size:19px;text-align:center}
.pill{background:var(--card);border:2px solid var(--line);border-radius:999px;padding:8px 14px;font-weight:600;min-height:44px}
.pill:active{transform:scale(.96)}
.hero{text-align:center;margin:10px 0 6px}
.hero .big{font-size:64px;line-height:1}
.hero h1{margin:6px 0 4px;font-size:30px}
.hero p{margin:0 auto;max-width:520px;color:var(--muted)}
.lvs{width:100%;max-width:560px;display:grid;gap:10px;margin-top:16px}
.lv{display:flex;align-items:center;gap:14px;background:var(--card);border:3px solid var(--line);border-radius:18px;padding:12px 16px;text-align:left;min-height:72px}
.lv:hover{border-color:var(--gold)}
.lv:active{transform:scale(.98)}
.lv .n{flex:none;width:48px;height:48px;border-radius:50%;display:grid;place-items:center;font-weight:700;font-size:22px;color:#fff}
.lv .tx{flex:1}.lv .tx b{display:block;font-size:19px}.lv .tx span{color:var(--muted);font-size:15px}
.stars{color:var(--gold);font-size:22px;letter-spacing:2px;white-space:nowrap}.stars .off{color:#ddd3bd}
.msg{min-height:58px;font-size:22px;font-weight:600;text-align:center;margin:4px 0 10px;max-width:700px;line-height:1.35}
.msg .em{font-size:40px;vertical-align:middle;margin:0 4px}
.dots{display:flex;gap:5px;justify-content:center;margin-bottom:6px}
.dots i{width:12px;height:12px;border-radius:50%;background:#e6dcc6;display:block}.dots i.ok{background:var(--ok)}.dots i.no{background:var(--no)}
.stage{width:100%;max-width:900px;display:flex;flex-direction:column;align-items:center;gap:14px}
.bar{width:min(420px,90%);height:12px;border-radius:99px;background:#eadfc8;overflow:hidden}
.bar i{display:block;height:100%;background:var(--gold);width:100%;transition:width linear}
.go{background:var(--teal);color:#fff;border-radius:16px;padding:12px 22px;font-size:20px;font-weight:700;min-height:52px;box-shadow:0 4px 0 #1d5d69}
.go:active{transform:translateY(2px);box-shadow:0 2px 0 #1d5d69}
.go.alt{background:var(--card);color:var(--ink);border:3px solid var(--line);box-shadow:none}
.row{display:flex;gap:10px;flex-wrap:wrap;justify-content:center}
.card{background:var(--card);border:3px solid var(--line);border-radius:16px;display:grid;place-items:center;aspect-ratio:1;font-size:clamp(28px,7vw,54px);line-height:1}
.grid{display:grid;gap:clamp(6px,1.6vw,12px);width:100%;margin:0 auto}
.end{background:var(--card);border:3px solid var(--line);border-radius:22px;padding:22px;text-align:center;max-width:460px;width:100%}
.end .big{font-size:60px}.end h2{margin:6px 0}.end p{color:var(--muted);margin:4px 0 16px}
.shake{animation:sh .35s}@keyframes sh{25%{transform:translateX(-6px)}75%{transform:translateX(6px)}}
.pop{animation:pp .3s}@keyframes pp{50%{transform:scale(1.12)}}
@media (max-height:620px){.hero .big{font-size:46px}.hero h1{font-size:24px}.msg{min-height:48px;font-size:19px}}
"""

# Gemeinsamer Rahmen: Stufen-Auswahl, Sterne, Töne, Runde mit 10 Aufgaben, Abschluss.
FRAME = r"""
var KN = window.knobelnest || { answer: function () {}, level: function () {}, round: function () {}, sterne: function () { return { have: 0, max: 3 }; } };
var ST = {}; try { ST = JSON.parse(localStorage.getItem('gd') || '{}') || {}; } catch (e) {}
function save() { try { localStorage.setItem('gd', JSON.stringify(ST)); } catch (e) {} }
var app = document.getElementById('app'), TM = [], RUN = 0, AC = null, CUR = -1;
var LV_COL = ['#5fb36b', '#3e9fc0', '#e0a526', '#e5793b', '#c4505e'];
function h(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
function shuffle(a) { a = a.slice(); for (var i = a.length - 1; i > 0; i--) { var j = Math.floor(Math.random() * (i + 1)), t = a[i]; a[i] = a[j]; a[j] = t; } return a; }
function pick(a, n) { return shuffle(a).slice(0, n); }
function rnd(a, b) { return a + Math.floor(Math.random() * (b - a + 1)); }
function stopAll() { TM.forEach(clearTimeout); TM = []; }
function tone(f, d, type, vol) {
  if (ST.mute) return;
  try {
    AC = AC || new (window.AudioContext || window.webkitAudioContext)();
    if (AC.state === 'suspended') AC.resume();
    var o = AC.createOscillator(), g = AC.createGain(), t = AC.currentTime;
    o.type = type || 'sine'; o.frequency.value = f;
    g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(vol || 0.22, t + 0.02); g.gain.exponentialRampToValueAtTime(0.0001, t + d);
    o.connect(g); g.connect(AC.destination); o.start(t); o.stop(t + d + 0.05);
  } catch (e) {}
}
function good() { tone(660, 0.12); setTimeout(function () { tone(990, 0.2); }, 110); }
function bad() { tone(200, 0.3, 'triangle', 0.18); }
function stars(have, max) { var o = ''; for (var i = 0; i < max; i++) o += i < have ? '★' : '<span class="off">★</span>'; return '<span class="stars">' + o + '</span>'; }
function sndBtn() { return '<button class="pill" data-snd aria-label="Ton ein oder aus">' + (ST.mute ? '🔇' : '🔊') + '</button>'; }
app.addEventListener('click', function (e) {
  var b = e.target.closest('[data-snd]'); if (!b) return;
  ST.mute = !ST.mute; save(); b.textContent = ST.mute ? '🔇' : '🔊';
});
window.addEventListener('knobelnest-sterne', function () { if (CUR < 0) menu(); });

function menu() {
  stopAll(); RUN++; CUR = -1; KN.level(null);
  var o = '<div class="top"><span style="flex:1"></span>' + sndBtn() + '</div><div class="hero"><div class="big">' + G.icon + '</div><h1>' + h(G.title) + '</h1><p>' + G.intro + '</p></div><div class="lvs">';
  G.levels.forEach(function (lv, i) {
    var s = KN.sterne('Stufe ' + (i + 1));
    o += '<button class="lv" data-lv="' + i + '"><span class="n" style="background:' + LV_COL[i] + '">' + (i + 1) + '</span><span class="tx"><b>' + h(lv.name) + '</b><span>' + h(lv.info) + '</span></span>' + stars(Math.min(s.have, s.max || 3), s.max || 3) + '</button>';
  });
  app.innerHTML = o + '</div>';
  Array.prototype.forEach.call(app.querySelectorAll('[data-lv]'), function (b) { b.onclick = function () { tone(520, 0.08); start(+b.dataset.lv); }; });
}

function start(i) {
  stopAll(); var run = ++RUN, lv = G.levels[i], res = [], N = G.n || 0; CUR = i;
  KN.level('Stufe ' + (i + 1));
  app.innerHTML = '<div class="top"><button class="pill" data-back>← Stufen</button><span class="t">Stufe ' + (i + 1) + ' · ' + h(lv.name) + '</span>' + sndBtn() + '</div>' +
    (N && !window.knobelnest ? '<div class="dots" id="dots"></div>' : '') + '<div class="msg" id="msg"></div><div class="stage" id="stage"></div>';
  app.querySelector('[data-back]').onclick = menu;
  var stage = document.getElementById('stage'), msgEl = document.getElementById('msg');
  function dots() { if (!N || !document.getElementById('dots')) return; var o = ''; for (var k = 0; k < N; k++) o += '<i class="' + (k < res.length ? (res[k] ? 'ok' : 'no') : '') + '"></i>'; document.getElementById('dots').innerHTML = o; }
  dots();
  var api = {
    stage: stage,
    alive: function () { return run === RUN; },
    msg: function (t) { msgEl.innerHTML = t; },
    later: function (fn, ms) { TM.push(setTimeout(function () { if (run === RUN) fn(); }, ms)); },
    // Antwort melden. Gibt false zurück, wenn die Runde fertig ist.
    answer: function (ok, quiet) {
      KN.answer(!!ok);
      if (!quiet) { if (ok) good(); else bad(); }
      if (!N) return true;
      res.push(!!ok); dots();
      if (res.length >= N) { api.later(function () { end(i, res.filter(Boolean).length + ' von ' + N + ' richtig', res.filter(Boolean).length / N); }, 1500); return false; }
      return true;
    },
    // Für Spiele ohne feste Anzahl Aufgaben (Paare finden)
    done: function (line, q) { KN.round(); end(i, line, q); },
    // Merkzeit mit Balken und Knopf «Ich bin bereit»
    watch: function (ms, after, host) {
      var w = document.createElement('div'); w.className = 'stage'; w.style.gap = '10px';
      w.innerHTML = '<div class="bar"><i></i></div><button class="go alt">Ich bin bereit ✓</button>';
      (host || stage).appendChild(w);
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
    '<button class="go" data-again>Nochmal</button>' + (next && q >= 0.7 ? '<button class="go" data-next>Nächste Stufe →</button>' : '') + '<button class="go alt" data-menu>Stufen</button></div></div></div>';
  app.querySelector('[data-again]').onclick = function () { start(i); };
  if (app.querySelector('[data-next]')) app.querySelector('[data-next]').onclick = function () { start(i + 1); };
  app.querySelector('[data-menu]').onclick = menu;
  if (q >= 0.7) { good(); setTimeout(function () { tone(1320, 0.25); }, 260); }
}
menu();
"""

# Bildersammlungen (nur Emojis, damit nichts nachgeladen werden muss)
POOL = r"""
var BILD = {
  tiere: ['🐶','🐱','🐭','🐰','🦊','🐻','🐼','🐨','🐯','🦁','🐮','🐷','🐸','🐵','🐔','🐧','🦉','🐢','🐙','🦋','🐝','🐞','🐟','🐘'],
  essen: ['🍎','🍐','🍊','🍋','🍌','🍉','🍇','🍓','🍒','🥕','🌽','🥦','🍄','🧀','🥨','🍕','🍦','🍪','🥚','🍞'],
  sachen: ['⚽','🎈','✏️','🔑','🎒','⏰','📚','🧸','🚲','☂️','🎁','🔔','🪁','🎨','✂️','🧦','👓','🎩','🕯️','🧩'],
  natur: ['🌞','🌙','⭐','☁️','🌈','❄️','🔥','🌵','🌲','🌻','🌷','🍁','🌍','⛄','🌊','🐚']
};
var ALLE = [].concat(BILD.tiere, BILD.essen, BILD.sachen, BILD.natur);
"""

SPIELE = []

def spiel(datei, titel, beschreibung, thema, sterne, js, sort):
    SPIELE.append(dict(datei=datei, titel=titel, beschreibung=beschreibung, thema=thema, sterne=sterne, js=js, sort=sort))

# ---------------------------------------------------------------- 1. Paare finden
spiel('paare-finden', 'Paare finden', 'Bildpaare aufdecken und merken, wo welches Bild liegt.', 'Bilder merken',
      {'modus': 'sammeln', 'pro': 'runde', 'max': 3, 'proLevel': True}, r"""
var G = { title: 'Paare finden', icon: '🃏', intro: 'Deck zwei Karten auf. Sind es gleiche Bilder? Merk dir, wo die Bilder liegen!',
  levels: [
    { name: 'Leicht', info: '3 Paare', p: 3, c: 3, set: 'essen' },
    { name: 'Gut', info: '4 Paare', p: 4, c: 4, set: 'tiere' },
    { name: 'Mittel', info: '6 Paare', p: 6, c: 4, set: 'sachen' },
    { name: 'Schwer', info: '8 Paare', p: 8, c: 4, set: 'mix' },
    { name: 'Profi', info: '10 Paare, ähnliche Tiere', p: 10, c: 5, set: 'tiere' }
  ],
  play: function (lv, api, li) {
    var set = lv.set === 'mix' ? ALLE : BILD[lv.set], pics = pick(set, lv.p), cards = shuffle(pics.concat(pics));
    var rows = Math.ceil(cards.length / lv.c), first = null, lock = false, moves = 0, found = 0, key = 'paare' + li;
    var best = (ST.best || {})[key];
    api.msg('Finde alle Paare! <span style="color:var(--muted);font-size:17px" id="mv">Züge: 0' + (best ? ' · Rekord: ' + best : '') + '</span>');
    var g = document.createElement('div'); g.className = 'grid';
    g.style.gridTemplateColumns = 'repeat(' + lv.c + ',1fr)';
    g.style.maxWidth = 'min(100%, calc((100vh - 190px) * ' + lv.c + ' / ' + rows + '), ' + (lv.c * 130) + 'px)';
    cards.forEach(function (p, k) {
      var b = document.createElement('button'); b.className = 'card'; b.dataset.p = p; b.setAttribute('aria-label', 'Karte ' + (k + 1));
      b.style.background = 'linear-gradient(135deg,#f3c94f,#e0a526)'; b.innerHTML = '<span style="font-size:.6em;color:#fff8">✦</span>';
      b.onclick = function () { turn(b); };
      g.appendChild(b);
    });
    api.stage.appendChild(g);
    function show(b, on) { b.style.background = on ? '#fff' : 'linear-gradient(135deg,#f3c94f,#e0a526)'; b.innerHTML = on ? b.dataset.p : '<span style="font-size:.6em;color:#fff8">✦</span>'; b.classList.toggle('pop', on); }
    function turn(b) {
      if (lock || b.dataset.open) return;
      b.dataset.open = 1; show(b, true); tone(520 + (first ? 120 : 0), 0.08);
      if (!first) { first = b; return; }
      moves++; document.getElementById('mv').textContent = 'Züge: ' + moves + (best ? ' · Rekord: ' + best : '');
      var a = first; first = null;
      if (a.dataset.p === b.dataset.p) {
        found++; api.answer(true);
        a.style.borderColor = b.style.borderColor = 'var(--ok)';
        if (found === lv.p) {
          var rec = !best || moves < best; ST.best = ST.best || {}; if (rec) { ST.best[key] = moves; save(); }
          var q = moves <= lv.p * 1.5 ? 1 : moves <= lv.p * 2.2 ? 0.8 : 0.6;
          api.later(function () { api.done('Alle Paare gefunden in ' + moves + ' Zügen.' + (rec && best ? ' Neuer Rekord!' : ''), q); }, 900);
        }
      } else {
        api.answer(false, true); lock = true;
        api.later(function () { delete a.dataset.open; delete b.dataset.open; show(a, false); show(b, false); lock = false; }, 950);
      }
    }
  }
};
""", 1)

# ---------------------------------------------------------------- 2. Farben-Reihe
spiel('farben-reihe', 'Farben-Reihe', 'Felder leuchten nacheinander auf. Die Reihenfolge merken und nachtippen.', 'Reihenfolgen merken',
      {'modus': 'runde', 'n': 10}, r"""
var PADS = [
  { c: '#e74c3c', s: '♥', f: 262 }, { c: '#2e86de', s: '●', f: 330 }, { c: '#f1c40f', s: '★', f: 392 }, { c: '#27ae60', s: '▲', f: 440 },
  { c: '#9b59b6', s: '◆', f: 523 }, { c: '#e67e22', s: '■', f: 587 }, { c: '#1abc9c', s: '✿', f: 659 }, { c: '#e84393', s: '☾', f: 698 }, { c: '#795548', s: '✚', f: 784 }
];
var G = { title: 'Farben-Reihe', icon: '🚦', n: 10, intro: 'Die Felder leuchten nacheinander auf. Schau gut zu und tippe sie danach in der gleichen Reihenfolge an.',
  levels: [
    { name: 'Leicht', info: '4 Felder, 2 bis 3 Mal leuchten', k: 4, c: 2, a: 2, b: 3, ms: 900 },
    { name: 'Gut', info: '4 Felder, 3 bis 4 Mal leuchten', k: 4, c: 2, a: 3, b: 4, ms: 800 },
    { name: 'Mittel', info: '6 Felder, 4 bis 5 Mal leuchten', k: 6, c: 3, a: 4, b: 5, ms: 720 },
    { name: 'Schwer', info: '9 Felder, 5 bis 6 Mal leuchten', k: 9, c: 3, a: 5, b: 6, ms: 650 },
    { name: 'Profi', info: '9 Felder, 6 bis 8 Mal, schneller', k: 9, c: 3, a: 6, b: 8, ms: 560 }
  ],
  play: function (lv, api) {
    var t = 0, g = document.createElement('div'), pads = PADS.slice(0, lv.k), btns = [], seq = [], pos = 0, input = false;
    g.className = 'grid'; g.style.gridTemplateColumns = 'repeat(' + lv.c + ',1fr)';
    var rows = Math.ceil(lv.k / lv.c);
    g.style.maxWidth = 'min(100%, calc((100vh - 200px) * ' + lv.c + ' / ' + rows + '), ' + (lv.c * 150) + 'px)';
    pads.forEach(function (p, k) {
      var b = document.createElement('button'); b.className = 'card'; b.setAttribute('aria-label', 'Feld ' + (k + 1));
      b.style.cssText = 'background:' + p.c + ';border-color:transparent;color:#fff;opacity:.45;transition:opacity .12s,transform .12s';
      b.innerHTML = '<span style="font-size:.8em;text-shadow:0 2px 4px #0004">' + p.s + '</span>';
      b.onclick = function () { tap(k); };
      g.appendChild(b); btns.push(b);
    });
    api.stage.appendChild(g);
    function flash(k, ms) { var b = btns[k]; b.style.opacity = 1; b.style.transform = 'scale(1.06)'; tone(pads[k].f, ms / 1000 * 0.9, 'sine', 0.2);
      api.later(function () { b.style.opacity = .45; b.style.transform = ''; }, ms); }
    function task() {
      var len = lv.a + Math.floor(t * (lv.b - lv.a + 1) / 10); t++;
      seq = []; for (var i = 0; i < len; i++) { var x; do { x = rnd(0, lv.k - 1); } while (len > 2 && i > 1 && x === seq[i - 1] && x === seq[i - 2]); seq.push(x); }
      pos = 0; input = false; api.msg('<span class="em">👀</span> Schau gut zu!');
      play(seq, 900, function () { input = true; api.msg('<span class="em">👆</span> Jetzt du! <span style="color:var(--muted)">(' + len + ' Mal)</span>'); });
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
  }
};
""", 2)

# ---------------------------------------------------------------- 3. Was fehlt?
spiel('was-fehlt', 'Was fehlt?', 'Bilder anschauen und merken. Danach ist eines weg: Welches fehlt?', 'Bilder merken',
      {'modus': 'runde', 'n': 10}, r"""
var G = { title: 'Was fehlt?', icon: '🔍', n: 10, intro: 'Schau dir die Bilder gut an. Dann verschwindet eines. Weisst du, welches fehlt?',
  levels: [
    { name: 'Leicht', info: '3 Bilder, gleicher Platz', k: 3, ms: 5000, opt: 3, mix: false, same: false },
    { name: 'Gut', info: '4 Bilder, gleicher Platz', k: 4, ms: 6000, opt: 4, mix: false, same: false },
    { name: 'Mittel', info: '5 Bilder, sie werden gemischt', k: 5, ms: 7000, opt: 4, mix: true, same: false },
    { name: 'Schwer', info: '6 ähnliche Bilder, gemischt', k: 6, ms: 8000, opt: 6, mix: true, same: true },
    { name: 'Profi', info: '8 ähnliche Bilder, gemischt', k: 8, ms: 9000, opt: 6, mix: true, same: true }
  ],
  play: function (lv, api) {
    var cats = Object.keys(BILD);
    function task() {
      api.stage.innerHTML = '';
      var cat = BILD[cats[rnd(0, cats.length - 1)]], src = lv.same ? cat : ALLE, shown = pick(src, lv.k), miss = rnd(0, lv.k - 1), gone = shown[miss];
      var cols = lv.k <= 4 ? lv.k : Math.ceil(lv.k / 2);
      var g = document.createElement('div'); g.className = 'grid'; g.style.gridTemplateColumns = 'repeat(' + cols + ',1fr)'; g.style.maxWidth = (cols * 120) + 'px';
      g.innerHTML = shown.map(function (p) { return '<div class="card">' + p + '</div>'; }).join('');
      api.stage.appendChild(g);
      api.msg('<span class="em">👀</span> Merk dir alle Bilder!');
      api.watch(lv.ms, function () {
        g.innerHTML = shown.map(function (p) { return '<div class="card" style="background:#f4ecd9"></div>'; }).join('');
        api.msg('<span class="em">🙈</span> Augen zu …');
        api.later(function () {
          var rest = shown.slice(); rest[miss] = null; if (lv.mix) rest = shuffle(rest);
          g.innerHTML = rest.map(function (p) { return p ? '<div class="card pop">' + p + '</div>' : '<div class="card" data-gap style="border-style:dashed;border-color:var(--gold);color:var(--gold)">?</div>'; }).join('');
          api.msg('<span class="em">🤔</span> Welches Bild fehlt?');
          var others = shuffle((lv.same ? cat : ALLE).filter(function (p) { return shown.indexOf(p) < 0; })).slice(0, lv.opt - 1);
          var opts = shuffle(others.concat([gone]));
          var r = document.createElement('div'); r.className = 'row';
          opts.forEach(function (p) {
            var b = document.createElement('button'); b.className = 'card'; b.style.width = 'clamp(64px,15vw,96px)'; b.style.fontSize = 'clamp(32px,7vw,50px)'; b.textContent = p;
            b.onclick = function () {
              if (r.dataset.done) return; r.dataset.done = 1;
              var ok = p === gone, gap = g.querySelector('[data-gap]');
              gap.textContent = gone; gap.style.borderStyle = 'solid'; gap.style.borderColor = ok ? 'var(--ok)' : 'var(--gold)'; gap.classList.add('pop');
              b.style.borderColor = ok ? 'var(--ok)' : 'var(--no)'; if (!ok) b.classList.add('shake');
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
  }
};
""", 3)

# ---------------------------------------------------------------- 4. Wo war es?
spiel('wo-war-es', 'Wo war es?', 'Bilder liegen auf einem Feld. Merken, wo sie liegen, und wiederfinden.', 'Orte merken',
      {'modus': 'runde', 'n': 10}, r"""
var G = { title: 'Wo war es?', icon: '📍', n: 10, intro: 'Schau dir gut an, wo die Bilder liegen. Dann werden sie zugedeckt. Findest du sie wieder?',
  levels: [
    { name: 'Leicht', info: '2 Bilder auf 4 Feldern', r: 2, c: 2, k: 2, ms: 5000 },
    { name: 'Gut', info: '3 Bilder auf 9 Feldern', r: 3, c: 3, k: 3, ms: 6000 },
    { name: 'Mittel', info: '4 Bilder auf 9 Feldern', r: 3, c: 3, k: 4, ms: 7000 },
    { name: 'Schwer', info: '5 Bilder auf 16 Feldern', r: 4, c: 4, k: 5, ms: 8000 },
    { name: 'Profi', info: '7 Bilder auf 16 Feldern', r: 4, c: 4, k: 7, ms: 10000 }
  ],
  play: function (lv, api) {
    function board() {
      api.stage.innerHTML = '';
      var n = lv.r * lv.c, cells = pick(Array.from({ length: n }, function (_, i) { return i; }), lv.k), pics = pick(ALLE, lv.k), at = {};
      cells.forEach(function (c, i) { at[c] = pics[i]; });
      var g = document.createElement('div'); g.className = 'grid'; g.style.gridTemplateColumns = 'repeat(' + lv.c + ',1fr)';
      g.style.maxWidth = 'min(100%, calc((100vh - 230px) * ' + lv.c + ' / ' + lv.r + '), ' + (lv.c * 130) + 'px)';
      var btns = [];
      for (var i = 0; i < n; i++) { var b = document.createElement('button'); b.className = 'card'; b.dataset.i = i; b.innerHTML = at[i] || ''; g.appendChild(b); btns.push(b); }
      api.stage.appendChild(g);
      api.msg('<span class="em">👀</span> Merk dir, wo die Bilder liegen!');
      api.watch(lv.ms, function () {
        btns.forEach(function (b) { b.innerHTML = ''; b.style.background = 'linear-gradient(135deg,#bfe3d0,#8fcbb0)'; });
        var q = shuffle(cells), lock = false;
        function ask() {
          if (!q.length) { api.later(board, 900); return; }
          var c = q[0]; lock = false;
          api.msg('Wo war <span class="em pop">' + at[c] + '</span> ?');
          btns.forEach(function (b) { b.onclick = function () {
            if (lock || b.dataset.done) return; lock = true;
            var i = +b.dataset.i, ok = i === c, right = btns[c];
            right.innerHTML = at[c]; right.style.background = '#fff'; right.dataset.done = 1; right.classList.add('pop');
            right.style.borderColor = ok ? 'var(--ok)' : 'var(--gold)';
            if (!ok) { b.classList.add('shake'); b.style.borderColor = 'var(--no)'; api.later(function () { b.style.borderColor = ''; b.classList.remove('shake'); }, 800); }
            api.msg(ok ? '<span class="em">🎉</span> Genau dort!' : '<span class="em">💡</span> Es war hier.');
            q.shift();
            if (api.answer(ok)) api.later(ask, ok ? 900 : 1700);
          }; });
        }
        ask();
      });
    }
    board();
  }
};
""", 4)

# ---------------------------------------------------------------- 5. Bilder-Reihe
spiel('bilder-reihe', 'Bilder-Reihe', 'Bilder erscheinen nacheinander. Die Reihenfolge merken und richtig antippen.', 'Reihenfolgen merken',
      {'modus': 'runde', 'n': 10}, r"""
var G = { title: 'Bilder-Reihe', icon: '🎞️', n: 10, intro: 'Die Bilder kommen eines nach dem anderen. Tippe sie danach in der gleichen Reihenfolge an.',
  levels: [
    { name: 'Leicht', info: '2 bis 3 Bilder', a: 2, b: 3, x: 0, ms: 1400 },
    { name: 'Gut', info: '3 bis 4 Bilder, 2 zum Verwechseln', a: 3, b: 4, x: 2, ms: 1300 },
    { name: 'Mittel', info: '4 bis 5 Bilder, 3 zum Verwechseln', a: 4, b: 5, x: 3, ms: 1200 },
    { name: 'Schwer', info: '5 bis 6 Bilder, 3 zum Verwechseln', a: 5, b: 6, x: 3, ms: 1100 },
    { name: 'Profi', info: 'Rückwärts! 4 bis 5 Bilder', a: 4, b: 5, x: 3, ms: 1200, back: true }
  ],
  play: function (lv, api) {
    var t = 0;
    function task() {
      api.stage.innerHTML = '';
      var len = lv.a + Math.floor(t * (lv.b - lv.a + 1) / 10); t++;
      var src = BILD[Object.keys(BILD)[rnd(0, 3)]], all = pick(src, len + lv.x), seq = all.slice(0, len), want = lv.back ? seq.slice().reverse() : seq;
      var box = document.createElement('div'); box.className = 'card'; box.style.cssText = 'width:min(46vw,190px);font-size:min(24vw,110px)';
      var cnt = document.createElement('div'); cnt.className = 'dots';
      api.stage.appendChild(box); api.stage.appendChild(cnt);
      api.msg('<span class="em">👀</span> Schau gut zu!');
      seq.forEach(function (p, i) {
        api.later(function () {
          box.textContent = p; box.classList.remove('pop'); void box.offsetWidth; box.classList.add('pop'); tone(440 + i * 60, 0.1);
          cnt.innerHTML = seq.map(function (_, k) { return '<i class="' + (k <= i ? 'ok' : '') + '"></i>'; }).join('');
        }, 600 + i * lv.ms);
        api.later(function () { box.textContent = ''; }, 600 + i * lv.ms + lv.ms * 0.75);
      });
      api.later(answer, 700 + len * lv.ms);
      function answer() {
        api.stage.innerHTML = '';
        api.msg(lv.back ? '<span class="em">🔙</span> Jetzt <b>rückwärts</b>: vom letzten zum ersten Bild!' : '<span class="em">👆</span> In welcher Reihenfolge kamen die Bilder?');
        var slots = document.createElement('div'); slots.className = 'row';
        slots.innerHTML = want.map(function () { return '<div class="card" style="width:clamp(52px,13vw,84px);font-size:clamp(28px,7vw,46px);border-style:dashed"></div>'; }).join('');
        var pool = document.createElement('div'); pool.className = 'row'; pool.style.marginTop = '12px';
        var pos = 0, over = false;
        shuffle(all).forEach(function (p) {
          var b = document.createElement('button'); b.className = 'card'; b.style.cssText = 'width:clamp(60px,15vw,92px);font-size:clamp(32px,7.5vw,52px)'; b.textContent = p;
          b.onclick = function () {
            if (over || b.disabled) return;
            var s = slots.children[pos];
            if (p === want[pos]) {
              s.textContent = p; s.style.borderStyle = 'solid'; s.style.borderColor = 'var(--ok)'; s.classList.add('pop'); b.disabled = true; b.style.opacity = .3; pos++; tone(520 + pos * 50, 0.08);
              if (pos === want.length) { over = true; api.msg('<span class="em">🎉</span> Richtig!'); if (api.answer(true)) api.later(task, 1300); }
            } else {
              over = true; b.classList.add('shake'); b.style.borderColor = 'var(--no)';
              want.forEach(function (w, k) { var c = slots.children[k]; if (k >= pos) { c.textContent = w; c.style.borderStyle = 'solid'; c.style.borderColor = 'var(--gold)'; } });
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
  }
};
""", 5)

# ---------------------------------------------------------------- 6. Zahlen merken
spiel('zahlen-merken', 'Zahlen merken', 'Ziffern erscheinen nacheinander. Merken und eintippen, auf den hohen Stufen rückwärts.', 'Reihenfolgen merken',
      {'modus': 'runde', 'n': 10}, r"""
var G = { title: 'Zahlen merken', icon: '🔢', n: 10, intro: 'Die Ziffern erscheinen eine nach der anderen. Merk sie dir und tippe sie dann ein.',
  levels: [
    { name: 'Leicht', info: '3 Ziffern', a: 3, b: 3, ms: 1100 },
    { name: 'Gut', info: '4 Ziffern', a: 4, b: 4, ms: 1000 },
    { name: 'Mittel', info: '5 Ziffern', a: 5, b: 5, ms: 1000 },
    { name: 'Schwer', info: '6 bis 7 Ziffern', a: 6, b: 7, ms: 950 },
    { name: 'Profi', info: 'Rückwärts! 4 bis 5 Ziffern', a: 4, b: 5, ms: 1000, back: true }
  ],
  play: function (lv, api) {
    var t = 0;
    function task() {
      api.stage.innerHTML = '';
      var len = lv.a + Math.floor(t * (lv.b - lv.a + 1) / 10); t++;
      var seq = []; for (var i = 0; i < len; i++) { var d; do { d = rnd(0, 9); } while (d === seq[i - 1]); seq.push(d); }
      var want = lv.back ? seq.slice().reverse() : seq;
      var box = document.createElement('div'); box.className = 'card'; box.style.cssText = 'width:min(46vw,190px);font-size:min(26vw,120px);font-weight:700;color:var(--teal)';
      api.stage.appendChild(box);
      api.msg('<span class="em">👀</span> Merk dir die Zahlen!');
      seq.forEach(function (d, i) {
        api.later(function () { box.textContent = d; box.classList.remove('pop'); void box.offsetWidth; box.classList.add('pop'); tone(400 + d * 40, 0.1); }, 600 + i * lv.ms);
        api.later(function () { box.textContent = ''; }, 600 + i * lv.ms + lv.ms * 0.75);
      });
      api.later(input, 700 + len * lv.ms);
      function input() {
        api.stage.innerHTML = '';
        api.msg(lv.back ? '<span class="em">🔙</span> Tippe die Zahlen <b>rückwärts</b> ein!' : '<span class="em">⌨️</span> Tippe die Zahlen ein!');
        var out = document.createElement('div'); out.className = 'row'; var got = [], over = false;
        function draw() { out.innerHTML = want.map(function (_, k) { return '<div class="card" style="width:clamp(40px,11vw,64px);font-size:clamp(26px,7vw,40px);font-weight:700;' + (k < got.length ? '' : 'border-style:dashed') + '">' + (k < got.length ? got[k] : '') + '</div>'; }).join(''); }
        draw();
        var pad = document.createElement('div'); pad.className = 'grid'; pad.style.cssText = 'grid-template-columns:repeat(3,1fr);max-width:280px;margin-top:6px';
        [1, 2, 3, 4, 5, 6, 7, 8, 9, '⌫', 0, ''].forEach(function (k) {
          var b = document.createElement('button'); b.className = 'card'; b.style.cssText = 'aspect-ratio:1.4;font-size:30px;font-weight:700' + (k === '' ? ';visibility:hidden' : '');
          b.textContent = k;
          b.onclick = function () {
            if (over) return;
            if (k === '⌫') { got.pop(); draw(); return; }
            got.push(k); tone(500 + k * 30, 0.06); draw();
            if (got.length === want.length) {
              over = true; var ok = got.join('') === want.join('');
              Array.prototype.forEach.call(out.children, function (c, j) { c.style.borderColor = got[j] === want[j] ? 'var(--ok)' : 'var(--no)'; });
              api.msg(ok ? '<span class="em">🎉</span> Richtig!' : '<span class="em">💡</span> Richtig wäre: <b style="font-size:30px;letter-spacing:4px">' + want.join(' ') + '</b>');
              if (api.answer(ok)) api.later(task, ok ? 1300 : 2600);
            }
          };
          pad.appendChild(b);
        });
        api.stage.appendChild(out); api.stage.appendChild(pad);
      }
    }
    task();
  }
};
""", 6)


def html_for(s):
    meta = json.dumps(s['sterne'], ensure_ascii=False).replace('"', '&quot;')
    return ('<!doctype html>\n<html lang="de-CH">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
            f'<meta name="knobelnest-sterne" content="{meta}">\n'
            f'<title>{s["titel"]}</title>\n<style>{CSS}</style>\n</head>\n<body>\n<div id="app"></div>\n'
            f'<script>\n{POOL}\n{s["js"]}\n{FRAME}\n</script>\n</body>\n</html>\n')


if __name__ == '__main__':
    paket = {'format': 'knobelnest-spielpaket', 'games': []}
    for s in SPIELE:
        html = html_for(s)
        with open(os.path.join(HIER, s['datei'] + '.html'), 'w', encoding='utf-8') as f: f.write(html)
        paket['games'].append({'title': s['titel'], 'description': s['beschreibung'], 'fach': 'Gedächtnis', 'thema': s['thema'],
                               'stufe': '1.–6. Klasse', 'sort': s['sort'], 'html': html})
    with open(os.path.join(HIER, 'gedaechtnis-spielpaket.json'), 'w', encoding='utf-8') as f: json.dump(paket, f, ensure_ascii=False)
    print(len(SPIELE), 'Spiele gebaut, Paket: werkstatt/spiele/gedaechtnis/gedaechtnis-spielpaket.json')
