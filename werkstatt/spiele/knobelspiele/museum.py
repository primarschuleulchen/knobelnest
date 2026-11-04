# Knobelspiel «Im Museum» (Englisch, Bildbeschreibung / describing pictures).
# Nach den Arbeitsblättern E4-3 «describing pictures» und dem Merkplakat «Bildbeschreibung»:
# There is a / There are + (additional information) + colour + shape + position.
# Wird von bauen.py aufgerufen: museum.alle(spiel)
#
# Stufen:
#   1 Read and choose   Beschreibung lesen (oder anhören), das richtige Bild aus drei finden
#   2 Look and describe Ein Bild beschreiben: Sätze aus Wörtern bauen (Farbe, Form, Ort)
#   3 Read and draw     Beschreibung lesen und das Bild selber malen
#   4 Look and describe* wie 2, dazu big/little, light/dark, facing up/down/…, There are two/three/four
#   5 Listen and draw*  Beschreibung nur anhören (Text kann man aufdecken) und malen, mit allen Zusätzen


import base64, os


def logo():
    # Logo des Spiels (rund, durchsichtige Ecken) direkt in die Datei eingebettet, damit es auch als Artefakt läuft
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logos', 'im-museum.webp'), 'rb') as f:
        return '<img class="logo" alt="" src="data:image/webp;base64,' + base64.b64encode(f.read()).decode() + '">'


def alle(spiel):
    spiel(id='im-museum', titel='Im Museum', icon=logo(), fach='Englisch', thema='Describing pictures', stufe='3.–6. Klasse', sort=1, n=4,
          sterne={'modus': 'sammeln', 'pro': 10, 'max': 10, 'proLevel': True, 'proTag': False},  # je 10 richtige Bilder 1 Stern, pro Stufe bis 10
          kurz='Bilder im Museum auf Englisch beschreiben, lesen und malen.',
          intro='Willkommen im Museum! Hier hängen bunte Bilder. Beschreibe sie auf Englisch: <b>There is a</b> + Farbe + Form + Ort.',
          levels=[dict(name='Bild finden', info='Read and choose: Welches Bild ist es?', t='wahl', min=1, max=2, extra=False, alle=False),
                  dict(name='Bild beschreiben', info='Look and describe: Sätze bauen', t='sag', min=2, max=2, extra=False, alle=False),
                  dict(name='Bild malen', info='Read and draw: lesen und malen', t='mal', min=2, max=3, extra=False, alle=True, pause=1300),
                  dict(name='Genau beschreiben', info='big, little, light, dark, facing …', t='sag', min=2, max=3, extra=True, alle=True),
                  dict(name='Zuhören und malen', info='Listen and draw: nur hören', t='mal', min=3, max=4, extra=True, alle=True, hoer=True, tempo=.68, pause=1800)],
          css=CSS, js=JS)


CSS = r"""
/* Logo statt Emoji im Kreis oben */
.ring{width:150px;height:150px;background:#fff;border:3px solid var(--gold);padding:5px;box-shadow:0 8px 18px rgba(63,120,168,.18)}.ring .logo{width:100%;height:100%;display:block;border-radius:50%}
/* bis 10 Sterne pro Stufe: rechts in zwei Reihen à 5 */
.lv .stars{flex:none;width:5.3em;font-size:19px;letter-spacing:0;line-height:1.15;white-space:normal;word-break:break-all;text-align:left}
.mu{display:flex;flex-wrap:wrap;gap:18px;justify-content:center;align-items:flex-start;width:100%;max-width:1040px}
.spalte{display:flex;flex-direction:column;align-items:center;gap:12px;width:min(100%,470px)}
.wand{position:relative;width:100%;border-radius:26px;padding:22px 20px 12px;display:flex;flex-direction:column;align-items:center;gap:10px;
  background:radial-gradient(60% 50% at 50% 0%,rgba(255,250,225,.95) 0%,rgba(255,250,225,0) 100%),linear-gradient(180deg,#efe2c6 0%,#e6d5b2 82%,#c9a97a 82%,#b8955f 100%);
  box-shadow:var(--sch)}
.wand.klein{padding:12px 10px 8px;border-radius:18px}
.rahmen{width:100%;padding:clamp(8px,2.2vw,15px);border-radius:5px;
  background:linear-gradient(135deg,#f6e3a1 0%,#c4952f 22%,#f3d98a 45%,#a8741f 70%,#e9c46a 100%);
  box-shadow:0 12px 18px rgba(90,60,10,.35),inset 0 0 0 2px rgba(255,255,255,.45),inset 0 0 0 4px rgba(120,80,20,.35)}
.lein{border:3px solid #7a5418;background:#fff;line-height:0}
.lein svg{display:block;width:100%;height:auto;touch-action:manipulation}
.schild{background:linear-gradient(180deg,#f6e3a1,#d6ad45);border:1px solid #a8741f;border-radius:4px;padding:0 14px;font-size:17px;color:#5a3d0c;box-shadow:0 2px 4px rgba(90,60,10,.25)}
.beschr{background:#fff;border:2px solid var(--line);border-radius:20px;padding:12px 16px;box-shadow:var(--sch-k);font-size:23px;width:100%;line-height:1.45}
.beschr .kopfz{display:flex;align-items:center;gap:10px;justify-content:space-between;margin-bottom:4px;color:var(--soft);font-size:18px}
.beschr p{margin:2px 0}
.beschr .zu{color:var(--soft);font-size:19px;text-align:center;padding:6px 0}
.hoer{background:var(--sun);border:2px solid var(--gold-d);border-radius:14px;min-height:46px;padding:4px 14px;font-size:20px;box-shadow:var(--sch-k)}
.hoer.gross{font-size:26px;min-height:70px;padding:8px 26px}
.drei{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,230px),1fr));gap:14px;width:100%;max-width:960px}
.drei button{padding:0;background:none;border:none;border-radius:22px;transition:transform .15s}
.drei button:hover{transform:translateY(-3px)}
.drei button.ok .wand{box-shadow:0 0 0 6px var(--ok),var(--sch)}
.drei button.no .wand{box-shadow:0 0 0 6px var(--no),var(--sch);opacity:.75}
.drei button.hint .wand{box-shadow:0 0 0 6px var(--gold),var(--sch)}
.satz{background:#fff;border:2px solid var(--line);border-radius:18px;padding:10px 14px;min-height:64px;width:100%;text-align:center;font-size:25px;line-height:1.7;box-shadow:var(--sch-k)}
.slot{display:inline-block;min-width:64px;border-bottom:3px solid var(--line2);margin:0 3px;padding:0 4px;line-height:1.25;color:var(--sky-d)}
.slot.jetzt{border-color:var(--gold);background:var(--sun);border-radius:8px 8px 0 0}
.slot.voll{border-color:transparent;color:#2c3e50;background:#eef6fc;border-radius:8px}
.opts4{display:flex;flex-wrap:wrap;gap:10px;justify-content:center;width:100%}
.opts4 button{background:#fff;border:2px solid var(--ink);border-radius:16px;min-height:56px;padding:6px 16px;font-size:23px;box-shadow:var(--sch-k);transition:transform .12s}
.opts4 button:active{transform:scale(.96)}
.opts4 button.no{background:#fbe5e2;border-color:var(--no)}.opts4 button.hint{background:var(--sun);border-color:var(--gold)}
.heft{width:100%;background:repeating-linear-gradient(180deg,#fff 0 38px,#c5d8e8 38px 40px);border-radius:12px;border:1.5px solid var(--line);padding:0 14px;font-size:22px;line-height:40px;min-height:82px}
.heft p{margin:0}
.heft p::before{content:"✎ ";color:var(--gold)}
.werk{display:flex;flex-direction:column;gap:10px;width:100%}
.werk h3{margin:2px 0 -4px;font-weight:400;font-size:18px;color:var(--soft)}
.reihe{display:flex;flex-wrap:wrap;gap:7px}
.tb{background:#fff;border:2px solid var(--line2);border-radius:14px;min-height:50px;padding:4px 10px;font-size:19px;display:inline-flex;align-items:center;gap:6px}
.tb svg{width:26px;height:26px}
.tb[aria-pressed="true"]{border-color:var(--gold-d);background:var(--sun);box-shadow:inset 0 0 0 2px var(--gold)}
.sw{width:44px;height:44px;border-radius:50%;border:2px solid rgba(0,0,0,.22);padding:0}
.sw[aria-pressed="true"]{outline:4px solid var(--gold);outline-offset:2px}
.zelle{fill:transparent;stroke:rgba(40,40,40,.28);stroke-width:1;stroke-dasharray:4 4;cursor:pointer}
.zelle.f{stroke:#c8574e;stroke-width:3.5;stroke-dasharray:7 4}
.mark{fill:none;stroke:#fff;stroke-width:3;stroke-dasharray:8 5;animation:mk 1s linear infinite}
.mark2{fill:none;stroke:#d6ad45;stroke-width:6;opacity:.85}
@keyframes mk{to{stroke-dashoffset:-26}}
.steuer{display:flex;gap:10px;flex-wrap:wrap;justify-content:center}
.steuer .go{min-height:54px}
.steuer .fertig{background:#e7f3df;border-color:#3f6b2e}
.loes{width:min(100%,300px)}
.loes p{text-align:center;margin:4px 0 0;color:var(--soft);font-size:18px}
"""


JS = r"""
// ---------- Wörter und Farben (wie auf dem Merkplakat)
var COL = { 'yellow': '#f7d330', 'orange': '#f39a2b', 'red': '#e5322d', 'purple': '#9b59c9', 'light blue': '#91d5f6', 'blue': '#2f7de1', 'dark blue': '#17418f',
  'light green': '#a8e090', 'green': '#3fae4a', 'dark green': '#1d6b34', 'brown': '#8a5a2b', 'black': '#222222', 'grey': '#9aa0a6', 'white': '#ffffff' };
var FAM = { 'light blue': 'blue', 'dark blue': 'blue', 'light green': 'green', 'dark green': 'green' };
var GRUND = ['yellow', 'orange', 'red', 'purple', 'blue', 'green', 'brown', 'black', 'grey', 'white'];
var ALLE = ['yellow', 'orange', 'red', 'purple', 'light blue', 'blue', 'dark blue', 'light green', 'green', 'dark green', 'brown', 'black', 'grey', 'white'];
var HINTER = ['yellow', 'orange', 'purple', 'light blue', 'light green', 'green', 'grey', 'red'];
var FORM = ['circle', 'square', 'triangle', 'rectangle'];
var ORT = ['at the top in the left corner', 'at the top in the middle', 'at the top in the right corner',
  'on the left in the middle', 'in the middle', 'on the right in the middle',
  'at the bottom in the left corner', 'at the bottom in the middle', 'at the bottom in the right corner'];
var RICHT = ['up', 'right', 'down', 'left'], RICHTW = { up: 'facing up', down: 'facing down', left: 'facing to the left', right: 'facing to the right' };
var ZAHL = ['', 'a', 'two', 'three', 'four'];
var LOB = ['Great!', 'Super!', 'Well done!', 'Excellent!', 'Fantastic!', 'Perfect!'];
function fam(c) { return FAM[c] || c; }
function passt(c, bg) { var a = fam(c), b = fam(bg); if (a === b) return false; var x = [a, b].sort().join('/'); return ['orange/yellow', 'purple/red', 'black/brown', 'blue/purple'].indexOf(x) < 0 && !(c === 'white' && /^light/.test(bg)) && !(bg === 'grey' && c === 'white'); }
function plural(s, n) { return n > 1 ? s + 's' : s; }
function art(w) { return /^[aeiou]/.test(w) ? 'an' : 'a'; }

// ---------- Ein Bild: { bg, it: [{ s, c, p, z, d, n }] }  (p = Feld 0…8, z = little/big/'', d = Richtung, n = Anzahl)
function neuesBild(lv) {
  for (var t = 0; t < 500; t++) {
    var k = rnd(lv.min, lv.max), felder = pick(range(9), k), bg = pick(HINTER, 1)[0], liste = lv.alle ? ALLE : GRUND, it = [], ok = true;
    felder.sort(function (a, b) { return a - b; });
    felder.forEach(function (p) {
      var farben = liste.filter(function (c) { return passt(c, bg); }), x = { s: pick(FORM, 1)[0], c: pick(farben, 1)[0], p: p, z: '', d: 'up', n: 1 };
      if (lv.extra) {
        x.z = Math.random() < .5 ? 'little' : 'big';
        if (x.s === 'triangle') x.d = pick(RICHT, 1)[0];
        if (Math.random() < .3) { x.n = rnd(2, 4); x.z = 'little'; }
      }
      it.push(x);
    });
    // Nicht zweimal genau dasselbe
    var keys = it.map(function (x) { return x.s + x.c; });
    if (keys.some(function (q, i) { return keys.indexOf(q) !== i; })) ok = false;
    // Grosse Formen nicht direkt nebeneinander (sonst wird es eng)
    it.forEach(function (a) { it.forEach(function (b) { if (a !== b && a.z === 'big' && b.z === 'big' && Math.abs(a.p - b.p) === 1 && Math.floor(a.p / 3) === Math.floor(b.p / 3)) ok = false; }); });
    if (ok) return { bg: bg, it: it };
  }
}
function schluessel(b, voll) {
  return b.bg + '|' + b.it.map(function (x) { return norm(x, voll); }).sort().join(';');
}
function norm(x, voll) {
  if (!voll) return x.p + ':' + x.s + ':' + x.c;
  return x.p + ':' + x.s + ':' + x.c + ':' + x.n + ':' + (x.n > 1 ? '' : x.z) + ':' + (x.s === 'triangle' ? x.d : '');
}

// ---------- Sätze
function satzHinter(b) { return 'The background is ' + b.bg + '.'; }
function satz(x, voll) {
  var w = [x.n > 1 ? 'There are ' + ZAHL[x.n] : 'There is ' + art(x.z || x.c)];
  if (x.z) w.push(x.z);
  w.push(x.c, plural(x.s, x.n));
  if (voll && x.s === 'triangle') w.push(RICHTW[x.d]);
  w.push(ORT[x.p]);
  return w.join(' ') + '.';
}
function text(b, voll) { return [satzHinter(b)].concat(b.it.map(function (x) { return satz(x, voll); })); }

// ---------- Vorlesen: dieselbe Stimmenwahl wie in der Vokabelkiste (englische Frauenstimme, en-GB bevorzugt, «natural» besser)
var FEMALE = /\b(female|samantha|karen|moira|tessa|serena|kate|stephanie|martha|fiona|victoria|allison|ava|susan|zira|hazel|libby|sonia|aria|jenny|emma|amy|joanna|salli|kimberly|olivia|natasha|clara)\b/i;
var MALE = /\b(male|daniel|alex|fred|oliver|george|ryan|guy|david|mark|james|thomas|arthur|rishi|aaron|gordon|reed|rocko|eddy|grandpa)\b/i;
function stimme() {
  var vs = []; try { vs = speechSynthesis.getVoices().filter(function (v) { return v.lang && /^en/i.test(v.lang); }); } catch (e) {}
  if (!vs.length) return null;
  function sc(v) { var n = v.name.replace(/female/ig, ''); return (FEMALE.test(v.name) ? 10 : 0) - (MALE.test(n) ? 10 : 0) + (/en[-_]gb/i.test(v.lang) ? 3 : 0) + (/natural|neural|premium|enhanced|online/i.test(v.name) ? 4 : 0); }
  return vs.slice().sort(function (a, b) { return sc(b) - sc(a); })[0];
}
function kannSprechen() { return !!(window.speechSynthesis && window.SpeechSynthesisUtterance); }
// Tempo und Pause zwischen den Sätzen (pro Stufe, gesetzt in G.play)
var TEMPO = .8, PAUSE = 900, SPRICH = 0, AKT_U = null;
// t = ein Satz oder eine Liste von Sätzen; jeder Satz einzeln, mit Pause dazwischen
function sag(t, immer) {
  if ((ST.mute && !immer) || !kannSprechen()) return;
  var liste = [].concat(t), nr = ++SPRICH, i = 0;
  try { var ss = speechSynthesis; if (ss.speaking || ss.pending) ss.cancel(); if (ss.paused) ss.resume(); } catch (e) {}
  function weiter() {
    if (nr !== SPRICH || i >= liste.length) return;
    var satz = liste[i++], fertig = false, notfall;
    function danach() { if (fertig) return; fertig = true; clearTimeout(notfall); if (nr === SPRICH && i < liste.length) setTimeout(weiter, PAUSE); }
    try {
      var u = new SpeechSynthesisUtterance(satz), v = stimme();
      if (v) { u.voice = v; u.lang = String(v.lang).replace('_', '-'); } else u.lang = 'en-GB';
      u.rate = TEMPO; u.pitch = 1; u.onend = danach; u.onerror = danach; AKT_U = u; // Referenz halten (sonst bricht Safari ab)
      speechSynthesis.speak(u);
      notfall = setTimeout(danach, 4000 + satz.length * 140 / TEMPO); // falls das Gerät «fertig» nicht meldet
    } catch (e) {}
  }
  weiter();
}
function still() { SPRICH++; try { if (window.speechSynthesis) speechSynthesis.cancel(); } catch (e) {} }

// ---------- Zeichnen (SVG 300 × 210, 3 × 3 Felder à 100 × 70)
function formSvg(s, cx, cy, r, d, fill, extra) {
  var st = ' fill="' + fill + '" stroke="rgba(0,0,0,.22)" stroke-width="1.3"' + (extra || '');
  if (s === 'circle') return '<circle cx="' + cx + '" cy="' + cy + '" r="' + r + '"' + st + '/>';
  if (s === 'square') { var a = r * 1.75; return '<rect x="' + (cx - a / 2) + '" y="' + (cy - a / 2) + '" width="' + a + '" height="' + a + '"' + st + '/>'; }
  if (s === 'rectangle') { var w = r * 2.5, hh = r * 1.3; return '<rect x="' + (cx - w / 2) + '" y="' + (cy - hh / 2) + '" width="' + w + '" height="' + hh + '"' + st + '/>'; }
  var rot = { up: 0, right: 90, down: 180, left: 270 }[d] || 0, q = r * 1.12;
  return '<polygon points="' + cx + ',' + (cy - r) + ' ' + (cx - q) + ',' + (cy + r * .8) + ' ' + (cx + q) + ',' + (cy + r * .8) + '" transform="rotate(' + rot + ' ' + cx + ' ' + cy + ')"' + st + '/>';
}
function dingSvg(x) {
  var cx = 50 + (x.p % 3) * 100, cy = 35 + Math.floor(x.p / 3) * 70, o = '';
  if (x.n > 1) {
    var r = x.s === 'rectangle' ? 8 : 10, ab = 24;
    for (var i = 0; i < x.n; i++) o += formSvg(x.s, cx + (i - (x.n - 1) / 2) * ab, cy, r, x.d, COL[x.c]);
    return o;
  }
  var R = x.z === 'little' ? 12 : x.z === 'big' ? 29 : 20;
  return formSvg(x.s, cx, cy, R, x.d, COL[x.c]);
}
// opt: { felder: true (Raster zum Malen), mark: Feld hervorheben, fehler: [Felder] }
function bildSvg(b, opt) {
  opt = opt || {};
  var o = '<svg viewBox="0 0 300 210" role="img" aria-label="Bild"><rect x="0" y="0" width="300" height="210" fill="' + (b.bg ? COL[b.bg] : '#fff') + '"/>';
  b.it.forEach(function (x) { o += dingSvg(x); });
  if (opt.mark != null) { var mx = (opt.mark % 3) * 100, my = Math.floor(opt.mark / 3) * 70; o += '<rect class="mark2" x="' + (mx + 4) + '" y="' + (my + 4) + '" width="92" height="62" rx="10"/><rect class="mark" x="' + (mx + 4) + '" y="' + (my + 4) + '" width="92" height="62" rx="10"/>'; }
  if (opt.felder) for (var p = 0; p < 9; p++) o += '<rect class="zelle' + ((opt.fehler || []).indexOf(p) >= 0 ? ' f' : '') + '" data-p="' + p + '" x="' + ((p % 3) * 100 + 1) + '" y="' + (Math.floor(p / 3) * 70 + 1) + '" width="98" height="68" rx="6"/>';
  return o + '</svg>';
}
function wand(b, schild, opt, klein) {
  return '<div class="wand' + (klein ? ' klein' : '') + '"><div class="rahmen"><div class="lein">' + bildSvg(b, opt) + '</div></div>' + (schild ? '<div class="schild">' + schild + '</div>' : '') + '</div>';
}
var TITEL = ['Sunny Day', 'Happy Shapes', 'The Blue Dream', 'Little Party', 'Owl Night', 'Colour Dance', 'Funny Friends', 'Big Adventure', 'Morning Light', 'Quiet Garden', 'Jumping Shapes', 'Rainbow Walk'];
function weiterKnopf(api, wo, fn, label) {
  var nb = document.createElement('button'); nb.className = 'go sun'; nb.textContent = label || 'Nächstes Bild →';
  nb.onclick = fn; wo.innerHTML = ''; wo.appendChild(nb);
}

G.play = function (lv, api) {
  still(); TEMPO = lv.tempo || .8; PAUSE = lv.pause || 900;
  var idx = 0, titel = pick(TITEL, G.n);
  function schild() { return '«' + titel[idx] + '» · No. ' + (idx + 1); }
  ({ wahl: waehlen, sag: beschreiben, mal: malen })[lv.t]();

  // ================= Stufe 1: Read and choose
  function waehlen() {
    var b = neuesBild(lv), seen = {}, bilder = [b];
    seen[schluessel(b)] = 1;
    for (var t = 0; bilder.length < 3 && t < 400; t++) {
      var v = JSON.parse(JSON.stringify(b)), x = v.it[rnd(0, v.it.length - 1)], w = rnd(0, 3);
      if (w === 0) v.bg = pick(HINTER.filter(function (c) { return c !== b.bg && v.it.every(function (y) { return passt(y.c, c); }); }), 1)[0];
      else if (w === 1) x.c = pick(GRUND.filter(function (c) { return c !== x.c && passt(c, v.bg); }), 1)[0];
      else if (w === 2) x.s = pick(FORM.filter(function (s) { return s !== x.s; }), 1)[0];
      else { var frei = range(9).filter(function (p) { return v.it.every(function (y) { return y.p !== p; }); }); x.p = pick(frei, 1)[0]; }
      if (!v.bg || !x.c) continue;
      var k = schluessel(v); if (seen[k]) continue; seen[k] = 1; bilder.push(v);
    }
    var reihe = shuffle(range(bilder.length)), saetze = text(b, false), fertig = false;
    api.stage.innerHTML = '<div class="beschr"><div class="kopfz"><span>📜 Read the description:</span>' + (kannSprechen() ? '<button class="hoer" data-hoer>🔊 Listen</button>' : '') + '</div>' +
      saetze.map(function (s) { return '<p lang="en">' + h(s) + '</p>'; }).join('') + '</div><div class="drei">' +
      reihe.map(function (i) { return '<button data-i="' + i + '" aria-label="Bild">' + wand(bilder[i], '', null, true) + '</button>'; }).join('') + '</div><div class="steuer"></div>';
    api.msg('<span class="em">🔍</span> Bild ' + (idx + 1) + ' von ' + G.n + ': Welches Bild passt zur Beschreibung?');
    var hb = api.stage.querySelector('[data-hoer]'); if (hb) hb.onclick = function () { sag(saetze, true); };
    api.stage.querySelector('.drei').onclick = function (e) {
      var k = e.target.closest('[data-i]'); if (!k || fertig) return; fertig = true;
      var ok = k.dataset.i === '0';
      k.classList.add(ok ? 'ok' : 'no');
      if (!ok) api.stage.querySelector('[data-i="0"]').classList.add('hint');
      api.msg(ok ? '<span class="em">🎉</span> ' + pick(LOB, 1)[0] + ' Das ist das richtige Bild.' : '<span class="em">💡</span> Fast! Das Bild mit dem goldenen Rand passt. Lies nochmal genau.');
      if (api.answer(ok)) weiterKnopf(api, api.stage.querySelector('.steuer'), function () { idx++; waehlen(); });
    };
  }

  // ================= Stufe 2 und 4: Look and describe
  function beschreiben() {
    var b = neuesBild(lv), voll = lv.extra, fehler = 0, si = 0;
    var farbListe = lv.alle ? ALLE : GRUND;
    function farbOpts(ans, liste) {
      var nah = liste.filter(function (c) { return c !== ans && fam(c) === fam(ans); });
      var rest = shuffle(liste.filter(function (c) { return c !== ans && nah.indexOf(c) < 0; }));
      return shuffle([ans].concat(nah.concat(rest).slice(0, 3)));
    }
    function ortOpts(p) {
      var r = Math.floor(p / 3), c = p % 3;
      var nah = range(9).filter(function (q) { return q !== p && Math.abs(Math.floor(q / 3) - r) + Math.abs(q % 3 - c) === 1; });
      var rest = range(9).filter(function (q) { return q !== p && nah.indexOf(q) < 0; });
      return shuffle([p].concat(shuffle(nah).slice(0, 2), pick(rest, 1))).map(function (q) { return ORT[q]; });
    }
    // Jeder Satz: Teile { f: fester Text } oder { a: Antwort, o: Auswahl, typ }
    var SAETZE = [{ mark: null, teile: [{ f: 'The background is' }, { a: b.bg, o: farbOpts(b.bg, HINTER.concat(['blue', 'white'])), typ: 'farbe' }, { f: '.' }] }];
    b.it.forEach(function (x) {
      var t = [];
      if (voll) {
        var st = x.n > 1 ? 'There are ' + ZAHL[x.n] : 'There is a';
        t.push({ a: st, o: ['There is a', 'There are two', 'There are three', 'There are four'] });
        t.push({ a: x.z, o: ['little', 'big'] });
      } else t.push({ art: true });
      t.push({ a: x.c, o: farbOpts(x.c, farbListe), typ: 'farbe' });
      t.push({ a: plural(x.s, x.n), o: FORM.map(function (s) { return plural(s, x.n); }) });
      if (voll && x.s === 'triangle') t.push({ a: RICHTW[x.d], o: RICHT.map(function (d) { return RICHTW[d]; }) });
      t.push({ a: ORT[x.p], o: ortOpts(x.p) });
      t.push({ f: '.' });
      SAETZE.push({ mark: x.p, teile: t, x: x });
    });
    var erlaubt = voll ? 3 : 2;
    api.stage.innerHTML = '<div class="mu"><div class="spalte"><div class="bildplatz" style="width:100%"></div></div><div class="spalte"><div class="satz" lang="en"></div><div class="opts4" lang="en"></div><div class="heft" lang="en"></div><div class="steuer"></div></div></div>';
    var platz = api.stage.querySelector('.bildplatz'), satzEl = api.stage.querySelector('.satz'), opts = api.stage.querySelector('.opts4'), heft = api.stage.querySelector('.heft'), steuer = api.stage.querySelector('.steuer');
    function zeigeBild(mark) { platz.innerHTML = wand(b, schild(), { mark: mark }); }
    function neuerSatz() {
      var S = SAETZE[si], ti = -1, falsch = 0;
      zeigeBild(S.mark);
      api.msg(si === 0 ? '<span class="em">🖼️</span> Bild ' + (idx + 1) + ' von ' + G.n + ': Start with the background! <small>Beschreibe zuerst den Hintergrund.</small>' :
        '<span class="em">✨</span> Beschreibe die Form mit dem goldenen Rahmen.');
      function nextSlot() { ti++; while (ti < S.teile.length && !S.teile[ti].o) ti++; falsch = 0; zeichne(); }
      function zeichne() {
        satzEl.innerHTML = S.teile.map(function (t, i) {
          if (t.art) { var nx = S.teile[i + 1]; return 'There is ' + (nx.voll ? art(nx.a) : 'a'); }
          if (t.f) return t.f === '.' ? '.' : h(t.f);
          return '<span class="slot' + (t.voll ? ' voll' : i === ti ? ' jetzt' : '') + '">' + (t.voll ? h(t.a) : '&nbsp;?&nbsp;') + '</span>';
        }).join(' ').replace(/ \./g, '.');
        opts.innerHTML = '';
        if (ti >= S.teile.length) return;
        S.teile[ti].o.forEach(function (w) {
          var k = document.createElement('button'); k.dataset.w = w;
          k.textContent = w; // Farben ohne Farbpunkt: die Wörter sollen gelernt werden
          opts.appendChild(k);
        });
      }
      opts.onclick = function (e) {
        var k = e.target.closest('[data-w]'); if (!k || ti >= S.teile.length) return;
        var t = S.teile[ti];
        if (k.dataset.w === t.a) {
          t.voll = true; tone(620 + ti * 40, 0.07, 'sine', 0.08); nextSlot();
          if (ti >= S.teile.length) {
            var fertigerSatz = satzEl.textContent.replace(/\s+/g, ' ').replace(/ \./g, '.').trim();
            sag(fertigerSatz);
            api.later(function () {
              heft.innerHTML += '<p>' + h(fertigerSatz) + '</p>';
              si++;
              if (si < SAETZE.length) neuerSatz(); else bildFertig();
            }, 900);
          }
        } else {
          fehler++; falsch++; bad(); k.classList.add('no'); k.classList.remove('shake'); void k.offsetWidth; k.classList.add('shake');
          api.msg('<span class="em">🤔</span> Schau nochmal genau hin!');
          if (falsch >= 2) Array.prototype.forEach.call(opts.children, function (c) { if (c.dataset.w === t.a) c.classList.add('hint'); });
        }
      };
      nextSlot();
    }
    function bildFertig() {
      zeigeBild(null); opts.innerHTML = ''; satzEl.innerHTML = '🎨 <b>' + h(titel[idx]) + '</b>';
      var ok = fehler <= erlaubt;
      api.msg(ok ? '<span class="em">🎉</span> ' + pick(LOB, 1)[0] + ' Das ganze Bild ist beschrieben' + (fehler ? '.' : ', ganz ohne Fehler!') :
        '<span class="em">💪</span> Geschafft! Es waren noch ' + fehler + ' Fehler. Beim nächsten Bild klappt es besser.');
      if (api.answer(ok, true)) weiterKnopf(api, steuer, function () { idx++; beschreiben(); });
      if (ok) good();
    }
    neuerSatz();
  }

  // ================= Stufe 3 und 5: Read / Listen and draw
  function malen() {
    var b = neuesBild(lv), voll = lv.extra, saetze = text(b, voll), versuch = 0, fertig = false, offen = !lv.hoer || !kannSprechen();
    var mein = { bg: '', it: [] }, wz = { m: 'form', s: 'circle', c: 'red', z: 'big', n: 1, d: 'up' }, fehlerFelder = [];
    var farben = lv.alle ? ALLE : GRUND;
    api.stage.innerHTML = '<div class="mu"><div class="spalte"><div class="bildplatz" style="width:100%"></div><div class="steuer"></div></div>' +
      '<div class="spalte"><div class="beschr"></div><div class="werk"></div></div></div>';
    var platz = api.stage.querySelector('.bildplatz'), beschr = api.stage.querySelector('.beschr'), werk = api.stage.querySelector('.werk'), steuer = api.stage.querySelector('.steuer');
    function zeigeText() {
      beschr.innerHTML = '<div class="kopfz"><span>' + (lv.hoer ? '👂 Listen and draw:' : '📜 Read and draw:') + '</span>' + (kannSprechen() && offen ? '<button class="hoer" data-hoer>🔊 Listen</button>' : '') + '</div>' +
        (offen ? saetze.map(function (s) { return '<p lang="en">' + h(s) + '</p>'; }).join('') :
          '<div class="zu"><button class="hoer gross" data-hoer>🔊 Hör gut zu!</button><br><button class="go alt" data-zeig style="margin-top:10px;font-size:18px;min-height:44px">👀 Text zeigen</button></div>');
    }
    zeigeText();
    beschr.onclick = function (e) {
      if (e.target.closest('[data-hoer]')) sag(saetze, true);
      if (e.target.closest('[data-zeig]')) { offen = true; zeigeText(); }
    };
    function zeigeBild() { platz.innerHTML = wand(mein, schild(), { felder: !fertig, fehler: fehlerFelder }); }
    function icon(s, d) { return '<svg viewBox="0 0 60 60">' + formSvg(s, 30, 32, s === 'rectangle' ? 11 : 17, d || 'up', '#5f6963') + '</svg>'; }
    function werkzeug() {
      var o = '<h3>1. Was willst du malen?</h3><div class="reihe">' +
        '<button class="tb" data-m="bg" aria-pressed="' + (wz.m === 'bg') + '">🖌️ <span lang="en">background</span></button>' +
        FORM.map(function (s) { return '<button class="tb" data-s="' + s + '" aria-pressed="' + (wz.m === 'form' && wz.s === s) + '">' + icon(s) + '<span lang="en">' + s + '</span></button>'; }).join('') +
        '<button class="tb" data-m="weg" aria-pressed="' + (wz.m === 'weg') + '">🧽 Radieren</button></div>';
      if (wz.m !== 'weg') {
        o += '<h3>2. Welche Farbe?</h3><div class="reihe">' + farben.map(function (c) {
          var an = wz.m === 'bg' ? mein.bg === c : wz.c === c;
          return '<button class="sw" data-c="' + c + '" aria-label="' + c + '" title="' + c + '" style="background:' + COL[c] + '" aria-pressed="' + an + '"></button>';
        }).join('') + '</div>';
      }
      if (voll && wz.m === 'form') {
        o += '<h3>3. Wie viele? Wie gross?</h3><div class="reihe" lang="en">' + [1, 2, 3, 4].map(function (n) { return '<button class="tb" data-n="' + n + '" aria-pressed="' + (wz.n === n) + '">' + (n === 1 ? 'one' : ZAHL[n]) + '</button>'; }).join('') +
          (wz.n === 1 ? ['little', 'big'].map(function (z) { return '<button class="tb" data-z="' + z + '" aria-pressed="' + (wz.z === z) + '">' + z + '</button>'; }).join('') : '') + '</div>';
        if (wz.s === 'triangle') o += '<h3>4. Wohin zeigt das Dreieck?</h3><div class="reihe" lang="en">' + RICHT.map(function (d) { return '<button class="tb" data-d="' + d + '" aria-pressed="' + (wz.d === d) + '">' + icon('triangle', d) + RICHTW[d].replace('facing ', '') + '</button>'; }).join('') + '</div>';
      }
      o += '<p style="margin:2px 0;color:var(--soft);font-size:18px">' + (wz.m === 'bg' ? '👉 Tippe auf eine Farbe für den Hintergrund.' : wz.m === 'weg' ? '👉 Tippe im Bild auf eine Form, die weg soll.' : '👉 Tippe im Bild auf den richtigen Platz.') + '</p>';
      werk.innerHTML = o;
    }
    werk.onclick = function (e) {
      var k = e.target.closest('button'); if (!k || fertig) return;
      if (k.dataset.m) wz.m = k.dataset.m;
      if (k.dataset.s) { wz.m = 'form'; wz.s = k.dataset.s; }
      if (k.dataset.c) { if (wz.m === 'bg') { mein.bg = k.dataset.c; zeigeBild(); } else wz.c = k.dataset.c; }
      if (k.dataset.n) wz.n = +k.dataset.n;
      if (k.dataset.z) wz.z = k.dataset.z;
      if (k.dataset.d) wz.d = k.dataset.d;
      tone(560, 0.04, 'sine', 0.06);
      werkzeug();
    };
    platz.onclick = function (e) {
      var z = e.target.closest('[data-p]'); if (!z || fertig) return;
      var p = +z.dataset.p, alt = mein.it.filter(function (x) { return x.p === p; })[0];
      mein.it = mein.it.filter(function (x) { return x.p !== p; });
      fehlerFelder = fehlerFelder.filter(function (q) { return q !== p; });
      if (wz.m === 'form') {
        var neu = { s: wz.s, c: wz.c, p: p, z: voll ? (wz.n > 1 ? 'little' : wz.z) : '', d: voll && wz.s === 'triangle' ? wz.d : 'up', n: voll ? wz.n : 1 };
        if (!alt || norm(alt, true) !== norm(neu, true)) { mein.it.push(neu); tone(700, 0.06, 'sine', 0.08); }
      } else if (wz.m === 'bg') { api.msg('<span class="em">🖌️</span> Für den Hintergrund tippst du auf eine Farbe.'); if (alt) mein.it.push(alt); }
      zeigeBild();
    };
    function pruefen() {
      if (fertig) return;
      if (!mein.bg && !mein.it.length) { api.msg('<span class="em">🖌️</span> Male zuerst etwas!'); return; }
      versuch++;
      var soll = {}, ist = {}, falsch = [];
      b.it.forEach(function (x) { soll[x.p] = norm(x, voll); });
      mein.it.forEach(function (x) { ist[x.p] = norm(x, voll); });
      range(9).forEach(function (p) { if (soll[p] !== ist[p]) falsch.push(p); });
      var bgOk = mein.bg === b.bg;
      if (bgOk && !falsch.length) {
        fertig = true; fehlerFelder = []; zeigeBild();
        api.msg('<span class="em">🎉</span> ' + pick(LOB, 1)[0] + ' Dein Bild hängt jetzt im Museum!' + (versuch === 1 ? ' Beim ersten Versuch!' : ''));
        if (api.answer(versuch <= 2)) weiterKnopf(api, steuer, function () { idx++; malen(); }); else steuer.innerHTML = '';
        werk.innerHTML = ''; if (!offen) { offen = true; zeigeText(); }
        return;
      }
      fehlerFelder = falsch; zeigeBild(); bad();
      var n = falsch.length + (bgOk ? 0 : 1);
      if (versuch >= 3) {
        fertig = true; fehlerFelder = []; zeigeBild();
        offen = true; zeigeText();
        werk.innerHTML = '<div class="loes">' + wand(b, 'So sieht das Bild aus', null, true) + '</div>';
        api.msg('<span class="em">💡</span> Schau, so sieht das Bild aus. Lies die Beschreibung nochmal.');
        if (api.answer(false, true)) weiterKnopf(api, steuer, function () { idx++; malen(); }); else steuer.innerHTML = '';
        return;
      }
      api.msg('<span class="em">🤔</span> Noch nicht ganz: ' + (n === 1 ? 'eine Sache stimmt' : n + ' Sachen stimmen') + ' noch nicht.' + (bgOk ? '' : ' <small>Schau auch den Hintergrund an!</small>') +
        (falsch.length ? ' <small>Die roten Felder musst du anschauen.</small>' : ''));
    }
    steuer.innerHTML = '<button class="go fertig">✓ Fertig!</button>';
    steuer.firstChild.onclick = pruefen;
    api.msg('<span class="em">🎨</span> Bild ' + (idx + 1) + ' von ' + G.n + ': ' + (offen ? 'Lies die Beschreibung und male das Bild.' : 'Hör gut zu und male das Bild.'));
    zeigeBild(); werkzeug();
    if (!offen) api.later(function () { sag(saetze); }, 600);
  }
};
"""
