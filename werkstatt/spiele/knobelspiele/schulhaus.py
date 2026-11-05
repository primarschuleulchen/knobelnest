# Knobelspiel «Im Schulhaus» (Englisch, Leseverstehen: Ortsangaben und Räume im Schulhaus).
# Nach der Leseübung «Unit 1» der Lehrerin (Text über die Green Park School, Räume auf dem Plan nummerieren).
# Wird von bauen.py aufgerufen: schulhaus.alle(spiel)
#
# Stufen (je 12 Aufgaben):
#   1 Wo ist was?        Ortspräpositionen mit Tieren auf einem Platz: next to, opposite, across from, to the left/right of,
#                        in the middle, between. Abwechselnd: Wort wählen (praepWort) und Tier hinsetzen (praepSetzen).
#   2 Die Räume          Wörter lernen am Plan vom Arbeitsblatt: Raum leuchtet → Wort wählen, oder Wort → Raum antippen
#   3 Green Park School  Der Text vom Arbeitsblatt, Satz für Satz: Raum antippen (ohne Nummern)
#   4 Lesen und finden   Jede Runde ein neues, erfundenes Schulhaus (neueSchule): andere Grösse der Räume, Eingänge
#                        links/rechts/unten, manchmal ein Raum hinten (behind). Sätze werden aus dem Plan erzeugt (aussagen):
#                        jeder Satz passt nur auf genau einen der noch nicht gefundenen Räume.
#   5 Hören und finden   wie 4, der Satz wird nur vorgelesen (Text kann man aufdecken)
#   6 Welcher Satz?      Neues Schulhaus, alles beschriftet, ein Raum leuchtet: welcher von drei Sätzen stimmt?
#
# Plan (SVG 760 × 515): Gebäude mit langem Gang, draussen drei Gebäude (rund, klein, lang).


def logo():
    # Kleiner Schulhausplan im runden Rahmen (gezeichnet, keine Bilddatei)
    return ('<svg class="logo" viewBox="0 0 100 100" aria-hidden="true">'
            '<circle cx="50" cy="50" r="48" fill="#dcf0fd" stroke="#d6ad45" stroke-width="3"/>'
            '<rect x="18" y="28" width="64" height="36" rx="2" fill="#fff" stroke="#3f78a8" stroke-width="2.5"/>'
            '<path d="M18 46h64M38 28v18M54 28v18M46 46v18M64 46v18" stroke="#3f78a8" stroke-width="2"/>'
            '<rect x="55" y="47" width="8" height="16" fill="#fbf3dc"/>'
            '<ellipse cx="28" cy="76" rx="9" ry="6" fill="#efe7f7" stroke="#3f78a8" stroke-width="2"/>'
            '<rect x="42" y="71" width="40" height="10" rx="2" fill="#dcf0fd" stroke="#3f78a8" stroke-width="2"/>'
            '<text x="59" y="44" font-size="13" text-anchor="middle">📍</text></svg>')


def alle(spiel):
    spiel(id='im-schulhaus', titel='Im Schulhaus', icon=logo(), fach='Englisch', thema='Places in school (Lesen)', stufe='4.–6. Klasse', sort=2, n=12,
          sterne={'modus': 'runde', 'n': 12},
          kurz='Englische Sätze über ein Schulhaus lesen und die Räume auf dem Plan finden.',
          intro='Lies, wo die Räume sind, und finde sie auf dem Plan: <b>next to</b>, <b>opposite</b>, <b>to the left of</b>, <b>in the middle</b> …',
          levels=[dict(name='Wo ist was?', info='next to, opposite, to the left …', t='praep'),
                  dict(name='Die Räume', info='Wie heissen die Räume auf Englisch?', t='wort'),
                  dict(name='Green Park School', info='Der Text vom Arbeitsblatt', t='text'),
                  dict(name='Lesen und finden', info='Immer ein neues Schulhaus', t='lesen'),
                  dict(name='Hören und finden', info='Nur anhören und finden', t='hoeren'),
                  dict(name='Welcher Satz stimmt?', info='Genau lesen: einer von drei', t='satz')],
          css=CSS, js=JS)


CSS = r"""
.ring{width:150px;height:150px;background:none;border:0;padding:0;box-shadow:0 8px 18px rgba(63,120,168,.18);border-radius:50%}.ring .logo{width:100%;height:100%;display:block}
@media (max-height:640px){.ring{width:100px;height:100px}}
@media (min-width:641px) and (max-height:820px){.ring{width:96px;height:96px}.kopf h1{font-size:34px;margin-top:4px}.kopf p{font-size:18px;margin-top:2px}
  .lvs{grid-template-columns:1fr 1fr;max-width:900px;gap:10px;margin-top:10px}.lv{min-height:62px;padding:8px 14px}}
.msg{min-height:0;margin:0 0 8px;font-size:21px;line-height:1.3}
.top{margin-bottom:4px}
.stage{max-width:1240px}.sh{display:flex;flex-direction:column;align-items:center;gap:10px;width:100%;max-width:1240px}
.karte{background:#fff;border:2px solid var(--line);border-radius:20px;padding:10px 16px;box-shadow:var(--sch-k);font-size:23px;line-height:1.4;width:100%;max-width:820px;position:relative}
.karte .vor{display:block;color:var(--soft);font-size:17px;margin-bottom:2px}
.karte b{font-weight:400;color:var(--sky-d);background:var(--sun);border-radius:6px;padding:0 4px}
.karte .luecke{display:inline-block;min-width:90px;border-bottom:3px solid var(--gold);text-align:center;color:var(--sky-d)}
.karte .tier{font-size:40px;line-height:1;vertical-align:middle;margin-right:4px}
.karte .zeile{display:flex;align-items:center;gap:10px;flex-wrap:wrap}
.karte .zeile .tx{flex:1;min-width:200px}
.knopf{background:var(--sun);border:2px solid var(--gold-d);border-radius:14px;min-height:44px;padding:2px 12px;font-size:19px;box-shadow:var(--sch-k);white-space:nowrap}
.knopf.weiss{background:#fff;border-color:var(--line2)}
.verdeckt{color:var(--soft);font-size:19px}
.plan{width:min(100%,calc((100vh - 290px) * 760 / 515),860px);min-width:min(100%,420px);display:block;touch-action:manipulation}
.plan svg{width:100%;height:auto;display:block}
.plan .raum{cursor:pointer}
.plan .raum rect,.plan .raum ellipse{transition:fill .25s}
.plan.tippen .raum:hover .r{fill:#fff3cf}
.plan .raum.leer .r{stroke-dasharray:9 7;fill:#fbfbf7}
.plan .raum.anker .r{fill:#d6ebfb}
.plan .raum.ziel .r{fill:#ffe39a}
.plan .raum.ok .r{fill:#e2f1d9}
.plan .raum.no .r{fill:#f7d2cd}
.plan .raum.zeig .r{fill:#ffe39a;animation:blink .5s 3}
@keyframes blink{50%{fill:#fff}}
.opts{display:grid;grid-template-columns:1fr 1fr;gap:10px;width:100%;max-width:820px}
.opts.eins{grid-template-columns:1fr}
.opts button{font-size:22px;min-height:56px;border-radius:18px;background:#fff;border:2px solid var(--ink);box-shadow:var(--sch-k);padding:6px 12px;line-height:1.25;text-align:center}
.opts.eins button{text-align:left;font-size:21px}
.opts button.ok{background:#e7f3df;border-color:var(--ok)}.opts button.no{background:#fbe5e2;border-color:var(--no)}.opts button.hint{background:var(--sun);border-color:var(--gold)}
.hilfe{display:none;background:#fff;border:2px solid var(--gold);border-radius:18px;padding:10px 14px;box-shadow:var(--sch-k);font-size:18px;width:100%;max-width:820px;columns:2;column-gap:24px}
.hilfe.auf{display:block}
.hilfe div{break-inside:avoid;padding:1px 0}.hilfe i{font-style:normal;color:var(--sky-d)}
.leiste{display:flex;gap:8px;justify-content:center;flex-wrap:wrap}
@media (max-width:640px){.karte{font-size:20px;padding:8px 12px}.opts button{font-size:19px;min-height:50px}.opts.eins button{font-size:18px}.hilfe{columns:1;font-size:17px}.msg{font-size:19px}}
/* iPad quer und Laptop: Plan links, Text und Antworten rechts */
@media (min-width:900px) and (max-height:900px){
  .sh{flex-direction:row;align-items:flex-start;justify-content:center;gap:18px}
  .sh .links{flex:2.2;display:flex;justify-content:center;min-width:0}.sh .rechts{flex:1;display:flex;flex-direction:column;gap:10px;align-items:stretch;max-width:400px;min-width:280px}
  .plan{width:100%;max-width:calc((100vh - 130px) * 760 / 515)}.karte{font-size:22px}
  .opts{grid-template-columns:1fr}.hilfe{columns:1}}
.links,.rechts{display:contents}
@media (min-width:900px) and (max-height:900px){.links,.rechts{display:flex}}
"""


JS = r"""
// =====================================================================  Vorlesen
// Englische Stimme wie in der Vokabelkiste. Gegen abgehacktes Vorlesen: nicht sofort nach cancel() sprechen,
// Apostroph ’ als ' (sonst stocken manche Stimmen), und die nächste Aufgabe wartet, bis fertig gesprochen ist.
var FEMALE = /\b(female|samantha|karen|moira|tessa|serena|kate|stephanie|martha|fiona|victoria|allison|ava|susan|zira|hazel|libby|sonia|aria|jenny|emma|amy|joanna|salli|kimberly|olivia|natasha|clara)\b/i;
var MALE = /\b(male|daniel|alex|fred|oliver|george|ryan|guy|david|mark|james|thomas|arthur|rishi|aaron|gordon|reed|rocko|eddy|grandpa)\b/i;
function stimme() {
  var vs = []; try { vs = speechSynthesis.getVoices().filter(function (v) { return v.lang && /^en/i.test(v.lang); }); } catch (e) {}
  if (!vs.length) return null;
  function sc(v) { var n = v.name.replace(/female/ig, ''); return (FEMALE.test(v.name) ? 10 : 0) - (MALE.test(n) ? 10 : 0) + (/en[-_]gb/i.test(v.lang) ? 3 : 0) + (/natural|neural|premium|enhanced|online/i.test(v.name) ? 4 : 0); }
  return vs.slice().sort(function (a, b) { return sc(b) - sc(a); })[0];
}
function kannSprechen() { return !!(window.speechSynthesis && window.SpeechSynthesisUtterance); }
var AKT_U = null, SPRICHT = false, SAG_NR = 0;
function sag(t) {
  if (!kannSprechen()) return;
  t = String(t).replace(/[’‘]/g, "'").replace(/…/g, '');
  var ss = speechSynthesis, nr = ++SAG_NR;
  function los() {
    if (nr !== SAG_NR) return;
    try {
      var u = new SpeechSynthesisUtterance(t), v = stimme();
      if (v) { u.voice = v; u.lang = String(v.lang).replace('_', '-'); } else u.lang = 'en-GB';
      u.rate = .82; u.onend = u.onerror = function () { if (AKT_U === u) SPRICHT = false; };
      AKT_U = u; SPRICHT = true; ss.speak(u);
      setTimeout(function () { if (AKT_U === u) SPRICHT = false; }, 3000 + t.length * 120);  // falls das Gerät «fertig» nicht meldet
    } catch (e) { SPRICHT = false; }
  }
  try { if (ss.paused) ss.resume(); if (ss.speaking || ss.pending) { ss.cancel(); setTimeout(los, 180); } else los(); } catch (e) {}
}
try { if (window.speechSynthesis) speechSynthesis.getVoices(); } catch (e) {}

// =====================================================================  Zeichnen
function zeilen(name, b) {
  var w = name.split(' '), out = [], cur = '';
  w.forEach(function (x) { if (cur && (cur + ' ' + x).length * 8.6 > b - 6) { out.push(cur); cur = x; } else cur = cur ? cur + ' ' + x : x; });
  if (cur) out.push(cur); return out;
}
function textSvg(x, y, t, fs, extra) { return '<text x="' + x + '" y="' + y + '" font-size="' + fs + '" text-anchor="middle"' + (extra || '') + '>' + h(t) + '</text>'; }
function schild(x, y, t, fs, dreh) {
  return '<text x="' + x + '" y="' + y + '" font-size="' + (fs || 14) + '" fill="#5f6963" text-anchor="middle" dominant-baseline="middle"' + (dreh ? ' transform="rotate(-90 ' + x + ' ' + y + ')"' : '') + '>' + h(t) + '</text>';
}
function baum(x, y, r) { return '<circle cx="' + x + '" cy="' + y + '" r="' + r + '" fill="#a9cf95" stroke="#7fae6a" stroke-width="2"/>'; }
function tuer(x, y, senk) { return senk ? '<rect x="' + (x - 2) + '" y="' + y + '" width="4" height="18" fill="#fff"/>' : '<rect x="' + x + '" y="' + (y - 2) + '" width="18" height="4" fill="#fff"/>'; }
function raumSvg(r) {
  var f = 'fill="#fff" stroke="#5f6963" stroke-width="2.5"';
  return '<g class="raum" data-s="' + r.id + '">' + (r.rund ? '<ellipse class="r" cx="' + (r.x + r.b / 2) + '" cy="' + (r.y + r.h / 2) + '" rx="' + r.b / 2 + '" ry="' + r.h / 2 + '" ' + f + '/>' :
    '<rect class="r" x="' + r.x + '" y="' + r.y + '" width="' + r.b + '" height="' + r.h + '" ' + f + '/>') + '<g class="lab" pointer-events="none"></g></g>';
}
// Beschriftung eines Raums: Bild und Name (art: 'leer', 'bild' = nur Bild, 'voll')
function beschrifte(svg, r, art) {
  var g = svg.querySelector('[data-s="' + r.id + '"] .lab'), cx = r.x + r.b / 2, o = '', nm = r.name;
  if (!nm || art === 'leer') { g.innerHTML = ''; return; }
  var z = art === 'bild' ? [] : zeilen(nm.n, r.h < 70 && r.b < 200 ? r.b - 22 : r.b), fs = r.b < 80 ? 15 : 17, top = r.y + r.h / 2;
  var hoch = 30 + z.length * (fs + 1);
  if (r.h < 70) { // flacher Raum: Bild links, Name rechts
    var lang = r.b > 200;
    o += textSvg(lang ? cx - 70 : r.x + 17, r.y + r.h / 2 + 9, nm.e, lang ? 30 : 22);
    z.forEach(function (t, i) { o += textSvg(lang ? cx + 20 : cx + 13, r.y + r.h / 2 + 5 - (z.length - 1) * 7.5 + i * 15, t, lang ? 18 : 13.5, ' fill="#1f2421"'); });
  } else {
    var y0 = top - hoch / 2 + 26;
    o += textSvg(cx, y0, nm.e, 28);
    z.forEach(function (t, i) { o += textSvg(cx, y0 + 6 + (i + 1) * (fs + 1), t, fs, ' fill="#1f2421"'); });
  }
  g.innerHTML = o;
}
function satzHtml(s) { return h(s).replace('\u0001', '<b>').replace('\u0002', '</b>'); }
function satzTxt(s) { return s.replace('\u0001', '').replace('\u0002', ''); }

// =====================================================================  Green Park School (Arbeitsblatt)
var PL = {
  s12: { x: 20, y: 210, b: 130, h: 160 }, s11: { x: 195, y: 10, b: 135, h: 200 }, s10: { x: 225, y: 250, b: 75, h: 120 },
  s9: { x: 300, y: 250, b: 90, h: 120 }, s8: { x: 370, y: 10, b: 85, h: 200 }, s7: { x: 665, y: 10, b: 85, h: 200 },
  s6: { x: 450, y: 250, b: 108, h: 60 }, s5: { x: 450, y: 310, b: 108, h: 60 }, s4: { x: 665, y: 250, b: 85, h: 120 },
  s3: { x: 10, y: 400, b: 170, h: 104, rund: true }, s2: { x: 215, y: 415, b: 100, h: 75 }, s1: { x: 345, y: 420, b: 400, h: 65 }
};
var BLATT = {
  s1: { n: 'swimming pool', e: '🏊', de: 'Schwimmbad' }, s2: { n: 'gym', e: '🏀', de: 'Turnhalle' }, s3: { n: 'assembly hall', e: '🎭', de: 'Aula' },
  s4: { n: 'kitchen', e: '🍳', de: 'Küche' }, s5: { n: 'science room', e: '🔬', de: 'Naturkunde-Zimmer' },
  s6: { n: 'headmaster’s office', e: '👔', de: 'Büro der Schulleitung' }, s7: { n: 'history classrooms', e: '🏛️', de: 'Geschichtszimmer', p: 1 },
  s8: { n: 'canteen', e: '🍽️', de: 'Mensa' }, s9: { n: 'teacher’s bathroom', e: '🚽', de: 'WC für Lehrpersonen' },
  s10: { n: 'teacher’s room', e: '☕', de: 'Lehrerzimmer' }, s11: { n: 'computer rooms', e: '💻', de: 'Computerräume', p: 1 },
  s12: { n: 'library', e: '📚', de: 'Bibliothek' }
};
// Der Text vom Arbeitsblatt, Satz für Satz (in dieser Reihenfolge)
var TEXT = [
  ['s12', 'The main entrance of Green Park School is on the left side of the building, next to the {n}.'],
  ['s11', 'When you walk into the building and turn left, you can see some {n}.'],
  ['s10', 'On the right, next to the changing rooms, there is the {n}.'],
  ['s9', 'When you walk down the corridor, the third room on the right is the {n}.'],
  ['s8', 'Opposite the music room you find the {n}.'],
  ['s7', 'At the very end of the long corridor on the left side you can see the {n}.'],
  ['s6', 'Across the children’s bathrooms there is the {n}.'],
  ['s5', 'Right behind that and next to the music room there is the {n}.'],
  ['s4', 'At the end of the corridor on the right side there is a big {n}.'],
  ['s3', 'If you walk out of the building through the side entrance you can see our {n}. It’s that round building.'],
  ['s2', 'The smaller building next to it is our {n}'],
  ['s1', 'and in the long building is our {n}.']
];
function greenParkSvg() {
  var o = '<svg viewBox="0 0 760 515" font-family="Patrick Hand, sans-serif">';
  o += '<rect x="0" y="0" width="760" height="515" rx="14" fill="#eef3ea"/>';
  o += '<rect x="12" y="40" width="112" height="150" rx="8" fill="#dfe5ea"/>' + schild(68, 100, 'main', 16) + schild(68, 120, 'entrance', 16) + '<path d="M118 115h26" stroke="#9aa8b4" stroke-width="3" stroke-dasharray="5 4"/><text x="134" y="111" font-size="13" text-anchor="middle" fill="#9aa8b4">▶</text>';
  o += baum(30, 22, 10) + baum(58, 22, 10) + baum(86, 22, 10);
  o += '<path d="M150 10H750V370H150V370H20V210H150Z" fill="#f7f4ec" stroke="#5f6963" stroke-width="4"/>';
  o += '<g fill="#e7e2d6" stroke="#5f6963" stroke-width="2.5">' +
    '<rect x="455" y="10" width="110" height="170" fill="#d9ead0"/>' +
    '<rect x="455" y="180" width="55" height="30"/><rect x="510" y="180" width="55" height="30"/>' +
    '<rect x="565" y="10" width="65" height="200"/>' +
    '<rect x="150" y="250" width="75" height="120"/><rect x="390" y="250" width="60" height="120"/>' +
    '<rect x="580" y="250" width="50" height="120"/></g>';
  o += baum(490, 50, 16) + baum(530, 40, 10) + baum(500, 135, 14) + baum(538, 112, 9);
  o += schild(597, 110, 'classrooms', 15, true) + schild(187, 310, 'changing rooms', 15, true) + schild(420, 310, 'music room', 15, true) + schild(605, 310, 'classroom', 15, true);
  o += '<text x="482" y="201" font-size="16" text-anchor="middle">🚹</text><text x="537" y="201" font-size="16" text-anchor="middle">🚺</text>';
  o += '<rect x="632" y="366" width="31" height="8" fill="#fff"/>' + schild(647, 388, 'side entrance', 14);
  o += tuer(150, 106, true) + tuer(160, 250) + tuer(470, 210) + tuer(596, 250) + tuer(410, 250) + tuer(588, 210) + tuer(640, 210);
  Object.keys(PL).forEach(function (k) { o += raumSvg(Object.assign({ id: k }, PL[k])); if (k === 's11') o += '<path d="M195 110h135" stroke="#5f6963" stroke-width="2" pointer-events="none"/>'; });
  return o + '</svg>';
}
function greenPark() {
  var R = {}; Object.keys(PL).forEach(function (k) { R[k] = Object.assign({ id: k, slot: true, name: BLATT[k] }, PL[k]); });
  return { svg: greenParkSvg(), R: R, slots: Object.keys(PL) };
}

// =====================================================================  Erfundene Schulhäuser (Stufe 4–6)
var POOL_DRIN = [
  { n: 'library', e: '📚', de: 'Bibliothek' }, { n: 'computer room', e: '💻', de: 'Computerraum' }, { n: 'teachers’ room', e: '☕', de: 'Lehrerzimmer' },
  { n: 'teachers’ bathroom', e: '🚽', de: 'WC für Lehrpersonen' }, { n: 'canteen', e: '🍽️', de: 'Mensa' }, { n: 'history classroom', e: '🏛️', de: 'Geschichtszimmer' },
  { n: 'headmaster’s office', e: '👔', de: 'Büro der Schulleitung' }, { n: 'science room', e: '🔬', de: 'Naturkunde-Zimmer' }, { n: 'kitchen', e: '🍳', de: 'Küche' },
  { n: 'art room', e: '🎨', de: 'Zeichenzimmer' }, { n: 'school office', e: '🗂️', de: 'Sekretariat' }, { n: 'English classroom', e: '💬', de: 'Englischzimmer' },
  { n: 'maths classroom', e: '➗', de: 'Mathematikzimmer' }, { n: 'nurse’s room', e: '🩹', de: 'Krankenzimmer' }
];
var POOL_DRAUSSEN = [{ n: 'assembly hall', e: '🎭', de: 'Aula' }, { n: 'gym', e: '🏀', de: 'Turnhalle' }, { n: 'swimming pool', e: '🏊', de: 'Schwimmbad' }];
var FEST = [{ n: 'music room' }, { n: 'classroom' }, { n: 'changing rooms', p: 1 }, { n: 'children’s bathrooms', p: 1 }];
var FORMEN = { round: { b: 170, h: 96, rund: true }, small: { b: 120, h: 84 }, long: { b: 320, h: 62 } };
var X0 = 80, X1 = 680, YT = 18, YC = 188, YC2 = 234, YB = 372;
function teile(n, tot) {
  var w = range(n).map(function () { return .8 + Math.random() * .55; }), s = w.reduce(function (a, b) { return a + b; }, 0), out = [], acc = 0;
  w.forEach(function (x, i) { var b = i === n - 1 ? tot - acc : Math.round(tot * x / s); out.push(b); acc += b; });
  return out;
}
function neueSchule() {
  var rooms = [], oben = rnd(5, 6), unten = 11 - oben, gb = 46, x = X0, R = {};
  teile(oben, X1 - X0).forEach(function (b) { rooms.push({ row: 'T', x: x, b: b, y: YT, h: YC - YT }); x += b; });
  var gi = rnd(1, unten - 1), gang = null; x = X0;
  teile(unten, X1 - X0 - gb).forEach(function (b, i) { if (i === gi) { gang = { x: x, b: gb }; x += gb; } rooms.push({ row: 'B', x: x, b: b, y: YC2, h: YB - YC2 }); x += b; });
  // manchmal liegt hinter einem oberen Raum noch ein Raum (behind / in front of)
  if (Math.random() < .55) {
    var v = rooms[rnd(1, oben - 2)], hh = Math.round((YC - YT) / 2), bk = { row: 'T', back: true, x: v.x, b: v.b, y: YT, h: hh, vor: v };
    v.y = YT + hh; v.h = YC - YT - hh; v.hinten = bk; rooms.push(bk);
  }
  // beschriftete Räume, die übrigen 9 sind zu finden
  var vorne = rooms.filter(function (r) { return !r.back; }), nFest = rooms.length - 9;
  var fest = pick(vorne, nFest), fn = pick(FEST, nFest), sn = pick(POOL_DRIN, 9), si = 0;
  rooms.forEach(function (r) { var f = fest.indexOf(r); if (f >= 0) { r.fest = true; r.name = fn[f]; } else { r.slot = true; r.name = sn[si++]; } });
  // Eingänge: einer am Ende des Gangs (links oder rechts), einer unten
  var endL = Math.random() < .5, mainEnd = Math.random() < .5;
  var eEnd = mainEnd ? 'main entrance' : 'back entrance', eBot = mainEnd ? 'side entrance' : 'main entrance', gx = gang.x + gb / 2;
  var geher = [endL ? { e: eEnd, x0: X0, dir: 1, links: 'T' } : { e: eEnd, x0: X1, dir: -1, links: 'B' },
    { e: eBot, x0: gx, dir: -1, links: 'B', turn: 'left' }, { e: eBot, x0: gx, dir: 1, links: 'T', turn: 'right' }];
  // draussen: rund, klein, lang in zufälliger Reihenfolge
  var ox = 50, nd = shuffle(POOL_DRAUSSEN);
  shuffle(['round', 'small', 'long']).forEach(function (f, i) {
    var F = FORMEN[f]; rooms.push({ row: 'O', i: i, shape: f, x: ox, b: F.b, y: 455 - F.h / 2, h: F.h, rund: F.rund, slot: true, name: nd[i] }); ox += F.b + 30;
  });
  rooms.forEach(function (r, i) { r.id = 'r' + i; R[r.id] = r; });
  var S = { R: R, rooms: rooms, geher: geher, gang: gang, endL: endL, eEnd: eEnd, eBot: eBot };
  S.svg = schuleSvg(S);
  S.slots = rooms.filter(function (r) { return r.slot; }).map(function (r) { return r.id; });
  return S;
}
function schuleSvg(S) {
  var o = '<svg viewBox="0 0 760 515" font-family="Patrick Hand, sans-serif"><rect x="0" y="0" width="760" height="515" rx="14" fill="#eef3ea"/>';
  o += '<rect x="' + X0 + '" y="' + YT + '" width="' + (X1 - X0) + '" height="' + (YB - YT) + '" fill="#f7f4ec" stroke="#5f6963" stroke-width="4"/>';
  var ex = S.endL ? X0 : X1, my = (YC + YC2) / 2, g = S.gang;
  S.rooms.forEach(function (r) {
    if (r.row === 'O') { o += raumSvg(r); return; }
    if (r.fest) {
      o += '<rect x="' + r.x + '" y="' + r.y + '" width="' + r.b + '" height="' + r.h + '" fill="#e7e2d6" stroke="#5f6963" stroke-width="2.5"/>';
      if (r.b >= 96) zeilen(r.name.n, r.b).forEach(function (t, i, a) { o += schild(r.x + r.b / 2, r.y + r.h / 2 + (i - (a.length - 1) / 2) * 18, t, 16); });
      else o += schild(r.x + r.b / 2, r.y + r.h / 2, r.name.n, 15, true);
    } else o += raumSvg(r);
  });
  // Türen
  S.rooms.forEach(function (r) { if (r.row !== 'O') o += tuer(r.x + r.b / 2 - 9, r.back ? r.y + r.h : r.row === 'T' ? YC : YC2); });
  // Eingang am Ende des Gangs und unten
  o += '<rect x="' + (ex - 4) + '" y="' + (YC + 7) + '" width="8" height="' + (YC2 - YC - 14) + '" fill="#f7f4ec"/>';
  o += schild(S.endL ? X0 - 40 : X1 + 40, my, S.eEnd, 17, true) + '<text x="' + (S.endL ? X0 - 16 : X1 + 16) + '" y="' + (my + 5) + '" font-size="15" text-anchor="middle" fill="#9aa8b4">' + (S.endL ? '▶' : '◀') + '</text>';
  o += '<rect x="' + (g.x + 7) + '" y="' + (YB - 4) + '" width="' + (g.b - 14) + '" height="8" fill="#f7f4ec"/>' + schild(g.x + g.b / 2, YB + 16, S.eBot, 16);
  o += baum(S.endL ? 712 : 30, 40, 11) + baum(S.endL ? 738 : 56, 64, 9) + baum(S.endL ? 716 : 34, 330, 12);
  return o + '</svg>';
}

// ---------- Was stimmt für einen Raum? (Aussagen mit Prüf-Funktion, aus dem Plan berechnet)
function adj(a, b) { return a !== b && a.row === b.row && a.row !== 'O' && !a.back && !b.back && (Math.abs(a.x + a.b - b.x) < 1 || Math.abs(b.x + b.b - a.x) < 1); }
function gegen(a, b) {
  if (a.row === b.row || a.row === 'O' || b.row === 'O' || a.back || b.back) return false;
  return Math.min(a.x + a.b, b.x + b.b) - Math.max(a.x, b.x) >= .6 * Math.min(a.b, b.b);
}
function seite(S, g, side) {
  return S.rooms.filter(function (r) { return r.row === side && !r.back && (r.x + r.b / 2 - g.x0) * g.dir > 0; })
    .sort(function (a, b) { return (a.x - b.x) * g.dir; });
}
function outI(S, i) { return S.rooms.filter(function (r) { return r.row === 'O' && r.i === i; })[0]; }
function aussagen(S, r, lab) {
  var A = [];
  function add(typ, test, d) { d.typ = typ; d.test = test; A.push(d); }
  if (r.row === 'O') {
    add('form', function (x) { return x.shape === r.shape; }, { f: r.shape });
    if (r.i === 1) {
      add('mitte', function (x) { return x.row === 'O' && x.i === 1; }, {});
      var a0 = outI(S, 0), a2 = outI(S, 2);
      if (lab(a0) && lab(a2)) add('zw', function (x) { return x.row === 'O' && x.i === 1; }, { a: a0, b: a2 });
    }
    S.rooms.forEach(function (a) {
      if (a.row !== 'O' || a === r || !lab(a) || Math.abs(a.i - r.i) !== 1) return;
      add('nb', function (x) { return x.row === 'O' && Math.abs(x.i - a.i) === 1; }, { a: a });
      var li = r.i < a.i; add(li ? 'links' : 'rechts', function (x) { return x.row === 'O' && x.i === a.i + (li ? -1 : 1); }, { a: a });
    });
    return A;
  }
  if (r.back) { if (lab(r.vor)) add('hinter', function (x) { return x.vor === r.vor; }, { a: r.vor }); return A; }
  if (r.hinten && lab(r.hinten)) add('vor', function (x) { return x.hinten === r.hinten; }, { a: r.hinten });
  var nb = S.rooms.filter(function (a) { return adj(a, r); });
  nb.forEach(function (a) {
    if (!lab(a)) return;
    add('nb', function (x) { return adj(x, a); }, { a: a });
    var li = r.x < a.x; add(li ? 'links' : 'rechts', function (x) { return adj(x, a) && (li ? x.x < a.x : x.x > a.x); }, { a: a });
  });
  if (nb.length === 2 && lab(nb[0]) && lab(nb[1])) { var n0 = nb[0], n1 = nb[1]; add('zw', function (x) { return adj(x, n0) && adj(x, n1); }, { a: n0, b: n1 }); }
  S.rooms.forEach(function (a) { if (lab(a) && gegen(a, r)) add('gegen', function (x) { return gegen(x, a); }, { a: a }); });
  S.geher.forEach(function (g) {
    ['left', 'right'].forEach(function (s) {
      var side = s === 'left' ? g.links : (g.links === 'T' ? 'B' : 'T'), L = seite(S, g, side), p = L.indexOf(r);
      if (p < 0) return;
      if (p < ORD.length) add('ord', function (x) { return seite(S, g, side)[p] === x; }, { g: g, s: s, k: p });
      if (p === L.length - 1 && p >= 1) add('letzt', function (x) { var M = seite(S, g, side); return M[M.length - 1] === x; }, { g: g, s: s });
    });
  });
  return A;
}
var ORD = ['first', 'second', 'third', 'fourth', 'fifth', 'sixth'];
var TX = {
  nb: ['The {n} {is} next to the {a}.', 'Next to the {a} you can find the {n}.', 'You can find the {n} next to the {a}.'],
  links: ['The {n} {is} to the left of the {a}.', 'To the left of the {a} you can see the {n}.', 'Look at the {a}. To the left of it there is the {n}.'],
  rechts: ['The {n} {is} to the right of the {a}.', 'To the right of the {a} you can see the {n}.', 'Look at the {a}. To the right of it there is the {n}.'],
  zw: ['The {n} {is} between the {a} and the {b}.', 'Between the {a} and the {b} there is the {n}.', 'The {n} {is} in the middle, between the {a} and the {b}.'],
  gegen: ['The {n} {is} opposite the {a}.', 'Opposite the {a} you find the {n}.', 'Across from the {a} there is the {n}.', 'The {n} {is} across the corridor from the {a}.'],
  hinter: ['The {n} {is} behind the {a}.', 'Behind the {a} there is the {n}.', 'Go into the {a}. Behind it you can find the {n}.'],
  vor: ['The {n} {is} in front of the {a}.', 'In front of the {a} you can see the {n}.'],
  form: ['The {n} {is} in the {f} building.', 'The {f} building outside is the {n}.', 'Walk out of the school. The {f} building is the {n}.'],
  mitte: ['The building in the middle is the {n}.', 'The {n} {is} the building in the middle.'],
  ordE: ['Come in through the {e} and walk down the corridor. The {k} room on your {s} is the {n}.', 'When you come in through the {e}, the {n} {is} the {k} room on the {s}.', 'Walk in through the {e}. The {k} door on the {s} is the {n}.'],
  ordT: ['Come in through the {e} and turn {t}. The {k} room on your {s} is the {n}.', 'Walk in through the {e} and turn {t}. The {n} {is} the {k} room on the {s}.', 'Go in through the {e}, turn {t} and walk down the corridor. The {k} door on your {s} is the {n}.'],
  letztE: ['Come in through the {e}. At the very end of the corridor on the {s} side you can see the {n}.', 'Walk in through the {e} and go to the end of the corridor. The last room on your {s} is the {n}.'],
  letztT: ['Come in through the {e} and turn {t}. At the end of the corridor on the {s} side there is the {n}.', 'Walk in through the {e} and turn {t}. The last room on the {s} is the {n}.']
};
var HINT = { nb: 'next to = neben', links: 'to the left of = links von', rechts: 'to the right of = rechts von', zw: 'between = zwischen', gegen: 'opposite / across from = gegenüber',
  hinter: 'behind = hinter', vor: 'in front of = vor', form: 'round / small / long = rund / klein / lang', mitte: 'in the middle = in der Mitte',
  ord: 'first, second, third = erste, zweite, dritte; on your left = links von dir', letzt: 'last = letzte; at the end = am Ende' };
function hinweis(d) { return HINT[d.typ] + (d.g && d.g.turn ? '; turn ' + d.g.turn + ' = ' + (d.g.turn === 'left' ? 'links' : 'rechts') + ' abbiegen' : ''); }
function satzAus(d, r) {
  var key = d.typ === 'ord' || d.typ === 'letzt' ? d.typ + (d.g.turn ? 'T' : 'E') : d.typ;
  return pick(TX[key], 1)[0].replace('{is}', r.name.p ? 'are' : 'is').replace('{a}', d.a ? d.a.name.n : '').replace('{b}', d.b ? d.b.name.n : '')
    .replace('{e}', d.g ? d.g.e : '').replace('{t}', d.g && d.g.turn || '').replace('{s}', d.s || '').replace('{k}', d.k != null ? ORD[d.k] : '')
    .replace('{f}', d.f || '').replace('{n}', '\u0001' + r.name.n + '\u0002');
}
// erst eine Art Satz zufällig wählen, dann einen Satz dieser Art (damit es abwechslungsreich bleibt)
function waehle(A) {
  var arten = []; A.forEach(function (d) { if (arten.indexOf(d.typ) < 0) arten.push(d.typ); });
  var t = pick(arten, 1)[0]; return pick(A.filter(function (d) { return d.typ === t; }), 1)[0];
}

// =====================================================================  Stufe 1: Ortspräpositionen mit Tieren
var TIERE = [['cat', '🐱'], ['dog', '🐶'], ['rabbit', '🐰'], ['mouse', '🐭'], ['horse', '🐴'], ['cow', '🐮'], ['pig', '🐷'], ['duck', '🦆'],
  ['frog', '🐸'], ['owl', '🦉'], ['fox', '🦊'], ['bear', '🐻'], ['lion', '🦁'], ['sheep', '🐑'], ['tiger', '🐯'], ['monkey', '🐵']].map(function (x) { return { n: x[0], e: x[1] }; });
var SPOT = { T0: { row: 'T', c: 0 }, T1: { row: 'T', c: 1 }, T2: { row: 'T', c: 2 }, M: { row: 'M', c: 1 }, B0: { row: 'B', c: 0 }, B1: { row: 'B', c: 1 }, B2: { row: 'B', c: 2 } };
var PWORT = ['next to', 'to the left of', 'to the right of', 'opposite', 'across from'];
var PHINT = { 'next to': 'next to = neben', 'to the left of': 'to the left of = links von', 'to the right of': 'to the right of = rechts von', 'opposite': 'opposite = gegenüber',
  'across from': 'across from = gegenüber', 'in the middle': 'in the middle = in der Mitte', 'between': 'between = zwischen' };
Object.keys(SPOT).forEach(function (k) {
  var s = SPOT[k]; s.id = k;
  if (s.row === 'M') { s.x = 285; s.y = 205; s.b = 190; s.h = 110; s.rund = true; } else { s.x = 70 + s.c * 220; s.y = s.row === 'T' ? 38 : 362; s.b = 180; s.h = 120; }
});
// Welche Wörter stimmen für Platz a im Verhältnis zu Platz b?
function pw(a, b) {
  var A = SPOT[a], B = SPOT[b], w = {};
  if (a === b || A.row === 'M' || B.row === 'M') return w;
  if (A.row === B.row && Math.abs(A.c - B.c) === 1) { w['next to'] = 1; w[A.c < B.c ? 'to the left of' : 'to the right of'] = 1; }
  if (A.row !== B.row && A.c === B.c) { w['opposite'] = 1; w['across from'] = 1; }
  return w;
}
function praepSvg() {
  var o = '<svg viewBox="0 0 760 515" font-family="Patrick Hand, sans-serif"><rect x="0" y="0" width="760" height="515" rx="14" fill="#eef3ea"/>';
  o += '<rect x="0" y="182" width="760" height="156" fill="#e3e7ea"/><path d="M0 184H760M0 336H760" stroke="#c9d0d6" stroke-width="3"/>';
  o += baum(30, 120, 14) + baum(730, 120, 14) + baum(30, 440, 14) + baum(730, 440, 14);
  Object.keys(SPOT).forEach(function (k) {
    var s = SPOT[k];
    if (s.row !== 'M') { var ry = s.row === 'T' ? s.y : s.y; o += '<path d="M' + (s.x - 8) + ' ' + ry + 'L' + (s.x + s.b / 2) + ' ' + (ry - 26) + 'L' + (s.x + s.b + 8) + ' ' + ry + 'Z" fill="#e8b4a0" stroke="#5f6963" stroke-width="2.5" pointer-events="none"/>'; }
    o += raumSvg(s);
  });
  return o + '</svg>';
}
function tierLabel(svg, k, tier) {
  var s = SPOT[k], g = svg.querySelector('[data-s="' + k + '"] .lab'), cx = s.x + s.b / 2, cy = s.y + s.h / 2;
  g.innerHTML = tier ? textSvg(cx, cy + 10, tier.e, 52) + textSvg(cx, cy + 44, tier.n, 22, ' fill="#1f2421"') : '';
}

// =====================================================================  Spiel
var WOERTER = [['next to', 'neben'], ['opposite / across from', 'gegenüber'], ['to the left of / to the right of', 'links von / rechts von'], ['in the middle', 'in der Mitte'],
  ['between', 'zwischen'], ['behind', 'hinter'], ['in front of', 'vor'], ['on your left / on your right', 'links / rechts (von dir)'], ['turn left / turn right', 'links / rechts abbiegen'],
  ['at the end of', 'am Ende von'], ['corridor', 'Gang'], ['first, second, third, fourth, fifth, last', 'erste, zweite, dritte, vierte, fünfte, letzte'],
  ['entrance', 'Eingang'], ['building', 'Gebäude'], ['round / small / long', 'rund / klein / lang'], ['changing rooms', 'Umkleide'],
  ['children’s bathrooms', 'WC für Kinder']];
function huelle(api, svgText, woerter) {
  var w = document.createElement('div'); w.className = 'sh';
  w.innerHTML = '<div class="links"><div class="plan">' + svgText + '</div></div><div class="rechts"><div class="karte"></div><div class="opts"></div>' +
    '<div class="leiste"><button class="knopf weiss" data-x="hilfe">📖 Wörter</button></div><div class="hilfe">' +
    woerter.map(function (x) { return '<div><i>' + h(x[0]) + '</i> = ' + h(x[1]) + '</div>'; }).join('') + '</div></div>';
  api.stage.appendChild(w);
  var U = { plan: w.querySelector('.plan'), karte: w.querySelector('.karte'), opts: w.querySelector('.opts') };
  U.svg = U.plan.querySelector('svg');
  var hilfe = w.querySelector('.hilfe'); w.querySelector('[data-x="hilfe"]').onclick = function () { hilfe.classList.toggle('auf'); };
  U.raum = function (id) { return U.svg.querySelector('[data-s="' + id + '"]'); };
  // nächste Aufgabe erst, wenn fertig vorgelesen ist
  U.weiter = function (fn, ms) { var t0 = Date.now(); api.later(function warte() { if (SPRICHT && Date.now() - t0 < ms + 8000) return api.later(warte, 200); fn(); }, ms); };
  return U;
}
function lob() { return '<span class="em">' + pick(['🎉', '✨', '🌟', '👍'], 1)[0] + '</span> ' + pick(['Richtig!', 'Genau!', 'Super!', 'Toll gelesen!'], 1)[0]; }

function spielPraep(api) {
  var U = huelle(api, praepSvg(), WOERTER.slice(0, 5)), k = 0, lock = false, tippe = null, leer = {};
  Object.keys(SPOT).forEach(function (x) { U.raum(x).addEventListener('click', function () { if (tippe && !lock && leer[x]) tippe(x); }); });
  function szene(belegt) {
    Object.keys(SPOT).forEach(function (x) { var r = U.raum(x); r.classList.remove('ziel', 'anker', 'ok', 'no', 'zeig'); leer[x] = !belegt[x]; r.classList.toggle('leer', !belegt[x]); tierLabel(U.svg, x, belegt[x]); });
  }
  function ende(ok, ms) { lock = true; if (api.answer(ok)) U.weiter(function () { k++; lock = false; aufgabe(); }, ms); }
  function wortAufgabe() {
    var tiere = pick(TIERE, 7), belegt = {}; Object.keys(SPOT).forEach(function (x, i) { belegt[x] = tiere[i]; }); szene(belegt);
    var typ = pick(PWORT.concat(['in the middle', 'between', 'next to', 'opposite']), 1)[0], X, Y = [], wahr = {}, satz;
    if (typ === 'in the middle') { X = 'M'; wahr[typ] = 1; }
    else if (typ === 'between') { var row = pick(['T', 'B'], 1)[0]; X = row + '1'; Y = [row + '0', row + '2']; wahr[typ] = 1; wahr['next to'] = 1; }
    else {
      var paare = []; Object.keys(SPOT).forEach(function (a) { Object.keys(SPOT).forEach(function (b) { if (pw(a, b)[typ]) paare.push([a, b]); }); });
      var p = pick(paare, 1)[0]; X = p[0]; Y = [p[1]]; wahr = pw(X, Y[0]);
    }
    U.raum(X).classList.add('ziel'); Y.forEach(function (y) { U.raum(y).classList.add('anker'); });
    function fuell(w) {
      return 'The ' + belegt[X].n + ' is ' + w + (Y.length === 2 ? ' the ' + belegt[Y[0]].n + ' and the ' + belegt[Y[1]].n : Y.length ? ' the ' + belegt[Y[0]].n : '') + '.';
    }
    U.karte.innerHTML = '<div class="zeile"><span class="tx">' + h(fuell('\u0003')).replace('\u0003', '<span class="luecke">?</span>') + '</span></div>';
    api.msg('<span class="em">🔎</span> Welches Wort passt? Schau die gelbe und die blaue Stelle an.');
    var falsch = shuffle((Y.length === 2 ? ['opposite', 'to the left of', 'to the right of', 'across from'] : PWORT.concat(Y.length ? [] : [])).filter(function (w) { return !wahr[w]; })).slice(0, 3);
    if (typ === 'in the middle') falsch = pick(PWORT, 3);
    U.opts.innerHTML = '';
    shuffle([typ].concat(falsch)).forEach(function (w) {
      var b = document.createElement('button'); b.textContent = w;
      b.onclick = function () {
        if (lock) return; var ok = w === typ; lock = true;
        b.classList.add(ok ? 'ok' : 'no');
        if (!ok) Array.prototype.forEach.call(U.opts.children, function (c) { if (c.textContent === typ) c.classList.add('hint'); });
        var ganz = fuell(typ); U.karte.querySelector('.tx').innerHTML = h(ganz).replace(h(typ), '<b>' + h(typ) + '</b>');
        api.msg(ok ? lob() + ' <small>' + h(PHINT[typ]) + '</small>' : '<span class="em">💡</span> Richtig ist <b>' + h(typ) + '</b>. <small>(' + h(PHINT[typ]) + ')</small>');
        sag(ganz); ende(ok, ok ? 900 : 2400);
      };
      U.opts.appendChild(b);
    });
  }
  function setzAufgabe() {
    for (var versuch = 0; versuch < 60; versuch++) {
      var tiere = pick(TIERE, 5), plaetze = shuffle(Object.keys(SPOT)), belegt = {};
      plaetze.slice(0, 4).forEach(function (x, i) { belegt[x] = tiere[i]; });
      var frei = plaetze.slice(4), neu = tiere[4], opt = [];
      frei.forEach(function (e) {
        if (e === 'M') opt.push({ ziel: e, w: 'in the middle', test: function (x) { return x === 'M'; } });
        Object.keys(belegt).forEach(function (a) {
          Object.keys(pw(e, a)).forEach(function (w) { opt.push({ ziel: e, w: w, a: a, test: function (x) { return !!pw(x, a)[w]; } }); });
        });
        var S = SPOT[e];
        if (S.row !== 'M' && S.c === 1 && belegt[S.row + '0'] && belegt[S.row + '2']) opt.push({ ziel: e, w: 'between', a: S.row + '0', b: S.row + '2', test: function (x) { return x === e; } });
      });
      opt = opt.filter(function (o) { return frei.filter(o.test).length === 1; });
      if (!opt.length) continue;
      var arten = []; opt.forEach(function (o) { if (arten.indexOf(o.w) < 0) arten.push(o.w); });
      var art = pick(arten, 1)[0], o = pick(opt.filter(function (x) { return x.w === art; }), 1)[0];
      szene(belegt);
      var teil = o.w + (o.b ? ' the ' + belegt[o.a].n + ' and the ' + belegt[o.b].n : o.a ? ' the ' + belegt[o.a].n : '');
      var satz = pick(['The ' + neu.n + ' is ' + teil + '.', 'Put the ' + neu.n + ' ' + teil + '.', 'Where is the ' + neu.n + '? It is ' + teil + '.'], 1)[0];
      U.karte.innerHTML = '<div class="zeile"><span class="tx"><span class="tier">' + neu.e + '</span>' + h(satz).replace(h(o.w), '<b>' + h(o.w) + '</b>') + '</span><button class="knopf" data-x="sag">🔊</button></div>';
      U.karte.querySelector('[data-x="sag"]').onclick = function () { sag(satz); };
      U.opts.innerHTML = '';
      api.msg('<span class="em">👆</span> Wo sitzt das Tier? Tippe auf den richtigen freien Platz.');
      U.plan.classList.add('tippen');
      tippe = function (x) {
        tippe = null; U.plan.classList.remove('tippen');
        var ok = x === o.ziel;
        if (!ok) { U.raum(x).classList.add('no'); }
        U.raum(o.ziel).classList.remove('leer'); U.raum(o.ziel).classList.add(ok ? 'ok' : 'zeig'); tierLabel(U.svg, o.ziel, neu);
        api.msg(ok ? lob() + ' <small>' + h(PHINT[o.w]) + '</small>' : '<span class="em">💡</span> Es gehört hierhin. <small>(' + h(PHINT[o.w]) + ')</small>');
        ende(ok, ok ? 1000 : 2600);
      };
      return;
    }
  }
  function aufgabe() { if (k % 2 === 0) wortAufgabe(); else setzAufgabe(); }
  aufgabe();
}

G.play = function (lv, api) {
  var t = lv.t;
  if (t === 'praep') return spielPraep(api);
  var P = t === 'wort' || t === 'text' ? greenPark() : neueSchule(), R = P.R, bekannt = {}, k = 0, lock = false, tippe = null;
  var reihe = t === 'text' ? TEXT.map(function (x) { return x[0]; }) : shuffle(P.slots.slice());
  var U = huelle(api, P.svg, WOERTER), plan = U.plan, karte = U.karte, opts = U.opts, svg = U.svg, raum = U.raum;
  function lab(x) { return !!(x.fest || bekannt[x.id]); }
  function klassen() { P.slots.forEach(function (x) { raum(x).classList.remove('ziel', 'no', 'zeig'); }); }
  function alleBeschriften() {
    P.slots.forEach(function (x) {
      var art = t === 'satz' ? 'voll' : bekannt[x] ? 'voll' : t === 'wort' ? 'bild' : 'leer';
      beschrifte(svg, R[x], art);
      raum(x).classList.toggle('ok', !!bekannt[x] && t !== 'satz');
    });
  }
  P.slots.forEach(function (x) { raum(x).addEventListener('click', function () { if (tippe && !lock) tippe(x); }); });
  function fertig(ok, ziel) {
    lock = true; bekannt[ziel] = true; alleBeschriften();
    if (api.answer(ok)) U.weiter(function () { k++; lock = false; aufgabe(); }, ok ? 1100 : 2600);
    else { tippe = null; plan.classList.remove('tippen'); }
  }
  function findenAuf(ziel, satz, hilfeTxt, modus) {
    tippe = function (x) {
      klassen(); plan.classList.remove('tippen');
      var ok = x === ziel, nm = R[ziel].name;
      if (!ok) { raum(x).classList.add('no'); raum(ziel).classList.add('zeig'); }
      api.msg(ok ? lob() + ' <small>' + h(nm.n) + ' = ' + h(nm.de) + '</small>' :
        '<span class="em">💡</span> Das ist hier: <b>' + h(nm.n) + '</b>' + (hilfeTxt ? ' <small>(' + h(hilfeTxt) + ')</small>' : ''));
      if (modus === 'hoeren') { var tx = karte.querySelector('.tx'); tx.innerHTML = satzHtml(satz); tx.classList.remove('verdeckt'); }
      if (modus === 'wort') sag(nm.n);
      tippe = null; fertig(ok, ziel);
    };
    plan.classList.add('tippen');
  }
  // Für Stufe 4 und 5: einen noch nicht gefundenen Raum wählen, zu dem es einen eindeutigen Satz gibt
  function naechstes() {
    var offen = P.slots.filter(function (id) { return !bekannt[id]; }), C = offen.map(function (id) { return R[id]; }), moegl = [];
    offen.forEach(function (id) {
      var A = aussagen(P, R[id], lab).filter(function (d) { return C.filter(d.test).length === 1; });
      if (A.length) moegl.push([id, A]);
    });
    return pick(moegl, 1)[0];
  }
  function aufgabe() {
    klassen(); opts.innerHTML = ''; opts.className = 'opts';
    var ziel, r, satz, hilfeTxt;
    if (t === 'wort') {
      ziel = reihe[k]; r = R[ziel];
      // abwechselnd: Raum leuchtet → Wort wählen, oder Wort → Raum antippen
      if (k % 2 === 0) {
        raum(ziel).classList.add('ziel');
        karte.innerHTML = '<div class="zeile"><span class="tx">What’s this room in English?</span></div>';
        api.msg('<span class="em">🔎</span> Wie heisst der leuchtende Raum?');
        var andere = pick(P.slots.filter(function (x) { return x !== ziel; }), 3).map(function (x) { return R[x].name; });
        shuffle([r.name].concat(andere)).forEach(function (o) {
          var b = document.createElement('button'); b.textContent = o.n;
          b.onclick = function () {
            if (lock) return; var ok = o === r.name;
            b.classList.add(ok ? 'ok' : 'no');
            if (!ok) Array.prototype.forEach.call(opts.children, function (c) { if (c.textContent === r.name.n) c.classList.add('hint'); });
            api.msg(ok ? '<span class="em">🎉</span> Richtig! <small>' + h(r.name.n) + ' = ' + h(r.name.de) + '</small>' : '<span class="em">💡</span> Das ist <b>' + h(r.name.n) + '</b> = ' + h(r.name.de) + '.');
            sag(r.name.n); fertig(ok, ziel);
          };
          opts.appendChild(b);
        });
      } else {
        var frage = 'Where ' + (r.name.p ? 'are' : 'is') + ' the ' + r.name.n + '?';
        karte.innerHTML = '<div class="zeile"><span class="tx">Where ' + (r.name.p ? 'are' : 'is') + ' the <b>' + h(r.name.n) + '</b>?</span><button class="knopf" data-x="sag">🔊</button></div>';
        karte.querySelector('[data-x="sag"]').onclick = function () { sag(frage); };
        api.msg('<span class="em">👆</span> Tippe den Raum auf dem Plan an.');
        findenAuf(ziel, '', r.name.de, 'wort');
      }
      return;
    }
    if (t === 'satz') {
      // Alles beschriftet, ein Raum leuchtet: welcher von drei Sätzen stimmt?
      ziel = reihe[k]; r = R[ziel];
      P.slots.forEach(function (x) { bekannt[x] = true; }); alleBeschriften();
      raum(ziel).classList.add('ziel');
      var alle = function () { return true; }, C = P.slots.map(function (id) { return R[id]; });
      var eindeutig = function (x) { return aussagen(P, x, alle).filter(function (d) { return C.filter(d.test).length === 1; }); };
      var d = waehle(eindeutig(r)), richtig = satzAus(d, r), falsch = [];
      shuffle(P.slots.filter(function (x) { return x !== ziel && (R[x].row === 'O') === (r.row === 'O'); })).forEach(function (x) {
        if (falsch.length >= 2) return;
        var A = eindeutig(R[x]).filter(function (e) { return !e.test(r) && e.a !== r && e.b !== r; });
        var gleich = A.filter(function (e) { return e.typ === d.typ; });
        if (!A.length) return;
        var s = satzAus(gleich.length && Math.random() < .6 ? pick(gleich, 1)[0] : pick(A, 1)[0], r);
        if (s !== richtig && falsch.indexOf(s) < 0) falsch.push(s);
      });
      karte.innerHTML = '<div class="zeile"><span class="tx">Look at the yellow room. Which sentence is right?</span></div>';
      api.msg('<span class="em">🔎</span> Welcher Satz stimmt für den leuchtenden Raum?');
      opts.className = 'opts eins';
      shuffle([richtig].concat(falsch)).forEach(function (s) {
        var b = document.createElement('button'); b.innerHTML = satzHtml(s);
        b.onclick = function () {
          if (lock) return; var ok = s === richtig; lock = true;
          b.classList.add(ok ? 'ok' : 'no');
          if (!ok) Array.prototype.forEach.call(opts.children, function (c) { if (c.innerHTML === satzHtml(richtig)) c.classList.add('hint'); });
          api.msg(ok ? '<span class="em">🎉</span> Genau gelesen!' : '<span class="em">💡</span> Der gelbe Satz stimmt. <small>(' + h(hinweis(d)) + ')</small>');
          sag(satzTxt(richtig));
          if (api.answer(ok)) U.weiter(function () { k++; lock = false; aufgabe(); }, ok ? 1200 : 3200);
        };
        opts.appendChild(b);
      });
      return;
    }
    if (t === 'text') {
      ziel = reihe[k]; r = R[ziel];
      satz = TEXT[k][1].replace('{n}', '\u0001' + r.name.n + '\u0002');
      var vor = k > 0 && (k === 7 || k >= 10) ? '<span class="vor">' + h(TEXT[k - 1][1].replace('{n}', R[TEXT[k - 1][0]].name.n)) + '</span>' : '';
      karte.innerHTML = vor + '<div class="zeile"><span class="tx">' + satzHtml(satz) + '</span><button class="knopf" data-x="sag">🔊</button></div>';
      api.msg('<span class="em">📖</span> Lies den Satz. Wo ist der Raum? Tippe ihn an.');
    } else {
      var w = naechstes(); ziel = w[0]; r = R[ziel];
      var d2 = waehle(w[1]); satz = satzAus(d2, r); hilfeTxt = hinweis(d2);
      if (t === 'hoeren') {
        karte.innerHTML = '<div class="zeile"><span class="tx verdeckt">🎧 Hör gut zu …</span><button class="knopf" data-x="sag">🔊 Nochmal</button><button class="knopf weiss" data-x="zeig">👀 Text</button></div>';
        karte.querySelector('[data-x="zeig"]').onclick = function () { var tx = karte.querySelector('.tx'); tx.innerHTML = satzHtml(satz); tx.classList.remove('verdeckt'); this.remove(); };
        api.msg('<span class="em">🎧</span> Hör zu und tippe den Raum an.');
        api.later(function () { sag(satzTxt(satz)); }, 450);
      } else {
        karte.innerHTML = '<div class="zeile"><span class="tx">' + satzHtml(satz) + '</span><button class="knopf" data-x="sag">🔊</button></div>';
        api.msg('<span class="em">📖</span> Lies den Satz. Wo ist der Raum? Tippe ihn an.');
      }
    }
    karte.querySelector('[data-x="sag"]').onclick = function () { sag(satzTxt(satz)); };
    findenAuf(ziel, satz, hilfeTxt, t);
  }
  alleBeschriften();
  aufgabe();
};
"""
