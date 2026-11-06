
'use strict';
var EULE = '../bilder/eule.webp';
var app = document.getElementById('app');
var R = function (a, b) { return a + Math.floor(Math.random() * (b - a + 1)); };
var pick = function (a) { return a[Math.floor(Math.random() * a.length)]; };
function mischen(a) { a = a.slice(); for (var i = a.length - 1; i > 0; i--) { var j = Math.floor(Math.random() * (i + 1)); var t = a[i]; a[i] = a[j]; a[j] = t; } return a; }
function fmt(n) { var s = String(Math.abs(n)); if (s.length >= 5) s = s.replace(/\B(?=(\d{3})+(?!\d))/g, ' '); return (n < 0 ? '−' : '') + s; }
function zahl(v) { v = String(v).replace(/[\s'’.  ]/g, ''); return /^\d+$/.test(v) ? Number(v) : null; }
var LOB = ['Richtig!', 'Super!', 'Genau!', 'Toll gerechnet!', 'Stimmt!', 'Prima!'];

/* Wo läuft die Seite?  artifact = alles auf einer Seite · eulenkiste = ohne Sterne · klassenkiste = ein Bereich als Spiel im Portal (Sterne über das Portal) */
var RK = window.RK_MODUS || { ziel: 'artifact' };
var OHNE_STERNE = RK.ziel === 'eulenkiste';
var PORTAL = RK.ziel === 'klassenkiste' && window.parent !== window;
function send(m) { if (!PORTAL) return; m.knobelnest = 1; try { parent.postMessage(m, '*'); } catch (e) {} }
var ST = {};
if (!PORTAL) try { ST = JSON.parse(localStorage.getItem('rechenkiste55') || '{}') || {}; } catch (e) { ST = {}; }
function speichern() {
  if (PORTAL) { send({ type: 'store', data: { rk: JSON.stringify(ST) } }); send({ type: 'award', award: awardDaten() }); return; }
  try { localStorage.setItem('rechenkiste55', JSON.stringify(ST)); } catch (e) {}
}
function antwort(ok) { send({ type: 'answer', ok: !!ok }); }
function sterneHTML(n, max) { var o = ''; for (var i = 0; i < (max || 3); i++) o += i < n ? '★' : '<span class="off">★</span>'; return '<span class="stars">' + o + '</span>'; }

/* ---------- Bausteine für Aufgaben ---------- */
function F(id) { return { f: id }; }
function eingabe(q, a, hint, erkl) { return { type: 'schritte', rows: [[q + ' =', F('x')]], fields: { x: { a: a } }, hint: hint, erkl: erkl, gross: true }; }

/* ---------- 1 Blitz-Rechnen (A1, B1) ---------- */
function plusMinus(a, b) {
  if (Math.random() < .5) return eingabe(fmt(a) + ' + ' + fmt(b), a + b);
  if (a === b) a += b;
  if (a < b) { var t = a; a = b; b = t; }
  return eingabe(fmt(a) + ' − ' + fmt(b), a - b);
}
function kopf1() { return Math.random() < .5 ? plusMinus(R(10, 79) * 10, R(10, 69) * 10) : plusMinus(R(12, 79) * 100, R(5, 59) * 100); }
function kopf2() {
  var w = R(1, 3);
  if (w === 1) return plusMinus(R(11, 89) * 1000, R(11, 69) * 1000);
  if (w === 2) return plusMinus(R(11, 69) * 10000, R(11, 49) * 10000);
  var b = R(11, 99) * 10000; return eingabe('1 000 000 − ' + fmt(b), 1000000 - b);
}
function nullen(k) { return Math.pow(10, k); }
function kopfMal() {
  var i = R(0, 3), j = R(1, 3); if (i + j > 5) i = 5 - j;
  var a = R(2, 9) * nullen(i), b = R(2, 9) * nullen(j);
  if (Math.random() < .5) { var t = a; a = b; b = t; }
  return eingabe(fmt(a) + ' × ' + fmt(b), a * b, 'Tipp: Rechne zuerst ohne Nullen und hänge die Nullen am Schluss an.');
}
function kopfDurch() {
  var j = R(0, 2), i = R(0, 2); if (i + j === 0) i = 1;
  var d = R(2, 9) * nullen(j), q = R(2, 9) * nullen(i);
  return eingabe(fmt(d * q) + ' : ' + fmt(d), q, 'Tipp: Streiche bei beiden Zahlen gleich viele Nullen weg.');
}

/* ---------- 2 Schritt für Schritt (A3) ---------- */
function zerlegen(op, gross) {
  var stellen = gross ? [100000, 10000, 1000, 100, 10, 1] : [10000, 1000, 100, 10, 1];
  var st = mischen(stellen.slice(0, gross ? 4 : 3)).slice(0, 1).concat(mischen(stellen).slice(0, R(1, 2)));
  st = st.filter(function (v, i) { return st.indexOf(v) === i; }).sort(function (x, y) { return y - x; });
  var teile = st.map(function (p) { return R(1, 9) * p; });
  var b = teile.reduce(function (s, v) { return s + v; }, 0);
  var a = gross ? R(100, 899) * 1000 + R(0, 9) * 100 + R(0, 99) : R(20, 89) * 1000 + R(0, 999);
  if (op === '−' && a <= b + 1000) a += b + R(1, 9) * 1000;
  var rows = [], fields = {}, wert = a, ids = [];
  teile.forEach(function (p, k) {
    wert = op === '+' ? wert + p : wert - p;
    var id = 's' + k; ids.push(id); fields[id] = { a: wert };
    rows.push(k === 0 ? [fmt(a) + ' ' + op + ' ' + fmt(p) + ' =', F(id)] : ['<span class="vor">→</span> ' + op + ' ' + fmt(p) + ' =', F(id)]);
  });
  rows[rows.length - 1].push('<span class="vor" style="font-size:.6em">← Resultat</span>');
  return { type: 'schritte', titel: fmt(a) + ' ' + op + ' ' + fmt(b), frage: 'Rechne in Teilschritten. Jede Zeile rechnet mit dem Resultat der Zeile darüber weiter.', rows: rows, fields: fields, hint: 'Schau die roten Felder nochmals an. Welche Stelle ändert sich?' };
}

/* ---------- 3 Rechen-Partner (A2, Flexibel rechnen) ---------- */
function partnerPlus() {
  var a; do { a = R(101, 899); } while (a % 100 === 0);
  var c = 100 * (Math.floor(a / 100) + R(1, 4)) - a;
  var b = R(201, 899), d = b - R(1, 9);
  var rest = mischen([{ v: b, s: '+' }, { v: c, s: '+' }, { v: d, s: '−' }]);
  return { type: 'partner', modus: 'plus', rund: 100, terme: [{ v: a, s: '+' }].concat(rest) };
}
function partnerMinus() {
  function paar() { var x = R(11, 89) * 100; if (x % 1000 === 0) x += 100; var y = 1000 * (Math.floor(x / 1000) + R(1, 9)) - x; return [x, y]; }
  var p1 = paar(), p2 = paar(), summe = p1[0] + p1[1] + p2[0] + p2[1];
  var S = summe + R(5, 40) * 1000;
  var rest = mischen([p1[0], p1[1], p2[0], p2[1]]).map(function (v) { return { v: v, s: '−' }; });
  return { type: 'partner', modus: 'plus', rund: 1000, terme: [{ v: S, s: '+' }].concat(rest) };
}
function partnerMal() {
  var n; do { n = R(13, 49); } while (n % 5 === 0 || n % 2 === 0);
  var vorl = pick([[5, n, 4, 5], [25, n, 4], [2, n, 5, 10], [50, n, 2], [125, n, 8], [4, n, 25], [5, n, 2, 7], [20, n, 5]]);
  if (Math.random() < .12) vorl = [R(2, 9) * 100, R(2, 9), R(2, 9), 0];
  var t = mischen(vorl).map(function (v) { return { v: v, s: '×' }; });
  return { type: 'partner', modus: 'mal', rund: 10, terme: t };
}

/* ---------- 4 Verteilen (D1) ---------- */
function verteilMal(gross) {
  var a = R(3, 9), b;
  if (!gross) { do { b = R(21, 98); } while (b % 10 === 0); }
  else { b = Math.random() < .5 ? R(1, 9) * 100 + R(11, 89) : R(1, 9) * 1000 + R(11, 89); if (b % 10 === 0) b++; }
  var st = Math.pow(10, String(b).length - 1), x0 = gross ? Math.floor(b / st) * st : b - b % 10;
  var fields = {
    x: { a: x0, ok: function (v) { return v > 0 && v < b; } },
    y: { a: b - x0, ok: function (v, w) { return v > 0 && w.x + v === b; } },
    p: { a: a * x0, ok: function (v, w) { return v === a * w.x; } },
    q: { a: a * (b - x0), ok: function (v, w) { return v === a * w.y; } },
    r: { a: a * b }
  };
  return { type: 'schritte', titel: a + ' × ' + fmt(b), frage: 'Zerlege ' + fmt(b) + ' in zwei Teile, rechne beide mal ' + a + ' und zähle zusammen.',
    rows: [['= (' + a + ' ×', F('x'), ') + (' + a + ' ×', F('y'), ')'], ['=', F('p'), '+', F('q')], ['=', F('r')]],
    fields: fields, erkl: 'Zum Beispiel: ' + a + ' × ' + fmt(b) + ' = (' + a + ' × ' + fmt(x0) + ') + (' + a + ' × ' + (b - x0) + ')' };
}
function verteilDurch() {
  var d = R(3, 9), q;
  do { q = Math.random() < .6 ? R(21, 98) : R(102, 999); } while (q % 10 === 0);
  var D = d * q, x0 = d * (q - q % 10);
  var fields = {
    x: { a: x0, ok: function (v) { return v > 0 && v < D && v % d === 0; } },
    y: { a: D - x0, ok: function (v, w) { return v > 0 && v % d === 0 && w.x + v === D; } },
    p: { a: x0 / d, ok: function (v, w) { return v * d === w.x; } },
    q: { a: (D - x0) / d, ok: function (v, w) { return v * d === w.y; } },
    r: { a: q }
  };
  return { type: 'schritte', titel: fmt(D) + ' : ' + d, frage: 'Zerlege ' + fmt(D) + ' in zwei Teile, die sich gut durch ' + d + ' teilen lassen.',
    rows: [['= (', F('x'), ': ' + d + ') + (', F('y'), ': ' + d + ')'], ['=', F('p'), '+', F('q')], ['=', F('r')]],
    fields: fields, hint: 'Beide Teile müssen sich ohne Rest durch ' + d + ' teilen lassen und zusammen ' + fmt(D) + ' geben.',
    erkl: 'Zum Beispiel: ' + fmt(D) + ' = ' + fmt(x0) + ' + ' + fmt(D - x0) };
}

/* ---------- 5 Rechentricks (D2, LZK 4) ---------- */
var TRICKS = {
  m5:   { lab: '× 10, dann : 2',   q: function (n) { return '5 × ' + fmt(n); },  s1: function (n) { return ['10 × ' + fmt(n) + ' =', n * 10]; }, s2: [': 2', function (n) { return n * 5; }] },
  m50:  { lab: '× 100, dann : 2',  q: function (n) { return '50 × ' + fmt(n); }, s1: function (n) { return ['100 × ' + fmt(n) + ' =', n * 100]; }, s2: [': 2', function (n) { return n * 50; }] },
  m500: { lab: '× 1000, dann : 2', q: function (n) { return '500 × ' + fmt(n); }, s1: function (n) { return ['1000 × ' + fmt(n) + ' =', n * 1000]; }, s2: [': 2', function (n) { return n * 500; }] },
  m9:   { lab: '× 10, dann minus die Zahl',   q: function (n) { return '9 × ' + fmt(n); },  s1: function (n) { return ['10 × ' + fmt(n) + ' =', n * 10]; }, s2: [function (n) { return '− ' + fmt(n); }, function (n) { return n * 9; }] },
  m99:  { lab: '× 100, dann minus die Zahl',  q: function (n) { return '99 × ' + fmt(n); }, s1: function (n) { return ['100 × ' + fmt(n) + ' =', n * 100]; }, s2: [function (n) { return '− ' + fmt(n); }, function (n) { return n * 99; }] },
  m999: { lab: '× 1000, dann minus die Zahl', q: function (n) { return '999 × ' + fmt(n); }, s1: function (n) { return ['1000 × ' + fmt(n) + ' =', n * 1000]; }, s2: [function (n) { return '− ' + fmt(n); }, function (n) { return n * 999; }] },
  d5:   { lab: ': 10, dann × 2',   q: function (n) { return fmt(n) + ' : 5'; },   s1: function (n) { return [fmt(n) + ' : 10 =', n / 10]; },   s2: ['× 2', function (n) { return n / 5; }] },
  d50:  { lab: ': 100, dann × 2',  q: function (n) { return fmt(n) + ' : 50'; },  s1: function (n) { return [fmt(n) + ' : 100 =', n / 100]; },  s2: ['× 2', function (n) { return n / 50; }] },
  d500: { lab: ': 1000, dann × 2', q: function (n) { return fmt(n) + ' : 500'; }, s1: function (n) { return [fmt(n) + ' : 1000 =', n / 1000]; }, s2: ['× 2', function (n) { return n / 500; }] }
};
var ANDERE = { m5: ['m50', 'm9'], m50: ['m5', 'm99', 'm500'], m500: ['m50', 'm999'], m9: ['m99', 'm5'], m99: ['m9', 'm50', 'm999'], m999: ['m99', 'm500'], d5: ['d50', 'm5'], d50: ['d5', 'd500', 'm50'], d500: ['d50', 'm500'] };
function trick(arten) {
  var art = pick(arten), T = TRICKS[art], n;
  if (art === 'd5') n = R(12, 999) * 10; else if (art === 'd50') n = R(12, 499) * 100; else if (art === 'd500') n = R(3, 99) * 1000;
  else if (art === 'm999' || art === 'm500') n = R(12, 98); else n = R(13, 999);
  var opts = mischen([art].concat(mischen(ANDERE[art]).slice(0, 2)));
  var s1 = T.s1(n), s2op = typeof T.s2[0] === 'function' ? T.s2[0](n) : T.s2[0];
  return { type: 'kette', titel: T.q(n), teile: [
    { type: 'wahl', q: '', frage: 'Welcher Trick passt?', opts: opts.map(function (k) { return TRICKS[k].lab; }), a: opts.indexOf(art), klein: true,
      erkl: 'Der passende Trick: ' + T.lab + '.' },
    { type: 'schritte', rows: [[s1[0], F('a')], ['<span class="vor">→</span> ' + s2op + ' =', F('b')]], fields: { a: { a: s1[1] }, b: { a: T.s2[1](n) } } }
  ] };
}

/* ---------- 6 Mal-Werkstatt (B2, LZK 3) ---------- */
function malWerk(stufe) {
  var a, b;
  if (stufe === 1) { a = R(3, 9); b = R(1001, 9999); }
  else if (stufe === 2) { do { a = R(12, 98); } while (a % 10 === 0); b = R(201, 9999); }
  else { do { a = R(102, 989); } while (a % 10 === 0); b = R(1001, 9999); }
  var teile = [], rows = [], fields = {};
  if (stufe === 1) { var sb = String(b); for (var i = 0; i < sb.length; i++) { var p = Number(sb[i]) * Math.pow(10, sb.length - 1 - i); if (p) teile.push([a, p]); } }
  else { var sa = String(a); for (var j = 0; j < sa.length; j++) { var q = Number(sa[j]) * Math.pow(10, sa.length - 1 - j); if (q) teile.push([q, b]); } }
  teile.forEach(function (t, k) { fields['t' + k] = { a: t[0] * t[1] }; rows.push([fmt(t[0]) + ' × ' + fmt(t[1]) + ' =', F('t' + k)]); });
  fields.r = { a: a * b }; rows.push(['<span class="vor">Zusammen:</span>', F('r'), '<span class="vor" style="font-size:.6em">← Resultat</span>']);
  return { type: 'schritte', titel: fmt(a) + ' × ' + fmt(b), frage: 'Rechne die Teilprodukte und zähle sie zusammen.', rows: rows, fields: fields };
}

/* ---------- 7 Divisions-Treppe (C1, C2, LZK 5) ---------- */
function division(stufe) {
  var d, q, r = 0;
  if (stufe === 1) { d = pick([11, 12, 13, 15, 20, 25, 30]); q = R(102, 999); }
  else if (stufe === 2) { d = R(11, 49); q = R(101, 2999); if (Math.random() < .5) r = R(1, d - 1); }
  else { d = pick([125, 150, 240, 250, R(101, 399)]); q = R(21, 899); if (Math.random() < .5) r = R(1, d - 1); }
  var D = d * q + r, dig = String(D).split('').map(Number), i = 0, p = 0, steps = [];
  while (i < dig.length && p < d) { p = p * 10 + dig[i]; i++; }
  for (;;) { var k = Math.floor(p / d); steps.push({ p: p, k: k, prod: k * d, r: p - k * d, end: i - 1 }); if (i >= dig.length) break; p = (p - k * d) * 10 + dig[i]; i++; }
  return { type: 'div', D: D, d: d, q: q, rest: r, dig: dig, steps: steps };
}

/* ---------- 8 Fachwörter (erweitert, LZK 6) ---------- */
var WORTE = { '+': ['Summand', 'Summand', 'Summe'], '−': ['Minuend', 'Subtrahend', 'Differenz'], '×': ['Faktor', 'Faktor', 'Produkt'], ':': ['Dividend', 'Divisor', 'Quotient'] };
var NAME = { '+': 'Addition', '−': 'Subtraktion', '×': 'Multiplikation', ':': 'Division' };
function begriff() {
  var op = pick(['+', '−', '×', ':']), a, b, c;
  if (op === '+') { a = R(120, 900); b = R(120, 900); c = a + b; }
  else if (op === '−') { a = R(500, 999); b = R(100, 480); c = a - b; }
  else if (op === '×') { a = R(12, 45); b = R(3, 9); c = a * b; }
  else { b = R(3, 9); c = R(12, 60); a = b * c; }
  var alle = ['Summand', 'Summe', 'Minuend', 'Subtrahend', 'Differenz', 'Faktor', 'Produkt', 'Dividend', 'Divisor', 'Quotient'];
  if (Math.random() < .3) {
    var richtig = WORTE[op][2];
    var opts = mischen([richtig].concat(mischen(alle.filter(function (w) { return w !== richtig; })).slice(0, 3)));
    return { type: 'wahl', q: 'Wie heisst das Resultat einer ' + NAME[op] + '?', klein: true, opts: opts, a: opts.indexOf(richtig) };
  }
  var pos = R(0, 2), z = [a, b, c].map(function (v, i) { return i === pos ? '<span class="mark">' + fmt(v) + '</span>' : fmt(v); });
  var wort = WORTE[op][pos];
  var eigene = WORTE[op].filter(function (w, i) { return WORTE[op].indexOf(w) === i; });
  var fremd = alle.filter(function (w) { return eigene.indexOf(w) < 0; });
  var o = mischen(eigene.concat(mischen(fremd).slice(0, 4 - eigene.length)));
  return { type: 'wahl', q: z[0] + ' ' + op + ' ' + z[1] + ' = ' + z[2], frage: 'Wie heisst die gelb markierte Zahl?', opts: o, a: o.indexOf(wort) };
}
var SAETZE = [
  ['Wenn man in einer Division den Divisor verdoppelt, verdoppelt sich auch der Quotient.', false, 'Der Quotient wird halb so gross: 24 : 4 = 6, aber 24 : 8 = 3.'],
  ['Wenn man den einen Faktor verdoppelt und den anderen halbiert, bleibt das Produkt gleich gross.', true, '4 × 6 = 24 und 8 × 3 = 24.'],
  ['Das Resultat einer Addition heisst Summand.', false, 'Das Resultat heisst Summe. Die Zahlen, die man zusammenzählt, heissen Summanden.'],
  ['Die Quersumme der grössten vierstelligen Zahl ergibt 1.', false, 'Die grösste vierstellige Zahl ist 9999. Ihre Quersumme ist 9 + 9 + 9 + 9 = 36.'],
  ['Die Quersumme von 1000 ist 1.', true, '1 + 0 + 0 + 0 = 1.'],
  ['Wenn man den Dividenden verdoppelt, verdoppelt sich auch der Quotient.', true, '24 : 4 = 6 und 48 : 4 = 12.'],
  ['Wenn man Dividend und Divisor verdoppelt, bleibt der Quotient gleich.', true, '24 : 4 = 6 und 48 : 8 = 6.'],
  ['Wenn man beide Faktoren verdoppelt, verdoppelt sich das Produkt.', false, 'Das Produkt wird viermal so gross: 3 × 4 = 12, aber 6 × 8 = 48.'],
  ['Bei einer Subtraktion darf man die Zahlen vertauschen.', false, '9 − 4 = 5, aber 4 − 9 geht nicht so.'],
  ['Bei einer Addition darf man die Summanden vertauschen.', true, '156 + 154 = 154 + 156.'],
  ['Eine Zahl mal 0 ergibt wieder die gleiche Zahl.', false, 'Eine Zahl mal 0 ergibt immer 0.'],
  ['Der Minuend ist die Zahl, von der man etwas wegnimmt.', true, 'In 750 − 430 ist 750 der Minuend.'],
  ['Das Resultat einer Subtraktion heisst Differenz.', true, '750 − 430 = 320. Die 320 ist die Differenz.'],
  ['Das Resultat einer Multiplikation heisst Faktor.', false, 'Das Resultat heisst Produkt. Die Zahlen, die man malrechnet, heissen Faktoren.'],
  ['Der Divisor ist die Zahl, durch die man teilt.', true, 'In 4272 : 12 ist 12 der Divisor.'],
  ['Wenn man zu einem Summanden 100 dazuzählt und vom anderen 100 wegnimmt, bleibt die Summe gleich.', true, '450 + 350 = 800 und 550 + 250 = 800.'],
  ['Wenn man zum Minuenden und zum Subtrahenden je 100 dazuzählt, bleibt die Differenz gleich.', true, '500 − 180 = 320 und 600 − 280 = 320.'],
  ['Die Quersumme von 345 ist 12.', true, '3 + 4 + 5 = 12.'],
  ['Wenn man den Divisor halbiert, halbiert sich auch der Quotient.', false, 'Der Quotient wird doppelt so gross: 24 : 6 = 4, aber 24 : 3 = 8.'],
  ['Eine Zahl geteilt durch 1 ergibt wieder die gleiche Zahl.', true, '648 : 1 = 648.'],
  ['Wenn man eine Zahl mit 99 malrechnet, kann man sie mit 100 malrechnen und dann die Zahl einmal abziehen.', true, '99 × 448 = 44 800 − 448 = 44 352.'],
  ['Durch 5 teilen ist gleich wie durch 10 teilen und dann verdoppeln.', true, '6700 : 10 = 670, dann 670 × 2 = 1340. Also ist 6700 : 5 = 1340.']
];
var satzStapel = [];
function satz() {
  if (!satzStapel.length) satzStapel = mischen(SAETZE);
  var s = satzStapel.pop();
  return { type: 'wahl', q: s[0], klein: true, frage: 'Richtig oder falsch?', opts: ['richtig', 'falsch'], a: s[1] ? 0 : 1, erkl: s[2] };
}
function quersumme() {
  var n = Math.random() < .15 ? pick([9999, 99999, 1000, 10000]) : R(100, 99999);
  var s = String(n).split('').reduce(function (x, c) { return x + Number(c); }, 0);
  return eingabe('Quersumme von ' + fmt(n), s, 'Zähle alle Ziffern zusammen.', String(n).split('').join(' + ') + ' = ' + s);
}

/* ---------- Die Spiele ---------- */
var GRUND = 'g', ERW = 'e';
var SPIELE = [
  { id: 'blitz', name: 'Blitz-Rechnen', sym: '40 × 3', bg: 'var(--sky)', lz: 'g', info: 'Im Kopf rechnen mit grossen Zahlen',
    ziel: 'Du kannst einfache Additionen und Subtraktionen im Kopf lösen. Du kannst Multiplikationen und Divisionen mit Zehner-, Hunderter- und Tausenderzahlen im Kopf lösen.',
    levels: [
      { name: 'Plus und Minus', info: '150 + 590, 6000 − 600', art: GRUND, n: 10, gen: kopf1 },
      { name: 'Grosse Zahlen', info: '37 000 + 51 000, 1 000 000 − 670 000', art: GRUND, n: 10, gen: kopf2 },
      { name: 'Mal mit Nullen', info: '40 × 300, 5000 × 900', art: GRUND, n: 10, gen: kopfMal },
      { name: 'Durch mit Nullen', info: '3200 : 40, 64 000 : 800', art: GRUND, n: 10, gen: kopfDurch },
      { name: 'Alles gemischt', info: 'Wie in der Lernkontrolle', art: GRUND, n: 12, gen: function () { return pick([kopf1, kopf2, kopfMal, kopfDurch])(); } }
    ] },
  { id: 'zerlegen', name: 'Schritt für Schritt', sym: '+ 500', bg: 'var(--sun)', lz: 'A3', info: 'Halbschriftlich mit Teilrechnungen',
    ziel: 'Du kannst eine Addition oder Subtraktion in Teilrechnungen zerlegen und halbschriftlich lösen.',
    levels: [
      { name: 'Plus in Schritten', info: '45 230 + 3 508', art: GRUND, n: 6, gen: function () { return zerlegen('+', false); } },
      { name: 'Minus in Schritten', info: '57 060 − 25 300', art: GRUND, n: 6, gen: function () { return zerlegen('−', false); } },
      { name: 'Sechsstellige Zahlen', info: '560 500 + 20 508', art: GRUND, n: 6, gen: function () { return zerlegen(pick(['+', '−']), true); } }
    ] },
  { id: 'partner', name: 'Rechen-Partner', sym: '+ = 100', bg: 'var(--leaf)', lz: 'ge', info: 'Zahlen geschickt zusammennehmen',
    ziel: 'Du kennst ein geeignetes Vorgehen für Rechnungen mit mehreren Zahlen. Du kannst die Reihenfolge verändern, damit es einfacher wird.',
    levels: [
      { name: 'Plus-Partner', info: '156 + 767 + 154 − 766', art: GRUND, n: 5, gen: partnerPlus },
      { name: 'Minus-Ketten', info: '66 000 − 6600 − 5900 − 12 400 − 5100', art: GRUND, n: 5, gen: partnerMinus },
      { name: 'Mal-Partner', info: '5 × 37 × 4 × 5', art: ERW, n: 6, gen: partnerMal }
    ] },
  { id: 'verteilen', name: 'Verteilen', sym: '( ) + ( )', bg: 'var(--rose)', lz: 'D1', info: 'Das Verteilungsgesetz anwenden',
    ziel: 'Du kannst das Verteilungsgesetz der Multiplikation und der Division anwenden, um schneller und einfacher zu rechnen.',
    levels: [
      { name: 'Mal mit Zweistelligen', info: '6 × 84 = (6 × 80) + (6 × 4)', art: GRUND, n: 6, gen: function () { return verteilMal(false); } },
      { name: 'Mal mit grossen Zahlen', info: '8 × 5038, 3 × 145', art: GRUND, n: 6, gen: function () { return verteilMal(true); } },
      { name: 'Durch verteilen', info: '504 : 6 = (480 : 6) + (24 : 6)', art: GRUND, n: 6, gen: verteilDurch }
    ] },
  { id: 'tricks', name: 'Rechentricks', sym: '× 99', bg: 'var(--lila)', lz: 'g', info: 'Mal 5, 50, 9, 99 und durch 5, 50',
    ziel: 'Du kennst ein geeignetes Vorgehen, um Zahlen mit 5, 50, 500, 9, 99, 999 zu multiplizieren und durch 5, 50, 500 zu dividieren.',
    levels: [
      { name: 'Mal 5, 50, 500', info: '50 × 843 = 84 300 : 2', art: GRUND, n: 6, gen: function () { return trick(['m5', 'm50', 'm500']); } },
      { name: 'Mal 9, 99, 999', info: '99 × 448 = 44 800 − 448', art: GRUND, n: 6, gen: function () { return trick(['m9', 'm99', 'm999']); } },
      { name: 'Durch 5, 50, 500', info: '6700 : 5, 38 400 : 50', art: GRUND, n: 6, gen: function () { return trick(['d5', 'd50', 'd500']); } },
      { name: 'Alle Tricks', info: 'Welcher Trick passt?', art: GRUND, n: 8, gen: function () { return trick(Object.keys(TRICKS)); } }
    ] },
  { id: 'mal', name: 'Mal-Werkstatt', sym: '76 × 8', bg: 'var(--sky)', lz: 'ge', info: 'Multiplizieren mit Teilprodukten',
    ziel: 'Du kennst ein geeignetes Vorgehen, um Multiplikationen mit zweistelligen Faktoren zu lösen. Erweitert: drei- oder vierstellige Faktoren.',
    levels: [
      { name: 'Einstellig mal', info: '6 × 2086', art: GRUND, n: 5, gen: function () { return malWerk(1); } },
      { name: 'Zweistellig mal', info: '76 × 812, 34 × 3287', art: GRUND, n: 5, gen: function () { return malWerk(2); } },
      { name: 'Dreistellig mal', info: '234 × 1567', art: ERW, n: 4, gen: function () { return malWerk(3); } }
    ] },
  { id: 'division', name: 'Divisions-Treppe', sym: ': 25', bg: 'var(--sun)', lz: 'C1 · C2 · LZK 5', info: 'Schriftlich dividieren, Schritt für Schritt',
    ziel: 'Du kannst Divisionen mit einem zweistelligen Divisor lösen. Erweitert: schriftlich mit zwei- oder dreistelligem Divisor.',
    levels: [
      { name: 'Ohne Rest', info: '7476 : 12, 43 375 : 25', art: GRUND, n: 4, gen: function () { return division(1); } },
      { name: 'Mit und ohne Rest', info: '6279 : 12 = 523 Rest 3', art: ERW, n: 4, gen: function () { return division(2); } },
      { name: 'Dreistelliger Divisor', info: '79 500 : 150', art: ERW, n: 3, gen: function () { return division(3); } }
    ] },
  { id: 'woerter', name: 'Fachwörter', sym: 'Summe', bg: 'var(--leaf)', lz: 'e', info: 'Summand, Produkt, Quotient …',
    ziel: 'Du kennst die Begriffe Summand, Summe, Minuend, Subtrahend, Differenz, Faktor, Produkt, Dividend, Divisor, Quotient und Quersumme.',
    levels: [
      { name: 'Wie heisst die Zahl?', info: 'Summand, Differenz, Divisor …', art: ERW, n: 10, gen: begriff },
      { name: 'Richtig oder falsch?', info: 'Sätze wie in der Lernkontrolle', art: ERW, n: 10, gen: satz },
      { name: 'Quersumme', info: 'Quersumme von 9999', art: ERW, n: 8, gen: quersumme }
    ] }
];
SPIELE = SPIELE.filter(function (g) { return ['blitz', 'mal', 'tricks', 'partner', 'woerter'].indexOf(g.id) >= 0; });
SPIELE.forEach(function (g) {
  if (g.id === 'blitz') { g.name = 'Kopfrechnen gemischt'; g.info = 'Plus, Minus, Mal und Durch wie in der Lernkontrolle'; }
  if (g.id === 'tricks') { g.name = 'Trick-Quiz'; g.sym = '?'; g.info = 'Alle Tricks gemischt: zuerst den passenden wählen, dann rechnen'; g.levels = [g.levels[3]]; g.levels[0].name = 'Welcher Trick passt?'; g.levels[0].info = 'Mal 5, 50, 500, 9, 99, 999 und durch 5, 50, 500 gemischt'; g.levels[0].n = 10; }
  if (g.id === 'mal') { g.name = 'Mal mit Teilprodukten'; g.info = '76 × 812 = 70 × 812 + 6 × 812'; }
});
function spielNr(id) { for (var i = 0; i < SPIELE.length; i++) if (SPIELE[i].id === id) return i; return -1; }
function A(app, view, name, sym, info, lz, ops) { return { app: app, view: view, name: name, sym: sym, info: info, lz: lz, ops: ops }; }
function SP(id) { return { spiel: id }; }
var BEREICHE = [
  { mb: ['add', 'mal', 'div'], id: 'kopf', name: 'Im Kopf', sym: '45 + 8', bg: 'var(--sky)', lz: 'g', info: 'Runde Zahlen und Nullen schnell im Kopf rechnen',
    items: [A('werkstatt', 'kopf', 'Plus und Minus im Kopf', '+ −', 'Runde Zahlen bis 1 Million, auch ergänzen', 'g', '+ −'),
            A('mal', 'kopf', 'Mal mit Nullen', '30 × 80', 'Nullentrick: Nullen weglassen, Einmaleins, Nullen anhängen', 'g', '×'),
            A('durch', 'kopf', 'Durch mit Nullen', '210 : 70', 'Nullentrick: gleich viele Nullen streichen', 'g', ':'),
            SP('blitz')] },
  { mb: ['add', 'mal', 'div'], id: 'halb', name: 'Halbschriftlich', sym: '→ 500', bg: 'var(--sun)', lz: 'ge', info: 'In Teilschritten rechnen und jeden Schritt aufschreiben',
    items: [A('werkstatt', 'strich', 'Rechenstrich', '− 3000', 'Grosse Rechnungen in Sprüngen lösen', 'g', '+ −'),
            SP('mal')] },
  { mb: ['add', 'mal', 'div'], id: 'schrift', name: 'Schriftlich', sym: '+ − × :', bg: 'var(--leaf)', lz: 'ge', info: 'Untereinander rechnen, alle vier Rechenarten',
    items: [A('werkstatt', 'schriftlich', 'Plus und Minus schriftlich', '+ −', 'Untereinander mit Behalte', 'g', '+ −'),
            A('mal', 'schriftlich', 'Mal schriftlich', '18 × 647', 'Mit 1-, 2- oder 3-stelligem Multiplikator', 'ge', '×'),
            A('durch', 'schriftlich', 'Durch schriftlich', '846 : 3', 'Schritt für Schritt geführt, auch mit Rest und 3-stelligem Divisor', 'ge', ':')] },
  { mb: ['flex'], id: 'flex', name: 'Flexibel rechnen', sym: '× 99', bg: 'var(--lila)', lz: 'ge', info: 'Rechentricks und Verteilungsgesetze, mit Erklärung',
    items: [A('flex', 't2', 'Trick mit 9, 99, 999', '× 99', '99 · 448 = 44 800 − 448', 'g', '×'),
            A('flex', 't45', 'Trick mit 5, 50, 500', '× 50', 'Mal oder durch: 50 · 862, 12 000 : 50', 'g', '× :'),
            A('flex', 'tv', 'Verteilungsgesetz', '( ) + ( )', 'Mal oder durch: 7 · 84 = (7 · 80) + (7 · 4)', 'g', '× :'),
            SP('tricks'), SP('partner')] },
  { id: 'woerter', name: 'Fachwörter', sym: 'Summe', bg: 'var(--rose)', lz: 'e', info: 'Summand, Produkt, Quotient, Quersumme',
    items: [SP('woerter')] }
];
var CUR_B = null;
/* Sterne der eingebauten Übungen: Stufen pro Übung */
var APP_STUFEN = { 'werkstatt:kopf': ['kopf-1', 'kopf-2', 'kopf-3'], 'werkstatt:strich': ['strich-1', 'strich-2', 'strich-3'], 'werkstatt:schriftlich': ['schrift-4', 'schrift-5', 'schrift-6'],
  'mal:kopf': ['kopf-1', 'kopf-2', 'kopf-3'], 'mal:schriftlich': ['schrift-1', 'schrift-2', 'schrift-3'], 'durch:kopf': ['kopf-1', 'kopf-2', 'kopf-3'], 'durch:schriftlich': ['schrift-1', 'schrift-R', 'schrift-2', 'schrift-3'],
  'flex:t2': ['t2-1', 't2-2', 't2-3'], 'flex:t45': ['t45-1', 't45-2', 't45-3'], 'flex:tv': ['tv-1', 'tv-2', 'tv-3'] };
function appSterne(it) { var d = (ST.apps && ST.apps[it.app]) || {}, x = 0; (APP_STUFEN[it.app + ':' + it.view] || []).forEach(function (k) { x += d[k] || 0; }); return x; }
function appMax(it) { return (APP_STUFEN[it.app + ':' + it.view] || []).length * 3; }
var ZAEHL = {};
function bereichItems() {
  var b = BEREICHE.filter(function (x) { return x.id === RK.bereich; })[0];
  return b ? b.items : [];
}
function awardDaten() {
  var lv = {}, st = 0, mx = 0;
  bereichItems().forEach(function (it) {
    if (it.spiel) {
      var g = SPIELE[spielNr(it.spiel)];
      g.levels.forEach(function (l, li) { var n = sterneVon(g, li); lv[(g.name + ' · ' + l.name).slice(0, 40)] = n; st += n; mx += 3; });
    } else {
      var d = (ST.apps && ST.apps[it.app]) || {};
      (APP_STUFEN[it.app + ':' + it.view] || []).forEach(function (k, i) { var n = d[k] || 0; lv[(it.name + ' · Stufe ' + (i + 1)).slice(0, 40)] = n; st += n; mx += 3; });
    }
  });
  return { lv: lv, stars: st, max: mx };
}
function sternSetzen(app, key, s) {
  ST.apps = ST.apps || {}; ST.apps[app] = ST.apps[app] || {};
  var alt = ST.apps[app][key] || 0;
  if (s > alt) { ST.apps[app][key] = s; speichern(); }
  return s > alt;
}
function toast(h) {
  document.querySelectorAll('.toast').forEach(function (x) { x.remove(); });
  var t = document.createElement('div'); t.className = 'toast'; t.innerHTML = h; document.body.appendChild(t);
  setTimeout(function () { t.classList.add('weg'); }, 2600); setTimeout(function () { t.remove(); }, 3200);
}
var THEO = { 'werkstatt:kopf': { mb: 'add', weg: 'im Kopf' }, 'werkstatt:strich': { mb: 'add', weg: 'Rechenstrich' }, 'werkstatt:schriftlich': { mb: 'add', weg: 'schriftlich' },
  'mal:kopf': { mb: 'mal', weg: '0-Trick' }, 'mal:schriftlich': { mb: 'mal', weg: 'schriftlich' }, 'durch:kopf': { mb: 'div', weg: '0-Trick' }, 'durch:schriftlich': { mb: 'div', weg: 'schriftlich' },
  'flex:t2': { mb: 'flex', weg: 'Trick mit 9 / 99 / 999' }, 'flex:t45': { mb: 'flex', weg: 'Multiplizieren mit 5 / 50 / 500' }, 'flex:tv': { mb: 'flex', weg: 'Verteilungsgesetz Multiplikation' } };
var SPIEL_THEO = { blitz: { mb: 'mal', weg: '0-Trick' }, mal: { mb: 'mal', weg: 'mit Notizen' }, tricks: { mb: 'flex' }, partner: { mb: 'flex' }, woerter: { mb: 'add' } };
var SPIEL_TIPP = {
  blitz: 'Bei Plus und Minus rechnest du mit den Tausendern wie mit Einern: 37 000 + 51 000 ist wie 37 + 51. Bei Mal und Durch lässt du die Nullen zuerst weg und hängst sie am Schluss wieder an. Beim Dividieren streichst du bei beiden Zahlen gleich viele Nullen.',
  mal: 'Zerlege die Zahl in ihre Stellen, z. B. 76 = 70 + 6. Rechne jede Zeile einzeln und zähle am Schluss alle Teilprodukte zusammen.',
  tricks: 'Schau dir die Zahl genau an: 9, 99, 999 sind nur 1 weniger als 10, 100, 1000. 5, 50, 500 sind die Hälfte von 10, 100, 1000.',
  partner: 'Suche zwei Zahlen, die zusammen eine runde Zahl geben, z. B. 156 + 154 = 310 oder 767 − 766 = 1. Beim Malrechnen helfen 5 · 2, 25 · 4 oder 125 · 8.',
  woerter: 'Plus: Summand + Summand = Summe. Minus: Minuend − Subtrahend = Differenz. Mal: Faktor · Faktor = Produkt. Durch: Dividend : Divisor = Quotient. Quersumme: alle Ziffern zusammenzählen.'
};
/* Filter: alle, nur Grundanforderungen (g) oder nur erweiterte Anforderungen (e) */
function filt() { return ST.filter === 'g' || ST.filter === 'e' ? ST.filter : ''; }
function passt(c) { var f = filt(); return !f || c.indexOf(f) >= 0; }
function itemLz(it) { return it.spiel ? SPIELE[spielNr(it.spiel)].lz : it.lz; }
function filterLeiste() {
  var f = filt();
  return '<div class="filter" role="group" aria-label="Anforderungen filtern"><span>Zeigen:</span>' +
    [['', 'Alle'], ['g', 'Grundanforderungen'], ['e', 'Erweiterte Anforderungen']].map(function (x) {
      return '<button class="fk ' + (x[0] || 'a') + '" data-f="' + x[0] + '" aria-pressed="' + (f === x[0]) + '">' + x[1] + '</button>';
    }).join('') + '</div>';
}
function filterBinden(neu) {
  app.querySelectorAll('[data-f]').forEach(function (b) { b.onclick = function () { ST.filter = b.dataset.f; speichern(); neu(); }; });
}
/* in den eingebauten Übungen: welche Knöpfe zu den erweiterten Anforderungen gehören */
var APP_ERW = { 'mal:schriftlich': { seg: 'wlen', e: ['3'] }, 'durch:schriftlich': { seg: 'slv', e: ['2', '3'] } };
function anf(c) {
  return '<span class="anf">' + (c.indexOf('g') >= 0 ? '<span class="lz g">Grundanforderungen</span>' : '') + (c.indexOf('e') >= 0 ? '<span class="lz e">erweiterte Anforderungen</span>' : '') + '</span>';
}
function sterneVon(g, li) { return (ST[g.id] && ST[g.id][li]) || 0; }

/* ---------- Ansichten ---------- */
function zurueck(txt) { return '<button class="back" data-back><img src="' + EULE + '" alt="">← ' + (txt || 'Zurück') + '</button>'; }
function sterneSumme(g) { var x = 0; g.levels.forEach(function (l, li) { x += sterneVon(g, li); }); return x; }
function heim() { if (RK.bereich) send({ type: 'close' }); else start(); }
function start() {
  RUN = null; CUR_B = null;
  if (RK.bereich) {
    if (RK.bereich === 'merk') return merkListe();
    var bi0 = -1; BEREICHE.forEach(function (b, i) { if (b.id === RK.bereich) bi0 = i; });
    var b0 = BEREICHE[bi0];
    if (b0.items.length === 1 && b0.items[0].spiel) return stufen(spielNr(b0.items[0].spiel));
    return bereich(bi0);
  }
  var o = '<div class="wrap">' + (RK.ziel === 'eulenkiste' ? '<a class="back" href="../mathekiste/" style="text-decoration:none;color:inherit"><img src="' + EULE + '" alt="">← Mathekiste</a>' : '') + '<div class="kopf"><div class="eule"><img src="' + EULE + '" alt="Eule"></div><div class="tx"><h1>Rechenoperationen</h1>' +
    '<div class="unter">Addieren und Subtrahieren · Multiplizieren · Dividieren · Flexibel rechnen</div></div></div><div class="deko">✦ ✧ ✦</div>' + filterLeiste() + '<div class="grid">';
  BEREICHE.forEach(function (b, bi) {
    var namen = b.items.filter(function (it) { return passt(itemLz(it)); });
    if (!namen.length) return;
    o += '<button class="spiel" data-b="' + bi + '"><span class="ic" style="background:' + b.bg + '">' + b.sym + '</span><span class="t"><b>' + b.name + '</b>' +
      '<span class="i">' + b.info + '</span>' + anf(filt() || b.lz) + '<span class="i" style="font-size:14px">' + namen.length + (namen.length === 1 ? ' Spiel' : ' Spiele') + '</span></span></button>';
  });
  o += '<button class="spiel" data-merk><span class="ic" style="background:#fff">Merk-<br>blatt</span><span class="t"><b>Merkblätter</b><span class="i">Theorie: So rechnest du, mit Beispielen zum Aufdecken</span><span class="i" style="font-size:14px">4 Merkblätter</span></span></button>';
  o += '</div>' + (OHNE_STERNE ? '<p class="hinweis2">Hier wird nichts gespeichert, ausser der Auswahl auf diesem Gerät. In der Klassenkiste sammeln die Kinder Sterne, und die Lehrperson sieht ihren Stand.</p>' : '') +
    '<div class="fuss">Lernziele 5.5 · Grundanforderungen und erweiterte Anforderungen</div></div>';
  app.innerHTML = o; scrollTo(0, 0);
  app.querySelector('[data-merk]').onclick = merkListe;
  filterBinden(start);
  app.querySelectorAll('[data-b]').forEach(function (x) { x.onclick = function () { var b = BEREICHE[+x.dataset.b]; var drin = b.items.filter(function (it) { return passt(itemLz(it)); }); if (drin.length === 1 && drin[0].spiel) { CUR_B = null; stufen(spielNr(drin[0].spiel)); } else bereich(+x.dataset.b); }; });
}
function bereich(bi) {
  RUN = null; CUR_B = bi;
  var b = BEREICHE[bi];
  var o = '<div class="wrap">' + zurueck(RK.bereich ? 'Zurück' : 'Übersicht') + '<div class="kopf"><span class="ic" style="background:' + b.bg + ';width:96px;height:96px;font-size:24px">' + b.sym + '</span><div class="tx"><h2>' + b.name + '</h2><div class="unter">' + b.info + '</div></div></div>' +
    (b.mb ? '<div class="mbrow"><span>Theorie:</span>' + b.mb.map(function (k) { return '<button class="klein-k" data-mbk="' + k + '">Merkblatt ' + MB[k].kurz + '</button>'; }).join('') + '</div>' : '') + filterLeiste() + '<div class="grid">';
  b.items.forEach(function (it, ii) {
    if (!passt(itemLz(it))) return;
    if (it.spiel) {
      var g = SPIELE[spielNr(it.spiel)];
      o += '<button class="spiel" data-i="' + ii + '"><span class="ic" style="background:' + g.bg + '">' + g.sym + '</span><span class="t"><b>' + g.name + '</b><span class="i">' + g.info + '</span>' +
        '' + anf(g.lz) + '<span class="stars" style="font-size:16px">★ ' + sterneSumme(g) + ' von ' + g.levels.length * 3 + '</span></span></button>';
    } else {
      o += '<button class="spiel" data-i="' + ii + '"><span class="ic" style="background:' + b.bg + '">' + it.sym + '</span><span class="t"><b>' + it.name + '</b><span class="i">' + it.info + '</span>' +
        anf(it.lz) + '<span class="stars" style="font-size:16px">★ ' + appSterne(it) + ' von ' + appMax(it) + '</span></span></button>';
    }
  });
  app.innerHTML = o + '</div></div>'; scrollTo(0, 0);
  app.querySelector('[data-back]').onclick = RK.bereich ? heim : start;
  app.querySelectorAll('[data-mbk]').forEach(function (x) { x.onclick = function () { merkblatt(x.dataset.mbk, function () { bereich(bi); }); }; });
  filterBinden(function () { if (BEREICHE[bi].items.some(function (it) { return passt(itemLz(it)); })) bereich(bi); else start(); });
  app.querySelectorAll('[data-i]').forEach(function (x) { x.onclick = function () { var it = b.items[+x.dataset.i]; if (it.spiel) stufen(spielNr(it.spiel)); else oeffneApp(it); }; });
}
function zuBereich() { if (CUR_B === null) heim(); else bereich(CUR_B); }
function oeffneApp(it) {
  RUN = null;
  app.innerHTML = '<div class="wrap"><div class="apphost"></div></div>';
  var host = app.querySelector('.apphost'), R = host.attachShadow({ mode: 'open' });
  R.innerHTML = '<style>' + APP_CSS[it.app] + APP_EULE + '</style><div class="app">' + APP_HTML[it.app] + '</div>';
  R.querySelectorAll('.back').forEach(function (b) { b.innerHTML = '<img src="' + EULE + '" alt="">← Zurück'; });
  R.addEventListener('click', function (e) { var b = e.target.closest('[data-go="home"]'); if (b) { e.stopPropagation(); e.preventDefault(); zuBereich(); } }, true);
  var th = THEO[it.app + ':' + it.view];
  R.querySelectorAll('.back').forEach(function (b) { var t = document.createElement('button'); t.className = 'theo'; t.textContent = 'Merkblatt'; t.onclick = function () { merkFenster(th); }; b.after(t); });
  R.querySelectorAll('section').forEach(function (sec) {
    var notes = sec.querySelectorAll('.note'), sheet = sec.querySelector('.sheet');
    if (!notes.length || !sheet) return;
    var b = document.createElement('button'); b.className = 'birne'; b.setAttribute('aria-expanded', 'false'); b.innerHTML = BIRNE + '<span>Tipp</span>';
    var box = document.createElement('div'); box.className = 'birnbox'; box.hidden = true;
    b.onclick = function () {
      var auf = box.hidden; box.hidden = !auf; b.setAttribute('aria-expanded', String(auf));
      if (auf) {
        box.innerHTML = Array.prototype.map.call(notes, function (n) { return n.textContent.trim() ? '<p>' + n.innerHTML + '</p>' : ''; }).join('') + '<button class="mbl">Im Merkblatt nachschauen</button>';
        box.querySelector('.mbl').onclick = function () { merkFenster(th); };
      }
    };
    sheet.prepend(box); sheet.prepend(b);
  });
  var STAR = function (key, s) {
    if (OHNE_STERNE) return '';
    var neu = sternSetzen(it.app, key, s);
    if (neu) toast(sterneHTML(s) + ' Neuer Rekord auf dieser Stufe!');
    var o = ''; for (var i = 0; i < 3; i++) o += '<span style="color:' + (i < s ? '#d6ad45' : '#e6dcc2') + '">★</span>';
    return '<div style="font-size:46px;letter-spacing:4px;margin-top:6px">' + o + '</div>';
  };
  var SOLVED = function (key) {
    antwort(true);
    if (OHNE_STERNE) return;
    var k = it.app + ':' + key; ZAEHL[k] = (ZAEHL[k] || 0) + 1;
    var s = Math.min(3, Math.floor(ZAEHL[k] / 2));
    if (ZAEHL[k] % 2 === 0 && ZAEHL[k] <= 6) toast(sterneHTML(s) + (sternSetzen(it.app, key, s) ? ' Ein Stern mehr!' : ' Stark, weiter so!'));
    else if (ZAEHL[k] === 1) toast('Je 2 Rechnungen ohne Hilfe geben einen Stern.');
  };
  var zeige = APPS[it.app](R, zuBereich, STAR, SOLVED, antwort);
  zeige(it.view);
  var ae = APP_ERW[it.app + ':' + it.view], f = filt();
  if (ae && f) {
    var knoepfe = Array.prototype.slice.call(R.querySelectorAll('.seg[data-for="' + ae.seg + '"] button'));
    var bleiben = knoepfe.filter(function (b) { return (ae.e.indexOf(b.dataset.v) >= 0) === (f === 'e'); });
    knoepfe.forEach(function (b) { b.hidden = bleiben.indexOf(b) < 0; });
    if (bleiben.length && bleiben.every(function (b) { return b.getAttribute('aria-pressed') !== 'true'; })) bleiben[0].click();
  }
  scrollTo(0, 0);
}
var FARBEN = ['var(--sky)', 'var(--sun)', 'var(--leaf)', 'var(--rose)', 'var(--lila)'];
function stufen(gi) {
  RUN = null;
  var g = SPIELE[gi];
  var o = '<div class="wrap">' + zurueck() + '<div class="kopf"><span class="ic" style="background:' + g.bg + ';width:96px;height:96px;font-size:24px">' + g.sym + '</span><div class="tx"><h2>' + g.name + '</h2><div class="unter">' + g.info + '</div></div></div>' +
    '<div class="ziel"><b>Lernziel:</b> ' + g.ziel + '</div><div class="lvs">';
  g.levels.forEach(function (l, li) {
    if (!passt(l.art)) return;
    o += '<button class="lv" data-l="' + li + '"><span class="n" style="background:' + FARBEN[li % 5] + '">' + (li + 1) + '</span><span class="tx"><b>' + l.name + '</b><span>' + l.info + '</span>' +
      '<span class="tag ' + l.art + '">' + (l.art === GRUND ? 'Grundanforderung' : 'erweiterte Anforderung') + '</span></span>' + sterneHTML(sterneVon(g, li)) + '</button>';
  });
  app.innerHTML = o + '</div></div>'; scrollTo(0, 0);
  app.querySelector('[data-back]').onclick = zuBereich;
  app.querySelectorAll('[data-l]').forEach(function (b) { b.onclick = function () { spielen(gi, +b.dataset.l); }; });
}

var RUN = null;
function spielen(gi, li) {
  var g = SPIELE[gi], lv = g.levels[li];
  RUN = { gi: gi, li: li, g: g, lv: lv, i: 0, n: lv.n, res: [] };
  send({ type: 'level', level: (g.name + ' · ' + lv.name).slice(0, 40) });
  app.innerHTML = '<div class="wrap"><div class="ptop">' + zurueck() + '<div class="pt">' + g.name + ' · ' + lv.name + '</div><div class="dots" id="dots"></div></div>' +
    '<div class="ptools"><button class="birne-k" id="birne" aria-expanded="false">' + BIRNE + 'Tipp</button><button class="theo-k" id="theo">Merkblatt</button></div><div class="birnbox" id="birnbox" hidden>' + (SPIEL_TIPP[g.id] || '') + '</div>' +
    '<div class="karte" id="karte"></div><div class="rueck" id="rueck" aria-live="polite"></div><div class="knopf"><button class="go" id="go">Prüfen</button></div></div>';
  app.querySelector('[data-back]').onclick = function () { stufen(gi); };
  document.getElementById('go').onclick = knopf;
  var bi = document.getElementById('birne'), bb = document.getElementById('birnbox');
  bi.onclick = function () { bb.hidden = !bb.hidden; bi.setAttribute('aria-expanded', String(!bb.hidden)); };
  document.getElementById('theo').onclick = function () { merkFenster(SPIEL_THEO[g.id]); };
  scrollTo(0, 0);
  naechste();
}
function punkte() {
  var o = '';
  for (var i = 0; i < RUN.n; i++) o += '<i class="' + (i < RUN.res.length ? (RUN.res[i] ? 'ok' : 'halb') : (i === RUN.i ? 'jetzt' : '')) + '"></i>';
  document.getElementById('dots').innerHTML = o;
}
var API = {
  msg: function (h, k) { var r = document.getElementById('rueck'); if (!r) return; r.innerHTML = h || ''; r.className = 'rueck ' + (k || ''); },
  fail: function () { RUN.t.err = true; },
  done: function () { RUN.t.fertig = true; var b = document.getElementById('go'); b.textContent = RUN.i + 1 >= RUN.n ? 'Fertig' : 'Weiter'; b.className = 'go sun'; b.hidden = false; b.focus(); }
};
function naechste() {
  if (RUN.i >= RUN.n) return ende();
  var t = RUN.lv.gen(); RUN.t = t; t.err = false; t.fertig = false;
  punkte(); API.msg('');
  var b = document.getElementById('go'); b.textContent = 'Prüfen'; b.className = 'go'; b.hidden = false;
  var k = document.getElementById('karte'); k.innerHTML = '';
  TYPEN[t.type].render(t, k, API);
}
function knopf() {
  var t = RUN.t;
  if (t.fertig) { RUN.res.push(!t.err); antwort(!t.err); RUN.i++; naechste(); return; }
  TYPEN[t.type].check(t, API);
}
document.addEventListener('keydown', function (e) {
  if (e.key !== 'Enter' || !RUN || !document.getElementById('go')) return;
  if (e.target && e.target.tagName === 'BUTTON' && e.target.id !== 'go') return;
  e.preventDefault(); knopf();
});
function ende() {
  var gut = RUN.res.filter(Boolean).length, n = RUN.n, s = gut / n >= .85 ? 3 : gut / n >= .6 ? 2 : 1;
  var g = RUN.g, li = RUN.li, gi = RUN.gi;
  ST[g.id] = ST[g.id] || {}; if ((ST[g.id][li] || 0) < s) ST[g.id][li] = s; speichern();
  var txt = s === 3 ? 'Ausgezeichnet!' : s === 2 ? 'Gut gemacht!' : 'Weiter üben lohnt sich!';
  app.innerHTML = '<div class="wrap">' + zurueck() + '<div class="ende"><div class="eule" style="width:120px;height:120px"><img src="' + EULE + '" alt=""></div><h2>' + txt + '</h2>' + sterneHTML(s) +
    '<div style="font-size:22px">' + gut + ' von ' + n + ' Aufgaben beim ersten Versuch richtig.</div><div class="knopf"><button class="go" id="nochmal">Nochmal spielen</button>' +
    (li + 1 < g.levels.length ? '<button class="go sun" id="weiter">Nächste Stufe</button>' : '') + '<button class="go alt" id="zu">Alle Stufen</button></div></div></div>';
  RUN = null;
  app.querySelector('[data-back]').onclick = function () { stufen(gi); };
  document.getElementById('nochmal').onclick = function () { spielen(gi, li); };
  document.getElementById('zu').onclick = function () { stufen(gi); };
  var w = document.getElementById('weiter'); if (w) w.onclick = function () { spielen(gi, li + 1); };
  document.getElementById('nochmal').focus();
}

/* ---------- Aufgabentypen ---------- */
function feld(id, f) {
  var l = Math.max(String(fmt(f.a)).length, 2);
  return '<input class="in" data-f="' + id + '" inputmode="numeric" autocomplete="off" aria-label="Antwort" style="width:' + (l * .58 + 1.1) + 'em">';
}
var TYPEN = {};
TYPEN.schritte = {
  render: function (t, k) {
    var h = '';
    if (t.titel) h += '<div class="q">' + t.titel + '</div>';
    if (t.frage) h += '<div class="frage">' + t.frage + '</div>';
    h += '<div class="rows"' + (t.gross ? ' style="align-items:center"' : '') + '>' + t.rows.map(function (r) {
      return '<div class="row"' + (t.gross ? ' style="font-size:clamp(30px,6vw,44px)"' : '') + '>' + r.map(function (x) { return typeof x === 'string' ? '<span>' + x + '</span>' : feld(x.f, t.fields[x.f]); }).join('') + '</div>';
    }).join('') + '</div>';
    var box = document.createElement('div'); box.style.cssText = 'display:flex;flex-direction:column;gap:16px;align-items:center;max-width:100%';
    box.innerHTML = h; k.appendChild(box); t.box = box; t.tries = 0;
    box.querySelectorAll('.in').forEach(function (i) { i.oninput = function () { i.classList.remove('no'); }; });
    var e = box.querySelector('.in'); if (e) setTimeout(function () { e.focus(); }, 30);
  },
  check: function (t, api) {
    var ins = t.box.querySelectorAll('.in'), w = {}, leer = null;
    ins.forEach(function (i) { var v = zahl(i.value); w[i.dataset.f] = v; if (v === null && !leer) leer = i; });
    if (leer) { api.msg('Fülle zuerst alle Felder aus (nur Ziffern).', 'info'); leer.focus(); return; }
    var alle = true, erstesFalsch = null;
    ins.forEach(function (i) {
      var f = t.fields[i.dataset.f], v = w[i.dataset.f];
      var ok = f.ok ? f.ok(v, w) : v === f.a;
      i.classList.toggle('ok', ok); i.classList.toggle('no', !ok);
      if (!ok) { alle = false; if (!erstesFalsch) erstesFalsch = i; }
    });
    if (alle) { ins.forEach(function (i) { i.disabled = true; }); api.msg(pick(LOB), 'ok'); api.done(); return; }
    t.tries++; api.fail();
    if (t.tries >= 2) {
      ins.forEach(function (i) { var f = t.fields[i.dataset.f]; var anders = zahl(i.value) !== f.a; i.value = fmt(f.a); i.disabled = true; i.classList.remove('no'); if (anders) { i.classList.remove('ok'); i.classList.add('zeig'); } });
      api.msg('So wäre es richtig (gelbe Felder).' + (t.erkl ? '<br><span style="font-size:.85em">' + t.erkl + '</span>' : ''), 'info'); api.done();
    } else { api.msg(t.hint || 'Schau die roten Felder nochmals an.', 'no'); erstesFalsch.focus(); erstesFalsch.select(); }
  }
};
TYPEN.wahl = {
  render: function (t, k, api) {
    var box = document.createElement('div'); box.style.cssText = 'display:flex;flex-direction:column;gap:16px;align-items:center;width:100%';
    box.innerHTML = (t.q ? '<div class="q' + (t.klein ? ' klein' : '') + '">' + t.q + '</div>' : '') + (t.frage ? '<div class="frage">' + t.frage + '</div>' : '') +
      '<div class="opts">' + t.opts.map(function (o, i) { return '<button class="opt" data-o="' + i + '">' + o + '</button>'; }).join('') + '</div>';
    k.appendChild(box); t.tries = 0;
    if (!t.inKette) document.getElementById('go').hidden = true;
    var bs = box.querySelectorAll('.opt');
    bs.forEach(function (b) {
      b.onclick = function () {
        if (t.fertig || t.zu || b.disabled) return;
        var i = +b.dataset.o;
        if (i === t.a) { b.classList.add('ok'); t.zu = true; bs.forEach(function (x) { x.disabled = true; }); api.msg(pick(LOB) + (t.erkl && t.opts.length === 2 ? '<br><span style="font-size:.85em">' + t.erkl + '</span>' : ''), 'ok'); api.done(); return; }
        b.classList.add('no'); b.disabled = true; t.tries++; api.fail();
        if (t.tries >= 2 || t.opts.length === 2) { bs[t.a].classList.add('zeig'); t.zu = true; bs.forEach(function (x) { x.disabled = true; }); api.msg('Richtig wäre: <b>' + t.opts[t.a] + '</b>' + (t.erkl ? '<br><span style="font-size:.85em">' + t.erkl + '</span>' : ''), 'info'); api.done(); }
        else api.msg('Noch nicht. Versuch es nochmals!', 'no');
      };
    });
    setTimeout(function () { bs[0].focus(); }, 30);
  },
  check: function (t, api) { api.msg('Tippe eine Antwort an.', 'info'); }
};
TYPEN.kette = {
  render: function (t, k, api) {
    k.innerHTML = '<div class="q">' + t.titel + '</div>'; t.pos = 0; t.k = k;
    var self = this;
    t.sub = {
      msg: api.msg, fail: function () { api.fail(); },
      done: function () {
        t.pos++;
        if (t.pos >= t.teile.length) { api.done(); return; }
        setTimeout(function () { api.msg(''); self.zeige(t); }, 650);
      }
    };
    self.zeige(t);
  },
  zeige: function (t) {
    var teil = t.teile[t.pos]; teil.inKette = true; teil.err = false; teil.fertig = false;
    document.getElementById('go').hidden = teil.type === 'wahl';
    TYPEN[teil.type].render(teil, t.k, t.sub);
  },
  check: function (t, api) { var teil = t.teile[t.pos]; if (teil) TYPEN[teil.type].check(teil, t.sub); }
};
TYPEN.partner = {
  render: function (t, k) {
    t.k = k; t.sel = []; t.offen = null; t.tries = 0; t.verlauf = [];
    t.terme.forEach(function (x, i) { x.id = i; }); t.nid = t.terme.length;
    var op = t.modus === 'mal' ? ' × ' : null;
    t.titel = t.terme.map(function (x, i) { return (i ? (op || ' ' + x.s + ' ') : '') + fmt(x.v); }).join('');
    this.zeichne(t);
  },
  zeichne: function (t) {
    var self = this, mal = t.modus === 'mal';
    var h = '<div class="q klein">' + t.titel + ' = ?</div><div class="frage">' +
      (t.terme.length > 1 ? 'Tippe zwei Zahlen an, die gut zusammenpassen.' + (mal ? '' : ' Das Zeichen vor der Zahl gehört zu ihr.') : 'Fertig gerechnet!') + '</div><div class="terme">';
    t.terme.forEach(function (x, i) {
      if (i) h += '<span class="sg">' + x.s + '</span>';
      h += '<button class="chip' + (t.sel.indexOf(x.id) >= 0 ? ' sel' : '') + (x.neu ? ' neu' : '') + '" data-id="' + x.id + '">' + fmt(x.v) + '</button>';
      x.neu = false;
    });
    h += '</div>';
    if (t.offen) h += '<div class="rows" style="align-items:center"><div class="row"><span>' + t.offen.txt + ' =</span>' + feld('p', { a: t.offen.r }) + '</div></div>';
    if (t.verlauf.length) h += '<div class="verlauf">' + t.verlauf.join('<br>') + '</div>';
    t.k.innerHTML = h;
    t.k.querySelectorAll('.chip').forEach(function (b) { b.onclick = function () { self.tipp(t, +b.dataset.id); }; });
    var inp = t.k.querySelector('.in'); if (inp) { inp.oninput = function () { inp.classList.remove('no'); }; setTimeout(function () { inp.focus(); }, 30); }
  },
  tipp: function (t, id) {
    if (t.fertig || t.terme.length < 2) return;
    if (t.offen) { t.offen = null; t.sel = []; t.tries = 0; }
    var j = t.sel.indexOf(id);
    if (j >= 0) t.sel.splice(j, 1); else t.sel.push(id);
    API.msg('');
    if (t.sel.length === 2) {
      var A = t.terme.filter(function (x) { return x.id === t.sel[0]; })[0], B = t.terme.filter(function (x) { return x.id === t.sel[1]; })[0];
      var iA = t.terme.indexOf(A), iB = t.terme.indexOf(B); if (iB < iA) { var tmp = A; A = B; B = tmp; }
      var sA = t.terme.indexOf(A) === 0 ? '+' : A.s, nur2 = t.terme.length === 2, r, s, txt, schoen;
      if (t.modus === 'mal') { r = A.v * B.v; s = '×'; txt = fmt(A.v) + ' × ' + fmt(B.v); schoen = r % 10 === 0; }
      else if (sA === B.s) { r = A.v + B.v; s = sA; txt = fmt(A.v) + ' + ' + fmt(B.v); schoen = r % t.rund === 0; if (s === '−') txt = '<span class="vor" style="font-size:.7em">beides abziehen:</span> ' + txt; }
      else {
        var P = sA === '+' ? A : B, N = sA === '+' ? B : A;
        if (P.v < N.v) { API.msg('Das gäbe eine Minuszahl. Nimm einen anderen Partner.', 'info'); t.sel = []; this.zeichne(t); return; }
        r = P.v - N.v; s = '+'; txt = fmt(P.v) + ' − ' + fmt(N.v); schoen = r % t.rund === 0 || r < 10;
      }
      if (!schoen && !nur2) { API.msg('Diese zwei geben keine runde Zahl. Such ein besseres Paar!', 'info'); t.sel = []; this.zeichne(t); return; }
      t.offen = { r: r, s: s, txt: txt, a: A, b: B };
    }
    this.zeichne(t);
  },
  check: function (t, api) {
    if (!t.offen) { api.msg(t.sel.length ? 'Tippe noch eine zweite Zahl an.' : 'Tippe zwei Zahlen an, die gut zusammenpassen.', 'info'); return; }
    var inp = t.k.querySelector('.in'), v = zahl(inp.value);
    if (v === null) { api.msg('Schreib das Resultat ins Feld.', 'info'); inp.focus(); return; }
    var o = t.offen;
    if (v !== o.r) {
      t.tries++; api.fail(); inp.classList.add('no');
      if (t.tries < 2) { api.msg('Rechne nochmals nach.', 'no'); inp.select(); return; }
      api.msg('Das gibt ' + fmt(o.r) + '.', 'info');
    } else api.msg(pick(LOB), 'ok');
    var pos = Math.min(t.terme.indexOf(o.a), t.terme.indexOf(o.b));
    t.terme = t.terme.filter(function (x) { return x !== o.a && x !== o.b; });
    t.terme.splice(pos, 0, { v: o.r, s: o.s, id: t.nid++, neu: true });
    t.verlauf.push(o.txt.replace(/<[^>]+>/g, '') + ' = ' + fmt(o.r));
    t.offen = null; t.sel = []; t.tries = 0;
    this.zeichne(t);
    if (t.terme.length === 1) { api.msg((t.err ? '' : pick(LOB) + ' ') + 'Resultat: <b>' + fmt(t.terme[0].v) + '</b>', t.err ? 'info' : 'ok'); api.done(); }
  }
};
TYPEN.div = {
  render: function (t, k) { t.k = k; t.si = 0; t.phase = 'k'; t.qs = ''; t.tries = 0; t.hilfe = false; this.zeichne(t); },
  zeichne: function (t) {
    var self = this, L = t.dig.length, W = L + 1, rows = [];
    function leer() { var a = []; for (var i = 0; i < W; i++) a.push({ c: '' }); return a; }
    function setz(row, str, endCol, cls) { for (var i = 0; i < str.length; i++) { var c = endCol - (str.length - 1 - i); if (c >= 0) row[c] = { c: str[i], k: cls }; } return endCol - str.length + 1; }
    var r0 = leer(); t.dig.forEach(function (d, i) { r0[i + 1] = { c: String(d), k: (t.si === 0 && i <= t.steps[0].end) ? 'hl' : '' }; });
    rows.push(r0);
    for (var s = 0; s <= t.si && s < t.steps.length; s++) {
      var st = t.steps[s], zeigK = s < t.si || t.phase === 'r', zeigR = s < t.si;
      if (!zeigK) break;
      var pr = leer(), anf = setz(pr, String(st.prod), st.end + 1, 'u');
      pr[anf - 1] = { c: '−', k: 'm' };
      for (var u = anf; u <= st.end + 1; u++) pr[u].k = 'u';
      rows.push(pr);
      if (zeigR) {
        var rr = leer(), naechst = s + 1 < t.steps.length;
        var txt = naechst ? String(t.steps[s + 1].p) : String(st.r);
        setz(rr, txt, naechst ? st.end + 2 : st.end + 1, (naechst && s + 1 === t.si) ? 'hl' : '');
        rows.push(rr);
      }
    }
    var fertig = t.si >= t.steps.length;
    var h = '<div class="dbox"><div class="dgrid">';
    rows.forEach(function (r, ri) {
      h += '<div class="drow">' + r.map(function (c) { return '<span class="dc ' + (c.k || '') + '">' + (c.c || '&nbsp;') + '</span>'; }).join('');
      if (ri === 0) h += '<span class="qq">: ' + fmt(t.d) + ' = ' + t.qs + (fertig || t.phase !== 'k' ? '' : '<span class="qbox">?</span>') + (fertig && t.rest ? ' Rest ' + t.rest : '') + '</span>';
      h += '</div>';
    });
    h += '</div>';
    if (!fertig) {
      var cur = t.steps[t.si];
      h += '<div class="dpan">';
      if (t.phase === 'k') h += '<div class="frage" style="text-align:left">Wie oft passt <b>' + fmt(t.d) + '</b> in <b>' + fmt(cur.p) + '</b>?</div><div class="row"><span>' + fmt(cur.p) + ' : ' + fmt(t.d) + ' ≈</span>' + feld('x', { a: 9 }) + '</div>';
      else h += '<div class="frage" style="text-align:left">' + cur.k + ' × ' + fmt(t.d) + ' = ' + fmt(cur.prod) + '. Wie viel bleibt übrig?</div><div class="row"><span>' + fmt(cur.p) + ' − ' + fmt(cur.prod) + ' =</span>' + feld('x', { a: cur.p }) + '</div>';
      h += '<button class="klein-k" id="vfk">' + (t.hilfe ? 'Vielfache ausblenden' : 'Hilfe: Vielfache von ' + fmt(t.d)) + '</button>';
      if (t.hilfe) { h += '<div class="vf">'; for (var m = 1; m <= 9; m++) h += '<span>' + m + ' × ' + fmt(t.d) + ' = ' + fmt(m * t.d) + '</span>'; h += '</div>'; }
      h += '</div>';
    }
    h += '</div>';
    t.k.innerHTML = '<div class="frage">Rechne schriftlich. Die gelbe Zahl ist dran.</div>' + h;
    var vb = document.getElementById('vfk'); if (vb) vb.onclick = function () { t.hilfe = !t.hilfe; self.zeichne(t); };
    var inp = t.k.querySelector('.in'); if (inp) { inp.oninput = function () { inp.classList.remove('no'); }; setTimeout(function () { inp.focus(); }, 30); }
  },
  check: function (t, api) {
    var inp = t.k.querySelector('.in'); if (!inp) return;
    var v = zahl(inp.value), cur = t.steps[t.si];
    if (v === null) { api.msg('Schreib eine Zahl ins Feld.', 'info'); inp.focus(); return; }
    if (t.phase === 'k') {
      if (v === cur.k) { t.qs += cur.k; t.phase = 'r'; t.tries = 0; api.msg(pick(LOB) + ' Jetzt abziehen.', 'ok'); this.zeichne(t); return; }
      t.tries++; api.fail(); inp.classList.add('no');
      var tipp = v * t.d > cur.p ? 'Zu viel: ' + v + ' × ' + fmt(t.d) + ' = ' + fmt(v * t.d) + ' ist grösser als ' + fmt(cur.p) + '.' : 'Da passt noch mehr: ' + (v + 1) + ' × ' + fmt(t.d) + ' = ' + fmt((v + 1) * t.d) + '.';
      if (t.tries >= 2) { t.qs += cur.k; t.phase = 'r'; t.tries = 0; this.zeichne(t); api.msg(fmt(t.d) + ' passt ' + cur.k + '-mal in ' + fmt(cur.p) + ', denn ' + cur.k + ' × ' + fmt(t.d) + ' = ' + fmt(cur.prod) + '.', 'info'); }
      else { api.msg(tipp, 'no'); inp.select(); }
      return;
    }
    if (v !== cur.r) {
      t.tries++; api.fail(); inp.classList.add('no');
      if (t.tries < 2) { api.msg('Rechne die Subtraktion nochmals nach.', 'no'); inp.select(); return; }
      api.msg(fmt(cur.p) + ' − ' + fmt(cur.prod) + ' = ' + fmt(cur.r) + '.', 'info');
    } else api.msg(t.si + 1 < t.steps.length ? pick(LOB) + ' Die nächste Ziffer kommt herunter.' : pick(LOB), 'ok');
    t.si++; t.phase = 'k'; t.tries = 0; this.zeichne(t);
    if (t.si >= t.steps.length) { api.msg((t.err ? '' : pick(LOB) + ' ') + fmt(t.D) + ' : ' + fmt(t.d) + ' = <b>' + fmt(t.q) + (t.rest ? ' Rest ' + t.rest : '') + '</b>', t.err ? 'info' : 'ok'); api.done(); }
  }
};

/* ---------- Merkblätter (Theorie) nach den Merkblättern 5.5 ---------- */
function Lz(t) { return { t: t, k: 'l' }; }
function Cz(t) { return { t: t, k: 'c l' }; }
function zeile(segs, kl) {
  var o = '';
  segs.forEach(function (s) {
    if (typeof s === 'string') s = { t: s };
    for (var i = 0; i < s.t.length; i++) {
      var ch = s.t[i];
      o += '<span class="' + (s.k || '') + '">' + (ch === ' ' ? '' : ch) + '</span>';
    }
  });
  return '<div class="hz ' + (kl || '') + '">' + o + '</div>';
}
function divZeilen(D, d) {
  var dig = String(D).split('').map(Number), i = 0, p = 0, steps = [];
  while (i < dig.length && p < d) { p = p * 10 + dig[i]; i++; }
  for (;;) { var k = Math.floor(p / d); steps.push({ p: p, prod: k * d, r: p - k * d, end: i - 1 }); if (i >= dig.length) break; p = (p - k * d) * 10 + dig[i]; i++; }
  var q = Math.floor(D / d), r = D % d, L = dig.length, W = L + 1, rows = [];
  rows.push(zeile([' ' + String(D) + ':' + d + '=', Lz(String(q) + (r ? ' R' + r : ''))]));
  function leer() { var a = []; for (var j = 0; j < W; j++) a.push({ t: ' ' }); return a; }
  function setz(a, str, endCol, k) { for (var j = 0; j < str.length; j++) { var c = endCol - (str.length - 1 - j); a[c] = { t: str[j], k: k }; } return endCol - str.length + 1; }
  steps.forEach(function (st, s) {
    var pr = leer(), anf = setz(pr, String(st.prod), st.end + 1, 'l b u');
    pr[anf - 1] = { t: '−', k: 'l b u' };
    rows.push(zeile(pr));
    var rr = leer(), next = s + 1 < steps.length;
    setz(rr, next ? String(steps[s + 1].p) : String(st.r), next ? st.end + 2 : st.end + 1, 'l');
    rows.push(zeile(rr));
  });
  return rows.join('');
}
function strichSvg() {
  var y = 70, pts = [{ x: 560, v: '607 100' }, { x: 380, v: '597 100' }, { x: 230, v: '593 100' }, { x: 150, v: '593 070' }], sp = ['− 10 000', '− 4000', '− 30'];
  var h = '<svg viewBox="0 0 600 110" class="strich" role="img" aria-label="Rechenstrich"><line x1="20" y1="' + y + '" x2="590" y2="' + y + '" stroke="#1f2421" stroke-width="3"/>';
  pts.forEach(function (p, i) {
    h += '<line x1="' + p.x + '" y1="' + (y - 9) + '" x2="' + p.x + '" y2="' + (y + 9) + '" stroke="#1f2421" stroke-width="2.5"/>';
    h += '<text x="' + p.x + '" y="' + (y + 32) + '" text-anchor="middle" class="' + (i ? 'l' : '') + '">' + p.v + '</text>';
    if (i) {
      var a = pts[i - 1], m = (a.x + p.x) / 2;
      h += '<path d="M' + a.x + ' ' + (y - 5) + ' Q' + m + ' ' + (y - 58) + ' ' + p.x + ' ' + (y - 5) + '" fill="none" stroke="#d6ad45" stroke-width="2.5" class="l"/>';
      h += '<text x="' + m + '" y="' + (y - 36) + '" text-anchor="middle" class="l" fill="#a87c1f">' + sp[i - 1] + '</text>';
    }
  });
  return h + '</svg>';
}
var MB = {
  add: { titel: 'Addition / Subtraktion', kurz: 'Plus und Minus', sym: '+ −', bg: 'var(--leaf)',
    intro: 'Eine Addition ist eine Plusrechnung und eine Subtraktion eine Minusrechnung.',
    begriffe: [['Addition', 'g', ['3', '+', '5', '=', '8'], ['Summand', '', 'Summand', '', 'Summe']],
               ['Subtraktion', 'r', ['8', '−', '3', '=', '5'], ['Minuend', '', 'Subtrahend', '', 'Differenz']]],
    wege: [
      { lab: 'im Kopf', rows: [zeile(['28 + 7 = ', Lz('35')]), zeile(['420 − 390 = ', Lz('30')])] },
      { lab: 'mit Notizen', rows: [zeile(['274 + 123 = ', Lz('397')]), zeile(['200 + 100 = ', Lz('300')]), zeile([' 70 +  20 = ', Lz(' 90')]), zeile(['  4 +   3 = ', Lz('  7')])],
        tipp: 'Zerlege beide Zahlen nach Stellenwerten. Rechne Hunderter, Zehner und Einer einzeln und zähle am Schluss zusammen.' },
      { lab: 'Rechenstrich', rows: [zeile(['607100 − 14030']), zeile(['       = ', Lz('593070')])], svg: strichSvg(),
        tipp: 'Springe in Teilen: zuerst die Zehntausender, dann die Tausender, dann die Zehner.' },
      { lab: 'schriftlich', teile: [
          { rows: [zeile([' 2413']), zeile(['+ 832']), zeile([' ', Cz('1'), '   '], 'ul'), zeile([Lz(' 3245')], 'uu')], tipp: '4 + 8 = 12<br>→ schreibe 2<br>→ übertrage 1', farbe: 'g' },
          { rows: [zeile([' 3621']), zeile(['−2178']), zeile(['  ', Cz('1'), Cz('1'), ' '], 'ul'), zeile([Lz(' 1443')], 'uu')], tipp: '8 + ☐ = 11<br>→ schreibe 3<br>→ übertrage 1', farbe: 'r' }
        ] }
    ] },
  mal: { titel: 'Multiplikation', kurz: 'Mal', sym: '×', bg: 'var(--sky)',
    intro: 'Eine Multiplikation ist eine Malrechnung.',
    begriffe: [['Multiplikation', 'b', ['3', '•', '5', '=', '15'], ['Faktor', '', 'Faktor', '', 'Produkt']]],
    wege: [
      { lab: 'im Kopf', rows: [zeile([' 9 •  7 = ', Lz('63')]), zeile(['20 • 70 = ', Lz('1400')])] },
      { lab: '0-Trick', rows: [zeile(['40 • 600 = ', Lz('24000')])], tipp: 'Rechne ohne Nullen: 4 • 6 = 24. Dann hängst du alle Nullen an, hier 3.' },
      { lab: 'mit Notizen', rows: [zeile(['64 • 40 = ', Lz('2560')]), zeile(['60 • 40 = ', Lz('2400')]), zeile([' 4 • 40 = ', Lz(' 160')])] },
      { lab: 'schriftlich', teile: [
          { rows: [zeile([' 7•413']), zeile(['    ', Cz('2'), ' '], 'ul'), zeile([Lz('  2891')])], tipp: '7 • 3 = 21<br>→ schreibe 1<br>→ behalte 2', farbe: 'b' },
          { rows: [zeile(['70•413']), zeile(['      '], 'ul'), zeile([Lz(' 28910')])], tipp: 'Bei • 70 schreibst du zuerst die 0 und rechnest dann • 7.', farbe: 'b' },
          { rows: [zeile([' 56•2784']), zeile(['        '], 'ul'), zeile([{ t: '   16704', k: 'l g' }]), zeile([{ t: '  13920', k: 'l b' }, { t: '0', k: 'l m' }], 'ul'), zeile([Lz('  155904')], 'uu')],
            tipp: 'Bei zweistelligen Faktoren rechnet man mit den einzelnen Ziffern nacheinander (hier • 6 und • 50). Bei der Zehnerzahl darf hinten die 0 nicht vergessen werden, weil • 50 und nicht • 5 gerechnet wird.', farbe: 'b', breit: true }
        ] }
    ] },
  div: { titel: 'Division', kurz: 'Durch', sym: ':', bg: 'var(--sun)',
    intro: 'Eine Division ist eine Durchrechnung.',
    begriffe: [['Division', 'g', ['15', ':', '5', '=', '3'], ['Dividend', '', 'Divisor', '', 'Quotient']]],
    wege: [
      { lab: 'im Kopf', rows: [zeile(['  63 :  7 = ', Lz('9')]), zeile(['2700 : 90 = ', Lz('30')])] },
      { lab: '0-Trick', rows: [zeile(['2800 : 400 = ', Lz('7')]), zeile(['2000 : 500 = ', Lz('4')])], tipp: 'Bei beiden Zahlen gleich viele Nullen streichen: 28 : 4 = 7 und 20 : 5 = 4.' },
      { lab: 'mit Notizen', rows: [zeile(['84 : 4 = ', Lz('21')]), zeile(['80 : 4 = ', Lz('20')]), zeile([' 4 : 4 = ', Lz(' 1')])] },
      { lab: 'schriftlich', teile: [
          { rows: [divZeilen(45584, 7)], tipp: '4 durch 7 → geht nicht<br>45 durch 7 → 6-mal haben Platz<br>6 × 7 = 42<br>45 − 42 = 3 bleiben übrig<br>die 5 wird heruntergenommen<br>→ es geht weiter mit 35', farbe: 'r' },
          { rows: [divZeilen(45584, 12)], tipp: 'Bei einem zweistelligen Divisor kann man als Hilfe eine Multiplikationstabelle erstellen:<br>1 – 12, 2 – 24, 3 – 36, 4 – 48, 5 – 60, 6 – 72, 7 – 84, 8 – 96, 9 – 108', farbe: 'r' }
        ] }
    ] },
  flex: { titel: 'Flexibel rechnen', kurz: 'Flexibel rechnen', sym: '× 99', bg: 'var(--lila)',
    intro: 'Beim flexiblen Rechnen geht es darum, schneller zum Resultat zu gelangen, indem man Rechnungen geschickt vereinfacht.',
    begriffe: [],
    wege: [
      { lab: 'Verteilungsgesetz Multiplikation', rows: [zeile(['7•84 = (7•80)+(7•4)']), zeile(['     = ', Lz('560+28')]), zeile(['     = ', Lz('588')])] },
      { lab: 'Trick mit 9 / 99 / 999', rows: [zeile([' 9•142 = ', Lz('1420−142')]), zeile(['        = ', Lz('1278')]), zeile(['99•240 = ', Lz('24000−240')]), zeile(['        = ', Lz('23760')])],
        tipp: 'Mal 10, 100 oder 1000 rechnen und die Zahl einmal abziehen.' },
      { lab: 'Verteilungsgesetz Division', rows: [zeile(['594:6']), zeile(['  = (600:6)−(6:6)']), zeile(['  = ', Lz('100−1')]), zeile(['  = ', Lz('99')])] },
      { lab: 'Multiplizieren mit 5 / 50 / 500', rows: [zeile(['50•862 = ', Lz('86200:2')]), zeile(['       = ', Lz('43100')])], tipp: 'Mal 10, 100 oder 1000 rechnen und dann halbieren.' },
      { lab: 'Dividieren durch 5 / 50 / 500', rows: [zeile(['12000:50']), zeile(['  = ', Lz('24000:100')]), zeile(['  = ', Lz('240')])], tipp: 'Zuerst verdoppeln, dann durch 10, 100 oder 1000 teilen.' }
    ] }
};
var MB_ZURUECK = null;
function merkListe() {
  RUN = null;
  var o = '<div class="wrap">' + zurueck(RK.bereich ? 'Zurück' : 'Übersicht') + '<div class="kopf"><span class="ic" style="background:var(--sun);width:96px;height:96px;font-size:24px">Merk-<br>blatt</span><div class="tx"><h2>Merkblätter</h2><div class="unter">So rechnest du: alle Wege mit Beispielen</div></div></div><div class="grid">';
  Object.keys(MB).forEach(function (k) {
    var m = MB[k];
    o += '<button class="spiel" data-mb="' + k + '"><span class="ic" style="background:' + m.bg + '">' + m.sym + '</span><span class="t"><b>' + m.titel + '</b><span class="i">' + m.intro + '</span></span></button>';
  });
  app.innerHTML = o + '</div></div>'; scrollTo(0, 0);
  app.querySelector('[data-back]').onclick = heim;
  app.querySelectorAll('[data-mb]').forEach(function (b) { b.onclick = function () { merkblatt(b.dataset.mb, merkListe); }; });
}
function merkHTML(k) {
  var m = MB[k];
  var o = '<div class="mb-blatt"><div class="mb-kopf"><h2>' + m.titel + '</h2><div class="mb-sub">Merkblatt</div></div>' +
    '<p class="mb-intro">' + m.intro + '</p>';
  m.begriffe.forEach(function (b) {
    o += '<div class="begr ' + b[1] + '"><b>' + b[0] + '</b><div class="bz">' + b[2].map(function (z, i) { return '<span><i>' + z + '</i><small>' + b[3][i] + '</small></span>'; }).join('') + '</div></div>';
  });
  o += '<div class="mb-zeile"><p class="mb-intro">' + (k === 'flex' ? 'Diese Tricks helfen dir:' : 'Es gibt verschiedene Vorgehensweisen beim Lösen der Aufgaben:') + '</p><button class="go sun alle">Alle Lösungen zeigen</button></div>';
  m.wege.forEach(function (w, wi) {
    o += '<div class="weg zu" data-lab="' + w.lab + '"><div class="lab"><span>' + w.lab + '</span><button class="klein-k lsg">Lösung zeigen</button></div><div class="weg-in">';
    var teile = w.teile || [{ rows: w.rows, tipp: w.tipp, svg: w.svg, farbe: 'g' }];
    teile.forEach(function (t) {
      o += '<div class="teil' + (t.breit ? ' breit' : '') + '"><div class="karo">' + t.rows.join('') + (t.svg || '') + '</div>' + (t.tipp ? '<div class="mbtipp ' + (t.farbe || 'g') + '">' + t.tipp + '</div>' : '') + '</div>';
    });
    o += '</div></div>';
  });
  return o + '<div class="wichtig"><b>Wichtig:</b> ' + (k === 'flex' ? 'Schau dir zuerst die Zahlen genau an. Erst dann entscheidest du, welcher Weg am einfachsten ist.' : 'Beim schriftlichen Rechnen müssen immer die gleichen Stellenwerte untereinander stehen.') + '</div></div>';
}
function merkBind(root) {
  root.querySelectorAll('.weg').forEach(function (w) {
    var b = w.querySelector('.lsg');
    b.onclick = function () { var zu = w.classList.toggle('zu'); b.textContent = zu ? 'Lösung zeigen' : 'Lösung verstecken'; };
  });
  var alle = root.querySelector('.alle');
  alle.onclick = function () {
    var zeigen = alle.textContent.indexOf('zeigen') > 0;
    root.querySelectorAll('.weg').forEach(function (w) { w.classList.toggle('zu', !zeigen); w.querySelector('.lsg').textContent = zeigen ? 'Lösung verstecken' : 'Lösung zeigen'; });
    alle.textContent = zeigen ? 'Alle Lösungen verstecken' : 'Alle Lösungen zeigen';
  };
}
function merkblatt(k, zurueckZu) {
  RUN = null; MB_ZURUECK = zurueckZu || start;
  app.innerHTML = '<div class="wrap">' + zurueck() + merkHTML(k) + '</div>'; scrollTo(0, 0);
  app.querySelector('[data-back]').onclick = function () { MB_ZURUECK(); };
  merkBind(app);
}
/* Merkblatt als Fenster über der Übung: die Übung bleibt, wie sie ist */
function merkFenster(th) {
  if (!th) return;
  var ov = document.createElement('div'); ov.className = 'ovl'; ov.setAttribute('role', 'dialog'); ov.setAttribute('aria-label', 'Merkblatt');
  ov.innerHTML = '<div class="ovl-in"><button class="back" data-zu><img src="' + EULE + '" alt="">← Zurück zur Übung</button>' + merkHTML(th.mb) + '</div>';
  document.body.appendChild(ov); document.body.classList.add('ovl-offen');
  merkBind(ov);
  function zu() { ov.remove(); document.body.classList.remove('ovl-offen'); document.removeEventListener('keydown', esc, true); }
  function esc(e) { if (e.key === 'Escape') { e.stopPropagation(); zu(); } }
  document.addEventListener('keydown', esc, true);
  ov.querySelector('[data-zu]').onclick = zu;
  ov.onclick = function (e) { if (e.target === ov) zu(); };
  var ziel = th.weg ? ov.querySelector('.weg[data-lab="' + th.weg + '"]') : null;
  if (ziel) { ziel.classList.add('fokus'); setTimeout(function () { ziel.scrollIntoView({ block: 'start' }); }, 30); }
  ov.querySelector('[data-zu]').focus();
}
var BIRNE = '<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><path d="M9 18h6M10 21h4M12 3a6 6 0 0 0-3.6 10.8c.7.6 1.1 1.3 1.1 2.2h5c0-.9.4-1.6 1.1-2.2A6 6 0 0 0 12 3z" fill="#fbe7a1" stroke="#a87c1f" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>';

var APP_CSS = {"werkstatt": "\n/* Layout: kariertes Heftblatt; Übersicht mit drei Kacheln, jede öffnet eine eigene Übungsansicht */\n:host{\n  --paper:#e8f0fb; --paper2:#dce8f8; --tile:#dfe9f7; --grid:#cde2f6; --ink:#1d2b53; --ink-soft:#5b6890;\n  --pen:#2752c9; --red:#c9372b; --green:#1b8048; --mark:#ffd84a;\n  --wash1:#fff3c7; --wash2:#f0f6ff; --wash3:#dcf2e3; --card:#ffffff; --line:#c3cde3;\n  --display:\"Baloo 2\",\"Trebuchet MS\",system-ui,sans-serif;\n  --body:\"Andika\",\"Segoe UI\",system-ui,sans-serif;\n}\n\n*{box-sizing:border-box}\n.app{background:var(--paper);color:var(--ink);font-family:var(--body);font-size:17px;line-height:1.5;\n  background-image:linear-gradient(160deg,var(--paper) 0%,var(--paper2) 100%);background-attachment:fixed;min-height:100%;}\n.wrap{max-width:880px;margin:0 auto;padding-inline:16px;padding-block:28px 60px}\nh1,h2{font-family:var(--display);line-height:1.1;text-wrap:balance;margin:0}\nh1{font-size:clamp(2rem,6vw,3rem);font-weight:800}\nh2{font-size:clamp(1.6rem,5vw,2.2rem);font-weight:800}\n.lead{color:var(--ink-soft);max-width:60ch;margin:.4rem 0 0}\n.num{font-variant-numeric:tabular-nums;white-space:nowrap}\n\n/* Kacheln */\n.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:18px;margin-top:28px}\n.tile{all:unset;box-sizing:border-box;cursor:pointer;display:flex;flex-direction:column;gap:12px;padding:20px;border-radius:14px;\n  border:2px solid var(--ink);box-shadow:4px 4px 0 var(--ink);transition:transform .12s, box-shadow .12s;min-width:0}\n.tile:hover{transform:translate(-2px,-2px);box-shadow:6px 6px 0 var(--ink)}\n.tile:active{transform:translate(2px,2px);box-shadow:2px 2px 0 var(--ink)}\n.tile:focus-visible{outline:3px solid var(--pen);outline-offset:3px}\n.tile.t1{background:#fdf1d8} .tile.t2{background:#e3ecfb} .tile.t3{background:#e2f3e8}\n.tile .kicker{font-size:.8rem;text-transform:uppercase;letter-spacing:.08em;color:var(--ink-soft);font-weight:700}\n.tile h3{font-family:var(--display);font-size:1.6rem;margin:0;line-height:1}\n.tile p{margin:0;color:var(--ink-soft);font-size:.95rem}\n.preview{background:var(--card);border-radius:10px;border:1.5px solid var(--line);min-height:96px;display:grid;place-items:center;padding:10px;font-variant-numeric:tabular-nums}\n.preview .big{font-family:var(--display);font-size:1.5rem;font-weight:800}\n.preview svg{width:100%;height:auto;max-width:220px}\n.mini{display:grid;grid-template-columns:repeat(5,22px);font-size:1.05rem;line-height:22px;text-align:center}\n.mini .c{font-size:.7rem;color:var(--red);font-weight:700}\n.mini .ln{grid-column:1/-1;border-top:2px solid var(--ink);height:0}\n.go{font-weight:700;color:var(--pen)}\n\n/* Übungsansicht */\n.back{all:unset;cursor:pointer;font-weight:700;color:var(--pen);display:inline-flex;gap:6px;margin-bottom:14px}\n.back:focus-visible{outline:2px solid var(--pen);outline-offset:3px;border-radius:4px}\n.vhead{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:flex-end;gap:12px}\n.score{font-weight:700;background:var(--card);border:1.5px solid var(--line);border-radius:999px;padding:4px 14px;font-variant-numeric:tabular-nums}\n.bar{display:flex;flex-wrap:wrap;gap:10px 18px;align-items:center;margin:18px 0}\n.seg{display:inline-flex;border:2px solid var(--ink);border-radius:10px;overflow:hidden;background:var(--card)}\n.seg button{all:unset;cursor:pointer;padding:6px 12px;font-weight:700;font-size:.95rem}\n.seg button+button{border-left:2px solid var(--ink)}\n.seg button[aria-pressed=\"true\"]{background:var(--ink);color:var(--paper)}\n.seg button:focus-visible{outline:3px solid var(--pen);outline-offset:-3px}\n.bar label{font-size:.85rem;color:var(--ink-soft);font-weight:700;text-transform:uppercase;letter-spacing:.06em;margin-right:6px}\n.sheet{background:var(--card);border:2px solid var(--ink);border-radius:14px;padding:22px;box-shadow:4px 4px 0 var(--ink)}\n.btns{display:flex;flex-wrap:wrap;gap:10px;margin-top:18px}\n.btn{all:unset;cursor:pointer;padding:9px 18px;border-radius:10px;border:2px solid var(--ink);font-weight:700;background:var(--card)}\n.btn.primary{background:var(--pen);border-color:var(--pen);color:var(--paper)}\n.btn:focus-visible{outline:3px solid var(--mark);outline-offset:2px}\n.btn:hover{filter:brightness(1.06)}\n.msg{margin-top:16px;padding:10px 14px;border-radius:10px;font-weight:700;min-height:1.5em}\n.msg:empty{display:none}\n.msg.ok{background:var(--wash3);color:var(--green)}\n.msg.bad{background:color-mix(in srgb,var(--red) 14%,var(--card));color:var(--red)}\n.msg.info{background:var(--wash1);color:var(--ink)}\n.note{color:var(--ink-soft);font-size:.92rem;margin:14px 0 0;max-width:62ch}\n\ninput.cell, input.field{font:inherit;color:var(--ink);background:var(--paper);border:2px solid var(--line);border-radius:8px;text-align:center;font-variant-numeric:tabular-nums}\ninput:focus{outline:none;border-color:var(--pen);box-shadow:0 0 0 3px color-mix(in srgb,var(--pen) 25%,transparent)}\ninput.ok{border-color:var(--green);background:var(--wash3)}\ninput.bad{border-color:var(--red);background:color-mix(in srgb,var(--red) 12%,var(--paper))}\ninput.shown{color:var(--ink-soft);border-style:dashed}\n\n/* Kopfrechnen */\n.dots{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:18px}\n.dot{width:14px;height:14px;border-radius:50%;border:2px solid var(--ink-soft)}\n.dot.now{border-color:var(--pen);background:color-mix(in srgb,var(--pen) 25%,transparent)}\n.dot.ok{background:var(--green);border-color:var(--green)}\n.dot.bad{background:var(--red);border-color:var(--red)}\n.task{font-family:var(--display);font-weight:800;font-size:clamp(1.6rem,6vw,2.6rem);display:flex;flex-wrap:wrap;align-items:center;gap:.3em;font-variant-numeric:tabular-nums}\n.task input.field{font-family:var(--display);font-weight:800;font-size:inherit;width:6.2em;padding:0 .2em}\n\n/* Rechenstrich */\n.svgbox{overflow-x:auto;margin:6px -6px 10px}\n.svgbox svg{display:block;width:100%;min-width:520px;height:auto}\n.rs-line{stroke:var(--ink);stroke-width:3}\n.rs-tick{stroke:var(--ink);stroke-width:2.5}\n.rs-arc{fill:none;stroke:var(--pen);stroke-width:2.5}\n.rs-arc.ok{stroke:var(--green)} .rs-arc.bad{stroke:var(--red)}\n.rs-arrow{fill:var(--pen)}\n.rs-lbl{fill:var(--ink);font:700 15px var(--body);font-variant-numeric:tabular-nums}\n.rs-jmp{fill:var(--pen);font:700 15px var(--body)}\n.rs-start{fill:var(--ink);font:800 17px var(--display)}\n.rows{display:grid;gap:10px}\n.row{display:flex;align-items:center;gap:8px;flex-wrap:wrap}\n.row .op{font-family:var(--display);font-weight:800;font-size:1.4rem;width:1em;text-align:center}\n.row input.field{width:8.5em;padding:6px 8px;font-size:1.05rem}\n.row .arrow{color:var(--ink-soft);font-weight:700}\n.row .lab{font-size:.75rem;color:var(--ink-soft);text-transform:uppercase;letter-spacing:.06em;width:100%;margin-bottom:-6px}\n.row input.given{background:var(--wash2);border-style:dashed;color:var(--pen);font-weight:700}\n.row .x{all:unset;cursor:pointer;color:var(--ink-soft);font-weight:700;padding:4px 8px;border-radius:6px}\n.row .x:hover{color:var(--red)}\n.row .x:focus-visible{outline:2px solid var(--pen)}\n\n/* Schriftlich */\n.written{overflow-x:auto;padding:4px 0}\n.wgrid{display:grid;gap:0;width:max-content;margin:0 auto;font-size:1.6rem;font-variant-numeric:tabular-nums}\n.wgrid > div{width:2.3rem;height:2.3rem;display:grid;place-items:center}\n.wgrid .head{font-size:.7rem;font-weight:700;color:var(--ink-soft);height:1.4rem;letter-spacing:.04em}\n.wgrid .opc{font-family:var(--display);font-weight:800}\n.wgrid .carry{height:1.9rem;border-bottom:3px solid var(--ink)}\n.wgrid .carry.nl{border-bottom-color:var(--ink)}\n.wgrid input.cell{width:2rem;height:2rem;font-size:1.4rem;padding:0}\n.wgrid input.cc{width:1.45rem;height:1.45rem;font-size:.9rem;font-weight:700;color:var(--red);border-radius:6px;padding:0}\n.wgrid .res{padding-top:6px;height:2.7rem}\n.legend{display:flex;flex-wrap:wrap;gap:6px 16px;font-size:.88rem;color:var(--ink-soft);margin-top:10px;justify-content:center}\n.legend b{color:var(--red)}\n\n@media (max-width:480px){\n  .sheet{padding:16px}\n  .wgrid > div{width:2.05rem}\n  .wgrid input.cell{width:1.8rem}\n}\n@media (prefers-reduced-motion:reduce){.tile{transition:none}}\n", "mal": "\n/* Layout: kariertes Heftblatt wie die Plus & Minus Werkstatt; Übersicht mit zwei Kacheln, jede öffnet eine Übungsansicht */\n:host{\n  --paper:#e4eef9; --grid:#c4dcf3; --sky1:#d8e7f7; --sky2:#ecf3fb; --tile1:#fdeee3; --tile2:#e6f4ea; --ink:#1d2b53; --ink-soft:#5b6890;\n  --pen:#2752c9; --red:#c9372b; --green:#1b8048; --mark:#ffd84a;\n  --wash1:#fff3c7; --wash2:#dfeaff; --wash3:#dcf2e3; --card:#ffffff; --line:#c3cde3;\n  --pe:#1b8048; --pz:#2752c9; --ph:#8a3fb8; --we:#dcf2e3; --wz:#dfeaff; --wh:#efe2f8;\n  --display:\"Baloo 2\",\"Trebuchet MS\",system-ui,sans-serif;\n  --body:\"Andika\",\"Segoe UI\",system-ui,sans-serif;\n}\n\n\n\n*{box-sizing:border-box}\n.app{background:var(--paper);color:var(--ink);font-family:var(--body);font-size:17px;line-height:1.5;\n  background-image:linear-gradient(160deg,var(--sky1) 0%,var(--sky2) 100%);background-attachment:fixed;min-height:100vh}\n.wrap{max-width:880px;margin:0 auto;padding-inline:16px;padding-block:28px 60px}\nh1,h2{font-family:var(--display);line-height:1.1;text-wrap:balance;margin:0}\nh1{font-size:clamp(2rem,6vw,3rem);font-weight:800}\nh2{font-size:clamp(1.6rem,5vw,2.2rem);font-weight:800}\n.lead{color:var(--ink-soft);max-width:60ch;margin:.4rem 0 0}\n.hl{background:linear-gradient(transparent 55%,var(--mark) 55%);padding:0 .1em;color:var(--ink)}\n\n\n.num{font-variant-numeric:tabular-nums;white-space:nowrap}\n\n/* Kacheln */\n.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:18px;margin-top:28px}\n.tile{all:unset;box-sizing:border-box;cursor:pointer;display:flex;flex-direction:column;gap:12px;padding:20px;border-radius:14px;\n  border:2px solid var(--ink);box-shadow:4px 4px 0 var(--ink);transition:transform .12s, box-shadow .12s;min-width:0}\n.tile:hover{transform:translate(-2px,-2px);box-shadow:6px 6px 0 var(--ink)}\n.tile:active{transform:translate(2px,2px);box-shadow:2px 2px 0 var(--ink)}\n.tile:focus-visible{outline:3px solid var(--pen);outline-offset:3px}\n.tile.t1{background:var(--tile1)} .tile.t2{background:var(--tile2)}\n.tile .kicker{font-size:.8rem;text-transform:uppercase;letter-spacing:.08em;color:var(--ink-soft);font-weight:700}\n.tile h3{font-family:var(--display);font-size:1.6rem;margin:0;line-height:1}\n.tile p{margin:0;color:var(--ink-soft);font-size:.95rem}\n.preview{background:var(--card);border-radius:10px;border:1.5px solid var(--line);min-height:110px;display:grid;place-items:center;padding:10px;font-variant-numeric:tabular-nums}\n.preview .big{font-family:var(--display);font-size:1.5rem;font-weight:800;text-align:center;line-height:1.3}\n.preview .big small{display:block;font-family:var(--body);font-weight:700;font-size:.85rem;color:var(--ink-soft)}\n.mini{display:grid;grid-template-columns:repeat(7,20px);font-size:1rem;line-height:20px;text-align:center}\n.mini .e{color:var(--pe);font-weight:700} .mini .z{color:var(--pz);font-weight:700}\n.mini .ln{grid-column:1/-1;border-top:2px solid var(--ink);height:0;margin:2px 0}\n.go{font-weight:700;color:var(--pen)}\n\n/* Übungsansicht */\n.back{all:unset;cursor:pointer;font-weight:700;color:var(--pen);display:inline-flex;gap:6px;margin-bottom:14px}\n.back:focus-visible{outline:2px solid var(--pen);outline-offset:3px;border-radius:4px}\n.vhead{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:flex-end;gap:12px}\n.score{font-weight:700;background:var(--card);border:1.5px solid var(--line);border-radius:999px;padding:4px 14px;font-variant-numeric:tabular-nums}\n.bar{display:flex;flex-wrap:wrap;gap:10px 18px;align-items:center;margin:18px 0}\n.seg{display:inline-flex;border:2px solid var(--ink);border-radius:10px;overflow:hidden;background:var(--card)}\n.seg button{all:unset;cursor:pointer;padding:6px 12px;font-weight:700;font-size:.95rem}\n.seg button+button{border-left:2px solid var(--ink)}\n.seg button[aria-pressed=\"true\"]{background:var(--ink);color:var(--paper)}\n.seg button:focus-visible{outline:3px solid var(--pen);outline-offset:-3px}\n.bar label{font-size:.85rem;color:var(--ink-soft);font-weight:700;text-transform:uppercase;letter-spacing:.06em;margin-right:6px}\n.sheet{background:var(--card);border:2px solid var(--ink);border-radius:14px;padding:22px;box-shadow:4px 4px 0 var(--ink)}\n.btns{display:flex;flex-wrap:wrap;gap:10px;margin-top:18px}\n.btn{all:unset;cursor:pointer;padding:9px 18px;border-radius:10px;border:2px solid var(--ink);font-weight:700;background:var(--card)}\n.btn.primary{background:var(--pen);border-color:var(--pen);color:var(--paper)}\n.btn:focus-visible{outline:3px solid var(--mark);outline-offset:2px}\n.btn:hover{filter:brightness(1.06)}\n.msg{margin-top:16px;padding:10px 14px;border-radius:10px;font-weight:700;min-height:1.5em}\n.msg:empty{display:none}\n.msg.ok{background:var(--wash3);color:var(--green)}\n.msg.bad{background:color-mix(in srgb,var(--red) 14%,var(--card));color:var(--red)}\n.msg.info{background:var(--wash1);color:var(--ink)}\n.note{color:var(--ink-soft);font-size:.92rem;margin:14px 0 0;max-width:62ch}\n\ninput.cell, input.field{font:inherit;color:var(--ink);background:var(--card);border:2px solid var(--line);border-radius:8px;text-align:center;font-variant-numeric:tabular-nums}\ninput:focus{outline:none;border-color:var(--pen);box-shadow:0 0 0 3px color-mix(in srgb,var(--pen) 25%,transparent)}\ninput.ok{border-color:var(--green);background:var(--wash3)}\ninput.bad{border-color:var(--red);background:color-mix(in srgb,var(--red) 12%,var(--paper))}\ninput.shown{color:var(--ink-soft);border-style:dashed}\n\n/* Nullentrick (Kopf) */\n.dots{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:18px}\n.dot{width:14px;height:14px;border-radius:50%;border:2px solid var(--ink-soft)}\n.dot.now{border-color:var(--pen);background:color-mix(in srgb,var(--pen) 25%,transparent)}\n.dot.ok{background:var(--green);border-color:var(--green)}\n.dot.bad{background:var(--red);border-color:var(--red)}\n.task{font-family:var(--display);font-weight:800;font-size:clamp(1.6rem,6vw,2.6rem);display:flex;flex-wrap:wrap;align-items:center;gap:.3em;font-variant-numeric:tabular-nums}\n.task input.field{font-family:var(--display);font-weight:800;font-size:inherit;width:6.2em;padding:0 .2em}\n\n/* Schriftlich */\n.written{overflow-x:auto;padding:4px 0}\n.wgrid{display:grid;gap:0;width:max-content;margin:0 auto;font-size:1.6rem;font-variant-numeric:tabular-nums}\n.wgrid > div{width:2.3rem;height:2.3rem;display:grid;place-items:center}\n.wgrid .mcr{height:1.9rem}\n.wgrid input.cc.t0{color:var(--pe)} .wgrid input.cc.t1{color:var(--pz)} .wgrid input.cc.t2{color:var(--ph)}\n.wgrid .opc{font-family:var(--display);font-weight:800}\n.wgrid .now{background:var(--mark);color:#1d2b53;border-radius:6px}\n.wgrid .pp{height:2.6rem}\n.wgrid .carry{height:1.9rem;border-bottom:3px solid var(--ink)}\n.wgrid input.cell{width:2rem;height:2rem;font-size:1.4rem;padding:0}\n.wgrid input.cc{width:1.45rem;height:1.45rem;font-size:.9rem;font-weight:700;color:var(--red);border-radius:6px;padding:0}\n.wgrid .res{padding-top:6px;height:2.7rem}\n.p0{color:var(--pe)} .p1{color:var(--pz)} .p2{color:var(--ph)}\n.wgrid .ex.p0,.wgrid .ex.p1,.wgrid .ex.p2{font-weight:800}\n.wgrid .zero{font-weight:700;opacity:.7}\n.wgrid input.t0{color:var(--pe);background:var(--we);border-color:color-mix(in srgb,var(--pe) 40%,var(--line))}\n.wgrid input.t1{color:var(--pz);background:var(--wz);border-color:color-mix(in srgb,var(--pz) 40%,var(--line))}\n.wgrid input.t2{color:var(--ph);background:var(--wh);border-color:color-mix(in srgb,var(--ph) 40%,var(--line))}\n.wgrid input.cell:focus{border-color:var(--pen)}\n.wgrid input.cell.ok{border-color:var(--green);background:var(--wash3)}\n.wgrid input.cell.bad{border-color:var(--red);background:color-mix(in srgb,var(--red) 12%,var(--paper))}\n.wgrid input.shown{border-style:dashed}\n.tag{font-family:var(--display);font-weight:800;font-size:.85rem;width:1.6rem;height:1.6rem;border-radius:50%;display:grid;place-items:center;color:var(--card)}\n.tag.t0{background:var(--pe)} .tag.t1{background:var(--pz)} .tag.t2{background:var(--ph)}\n.sw{display:inline-block;width:.8em;height:.8em;border-radius:3px;margin-right:5px;vertical-align:-1px}\n.sw.t0{background:var(--pe)} .sw.t1{background:var(--pz)} .sw.t2{background:var(--ph)}\n.legend{display:flex;flex-wrap:wrap;gap:6px 16px;font-size:.88rem;color:var(--ink-soft);margin-top:10px;justify-content:center}\n.legend b{color:var(--red)}\n\n@media (max-width:480px){\n  .sheet{padding:16px}\n  .wgrid > div{width:2.05rem}\n  .wgrid input.cell{width:1.8rem}\n}\n@media (prefers-reduced-motion:reduce){.tile{transition:none}}\n", "durch": "\n/* Layout: kariertes Heftblatt wie «Multiplizieren üben»; Übersicht mit zwei Kacheln, jede öffnet eine Übungsansicht */\n:host{\n  --paper:#fbfcfe; --grid:#c4ddf4; --bg:#dfe9f6; --bg2:#e8eff9; --tile1:#faede4; --tile2:#e8f3ea; --ink:#1d2b53; --ink-soft:#5b6890;\n  --pen:#2752c9; --red:#c9372b; --green:#1b8048; --mark:#ffd84a;\n  --wash1:#fff3c7; --wash2:#dfeaff; --wash3:#dcf2e3; --card:#ffffff; --line:#c3cde3;\n  --pe:#1b8048; --pz:#2752c9; --ph:#8a3fb8; --we:#dcf2e3; --wz:#dfeaff; --wh:#efe2f8;\n  --display:\"Baloo 2\",\"Trebuchet MS\",system-ui,sans-serif;\n  --body:\"Andika\",\"Segoe UI\",system-ui,sans-serif;\n}\n\n\n\n*{box-sizing:border-box}\n.app{background-color:var(--bg);color:var(--ink);font-family:var(--body);font-size:17px;line-height:1.5;\n  background-image:linear-gradient(160deg,var(--bg),var(--bg2));background-attachment:fixed;min-height:100%;}\n.wrap{max-width:880px;margin:0 auto;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));padding-block:28px 60px}\nh1,h2{font-family:var(--display);line-height:1.1;text-wrap:balance;margin:0}\nh1{font-size:clamp(2rem,6vw,3rem);font-weight:800}\nh2{font-size:clamp(1.6rem,5vw,2.2rem);font-weight:800}\n.lead{color:var(--ink-soft);max-width:60ch;margin:.4rem 0 0}\n.hl-t{color:inherit}\n.num{font-variant-numeric:tabular-nums;white-space:nowrap}\n\n/* Kacheln */\n.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:18px;margin-top:28px}\n.tile{all:unset;box-sizing:border-box;cursor:pointer;display:flex;flex-direction:column;gap:12px;padding:20px;border-radius:14px;\n  border:2px solid var(--ink);box-shadow:4px 4px 0 var(--ink);transition:transform .12s, box-shadow .12s;min-width:0}\n.tile:hover{transform:translate(-2px,-2px);box-shadow:6px 6px 0 var(--ink)}\n.tile:active{transform:translate(2px,2px);box-shadow:2px 2px 0 var(--ink)}\n.tile:focus-visible{outline:3px solid var(--pen);outline-offset:3px}\n.tile.t1{background:var(--tile1)} .tile.t2{background:var(--tile2)}\n.tile .kicker{font-size:.8rem;text-transform:uppercase;letter-spacing:.08em;color:var(--ink-soft);font-weight:700}\n.tile h3{font-family:var(--display);font-size:1.6rem;margin:0;line-height:1}\n.tile p{margin:0;color:var(--ink-soft);font-size:.95rem}\n.preview{background:var(--card);border-radius:10px;border:1.5px solid var(--line);min-height:150px;display:grid;place-items:center;padding:10px;font-variant-numeric:tabular-nums}\n.preview .big{font-family:var(--display);font-size:1.4rem;font-weight:800;text-align:center;line-height:1.3}\n.preview .big small{display:block;font-family:var(--body);font-weight:700;font-size:.85rem;color:var(--ink-soft)}\n.preview .strk{text-decoration:line-through;text-decoration-color:var(--red);text-decoration-thickness:3px;color:var(--ink-soft)}\n.mini{display:grid;grid-template-columns:repeat(10,17px);font-size:.95rem;line-height:19px;text-align:center}\n.mini .ul{border-bottom:2px solid var(--ink)}\n.mini .q{color:var(--pe);font-weight:700} .mini .p{color:var(--pz);font-weight:700} .mini .d{color:var(--ph);font-weight:700}\n.go{font-weight:700;color:var(--pen)}\n\n/* Übungsansicht */\n.back{all:unset;cursor:pointer;font-weight:700;color:var(--pen);display:inline-flex;gap:6px;margin-bottom:14px}\n.back:focus-visible{outline:2px solid var(--pen);outline-offset:3px;border-radius:4px}\n.vhead{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:flex-end;gap:12px}\n.score{font-weight:700;background:var(--card);border:1.5px solid var(--line);border-radius:999px;padding:4px 14px;font-variant-numeric:tabular-nums}\n.bar{display:flex;flex-wrap:wrap;gap:10px 18px;align-items:center;margin:18px 0}\n.seg{display:inline-flex;border:2px solid var(--ink);border-radius:10px;overflow:hidden;background:var(--card);flex-wrap:wrap}\n.seg button{all:unset;cursor:pointer;padding:6px 12px;font-weight:700;font-size:.95rem}\n.seg button+button{border-left:2px solid var(--ink)}\n.seg button[aria-pressed=\"true\"]{background:var(--ink);color:var(--paper)}\n.seg button:focus-visible{outline:3px solid var(--pen);outline-offset:-3px}\n.bar label{font-size:.85rem;color:var(--ink-soft);font-weight:700;text-transform:uppercase;letter-spacing:.06em;margin-right:6px}\n.sheet{background:var(--card);border:2px solid var(--ink);border-radius:14px;padding:22px;box-shadow:4px 4px 0 var(--ink)}\n.btns{display:flex;flex-wrap:wrap;gap:10px;margin-top:18px}\n.btn{all:unset;cursor:pointer;padding:9px 18px;border-radius:10px;border:2px solid var(--ink);font-weight:700;background:var(--card)}\n.btn.primary{background:var(--pen);border-color:var(--pen);color:var(--paper)}\n.btn:focus-visible{outline:3px solid var(--mark);outline-offset:2px}\n.btn:hover{filter:brightness(1.06)}\n.msg{margin-top:16px;padding:10px 14px;border-radius:10px;font-weight:700;min-height:1.5em}\n.msg:empty{display:none}\n.msg.ok{background:var(--wash3);color:var(--green)}\n.msg.bad{background:color-mix(in srgb,var(--red) 14%,var(--card));color:var(--red)}\n.msg.info{background:var(--wash1);color:var(--ink)}\n.note{color:var(--ink-soft);font-size:.92rem;margin:14px 0 0;max-width:62ch}\n\ninput.cell, input.field{font:inherit;color:var(--ink);background:var(--paper);border:2px solid var(--line);border-radius:8px;text-align:center;font-variant-numeric:tabular-nums}\ninput:focus{outline:none;border-color:var(--pen);box-shadow:0 0 0 3px color-mix(in srgb,var(--pen) 25%,transparent)}\ninput.ok{border-color:var(--green);background:var(--wash3)}\ninput.bad{border-color:var(--red);background:color-mix(in srgb,var(--red) 12%,var(--paper))}\ninput.shown{color:var(--ink-soft);border-style:dashed}\n\n/* Nullentrick (Kopf) */\n.dots{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:18px}\n.dot{width:14px;height:14px;border-radius:50%;border:2px solid var(--ink-soft)}\n.dot.now{border-color:var(--pen);background:color-mix(in srgb,var(--pen) 25%,transparent)}\n.dot.ok{background:var(--green);border-color:var(--green)}\n.dot.bad{background:var(--red);border-color:var(--red)}\n.task{font-family:var(--display);font-weight:800;font-size:clamp(1.6rem,6vw,2.6rem);display:flex;flex-wrap:wrap;align-items:center;gap:.3em;font-variant-numeric:tabular-nums}\n.task input.field{font-family:var(--display);font-weight:800;font-size:inherit;width:6.2em;padding:0 .2em}\n.task .z-strk{color:var(--red);text-decoration:line-through;text-decoration-thickness:4px}\n.task .z-fade{color:var(--ink-soft);opacity:.45}\n.core{margin-top:12px;font-weight:700;display:flex;flex-wrap:wrap;gap:6px 14px;align-items:center}\n.chip{display:inline-flex;align-items:center;gap:6px;padding:3px 12px;border-radius:999px;font-size:.95rem;border:1.5px solid var(--line);background:var(--paper)}\n.chip.s{border-color:var(--red);color:var(--red)}\n.chip.c{border-color:var(--pen);color:var(--pen)}\n.chip.f{color:var(--ink-soft)}\n.task input.field.bad{text-decoration:line-through;text-decoration-color:var(--red);width:4.5em}\n.task .sol{color:var(--green);background:var(--wash3);border:2px solid var(--green);border-radius:8px;padding:0 .3em}\n\n/* Schriftlich */\n.step{display:flex;gap:12px;align-items:flex-start;background:var(--wash1);border-radius:10px;padding:10px 14px;margin-bottom:18px;font-weight:700}\n.step .nr{font-family:var(--display);font-weight:800;font-size:.85rem;white-space:nowrap;background:var(--ink);color:var(--paper);border-radius:999px;padding:1px 10px;margin-top:2px}\n.step.done{background:var(--wash3);color:var(--green)}\n.written{overflow-x:auto;padding:4px 0 8px}\n.dgrid{display:grid;grid-auto-rows:2.5rem;width:max-content;margin:0 auto;font-size:1.6rem;font-variant-numeric:tabular-nums}\n.dgrid > div{width:2.3rem;display:grid;place-items:center}\n.dgrid .ex{font-weight:700}\n.dgrid .op{font-family:var(--display);font-weight:800}\n.dgrid .ul{border-bottom:3px solid var(--ink)}\n.dgrid .fut{visibility:hidden}\n.dgrid .mi{font-family:var(--display);font-weight:800;color:var(--pz)}\n.dgrid .rlab{font-family:var(--display);font-weight:800;color:var(--red);font-size:1.3rem}\n.dgrid input.cell{width:2rem;height:2rem;font-size:1.4rem;padding:0}\n.dgrid input.tq{color:var(--pe);background:var(--we);border-color:color-mix(in srgb,var(--pe) 40%,var(--line))}\n.dgrid input.tp{color:var(--pz);background:var(--wz);border-color:color-mix(in srgb,var(--pz) 40%,var(--line))}\n.dgrid input.td{color:var(--ph);background:var(--wh);border-color:color-mix(in srgb,var(--ph) 40%,var(--line))}\n.dgrid input.tr{color:var(--red)}\n.dgrid input[readonly]{cursor:default}\n.dgrid input.ok{border-color:var(--green)}\n.dgrid input.bad{border-color:var(--red);background:color-mix(in srgb,var(--red) 12%,var(--paper))}\n.dgrid input.cur{border-color:var(--pen);border-width:3px;box-shadow:0 0 0 3px color-mix(in srgb,var(--pen) 25%,transparent)}\n.dgrid .hl, .dgrid input.hl{background:var(--mark);color:#1d2b53;border-radius:6px}\n.sw{display:inline-block;width:.8em;height:.8em;border-radius:3px;margin-right:5px;vertical-align:-1px}\n.sw.q{background:var(--pe)} .sw.p{background:var(--pz)} .sw.d{background:var(--ph)} .sw.m{background:var(--mark)}\n.legend{display:flex;flex-wrap:wrap;gap:6px 16px;font-size:.88rem;color:var(--ink-soft);margin-top:10px;justify-content:center}\n\n@media (max-width:480px){\n  .sheet{padding:16px}\n  .dgrid{font-size:1.35rem;grid-auto-rows:2.2rem}\n  .dgrid > div{width:1.95rem}\n  .dgrid input.cell{width:1.75rem;height:1.8rem;font-size:1.2rem}\n}\n@media (prefers-reduced-motion:reduce){.tile{transition:none}}\n", "flex": "\n/* Layout: kariertes Heftblatt wie «Multiplizieren üben» und «Dividieren üben»; Übersicht mit fünf Trick-Kacheln, jede öffnet eine Schritt-für-Schritt-Präsentation mit «Jetzt du» */\n:host{\n  --paper:#e6f0fc; --grid:#e1e8f4; --ink:#1d2b53; --ink-soft:#5b6890;\n  --pen:#2752c9; --red:#c9372b; --green:#1b8048; --mark:#ffd84a;\n  --wash1:#fff3c7; --wash2:#dfeaff; --wash3:#dcf2e3; --wash4:#efe2f8; --card:#ffffff; --line:#c3cde3;\n  --c1:#2752c9; --c2:#1b8048;\n  --display:\"Baloo 2\",\"Trebuchet MS\",system-ui,sans-serif;\n  --body:\"Andika\",\"Segoe UI\",system-ui,sans-serif;\n  --title:\"Fredoka\",\"Baloo 2\",\"Trebuchet MS\",system-ui,sans-serif;\n}\n\n\n\n*{box-sizing:border-box}\n.app{background:var(--paper);color:var(--ink);font-family:var(--body);font-size:17px;line-height:1.5}\n.wrap{max-width:980px;margin:0 auto;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));padding-block:16px 16px}\nh1,h2,h3{font-family:var(--title);font-weight:400;line-height:1.1;text-wrap:balance;margin:0}\nh1{font-size:clamp(1.8rem,5vw,2.6rem)}\nh2{font-size:clamp(1.35rem,3.6vw,1.9rem)}\n.lead{color:var(--ink-soft);max-width:70ch;margin:.3rem 0 0;font-size:.95rem}\n.hl-t{background:linear-gradient(transparent 55%,var(--mark) 55%);padding:0 .1em;color:var(--ink)}\n\n\n.num{font-variant-numeric:tabular-nums;white-space:nowrap}\ni.c1{font-style:normal;color:var(--c1);font-weight:800}\ni.c2{font-style:normal;color:var(--c2);font-weight:800}\n.strk{color:var(--red);text-decoration:line-through;text-decoration-thickness:.12em}\n\n/* Kacheln */\n.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:14px;margin-top:8px}\n.group{margin-top:16px}\n.group h2{font-size:clamp(1.2rem,3.4vw,1.5rem)}\n.tile{all:unset;box-sizing:border-box;cursor:pointer;display:flex;flex-direction:column;gap:7px;padding:13px 15px;border-radius:14px;\n  border:2px solid var(--ink);box-shadow:4px 4px 0 var(--ink);transition:transform .12s, box-shadow .12s;min-width:0}\n.tile:hover{transform:translate(-2px,-2px);box-shadow:6px 6px 0 var(--ink)}\n.tile:active{transform:translate(2px,2px);box-shadow:2px 2px 0 var(--ink)}\n.tile:focus-visible{outline:3px solid var(--pen);outline-offset:3px}\n.tile.w1{background:var(--wash1)} .tile.w2{background:var(--wash2)} .tile.w3{background:var(--wash3)} .tile.w4{background:var(--wash4)}\n.kicker{font-size:.8rem;text-transform:uppercase;letter-spacing:.08em;color:var(--ink-soft);font-weight:700}\n.tile h3{font-size:1.2rem}\n.tile p{margin:0;color:var(--ink-soft);font-size:.86rem;line-height:1.35}\n.preview{background:var(--card);border-radius:10px;border:1.5px solid var(--line);padding:7px 8px;text-align:center;font-family:var(--display);font-weight:800;font-size:1rem;line-height:1.3;font-variant-numeric:tabular-nums}\n.preview small{display:block;font-family:var(--body);font-weight:700;font-size:.82rem;color:var(--ink-soft)}\n.go{font-weight:700;color:var(--pen);margin-top:auto}\n\n/* Präsentation */\n.back{all:unset;cursor:pointer;font-weight:700;color:var(--pen);display:inline-flex;gap:6px}\n.topbar{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:8px 16px;margin-bottom:8px}\n.seg{display:inline-flex;border:2px solid var(--ink);border-radius:10px;overflow:hidden;background:var(--card)}\n.seg button{all:unset;cursor:pointer;padding:5px 16px;font-weight:700;font-size:.95rem;color:var(--ink)}\n.seg button+button{border-left:2px solid var(--ink)}\n.seg button[aria-pressed=\"true\"]{background:var(--ink);color:var(--paper)}\n.seg button:focus-visible{outline:3px solid var(--pen);outline-offset:-3px}\n.choose{display:flex;flex-wrap:wrap;align-items:center;gap:8px 28px;margin-top:8px}\n.cgroup{display:inline-flex;flex-wrap:wrap;align-items:center;gap:6px 10px}\n.cgroup[hidden]{display:none}\n.back:focus-visible{outline:2px solid var(--pen);outline-offset:3px;border-radius:4px}\n.vhead{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:flex-end;gap:10px 16px}\n.vhead .kicker{display:block;margin-bottom:2px}\n.pill{font-weight:700;background:var(--card);border:1.5px solid var(--line);border-radius:999px;padding:4px 14px;font-variant-numeric:tabular-nums;white-space:nowrap}\n.sheet{background:var(--card);border:2px solid var(--ink);border-radius:14px;padding:16px 20px;box-shadow:4px 4px 0 var(--ink);margin-top:10px}\n.dots{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:8px}\n.dot{all:unset;cursor:pointer;width:16px;height:16px;border-radius:50%;border:2px solid var(--ink-soft)}\n.dot.done{background:var(--ink-soft)}\n.dot.now{border-color:var(--pen);background:var(--pen)}\n.dot:focus-visible{outline:3px solid var(--mark);outline-offset:2px}\n\n.boardwrap{overflow-x:auto;padding:6px 2px 10px}\n.board{display:grid;grid-template-columns:max-content max-content max-content;column-gap:.45em;row-gap:.25em;width:max-content;min-width:0;\n  font-family:var(--display);font-weight:600;font-size:clamp(1.3rem,min(4.4vw,4.8vh),2.4rem);line-height:1.3;font-variant-numeric:tabular-nums}\n.board .l{text-align:right;white-space:nowrap}\n.board .o{text-align:center;color:var(--ink-soft)}\n.board .r{white-space:nowrap}\n.board.ralign .r{text-align:right}\n.board .ul{border-bottom:3px solid var(--ink)}\n.board .aside{grid-column:1/-1;font-family:var(--body);font-weight:700;font-size:.55em;background:var(--wash2);border-radius:10px;padding:.35em .8em;justify-self:start;margin:.15em 0 .3em}\n.board .hot{background:color-mix(in srgb,var(--mark) 45%,transparent);border-radius:6px}\n.board .hot.aside{background:var(--wash1)}\n@media (prefers-reduced-motion:no-preference){.board .hot{animation:pop .45s ease-out}}\n@keyframes pop{from{background:var(--mark)}}\n.res{color:var(--red);font-weight:800;border-bottom:4px double var(--red)}\n\n.say{display:flex;gap:12px;align-items:flex-start;background:var(--wash1);border-radius:12px;padding:10px 14px;margin-top:8px;font-size:clamp(1rem,min(2.4vw,2.6vh),1.15rem)}\n.say .nr{font-family:var(--display);font-weight:800;font-size:.85rem;white-space:nowrap;background:var(--ink);color:var(--paper);border-radius:999px;padding:1px 10px;margin-top:3px}\n.say p{margin:0;min-width:0}\n.merke{margin-top:8px;border:2.5px dashed var(--green);border-radius:12px;padding:8px 14px;background:var(--wash3)}\n.merke b.t{font-family:var(--display);font-weight:800;color:var(--green);text-transform:uppercase;letter-spacing:.06em;font-size:.9rem;display:block}\n.merke p{margin:.2rem 0 0}\n\n.btns{display:flex;flex-wrap:wrap;gap:10px;margin-top:12px}\n.btn{all:unset;cursor:pointer;padding:9px 18px;border-radius:10px;border:2px solid var(--ink);font-weight:700;background:var(--card);color:var(--ink)}\n.btn.primary{background:var(--pen);border-color:var(--pen);color:var(--paper)}\n.btn[disabled]{opacity:.35;cursor:default}\n.btn:focus-visible{outline:3px solid var(--mark);outline-offset:2px}\n.btn:not([disabled]):hover{filter:brightness(1.06)}\n.btn.ghost{border-color:var(--line)}\n.btn.you{background:var(--green);border-color:var(--green);color:var(--card);font-family:var(--title);font-weight:400;font-size:1.15rem;padding:7px 22px;margin-left:auto}\n@media (max-width:560px){.btn.you{margin-left:0}}\n.keys{color:var(--ink-soft);font-size:.85rem;margin:10px 0 0}\n\n/* Jetzt du */\n.phead{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:8px 16px;margin-bottom:8px}\n.ptask{font-family:var(--display);font-weight:800;font-size:clamp(1.5rem,5vw,2.2rem);font-variant-numeric:tabular-nums}\n.prow{display:flex;flex-wrap:wrap;align-items:center;gap:.3em;font-family:var(--display);font-weight:600;font-size:clamp(1.15rem,3.8vw,1.6rem);margin:.4em 0;font-variant-numeric:tabular-nums}\ninput.field{font:inherit;font-weight:800;color:var(--ink);background:var(--paper);border:2px solid var(--line);border-radius:8px;text-align:center;padding:0 .2em;font-variant-numeric:tabular-nums}\ninput.field:focus{outline:none;border-color:var(--pen);box-shadow:0 0 0 3px color-mix(in srgb,var(--pen) 25%,transparent)}\ninput.field.ok{border-color:var(--green);background:var(--wash3)}\ninput.field.bad{border-color:var(--red);background:color-mix(in srgb,var(--red) 12%,var(--paper))}\ninput.field.shown{border-style:dashed;color:var(--ink-soft)}\n.msg{margin-top:14px;padding:10px 14px;border-radius:10px;font-weight:700}\n.msg:empty{display:none}\n.msg.ok{background:var(--wash3);color:var(--green)}\n.msg.bad{background:color-mix(in srgb,var(--red) 14%,var(--card));color:var(--red)}\n.msg.info{background:var(--wash1);color:var(--ink)}\n\n@media (max-width:480px){.sheet{padding:16px}}\n@media (prefers-reduced-motion:reduce){.tile{transition:none}}\n"};
var APP_HTML = {"werkstatt": "<div class=\"wrap\">\n\n<!-- ÜBERSICHT -->\n<section id=\"home\">\n  <h1>Plus &amp; Minus bis 1 Million</h1>\n  <p class=\"lead\">Wähle eine Kachel. Drei Wege zum gleichen Ziel: im Kopf, mit dem Rechenstrich oder schriftlich mit Behalte.</p>\n  <div class=\"tiles\">\n    <button class=\"tile t1\" data-go=\"kopf\">\n      <span class=\"kicker\">Weg 1</span>\n      <h3>Im Kopf</h3>\n      <div class=\"preview\"><span class=\"big num\">45 000 + 8 000</span></div>\n      <p>Runde Zahlen schnell addieren, subtrahieren und ergänzen. 10 Aufgaben pro Runde.</p>\n      <span class=\"go\">Übung öffnen →</span>\n    </button>\n    <button class=\"tile t2\" data-go=\"strich\">\n      <span class=\"kicker\">Weg 2</span>\n      <h3>Rechenstrich</h3>\n      <div class=\"preview\">\n        <svg viewBox=\"0 0 220 80\" aria-hidden=\"true\">\n          <line x1=\"10\" y1=\"56\" x2=\"210\" y2=\"56\" class=\"rs-line\"/>\n          <path d=\"M200 56 Q170 22 140 56\" class=\"rs-arc\"/><path d=\"M140 56 Q110 22 80 56\" class=\"rs-arc\"/><path d=\"M80 56 Q55 30 30 56\" class=\"rs-arc\"/>\n          <text x=\"170\" y=\"30\" text-anchor=\"middle\" class=\"rs-jmp\" style=\"font-size:11px\">−10 000</text>\n          <text x=\"110\" y=\"30\" text-anchor=\"middle\" class=\"rs-jmp\" style=\"font-size:11px\">−3 000</text>\n          <text x=\"55\" y=\"34\" text-anchor=\"middle\" class=\"rs-jmp\" style=\"font-size:11px\">−80</text>\n          <text x=\"200\" y=\"74\" text-anchor=\"middle\" class=\"rs-lbl\" style=\"font-size:10px\">705 100</text>\n          <text x=\"30\" y=\"74\" text-anchor=\"middle\" class=\"rs-lbl\" style=\"font-size:10px\">692 020</text>\n        </svg>\n      </div>\n      <p>Grosse Rechnungen in Sprüngen lösen und jedes Zwischenergebnis notieren.</p>\n      <span class=\"go\">Übung öffnen →</span>\n    </button>\n    <button class=\"tile t3\" data-go=\"schriftlich\">\n      <span class=\"kicker\">Weg 3</span>\n      <h3>Schriftlich</h3>\n      <div class=\"preview\">\n        <div class=\"mini num\" aria-hidden=\"true\">\n          <span></span><span>4</span><span>6</span><span>8</span><span>5</span>\n          <span>+</span><span>2</span><span>7</span><span>4</span><span>9</span>\n          <span></span><span class=\"c\">1</span><span class=\"c\">1</span><span class=\"c\">1</span><span></span>\n          <span class=\"ln\"></span>\n          <span></span><span>7</span><span>4</span><span>3</span><span>4</span>\n        </div>\n      </div>\n      <p>Untereinander rechnen mit Übertrag. Die Behalte schreibst du über den Strich.</p>\n      <span class=\"go\">Übung öffnen →</span>\n    </button>\n  </div>\n</section>\n\n<!-- KOPFRECHNEN -->\n<section id=\"kopf\" hidden>\n  <button class=\"back\" data-go=\"home\">← Übersicht</button>\n  <div class=\"vhead\"><h2>Im Kopf rechnen</h2><span class=\"score\" id=\"k-score\">Runde 1</span></div>\n  <div class=\"bar\"><span><label>Zahlenraum</label><span class=\"seg\" data-for=\"kopf\">\n    <button data-lv=\"1\">bis 10 000</button><button data-lv=\"2\" aria-pressed=\"true\">bis 100 000</button><button data-lv=\"3\">bis 1 000 000</button></span></span></div>\n  <div class=\"sheet\">\n    <div class=\"dots\" id=\"k-dots\"></div>\n    <div id=\"k-body\"></div>\n    <div class=\"msg\" id=\"k-msg\"></div>\n    <div class=\"btns\" id=\"k-btns\"></div>\n  </div>\n  <p class=\"note\">Tipp: Rechne mit den Tausendern wie mit Einern. 45 000 + 8 000 ist wie 45 + 8, nur mit drei Nullen dahinter.</p>\n</section>\n\n<!-- RECHENSTRICH -->\n<section id=\"strich\" hidden>\n  <button class=\"back\" data-go=\"home\">← Übersicht</button>\n  <div class=\"vhead\"><h2>Mit dem Rechenstrich</h2><span class=\"score\" id=\"s-score\">Richtig gelöst: 0</span></div>\n  <div class=\"bar\"><span><label>Zahlenraum</label><span class=\"seg\" data-for=\"strich\">\n    <button data-lv=\"1\">bis 10 000</button><button data-lv=\"2\">bis 100 000</button><button data-lv=\"3\" aria-pressed=\"true\">bis 1 000 000</button></span></span>\n    <span><label>Schwierigkeit</label><span class=\"seg\" data-for=\"sdiff\">\n      <button data-v=\"1\" aria-pressed=\"true\">Leicht</button><button data-v=\"2\">Mittel</button><button data-v=\"3\">Schwer</button></span></span>\n    <span><label>Hilfe</label><span class=\"seg\" data-for=\"shelp\">\n      <button data-v=\"0\" aria-pressed=\"true\">Ohne</button><button data-v=\"1\">Sprünge vorgeben</button></span></span>\n  </div>\n  <div class=\"sheet\">\n    <p class=\"note\" id=\"s-level\" style=\"margin:0 0 10px\"></p>\n    <div class=\"task\" id=\"s-task\"></div>\n    <div class=\"svgbox\"><svg id=\"s-svg\" viewBox=\"0 0 660 150\" role=\"img\" aria-label=\"Rechenstrich mit deinen Sprüngen\"></svg></div>\n    <div class=\"rows\" id=\"s-rows\"></div>\n    <div class=\"btns\">\n      <button class=\"btn\" id=\"s-add\">+ Sprung</button>\n      <button class=\"btn primary\" id=\"s-check\">Prüfen</button>\n      <button class=\"btn\" id=\"s-tip\">Tipp</button>\n      <button class=\"btn\" id=\"s-new\">Neue Rechnung</button>\n    </div>\n    <div class=\"msg\" id=\"s-msg\"></div>\n  </div>\n  <p class=\"note\">Springe vom Startwert aus in Schritten. Schreibe bei jedem Sprung, wie gross er ist und wo du landest. Der Rechenstrich ist nicht massstabgetreu.</p>\n</section>\n\n<!-- SCHRIFTLICH -->\n<section id=\"schriftlich\" hidden>\n  <button class=\"back\" data-go=\"home\">← Übersicht</button>\n  <div class=\"vhead\"><h2>Schriftlich rechnen</h2><span class=\"score\" id=\"w-score\">Richtig gelöst: 0</span></div>\n  <div class=\"bar\">\n    <span><label>Rechenart</label><span class=\"seg\" data-for=\"wop\">\n      <button data-v=\"+\" aria-pressed=\"true\">Plus</button><button data-v=\"-\">Minus</button><button data-v=\"mix\">Gemischt</button></span></span>\n    <span><label>Stellen</label><span class=\"seg\" data-for=\"wlen\">\n      <button data-v=\"4\">4</button><button data-v=\"5\" aria-pressed=\"true\">5</button><button data-v=\"6\">6</button></span></span>\n  </div>\n  <div class=\"sheet\">\n    <div class=\"written\"><div class=\"wgrid\" id=\"w-grid\"></div></div>\n    <div class=\"legend\"><span><b>Behalte</b> = kleines Feld direkt über dem Strich</span><span>Rechne von rechts nach links</span></div>\n    <div class=\"btns\">\n      <button class=\"btn primary\" id=\"w-check\">Prüfen</button>\n      <button class=\"btn\" id=\"w-show\">Lösung zeigen</button>\n      <button class=\"btn\" id=\"w-new\">Neue Rechnung</button>\n    </div>\n    <div class=\"msg\" id=\"w-msg\"></div>\n  </div>\n  <p class=\"note\" id=\"w-note\"></p>\n</section>\n\n</div>", "mal": "<div class=\"wrap\">\n\n<!-- ÜBERSICHT -->\n<section id=\"home\">\n  <h1>Multiplizieren bis 1 Million</h1>\n  <p class=\"lead\">Wähle eine Kachel. Zuerst den Nullentrick im Kopf, dann schriftlich mit immer grösseren Multiplikatoren.</p>\n  <div class=\"tiles\">\n    <button class=\"tile t1\" data-go=\"kopf\">\n      <span class=\"kicker\">Weg 1</span>\n      <h3>Nullentrick</h3>\n      <div class=\"preview\"><span class=\"big num\">30 · 80<small>3 · 8 = 24 → 2 Nullen anhängen</small>2 400</span></div>\n      <p>Zehner-, Hunderter- und Tausenderzahlen im Kopf malrechnen. 10 Aufgaben pro Runde.</p>\n      <span class=\"go\">Übung öffnen →</span>\n    </button>\n    <button class=\"tile t2\" data-go=\"schriftlich\">\n      <span class=\"kicker\">Weg 2</span>\n      <h3>Schriftlich</h3>\n      <div class=\"preview\">\n        <div class=\"mini num\" aria-hidden=\"true\">\n          <span></span><span class=\"z\">1</span><span class=\"e\">8</span><span>·</span><span>6</span><span>4</span><span>7</span>\n          <span></span><span></span><span></span><span class=\"e\">5</span><span class=\"e\">1</span><span class=\"e\">7</span><span class=\"e\">6</span>\n          <span></span><span></span><span></span><span class=\"z\">6</span><span class=\"z\">4</span><span class=\"z\">7</span><span class=\"z\">0</span>\n          <span class=\"ln\"></span>\n          <span></span><span></span><span>1</span><span>1</span><span>6</span><span>4</span><span>6</span>\n        </div>\n      </div>\n      <p>Untereinander rechnen mit ein-, zwei- oder dreistelligem Multiplikator.</p>\n      <span class=\"go\">Übung öffnen →</span>\n    </button>\n  </div>\n</section>\n\n<!-- NULLENTRICK -->\n<section id=\"kopf\" hidden>\n  <button class=\"back\" data-go=\"home\">← Übersicht</button>\n  <div class=\"vhead\"><h2>Nullentrick</h2><span class=\"score\" id=\"k-score\">Runde 1</span></div>\n  <div class=\"bar\"><span><label>Schwierigkeit</label><span class=\"seg\" data-for=\"kopf\">\n    <button data-lv=\"1\">Leicht</button><button data-lv=\"2\" aria-pressed=\"true\">Mittel</button><button data-lv=\"3\">Schwer</button></span></span></div>\n  <div class=\"sheet\">\n    <p class=\"note\" id=\"k-level\" style=\"margin:0 0 12px\"></p>\n    <div class=\"dots\" id=\"k-dots\"></div>\n    <div id=\"k-body\"></div>\n    <div class=\"msg\" id=\"k-msg\"></div>\n    <div class=\"btns\" id=\"k-btns\"></div>\n  </div>\n  <p class=\"note\">Tipp: Lass zuerst alle Nullen weg und rechne das kleine Einmaleins. Zähle dann die Nullen beider Zahlen und hänge sie an. Achtung bei 5 · 2, 5 · 4, 5 · 6 und 5 · 8: Da entsteht noch eine Null dazu!</p>\n</section>\n\n<!-- SCHRIFTLICH -->\n<section id=\"schriftlich\" hidden>\n  <button class=\"back\" data-go=\"home\">← Übersicht</button>\n  <div class=\"vhead\"><h2>Schriftlich multiplizieren</h2><span class=\"score\" id=\"w-score\">Richtig gelöst: 0</span></div>\n  <div class=\"bar\">\n    <span><label>Multiplikator</label><span class=\"seg\" data-for=\"wlen\">\n      <button data-v=\"1\" aria-pressed=\"true\">1-stellig</button><button data-v=\"2\">2-stellig</button><button data-v=\"3\">3-stellig</button></span></span>\n  </div>\n  <div class=\"sheet\">\n    <div class=\"written\"><div class=\"wgrid\" id=\"w-grid\"></div></div>\n    <div class=\"legend\" id=\"w-legend\"></div>\n    <div class=\"btns\">\n      <button class=\"btn primary\" id=\"w-check\">Prüfen</button>\n      <button class=\"btn\" id=\"w-show\">Lösung zeigen</button>\n      <button class=\"btn\" id=\"w-new\">Neue Rechnung</button>\n    </div>\n    <div class=\"msg\" id=\"w-msg\"></div>\n  </div>\n  <p class=\"note\" id=\"w-note\"></p>\n</section>\n\n</div>", "durch": "<div class=\"wrap\">\n\n<!-- ÜBERSICHT -->\n<section id=\"home\">\n  <h1>Dividieren <span class=\"hl-t\">bis 1 Million</span></h1>\n  <p class=\"lead\">Wähle eine Kachel. Zuerst den Nullentrick im Kopf, dann schriftlich Schritt für Schritt.</p>\n  <div class=\"tiles\">\n    <button class=\"tile t1\" data-go=\"kopf\">\n      <span class=\"kicker\">Weg 1</span>\n      <h3>Nullentrick</h3>\n      <div class=\"preview\"><span class=\"big num\">21 00<span class=\"strk\">0</span> : 7<span class=\"strk\">0</span><small>Gleich viele Nullen streichen</small>21 : 7 = 3<small>2 Nullen wieder anhängen</small>300</span></div>\n      <p>Nullen wegdenken, mit dem Einmaleins rechnen, Nullen wieder anhängen. 10 Aufgaben pro Runde.</p>\n      <span class=\"go\">Übung öffnen →</span>\n    </button>\n    <button class=\"tile t2\" data-go=\"schriftlich\">\n      <span class=\"kicker\">Weg 2</span>\n      <h3>Schriftlich</h3>\n      <div class=\"preview\"><div class=\"mini num\" id=\"mini\" aria-hidden=\"true\"></div></div>\n      <p>Mit «Weiter» wirst du Schritt für Schritt durch die Rechnung geführt.</p>\n      <span class=\"go\">Übung öffnen →</span>\n    </button>\n  </div>\n</section>\n\n<!-- NULLENTRICK -->\n<section id=\"kopf\" hidden>\n  <button class=\"back\" data-go=\"home\">← Übersicht</button>\n  <div class=\"vhead\"><h2>Nullentrick</h2><span class=\"score\" id=\"k-score\">Runde 1</span></div>\n  <div class=\"bar\"><span><label>Schwierigkeit</label><span class=\"seg\" data-for=\"kopf\">\n    <button data-lv=\"1\" aria-pressed=\"true\">Leicht</button><button data-lv=\"2\">Mittel</button><button data-lv=\"3\">Schwer</button></span></span></div>\n  <div class=\"sheet\">\n    <p class=\"note\" id=\"k-level\" style=\"margin:0 0 12px\"></p>\n    <div class=\"dots\" id=\"k-dots\"></div>\n    <div id=\"k-body\"></div>\n    <div class=\"msg\" id=\"k-msg\"></div>\n    <div class=\"btns\" id=\"k-btns\"></div>\n  </div>\n  <p class=\"note\">Tipp: Hat die zweite Zahl Nullen, streichst du bei beiden Zahlen gleich viele Nullen. Dann denkst du die restlichen Nullen weg, rechnest die Einmaleins-Aufgabe und hängst die weggedachten Nullen ans Resultat. Achtung bei Aufgaben wie 4 000 : 5: Hier brauchst du 40 : 5, eine Null gehört zur Grundaufgabe!</p>\n</section>\n\n<!-- SCHRIFTLICH -->\n<section id=\"schriftlich\" hidden>\n  <button class=\"back\" data-go=\"home\">← Übersicht</button>\n  <div class=\"vhead\"><h2>Schriftlich dividieren</h2><span class=\"score\" id=\"s-score\">Richtig gelöst: 0</span></div>\n  <div class=\"bar\">\n    <span><label>Aufgaben</label><span class=\"seg\" data-for=\"slv\">\n      <button data-v=\"1\" aria-pressed=\"true\">Durch 1-stellig</button><button data-v=\"R\">Mit Rest</button><button data-v=\"2\">Durch 2-stellig</button><button data-v=\"3\">Durch 3-stellig</button></span></span>\n  </div>\n  <div class=\"sheet\">\n    <div class=\"step\" id=\"s-step\"><span class=\"nr\" id=\"s-nr\">Schritt 1</span><span id=\"s-text\"></span></div>\n    <div class=\"written\"><div class=\"dgrid\" id=\"s-grid\"></div></div>\n    <div class=\"legend\">\n      <span><i class=\"sw m\"></i>Damit rechnest du jetzt</span>\n      <span><i class=\"sw q\"></i>Resultat</span>\n      <span><i class=\"sw p\"></i>Malrechnung</span>\n      <span><i class=\"sw d\"></i>Heruntergeholte Ziffer</span>\n      <span>Zahlen ganz normal eintippen</span>\n    </div>\n    <div class=\"btns\">\n      <button class=\"btn primary\" id=\"s-next\">Weiter →</button>\n      <button class=\"btn\" id=\"s-show\">Schritt zeigen</button>\n      <button class=\"btn\" id=\"s-new\">Neue Rechnung</button>\n    </div>\n    <div class=\"msg\" id=\"s-msg\"></div>\n  </div>\n  <p class=\"note\" id=\"s-note\"></p>\n</section>\n\n</div>", "flex": "<div class=\"wrap\">\n\n<!-- ÜBERSICHT -->\n<section id=\"home\">\n  <h1>Flexibel rechnen</h1>\n  <p class=\"lead\">Beim flexiblen Rechnen kommst du schneller zum Resultat, weil du die Rechnung geschickt vereinfachst. Wähle einen Trick. Mit «Weiter» wird er Schritt für Schritt erklärt.</p>\n  <div class=\"group\"><h2>Rechentricks</h2><div class=\"tiles\" id=\"tiles-a\"></div></div>\n  <div class=\"group\"><h2>Verteilungsgesetze</h2><div class=\"tiles\" id=\"tiles-b\"></div></div>\n</section>\n\n<!-- PRÄSENTATION -->\n<section id=\"show\" hidden>\n  <div class=\"topbar\">\n    <button class=\"back\" data-go=\"home\">← Übersicht</button>\n  </div>\n  <div class=\"vhead\">\n    <div><span class=\"kicker\" id=\"v-kicker\"></span><h2 id=\"v-title\"></h2></div>\n    <span class=\"pill\" id=\"v-count\"></span>\n  </div>\n  <div class=\"choose\">\n    <span class=\"cgroup\" id=\"v-opg\" hidden><span class=\"kicker\">Rechenart</span><span class=\"seg\" id=\"v-op\"></span></span><span class=\"cgroup\" id=\"v-choose\" hidden><span class=\"kicker\">Rechnen mit</span><span class=\"seg\" id=\"v-seg\"></span></span>\n    <span class=\"cgroup\"><span class=\"kicker\">Schwierigkeit</span><span class=\"seg\" id=\"v-lv\"></span></span>\n  </div>\n  <div class=\"sheet\" id=\"pane-e\">\n    <div class=\"dots\" id=\"v-dots\"></div>\n    <div class=\"boardwrap\"><div class=\"board\" id=\"v-board\"></div></div>\n    <div class=\"say\"><span class=\"nr\" id=\"v-nr\"></span><p id=\"v-say\"></p></div>\n    <div class=\"merke\" id=\"v-merke\" hidden><b class=\"t\">Merke</b><p id=\"v-merke-t\"></p></div>\n    <div class=\"btns\">\n      <button class=\"btn\" id=\"v-prev\">← Zurück</button>\n      <button class=\"btn primary\" id=\"v-next\">Weiter →</button>\n      <button class=\"btn ghost\" id=\"v-new\">Anderes Beispiel</button>\n      <button class=\"btn ghost\" id=\"v-full\" hidden>Vollbild</button>\n      <button class=\"btn you\" id=\"tab-p\">Jetzt du! ✎</button>\n    </div>\n  </div>\n\n  <div id=\"pane-p\" hidden>\n    <div class=\"sheet\">\n      <div class=\"phead\"><div class=\"ptask\" id=\"p-task\"></div><span class=\"pill\" id=\"p-score\">Richtig: 0</span></div>\n      <div id=\"p-body\"></div>\n      <div class=\"btns\">\n        <button class=\"btn primary\" id=\"p-check\">Prüfen</button>\n        <button class=\"btn\" id=\"p-show\">Lösung zeigen</button>\n        <button class=\"btn\" id=\"p-new\">Neue Aufgabe</button>\n        <button class=\"btn ghost\" id=\"tab-e\">← Zurück zur Erklärung</button>\n      </div>\n      <div class=\"msg\" id=\"p-msg\"></div>\n    </div>\n  </div>\n</section>\n\n</div>"};
var APP_EULE = "\n:host{display:block;--ink:#1f2421;--ink-soft:#5f6963;--pen:#3f78a8;--green:#5f9a4a;--red:#c8574e;--mark:#ffdf5e;\n  --wash1:#fbf3dc;--wash2:#e4f2fd;--wash3:#e9f1e3;--wash4:#efe7f7;--card:#fff;--line:#c5d8e8;--paper:#fbfdff;--paper2:#fbfdff;\n  --sky1:transparent;--sky2:transparent;--bg:transparent;--bg2:transparent;--tile:#fff;--tile1:#fbf3dc;--tile2:#e9f1e3;\n  --pe:#2f8f3a;--pz:#1d63c4;--ph:#9a3fc9;--we:#e3f4e1;--wz:#e2edfb;--wh:#f3e6fb;--c1:#3f78a8;--c2:#5f9a4a;\n  --display:\"Patrick Hand\",\"Segoe Print\",\"Comic Sans MS\",cursive;--body:var(--display);--title:var(--display)}\n[hidden]{display:none!important}\n.app{background:none!important;font-family:var(--display);font-size:20px;line-height:1.35;color:var(--ink);min-height:0!important}\n.wrap{max-width:none!important;padding:0!important}\nh1,h2,h3,.task,.ptask,.board,.prow,.preview,.preview .big,.tile h3,.say .nr,.step .nr,.merke b.t,.dgrid .op,.dgrid .mi,.wgrid .opc,.row .op,.tag,.btn.you{font-weight:400!important}\nh2{font-size:clamp(30px,5.4vw,40px)}\nh2::after{content:\" ✦\";color:#d6ad45;font-size:.5em;vertical-align:super}\n.back{all:unset;box-sizing:border-box;cursor:pointer;display:inline-flex!important;align-items:center;gap:8px;background:#fff;border:2px solid var(--ink);border-radius:999px;\n  padding:3px 16px 3px 6px;box-shadow:0 4px 12px rgba(63,120,168,.14);font-size:22px;min-height:46px;margin-bottom:16px;color:var(--ink)!important}\n.back img{width:36px;height:36px;border-radius:50%;object-fit:cover}\n.sheet{border:1.5px solid #e1edf7!important;border-radius:28px!important;box-shadow:0 10px 26px rgba(63,120,168,.18),0 2px 6px rgba(63,120,168,.10)!important;background:#fff}\n.btn{border-radius:14px!important;border:2px solid var(--ink)!important;background:#fff!important;color:var(--ink)!important;box-shadow:0 4px 12px rgba(63,120,168,.14);font-weight:400!important;font-size:21px;padding:6px 18px!important}\n.btn.primary{background:#dcf0fd!important}\n.btn.you{background:#fbf3dc!important;border-color:#d6ad45!important;color:var(--ink)!important}\n.btn.ghost{border-color:var(--line)!important}\n.seg{border:2px solid var(--ink);border-radius:14px}\n.seg button{font-weight:400!important;font-size:18px!important}\n.seg button[aria-pressed=\"true\"]{background:#fbf3dc!important;color:var(--ink)!important;box-shadow:inset 0 -3px 0 #d6ad45}\n.bar label,.kicker,.choose .kicker{font-weight:400!important;font-size:15px!important;color:var(--ink-soft)}\n.score,.pill{font-weight:400!important;border-color:#efdca6!important;background:#fbf3dc!important;color:#a87c1f}\n.msg{font-weight:400!important;font-size:20px;border-radius:16px}\n.note,.lead{font-size:17px}\n.dot{border-color:#c5d8e8}\n.dot.now{border-color:#d6ad45!important;background:#fbf3dc!important}\n.dot.ok{background:#5f9a4a!important;border-color:#5f9a4a!important}\n.dot.bad{background:#d6ad45!important;border-color:#d6ad45!important}\n.say{background:#fbf3dc;border:1.5px solid #efdca6}\n.say .nr,.step .nr{background:#d6ad45!important;color:#fff!important}\n.step{font-weight:400!important;background:#fbf3dc!important;border:1.5px solid #efdca6}\n.step.done{background:#e9f1e3!important;border-color:#cfe1c4}\n.merke{border-color:#d6ad45!important;background:#fffaf0!important}\n.merke b.t{color:#a87c1f!important}\ninput.cell,input.field,input.cc{font-family:var(--display)!important;font-weight:400!important}\ninput:focus{border-color:#d6ad45!important;box-shadow:0 0 0 4px #fbf3dc!important}\n.res{color:#a87c1f!important;border-bottom-color:#d6ad45!important}\n.board .hot{background:#fbf3dc!important}\n.legend{font-size:15px}\n/* Schriftlich: kariertes Heftblatt wie auf den Merkblättern */\n.written{overflow-x:auto;padding:6px 0 10px}\n.dgrid,.wgrid{--k:2.7rem;background-color:#fff;background-image:linear-gradient(#d9e7f5 1px,transparent 1px),linear-gradient(90deg,#d9e7f5 1px,transparent 1px);\n  background-size:var(--k) var(--k);padding:var(--k);border-radius:20px;border:1.5px solid #d9e7f5;font-size:1.8rem!important;box-shadow:inset 0 0 0 6px #fff}\n.dgrid{grid-auto-rows:var(--k)!important}\n.dgrid > div,.wgrid > div{width:var(--k)!important;height:var(--k)!important;padding:0!important}\n.dgrid .ex,.wgrid .ex{font-weight:400!important}\n.dgrid .op,.wgrid .opc{color:#5f6963}\n.dgrid input.cell,.wgrid input.cell{width:calc(var(--k) - 8px)!important;height:calc(var(--k) - 8px)!important;font-size:1.7rem!important;background:rgba(255,255,255,.7)!important;\n  border:2px dashed #b4cde4!important;border-radius:10px!important;box-shadow:none!important}\n.dgrid input.cell[readonly]{border-color:transparent!important;background:transparent!important}\n.dgrid input.tq{color:#2f8f3a!important}.dgrid input.tp{color:#1d63c4!important}.dgrid input.td{color:#9a3fc9!important}.dgrid input.tr{color:#d0453a!important}\n.dgrid input.cell.tq:not([readonly]){background:#e3f4e1!important;border-color:#7cc27f!important}.dgrid input.cell.tp:not([readonly]){background:#e2edfb!important;border-color:#7ea6e3!important}.dgrid input.cell.td:not([readonly]){background:#f3e6fb!important;border-color:#c18fe0!important}\n.dgrid input.cell.cur.cur:not([readonly]){border:3px solid #e07a2e!important;box-shadow:0 0 0 4px #fde3cc!important}\n.dgrid input.cell.bad,.wgrid input.cell.bad,.wgrid input.cc.bad{border:2.5px solid #c8574e!important;background:#fcefed!important}\n.dgrid input.cell.shown,.wgrid input.shown{color:#a87c1f!important}\n.dgrid .hl,.dgrid input.cell.hl,.wgrid .now{background:#ffdf5e!important;border-radius:9px}\n.dgrid .ul,.wgrid .carry{border-bottom:2.5px solid #1f2421!important}\n.dgrid .mi{color:#1d63c4!important}\n.wgrid .p0,.wgrid input.t0{color:#2f8f3a!important}.wgrid .p1,.wgrid input.t1{color:#1d63c4!important}.wgrid .p2,.wgrid input.t2{color:#9a3fc9!important}\n.sw{width:1em!important;height:1em!important}\n.dgrid .rlab{color:#c8574e!important;font-weight:400!important}\n.wgrid input.cc{width:1.5rem!important;height:1.5rem!important;font-size:1rem!important;border:1.5px dashed #e3b1aa!important;background:transparent!important;color:#c8574e!important}\n.wgrid input.cell.ok,.wgrid input.cc.ok{border-style:solid!important;border-color:#a8cc98!important;background:#f3f8ef!important}\n.wgrid input.cell:focus,.dgrid input.cell:focus{border-style:solid!important}\n.wgrid .head{font-size:.75rem!important;color:#a87c1f}\n.tag{transform:scale(.85)}\n/* Tipp hinter der Glühbirne, Merkblatt-Knopf */\n.note{display:none!important}\nsection{position:relative}\n.sheet{position:relative}\n.birne{position:absolute;top:-18px;right:18px;z-index:3;display:inline-flex;align-items:center;gap:4px;background:#fff;border:2px solid #d6ad45;border-radius:999px;padding:3px 12px 3px 6px;\n  font:inherit;font-size:17px;color:#a87c1f;cursor:pointer;box-shadow:0 4px 12px rgba(63,120,168,.16)}\n.birne[aria-expanded=\"true\"]{background:#fff6cf}\n.birnbox{background:#fffbea;border:2px solid #f0d97a;border-radius:18px;padding:10px 16px;margin:4px 0 14px;font-size:18px;line-height:1.35}\n.birnbox p{margin:0 0 6px}\n.birnbox .mbl{all:unset;cursor:pointer;color:#1d63c4;text-decoration:underline}\n.theo{all:unset;box-sizing:border-box;cursor:pointer;display:inline-flex;align-items:center;gap:6px;margin:0 0 16px 10px;background:#fff;border:2px solid #d6ad45;border-radius:999px;\n  padding:3px 16px;min-height:46px;font-size:20px;color:#a87c1f;box-shadow:0 4px 12px rgba(63,120,168,.14);vertical-align:top}\n#k-tip::before,#s-tip::before{content:\"\";display:inline-block;width:20px;height:20px;margin-right:6px;vertical-align:-3px;background:url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M9 18h6M10 21h4M12 3a6 6 0 0 0-3.6 10.8c.7.6 1.1 1.3 1.1 2.2h5c0-.9.4-1.6 1.1-2.2A6 6 0 0 0 12 3z' fill='%23fbe7a1' stroke='%23a87c1f' stroke-width='1.6' stroke-linejoin='round'/%3E%3C/svg%3E\") center/contain no-repeat}\n@media (max-width:480px){.dgrid,.wgrid{--k:2.2rem;font-size:1.4rem!important}.dgrid input.cell,.wgrid input.cell{font-size:1.35rem!important}}\n";
var APPS = {
"werkstatt": function (KR, EXIT, STAR, SOLVED, ANS) {

// ---------- Hilfsfunktionen ----------
const $ = s => KR.querySelector(s);
const rnd = (a,b) => a + Math.floor(Math.random()*(b-a+1));
const pick = arr => arr[Math.floor(Math.random()*arr.length)];
const fmt = n => String(n).replace(/\B(?=(\d{3})+(?!\d))/g,' ');
const parse = s => { const t = String(s).replace(/[\s'’.  ]/g,''); return /^\d+$/.test(t) ? Number(t) : null; };
const MINUS = '−';

// ---------- Navigation ----------
const views = ['home','kopf','strich','schriftlich'];
function show(id){
  if(!views.includes(id)) id='home';
  views.forEach(v => KR.getElementById(v).hidden = v!==id);
  window.scrollTo(0,0);
  if(id==='kopf') focusKopf();
  if(id==='schriftlich') setTimeout(() => $('#w-r0')?.focus(), 30);
}
KR.querySelectorAll('[data-go]').forEach(b => b.addEventListener('click', () => {
  const id = b.dataset.go;
  show(id);
}));

// Segment-Schalter
function seg(name, onChange){
  const el = KR.querySelector(`.seg[data-for="${name}"]`);
  el.querySelectorAll('button').forEach(b => b.addEventListener('click', () => {
    el.querySelectorAll('button').forEach(x => x.setAttribute('aria-pressed', x===b ? 'true':'false'));
    onChange(b.dataset.lv ?? b.dataset.v);
  }));
  const cur = el.querySelector('[aria-pressed="true"]');
  return cur.dataset.lv ?? cur.dataset.v;
}
function setMsg(el, text, kind){ el.textContent = text; el.className = 'msg ' + (kind||''); }

// =========================================================
// 1) KOPFRECHNEN
// =========================================================
const K = { lv: 2, tasks: [], i: 0, results: [], answered: false, round: 1 };
K.lv = Number(seg('kopf', v => { K.lv = Number(v); kNewRound(); }));

function kGen(lv){
  const max = [0,10000,100000,1000000][lv];
  const s = [0,100,1000,10000][lv];
  const units = max / s;            // 100
  const type = pick(['add','add','sub','sub','erg','mix','mixsub']);
  if(type==='add'){
    const x = rnd(11, units-12), y = rnd(2, Math.min(units-x-1, 89));
    return {parts:[x*s,'+',y*s,'=',null], ans:(x+y)*s};
  }
  if(type==='sub'){
    const x = rnd(20, units-1), y = rnd(2, x-3);
    return {parts:[x*s, MINUS, y*s,'=',null], ans:(x-y)*s};
  }
  if(type==='erg'){
    let x; do { x = rnd(11, units-1); } while(x%10===0);
    const target = Math.ceil(x/10)*10*s;
    return {parts:[x*s,'+',null,'=',target], ans:target - x*s};
  }
  const t = s/10;                    // feinere Stelle
  if(type==='mix'){
    const a = rnd(101, units*10-200)*t, b = rnd(2,9)*s;
    if(a+b>max) return kGen(lv);
    return {parts:[a,'+',b,'=',null], ans:a+b};
  }
  const a = rnd(200, units*10-1)*t, b = rnd(2,9)*s;
  if(b>=a) return kGen(lv);
  return {parts:[a, MINUS, b,'=',null], ans:a-b};
}
function kNewRound(){
  K.tasks = Array.from({length:10}, () => kGen(K.lv));
  K.i = 0; K.results = []; K.answered = false;
  kRender();
}
function kRender(){
  const dots = $('#k-dots'); dots.innerHTML = '';
  K.tasks.forEach((_,j) => {
    const d = document.createElement('span');
    d.className = 'dot' + (K.results[j]===true?' ok':K.results[j]===false?' bad':j===K.i?' now':'');
    dots.appendChild(d);
  });
  $('#k-score').textContent = `Runde ${K.round} · ${K.results.filter(Boolean).length} richtig`;
  const body = $('#k-body'), btns = $('#k-btns');
  setMsg($('#k-msg'),'');
  btns.innerHTML = '';
  if(K.i >= K.tasks.length){
    const n = K.results.filter(Boolean).length;
    body.innerHTML = `<div class="task">${n} von 10 richtig</div>` + STAR('kopf-' + K.lv, n>=9 ? 3 : n>=6 ? 2 : 1);
    setMsg($('#k-msg'), n>=9 ? 'Ausgezeichnet! Probiere den nächsten Zahlenraum.' : n>=6 ? 'Gut gemacht. Mit einer weiteren Runde wirst du noch sicherer.' : 'Übe noch eine Runde. Denk an den Tipp unten.', n>=6?'ok':'info');
    const b = document.createElement('button'); b.className='btn primary'; b.textContent='Neue Runde';
    b.onclick = () => { K.round++; kNewRound(); focusKopf(); };
    btns.appendChild(b); b.focus(); return;
  }
  const t = K.tasks[K.i];
  body.innerHTML = '<div class="task">' + t.parts.map(p =>
    p===null ? '<input class="field" id="k-in" inputmode="numeric" autocomplete="off" aria-label="Deine Antwort">' :
    typeof p==='number' ? `<span class="num">${fmt(p)}</span>` : `<span>${p}</span>`).join('') + '</div>';
  const b = document.createElement('button'); b.className='btn primary'; b.id='k-go'; b.textContent='Prüfen';
  b.onclick = kStep; btns.appendChild(b);
  $('#k-in').addEventListener('keydown', e => { if(e.key==='Enter') kStep(); });
  K.answered = false;
}
function kStep(){
  if(K.answered){ K.i++; kRender(); focusKopf(); return; }
  const inp = $('#k-in'), v = parse(inp.value), t = K.tasks[K.i];
  if(v===null){ setMsg($('#k-msg'),'Schreibe eine Zahl ins Feld.','info'); inp.focus(); return; }
  const ok = v===t.ans;
  K.results[K.i] = ok; K.answered = true; ANS(ok);
  inp.classList.add(ok?'ok':'bad'); inp.readOnly = true;
  setMsg($('#k-msg'), ok ? 'Richtig!' : `Leider nein. Richtig ist ${fmt(t.ans)}.`, ok?'ok':'bad');
  $('#k-go').textContent = K.i===9 ? 'Auswertung' : 'Weiter';
  $('#k-go').focus();
  // Punkte neu zeichnen
  const dots = $('#k-dots').children; dots[K.i].className = 'dot ' + (ok?'ok':'bad');
  $('#k-score').textContent = `Runde ${K.round} · ${K.results.filter(Boolean).length} richtig`;
  // Enter auf dem Button führt weiter
}
function focusKopf(){ setTimeout(() => $('#k-in')?.focus(), 30); }
kNewRound();

// =========================================================
// 2) RECHENSTRICH
// =========================================================
const S = { lv: 3, a:0, b:0, op:'-', solved:false, score:0 };
S.lv = Number(seg('strich', v => { S.lv = Number(v); sNew(); }));
S.diff = Number(seg('sdiff', v => { S.diff = Number(v); sNew(); }));
S.help = seg('shelp', v => { S.help = v==='1'; sNew(); }) === '1';

const S_LEVEL_TEXT = {
  1: 'Leicht: Die zweite Zahl hat nur zwei Teile, und bei keinem Sprung gibt es einen Übergang. Es ändert sich jeweils nur eine Ziffer.',
  2: 'Mittel: Die zweite Zahl hat zwei Teile. Bei einem Sprung gibt es einen Übergang.',
  3: 'Schwer: Die zweite Zahl hat zwei bis drei Teile, mit mehreren Übergängen und Nullen in der Startzahl.'
};

function digitsOf(n,len){ return String(n).padStart(len,'0').split('').reverse().map(Number); }
function placeParts(n){
  const out = [];
  String(n).split('').reverse().forEach((d,p) => { if(d!=='0') out.unshift(Number(d)*10**p); });
  return out;
}
function sGen(lv, diff){
  const D = [0,4,5,6][lv];
  for(let tries=0; tries<2000; tries++){
    const op = Math.random()<0.5 ? '-' : '+';
    // Startzahl: leicht = nur 2–3 besetzte Stellen, sonst mit einigen Nullen
    let a;
    if(diff===1){
      a = rnd(1,9)*10**(D-1) + rnd(0,9)*10**(D-2) + rnd(0,9)*10**(D-3);
    } else {
      a = rnd(2*10**(D-1), 10**D - 1);
      const rr = diff===2 ? 10**(D-4) : pick([1,10,100]);
      a = Math.round(a / rr) * rr;
    }
    a = Math.min(a, 10**D - 1);
    if(a < 10**(D-1)) continue;
    // Zweite Zahl: leicht/mittel 2 Teile, schwer 2–3 Teile
    const places = [];
    const lowest = diff===1 ? D-3 : diff===2 ? D-4 : 0;
    for(let p=lowest;p<=D-2;p++) places.push(p);
    const k = diff===3 ? rnd(2,3) : 2, chosen = [];
    while(chosen.length<k){ const p = pick(places); if(!chosen.includes(p)) chosen.push(p); }
    if(!chosen.includes(D-2) && lv>1 && Math.random()<0.7) chosen[0] = D-2;
    let b = 0; new Set(chosen).forEach(p => b += rnd(1,9)*10**p);
    const res = op==='-' ? a-b : a+b;
    if(res<=0 || res>=10**D) continue;
    // Übergänge zählen (Sprung pro Stellenwert)
    const da = digitsOf(a,D), db = digitsOf(b,D);
    let cross = 0;
    for(let p=0;p<D;p++){ if(db[p] && (op==='-' ? da[p]<db[p] : da[p]+db[p]>9)) cross++; }
    if(diff===1 && cross!==0) continue;
    if(diff===2 && cross!==1) continue;
    if(diff===3 && cross<1) continue;
    return {a,b,op};
  }
  return {a:705100,b:13080,op:'-'};
}
function sNew(){
  Object.assign(S, sGen(S.lv, S.diff)); S.solved = false;
  $('#s-level').textContent = S_LEVEL_TEXT[S.diff] + (S.help ? ' Die Sprünge sind vorgegeben: Du rechnest nur die Landepunkte.' : '');
  $('#s-task').innerHTML = `<span class="num">${fmt(S.a)}</span><span>${S.op==='-'?MINUS:'+'}</span><span class="num">${fmt(S.b)}</span><span>=</span><span>?</span>`;
  $('#s-rows').innerHTML = '';
  if(S.help){ placeParts(S.b).forEach(j => sAddRow(j)); $('#s-v1')?.focus(); }
  else sAddRow();
  $('#s-add').hidden = S.help;
  setMsg($('#s-msg'),'');
  sDraw();
}
function sAddRow(given){
  const rows = $('#s-rows');
  if(rows.children.length>=6){ setMsg($('#s-msg'),'Mehr als 6 Sprünge braucht es nicht. Versuche grössere Sprünge.','info'); return; }
  const n = rows.children.length+1;
  const r = document.createElement('div'); r.className='row';
  r.innerHTML = `<span class="lab">Sprung ${n}</span>
    <span class="op">${S.op==='-'?MINUS:'+'}</span>
    <input class="field jmp" id="s-j${n}" inputmode="numeric" autocomplete="off" placeholder="Sprung" aria-label="Sprung ${n}: Wie weit springst du?">
    <span class="arrow">→</span>
    <input class="field val" id="s-v${n}" inputmode="numeric" autocomplete="off" placeholder="Landepunkt" aria-label="Sprung ${n}: Wo landest du?">
    <button class="x" title="Sprung entfernen" aria-label="Sprung ${n} entfernen">✕</button>`;
  r.querySelectorAll('input').forEach(i => {
    i.addEventListener('input', () => { i.classList.remove('ok','bad'); sDraw(); });
    i.addEventListener('keydown', e => { if(e.key==='Enter') sCheck(); });
  });
  r.querySelector('.x').onclick = () => { if(rows.children.length>1){ r.remove(); sRenumber(); sDraw(); } };
  rows.appendChild(r);
  if(typeof given==='number'){
    const j = r.querySelector('.jmp'); j.value = fmt(given); j.readOnly = true; j.classList.add('given');
    r.querySelector('.x').hidden = true;
  } else r.querySelector('.jmp').focus();
  sDraw();
}
function sRenumber(){
  [...$('#s-rows').children].forEach((r,i) => r.querySelector('.lab').textContent = `Sprung ${i+1}`);
}
function sRowsData(){
  return [...$('#s-rows').children].map(r => ({
    row:r, jIn:r.querySelector('.jmp'), vIn:r.querySelector('.val'),
    j:parse(r.querySelector('.jmp').value), v:parse(r.querySelector('.val').value) }));
}
function sDraw(status){
  const data = sRowsData(), N = data.length;
  const svg = $('#s-svg'), y = 100, L = 50, R = 610;
  const step = (R-L)/Math.max(N,1);
  const xs = [S.op==='-' ? R : L];
  for(let i=1;i<=N;i++) xs.push(S.op==='-' ? R - i*step : L + i*step);
  let h = `<defs><marker id="ah" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" class="rs-arrow"/></marker></defs>`;
  h += `<line x1="20" y1="${y}" x2="640" y2="${y}" class="rs-line"/>`;
  h += `<line x1="${xs[0]}" y1="${y-10}" x2="${xs[0]}" y2="${y+10}" class="rs-tick"/>`;
  h += `<text x="${xs[0]}" y="${y+32}" text-anchor="middle" class="rs-start">${fmt(S.a)}</text>`;
  data.forEach((d,i) => {
    const x0 = xs[i], x1 = xs[i+1], mx = (x0+x1)/2;
    const cls = status ? (status[i] ? ' ok':' bad') : '';
    h += `<path d="M${x0} ${y-4} Q${mx} ${y-64} ${x1} ${y-4}" class="rs-arc${cls}" marker-end="url(#ah)"/>`;
    h += `<text x="${mx}" y="${y-40}" text-anchor="middle" class="rs-jmp">${(S.op==='-'?MINUS:'+')}${d.j!==null?fmt(d.j):'?'}</text>`;
    h += `<line x1="${x1}" y1="${y-10}" x2="${x1}" y2="${y+10}" class="rs-tick"/>`;
    h += `<text x="${x1}" y="${y+32}" text-anchor="middle" class="rs-lbl">${d.v!==null?fmt(d.v):'?'}</text>`;
  });
  svg.innerHTML = h;
}
function sCheck(){
  const data = sRowsData();
  let prev = S.a, sum = 0, allOk = true, empty = false;
  const status = [];
  data.forEach(d => {
    if(d.j===null || d.v===null){ empty = true; }
    const expect = d.j===null ? null : (S.op==='-' ? prev - d.j : prev + d.j);
    const ok = d.j!==null && d.j>0 && d.v!==null && d.v===expect;
    d.jIn.classList.toggle('ok', ok); d.jIn.classList.toggle('bad', !ok && d.j===null ? false : !ok && d.j!==null && d.j<=0);
    d.vIn.classList.toggle('ok', ok); d.vIn.classList.toggle('bad', !ok && d.v!==null);
    status.push(ok);
    if(!ok) allOk = false;
    if(d.j!==null) sum += d.j;
    prev = d.v!==null ? d.v : (expect ?? prev);
  });
  sDraw(status);
  const msg = $('#s-msg');
  if(empty){ setMsg(msg,'Fülle bei jedem Sprung beide Felder aus: Sprunggrösse und Landepunkt.','info'); return; }
  if(!allOk){ setMsg(msg,'Bei den rot markierten Landepunkten stimmt die Rechnung noch nicht. Rechne diesen Sprung nochmals.','bad'); return; }
  if(sum < S.b){ setMsg(msg,`Deine Sprünge sind zusammen ${fmt(sum)}. Es fehlen noch ${fmt(S.b-sum)}. Füge einen Sprung hinzu.`,'info'); return; }
  if(sum > S.b){ setMsg(msg,`Deine Sprünge sind zusammen ${fmt(sum)}, also ${fmt(sum-S.b)} zu viel. Du darfst insgesamt genau ${fmt(S.b)} springen.`,'bad'); return; }
  const res = S.op==='-' ? S.a-S.b : S.a+S.b;
  setMsg(msg,`Super! ${fmt(S.a)} ${S.op==='-'?MINUS:'+'} ${fmt(S.b)} = ${fmt(res)}`,'ok');
  $('#s-task').lastElementChild.textContent = fmt(res);
  if(!S.solved){ SOLVED('strich-' + S.diff); S.solved = true; S.score++; $('#s-score').textContent = `Richtig gelöst: ${S.score}`; }
}
function sTip(){
  const parts = [];
  String(S.b).split('').reverse().forEach((d,p) => { if(d!=='0') parts.unshift(fmt(Number(d)*10**p)); });
  setMsg($('#s-msg'), `Tipp: Zerlege ${fmt(S.b)} nach Stellenwerten in ${parts.join(' + ')}. Mache mit jedem Teil einen Sprung.`,'info');
}
$('#s-add').onclick = () => sAddRow();
$('#s-check').onclick = sCheck;
$('#s-tip').onclick = sTip;
$('#s-new').onclick = sNew;
sNew();

// =========================================================
// 3) SCHRIFTLICH mit Behalte
// =========================================================
const W = { op:'+', mode:'+', len:5, score:0, solved:false, shown:false };
W.mode = seg('wop', v => { W.mode = v; wNew(); });
W.len = Number(seg('wlen', v => { W.len = Number(v); wNew(); }));
const PLACES = ['E','Z','H','T','ZT','HT','M'];

function wCompute(a,b,op,n){
  const da = digitsOf(a,n), db = digitsOf(b,n), c = Array(n+1).fill(0), r = Array(n).fill(0);
  for(let p=0;p<n;p++){
    if(op==='+'){ const s = da[p]+db[p]+c[p]; r[p] = s%10; c[p+1] = Math.floor(s/10); }
    else { const u = db[p]+c[p]; if(da[p]<u){ r[p] = da[p]+10-u; c[p+1]=1; } else { r[p] = da[p]-u; c[p+1]=0; } }
  }
  return {c,r};
}
function wGen(){
  const D = W.len;
  for(let t=0;t<800;t++){
    const op = W.mode==='mix' ? pick(['+','-']) : W.mode;
    let a = rnd(10**(D-1), 10**D - 1);
    if(op==='-' && Math.random()<0.4){ // Nullen in der oberen Zahl, z. B. 705 100
      const p = rnd(1,D-2); a = a - (Math.floor(a/10**p)%10)*10**p;
    }
    const bl = Math.random()<0.6 ? D : D-1;
    let b = rnd(10**(bl-1), 10**bl - 1);
    if(op==='-' && b>=a) continue;
    if(op==='+' && a+b>=10**D && Math.random()<0.5) continue;
    const n = op==='+' ? D+1 : D;
    const {c} = wCompute(a,b,op,n);
    const carries = c.filter(x=>x>0).length;
    if(carries<2 || carries>D-1) continue;
    return {a,b,op,n};
  }
  return {a:705100,b:13080,op:'-',n:6};
}
function wNew(){
  Object.assign(W, wGen()); W.solved=false; W.shown=false;
  W.exp = wCompute(W.a,W.b,W.op,W.n);
  W.res = W.op==='+' ? W.a+W.b : W.a-W.b;
  wBuild();
  setMsg($('#w-msg'),'');
  $('#w-note').textContent = W.op==='+'
    ? 'Plus: Zähle Spalte für Spalte von rechts zusammen. Ist die Summe 10 oder mehr, schreibst du die Einer unter den Strich und den Behalte klein in die nächste Spalte über den Strich.'
    : 'Minus mit Ergänzen: Rechne unten + Behalte, dann ergänze bis zur oberen Ziffer. Geht das nicht, ergänzt du bis zur oberen Ziffer + 10 und schreibst den Behalte 1 klein in die nächste Spalte über den Strich.';
}
function wBuild(){
  const g = $('#w-grid'), n = W.n;
  g.style.gridTemplateColumns = `repeat(${n+1}, auto)`;
  const sa = String(W.a), sb = String(W.b);
  let h = '<div class="head"></div>';
  for(let col=n-1; col>=0; col--) h += `<div class="head">${PLACES[col]}</div>`;
  // Zeile 1: obere Zahl
  h += '<div></div>';
  for(let p=n-1;p>=0;p--) h += `<div>${p<sa.length ? sa[sa.length-1-p] : ''}</div>`;
  // Zeile 2: untere Zahl
  h += `<div class="opc">${W.op==='+'?'+':MINUS}</div>`;
  for(let p=n-1;p>=0;p--) h += `<div>${p<sb.length ? sb[sb.length-1-p] : ''}</div>`;
  // Zeile 3: Behalte über dem Strich
  h += '<div class="carry"></div>';
  for(let p=n-1;p>=0;p--){
    h += p===0 ? '<div class="carry"></div>'
      : `<div class="carry"><input class="cc" id="w-c${p}" data-p="${p}" data-k="c" inputmode="numeric" autocomplete="off" aria-label="Behalte in der Spalte ${PLACES[p]}"></div>`;
  }
  // Zeile 4: Ergebnis
  h += '<div class="res"></div>';
  for(let p=n-1;p>=0;p--) h += `<div class="res"><input class="cell" id="w-r${p}" data-p="${p}" data-k="r" inputmode="numeric" autocomplete="off" aria-label="Ergebnis in der Spalte ${PLACES[p]}"></div>`;
  g.innerHTML = h;
  g.querySelectorAll('input').forEach(i => {
    i.addEventListener('input', () => {
      i.value = i.value.replace(/\D/g,'').slice(-1);
      i.classList.remove('ok','bad','shown');
      if(i.value==='') return;
      const p = Number(i.dataset.p);
      // Reihenfolge: Ergebnis-Ziffer → Behalte der nächsten Spalte → nächste Ergebnis-Ziffer
      const next = i.dataset.k==='r' ? (KR.getElementById('w-c'+(p+1)) || KR.getElementById('w-r'+(p+1))) : KR.getElementById('w-r'+p);
      next?.focus(); next?.select?.();
    });
    i.addEventListener('keydown', e => {
      if(e.key==='Enter') wCheck();
      if(e.key==='Backspace' && i.value===''){
        const p = Number(i.dataset.p);
        const prev = i.dataset.k==='r' ? KR.getElementById('w-c'+p) || KR.getElementById('w-r'+(p-1)) : KR.getElementById('w-r'+(p-1));
        if(prev){ e.preventDefault(); prev.focus(); }
      }
    });
  });
  setTimeout(() => $('#w-r0')?.focus(), 30);
}
function wCheck(){
  const n = W.n, rs = String(W.res);
  let badR = 0, badC = 0, emptyR = 0;
  for(let p=0;p<n;p++){
    const el = KR.getElementById('w-r'+p), v = el.value;
    const leading = p >= rs.length;
    const ok = leading ? (v==='' || v==='0') : v===String(W.exp.r[p]);
    if(!leading && v==='') emptyR++;
    el.classList.toggle('ok', ok && v!==''); el.classList.toggle('bad', !ok);
    if(!ok) badR++;
  }
  for(let p=1;p<n;p++){
    const el = KR.getElementById('w-c'+p), v = el.value, e = W.exp.c[p];
    const ok = e===0 ? (v===''||v==='0') : v===String(e);
    el.classList.toggle('ok', ok && v!==''); el.classList.toggle('bad', !ok);
    if(!ok) badC++;
  }
  const msg = $('#w-msg');
  if(emptyR===rs.length){ setMsg(msg,'Beginne ganz rechts bei den Einern.','info'); return; }
  if(badR===0 && badC===0){
    setMsg(msg, `Richtig, auch alle Behalte! ${fmt(W.a)} ${W.op==='+'?'+':MINUS} ${fmt(W.b)} = ${fmt(W.res)}`, 'ok');
    if(!W.solved && !W.shown){ SOLVED('schrift-' + W.len); W.solved = true; W.score++; $('#w-score').textContent = `Richtig gelöst: ${W.score}`; }
    return;
  }
  const parts = [];
  if(badR) parts.push(badR===1 ? '1 Ergebnisziffer stimmt nicht' : `${badR} Ergebnisziffern stimmen nicht`);
  if(badC) parts.push(badC===1 ? '1 Behalte fehlt oder ist falsch' : `${badC} Behalte fehlen oder sind falsch`);
  const txt = parts.join(', ') + '.';
  setMsg(msg, txt.charAt(0).toUpperCase() + txt.slice(1) + ' Schau dir die roten Felder nochmals an.', badR ? 'bad' : 'info');
}
function wShow(){
  W.shown = true;
  const rs = String(W.res);
  for(let p=0;p<W.n;p++){ const el = KR.getElementById('w-r'+p); el.value = p<rs.length ? W.exp.r[p] : ''; el.className='cell shown'; }
  for(let p=1;p<W.n;p++){ const el = KR.getElementById('w-c'+p); el.value = W.exp.c[p] ? W.exp.c[p] : ''; el.className='cc shown'; }
  setMsg($('#w-msg'), 'So sieht die Lösung aus. Vergleiche mit deinem Weg und versuche dann eine neue Rechnung.', 'info');
}
$('#w-check').onclick = wCheck;
$('#w-show').onclick = wShow;
$('#w-new').onclick = wNew;
wNew();

// Startansicht (Deep-Link per #kopf, #strich, #schriftlich)

return show;
},
"mal": function (KR, EXIT, STAR, SOLVED, ANS) {

// ---------- Hilfsfunktionen ----------
const $ = s => KR.querySelector(s);
const rnd = (a,b) => a + Math.floor(Math.random()*(b-a+1));
const pick = arr => arr[Math.floor(Math.random()*arr.length)];
const fmt = n => String(n).replace(/\B(?=(\d{3})+(?!\d))/g,' ');
const parse = s => { const t = String(s).replace(/[\s'’.  ]/g,''); return /^\d+$/.test(t) ? Number(t) : null; };
const zerosOf = n => { let z=0; while(n>0 && n%10===0){ n/=10; z++; } return z; };
const core = n => n / 10**zerosOf(n);
const nullen = z => z===1 ? '1 Null' : z + ' Nullen';

// ---------- Navigation ----------
const views = ['home','kopf','schriftlich'];
function show(id){
  if(!views.includes(id)) id='home';
  views.forEach(v => KR.getElementById(v).hidden = v!==id);
  window.scrollTo(0,0);
  if(id==='kopf') focusKopf();
  if(id==='schriftlich') wFocusStart();
}
KR.querySelectorAll('[data-go]').forEach(b => b.addEventListener('click', () => {
  const id = b.dataset.go;
  show(id);
}));

function seg(name, onChange){
  const el = KR.querySelector(`.seg[data-for="${name}"]`);
  el.querySelectorAll('button').forEach(b => b.addEventListener('click', () => {
    el.querySelectorAll('button').forEach(x => x.setAttribute('aria-pressed', x===b ? 'true':'false'));
    onChange(b.dataset.lv ?? b.dataset.v);
  }));
  const cur = el.querySelector('[aria-pressed="true"]');
  return cur.dataset.lv ?? cur.dataset.v;
}
function setMsg(el, text, kind){ el.textContent = text; el.className = 'msg ' + (kind||''); }

// =========================================================
// 1) NULLENTRICK
// =========================================================
const K = { lv: 2, tasks: [], i: 0, results: [], answered: false, round: 1, first: true };
const K_LEVEL_TEXT = {
  1: 'Leicht: Eine Zahl ist einstellig, z. B. 40 · 7 oder 3 · 600.',
  2: 'Mittel: Beide Zahlen haben Nullen, z. B. 30 · 80 oder 500 · 60.',
  3: 'Schwer: Viele Nullen und Fallen mit der 5, z. B. 600 · 600 oder 50 · 400.'
};
K.lv = Number(seg('kopf', v => { K.lv = Number(v); K.round = 1; kNewRound(); focusKopf(); }));

function kGen(lv){
  for(let t=0;t<500;t++){
    let a, b;
    if(lv===1){ a = rnd(2,9)*10**rnd(1,3); b = rnd(2,9); }
    else if(lv===2){ const m1 = rnd(1,2), m2 = m1===2 ? 1 : rnd(1,2); a = rnd(2,9)*10**m1; b = rnd(2,9)*10**m2; }
    else {
      const m = rnd(3,5), m1 = rnd(1,m-1), m2 = m-m1;
      let d1 = rnd(2,9), d2 = rnd(2,9);
      if(Math.random()<0.4){ d1 = 5; d2 = pick([2,4,6,8]); }
      a = d1*10**m1; b = d2*10**m2;
    }
    if(a*b >= 1000000) continue;
    if(Math.random()<0.5) [a,b] = [b,a];
    return {a,b};
  }
  return {a:30,b:80};
}
function kNewRound(){
  const seen = new Set(); K.tasks = [];
  if(K.first && K.lv===2){ K.tasks.push({a:30,b:80},{a:500,b:60}); seen.add('30x80'); seen.add('500x60'); }
  K.first = false;
  let g=0; while(K.tasks.length<10 && g++<500){ const t = kGen(K.lv), k = t.a+'x'+t.b; if(!seen.has(k)){ seen.add(k); K.tasks.push(t); } }
  K.i = 0; K.results = []; K.answered = false;
  $('#k-level').textContent = K_LEVEL_TEXT[K.lv];
  kRender();
}
function kRender(){
  const dots = $('#k-dots'); dots.innerHTML = '';
  K.tasks.forEach((_,j) => {
    const d = document.createElement('span');
    d.className = 'dot' + (K.results[j]===true?' ok':K.results[j]===false?' bad':j===K.i?' now':'');
    dots.appendChild(d);
  });
  $('#k-score').textContent = `Runde ${K.round} · ${K.results.filter(Boolean).length} richtig`;
  const body = $('#k-body'), btns = $('#k-btns');
  setMsg($('#k-msg'),'');
  btns.innerHTML = '';
  if(K.i >= K.tasks.length){
    const n = K.results.filter(Boolean).length;
    body.innerHTML = `<div class="task">${n} von 10 richtig</div>` + STAR('kopf-' + K.lv, n>=9 ? 3 : n>=6 ? 2 : 1);
    setMsg($('#k-msg'), n>=9 ? 'Ausgezeichnet! Probiere die nächste Schwierigkeit.' : n>=6 ? 'Gut gemacht. Mit einer weiteren Runde wirst du noch sicherer.' : 'Übe noch eine Runde. Denk an den Tipp unten.', n>=6?'ok':'info');
    const b = document.createElement('button'); b.className='btn primary'; b.textContent='Neue Runde';
    b.onclick = () => { K.round++; kNewRound(); focusKopf(); };
    btns.appendChild(b); b.focus(); return;
  }
  const t = K.tasks[K.i];
  body.innerHTML = `<div class="task"><span class="num">${fmt(t.a)}</span><span>·</span><span class="num">${fmt(t.b)}</span><span>=</span><input class="field" id="k-in" inputmode="numeric" autocomplete="off" aria-label="Deine Antwort"></div>`;
  const b = document.createElement('button'); b.className='btn primary'; b.id='k-go'; b.textContent='Prüfen';
  b.onclick = kStep; btns.appendChild(b);
  const tb = document.createElement('button'); tb.className='btn'; tb.id='k-tip'; tb.textContent='Tipp';
  tb.onclick = () => { const ca = core(t.a), cb = core(t.b), z = zerosOf(t.a)+zerosOf(t.b);
    setMsg($('#k-msg'), `Lass zuerst alle Nullen weg und rechne ${ca} · ${cb}. Dann hängst du ${nullen(z)} an.` + ((ca*cb)%10===0 ? ` Achtung: ${ca} · ${cb} gibt selbst schon eine Null, die bleibt auch stehen.` : ''), 'info'); $('#k-in').focus(); };
  btns.appendChild(tb);
  $('#k-in').addEventListener('keydown', e => { if(e.key==='Enter') kStep(); });
  K.answered = false;
}
function kStep(){
  if(K.answered){ K.i++; kRender(); focusKopf(); return; }
  const inp = $('#k-in'), v = parse(inp.value), t = K.tasks[K.i];
  if(v===null){ setMsg($('#k-msg'),'Schreibe eine Zahl ins Feld.','info'); inp.focus(); return; }
  const ans = t.a*t.b, ok = v===ans;
  K.results[K.i] = ok; K.answered = true; ANS(ok); $('#k-tip')?.remove();
  inp.classList.add(ok?'ok':'bad'); inp.readOnly = true;
  const ca = core(t.a), cb = core(t.b), z = zerosOf(t.a)+zerosOf(t.b);
  const how = `${ca} · ${cb} = ${ca*cb}, dazu ${nullen(z)} → ${fmt(ans)}.`;
  setMsg($('#k-msg'), ok ? 'Richtig! ' + how : 'Leider nein. ' + how, ok?'ok':'bad');
  $('#k-go').textContent = K.i===9 ? 'Auswertung' : 'Weiter';
  $('#k-go').focus();
  $('#k-dots').children[K.i].className = 'dot ' + (ok?'ok':'bad');
  $('#k-score').textContent = `Runde ${K.round} · ${K.results.filter(Boolean).length} richtig`;
}
function focusKopf(){ setTimeout(() => $('#k-in')?.focus(), 30); }
kNewRound();

// =========================================================
// 2) SCHRIFTLICH  (kleine Zahl links · zuerst Einer, dann Zehner, dann Hunderter)
// =========================================================
const W = { len:1, score:0, solved:false, shown:false, firsts:{1:[8,647],2:[18,647],3:[590,622]} };
const PL = ['E','Z','H'], PLN = ['Einer','Zehner','Hunderter'], PCOL = ['grün','blau','violett'];
W.len = Number(seg('wlen', v => { W.len = Number(v); wNew(); }));

function wGen(len){
  if(W.firsts[len]){ const f = W.firsts[len]; W.firsts[len] = null; return {m:f[0], a:f[1]}; }
  for(let t=0;t<500;t++){
    let m, a;
    if(len===1){ m = rnd(3,9); a = Math.random()<0.6 ? rnd(234,989) : rnd(1012,4987); }
    else if(len===2){ do{ m = rnd(12,89); }while(m%10===0 || m%11===0); a = Math.random()<0.7 ? rnd(213,987) : rnd(1012,2987); }
    else { m = Math.random()<0.25 ? rnd(2,8)*100 + rnd(1,9)*10 : rnd(213,789); a = rnd(Math.max(m+1,312), 989); }
    if(a%10===0 || m>=a || m*a>=1000000) continue;
    return {m,a};
  }
  return {m:8,a:647};
}
function wNote(){
  if(W.len===1) return `Rechne von rechts nach links: zuerst ${W.m} · ${String(W.a).slice(-1)} Einer, dann die Zehner usw. Den Behalte schreibst du klein über den Strich, eine Spalte weiter links.`;
  const used = W.rows.map(r => `${PLN[r.k]} (${PCOL[r.k]})`).join(', dann ');
  return `Zuerst ${used}. Die Behalte vom Malrechnen schreibst du klein über den Strich, jeweils in die Reihe mit der passenden Farbe. In jeder neuen Zeile steht rechts eine Null mehr, sie ist schon eingetragen. Zum Schluss addierst du die Zeilen; diese Behalte kommen über den Schlussstrich.` + (String(W.m).includes('0') ? ' Die Null im Multiplikator braucht keine eigene Zeile.' : '');
}
function wNew(){
  Object.assign(W, wGen(W.len)); W.solved=false; W.shown=false;
  wBuild();
  setMsg($('#w-msg'),'');
  $('#w-note').textContent = wNote();
}
function wBuild(){
  const ms = String(W.m), as = String(W.a), expr = ms + '·' + as, res = W.m*W.a;
  const rows = [];
  if(ms.length>1){
    for(let k=0;k<ms.length;k++){ const d = +ms[ms.length-1-k]; if(d===0) continue; rows.push({k, d, exp:W.a*d, len:String(W.a*d).length + k}); }
  }
  const n = Math.max(expr.length, String(res).length, ...rows.map(r=>r.len)) + 1;
  const exOff = n - expr.length;
  const kcol = {}; for(let i=0;i<ms.length;i++) kcol[ms.length-1-i] = exOff + i;
  W.rows = rows; W.res = res; W.n = n; W.kcol = kcol;

  const g = $('#w-grid');
  g.style.gridTemplateColumns = `repeat(${n}, auto) auto`;
  let h = '';
  // Aufgabe: kleine Zahl links
  for(let c=0;c<n;c++){
    const i = c - exOff, ch = i>=0 ? expr[i] : '';
    let cls = 'ex';
    if(ch==='·') cls += ' opc';
    else if(i>=0 && i<ms.length) cls += ' p' + (ms.length-1-i);
    h += `<div class="${cls}" id="w-x${c}">${ch}</div>`;
  }
  h += '<div class="ex"></div>';
  // Teilprodukte: Einer, Zehner, Hunderter
  // Alle Behalte vom Malrechnen über dem Strich unter der Aufgabe (eine farbige Reihe pro Zeile)
  rows.forEach((r,ri) => {
    const mc = ri===rows.length-1 ? 'carry' : 'mcr';
    for(let c=0;c<n;c++) h += c < n-1-r.k
      ? `<div class="${mc}"><input class="cc t${r.k}" id="w-m${ri}-${c}" data-row="m${ri}" data-c="${c}" inputmode="numeric" autocomplete="off" aria-label="Behalte ${PLN[r.k]}zeile, Spalte ${c+1}"></div>`
      : `<div class="${mc}"></div>`;
    h += `<div class="${mc}"></div>`;
  });
  rows.forEach((r,ri) => {
    for(let c=0;c<n;c++){
      if(c > n-1-r.k) h += `<div class="pp zero p${r.k}">0</div>`;
      else h += `<div class="pp"><input class="cell t${r.k}" id="w-p${ri}-${c}" data-row="${ri}" data-c="${c}" inputmode="numeric" autocomplete="off" aria-label="${PLN[r.k]}zeile, Spalte ${c+1}"></div>`;
    }
    h += `<div class="pp"><span class="tag t${r.k}">${PL[r.k]}</span></div>`;
  });
  // Behalte über dem Strich
  for(let c=0;c<n;c++) h += c<n-1
    ? `<div class="carry"><input class="cc" id="w-c${c}" data-row="c" data-c="${c}" inputmode="numeric" autocomplete="off" aria-label="Behalte, Spalte ${c+1}"></div>`
    : '<div class="carry"></div>';
  h += '<div class="carry"></div>';
  // Ergebnis
  for(let c=0;c<n;c++) h += `<div class="res"><input class="cell" id="w-r${c}" data-row="r" data-c="${c}" inputmode="numeric" autocomplete="off" aria-label="Ergebnis, Spalte ${c+1}"></div>`;
  h += '<div class="res"></div>';
  g.innerHTML = h;

  $('#w-legend').innerHTML = rows.length
    ? '<span>Tippe von rechts nach links</span><span>Farbige kleine Felder über dem Strich = Behalte vom Malrechnen</span><span><i class="sw t0"></i>Einer</span><span><i class="sw t1"></i>Zehner</span>' + (ms.length>2 ? '<span><i class="sw t2"></i>Hunderter</span>' : '') + '<span><b>Behalte</b> vom Addieren = über dem Schlussstrich</span>'
    : '<span>Tippe von rechts nach links</span><span>Gelb = die Ziffer, mit der du rechnest</span><span><b>Behalte</b> = kleines Feld über dem Strich</span>';

  const rowIds = [...rows.map((_,i)=>'m'+i), ...rows.map((_,i)=>String(i)), 'c', 'r'];
  const cellOf = (row, c) => KR.getElementById(row==='c' ? 'w-c'+c : row==='r' ? 'w-r'+c : row[0]==='m' ? `w-m${row.slice(1)}-${c}` : `w-p${row}-${c}`);
  g.querySelectorAll('input').forEach(i => {
    const row = i.dataset.row, c = Number(i.dataset.c);
    i.addEventListener('focus', () => {
      i.select();
      const r = rows[Number(row[0]==='m' ? row.slice(1) : row)];
      if(r) KR.getElementById('w-x'+kcol[r.k]).classList.add('now');
      else if(!rows.length && row==='r') KR.getElementById('w-x'+kcol[0]).classList.add('now');
    });
    i.addEventListener('blur', () => g.querySelectorAll('.now').forEach(x => x.classList.remove('now')));
    i.addEventListener('input', () => {
      i.value = i.value.replace(/\D/g,'').slice(-1);
      i.classList.remove('ok','bad','shown');
      if(i.value!=='' && row!=='c' && row[0]!=='m'){ const nx = cellOf(row, c-1); nx?.focus(); }
    });
    i.addEventListener('keydown', e => {
      const ri = rowIds.indexOf(row);
      const go = (r2, c2) => { const t = cellOf(r2, c2); if(t){ e.preventDefault(); t.focus(); } };
      if(e.key==='Enter'){ e.preventDefault(); wCheck(); }
      else if(e.key==='Backspace' && i.value===''){ const nx = cellOf(row, c+1); if(nx){ e.preventDefault(); nx.value=''; nx.focus(); } }
      else if(e.key==='ArrowLeft') go(row, c-1);
      else if(e.key==='ArrowRight') go(row, c+1);
      else if(e.key==='ArrowUp' && ri>0) go(rowIds[ri-1], c);
      else if(e.key==='ArrowDown' && ri<rowIds.length-1) go(rowIds[ri+1], c);
    });
  });
  wFocusStart();
}
function wFocusStart(){
  setTimeout(() => {
    const first = W.rows && W.rows.length ? KR.getElementById(`w-p0-${W.n-1-W.rows[0].k}`) : KR.getElementById('w-r'+(W.n-1));
    first?.focus();
  }, 30);
}
function wRead(cells){
  const s = cells.map(c => c.value || ' ').join('');
  if(!s.trim()) return {empty:true};
  return { empty:false, val:Number(s.replace(/ /g,'')), gap:/\d +\d/.test(s.trim()), endOk:s[s.length-1]!==' ' };
}
function wCarries(){
  // erwartete Behalte, Spalte → Ziffer
  const out = {}, n = W.n;
  if(!W.rows.length){
    const da = String(W.a).split('').reverse().map(Number); let c = 0;
    da.forEach((x,p) => { c = Math.floor((W.m*x + c)/10); if(c) out[n-2-p] = c; });
  } else {
    const vals = W.rows.map(r => r.exp * 10**r.k); let c = 0;
    for(let p=0;p<n;p++){ const s = vals.reduce((t,v) => t + Math.floor(v/10**p)%10, 0) + c; c = Math.floor(s/10); if(c && n-2-p>=0) out[n-2-p] = c; }
  }
  return out;
}
function wCheck(){
  const msgs = []; let all = true, any = false;
  const check = (cells, exp, label, endHint) => {
    const x = wRead(cells);
    cells.forEach(c => c.classList.remove('ok','bad','shown'));
    if(x.empty){ all = false; msgs.push(label + ' fehlt noch.'); return; }
    any = true;
    const good = !x.gap && x.endOk && x.val===exp;
    cells.forEach(c => { if(c.value!=='') c.classList.add(good ? 'ok' : 'bad'); });
    if(good) return;
    all = false;
    if(!x.gap && !x.endOk && x.val===exp) msgs.push(label + ': Die Zahl stimmt, aber sie muss ' + endHint + ' enden.');
    else if(x.gap) msgs.push(label + ': Da ist eine Lücke zwischen den Ziffern.');
    else msgs.push(label + ' stimmt noch nicht.');
  };
  W.rows.forEach((r,ri) => {
    const cells = []; for(let c=0;c<=W.n-1-r.k;c++) cells.push(KR.getElementById(`w-p${ri}-${c}`));
    check(cells, r.exp, `Die ${PLN[r.k]}zeile (${r.d} · ${W.a})`, r.k ? 'direkt vor der Null' : 'ganz rechts');
  });
  const rc = []; for(let c=0;c<W.n;c++) rc.push(KR.getElementById('w-r'+c));
  check(rc, W.res, 'Das Ergebnis', 'ganz rechts');
  const msg = $('#w-msg');
  if(!any){ setMsg(msg, W.rows.length ? 'Beginne mit der grünen Einerzeile ganz rechts.' : 'Beginne ganz rechts bei den Einern.', 'info'); return; }
  if(all){
    setMsg(msg, `Richtig! ${fmt(W.m)} · ${fmt(W.a)} = ${fmt(W.res)}`, 'ok');
    if(!W.solved && !W.shown){ SOLVED('schrift-' + W.len); W.solved = true; W.score++; $('#w-score').textContent = `Richtig gelöst: ${W.score}`; }
    return;
  }
  setMsg(msg, msgs.join(' ') + ' Schau dir die roten Felder nochmals an.', 'bad');
}
function wShow(){
  W.shown = true;
  const fill = (ids, val) => {
    const s = String(val);
    ids.forEach((id,c) => { const el = KR.getElementById(id); const k = c - (ids.length - s.length); el.value = k>=0 ? s[k] : ''; el.classList.remove('ok','bad'); el.classList.add('shown'); });
  };
  W.rows.forEach((r,ri) => { const ids = []; for(let c=0;c<=W.n-1-r.k;c++) ids.push(`w-p${ri}-${c}`); fill(ids, r.exp); });
  const ids = []; for(let c=0;c<W.n;c++) ids.push('w-r'+c); fill(ids, W.res);
  const car = wCarries();
  for(let c=0;c<W.n-1;c++){ const el = KR.getElementById('w-c'+c); el.value = car[c] || ''; el.classList.add('shown'); }
  W.rows.forEach((r,ri) => {
    const da = String(W.a).split('').reverse().map(Number); let cc = 0;
    da.forEach((x,p) => { cc = Math.floor((r.d*x + cc)/10); const el = KR.getElementById(`w-m${ri}-${W.n-2-r.k-p}`); if(el){ el.value = cc || ''; el.classList.add('shown'); } });
  });
  setMsg($('#w-msg'), 'So sieht die Lösung aus. Vergleiche mit deinem Weg und versuche dann eine neue Rechnung.', 'info');
}
$('#w-check').onclick = wCheck;
$('#w-show').onclick = wShow;
$('#w-new').onclick = wNew;
wNew();

// Startansicht (Deep-Link per #kopf oder #schriftlich)

return show;
},
"durch": function (KR, EXIT, STAR, SOLVED, ANS) {

// ---------- Hilfsfunktionen ----------
const $ = s => KR.querySelector(s);
const rnd = (a,b) => a + Math.floor(Math.random()*(b-a+1));
const pick = arr => arr[Math.floor(Math.random()*arr.length)];
const fmt = n => String(n).replace(/\B(?=(\d{3})+(?!\d))/g,' ');
const parse = s => { const t = String(s).replace(/[\s'’.  ]/g,''); return /^\d+$/.test(t) ? Number(t) : null; };
const zerosOf = n => { let z=0; while(n>0 && n%10===0){ n/=10; z++; } return z; };
const nullen = z => z===1 ? '1 Null' : z + ' Nullen';

// Vorschau Schriftlich
(function(){
  const rows = [
    ['','8','4','6',':','3','=','q2','q8','q2'],
    ['-u','pu6','','','','','','','',''],
    ['','2','d4','','','','','','',''],
    ['-u','pu2','pu4','','','','','','',''],
    ['','','0','d6','','','','','',''],
    ['','','-u','pu6','','','','','',''],
    ['','','','0','','','','','','']
  ];
  let h='';
  rows.forEach(r => r.forEach(c => {
    let cls='', t=c;
    if(c[0]==='-'){ t='−'; cls='p'+(c.includes('u')?' ul':''); }
    else if(c[0]==='q'){ cls='q'; t=c.slice(1); }
    else if(c[0]==='d'){ cls='d'; t=c.slice(1); }
    else if(c[0]==='p'){ cls='p ul'; t=c.slice(2); }
    h += `<span class="${cls}">${t}</span>`;
  }));
  $('#mini').innerHTML = h;
})();

// ---------- Navigation ----------
const views = ['home','kopf','schriftlich'];
function show(id){
  if(!views.includes(id)) id='home';
  views.forEach(v => KR.getElementById(v).hidden = v!==id);
  window.scrollTo(0,0);
  if(id==='kopf') focusKopf();
  if(id==='schriftlich') sFocus();
}
KR.querySelectorAll('[data-go]').forEach(b => b.addEventListener('click', () => {
  const id = b.dataset.go;
  show(id);
}));

function seg(name, onChange){
  const el = KR.querySelector(`.seg[data-for="${name}"]`);
  el.querySelectorAll('button').forEach(b => b.addEventListener('click', () => {
    el.querySelectorAll('button').forEach(x => x.setAttribute('aria-pressed', x===b ? 'true':'false'));
    onChange(b.dataset.lv ?? b.dataset.v);
  }));
  const cur = el.querySelector('[aria-pressed="true"]');
  return cur.dataset.lv ?? cur.dataset.v;
}
function setMsg(el, text, kind){ el.textContent = text; el.className = 'msg ' + (kind||''); }

// =========================================================
// 1) NULLENTRICK
// =========================================================
const K = { lv: 1, tasks: [], i: 0, results: [], answered: false, round: 1, tip:false,
  firsts: {1:[{a:21000,b:7},{a:2100,b:7}], 2:[{a:21000,b:70},{a:2100,b:70}], 3:[{a:4000,b:5},{a:30000,b:600}]} };
const K_LEVEL_TEXT = {
  1: 'Leicht: Nur die erste Zahl hat Nullen, z. B. 2 100 : 7 oder 21 000 : 7. Denk die Nullen weg und häng sie beim Resultat wieder an.',
  2: 'Mittel: Beide Zahlen haben Nullen, z. B. 21 000 : 70. Streiche zuerst bei beiden Zahlen gleich viele Nullen.',
  3: 'Schwer: Viele Nullen und Fallen, z. B. 4 000 : 5 oder 30 000 : 600.'
};
K.lv = Number(seg('kopf', v => { K.lv = Number(v); K.round = 1; kNewRound(); focusKopf(); }));

// Zerlegt a : b in gestrichene Nullen (s), Grundaufgabe (base : d) und weggedachte Nullen (k)
function analyse(a,b){
  const s = zerosOf(b), A = a/10**s, d = b/10**s;
  let k = zerosOf(A);
  while(k>0 && (A/10**k) % d !== 0) k--;
  const base = A/10**k;
  return { s, k, A, d, base, q: base/d, ans: a/b };
}
function kGen(lv){
  for(let t=0;t<500;t++){
    let d = rnd(2,9), q = rnd(2,9), base = d*q, s = 0, k;
    if(lv===1){ if(base%10===0) continue; k = rnd(1,4); }
    else if(lv===2){ if(base%10===0) continue; s = rnd(1,3); k = rnd(0,3); }
    else {
      if(Math.random()<0.45){ const pr = pick([[5,2],[5,4],[5,6],[5,8],[2,5],[4,5],[6,5],[8,5]]); d = pr[0]; q = pr[1]; base = d*q; s = rnd(0,3); }
      else { if(base%10===0) continue; s = rnd(1,3); }
      k = rnd(1,3);
    }
    const a = base*10**(k+s), b = d*10**s;
    if(a>1000000 || a<100) continue;
    return {a,b};
  }
  return {a:2100,b:7};
}
function kNewRound(){
  const seen = new Set(); K.tasks = [];
  if(K.firsts[K.lv]){ K.firsts[K.lv].forEach(t => { K.tasks.push(t); seen.add(t.a+':'+t.b); }); K.firsts[K.lv] = null; }
  let g=0; while(K.tasks.length<10 && g++<500){ const t = kGen(K.lv), key = t.a+':'+t.b; if(!seen.has(key)){ seen.add(key); K.tasks.push(t); } }
  K.i = 0; K.results = []; K.answered = false;
  $('#k-level').textContent = K_LEVEL_TEXT[K.lv];
  kRender();
}
// Zahl mit gestrichenen (rot) und weggedachten (grau) Nullen
function numHTML(n, strike, fade){
  const s = String(n), L = s.length; let h = '';
  for(let i=0;i<L;i++){
    if(i>0 && (L-i)%3===0) h += ' ';
    const r = L-1-i;
    const cls = r<strike ? 'z-strk' : r<strike+fade ? 'z-fade' : '';
    h += cls ? `<span class="${cls}">${s[i]}</span>` : s[i];
  }
  return h;
}
function kTask(marked){
  const t = K.tasks[K.i], x = analyse(t.a,t.b);
  $('#k-a').innerHTML = marked ? numHTML(t.a, x.s, x.k) : fmt(t.a);
  $('#k-b').innerHTML = marked ? numHTML(t.b, x.s, 0) : fmt(t.b);
  if(marked){
    let h = '';
    if(x.s) h += `<span class="chip s">${nullen(x.s)} gestrichen</span>`;
    h += `<span class="chip c">Grundaufgabe: ${x.base} : ${x.d}</span>`;
    if(x.k) h += `<span class="chip f">${nullen(x.k)} weggedacht</span>`;
    $('#k-core').innerHTML = h;
  }
}
function kRender(){
  const dots = $('#k-dots'); dots.innerHTML = '';
  K.tasks.forEach((_,j) => {
    const d = document.createElement('span');
    d.className = 'dot' + (K.results[j]===true?' ok':K.results[j]===false?' bad':j===K.i?' now':'');
    dots.appendChild(d);
  });
  $('#k-score').textContent = `Runde ${K.round} · ${K.results.filter(Boolean).length} richtig`;
  const body = $('#k-body'), btns = $('#k-btns');
  setMsg($('#k-msg'),'');
  btns.innerHTML = '';
  if(K.i >= K.tasks.length){
    const n = K.results.filter(Boolean).length;
    body.innerHTML = `<div class="task">${n} von 10 richtig</div>` + STAR('kopf-' + K.lv, n>=9 ? 3 : n>=6 ? 2 : 1);
    setMsg($('#k-msg'), n>=9 ? 'Ausgezeichnet! Probiere die nächste Schwierigkeit.' : n>=6 ? 'Gut gemacht. Mit einer weiteren Runde wirst du noch sicherer.' : 'Übe noch eine Runde. Drück bei Unsicherheit auf «Tipp».', n>=6?'ok':'info');
    const b = document.createElement('button'); b.className='btn primary'; b.textContent='Neue Runde';
    b.onclick = () => { K.round++; kNewRound(); focusKopf(); };
    btns.appendChild(b); b.focus(); return;
  }
  body.innerHTML = `<div class="task"><span class="num" id="k-a"></span><span>:</span><span class="num" id="k-b"></span><span>=</span><input class="field" id="k-in" inputmode="numeric" autocomplete="off" aria-label="Deine Antwort"></div><div class="core" id="k-core"></div>`;
  kTask(false);
  const b = document.createElement('button'); b.className='btn primary'; b.id='k-go'; b.textContent='Prüfen';
  b.onclick = kStep; btns.appendChild(b);
  const tb = document.createElement('button'); tb.className='btn'; tb.id='k-tip'; tb.textContent='Tipp';
  tb.onclick = kTip; btns.appendChild(tb);
  $('#k-in').addEventListener('keydown', e => { if(e.key==='Enter'){ e.preventDefault(); kStep(); } });
  K.answered = false;
}
function kTip(){
  const t = K.tasks[K.i], x = analyse(t.a,t.b);
  kTask(true);
  let s = '';
  if(x.s) s += `Streiche bei beiden Zahlen ${nullen(x.s)} (rot). `;
  s += x.k ? `Denk die grauen Nullen weg und rechne ${x.base} : ${x.d}. Die grauen Nullen hängst du am Schluss wieder an.` : `Rechne jetzt ${x.base} : ${x.d}.`;
  setMsg($('#k-msg'), s, 'info');
  $('#k-in').focus();
}
function kStep(){
  if(K.answered){ if(Date.now() - K.at < 700) return; K.i++; kRender(); focusKopf(); return; }
  const inp = $('#k-in'), v = parse(inp.value), t = K.tasks[K.i];
  if(v===null){ setMsg($('#k-msg'),'Schreibe eine Zahl ins Feld.','info'); inp.focus(); return; }
  const x = analyse(t.a,t.b), ok = v===x.ans;
  K.results[K.i] = ok; K.answered = true; ANS(ok); K.at = Date.now();
  inp.classList.add(ok?'ok':'bad'); inp.readOnly = true;
  if(!ok) inp.insertAdjacentHTML('afterend', `<span class="sol num" aria-label="Richtige Lösung">${fmt(x.ans)}</span>`);
  kTask(true);
  let how = '';
  if(x.s) how += `Streiche bei beiden ${nullen(x.s)}: ${fmt(t.a/10**x.s)} : ${x.d}. `;
  how += `${x.base} : ${x.d} = ${x.q}` + (x.k ? `, dazu ${nullen(x.k)} → ${fmt(x.ans)}.` : '.');
  if(x.base%10===0) how += ` Achtung: Die Null in ${x.base} gehört zur Grundaufgabe.`;
  setMsg($('#k-msg'), ok ? 'Richtig! ' + how : `Die richtige Lösung ist ${fmt(x.ans)}. So geht es: ` + how, ok?'ok':'info');
  $('#k-tip')?.remove();
  $('#k-go').textContent = K.i===9 ? 'Auswertung' : 'Weiter';
  setTimeout(() => $('#k-go')?.focus(), 50);
  $('#k-dots').children[K.i].className = 'dot ' + (ok?'ok':'bad');
  $('#k-score').textContent = `Runde ${K.round} · ${K.results.filter(Boolean).length} richtig`;
}
function focusKopf(){ setTimeout(() => $('#k-in')?.focus(), 30); }
kNewRound();

// =========================================================
// 2) SCHRIFTLICH  (geführt: Weiter prüft das aktuelle Feld und springt zum nächsten)
// =========================================================
const S = { lv:'1', score:0, firsts:{'1':[846,3],'R':[847,3],'2':[966,23],'3':[79500,150]} };
S.lv = seg('slv', v => { S.lv = v; sNew(); });

function sGen(lv){
  if(S.firsts[lv]){ const f = S.firsts[lv]; S.firsts[lv] = null; return {a:f[0], d:f[1]}; }
  for(let t=0;t<500;t++){
    let d, a;
    if(lv==='1'){ d = rnd(2,9); a = d * (Math.random()<0.6 ? rnd(102,999) : rnd(1001,2499)); }
    else if(lv==='R'){ d = rnd(3,9); a = d * (Math.random()<0.6 ? rnd(102,999) : rnd(1001,2499)) + rnd(1,d-1); }
    else if(lv==='3'){ d = Math.random()<.4 ? pick([125,150,240,250]) : rnd(101,399); a = d * rnd(21,249) + (Math.random()<.5 ? rnd(1,d-1) : 0); }
    else { do{ d = rnd(12,48); }while(d%10===0 || d%11===0); a = d * rnd(12,349); }
    if(a<100 || a>99999) continue;
    return {a,d};
  }
  return {a:846,d:3};
}
function sNew(){
  Object.assign(S, sGen(S.lv)); S.shown = false; S.done = false;
  sBuild();
  const D = S.d;
  $('#s-note').textContent = (S.lv==='2' || S.lv==='3')
    ? `Hilfe – die ${D}er-Reihe: ` + [1,2,3,4,5,6,7,8,9].map(i => `${i} · ${D} = ${i*D}`).join(', ') + '.'
    : 'Der Ablauf wiederholt sich immer: Wie oft passt es hinein? – Malrechnen – Subtrahieren – nächste Ziffer herunterholen. Drück nach jedem Feld auf «Weiter» oder Enter.';
}
function sBuild(){
  const as = String(S.a), L = as.length, ds = String(S.d), D = S.d;
  let p = 1; while(Number(as.slice(0,p)) < D) p++;
  const steps = []; let cur = Number(as.slice(0,p));
  for(let e=p-1;e<L;e++){
    const q = Math.floor(cur/D), prod = q*D, rem = cur-prod, w = String(cur).length;
    const st = {e,cur,q,prod,rem,w};
    if(e<L-1){ st.down = Number(as[e+1]); cur = rem*10 + st.down; }
    steps.push(st);
  }
  const Q = Math.floor(S.a/D), R = S.a % D;
  S.Q = Q; S.R = R;
  const C = i => i+2; // Ziffer i des Dividenden → Spalte
  let col = L+2; const cColon = col++, cDiv = col; col += ds.length; const cEq = col++, cQ = col; col += steps.length;
  let cR = 0, cRest = 0; if(R>0){ cR = col++; cRest = col; col += ds.length; }
  const g = $('#s-grid');
  g.style.gridTemplateColumns = `repeat(${col-1}, auto)`;
  let h = '';
  const put = (r,c,inner,cls='',id='') => { h += `<div${id?` id="${id}"`:''} class="${cls}" style="grid-row:${r};grid-column:${c}">${inner}</div>`; };
  const inp = (id, cls, label) => `<input class="cell ${cls}" id="${id}" inputmode="numeric" autocomplete="off" readonly aria-label="${label}">`;
  // Aufgabe
  for(let i=0;i<L;i++) put(1, C(i), as[i], 'ex', 's-a'+i);
  put(1, cColon, ':', 'op');
  for(let i=0;i<ds.length;i++) put(1, cDiv+i, ds[i], 'ex', 's-v'+i);
  put(1, cEq, '=', 'op');
  for(let j=0;j<steps.length;j++) put(1, cQ+j, inp('s-q'+j,'tq',`Resultat, Ziffer ${j+1}`), 'fut', 'b-s-q'+j);
  if(R>0){
    put(1, cR, 'R', 'rlab fut', 's-Rlab');
    for(let i=0;i<ds.length;i++) put(1, cRest+i, inp('s-r'+i,'tr',`Rest, Ziffer ${i+1}`), 'fut', 'b-s-r'+i);
  }
  // Schritte
  steps.forEach((st,j) => {
    const rp = 2+2*j, rs = 3+2*j, left = st.e - st.w + 1;
    put(rp, C(left)-1, '−', 'mi ul fut', 's-m'+j);
    for(let i=0;i<st.w;i++){
      put(rp, C(left+i), inp(`s-p${j}-${i}`,'tp',`Malrechnung Schritt ${j+1}`), 'ul fut', `b-s-p${j}-${i}`);
      put(rs, C(left+i), inp(`s-s${j}-${i}`,'',`Subtraktion Schritt ${j+1}`), 'fut', `b-s-s${j}-${i}`);
    }
    if(st.down!==undefined) put(rs, C(st.e+1), inp('s-dn'+j,'td','Heruntergeholte Ziffer'), 'fut', 'b-s-dn'+j);
  });
  g.innerHTML = h;

  // Felder in der richtigen Reihenfolge
  const divIds = [...ds].map((_,i) => 's-v'+i);
  const range = (n,f) => Array.from({length:n}, (_,i) => f(i));
  const F = [];
  let curIds = range(p, i => 's-a'+i);
  steps.forEach((st,j) => {
    const prodIds = range(st.w, i => `s-p${j}-${i}`), remIds = range(st.w, i => `s-s${j}-${i}`);
    F.push({kind:'q', st, ids:['s-q'+j], exp:st.q, hl:[...curIds, ...divIds],
      text: `Wie oft passt ${D} in ${st.cur}? Schreibe die Zahl ins grüne Feld beim Resultat.`});
    F.push({kind:'p', st, ids:prodIds, exp:st.prod, hl:['s-q'+j, ...divIds], reveal:['s-m'+j],
      text: `Rechne ${st.q} · ${D} und schreibe das Ergebnis unter ${st.cur}.`});
    F.push({kind:'s', st, ids:remIds, exp:st.rem, hl:[...curIds, ...prodIds],
      text: `Subtrahiere: ${st.cur} − ${st.prod}. Schreibe den Unterschied unter den Strich.`});
    if(st.down!==undefined){
      F.push({kind:'d', st, ids:['s-dn'+j], exp:st.down, hl:['s-a'+(st.e+1)],
        text: `Hole die nächste Ziffer (gelb) herunter und schreibe sie neben ${st.rem}.`});
      curIds = [...remIds, 's-dn'+j];
    } else curIds = remIds;
  });
  if(R>0) F.push({kind:'r', ids:range(ds.length, i => 's-r'+i), exp:R, hl:curIds, reveal:['s-Rlab'],
    text: `Es bleibt ${R} übrig, und ${R} ist kleiner als ${D}. Das ist der Rest. Schreibe ihn hinter das R.`});
  S.F = F; S.fi = 0; S.tries = 0;

  // Eingabeverhalten
  g.querySelectorAll('input').forEach(el => {
    el.addEventListener('focus', () => el.select());
    // Zahlen wie gewohnt eintippen: die Ziffern rutschen von rechts nach links (wie beim Taschenrechner)
    el.addEventListener('beforeinput', e => {
      const f = S.F[S.fi]; if(!f || !f.ids.includes(el.id)) return;
      const cur = () => f.ids.map(id => KR.getElementById(id).value).join('');
      const fill = s => f.ids.forEach((id,c) => { const x = KR.getElementById(id), k = c - (f.ids.length - s.length); x.value = k>=0 ? s[k] : ''; x.classList.remove('bad'); });
      const t = e.inputType || '';
      if(t.indexOf('insert')===0){
        e.preventDefault();
        const d = String(e.data||'').replace(/\D/g,''); if(!d) return;
        let s = cur() + d; if(s.length > f.ids.length) s = s.slice(-f.ids.length);
        fill(s); KR.getElementById(f.ids[f.ids.length-1]).focus();
      } else if(t.indexOf('delete')===0){ e.preventDefault(); fill(cur().slice(0,-1)); }
    });
    el.addEventListener('input', () => { el.value = el.value.replace(/\D/g,'').slice(-1); el.classList.remove('bad'); });
    el.addEventListener('keydown', e => { if(e.key==='Enter'){ e.preventDefault(); sNext(); } });
  });
  $('#s-next').textContent = 'Weiter →';
  $('#s-show').hidden = false;
  setMsg($('#s-msg'),'');
  sActivate();
}
function sActivate(){
  const g = $('#s-grid');
  g.querySelectorAll('.hl').forEach(x => x.classList.remove('hl'));
  g.querySelectorAll('input.cur').forEach(x => { x.classList.remove('cur'); x.readOnly = true; });
  const f = S.F[S.fi];
  if(!f){ sFinish(); return; }
  (f.reveal||[]).forEach(id => KR.getElementById(id).classList.remove('fut'));
  f.ids.forEach(id => { KR.getElementById('b-'+id).classList.remove('fut'); const el = KR.getElementById(id); el.readOnly = false; el.classList.add('cur'); });
  f.hl.forEach(id => KR.getElementById(id)?.classList.add('hl'));
  $('#s-step').className = 'step';
  $('#s-nr').textContent = `Schritt ${S.fi+1} von ${S.F.length}`;
  $('#s-text').textContent = f.text;
  S.tries = 0;
  sFocus();
}
function sFocus(){
  setTimeout(() => { const f = S.F && S.F[S.fi]; if(f) KR.getElementById(f.ids[f.ids.length-1]).focus(); else $('#s-next').focus(); }, 30);
}
function sRead(ids){
  const s = ids.map(id => KR.getElementById(id).value || ' ').join('');
  if(!s.trim()) return {empty:true};
  return { empty:false, val:Number(s.replace(/ /g,'')), gap:/\d +\d/.test(s.trim()), endOk:s[s.length-1]!==' ' };
}
function sNext(){
  if(S.done){ sNew(); return; }
  const f = S.F[S.fi], D = S.d, msg = $('#s-msg'), x = sRead(f.ids);
  if(x.empty){ setMsg(msg, 'Schreibe zuerst eine Zahl ins Feld mit dem blauen Rand.', 'info'); sFocus(); return; }
  const good = !x.gap && x.endOk && x.val===f.exp;
  if(good){
    f.ids.forEach(id => { const el = KR.getElementById(id); if(el.value!=='') el.classList.add('ok'); el.classList.remove('bad'); });
    setMsg(msg, '');
    S.fi++; sActivate(); return;
  }
  S.tries++;
  f.ids.forEach(id => { const el = KR.getElementById(id); if(el.value!=='') el.classList.add('bad'); });
  const st = f.st, v = x.val;
  let t;
  if(x.gap) t = 'Da ist eine Lücke zwischen den Ziffern.';
  else if(!x.endOk) t = 'Die Zahl muss ganz rechts im Feld enden.';
  else if(f.kind==='q'){
    t = v*D > st.cur ? `${v} · ${D} = ${v*D}. Das ist mehr als ${st.cur}. Nimm eine kleinere Zahl.`
      : `${v} · ${D} = ${v*D}. Dann bleiben ${st.cur - v*D} übrig, und da passt die ${D} noch einmal hinein. Nimm eine grössere Zahl.`;
  }
  else if(f.kind==='p') t = `Rechne nochmals ${st.q} · ${D}.`;
  else if(f.kind==='s') t = `Rechne nochmals ${st.cur} − ${st.prod}.`;
  else if(f.kind==='d') t = 'Schau oben in der Rechnung: Die gelbe Ziffer kommt herunter.';
  else t = 'Der Rest ist die Zahl, die ganz unten übrig bleibt.';
  if(S.tries>=2) t += ' Mit «Schritt zeigen» siehst du die Lösung für dieses Feld.';
  setMsg(msg, t, 'bad');
  sFocus();
}
function sShowStep(){
  const f = S.F[S.fi]; if(!f) return;
  S.shown = true;
  const s = String(f.exp);
  f.ids.forEach((id,c) => { const el = KR.getElementById(id); const k = c - (f.ids.length - s.length); el.value = k>=0 ? s[k] : ''; el.classList.remove('bad'); el.classList.add('shown'); });
  setMsg($('#s-msg'), '');
  S.fi++; sActivate();
}
function sFinish(){
  S.done = true;
  const D = S.d, Q = S.Q, R = S.R;
  $('#s-step').className = 'step done';
  $('#s-nr').textContent = 'Fertig';
  $('#s-text').textContent = `${fmt(S.a)} : ${D} = ${fmt(Q)}` + (R ? ` Rest ${R}` : '');
  const probe = `Probe: ${fmt(Q)} · ${D}` + (R ? ` + ${R}` : '') + ` = ${fmt(S.a)}.`;
  if(!S.shown){
    SOLVED('schrift-' + S.lv); S.score++; $('#s-score').textContent = `Richtig gelöst: ${S.score}`;
    setMsg($('#s-msg'), 'Super, alles richtig! ' + probe, 'ok');
  } else setMsg($('#s-msg'), 'Geschafft, mit etwas Hilfe. ' + probe + ' Versuch die nächste Rechnung ganz allein.', 'info');
  $('#s-next').textContent = 'Neue Rechnung →';
  $('#s-show').hidden = true;
  $('#s-next').focus();
}
$('#s-next').onclick = sNext;
$('#s-show').onclick = sShowStep;
$('#s-new').onclick = sNew;
sNew();

// Startansicht (Deep-Link per #kopf oder #schriftlich)

return show;
},
"flex": function (KR, EXIT, STAR, SOLVED, ANS) {

// ---------- Hilfsfunktionen ----------
const $ = s => KR.querySelector(s);
const rnd = (a,b) => a + Math.floor(Math.random()*(b-a+1));
const pick = arr => arr[Math.floor(Math.random()*arr.length)];
const fmt = n => String(n).replace(/\B(?=(\d{3})+(?!\d))/g,' ');
const parse = s => { const t = String(s).replace(/[\s'’.  ]/g,''); return /^\d+$/.test(t) ? Number(t) : null; };
const ZW = ['','eine Null','zwei Nullen','drei Nullen'];
const zeros = n => { let z=0; while(n>0 && n%10===0){ n/=10; z++; } return z; };
const c1 = x => `<i class="c1">${x}</i>`;
const c2 = x => `<i class="c2">${x}</i>`;
const res = x => `<span class="res">${x}</span>`;

// Zerlegung für das Verteilungsgesetz: 84 = 80 + 4, 307 = 300 + 7, 640 = 600 + 40
const splitB = b => b < 100 ? [b - b%10, b%10] : [b - b%100, b%100];
const partNames = b => b < 100 ? 'Zehner und Einer' : (b%10===0 ? 'Hunderter und Zehner' : 'Hunderter und Einer');
function expl(a, x){
  const z = zeros(x);
  if(z===0) return `${a} · ${x} = ${a*x} kennst du aus dem Einmaleins.`;
  const k = x / 10**z;
  return `${a} · ${fmt(x)} = ${fmt(a*x)}, denn ${a} · ${k} = ${a*k} und dann ${ZW[z]} anhängen.`;
}

// Baut die Schritte: jede Momentaufnahme der Tafel ist ein Schritt
function builder(){
  const R = [], S = [];
  return { R, S, snap(say, hot){ S.push({ rows: R.map(r => ({...r})), say, hot }); } };
}

// =========================================================
// Die fünf Tricks
// =========================================================
const TRICKS = [
{
  key:'t1', kicker:'Trick 1', title:'Verteilungsgesetz Multiplikation', wash:'w1',
  preview:`7 · 84 = (7 · 80) + (7 · 4)<small>560 + 28</small>= 588`,
  blurb:'Die grosse Zahl zerlegen, jeden Teil malrechnen, dann zusammenzählen.',
  ex:{a:7,b:84},
  rand(){
    if(this.lv===1) return { a:rnd(2,5), b:rnd(1,4)*10 + rnd(1,9) };
    if(this.lv===2) return { a:rnd(3,9), b:rnd(2,9)*10 + rnd(1,9) };
    return { a:rnd(3,9), b:rnd(1,9)*100 + (Math.random()<.5 ? rnd(1,9) : rnd(1,9)*10) };
  },
  steps({a,b}){
    const [t,u] = splitB(b), B = builder(), R = B.R;
    R.push({l:`${a} · ${b}`, o:'=', r:'?'});
    B.snap(`Wie viel ist <b>${a} · ${b}</b>? Im Kopf ist das schwierig. Wir machen die Rechnung einfacher.`, 0);
    R.push({aside:`Zerlege ${b} in ${partNames(b)}: ${b} = ${c1(t)} + ${c2(u)}`});
    B.snap(`Zerlege die grosse Zahl ${b} in zwei einfache Teile: ${c1(t)} und ${c2(u)}.`, 1);
    R[0].r = `(${a} · ${c1(t)}) + (${a} · ${c2(u)})`;
    B.snap(`Jetzt rechnest du <b>jeden Teil</b> mal ${a}. Die Klammern zeigen, was zusammengehört. Dazwischen steht ein Plus.`, 0);
    R.push({l:'', o:'', r:`${c1(fmt(a*t))} + ${c2(fmt(a*u))}`});
    B.snap(`${expl(a,t)} ${expl(a,u)}`, 2);
    R[2].r += ` = ${res(fmt(a*b))}`;
    B.snap(`Zum Schluss zählst du die Teilresultate zusammen: ${fmt(a*t)} + ${fmt(a*u)} = <b>${fmt(a*b)}</b>.`, 2);
    return B.S;
  },
  merke:'Zerlege die grosse Zahl in einfache Teile (zum Beispiel Zehner und Einer). Rechne jeden Teil mal. Zähle die Teilresultate zusammen.',
  practice(){
    const {a,b} = this.rand(), [t,u] = splitB(b);
    return {
      task:`${a} · ${b} = ?`,
      rows:[
        [`${a} · ${b} = (${a} ·`, {k:'t', sol:t}, `) + (${a} ·`, {k:'u', sol:u}, `)`],
        [`=`, {k:'pt', sol:a*t}, `+`, {k:'pu', sol:a*u}],
        [`=`, {k:'r', sol:a*b}]
      ],
      check(V){ return {
        t: V.t!==null && V.u!==null && V.t+V.u===b && V.t>0,
        u: V.t!==null && V.u!==null && V.t+V.u===b && V.u>0,
        pt: V.t!==null && V.pt===a*V.t,
        pu: V.u!==null && V.pu===a*V.u,
        r: V.r===a*b };
      }
    };
  }
},
{
  key:'t2', kicker:'Trick 2', title:'Trick mit 9 / 99 / 999', wash:'w2', align:'right',
  preview:`9 · 142<small>10 · 142 − 1 · 142</small>1420 − 142 = 1278`,
  blurb:'Mit 10, 100 oder 1000 rechnen und die Zahl einmal abziehen.',
  ex:{f:9,n:142},
  choices:[9,99,999], sel:0,
  rand(){
    const f = this.sel || pick([9,99,999]);
    const R = { 9:[[11,49],[50,199],[200,999]], 99:[[11,30],[31,99],[100,499]], 999:[[2,9],[11,50],[51,250]] }[f][this.lv-1];
    let n = rnd(R[0],R[1]); if(n%10===0) n++;
    return { f, n };
  },
  steps({f,n}){
    const P = f+1, B = builder(), R = B.R;
    R.push({l:`${f} · ${n}`, o:'=', r:''});
    B.snap(`Wie viel ist <b>${f} · ${n}</b>? Schau dir die ${f} genau an: Sie ist nur <b>1 weniger als ${fmt(P)}</b>. Mit ${fmt(P)} rechnet es sich viel leichter!`, 0);
    R.push({l:`${c1(fmt(P))} · ${n}`, o:'=', r:fmt(P*n)});
    B.snap(`Rechne zuerst mal ${fmt(P)} statt mal ${f}. Das ist leicht: ${ZW[zeros(P)]} anhängen. ${fmt(P)} · ${n} = ${fmt(P*n)}.`, 1);
    R.push({l:`${c2('1')} · ${n}`, o:'=', r:`− ${fmt(n)}`, ul:true});
    B.snap(`Aber du solltest nur ${f}-mal rechnen, nicht ${fmt(P)}-mal. Du hast ${n} also <b>einmal zu viel</b>. Darum ziehst du 1 · ${n} wieder ab.`, 2);
    R.push({l:'', o:'', r:res(fmt(f*n))});
    B.snap(`Subtrahiere: ${fmt(P*n)} − ${n} = <b>${fmt(f*n)}</b>. Fertig!`, 3);
    return B.S;
  },
  merke:'Mal 9: rechne mal 10 und ziehe die Zahl einmal ab. Mal 99: rechne mal 100 und ziehe die Zahl einmal ab. Mal 999: rechne mal 1000 und ziehe die Zahl einmal ab.',
  practice(){
    const {f,n} = this.rand(), P = f+1;
    return {
      task:`${f} · ${n} = ?`,
      rows:[
        [`${fmt(P)} · ${n} =`, {k:'a', sol:P*n}],
        [`1 · ${n} = −`, {k:'b', sol:n}],
        [`${f} · ${n} =`, {k:'r', sol:f*n}]
      ],
      check(V){ return { a:V.a===P*n, b:V.b===n, r:V.r===f*n }; }
    };
  }
},
{
  key:'t3', kicker:'Trick 3', title:'Verteilungsgesetz Division', wash:'w3',
  preview:`594 : 6 = (600 : 6) − (6 : 6)<small>100 − 1</small>= 99`,
  blurb:'Eine Nachbarzahl suchen, die sich leicht teilen lässt.',
  ex:{d:6,m:100,j:1,s:'−'},
  rand(){
    for(;;){
      const lv = this.lv;
      const d = lv===1 ? rnd(2,5) : rnd(3,9);
      const m = lv===1 ? pick([10,20,30,40,50]) : lv===2 ? pick([10,20,30,40,50,60,70,80,90,100]) : pick([100,200,300,400,500]);
      const j = lv===1 ? 1 : lv===2 ? rnd(1,2) : rnd(1,3);
      const s = pick(['−','−','+']);
      if(s==='−' && m-j<2) continue;
      return {d,m,j,s};
    }
  },
  steps({d,m,j,s}){
    const R0 = d*m, k = d*j, N = s==='−' ? R0-k : R0+k, q = N/d, B = builder(), R = B.R;
    R.push({l:`${N} : ${d}`, o:'=', r:'?'});
    B.snap(`Wie viel ist <b>${N} : ${d}</b>? Schau dir die Zahl ${N} genau an. Welche Zahl in der Nähe kannst du leicht durch ${d} teilen?`, 0);
    R.push({aside:`${N} liegt nah bei ${R0}. Also: ${N} = ${c1(R0)} ${s} ${c2(k)}`});
    B.snap(`${N} liegt ganz nah bei ${c1(R0)}. ${R0} kannst du leicht durch ${d} teilen. Es fehlen ${s==='−' ? 'nur' : 'noch'} ${c2(k)}: ${N} = ${R0} ${s} ${k}.`, 1);
    R[0].r = `(${c1(R0)} : ${d}) ${s} (${c2(k)} : ${d})`;
    B.snap(`Jetzt teilst du <b>beide Teile</b> durch ${d}. Das Rechenzeichen ${s} bleibt dazwischen stehen.`, 0);
    R.push({l:'', o:'', r:`${c1(m)} ${s} ${c2(j)}`});
    B.snap(`${R0} : ${d} = ${m}, denn ${d} · ${m} = ${R0}. Und ${k} : ${d} = ${j}.`, 2);
    R[2].r += ` = ${res(q)}`;
    B.snap(`Zum Schluss rechnest du ${m} ${s} ${j} = <b>${q}</b>. Fertig!`, 2);
    return B.S;
  },
  merke:'Suche eine Nachbarzahl, die sich leicht teilen lässt. Teile beide Teile durch die gleiche Zahl. Rechne dann die Teilresultate minus (oder plus).',
  practice(){
    const {d,m,j,s} = this.rand(), R0 = d*m, k = d*j, N = s==='−' ? R0-k : R0+k, sg = s==='−' ? -1 : 1;
    return {
      task:`${N} : ${d} = ?`,
      rows:[
        [`${N} : ${d} = (`, {k:'a', sol:R0}, `: ${d}) ${s} (`, {k:'b', sol:k}, `: ${d})`],
        [`=`, {k:'x', sol:m}, s, {k:'y', sol:j}],
        [`=`, {k:'r', sol:N/d}]
      ],
      check(V){
        const split = V.a!==null && V.b!==null && V.a + sg*V.b===N && V.a%d===0 && V.b%d===0 && V.b>0;
        return { a:split, b:split, x:V.a!==null && V.x===V.a/d, y:V.b!==null && V.y===V.b/d, r:V.r===N/d };
      }
    };
  }
},
{
  key:'t4', kicker:'Trick 4', title:'Multiplizieren mit 5 / 50 / 500', wash:'w4',
  preview:`50 · 862<small>100 · 862 = 86 200</small>86 200 : 2 = 43 100`,
  blurb:'Mal 10, 100 oder 1000 rechnen und dann halbieren.',
  ex:{f:50,n:862},
  choices:[5,50,500], sel:0,
  rand(){
    const f = this.sel || pick([5,50,500]);
    const R = { 5:[[12,98],[100,998],[1001,9999]], 50:[[12,98],[100,998],[1001,1999]], 500:[[2,20],[22,98],[101,999]] }[f][this.lv-1];
    let n = rnd(R[0],R[1]);
    if(this.lv<3 && n%2) n++;
    if(this.lv===3 && Math.random()<.5 && n%2===0) n++;
    return {f,n};
  },
  steps({f,n}){
    const P = f*2, B = builder(), R = B.R;
    R.push({l:`${f} · ${n}`, o:'=', r:''});
    B.snap(`Wie viel ist <b>${f} · ${n}</b>? Mal ${f} ist schwierig. Aber: ${f} ist genau <b>die Hälfte von ${fmt(P)}</b>!`, 0);
    R.push({l:`${c1(fmt(P))} · ${n}`, o:'=', r:fmt(P*n)});
    B.snap(`Rechne zuerst mal ${fmt(P)}. Das ist leicht: ${ZW[zeros(P)]} anhängen. ${fmt(P)} · ${n} = ${fmt(P*n)}.`, 1);
    R[1].r += ` ${c2(': 2')}`;
    B.snap(`Mit ${fmt(P)} hast du <b>doppelt so viel</b> gerechnet wie mit ${f}. Darum musst du das Resultat jetzt halbieren: geteilt durch 2.`, 1);
    R[1].r += ` = ${res(fmt(f*n))}`;
    B.snap(`Die Hälfte von ${fmt(P*n)} ist <b>${fmt(f*n)}</b>. Fertig!`, 1);
    return B.S;
  },
  merke:'Mal 5: rechne mal 10 und halbiere. Mal 50: rechne mal 100 und halbiere. Mal 500: rechne mal 1000 und halbiere.',
  practice(){
    const {f,n} = this.rand(), P = f*2;
    return {
      task:`${f} · ${n} = ?`,
      rows:[
        [`${fmt(P)} · ${n} =`, {k:'a', sol:P*n}],
        [`Halbieren: … : 2 =`, {k:'r', sol:f*n}]
      ],
      check(V){ return { a:V.a===P*n, r:V.r===f*n }; }
    };
  }
},
{
  key:'t5', kicker:'Trick 5', title:'Dividieren durch 5 / 50 / 500', wash:'w1',
  preview:`12 000 : 50<small>12 000 · 2 = 24 000</small>24 0<span class="strk">00</span> : 1<span class="strk">00</span> = 240`,
  blurb:'Zuerst verdoppeln, dann durch 10, 100 oder 1000 teilen.',
  ex:{f:50,q:240},
  choices:[5,50,500], sel:0,
  rand(){
    const f = this.sel || pick([5,50,500]);
    const q = this.lv===1 ? rnd(2,20) : this.lv===2 ? rnd(21,99) : rnd(100, f===500 ? 400 : 999);
    return {f,q};
  },
  steps({f,q}){
    const P = f*2, N = f*q, D = 2*N, z = zeros(P), B = builder(), R = B.R;
    const Ds = fmt(D), Ps = fmt(P);
    const Dst = `${Ds.slice(0,-z)}<span class="strk">${Ds.slice(-z)}</span>`;
    const Pst = `${Ps.slice(0,-z)}<span class="strk">${Ps.slice(-z)}</span>`;
    R.push({l:`${fmt(N)} : ${f}`, o:'=', r:''});
    B.snap(`Wie viel ist <b>${fmt(N)} : ${f}</b>? Durch ${f} teilen ist schwierig. Durch ${Ps} teilen ist leicht, da streicht man nur Nullen!`, 0);
    R.push({l:`${fmt(N)} · ${c1('2')}`, o:'=', r:Ds});
    B.snap(`Darum verdoppelst du zuerst die Zahl: ${fmt(N)} · 2 = ${Ds}.`, 1);
    R[1].r += ` : ${c2(Ps)}`;
    B.snap(`Weil du verdoppelt hast, teilst du jetzt durch ${c2(Ps)} statt durch ${f}. Das Resultat bleibt gleich, denn ${Ps} ist das Doppelte von ${f}.`, 1);
    R[1].r = `${Dst} : ${Pst} = ${res(fmt(q))}`;
    B.snap(`Durch ${Ps} teilen heisst: bei beiden Zahlen ${ZW[z]} streichen. ${fmt(N)} : ${f} = <b>${fmt(q)}</b>. Fertig!`, 1);
    return B.S;
  },
  merke:'Durch 5: verdopple und teile durch 10. Durch 50: verdopple und teile durch 100. Durch 500: verdopple und teile durch 1000.',
  practice(){
    const {f,q} = this.rand(), P = f*2, N = f*q;
    return {
      task:`${fmt(N)} : ${f} = ?`,
      rows:[
        [`${fmt(N)} · 2 =`, {k:'a', sol:2*N}],
        [`… : ${fmt(P)} =`, {k:'r', sol:q}]
      ],
      check(V){ return { a:V.a===2*N, r:V.r===q }; }
    };
  }
}
];

// Reihenfolge: zuerst die drei Rechentricks, dann die zwei Verteilungsgesetze
// Mal und Durch zusammengelegt: 5/50/500 und Verteilungsgesetz, Rechenart wählbar
const BY = k => TRICKS.find(t => t.key===k);
function merge(key, title, subs, extra){
  const o = Object.assign({ key, title, op:0, lv:1, sel:0, ops:[['mal','Mal'],['durch','Durch']], subs,
    preview: subs.mal.preview, blurb: subs.mal.blurb, merke: subs.mal.merke,
    sub(op){ const s = this.subs[op]; s.lv = this.lv; s.sel = this.sel; return s; },
    rand(){ const op = this.op || pick(['mal','durch']); return Object.assign({_op:op}, this.sub(op).rand()); },
    steps(x){ const s = this.sub(x._op); this.merke = s.merke; this.align = s.align; return s.steps(x); },
    practice(){ return this.sub(this.op || pick(['mal','durch'])).practice(); }
  }, extra);
  Object.defineProperty(o, 'ex', { get(){ const op = this.op || 'mal'; return Object.assign({_op:op}, this.subs[op].ex); } });
  return o;
}
const T2 = BY('t2');
const T45 = merge('t45', 'Trick mit 5 / 50 / 500', {mal:BY('t4'), durch:BY('t5')}, {choices:[5,50,500]});
const TV = merge('tv', 'Verteilungsgesetz', {mal:BY('t1'), durch:BY('t3')}, {});
TRICKS.length = 0; TRICKS.push(T2, T45, TV);
const META = { t2:['Trick 1','w1'], t45:['Trick 2','w2'], tv:['Gesetz','w3'] };
TRICKS.forEach(t => { [t.kicker, t.wash] = META[t.key]; t.lv = 1; });

// ---------- Übersicht ----------
const tileHtml = t => `
  <button class="tile ${t.wash}" data-go="${t.key}">
    <span class="kicker">${t.kicker}</span>
    <h3>${t.title}</h3>
    <div class="preview num">${t.preview}</div>
    <p>${t.blurb}</p>
  </button>`;
$('#tiles-a').innerHTML = TRICKS.slice(0,3).map(tileHtml).join('');
$('#tiles-b').innerHTML = TRICKS.slice(3).map(tileHtml).join('');

// ---------- Präsentation ----------
const V = { t:null, steps:[], i:0 };

function renderStep(){
  const st = V.steps[V.i], last = V.i === V.steps.length-1;
  const board = $('#v-board');
  board.className = 'board' + (V.t.align==='right' ? ' ralign' : '');
  board.innerHTML = st.rows.map((r,idx) => {
    const hot = idx===st.hot ? ' hot' : '';
    if(r.aside) return `<div class="aside${hot}">${r.aside}</div>`;
    return `<div class="l${hot}">${r.l}</div><div class="o${hot}">${r.o}</div><div class="r${hot}${r.ul?' ul':''}">${r.r}</div>`;
  }).join('');
  $('#v-say').innerHTML = st.say;
  $('#v-nr').textContent = 'Schritt ' + (V.i+1);
  $('#v-count').textContent = `Schritt ${V.i+1} von ${V.steps.length}`;
  $('#v-merke').hidden = !last;
  $('#v-merke-t').textContent = V.t.merke;
  $('#v-dots').innerHTML = V.steps.map((_,k) =>
    `<button class="dot ${k===V.i?'now':k<V.i?'done':''}" data-k="${k}" aria-label="Schritt ${k+1}"></button>`).join('');
  $('#v-prev').disabled = V.i===0;
  const ti = TRICKS.indexOf(V.t);
  const nextBtn = $('#v-next');
  if(last){
    nextBtn.textContent = ti < TRICKS.length-1 ? 'Nächster Trick →' : 'Zur Übersicht';
  } else nextBtn.textContent = 'Weiter →';
}
$('#v-dots').addEventListener('click', e => {
  const b = e.target.closest('.dot'); if(!b) return;
  V.i = Number(b.dataset.k); renderStep();
});
function next(){
  if(V.i < V.steps.length-1){ V.i++; renderStep(); return; }
  const ti = TRICKS.indexOf(V.t);
  go(ti < TRICKS.length-1 ? TRICKS[ti+1].key : 'home');
}
function prev(){ if(V.i>0){ V.i--; renderStep(); } }
$('#v-next').addEventListener('click', next);
$('#v-prev').addEventListener('click', prev);
$('#v-new').addEventListener('click', () => { V.steps = V.t.steps(V.t.rand()); V.i = 0; renderStep(); });
KR.addEventListener('keydown', e => {
  if($('#show').hidden || $('#pane-e').hidden) return;
  if(e.target.closest('input')) return;
  if(e.key==='ArrowRight' || e.key==='PageDown'){ e.preventDefault(); next(); }
  if(e.key==='ArrowLeft' || e.key==='PageUp'){ e.preventDefault(); prev(); }
});
// Vollbild für die Wandtafel (optional)
try{
  if(document.fullscreenEnabled){
    const fb = $('#v-full'); fb.hidden = false;
    fb.addEventListener('click', () => {
      try{
        const p = document.fullscreenElement ? document.exitFullscreen() : document.documentElement.requestFullscreen();
        if(p && p.catch) p.catch(()=>{ fb.hidden = true; });
      }catch(_){ fb.hidden = true; }
    });
    document.addEventListener('fullscreenchange', () => { fb.textContent = document.fullscreenElement ? 'Vollbild beenden' : 'Vollbild'; });
  }
}catch(_){}

// ---------- Jetzt du ----------
const P = { task:null, score:0 };
function newPractice(){
  P.task = V.t.practice();
  $('#p-task').textContent = P.task.task;
  $('#p-body').innerHTML = P.task.rows.map(row => `<div class="prow">${row.map(seg => {
    if(typeof seg === 'string') return `<span>${seg}</span>`;
    const w = String(seg.sol).length + 2.2;
    return `<input class="field" id="p-${seg.k}" data-k="${seg.k}" inputmode="numeric" autocomplete="off" style="width:${w}ch" aria-label="Feld">`;
  }).join('')}</div>`).join('');
  setMsg('', '');
  P.solved = false;
  const first = $('#p-body input'); if(first && !$('#show').hidden && KR.activeElement && KR.activeElement.closest('#pane-p')) first.focus();
}
function setMsg(t, k){ const m = $('#p-msg'); m.textContent = t; m.className = 'msg ' + (k||''); }
function vals(){
  const o = {};
  KR.querySelectorAll('#p-body input').forEach(i => o[i.dataset.k] = parse(i.value));
  return o;
}
function checkPractice(){
  const Vv = vals(), r = P.task.check(Vv);
  let all = true, empty = false;
  KR.querySelectorAll('#p-body input').forEach(i => {
    i.classList.remove('ok','bad','shown');
    if(i.value.trim()===''){ empty = true; all = false; return; }
    const ok = !!r[i.dataset.k];
    i.classList.add(ok ? 'ok' : 'bad');
    if(!ok) all = false;
  });
  if(all){
    if(!P.solved){ SOLVED(V.t.key + '-' + V.t.lv); P.score++; P.solved = true; $('#p-score').textContent = 'Richtig: ' + P.score; }
    setMsg('Super, alles richtig! Klicke auf «Neue Aufgabe».', 'ok');
  } else if(empty){
    setMsg('Fülle zuerst alle Felder aus.', 'info');
  } else {
    setMsg('Rot markierte Felder stimmen noch nicht. Schau dir die Schritte oben nochmals an.', 'bad');
  }
}
$('#p-check').addEventListener('click', checkPractice);
$('#p-new').addEventListener('click', () => { newPractice(); const f = $('#p-body input'); if(f) f.focus(); });
$('#p-show').addEventListener('click', () => {
  P.task.rows.flat().forEach(seg => {
    if(typeof seg === 'string') return;
    const i = KR.getElementById('p-' + seg.k);
    i.value = fmt(seg.sol); i.classList.remove('ok','bad'); i.classList.add('shown');
  });
  P.solved = true;
  setMsg('So geht die Lösung. Probiere danach eine neue Aufgabe.', 'info');
});
$('#p-body').addEventListener('keydown', e => {
  if(e.key !== 'Enter') return;
  const ins = [...KR.querySelectorAll('#p-body input')];
  const ix = ins.indexOf(e.target);
  if(ix > -1 && ix < ins.length-1){ ins[ix+1].focus(); } else checkPractice();
});

// ---------- Erklärung / Jetzt du ----------
function tab(practice){
  $('#pane-e').hidden = practice;
  $('#pane-p').hidden = !practice;
  $('#v-count').hidden = practice;
  if(practice){ const f = $('#p-body input'); if(f) f.focus(); }
}
$('#tab-e').addEventListener('click', () => tab(false));
$('#tab-p').addEventListener('click', () => tab(true));

// ---------- Auswahl 9 / 99 / 999 bzw. 5 / 50 / 500 ----------
function renderChoose(t){
  $('#v-lv').innerHTML = [[1,'Leicht'],[2,'Mittel'],[3,'Schwer']].map(([v,l]) => `<button data-v="${v}" aria-pressed="${t.lv===v}">${l}</button>`).join('');
  $('#v-opg').hidden = !t.ops;
  if(t.ops) $('#v-op').innerHTML = [...t.ops, [0,'Gemischt']].map(([v,l]) => `<button data-v="${v}" aria-pressed="${t.op===v}">${l}</button>`).join('');
  const box = $('#v-choose');
  box.hidden = !t.choices;
  if(!t.choices) return;
  const opts = [...t.choices.map(c => [c, String(c)]), [0, 'Gemischt']];
  $('#v-seg').innerHTML = opts.map(([v,l]) => `<button data-v="${v}" aria-pressed="${t.sel===v}">${l}</button>`).join('');
}
$('#v-seg').addEventListener('click', e => {
  const b = e.target.closest('button'); if(!b) return;
  const t = V.t; t.sel = Number(b.dataset.v);
  renderChoose(t);
  V.steps = t.steps(t.rand()); V.i = 0;
  renderStep(); newPractice();
});
$('#v-lv').addEventListener('click', e => {
  const b = e.target.closest('button'); if(!b) return;
  const t = V.t; t.lv = Number(b.dataset.v);
  renderChoose(t);
  V.steps = t.steps(t.rand()); V.i = 0;
  renderStep(); newPractice();
});

$('#v-op').addEventListener('click', e => {
  const b = e.target.closest('button'); if(!b) return;
  const t = V.t; t.op = b.dataset.v==='0' ? 0 : b.dataset.v;
  renderChoose(t); V.steps = t.steps(t.rand()); V.i = 0; renderStep(); newPractice();
});
// ---------- Navigation ----------
function show(id){
  const t = TRICKS.find(x => x.key===id);
  $('#home').hidden = !!t;
  $('#show').hidden = !t;
  if(t){
    V.t = t; V.steps = t.steps(t.ex); V.i = 0;
    $('#v-kicker').textContent = t.kicker;
    $('#v-title').textContent = t.title;
    renderChoose(t); renderStep(); newPractice(); tab(false);
  }
  window.scrollTo(0,0);
}
function go(id){ if(id==='home'){ EXIT(); return; } show(id); }
KR.addEventListener('click', e => {
  const b = e.target.closest('[data-go]'); if(!b) return;
  go(b.dataset.go);
});

return show;
}
};
if (OHNE_STERNE) document.body.classList.add('ohne-sterne');
if (PORTAL) {
  var gestartet = false;
  var los = function () { if (!gestartet) { gestartet = true; start(); } };
  window.addEventListener('message', function (e) {
    if (e.source !== parent || !e.data || !e.data.knobelnestInit) return;
    var st = e.data.knobelnestInit.store;
    if (st && st.rk) try { ST = JSON.parse(st.rk) || {}; } catch (x) { ST = {}; }
    los();
  });
  send({ type: 'hello' });
  setTimeout(los, 1500);
} else start();
