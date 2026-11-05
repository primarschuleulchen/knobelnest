# Knobelspiel «Im Schulhaus» (Englisch, Leseverstehen: Räume im Schulhaus und Ortsangaben).
# Nach der Leseübung «Unit 1» der Lehrerin (Text über die Green Park School, Räume auf dem Plan nummerieren).
# Wird von bauen.py aufgerufen: schulhaus.alle(spiel)
#
# Stufen (je 12 Aufgaben, eine pro Raum):
#   1 Die Räume        Wörter lernen: Raum mit Bild → richtiges Wort, oder Wort → Raum antippen
#   2 Green Park School Der Text vom Arbeitsblatt, Satz für Satz: den Raum auf dem Plan antippen (Nummer erscheint)
#   3 Lesen und finden  Neues Schulhaus (Räume zufällig verteilt), neue Sätze: Raum antippen
#   4 Hören und finden  wie 3, der Satz wird nur vorgelesen (Text kann man aufdecken)
#   5 Welcher Satz?     Ein Raum leuchtet: Welcher von drei Sätzen stimmt?
#
# Plan (SVG 760 × 515): Hauptgebäude mit langem Gang (links Haupteingang, unten Seiteneingang), draussen drei Gebäude.
# Die Lage der Räume entspricht dem Plan auf dem Arbeitsblatt (gleiche Nachbarn, gleiche Reihenfolge im Gang).


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
          intro='Lies, wo die Räume sind, und finde sie auf dem Plan: <b>next to</b>, <b>opposite</b>, <b>behind</b>, <b>at the end of the corridor</b> …',
          levels=[dict(name='Die Räume', info='Wie heissen die Räume auf Englisch?', t='wort'),
                  dict(name='Green Park School', info='Der Text vom Arbeitsblatt', t='text'),
                  dict(name='Lesen und finden', info='Neues Schulhaus, neue Sätze', t='lesen'),
                  dict(name='Hören und finden', info='Nur anhören und finden', t='hoeren'),
                  dict(name='Welcher Satz stimmt?', info='Genau lesen: einer von drei', t='satz')],
          css=CSS, js=JS)


CSS = r"""
.ring{width:150px;height:150px;background:none;border:0;padding:0;box-shadow:0 8px 18px rgba(63,120,168,.18);border-radius:50%}.ring .logo{width:100%;height:100%;display:block}
@media (max-height:640px){.ring{width:100px;height:100px}}
.msg{min-height:0;margin:0 0 8px;font-size:21px;line-height:1.3}
.top{margin-bottom:4px}
.stage{max-width:1240px}.sh{display:flex;flex-direction:column;align-items:center;gap:10px;width:100%;max-width:1240px}
.karte{background:#fff;border:2px solid var(--line);border-radius:20px;padding:10px 16px;box-shadow:var(--sch-k);font-size:23px;line-height:1.4;width:100%;max-width:820px;position:relative}
.karte .vor{display:block;color:var(--soft);font-size:17px;margin-bottom:2px}
.karte b{font-weight:400;color:var(--sky-d);background:var(--sun);border-radius:6px;padding:0 4px}
.karte .zeile{display:flex;align-items:center;gap:10px;flex-wrap:wrap}
.karte .zeile .tx{flex:1;min-width:200px}
.knopf{background:var(--sun);border:2px solid var(--gold-d);border-radius:14px;min-height:44px;padding:2px 12px;font-size:19px;box-shadow:var(--sch-k);white-space:nowrap}
.knopf.weiss{background:#fff;border-color:var(--line2)}
.verdeckt{color:var(--soft);font-size:19px}
.plan{width:min(100%,calc((100vh - 290px) * 760 / 515),860px);min-width:min(100%,420px);display:block;touch-action:manipulation}
.plan svg{width:100%;height:auto;display:block}
.plan .raum{cursor:pointer}
.plan .raum rect,.plan .raum ellipse{transition:fill .25s}
.plan.tippen .raum:hover rect.r,.plan.tippen .raum:hover ellipse.r{fill:#fff3cf}
.plan .raum.ziel rect.r,.plan .raum.ziel ellipse.r{fill:#ffe39a}
.plan .raum.ok rect.r,.plan .raum.ok ellipse.r{fill:#e2f1d9}
.plan .raum.no rect.r,.plan .raum.no ellipse.r{fill:#f7d2cd}
.plan .raum.zeig rect.r,.plan .raum.zeig ellipse.r{fill:#ffe39a;animation:blink .5s 3}
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
// ---------- Räume
// Plätze auf dem Plan: x, y, b, h (oder Ellipse), drinnen/draussen
var PL = {
  s12: { x: 20, y: 210, b: 130, h: 160 },
  s11: { x: 195, y: 10, b: 135, h: 200 },
  s10: { x: 225, y: 250, b: 75, h: 120 },
  s9:  { x: 300, y: 250, b: 90, h: 120 },
  s8:  { x: 370, y: 10, b: 85, h: 200 },
  s7:  { x: 665, y: 10, b: 85, h: 200 },
  s6:  { x: 450, y: 250, b: 108, h: 60 },
  s5:  { x: 450, y: 310, b: 108, h: 60 },
  s4:  { x: 665, y: 250, b: 85, h: 120 },
  s3:  { x: 10, y: 400, b: 170, h: 104, rund: true },
  s2:  { x: 215, y: 415, b: 100, h: 75 },
  s1:  { x: 345, y: 420, b: 400, h: 65 }
};
var DRIN = ['s12', 's11', 's10', 's9', 's8', 's7', 's6', 's5', 's4'], DRAUSSEN = ['s3', 's2', 's1'];
// Die Räume vom Arbeitsblatt (Nummer = Nummer auf dem Arbeitsblatt)
var BLATT = {
  s1: { n: 'swimming pool', e: '🏊', de: 'Schwimmbad', nr: 1 },
  s2: { n: 'gym', e: '🏀', de: 'Turnhalle', nr: 2 },
  s3: { n: 'assembly hall', e: '🎭', de: 'Aula', nr: 3 },
  s4: { n: 'kitchen', e: '🍳', de: 'Küche', nr: 4 },
  s5: { n: 'science room', e: '🔬', de: 'Naturkunde-Zimmer', nr: 5 },
  s6: { n: 'headmaster’s office', e: '👔', de: 'Büro der Schulleitung', nr: 6 },
  s7: { n: 'history classrooms', e: '🏛️', de: 'Geschichtszimmer', nr: 7, p: 1 },
  s8: { n: 'canteen', e: '🍽️', de: 'Mensa', nr: 8 },
  s9: { n: 'teacher’s bathroom', e: '🚽', de: 'WC für Lehrpersonen', nr: 9 },
  s10: { n: 'teacher’s room', e: '☕', de: 'Lehrerzimmer', nr: 10 },
  s11: { n: 'computer rooms', e: '💻', de: 'Computerräume', nr: 11, p: 1 },
  s12: { n: 'library', e: '📚', de: 'Bibliothek', nr: 12 }
};
// Für die neuen Schulhäuser (Stufe 3–5)
var POOL_DRIN = [
  { n: 'library', e: '📚', de: 'Bibliothek' }, { n: 'computer room', e: '💻', de: 'Computerraum' }, { n: 'teachers’ room', e: '☕', de: 'Lehrerzimmer' },
  { n: 'teachers’ bathroom', e: '🚽', de: 'WC für Lehrpersonen' }, { n: 'canteen', e: '🍽️', de: 'Mensa' }, { n: 'history classroom', e: '🏛️', de: 'Geschichtszimmer' },
  { n: 'headmaster’s office', e: '👔', de: 'Büro der Schulleitung' }, { n: 'science room', e: '🔬', de: 'Naturkunde-Zimmer' }, { n: 'kitchen', e: '🍳', de: 'Küche' },
  { n: 'art room', e: '🎨', de: 'Zeichenzimmer' }, { n: 'school office', e: '🗂️', de: 'Sekretariat' }, { n: 'English classroom', e: '💬', de: 'Englischzimmer' }
];
var POOL_DRAUSSEN = [{ n: 'assembly hall', e: '🎭', de: 'Aula' }, { n: 'gym', e: '🏀', de: 'Turnhalle' }, { n: 'swimming pool', e: '🏊', de: 'Schwimmbad' }];

// ---------- Sätze pro Platz: [Satz, Hilfe]. {n} = gesuchter Raum, {is} = is/are, {s8} usw. = ein anderer Raum (nur wenn schon bekannt)
var SAETZE = {
  s12: [['The {n} {is} next to the main entrance.', 'next to = neben'],
        ['In the corner next to the main entrance you can find the {n}.', 'corner = Ecke'],
        ['The {n} {is} the big room between the main entrance and the changing rooms.', 'between = zwischen']],
  s11: [['When you walk into the building and turn left, you can see the {n}.', 'turn left = links abbiegen'],
        ['The first room on the left of the long corridor is the {n}.', 'first = erste, on the left = links'],
        ['Opposite the {s10} you can find the {n}.', 'opposite = gegenüber']],
  s10: [['The second room on the right is the {n}.', 'second = zweite, on the right = rechts'],
        ['On the right, next to the changing rooms, there is the {n}.', 'next to = neben'],
        ['The {n} {is} the small room between the changing rooms and the {s9}.', 'between = zwischen']],
  s9:  [['When you walk down the corridor, the third room on the right is the {n}.', 'third = dritte'],
        ['Between the {s10} and the music room you can find the {n}.', 'between = zwischen']],
  s8:  [['Opposite the music room you find the {n}.', 'opposite = gegenüber'],
        ['The second room on the left of the long corridor is the {n}.', 'second = zweite, on the left = links'],
        ['The {n} {is} between the {s11} and the children’s bathrooms.', 'between = zwischen']],
  s7:  [['At the very end of the long corridor on the left side you can see the {n}.', 'at the end = am Ende'],
        ['The last room on the left is the {n}.', 'last = letzte'],
        ['Opposite the {s4} you can find the {n}.', 'opposite = gegenüber']],
  s6:  [['Across from the children’s bathrooms there is the {n}.', 'across from = gegenüber'],
        ['Walk into the little corridor next to the classroom. The first door on the right is the {n}.', 'first door = erste Tür'],
        ['In front of the {s5}, next to the music room, you can find the {n}.', 'in front of = vor']],
  s5:  [['Behind the {s6} and next to the music room you can find the {n}.', 'behind = hinter'],
        ['Walk into the little corridor next to the classroom. The second door on the right is the {n}.', 'second door = zweite Tür'],
        ['The {n} {is} next to the music room, but not opposite the children’s bathrooms.', 'not opposite = nicht gegenüber']],
  s4:  [['At the end of the corridor on the right side there is the {n}.', 'at the end = am Ende, on the right = rechts'],
        ['The last room on the right is the {n}.', 'last = letzte'],
        ['Opposite the {s7} you can find the {n}.', 'opposite = gegenüber']],
  s3:  [['Walk out through the side entrance. The round building is the {n}.', 'round = rund'],
        ['The {n} {is} in the round building.', 'round = rund'],
        ['The round building next to the {s2} is the {n}.', 'round = rund']],
  s2:  [['The {n} {is} in the small building.', 'small = klein'],
        ['The small building between the round building and the long building is the {n}.', 'between = zwischen'],
        ['Between the {s3} and the {s1} you can find the {n}.', 'between = zwischen']],
  s1:  [['The {n} {is} in the long building.', 'long = lang'],
        ['The long building outside is the {n}.', 'outside = draussen'],
        ['Next to the {s2}, in the long building, you can find the {n}.', 'next to = neben']]
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
var WOERTER = [['next to', 'neben'], ['opposite / across from', 'gegenüber'], ['behind', 'hinter'], ['in front of', 'vor'], ['between', 'zwischen'],
  ['on the left / on the right', 'links / rechts'], ['turn left', 'links abbiegen'], ['at the end of', 'am Ende von'], ['corridor', 'Gang'],
  ['first / second / third / last', 'erste / zweite / dritte / letzte'], ['entrance', 'Eingang'], ['building', 'Gebäude'], ['round / small / long', 'rund / klein / lang'],
  ['changing rooms', 'Garderoben'], ['children’s bathrooms', 'WC für Kinder']];

// ---------- Vorlesen (englische Stimme wie in der Vokabelkiste und im Museum)
var FEMALE = /\b(female|samantha|karen|moira|tessa|serena|kate|stephanie|martha|fiona|victoria|allison|ava|susan|zira|hazel|libby|sonia|aria|jenny|emma|amy|joanna|salli|kimberly|olivia|natasha|clara)\b/i;
var MALE = /\b(male|daniel|alex|fred|oliver|george|ryan|guy|david|mark|james|thomas|arthur|rishi|aaron|gordon|reed|rocko|eddy|grandpa)\b/i;
function stimme() {
  var vs = []; try { vs = speechSynthesis.getVoices().filter(function (v) { return v.lang && /^en/i.test(v.lang); }); } catch (e) {}
  if (!vs.length) return null;
  function sc(v) { var n = v.name.replace(/female/ig, ''); return (FEMALE.test(v.name) ? 10 : 0) - (MALE.test(n) ? 10 : 0) + (/en[-_]gb/i.test(v.lang) ? 3 : 0) + (/natural|neural|premium|enhanced|online/i.test(v.name) ? 4 : 0); }
  return vs.slice().sort(function (a, b) { return sc(b) - sc(a); })[0];
}
function kannSprechen() { return !!(window.speechSynthesis && window.SpeechSynthesisUtterance); }
var AKT_U = null;
function sag(t) {
  if (!kannSprechen()) return;
  try {
    var ss = speechSynthesis; if (ss.speaking || ss.pending) ss.cancel(); if (ss.paused) ss.resume();
    var u = new SpeechSynthesisUtterance(t), v = stimme();
    if (v) { u.voice = v; u.lang = String(v.lang).replace('_', '-'); } else u.lang = 'en-GB';
    u.rate = .82; AKT_U = u; ss.speak(u);
  } catch (e) {}
}
function still() { try { if (window.speechSynthesis) speechSynthesis.cancel(); } catch (e) {} }
try { if (window.speechSynthesis) speechSynthesis.getVoices(); } catch (e) {}

// ---------- Plan zeichnen
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
function planSvg() {
  var o = '<svg viewBox="0 0 760 515" font-family="Patrick Hand, sans-serif">';
  o += '<rect x="0" y="0" width="760" height="515" rx="14" fill="#eef3ea"/>';
  // Platz vor dem Haupteingang und Bäume
  o += '<rect x="12" y="40" width="112" height="150" rx="8" fill="#dfe5ea"/>' + schild(68, 100, 'main', 16) + schild(68, 120, 'entrance', 16) + '<path d="M118 115h26" stroke="#9aa8b4" stroke-width="3" stroke-dasharray="5 4"/><text x="134" y="111" font-size="13" text-anchor="middle" fill="#9aa8b4">▶</text>';
  o += baum(30, 22, 10) + baum(58, 22, 10) + baum(86, 22, 10);
  // Hauptgebäude (Grundfläche = Gang)
  o += '<path d="M150 10H750V370H150V370H20V210H150Z" fill="#f7f4ec" stroke="#5f6963" stroke-width="4"/>';
  // feste Räume
  var fest = '<g fill="#e7e2d6" stroke="#5f6963" stroke-width="2.5">' +
    '<rect x="455" y="10" width="110" height="170" fill="#d9ead0"/>' +
    '<rect x="455" y="180" width="55" height="30"/><rect x="510" y="180" width="55" height="30"/>' +
    '<rect x="565" y="10" width="65" height="200"/>' +
    '<rect x="150" y="250" width="75" height="120"/><rect x="390" y="250" width="60" height="120"/>' +
    '<rect x="580" y="250" width="50" height="120"/></g>';
  o += fest + baum(490, 50, 16) + baum(530, 40, 10) + baum(500, 135, 14) + baum(538, 112, 9);
  o += schild(597, 110, 'classrooms', 15, true) + schild(187, 310, 'changing rooms', 15, true) + schild(420, 310, 'music room', 15, true) + schild(605, 310, 'classroom', 15, true);
  o += '<text x="482" y="201" font-size="16" text-anchor="middle">🚹</text><text x="537" y="201" font-size="16" text-anchor="middle">🚺</text>';
  // Seiteneingang
  o += '<rect x="632" y="366" width="31" height="8" fill="#fff"/>' + schild(647, 388, 'side entrance', 14);
  o += tuer(150, 106, true) + tuer(160, 250) + tuer(470, 210) + tuer(596, 250) + tuer(410, 250) + tuer(588, 210) + tuer(640, 210);
  // Räume zum Finden
  Object.keys(PL).forEach(function (k) {
    var p = PL[k], f = 'fill="#fff" stroke="#5f6963" stroke-width="2.5"';
    o += '<g class="raum" data-s="' + k + '">';
    o += p.rund ? '<ellipse class="r" cx="' + (p.x + p.b / 2) + '" cy="' + (p.y + p.h / 2) + '" rx="' + p.b / 2 + '" ry="' + p.h / 2 + '" ' + f + '/>' : '<rect class="r" x="' + p.x + '" y="' + p.y + '" width="' + p.b + '" height="' + p.h + '" ' + f + '/>';
    if (k === 's11') o += '<path d="M195 110h135" stroke="#5f6963" stroke-width="2"/>';
    o += '<g class="lab" pointer-events="none"></g></g>';
  });
  return o + '</svg>';
}
// Beschriftung eines Raums: Nummer (Stufe 2), Bild, Name
function beschrifte(svg, k, r, art) {
  var p = PL[k], g = svg.querySelector('[data-s="' + k + '"] .lab'), cx = p.x + p.b / 2, o = '';
  if (!r || art === 'leer') { g.innerHTML = ''; return; }
  var z = art === 'bild' ? [] : zeilen(r.n, p.h < 70 && p.b < 200 ? p.b - 22 : p.b), fs = p.b < 80 ? 15 : 17, top = p.y + p.h / 2;
  var hoch = 30 + z.length * (fs + 1);
  if (p.h < 70) { // flacher Raum: Bild links, Name rechts
    var lang = p.b > 200;
    o += textSvg(lang ? cx - 70 : p.x + 17, p.y + p.h / 2 + 9, r.e, lang ? 30 : 22);
    z.forEach(function (t, i) { o += textSvg(lang ? cx + 20 : cx + 13, p.y + p.h / 2 + 5 - (z.length - 1) * 7.5 + i * 15, t, lang ? 18 : 13.5, ' fill="#1f2421"'); });
  } else {
    var y0 = top - hoch / 2 + 26;
    o += textSvg(cx, y0, r.e, 28);
    z.forEach(function (t, i) { o += textSvg(cx, y0 + 6 + (i + 1) * (fs + 1), t, fs, ' fill="#1f2421"'); });
  }
  if (art === 'nr' && r.nr) o += '<circle cx="' + (p.x + p.b - 14) + '" cy="' + (p.y + 14) + '" r="11" fill="#d6ad45"/>' + textSvg(p.x + p.b - 14, p.y + 19, String(r.nr), 14, ' fill="#fff"');
  g.innerHTML = o;
}

// ---------- Hilfen
function satzMit(t, r, haus) {
  return t.replace('{is}', r.p ? 'are' : 'is').replace(/\{(s\d+)\}/g, function (m, k) { return haus[k].n; }).replace('{n}', '\u0001' + r.n + '\u0002');
}
function satzHtml(s) { return h(s).replace('\u0001', '<b>').replace('\u0002', '</b>'); }
function satzTxt(s) { return s.replace('\u0001', '').replace('\u0002', ''); }
function verdecke(s) { return h(s.replace(/\u0001[^\u0002]*\u0002/, '…')); }
function braucht(t) { var m = t.match(/\{s\d+\}/g) || []; return m.map(function (x) { return x.slice(1, -1); }); }
function neuesHaus() {
  var d = pick(POOL_DRIN, 9), a = shuffle(POOL_DRAUSSEN), haus = {};
  DRIN.forEach(function (k, i) { haus[k] = d[i]; }); DRAUSSEN.forEach(function (k, i) { haus[k] = a[i]; });
  return haus;
}
function blattHaus() { var h2 = {}; Object.keys(BLATT).forEach(function (k) { h2[k] = BLATT[k]; }); return h2; }
// Satz für Platz k, nur mit bekannten Räumen; [Satz, Hilfe]
function satzFuer(k, haus, bekannt, alt) {
  var ok = SAETZE[k].filter(function (s) { return braucht(s[0]).every(function (x) { return bekannt[x]; }) && s[0] !== alt; });
  var mit = ok.filter(function (s) { return braucht(s[0]).length; });
  var s = mit.length && Math.random() < .45 ? pick(mit, 1)[0] : pick(ok, 1)[0];
  return [satzMit(s[0], haus[k], haus), s[1], s[0]];
}

G.play = function (lv, api) {
  var t = lv.t, haus = t === 'wort' || t === 'text' ? blattHaus() : neuesHaus(), bekannt = {}, k = 0, lock = false;
  var orte = t === 'text' ? TEXT.map(function (x) { return x[0]; }) : shuffle(Object.keys(PL));
  var w = document.createElement('div'); w.className = 'sh';
  w.innerHTML = '<div class="links"><div class="plan">' + planSvg() + '</div></div><div class="rechts"><div class="karte"></div><div class="opts"></div>' +
    '<div class="leiste"><button class="knopf weiss" data-x="hilfe">📖 Wörter</button></div><div class="hilfe">' +
    WOERTER.map(function (x) { return '<div><i>' + h(x[0]) + '</i> = ' + h(x[1]) + '</div>'; }).join('') + '</div></div>';
  api.stage.appendChild(w);
  var plan = w.querySelector('.plan'), svg = plan.querySelector('svg'), karte = w.querySelector('.karte'), opts = w.querySelector('.opts'), hilfe = w.querySelector('.hilfe');
  w.querySelector('[data-x="hilfe"]').onclick = function () { hilfe.classList.toggle('auf'); };
  function raum(k) { return svg.querySelector('[data-s="' + k + '"]'); }
  function klassen() { Object.keys(PL).forEach(function (x) { raum(x).classList.remove('ziel', 'no', 'zeig'); }); }
  function alleBeschriften() {
    Object.keys(PL).forEach(function (x) {
      var art = t === 'wort' ? 'voll' : t === 'satz' ? 'voll' : bekannt[x] ? (t === 'text' ? 'nr' : 'voll') : 'leer';
      if (t === 'wort' && !bekannt[x]) art = 'bild';
      beschrifte(svg, x, haus[x], art);
      raum(x).classList.toggle('ok', !!bekannt[x] && t !== 'satz');
    });
  }
  // Antippen auf dem Plan
  var tippe = null;
  Object.keys(PL).forEach(function (x) { raum(x).addEventListener('click', function () { if (tippe && !lock) tippe(x); }); });
  function fertig(ok, ziel, warum) {
    lock = true; bekannt[ziel] = true; alleBeschriften();
    var weiter = api.answer(ok);
    if (weiter) api.later(function () { k++; lock = false; aufgabe(); }, ok ? 1100 : 2600);
    else { tippe = null; plan.classList.remove('tippen'); }
  }
  function findenAuf(ziel, satz, hilfeTxt, modus) {
    tippe = function (x) {
      klassen(); plan.classList.remove('tippen');
      var ok = x === ziel;
      if (!ok) { raum(x).classList.add('no'); raum(ziel).classList.add('zeig'); }
      var r = haus[ziel];
      api.msg(ok ? '<span class="em">' + pick(['🎉', '✨', '🌟', '👍'], 1)[0] + '</span> ' + pick(['Richtig!', 'Genau!', 'Super!', 'Toll gelesen!'], 1)[0] + ' <small>' + h(r.n) + ' = ' + h(r.de) + '</small>' :
        '<span class="em">💡</span> Das ist hier: <b>' + h(r.n) + '</b>' + (hilfeTxt ? ' <small>(' + h(hilfeTxt) + ')</small>' : ''));
      if (modus === 'hoeren') karte.querySelector('.tx').innerHTML = satzHtml(satz);
      tippe = null; fertig(ok, ziel);
    };
    plan.classList.add('tippen');
  }
  function aufgabe() {
    klassen(); opts.innerHTML = ''; opts.className = 'opts'; still();
    var ziel = orte[k], r = haus[ziel];
    if (t === 'wort') {
      // abwechselnd: Raum leuchtet → Wort wählen, oder Wort → Raum antippen
      if (k % 2 === 0) {
        raum(ziel).classList.add('ziel');
        karte.innerHTML = '<div class="zeile"><span class="tx">What’s this room in English?</span></div>';
        api.msg('<span class="em">🔎</span> Wie heisst der leuchtende Raum?');
        var andere = pick(Object.keys(PL).filter(function (x) { return x !== ziel; }), 3).map(function (x) { return haus[x]; });
        shuffle([r].concat(andere)).forEach(function (o) {
          var b = document.createElement('button'); b.textContent = o.n;
          b.onclick = function () {
            if (lock) return; var ok = o === r;
            b.classList.add(ok ? 'ok' : 'no');
            if (!ok) Array.prototype.forEach.call(opts.children, function (c) { if (c.textContent === r.n) c.classList.add('hint'); });
            api.msg(ok ? '<span class="em">🎉</span> Richtig! <small>' + h(r.n) + ' = ' + h(r.de) + '</small>' : '<span class="em">💡</span> Das ist <b>' + h(r.n) + '</b> = ' + h(r.de) + '.');
            sag(r.n); fertig(ok, ziel);
          };
          opts.appendChild(b);
        });
      } else {
        karte.innerHTML = '<div class="zeile"><span class="tx">Where is the <b>' + h(r.n) + '</b>?</span><button class="knopf" data-x="sag">🔊</button></div>';
        karte.querySelector('[data-x="sag"]').onclick = function () { sag('Where is the ' + r.n + '?'); };
        api.msg('<span class="em">👆</span> Tippe den Raum auf dem Plan an.');
        findenAuf(ziel, '', r.de, 'wort');
      }
      return;
    }
    if (t === 'satz') {
      // Alle Räume sind beschriftet, einer leuchtet: welcher Satz passt?
      bekannt = {}; Object.keys(PL).forEach(function (x) { bekannt[x] = true; }); alleBeschriften();
      raum(ziel).classList.add('ziel');
      var richtig = satzFuer(ziel, haus, bekannt), falsch = [];
      // falsche Sätze: passen zu anderen Plätzen, aber mit dem Namen des leuchtenden Raums
      var plaetze = shuffle(Object.keys(PL).filter(function (x) { return x !== ziel && (DRIN.indexOf(x) >= 0) === (DRIN.indexOf(ziel) >= 0); }));
      plaetze.forEach(function (x) {
        if (falsch.length >= 2) return;
        var s = pick(SAETZE[x], 1)[0], txt = satzMit(s[0], r, haus);
        if (braucht(s[0]).indexOf(ziel) >= 0) return;
        falsch.push(txt);
      });
      karte.innerHTML = '<div class="zeile"><span class="tx">Look at the yellow room. Which sentence is right?</span></div>';
      api.msg('<span class="em">🔎</span> Welcher Satz stimmt für den leuchtenden Raum?');
      opts.className = 'opts eins';
      shuffle([richtig[0]].concat(falsch)).forEach(function (s) {
        var b = document.createElement('button'); b.innerHTML = satzHtml(s);
        b.onclick = function () {
          if (lock) return; var ok = s === richtig[0];
          b.classList.add(ok ? 'ok' : 'no');
          if (!ok) Array.prototype.forEach.call(opts.children, function (c) { if (c.innerHTML === satzHtml(richtig[0])) c.classList.add('hint'); });
          api.msg(ok ? '<span class="em">🎉</span> Genau gelesen!' : '<span class="em">💡</span> Der gelbe Satz stimmt. <small>(' + h(richtig[1]) + ')</small>');
          lock = true; var weiter = api.answer(ok);
          if (weiter) api.later(function () { k++; lock = false; aufgabe(); }, ok ? 1200 : 3200);
        };
        opts.appendChild(b);
      });
      return;
    }
    var satz, hilfeTxt;
    if (t === 'text') {
      satz = satzMit(TEXT[k][1], r, haus);
      var vor = k > 0 && (k === 7 || k >= 10) ? '<span class="vor">' + h(satzTxt(satzMit(TEXT[k - 1][1], haus[TEXT[k - 1][0]], haus))) + '</span>' : '';
      karte.innerHTML = vor + '<div class="zeile"><span class="tx">' + satzHtml(satz) + '</span><button class="knopf" data-x="sag">🔊</button></div>';
      api.msg('<span class="em">📖</span> Lies den Satz. Wo ist der Raum? Tippe ihn an.');
    } else {
      var s = satzFuer(ziel, haus, bekannt); satz = s[0]; hilfeTxt = s[1];
      if (t === 'hoeren') {
        karte.innerHTML = '<div class="zeile"><span class="tx verdeckt">🎧 Hör gut zu …</span><button class="knopf" data-x="sag">🔊 Nochmal</button><button class="knopf weiss" data-x="zeig">👀 Text</button></div>';
        karte.querySelector('[data-x="zeig"]').onclick = function () { karte.querySelector('.tx').innerHTML = satzHtml(satz); karte.querySelector('.tx').classList.remove('verdeckt'); this.remove(); };
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
