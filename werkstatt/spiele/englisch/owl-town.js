// ====================================================================== Owl Town – Englisch-Stadt in 3D
// Die Eule läuft mit den Pfeiltasten (oder Knöpfen) durch die Stadt. Stufen: Orte finden, Berufe finden,
// Wege nach Beschreibung laufen (turn left/right, walk straight on, cross the bridge, take the second exit …).
// Nach dem Markieren des Ziels: richtiger Weg (rot) und eigener Weg (blau), Fehlerstelle wird erklärt.
// three.js kommt von jsdelivr (wie die Zeitreise). Rahmen (Stufen, Sterne, Ton) aus werkstatt/spiele/gedaechtnis/bauen.py.

var THREE = null, T3P = null;
function loadThree(cb) {
  if (THREE) return cb();
  T3P = T3P || import('https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.min.js');
  T3P.then(function (m) { THREE = m; cb(); }, function () { cb('err'); });
}

// ---------------------------------------------------------------------- Orte und Berufe
var PLACES = {
  restaurant: { en: 'restaurant', de: 'das Restaurant', emo: '🍝', col: '#f08a3c', sign: '#c0392b' },
  postoffice: { en: 'post office', de: 'die Post', emo: '✉️', col: '#5aa0dc', sign: '#2a6fb0' },
  bakery: { en: 'bakery', de: 'die Bäckerei', emo: '🥐', col: '#f6cf4a', sign: '#e0782c' },
  school: { en: 'school', de: 'die Schule', emo: '🏫', col: '#f1dcb3', sign: '#8a5a2b' },
  police: { en: 'police station', de: 'der Polizeiposten', emo: '🚓', col: '#3d7fd0', sign: '#1d4f96' },
  hospital: { en: 'hospital', de: 'das Spital', emo: '🏥', col: '#f4f7fb', sign: '#d23a3a' },
  supermarket: { en: 'supermarket', de: 'der Supermarkt', emo: '🛒', col: '#a9c6ee', sign: '#2f7d4a' },
  taxi: { en: 'taxi rank', de: 'der Taxistand', emo: '🚕', col: '#f3c623', sign: '#222', open: true },
  station: { en: 'train station', de: 'der Bahnhof', emo: '🚆', col: '#e9ddc8', sign: '#2f8f7a' },
  firestation: { en: 'fire station', de: 'die Feuerwehr', emo: '🚒', col: '#a8433a', sign: '#e8962c' },
  vet: { en: 'veterinary', de: 'die Tierarztpraxis', emo: '🐾', col: '#ef6a3a', sign: '#e8b52c' },
  church: { en: 'church', de: 'die Kirche', emo: '⛪', col: '#f5e6d6', sign: '#8a4a6a' },
  farm: { en: 'farm', de: 'der Bauernhof', emo: '🐄', col: '#c8423a', sign: '#7a4a24' },
  cinema: { en: 'cinema', de: 'das Kino', emo: '🎬', col: '#e8553a', sign: '#b8262c' },
  court: { en: 'court', de: 'das Gericht', emo: '⚖️', col: '#d9b8a8', sign: '#7a4a3a' },
  casino: { en: 'casino', de: 'das Casino', emo: '🎰', col: '#8a5ad0', sign: '#e0368a' },
  pharmacy: { en: 'pharmacy', de: 'die Apotheke', emo: '💊', col: '#f7c6d8', sign: '#d0367a' },
  airport: { en: 'airport', de: 'der Flughafen', emo: '✈️', col: '#dfeaf6', sign: '#2a6fb0' },
  butcher: { en: 'butcher\'s', de: 'die Metzgerei', emo: '🥩', col: '#f2e3e0', sign: '#b8262c' },
  library: { en: 'library', de: 'die Bibliothek', emo: '📚', col: '#b8734a', sign: '#5a3a8a' },
  bank: { en: 'bank', de: 'die Bank', emo: '🏦', col: '#e8e0cc', sign: '#2a5a3a' },
  museum: { en: 'museum', de: 'das Museum', emo: '🏛️', col: '#e6d3b0', sign: '#7a5a2a' },
  park: { en: 'park', de: 'der Park', emo: '🌳', col: '#7cc46a', sign: '#3a7a2a', open: true },
  space: { en: 'space centre', de: 'das Raumfahrtzentrum', emo: '🚀', col: '#eef2f7', sign: '#1d3557' },
  site: { en: 'building site', de: 'die Baustelle', emo: '🚧', col: '#d9a441', sign: '#e0782c', open: true }
};
// [Beruf, Bild, Ort, Deutsch, Kleidung]
var JOBS = [
  ['waitress', '💁‍♀️', 'restaurant', 'die Kellnerin', { shirt: '#ffffff', pants: '#1f2a44', hair: '#2a1a10', vest: '#1f2a44' }],
  ['chef', '🧑‍🍳', 'restaurant', 'der Koch / die Köchin', { shirt: '#ffffff', pants: '#ffffff', hat: 'chef' }],
  ['postman', '📮', 'postoffice', 'der Pöstler', { shirt: '#9cc8ec', pants: '#2f6fb0', hat: 'cap', hatC: '#2f6fb0' }],
  ['baker', '🥖', 'bakery', 'der Bäcker / die Bäckerin', { shirt: '#f2a7b8', pants: '#5a8ad0', hat: 'chef', apron: '#cfe8f2' }],
  ['teacher', '🧑‍🏫', 'school', 'die Lehrerin / der Lehrer', { shirt: '#e0368a', pants: '#2a2a2a', hair: '#2a1a10' }],
  ['police officer', '👮', 'police', 'der Polizist / die Polizistin', { shirt: '#4a90e2', pants: '#1f2a66', hat: 'cap', hatC: '#1f2a66' }],
  ['doctor', '🧑‍⚕️', 'hospital', 'der Arzt / die Ärztin', { shirt: '#ffffff', pants: '#666666', hair: '#2a1a10' }],
  ['nurse', '💉', 'hospital', 'die Pflegefachfrau / der Pflegefachmann', { shirt: '#8fd3c8', pants: '#8fd3c8', hat: 'nurse', hair: '#e8c34a' }],
  ['shop assistant', '🛍️', 'supermarket', 'die Verkäuferin / der Verkäufer', { shirt: '#f6d23a', pants: '#2a4a9a', hair: '#2a1a10' }],
  ['taxi driver', '🚕', 'taxi', 'der Taxifahrer / die Taxifahrerin', { shirt: '#ffffff', pants: '#1f2a66', hat: 'cap', hatC: '#1f2a66' }],
  ['firefighter', '🧑‍🚒', 'firestation', 'der Feuerwehrmann / die Feuerwehrfrau', { shirt: '#f6d23a', pants: '#f6d23a', hat: 'helmet', hatC: '#d23a2a' }],
  ['vet', '🐶', 'vet', 'der Tierarzt / die Tierärztin', { shirt: '#8ccf5a', pants: '#3a5a9a', hair: '#7a4a24' }],
  ['priest', '✝️', 'church', 'der Pfarrer / die Pfarrerin', { shirt: '#333333', pants: '#333333', hair: '#5a3a1a' }],
  ['farmer', '🧑‍🌾', 'farm', 'der Bauer / die Bäuerin', { shirt: '#9cc8ec', pants: '#3a5aa0', hat: 'farmer', hatC: '#8a5a2a' }],
  ['actor', '🎬', 'cinema', 'der Schauspieler / die Schauspielerin', { shirt: '#3a7ad0', pants: '#1a1a1a', hair: '#1a1a1a' }],
  ['lawyer', '⚖️', 'court', 'der Anwalt / die Anwältin', { shirt: '#2a3a7a', pants: '#2a3a7a', hair: '#1a1a1a' }],
  ['train driver', '🚆', 'station', 'der Lokführer / die Lokführerin', { shirt: '#3a5aa0', pants: '#3a5aa0', hat: 'cap', hatC: '#2a4a9a' }],
  ['pilot', '🧑‍✈️', 'airport', 'der Pilot / die Pilotin', { shirt: '#1f2a66', pants: '#1f2a66', hat: 'cap', hatC: '#1f2a66' }],
  ['pharmacist', '💊', 'pharmacy', 'der Apotheker / die Apothekerin', { shirt: '#ffffff', pants: '#4a6ab0', hair: '#e0782c' }],
  ['street worker', '👷', 'site', 'der Strassenarbeiter / die Strassenarbeiterin', { shirt: '#f08a2c', pants: '#3a5aa0', hat: 'helmet', hatC: '#f6d23a' }],
  ['casino host', '🃏', 'casino', 'die Casino-Gastgeberin / der Casino-Gastgeber', { shirt: '#ffffff', pants: '#1a1a1a', vest: '#1a1a1a', hair: '#1a1a1a' }],
  ['painter', '🧑‍🎨', 'park', 'der Maler / die Malerin', { shirt: '#4ab0e0', pants: '#2a4a9a', hat: 'beret', hatC: '#4ab0e0', apron: '#d23a2a' }],
  ['musician', '🎻', 'park', 'der Musiker / die Musikerin', { shirt: '#3a5ad0', pants: '#d23a2a', hair: '#1a1a1a' }],
  ['astronaut', '🧑‍🚀', 'space', 'der Astronaut / die Astronautin', { shirt: '#dfe6f2', pants: '#dfe6f2', hat: 'space' }],
  ['butcher', '🥩', 'butcher', 'der Metzger / die Metzgerin', { shirt: '#ffffff', pants: '#2a2a2a', apron: '#e88a9a', hat: 'chef' }],
  ['librarian', '📚', 'library', 'der Bibliothekar / die Bibliothekarin', { shirt: '#7a4ab0', pants: '#2a2a2a', hair: '#7a4a24' }],
  ['bank clerk', '💶', 'bank', 'der Bankangestellte / die Bankangestellte', { shirt: '#ffffff', pants: '#2a3a5a', vest: '#2a3a5a', hair: '#1a1a1a' }]
];

// ---------------------------------------------------------------------- Stadtplan
// Kreuzungen auf einem Raster (x nach Osten, z nach Süden, Norden = −z). Zwischen Spalte 3 und 4 fliesst der Fluss,
// Brücken gibt es nur in Reihe 1 und 3. Bei (2,2) ist der Kreisel.
var GX = [0, 54, 108, 162, 222, 276], GZ = [0, 40, 80, 120, 160];
var RB = { i: 2, j: 2, r: 8 }, RBX = GX[2], RBZ = GZ[2];
var RIV = [183, 201];
var OFF = { a: 13, b: 27, c: 41, B: 27 };
// [Ort, H/V, i, j, Seite, Platz]   H-Strassen (Ost–West) haben Plätze a, b, c oder gross B; V-Strassen nur aussen (Platz B in der Mitte)
var NAMED = [
  ['farm', 'H', 0, 0, 'N', 'B'], ['school', 'H', 1, 0, 'N', 'B'], ['church', 'H', 2, 0, 'N', 'B'], ['space', 'H', 4, 0, 'N', 'B'],
  ['bakery', 'H', 0, 0, 'S', 'b'], ['postoffice', 'H', 1, 0, 'S', 'a'], ['museum', 'H', 2, 0, 'S', 'b'], ['vet', 'H', 4, 0, 'S', 'b'],
  ['park', 'H', 0, 1, 'N', 'B'], ['butcher', 'H', 1, 1, 'N', 'a'], ['bank', 'H', 2, 1, 'N', 'b'], ['pharmacy', 'H', 4, 1, 'N', 'a'],
  ['restaurant', 'H', 0, 1, 'S', 'b'], ['cinema', 'H', 1, 1, 'S', 'b'], ['police', 'H', 2, 1, 'S', 'B'], ['supermarket', 'H', 4, 1, 'S', 'B'],
  ['court', 'H', 0, 2, 'N', 'b'], ['firestation', 'H', 2, 2, 'N', 'c'], ['site', 'H', 4, 2, 'N', 'b'],
  ['casino', 'H', 0, 2, 'S', 'a'], ['library', 'H', 1, 3, 'N', 'b'],
  ['taxi', 'H', 1, 4, 'N', 'c'], ['station', 'H', 1, 4, 'S', 'B'], ['hospital', 'H', 4, 4, 'S', 'B'],
  ['airport', 'V', 5, 1, 'E', 'B']
];

var NODES = {}, EDGES = [], EMAP = {}, LOTS = [], SEGS = [];
function rng(seed) { return function () { seed |= 0; seed = seed + 0x6D2B79F5 | 0; var t = Math.imul(seed ^ seed >>> 15, 1 | seed); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
function angd(a, b) { var d = a - b; while (d > Math.PI) d -= 2 * Math.PI; while (d < -Math.PI) d += 2 * Math.PI; return d; }
function isRB(i, j) { return i === RB.i && j === RB.j; }
function jid(i, j) { return isRB(i, j) ? null : 'J' + i + '_' + j; }
function node(id, x, z, t) { if (!NODES[id]) NODES[id] = { id: id, x: x, z: z, t: t, out: [], lots: [] }; return NODES[id]; }
function lineEdge(a, b, seg, bridge) {
  var A = NODES[a], B = NODES[b], dx = B.x - A.x, dz = B.z - A.z, len = Math.hypot(dx, dz), hd = Math.atan2(dz, dx);
  var e = { a: a, b: b, k: 'L', len: len, h0: hd, h1: hd, seg: seg, bridge: !!bridge };
  EDGES.push(e); A.out.push(e); EMAP[a + '>' + b] = e; return e;
}
function arcEdge(a, b, th0) {
  var e = { a: a, b: b, k: 'A', len: RB.r * Math.PI / 2, th0: th0, th1: th0 - Math.PI / 2, seg: 'ring' };
  e.h0 = Math.atan2(-Math.cos(th0), Math.sin(th0)); e.h1 = Math.atan2(-Math.cos(e.th1), Math.sin(e.th1));
  EDGES.push(e); NODES[a].out.push(e); EMAP[a + '>' + b] = e; return e;
}
function epos(e, t) {
  if (e.k === 'A') { var th = e.th0 + (e.th1 - e.th0) * t; return { x: RBX + RB.r * Math.cos(th), z: RBZ + RB.r * Math.sin(th), h: Math.atan2(-Math.cos(th), Math.sin(th)) }; }
  var A = NODES[e.a], B = NODES[e.b]; return { x: A.x + (B.x - A.x) * t, z: A.z + (B.z - A.z) * t, h: e.h0 };
}
var RING = [['RN', -Math.PI / 2], ['RW', Math.PI], ['RS', Math.PI / 2], ['RE', 0]]; // gegen den Uhrzeigersinn (von oben, Norden oben)

function buildPlan() {
  var i, j;
  for (i = 0; i < GX.length; i++) for (j = 0; j < GZ.length; j++) if (!isRB(i, j)) node(jid(i, j), GX[i], GZ[j], 'J');
  RING.forEach(function (r) { node(r[0], RBX + RB.r * Math.cos(r[1]), RBZ + RB.r * Math.sin(r[1]), 'R'); });
  for (var k = 0; k < 4; k++) arcEdge(RING[k][0], RING[(k + 1) % 4][0], RING[k][1]);
  // Strassenstücke
  for (j = 0; j < GZ.length; j++) for (i = 0; i < GX.length - 1; i++) {
    if (i === 3 && j !== 1 && j !== 3) continue;
    SEGS.push({ id: 'H' + i + '_' + j, d: 'H', i: i, j: j, a: isRB(i, j) ? 'RE' : jid(i, j), b: isRB(i + 1, j) ? 'RW' : jid(i + 1, j), bridge: i === 3 });
  }
  for (i = 0; i < GX.length; i++) for (j = 0; j < GZ.length - 1; j++)
    SEGS.push({ id: 'V' + i + '_' + j, d: 'V', i: i, j: j, a: isRB(i, j) ? 'RS' : jid(i, j), b: isRB(i, j + 1) ? 'RN' : jid(i, j + 1) });
  var segById = {}; SEGS.forEach(function (s) { segById[s.id] = s; s.lots = []; });
  // Plätze: benannte zuerst, dann gewöhnliche Häuser
  var taken = {};
  function addLot(place, d, i, j, side, slot) {
    var s = segById[d + i + '_' + j]; if (!s) throw new Error('Strasse fehlt ' + d + i + '_' + j);
    var big = slot === 'B', outer = (d === 'H' && ((j === 0 && side === 'N') || (j === GZ.length - 1 && side === 'S'))) || d === 'V';
    var w = big ? 40 : 12, dep = outer ? (big ? 22 : 14) : 13, sg = side === 'N' || side === 'W' ? -1 : 1, off = d === 'V' ? 20 : OFF[slot];
    var L = { id: 'L' + LOTS.length, place: place, seg: s.id, side: side, slot: slot, off: off, w: w, d: dep, big: big, outer: outer };
    if (d === 'H') { L.x = GX[i] + off; L.z = GZ[j] + sg * (5.5 + dep / 2); L.sx = L.x; L.sz = GZ[j]; L.fx = 0; L.fz = -sg; }
    else { L.z = GZ[j] + off; L.x = GX[i] + sg * (5.5 + dep / 2); L.sx = GX[i]; L.sz = L.z; L.fx = -sg; L.fz = 0; if (big) { L.w = 26; } }
    LOTS.push(L); s.lots.push(L); taken[s.id + side + slot] = 1; if (big) taken[s.id + side + 'all'] = 1;
    return L;
  }
  NAMED.forEach(function (n) { addLot(n[0], n[1], n[2], n[3], n[4], n[5]); });
  var R = rng(7);
  SEGS.forEach(function (s) {
    if (s.bridge) return;
    if (s.d === 'H') {
      ['N', 'S'].forEach(function (side) {
        if (taken[s.id + side + 'all']) return;
        ['a', 'b', 'c'].forEach(function (slot) {
          if (taken[s.id + side + slot]) return;
          if (s.a === 'RE' && slot === 'a') return;   // zu nah am Kreisel
          if (s.b === 'RW' && slot === 'c') return;
          addLot(null, 'H', s.i, s.j, side, slot);
        });
      });
    } else if (s.i === 0 || s.i === GX.length - 1) {
      var side = s.i === 0 ? 'W' : 'E';
      if (taken[s.id + side + 'B'] || (s.i === 5 && s.j === 2)) return; // Flughafen-Gelände
      addLot(null, 'V', s.i, s.j, side, 'B');
    }
  });
  LOTS.forEach(function (L) {
    if (L.place) return;
    var center = L.x > 40 && L.x < 170 && L.z > 30 && L.z < 135;
    L.h = center ? 14 + Math.round(R() * 26) : L.outer ? 6 + Math.round(R() * 4) : 8 + Math.round(R() * 12);
    L.roof = !center && (L.h < 12 || R() < .3) ? 'dach' : 'flach';
    L.wall = ['#f3e3c3', '#e8c9a6', '#d7e3ef', '#f1d4cf', '#dfe9d6', '#efe7f7', '#f6efe0', '#cfd8e3', '#e9d8b8'][Math.floor(R() * 9)];
  });
  // Haltepunkte entlang jeder Strasse (vor den Häusern), dann Kanten
  SEGS.forEach(function (s) {
    var A = NODES[s.a], B = NODES[s.b], offs = {};
    s.lots.forEach(function (L) { offs[L.off] = 1; });
    var list = Object.keys(offs).map(Number).sort(function (x, y) { return x - y; });
    var chain = [s.a];
    list.forEach(function (o) {
      var id = 'S' + s.id + '_' + o, x = s.d === 'H' ? GX[s.i] + o : GX[s.i], z = s.d === 'H' ? GZ[s.j] : GZ[s.j] + o;
      var n = node(id, x, z, 'S'); n.seg = s.id; chain.push(id);
      s.lots.forEach(function (L) { if (L.off === o) { n.lots.push(L); L.stop = id; } });
    });
    chain.push(s.b); s.chain = chain;
    for (var k = 0; k < chain.length - 1; k++) { lineEdge(chain[k], chain[k + 1], s.id, s.bridge); lineEdge(chain[k + 1], chain[k], s.id, s.bridge); }
  });
}
buildPlan();

function isBuilding(L) { return !L.place || !PLACES[L.place].open; }
function lotName(L) { return L.place ? PLACES[L.place].en : L.h >= 14 ? 'flats' : 'house'; }
function lotArt(L) { return L.place ? 'the ' + PLACES[L.place].en : L.h >= 14 ? 'flats' : 'a house'; }
function sideOf(L, x, z, hd) { var rx = -Math.sin(hd), rz = Math.cos(hd); return ((L.x - x) * rx + (L.z - z) * rz) > 0 ? 'R' : 'L'; }
function rel(h0, h1) { var d = angd(h1, h0); return Math.abs(d) < 0.6 ? 'S' : Math.abs(d) > 2.5 ? 'B' : d > 0 ? 'R' : 'L'; }
function straightEdge(id, hd) { var best = null, bd = 0.6; NODES[id].out.forEach(function (e) { var d = Math.abs(angd(e.h0, hd)); if (d < bd) { bd = d; best = e; } }); return best; }
function ringEntry(id, hd) { var n = NODES[id]; return n.t === 'R' && Math.abs(angd(Math.atan2(RBZ - n.z, RBX - n.x), hd)) < 0.7; }
function ringArc(id) { return NODES[id].out.filter(function (e) { return e.k === 'A'; })[0]; }
function ringArm(id) { return NODES[id].out.filter(function (e) { return e.k !== 'A'; })[0]; }
var ORD = ['first', 'second', 'third', 'fourth', 'fifth'], ORDDE = ['1.', '2.', '3.', '4.', '5.'];
var DIR = { L: 'left', R: 'right' }, DIRDE = { L: 'links ⬅', R: 'rechts ➡', S: 'geradeaus ⬆', B: 'zurück ⬇' };
function cap(s) { return s.charAt(0).toUpperCase() + s.slice(1); }

// ---------------------------------------------------------------------- Wege erfinden
// Ergebnis: { nodes:[…], stepOf:[…], steps:[{t, text, …}], start: Los, target: Los, face }
function genRoute(lv) {
  for (var k = 0; k < 900; k++) { var r = tryRoute(lv); if (r) return r; }
  return null;
}
function tryRoute(lv) {
  var R = Math.random, starts = LOTS.filter(function (L) { return L.place && isBuilding(L) && L.stop && NODES[L.stop].t === 'S'; });
  var L0 = starts[Math.floor(R() * starts.length)], start = L0.stop, face = Math.atan2(L0.fz, L0.fx);
  var turn = R() < .5 ? 'L' : 'R', hd = face + (turn === 'R' ? Math.PI / 2 : -Math.PI / 2);
  if (!straightEdge(start, hd)) return null;
  var nodes = [start], stepOf = [0], steps = [], pend = [], cross = 0, dec = 0, want = lv.ev[0] + Math.floor(R() * (lv.ev[1] - lv.ev[0] + 1));
  var visited = {}, hadBridge = false, hadRound = false, lm = 0, crossNo = {};
  steps.push({ t: 'start', turn: turn, text: 'Start in front of the ' + PLACES[L0.place].en + '. Turn ' + DIR[turn] + ' and walk straight on.' });
  var cur = start, justDecided = true;
  function emit(st) { steps.push(st); var k = steps.length - 1; pend.forEach(function (ix) { stepOf[ix] = k; }); pend = []; return k; }
  function push(id) { nodes.push(id); stepOf.push(null); pend.push(nodes.length - 1); }
  function finalSeg(e) {
    // Ziel auf dem Strassenstück nach einer Entscheidung suchen
    if (e.bridge || e.k === 'A' || dec < want) return null;
    var walk = [], id = e.b, h = e.h1, seen = { L: [], R: [] }, cands = [];
    var prevBlock = { L: false, R: false };
    while (NODES[id].t === 'S') {
      walk.push(id);
      var n = NODES[id];
      ['L', 'R'].forEach(function (sd) {
        n.lots.forEach(function (L) {
          if (sideOf(L, n.x, n.z, h) !== sd) return;
          seen[sd].push(L);
          if (L.place && isBuilding(L) && L.place !== L0.place && !prevBlock[sd]) cands.push({ L: L, side: sd, ord: seen[sd].length, walk: walk.slice(), prev: seen[sd].slice(0, -1) });
          if (!isBuilding(L)) prevBlock[sd] = true;
        });
      });
      var nx = straightEdge(id, h); if (!nx) break; id = nx.b; h = nx.h1;
    }
    if (!cands.length) return null;
    return cands[Math.floor(R() * cands.length)];
  }
  function finish(c) {
    c.walk.forEach(function (id) { push(id); });
    var p = c.prev.length ? c.prev[c.prev.length - 1] : null, txt;
    if (lv.lm && p && p.place && R() < .5) txt = 'Walk past the ' + PLACES[p.place].en + '. The next building on your ' + DIR[c.side] + ' is your goal.';
    else txt = 'Stop at the ' + ORD[c.ord - 1] + ' building on your ' + DIR[c.side] + '.';
    emit({ t: 'end', side: c.side, ord: c.ord, text: txt });
    if (lv.round === 'need' && !hadRound) return null;
    if (lv.bridge === 'need' && !hadBridge) return null;
    return { nodes: nodes, stepOf: stepOf, steps: steps, start: L0, target: c.L, face: face, crossNo: crossNo };
  }
  // erste Bewegung nach dem Start
  var e = straightEdge(start, hd);
  for (var guard = 0; guard < 40; guard++) {
    if (justDecided && e && !e.bridge && e.k !== 'A') {
      var c = finalSeg(e); if (c) return finish(c);
    }
    // dem Strassenstück folgen bis zur nächsten Kreuzung / zum Kreisel
    var passed = [];
    while (true) {
      if (e.bridge) { hadBridge = true; if (lv.bridge === 'no') return null; }
      push(e.b); cur = e.b; hd = e.h1;
      if (NODES[cur].t !== 'S') break;
      passed.push(cur);
      e = straightEdge(cur, hd); if (!e) return null;
    }
    // Sehenswürdigkeit am Weg («walk past the …»), nur direkt nach einer Entscheidung
    if (lv.lm && justDecided && lm < 2 && passed.length && R() < .55) {
      var named = [];
      passed.forEach(function (id) { NODES[id].lots.forEach(function (L) { if (L.place && L.place !== L0.place) named.push({ L: L, id: id }); }); });
      if (named.length) {
        var pk = named[Math.floor(R() * named.length)], sd = sideOf(pk.L, NODES[pk.id].x, NODES[pk.id].z, hd);
        var last = pend.pop(); // die Kreuzung gehört zum nächsten Satz
        emit({ t: 'lm', text: R() < .5 ? 'Walk past the ' + PLACES[pk.L.place].en + '.' : 'On your ' + DIR[sd] + ' you can see the ' + PLACES[pk.L.place].en + '.' });
        pend.push(last); lm++;
      }
    }
    justDecided = false;
    var N = NODES[cur];
    if (visited[cur] || dec > want) return null; visited[cur] = 1;
    if (N.t === 'R') {
      if (lv.round === 'no' || hadRound) return null;
      hadRound = true;
      var ex = 1 + Math.floor(R() * 3), rid = cur, txt = (cross > 0 ? 'Walk straight on to the roundabout. Take the ' : 'At the roundabout take the ') + ORD[ex - 1] + ' exit.';
      for (var q = 0; q < ex; q++) { var a = ringArc(rid); push(a.b); rid = a.b; }
      e = ringArm(rid); hd = e.h0; cross = 0; dec++;
      emit({ t: 'round', exit: ex, text: txt });
      justDecided = true; continue;
    }
    var opts = N.out.filter(function (o) { return rel(hd, o.h0) !== 'B'; }), byRel = {};
    opts.forEach(function (o) { byRel[rel(hd, o.h0)] = o; });
    if (!byRel.S) {
      var turns = Object.keys(byRel); if (!turns.length) return null;
      var tr = turns[Math.floor(R() * turns.length)];
      e = byRel[tr]; hd = e.h0; dec++;
      emit({ t: 'endst', dir: tr, text: (cross > 0 ? 'Walk straight on to the end of the street. Turn ' : 'Walk to the end of the street and turn ') + DIR[tr] + '.' + (e.bridge ? ' Cross the bridge.' : '') });
      cross = 0; justDecided = true; continue;
    }
    var goStraight = R() < (lv.straight || .35) && cross < 2;
    if (goStraight) {
      cross++; crossNo[nodes.length - 1] = cross;
      e = byRel.S;
      if (e.bridge) { emit({ t: 'bridge', text: 'Walk straight on and cross the bridge.' }); cross = 0; dec++; justDecided = true; }
      continue;
    }
    var tl = Object.keys(byRel).filter(function (x) { return x !== 'S'; });
    if (!tl.length) return null;
    var td = tl[Math.floor(R() * tl.length)];
    crossNo[nodes.length - 1] = cross + 1;
    e = byRel[td]; hd = e.h0; dec++;
    emit({ t: 'turn', dir: td, n: cross + 1, text: 'At the ' + ORD[cross] + ' crossing turn ' + DIR[td] + '.' + (e.bridge ? ' Cross the bridge.' : '') });
    cross = 0; justDecided = true;
  }
  return null;
}

// Kürzester Weg (für «Orte» und «Berufe»)
function shortest(from, toSet) {
  var dist = {}, prev = {}, Q = [from]; dist[from] = 0;
  while (Q.length) {
    Q.sort(function (a, b) { return dist[a] - dist[b]; });
    var u = Q.shift(); if (toSet[u]) { var p = [u]; while (prev[u]) { u = prev[u]; p.unshift(u); } return p; }
    NODES[u].out.forEach(function (e) { var d = dist[u] + e.len; if (dist[e.b] == null || d < dist[e.b]) { dist[e.b] = d; prev[e.b] = u; Q.push(e.b); } });
  }
  return [from];
}

// ---------------------------------------------------------------------- Sprache (Englisch vorlesen)
// Stimme wählen wie in der Vokabelkiste: lieber Frauenstimme, britisch, «natural/neural/premium/enhanced/online»; Spassstimmen nie.
var FEMALE = /\b(female|samantha|karen|moira|tessa|serena|kate|stephanie|martha|fiona|victoria|allison|ava|susan|zira|hazel|libby|sonia|aria|jenny|emma|amy|joanna|salli|kimberly|olivia|natasha|clara)\b/i;
var MALE = /\b(male|daniel|alex|fred|oliver|george|ryan|guy|david|mark|james|thomas|arthur|rishi|aaron|gordon|reed|rocko|eddy|grandpa)\b/i;
var SILLY = /\b(albert|bad news|bahh|bells|boing|bubbles|cellos|good news|jester|organ|superstar|trinoids|whisper|wobble|zarvox|junior|ralph|kathy|princess|deranged|hysterical|pipe organ)\b/i;
var VKEY = 'kn_ow_voice', VOICE = null, curU = null, SAYRUN = 0;
function enVoices() { try { return (speechSynthesis.getVoices() || []).filter(function (v) { return v.lang && /^en/i.test(v.lang) && !SILLY.test(v.name); }); } catch (e) { return []; } }
function pickVoice() {
  var vs = enVoices(); if (!vs.length) return;
  var want = null; try { want = localStorage.getItem(VKEY); } catch (e) {}
  var w = want && vs.filter(function (v) { return v.name === want; })[0]; if (w) { VOICE = w; return; }
  function sc(v) { var n = v.name.replace(/female/ig, ''); return (FEMALE.test(v.name) ? 10 : 0) - (MALE.test(n) ? 10 : 0) + (/en[-_]gb/i.test(v.lang) ? 3 : 0) + (/natural|neural|premium|enhanced|online/i.test(v.name) ? 4 : 0); }
  VOICE = vs.slice().sort(function (a, b) { return sc(b) - sc(a); })[0];
}
try { pickVoice(); speechSynthesis.addEventListener('voiceschanged', pickVoice); } catch (e) {}
function canSay() { try { return !!window.speechSynthesis && !!window.SpeechSynthesisUtterance; } catch (e) { return false; } }
function utter(t, rate) {
  if (!VOICE) pickVoice();
  var u = new SpeechSynthesisUtterance(t); if (VOICE) { u.voice = VOICE; u.lang = String(VOICE.lang).replace('_', '-'); } else u.lang = 'en-GB';
  u.rate = rate || .9; u.pitch = 1; curU = u; return u;
}
function say(t, rate) { return sayList([t], rate, 0); }
// Mehrere Sätze nacheinander, mit Pause dazwischen (Stufe «Listening»)
function sayList(list, rate, pause) {
  if (!canSay()) return false;
  var run = ++SAYRUN, k = 0;
  try { var ss = speechSynthesis; if (ss.speaking || ss.pending) ss.cancel(); if (ss.paused) ss.resume(); } catch (e) { return false; }
  function next() {
    if (run !== SAYRUN || k >= list.length) return;
    var t = list[k++], done = false, u = utter(t, rate);
    function fin() { if (done) return; done = true; setTimeout(next, pause || 0); }
    u.onend = fin; u.onerror = fin;
    setTimeout(fin, 1500 + t.split(' ').length * 650 / (rate || .9)); // falls «onend» nicht kommt
    try { speechSynthesis.speak(u); } catch (e) {}
  }
  next(); return true;
}
function stopSay() { SAYRUN++; try { speechSynthesis.cancel(); } catch (e) {} }

// ---------------------------------------------------------------------- 3D-Welt
var WD = null; // die Welt (wird nur einmal gebaut)
var MATS = {};
function M(c) { return MATS[c] || (MATS[c] = new THREE.MeshLambertMaterial({ color: c })); }
function mesh(geo, c, x, y, z, par, sh) {
  var m = new THREE.Mesh(geo, typeof c === 'string' ? M(c) : c); m.position.set(x || 0, y || 0, z || 0);
  if (sh !== false) { m.castShadow = true; m.receiveShadow = true; } if (par) par.add(m); return m;
}
function bx(w, h, d, c, x, y, z, par, sh) { return mesh(new THREE.BoxGeometry(w, h, d), c, x, y, z, par, sh); }
function cyl(rt, rb, h, c, x, y, z, par, seg) { return mesh(new THREE.CylinderGeometry(rt, rb, h, seg || 12), c, x, y, z, par); }
function canvasTex(w, h, draw) {
  var cv = document.createElement('canvas'); cv.width = w; cv.height = h; draw(cv.getContext('2d'), w, h);
  var t = new THREE.CanvasTexture(cv); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 4; return t;
}
var FONT = '"Patrick Hand","Comic Sans MS",cursive';
function rr(g, x, y, w, h, r) { g.beginPath(); g.moveTo(x + r, y); g.arcTo(x + w, y, x + w, y + h, r); g.arcTo(x + w, y + h, x, y + h, r); g.arcTo(x, y + h, x, y, r); g.arcTo(x, y, x + w, y, r); g.closePath(); }
function signTex(text, emo, bg) {
  return canvasTex(768, 160, function (g, w, h) {
    rr(g, 4, 4, w - 8, h - 8, 26); g.fillStyle = '#fff'; g.fill(); g.lineWidth = 8; g.strokeStyle = bg; g.stroke();
    g.fillStyle = bg; g.font = '92px ' + FONT; g.textAlign = 'center'; g.textBaseline = 'middle';
    var t = (emo ? emo + ' ' : '') + text.toUpperCase(); var m = g.measureText(t).width; if (m > w - 50) g.font = Math.floor(92 * (w - 50) / m) + 'px ' + FONT;
    g.fillText(t, w / 2, h / 2 + 6);
  });
}
function sign(L, par, y, wmax) {
  var P = PLACES[L.place], w = Math.min(wmax || L.w * .9, 11), t = signTex(P.en, P.emo, P.sign);
  var m = new THREE.Mesh(new THREE.PlaneGeometry(w, w * 160 / 768), new THREE.MeshBasicMaterial({ map: t }));
  m.position.set(0, y, L.d / 2 + 0.08); par.add(m); return m;
}
function placeSprite(text) {
  var t = canvasTex(640, 128, function (g, w, h) {
    g.font = '72px ' + FONT; var m = Math.min(w - 16, g.measureText(text).width + 56);
    rr(g, (w - m) / 2, 12, m, h - 24, 40); g.fillStyle = 'rgba(31,36,33,.82)'; g.fill(); g.lineWidth = 5; g.strokeStyle = '#d6ad45'; g.stroke();
    g.fillStyle = '#ffffff'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText(text, w / 2, h / 2 + 4);
  });
  var s = new THREE.Sprite(new THREE.SpriteMaterial({ map: t, sizeAttenuation: false })); s.scale.set(.25, .05, 1); s.renderOrder = 5; return s;
}
function emoSprite(emo, sz) {
  var t = canvasTex(128, 128, function (g) { g.font = '100px Arial'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText(emo, 64, 72); });
  var s = new THREE.Sprite(new THREE.SpriteMaterial({ map: t, depthTest: false })); s.scale.set(sz, sz, 1); s.renderOrder = 11; return s;
}
function labelSprite(text, bg, fg) {
  var t = canvasTex(512, 128, function (g, w, h) {
    g.font = '76px ' + FONT; var m = Math.min(w - 20, g.measureText(text).width + 60);
    rr(g, (w - m) / 2, 10, m, h - 20, 50); g.fillStyle = bg || 'rgba(255,255,255,.95)'; g.fill(); g.lineWidth = 6; g.strokeStyle = '#d6ad45'; g.stroke();
    g.fillStyle = fg || '#1f2421'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText(text, w / 2, h / 2 + 4);
  });
  var s = new THREE.Sprite(new THREE.SpriteMaterial({ map: t })); s.scale.set(6, 1.5, 1); return s;
}
var WIN = {};
function wallMat(col, kind) {
  var k = col + kind; if (WIN[k]) return WIN[k];
  var t = canvasTex(128, 128, function (g) {
    g.fillStyle = col; g.fillRect(0, 0, 128, 128);
    g.fillStyle = 'rgba(0,0,0,.05)'; for (var y = 0; y < 128; y += 8) g.fillRect(0, y, 128, 1);
    var gl = g.createLinearGradient(0, 20, 0, 100); gl.addColorStop(0, '#9cc3de'); gl.addColorStop(.55, '#5f87a8'); gl.addColorStop(1, '#7ea6c4');
    if (kind === 'office') {
      g.fillStyle = gl; g.fillRect(8, 16, 112, 84); g.fillStyle = shade(col, -.25); g.fillRect(8, 98, 112, 8);
      g.fillStyle = 'rgba(255,255,255,.75)'; g.fillRect(62, 16, 4, 84); g.fillRect(8, 56, 112, 3);
      g.fillStyle = 'rgba(255,255,255,.25)'; g.beginPath(); g.moveTo(14, 96); g.lineTo(44, 20); g.lineTo(58, 20); g.lineTo(28, 96); g.fill();
    } else {
      g.fillStyle = '#ffffff'; g.fillRect(30, 22, 68, 76);
      g.fillStyle = gl; g.fillRect(36, 28, 56, 64);
      g.fillStyle = ['#e8d8b0', '#f0c8c0', '#d0e0c8', '#ffffff'][col.length % 4]; g.fillRect(36, 28, 12, 64); g.fillRect(80, 28, 12, 64);
      g.fillStyle = '#ffffff'; g.fillRect(62, 28, 4, 64); g.fillRect(36, 56, 56, 4);
      g.fillStyle = shade(col, -.3); g.fillRect(26, 98, 76, 7);
      g.fillStyle = 'rgba(255,255,255,.22)'; g.beginPath(); g.moveTo(40, 88); g.lineTo(56, 30); g.lineTo(62, 30); g.lineTo(46, 88); g.fill();
    }
  });
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  return (WIN[k] = new THREE.MeshLambertMaterial({ map: t }));
}
// Kasten mit Fenstern (Fensterraster ca. alle 3.4 m)
function house(w, h, d, col, kind, par, x, y, z) {
  var geo = new THREE.BoxGeometry(w, h, d), uv = geo.attributes.uv, cell = kind === 'office' ? 3.2 : 3.6;
  // Flächen: +x, −x, +y, −y, +z, −z (je 4 Ecken)
  for (var f = 0; f < 6; f++) {
    var sx = (f < 2 ? d : w) / cell, sy = (f === 2 || f === 3 ? 0 : h / cell);
    for (var v = 0; v < 4; v++) { var ix = f * 4 + v; uv.setXY(ix, uv.getX(ix) * Math.max(1, Math.round(sx)), uv.getY(ix) * Math.max(0.001, Math.round(sy))); }
  }
  var wm = wallMat(col, kind || 'win'), top = M(shade(col, -0.15));
  var m = new THREE.Mesh(geo, [wm, wm, top, top, wm, wm]); m.position.set(x || 0, (y || 0) + h / 2, z || 0); m.castShadow = m.receiveShadow = true; par.add(m); return m;
}
function shade(hex, f) {
  var n = parseInt(hex.slice(1), 16), r = n >> 16 & 255, g = n >> 8 & 255, b = n & 255;
  function c(v) { return Math.max(0, Math.min(255, Math.round(f < 0 ? v * (1 + f) : v + (255 - v) * f))); }
  return '#' + ((1 << 24) + (c(r) << 16) + (c(g) << 8) + c(b)).toString(16).slice(1);
}
function roof(w, d, hr, col, par, y) {
  var s = new THREE.Shape(); s.moveTo(-d / 2 - .5, 0); s.lineTo(d / 2 + .5, 0); s.lineTo(0, hr); s.closePath();
  var g = new THREE.ExtrudeGeometry(s, { depth: w + 1, bevelEnabled: false }); g.translate(0, 0, -(w + 1) / 2); g.rotateY(Math.PI / 2);
  return mesh(g, col, 0, y, 0, par);
}
function door(par, L, w, h, c) { return bx(w || 2, h || 3, .3, c || '#6b4a2f', 0, (h || 3) / 2, L.d / 2 + .1, par); }
function awning(par, L, w, c1, c2, y) {
  var t = canvasTex(128, 32, function (g) { for (var k = 0; k < 8; k++) { g.fillStyle = k % 2 ? c2 : c1; g.fillRect(k * 16, 0, 16, 32); } });
  var m = new THREE.Mesh(new THREE.BoxGeometry(w, .3, 2.4), new THREE.MeshLambertMaterial({ map: t }));
  m.position.set(0, y || 3.6, L.d / 2 + 1.1); m.rotation.x = .25; m.castShadow = true; par.add(m);
}
function columns(par, L, n, h, w, c) { for (var k = 0; k < n; k++) cyl(.45, .5, h, c || '#fbf6ec', -w / 2 + w * k / (n - 1), h / 2 + .6, L.d / 2 + 1.4, par); bx(w + 3, .6, 3.6, '#efe6d6', 0, .3, L.d / 2 + 1.2, par); }
var TG = null;
function treeAt(x, z, s, kind) {
  var I = WD.INS; s = s || 1;
  I.trunk.push([x, s, z, s, s, s]);
  if (kind === 'laub') I.crown.push([x, 3.6 * s, z, 2.2 * s, 2 * s, 2.2 * s]); else I.cone.push([x, 3.4 * s, z, s, s, s]);
}
function instM(g, x, y, z, sx, sy, sz) { var o = new THREE.Object3D(); o.position.set(x, y, z); o.scale.set(sx, sy, sz); o.updateMatrix(); return new THREE.Matrix4().multiplyMatrices(g.matrixWorld, o.matrix); }
function buildInst(geo, mat, list, sh, cols) {
  if (!list.length) return null;
  var m = new THREE.InstancedMesh(geo, mat, list.length), o = new THREE.Object3D(), c = new THREE.Color();
  list.forEach(function (p, k) {
    if (p.isMatrix4) m.setMatrixAt(k, p); else { o.position.set(p[0], p[1], p[2]); o.scale.set(p[3], p[4], p[5]); o.rotation.set(0, 0, 0); o.updateMatrix(); m.setMatrixAt(k, o.matrix); }
    if (cols) m.setColorAt(k, c.set(cols[k % cols.length]));
  });
  m.castShadow = sh !== false; m.receiveShadow = true; WD.city.add(m); return m;
}
function noiseTex(col, amt, cell, tiles) {
  return (function () {
    var t = canvasTex(128, 128, function (g) {
      g.fillStyle = col; g.fillRect(0, 0, 128, 128); var R = rng(col.length * 7 + amt);
      for (var k = 0; k < 900; k++) { var v = (R() - .5) * amt; g.fillStyle = v > 0 ? 'rgba(255,255,255,' + v / 100 + ')' : 'rgba(0,0,0,' + (-v) / 100 + ')'; g.fillRect(R() * 128, R() * 128, 1 + R() * 3, 1 + R() * 3); }
      if (tiles) { g.strokeStyle = 'rgba(0,0,0,.09)'; g.lineWidth = 2; for (var q = 0; q <= 128; q += 32) { g.beginPath(); g.moveTo(q, 0); g.lineTo(q, 128); g.moveTo(0, q); g.lineTo(128, q); g.stroke(); } }
    });
    t.wrapS = t.wrapT = THREE.RepeatWrapping; return t;
  })();
}
function tree(par, x, z, s, c) {
  if (par === WD.city) return treeAt(x, z, s, c === 'laub' || (c == null && ((x * 7 + z * 3) | 0) % 3 === 0) ? 'laub' : 'nadel');
  s = s || 1; TG = TG || { st: new THREE.CylinderGeometry(.25, .35, 2, 6), co: new THREE.ConeGeometry(1.6, 3.6, 7) };
  var a = mesh(TG.st, '#8a5a3a', x, s, z, par); a.scale.setScalar(s);
  var k = mesh(TG.co, c || '#4f9a4a', x, 3.4 * s, z, par); k.scale.setScalar(s);
  return k;
}
function car(par, x, z, rot, col, kind) {
  var g = new THREE.Group(); g.position.set(x, 0, z); g.rotation.y = rot || 0; par.add(g);
  var L = kind === 'truck' ? 7.5 : kind === 'van' ? 5.2 : 4.4, H = kind === 'truck' ? 2.6 : kind === 'van' ? 2.3 : 1.2;
  bx(2.1, H, L, col, 0, .5 + H / 2, 0, g);
  if (kind !== 'truck') bx(1.9, 1, L * .55, kind === 'van' ? col : '#bfe0f5', 0, .5 + H + .5, kind === 'van' ? 0 : -.2, g);
  [[-1, 1], [1, 1], [-1, -1], [1, -1]].forEach(function (p) { var w = cyl(.5, .5, .4, '#222', p[0] * 1.05, .5, p[1] * L * .32, g, 10); w.rotation.z = Math.PI / 2; });
  if (kind === 'taxi') bx(.9, .35, .5, '#222', 0, 2.95, -.2, g);
  if (kind === 'police' || kind === 'amb') { bx(1.2, .3, .4, '#3a7ad0', -.3, kind === 'amb' ? 3.4 : 2.95, -.2, g); bx(.6, .3, .4, '#e03a3a', .35, kind === 'amb' ? 3.4 : 2.95, -.2, g); }
  if (kind === 'truck') { bx(.5, .5, 6, '#c8c8c8', 0, 3.4, -.5, g); }
  return g;
}
function person(o) {
  var g = new THREE.Group(), skin = o.skin || '#f1c7a0';
  bx(.36, 1.05, .42, o.pants, -.22, .55, 0, g); bx(.36, 1.05, .42, o.pants, .22, .55, 0, g);
  bx(1.0, 1.15, .55, o.shirt, 0, 1.65, 0, g);
  if (o.vest) bx(1.02, .9, .2, o.vest, 0, 1.6, .2, g);
  if (o.apron) bx(.8, 1.3, .1, o.apron, 0, 1.4, .3, g);
  bx(.28, 1.0, .3, o.shirt, -.66, 1.6, 0, g); bx(.28, 1.0, .3, o.shirt, .66, 1.6, 0, g);
  mesh(new THREE.SphereGeometry(.44, 14, 10), skin, 0, 2.62, 0, g);
  bx(.08, .08, .02, '#222', -.15, 2.68, .43, g); bx(.08, .08, .02, '#222', .15, 2.68, .43, g);
  if (o.hat === 'chef') { cyl(.42, .38, .7, '#ffffff', 0, 3.25, 0, g); mesh(new THREE.SphereGeometry(.5, 10, 8), '#ffffff', 0, 3.6, 0, g); }
  else if (o.hat === 'cap') { cyl(.47, .47, .3, o.hatC, 0, 3.0, 0, g); bx(.6, .06, .4, o.hatC, 0, 2.9, .4, g); }
  else if (o.hat === 'helmet') { mesh(new THREE.SphereGeometry(.52, 12, 8, 0, Math.PI * 2, 0, Math.PI / 2), o.hatC, 0, 2.8, 0, g); }
  else if (o.hat === 'farmer') { cyl(.8, .8, .08, o.hatC, 0, 2.95, 0, g); cyl(.4, .45, .45, o.hatC, 0, 3.15, 0, g); }
  else if (o.hat === 'beret') { cyl(.5, .45, .2, o.hatC, 0, 3.0, 0, g); }
  else if (o.hat === 'nurse') { bx(.6, .3, .4, '#ffffff', 0, 3.0, .05, g); }
  else if (o.hat === 'space') { var hm = mesh(new THREE.SphereGeometry(.62, 14, 10), new THREE.MeshLambertMaterial({ color: '#cfe0ff', transparent: true, opacity: .55 }), 0, 2.62, 0, g); hm.castShadow = false; }
  else mesh(new THREE.SphereGeometry(.47, 12, 8, 0, Math.PI * 2, 0, Math.PI / 2.2), o.hair || '#3a2a1a', 0, 2.68, -.03, g);
  return g;
}
function owlMesh() {
  var g = new THREE.Group(), body = new THREE.Group(); g.add(body);
  var b = mesh(new THREE.SphereGeometry(1, 20, 16), '#9a6b45', 0, 1.35, 0, body); b.scale.set(1, 1.15, .95);
  var belly = mesh(new THREE.SphereGeometry(.78, 16, 12), '#f1dcb8', 0, 1.2, .32, body); belly.scale.set(1, 1.1, .7);
  [-1, 1].forEach(function (s) {
    var e = mesh(new THREE.SphereGeometry(.34, 14, 10), '#ffffff', s * .36, 1.85, .72, body);
    mesh(new THREE.SphereGeometry(.17, 10, 8), '#1f2421', s * .36, 1.86, 1.0, body);
    mesh(new THREE.SphereGeometry(.06, 6, 6), '#ffffff', s * .32, 1.92, 1.13, body);
    var t = mesh(new THREE.ConeGeometry(.2, .6, 6), '#7a5232', s * .55, 2.55, .1, body); t.rotation.z = -s * .5;
    var w = mesh(new THREE.SphereGeometry(.45, 10, 8), '#7a5232', s * .95, 1.25, -.05, body); w.scale.set(.35, 1, .8);
    var f = mesh(new THREE.ConeGeometry(.16, .35, 6), '#e8a23a', s * .35, .12, .35, g); f.rotation.x = Math.PI / 2;
  });
  var bk = mesh(new THREE.ConeGeometry(.14, .4, 8), '#e8a23a', 0, 1.62, 1.0, body); bk.rotation.x = Math.PI / 2 + .3;
  var sc = cyl(.98, .98, .3, '#d6ad45', 0, 1.05, 0, body, 20); sc.scale.set(1, 1, .95);
  g.userData.body = body;
  g.scale.setScalar(1.05);
  return g;
}

function placeBuild(L, g) {
  var P = PLACES[L.place], d = L.d, w = L.w, fz = d / 2;
  switch (L.place) {
    case 'bakery': house(w, 6, d, P.col, 'win', g); awning(g, L, w, '#e0782c', '#fff4d6'); door(g, L); sign(L, g, 5.1); break;
    case 'butcher': house(w, 6.5, d, P.col, 'win', g); awning(g, L, w, '#c8302c', '#ffffff'); door(g, L); sign(L, g, 5.4); break;
    case 'pharmacy': house(w, 6, d, P.col, 'win', g); awning(g, L, w, '#3a9ad0', '#ffffff'); door(g, L, 2, 3, '#2f8f9a');
      bx(1.6, .5, .2, '#d0367a', 0, 7, fz - .5, g); bx(.5, 1.6, .2, '#d0367a', 0, 7, fz - .5, g); sign(L, g, 5.0); break;
    case 'vet': house(w, 6.5, d, P.col, 'win', g); bx(w + .6, .5, d + .6, '#c8302c', 0, 6.7, 0, g); door(g, L, 2, 3, '#2f8f9a'); sign(L, g, 5.2); break;
    case 'postoffice': house(w, 7, d, P.col, 'office', g); bx(w + .6, .5, d + .6, '#2a6fb0', 0, 7.2, 0, g); door(g, L); sign(L, g, 5.6); car(g, w / 2 + 2.5, fz - 2, 0, '#f4f4f4', 'van'); break;
    case 'restaurant': house(w, 6, d, P.col, 'win', g); roof(w, d, 3, '#c0392b', g, 6); door(g, L, 2.4, 3.2, '#b8302c'); sign(L, g, 4.8); break;
    case 'cinema': house(w, 9, d, P.col, 'office', g); var mq = bx(w + 1, 1.2, 3, '#3a6ad0', 0, 4.4, fz + 1.2, g);
      door(g, L, 3, 3.6, '#4a2a1a'); sign(L, g, 7.2); for (var k = 0; k < 6; k++) mesh(new THREE.SphereGeometry(.22, 8, 6), new THREE.MeshBasicMaterial({ color: '#ffe48a' }), -w / 2 + .8 + k * (w - 1.6) / 5, 5.15, fz + 2.6, g); break;
    case 'casino': house(w, 8, d, P.col, 'office', g); bx(w + .4, 1, d + .4, '#e0368a', 0, 8.3, 0, g);
      [-3, 0, 3].forEach(function (x) { var s = mesh(new THREE.OctahedronGeometry(1), new THREE.MeshBasicMaterial({ color: '#ffd23a' }), x * .9, 10.3, fz - 1, g); s.userData.spin = 1; WD.spin.push(s); });
      door(g, L, 3, 3.4, '#e0368a'); sign(L, g, 6.4); break;
    case 'library': house(w, 8, d, P.col, 'win', g); roof(w, d, 2.4, '#5a3a2a', g, 8); door(g, L, 2.4, 3.4, '#3a2a1a'); sign(L, g, 6.3);
      ['#d23a3a', '#3a7ad0', '#f6c623', '#3a9a5a'].forEach(function (c, k) { bx(.6, 2.2, .3, c, -2 + k * .8, 1.5, fz + .25, g); }); break;
    case 'bank': house(w, 9, d, P.col, 'office', g); columns(g, L, 4, 6, w - 3); bx(w, 1, 4, '#f4ecdc', 0, 7.1, fz + 1.3, g); door(g, L, 2.4, 3.6, '#3a5a3a'); sign(L, g, 8.2); break;
    case 'museum': house(w, 9, d, P.col, 'win', g); columns(g, L, 5, 6.5, w - 2.5);
      var pd = new THREE.Shape(); pd.moveTo(-w / 2 - .5, 0); pd.lineTo(w / 2 + .5, 0); pd.lineTo(0, 2.4); pd.closePath();
      mesh(new THREE.ExtrudeGeometry(pd, { depth: 3.6, bevelEnabled: false }), '#efe2c4', 0, 7.1, fz - 1, g);
      bx(w, .6, 4, '#efe2c4', 0, 7.1, fz + 1.2, g); door(g, L, 2.4, 3.6, '#5a3a1a'); sign(L, g, 8.4, 9); break;
    case 'court': house(w, 9, d, P.col, 'win', g); columns(g, L, 4, 6.2, w - 3);
      var cp = new THREE.Shape(); cp.moveTo(-w / 2 - .5, 0); cp.lineTo(w / 2 + .5, 0); cp.lineTo(0, 2.6); cp.closePath();
      mesh(new THREE.ExtrudeGeometry(cp, { depth: 3.6, bevelEnabled: false }), '#c9a08e', 0, 7.0, fz - 1, g);
      bx(w, .6, 4, '#c9a08e', 0, 7.0, fz + 1.2, g); door(g, L, 2.4, 3.6, '#5a2a1a'); sign(L, g, 8.3, 9); break;
    case 'firestation': house(w, 7.5, d, P.col, 'win', g); bx(w - 3, 5, .3, '#5a2a24', 0, 2.5, fz + .1, g);
      for (var k2 = 0; k2 < 5; k2++) bx(w - 3.4, .12, .32, '#7a3a34', 0, .8 + k2, fz + .2, g); sign(L, g, 6.4);
      car(g, w / 2 + 1.5, fz - 2.5, 0, '#d8302a', 'truck'); break;
    case 'police': house(w, 10, d, P.col, 'office', g); bx(w + .6, .6, d + .6, '#1d4f96', 0, 10.2, 0, g);
      var hp = cyl(4, 4, .2, '#3a3a3a', 0, 10.6, 0, g, 20); var ht = canvasTex(128, 128, function (gg) { gg.fillStyle = '#3a3a3a'; gg.fillRect(0, 0, 128, 128); gg.fillStyle = '#fff'; gg.font = 'bold 90px Arial'; gg.textAlign = 'center'; gg.textBaseline = 'middle'; gg.fillText('H', 64, 68); });
      var hm = new THREE.Mesh(new THREE.CircleGeometry(3.6, 20), new THREE.MeshBasicMaterial({ map: ht })); hm.rotation.x = -Math.PI / 2; hm.position.set(0, 10.72, 0); g.add(hm);
      door(g, L, 3, 3.4, '#1d3f76'); sign(L, g, 7.8, 13); car(g, -w / 2 + 4, fz + 2.2, Math.PI / 2, '#f4f4f4', 'police'); break;
    case 'hospital': house(w, 22, d, P.col, 'office', g); house(14, 10, d + 4, '#e8eef6', 'office', g, -w / 2 + 7, 0, 2);
      bx(.9, 3.4, .3, '#d23a3a', w / 4, 18.5, fz + .2, g); bx(3.4, .9, .3, '#d23a3a', w / 4, 18.5, fz + .2, g);
      door(g, L, 4, 3.6, '#5a7a9a'); sign(L, g, 8.0, 12); car(g, w / 2 - 4, fz + 2.2, Math.PI / 2, '#ffffff', 'amb'); break;
    case 'supermarket': house(w, 8, d, P.col, 'office', g); bx(w + .4, .6, d + .4, '#2f7d4a', 0, 8.3, 0, g); door(g, L, 6, 3.4, '#a8d0e8'); sign(L, g, 6.4, 14);
      [-1, 1].forEach(function (s) { bx(3, 1, 1.4, '#c8302c', s * 6, .5, fz + 1, g); bx(2.8, .4, 1.2, s > 0 ? '#e88a2a' : '#5aa04a', s * 6, 1.2, fz + 1, g); }); break;
    case 'school': house(w - 6, 9, d - 6, P.col, 'win', g, 0, 0, -3); roof(w - 6, d - 6, 3.5, '#c0392b', g, 9).position.z = -3;
      var ck = canvasTex(128, 128, function (gg) { gg.fillStyle = '#fff'; gg.beginPath(); gg.arc(64, 64, 60, 0, 7); gg.fill(); gg.strokeStyle = '#333'; gg.lineWidth = 6; gg.stroke(); gg.beginPath(); gg.moveTo(64, 64); gg.lineTo(64, 22); gg.moveTo(64, 64); gg.lineTo(92, 64); gg.stroke(); });
      var cm = new THREE.Mesh(new THREE.CircleGeometry(1.2, 20), new THREE.MeshBasicMaterial({ map: ck })); cm.position.set(0, 10.6, fz - 5.9); g.add(cm);
      door(g, L, 3, 3.6, '#7a4a24').position.z = fz - 5.9; sign(L, g, 7.6).position.z = fz - 5.85;
      cyl(.12, .12, 9, '#cccccc', w / 2 - 4, 4.5, fz - 1, g, 6); bx(2.2, 1.4, .05, '#d23a3a', w / 2 - 2.8, 8.2, fz - 1, g);
      bx(w, .1, 6, '#e6d6b8', 0, .3, fz - 3, g, false); break;
    case 'church':
      house(12, 9, d - 4, P.col, 'win', g, 0, 0, -2); roof(12, d - 4, 4.5, '#8a3a5a', g, 9).position.z = -2;
      var tw = new THREE.Group(); tw.position.set(0, 0, fz - 4); g.add(tw);
      house(5, 16, 5, '#f8ecdd', 'win', tw); mesh(new THREE.ConeGeometry(3.6, 8, 4), '#8a3a5a', 0, 20, 0, tw).rotation.y = Math.PI / 4;
      bx(.35, 3, .35, '#d6ad45', 0, 25.4, 0, tw); bx(1.8, .35, .35, '#d6ad45', 0, 25.8, 0, tw);
      door(g, L, 2.4, 3.6, '#6b3a2a').position.z = fz - 1.4; sign(L, g, 5.2, 7).position.z = fz - 1.35;
      tree(g, -12, -2, 1.1); tree(g, 12, -4, 1.2); break;
    case 'farm':
      var br = new THREE.Group(); br.position.set(-8, 0, -2); g.add(br);
      house(13, 7, 11, '#c8423a', 'win', br); roof(13, 11, 4.5, '#6b3a2a', br, 7); bx(4, 4.5, .3, '#ffffff', 0, 2.25, 5.6, br);
      sign(L, g, 3.2, 7).position.set(7, 3.2, fz - 6.8);
      bx(9, .3, 7, '#8a6a3a', 9, .15, -3, g, false); for (var r2 = 0; r2 < 4; r2++) bx(8.5, .4, .6, '#5aa04a', 9, .45, -6 + r2 * 2, g);
      for (var f2 = -18; f2 <= 18; f2 += 3) bx(.25, 1.3, .25, '#f4f0e6', f2, .65, fz - 1, g);
      bx(37, .2, .15, '#f4f0e6', 0, 1.1, fz - 1, g);
      [[-14, -12], [-4, -14], [10, -12]].forEach(function (p) { var cw = new THREE.Group(); cw.position.set(p[0], 0, p[1]); g.add(cw); bx(1.2, 1.1, 2.2, '#ffffff', 0, 1.3, 0, cw); bx(.5, .5, .4, '#222', .3, 1.5, .4, cw); bx(.8, .8, .8, '#ffffff', 0, 1.7, 1.3, cw); [[-1, 1], [1, 1], [-1, -1], [1, -1]].forEach(function (q) { bx(.25, .8, .25, '#ffffff', q[0] * .4, .4, q[1] * .8, cw); }); });
      break;
    case 'station':
      house(w - 10, 7, 8, P.col, 'win', g, 0, 0, -4); bx(w, .5, 10, '#2f8f7a', 0, 7.2, 0, g);
      for (var c3 = -2; c3 <= 2; c3++) cyl(.25, .25, 7, '#2f8f7a', c3 * 9, 3.5, 4.2, g, 6);
      bx(w, .8, 5, '#d8d2c6', 0, .4, -8, g); door(g, L, 4, 3.4, '#5a7a8a').position.z = 0.1; sign(L, g, 5.6, 14).position.z = 0.15 + 0;
      var tr = new THREE.Group(); tr.position.set(4, 0, -28.5); g.add(tr);
      bx(30, 3.2, 3, '#f4f4f4', 0, 2.4, 0, tr); bx(30, .9, 3.05, '#d23a3a', 0, 1.6, 0, tr); bx(26, 1, 3.1, '#5a8ab0', 0, 3.1, 0, tr);
      break;
    case 'airport':
      house(34, 9, d, P.col, 'office', g);
      var at = new THREE.Group(); at.position.set(14, 0, -4); g.add(at); cyl(1.4, 1.8, 18, '#e8eef6', 0, 9, 0, at); cyl(3, 2.4, 3, '#5aa0b8', 0, 19.5, 0, at); cyl(3.2, 3.2, .5, '#2a6fb0', 0, 21.2, 0, at);
      var pl = new THREE.Group(); pl.position.set(-4, 0, -26); pl.rotation.y = Math.PI / 2; g.add(pl);
      var fu = cyl(1.4, 1.4, 18, '#f4f8fc', 0, 3, 0, pl, 14); fu.rotation.x = Math.PI / 2; var no = mesh(new THREE.SphereGeometry(1.4, 14, 10), '#f4f8fc', 0, 3, 9, pl);
      bx(20, .4, 3.4, '#cfe0f0', 0, 3, 0, pl); bx(7, .3, 2, '#cfe0f0', 0, 3.6, -8, pl); bx(.3, 3, 2.2, '#2a6fb0', 0, 5, -8, pl);
      [-5, 5].forEach(function (x) { cyl(.7, .7, 2.6, '#9aa8b8', x, 2.3, .6, pl, 10).rotation.x = Math.PI / 2; });
      door(g, L, 5, 3.6, '#8ab8d8'); sign(L, g, 7.2, 10).position.z = L.d / 2 + .08;
      break;
    case 'space':
      house(16, 8, d - 4, P.col, 'office', g, -10, 0, -2);
      var rk = new THREE.Group(); rk.position.set(10, 0, -4); g.add(rk);
      cyl(1.8, 1.8, 22, '#ffffff', 0, 13, 0, rk, 16); mesh(new THREE.ConeGeometry(1.8, 5, 16), '#d23a3a', 0, 26.5, 0, rk);
      [0, 1, 2, 3].forEach(function (k) { var fn = bx(.3, 4, 2.6, '#d23a3a', 0, 3.5, 0, rk); fn.position.x = Math.cos(k * Math.PI / 2) * 2; fn.position.z = Math.sin(k * Math.PI / 2) * 2; fn.rotation.y = -k * Math.PI / 2; });
      cyl(2, 2.4, 2, '#555', 0, 1, 0, rk); bx(1, 24, 1, '#9aa8b8', 4, 12, 0, rk);
      var dr2 = door(g, L, 3, 3.4, '#5a7a9a'); dr2.position.x = -10; dr2.position.z = fz - 3.9; var sg2 = sign(L, g, 6.4, 12); sg2.position.x = -10; sg2.position.z = fz - 3.85; break;
    case 'park':
      bx(w, .2, d, '#8fd46a', 0, .3, 0, g, false);
      var pond = new THREE.Mesh(new THREE.CircleGeometry(5, 24), new THREE.MeshLambertMaterial({ color: '#6ab8e8' })); pond.rotation.x = -Math.PI / 2; pond.position.set(-8, .25, -1); g.add(pond);
      [[-17, -5], [-14, 5], [2, -6], [9, 4], [16, -4], [14, 6], [-2, 5]].forEach(function (p, k) { tree(g, p[0], p[1], 1 + (k % 3) * .2, k % 2 ? '#5aa84a' : '#3f8a3f'); });
      bx(4, .5, 1.2, '#a06a3a', 4, .8, 3, g); bx(4, 1, .2, '#a06a3a', 4, 1.3, 2.5, g);
      var arch = new THREE.Group(); arch.position.set(0, 0, fz - .6); g.add(arch); cyl(.25, .25, 5, '#7a5a3a', -3, 2.5, 0, arch, 6); cyl(.25, .25, 5, '#7a5a3a', 3, 2.5, 0, arch, 6);
      sign(L, g, 4.6, 7.5).position.z = fz - .4; break;
    case 'site':
      bx(w, .2, d, '#c8a46a', 0, .3, 0, g, false);
      for (var c4 = -5; c4 <= 5; c4 += 2.5) mesh(new THREE.ConeGeometry(.4, 1, 8), '#f08a2c', c4, .5, fz - .6, g);
      var cr = new THREE.Group(); cr.position.set(-3, 0, -3); g.add(cr); bx(1, 18, 1, '#f6c623', 0, 9, 0, cr); bx(16, .8, .8, '#f6c623', 4, 18, 0, cr); bx(.1, 8, .1, '#333', 10, 14, 0, cr); bx(1.6, 1, 1.6, '#8a8a8a', 10, 9.6, 0, cr);
      bx(4, 1.6, 3, '#9a7a4a', 3, .8, -2, g); bx(2.4, 2.4, 2.4, '#d0a040', 3, 1.2, 1.8, g);
      sign(L, g, 2.6, 9).position.z = fz + .1; break;
    case 'taxi':
      bx(w, .1, d, '#a9aaa6', 0, .3, 0, g, false); car(g, -3, -1, 0, '#f3c623', 'taxi'); car(g, 1.5, -1, 0, '#f3c623', 'taxi');
      cyl(.12, .12, 4, '#555', 4.5, 2, fz - 1, g, 6); var ts = sign(L, g, 4.2, 5); ts.position.set(4.5, 4.2, fz - .9); break;
  }
}

function buildWorld() {
  var w = WD = { spin: [], boxes: [], workers: [], hl: [] };
  var R = rng(11);
  var sc = w.scene = new THREE.Scene(); sc.background = new THREE.Color('#bfe3f7'); sc.fog = new THREE.Fog('#cfe8f6', 180, 620);
  var ren = w.ren = new THREE.WebGLRenderer({ antialias: true, logarithmicDepthBuffer: true }); ren.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.6));
  ren.shadowMap.enabled = true; ren.shadowMap.type = THREE.PCFSoftShadowMap;
  w.cam = new THREE.PerspectiveCamera(58, 1, 1, 900);
  sc.add(new THREE.HemisphereLight('#ffffff', '#8ab07a', 1.6));
  var sun = new THREE.DirectionalLight('#fff6e0', 2.0); sun.position.set(-120, 200, -60); sun.target.position.set(140, 0, 80);
  sun.castShadow = true; sun.shadow.mapSize.set(2048, 2048); var sc2 = sun.shadow.camera; sc2.left = -220; sc2.right = 220; sc2.top = 200; sc2.bottom = -200; sc2.near = 10; sc2.far = 600; sun.shadow.bias = -0.0008;
  sc.add(sun); sc.add(sun.target);
  var city = w.city = new THREE.Group(); sc.add(city);
  var PAVE = new THREE.MeshLambertMaterial({ map: noiseTex('#e2ddd2', 18, 3.2, true) }); PAVE.map.repeat.set(14, 10);
  // Boden, Fluss, Gleise, Piste
  var grM = new THREE.MeshLambertMaterial({ map: noiseTex('#9cd27a', 26) }); grM.map.repeat.set(160, 130);
  var gr = mesh(new THREE.PlaneGeometry(1000, 800), grM, 140, 0, 80, city); gr.rotation.x = -Math.PI / 2; gr.castShadow = false;
  var rv = mesh(new THREE.PlaneGeometry(RIV[1] - RIV[0], 800), '#5fb3e6', (RIV[0] + RIV[1]) / 2, .08, 80, city); rv.rotation.x = -Math.PI / 2; rv.castShadow = false; w.river = rv;
  [RIV[0] - 1, RIV[1] + 1].forEach(function (x) { var bk = mesh(new THREE.PlaneGeometry(2.4, 800), '#d9c79a', x + (x < RIV[0] ? -.7 : .7), .03, 80, city); bk.rotation.x = -Math.PI / 2; bk.castShadow = false; });
  bx(500, .3, 1.2, '#8a7a6a', 120, .15, 203, city, false); bx(500, .3, 1.2, '#8a7a6a', 120, .15, 207, city, false);
  for (var s = -120; s < 360; s += 3) bx(.6, .2, 6, '#6a4a2a', s, .1, 205, city, false);
  bx(14, .1, 200, '#5a5a5a', 345, .06, 80, city, false); for (var rz = -10; rz < 180; rz += 12) bx(.6, .12, 5, '#ffffff', 345, .1, rz, city, false);
  // Häuserblöcke als Trottoir
  for (var i = 0; i < GX.length - 1; i++) for (var j = 0; j < GZ.length - 1; j++) {
    if (i === 3) continue;
    var bw2 = GX[i + 1] - GX[i] - 8, bd2 = GZ[j + 1] - GZ[j] - 8, cx2 = (GX[i] + GX[i + 1]) / 2, cz2 = (GZ[j] + GZ[j + 1]) / 2;
    bx(bw2, .22, bd2, '#b9b4aa', cx2, .11, cz2, city, false);
    bx(bw2 - .7, .04, bd2 - .7, PAVE, cx2, .22, cz2, city, false);
  }
  // Strassen
  var roadM = new THREE.MeshLambertMaterial({ color: '#ffffff', map: noiseTex('#5b5f64', 14) }), dashM = M('#ffffff');
  roadM.map.repeat.set(6, 6);
  var INS = { dash: [], zebra: [], pole: [], lamp: [], trunk: [], cone: [], crown: [], balc: [], rail: [] }; w.INS = INS;
  SEGS.forEach(function (s) {
    var A = { x: GX[s.i], z: GZ[s.j] }, B = s.d === 'H' ? { x: GX[s.i + 1], z: GZ[s.j] } : { x: GX[s.i], z: GZ[s.j + 1] };
    var len = Math.hypot(B.x - A.x, B.z - A.z), cx = (A.x + B.x) / 2, cz = (A.z + B.z) / 2;
    if (s.bridge) {
      var bw = RIV[1] - RIV[0] + 10;
      var deck = bx(bw, .7, 10, '#b9b2a6', (RIV[0] + RIV[1]) / 2, .35, cz, city);
      [-5, 5].forEach(function (o) { bx(bw, 1.1, .4, '#8a7a6a', (RIV[0] + RIV[1]) / 2, 1.25, cz + o, city); for (var p = RIV[0] - 4; p <= RIV[1] + 4; p += 3) bx(.4, 1.1, .4, '#8a7a6a', p, .9, cz + o, city); });
      var r1 = bx(len - bw, .1, 8, roadM, 0, .06, cz, city, false); r1.receiveShadow = true;
      r1.geometry = new THREE.BoxGeometry(RIV[0] - 5 - A.x, .1, 8); r1.position.x = (A.x + RIV[0] - 5) / 2;
      var r2 = bx(B.x - RIV[1] - 5, .1, 8, roadM, (B.x + RIV[1] + 5) / 2, .06, cz, city, false); r2.receiveShadow = true;
      return;
    }
    var r = s.d === 'H' ? bx(len, .1, 8, roadM, cx, .06, cz, city, false) : bx(8, .1, len, roadM, cx, .06, cz, city, false); r.receiveShadow = true;
    for (var t = 8; t < len - 6; t += 5) {
      var px = s.d === 'H' ? A.x + t : A.x, pz = s.d === 'H' ? A.z : A.z + t;
      if (Math.hypot(px - RBX, pz - RBZ) < RB.r + 5) continue;
      INS.dash.push(s.d === 'H' ? [px, .13, pz, 2.2, 1, .3] : [px, .13, pz, .3, 1, 2.2]);
    }
    // Laternen beidseits
    for (var lt = 12; lt < len - 8; lt += 18) [-5, 5].forEach(function (o) {
      var lx = s.d === 'H' ? A.x + lt : A.x + o, lz = s.d === 'H' ? A.z + o : A.z + lt;
      if (Math.hypot(lx - RBX, lz - RBZ) < 16) return;
      if (s.d === 'V' && (lx > RIV[0] - 4 && lx < RIV[1] + 4)) return;
      INS.pole.push([lx, 2.9, lz, 1, 1, 1]); INS.lamp.push([lx - (s.d === 'V' ? o * .12 : 0), 5.6, lz - (s.d === 'H' ? o * .12 : 0), 1, 1, 1]);
    });
    // Zebrastreifen an den Kreuzungen
    [[A, 1], [B, -1]].forEach(function (q) {
      var nd = q[0], dir = q[1]; if (isRB(GX.indexOf(nd.x), GZ.indexOf(nd.z))) return;
      for (var k = -3; k <= 3; k += 1.2) INS.zebra.push(s.d === 'H' ? [nd.x + dir * 6.3, .13, nd.z + k, 2, 1, .6] : [nd.x + k, .13, nd.z + dir * 6.3, .6, 1, 2]);
    });
  });
  for (i = 0; i < GX.length; i++) for (j = 0; j < GZ.length; j++) if (!isRB(i, j)) bx(8, .1, 8, roadM, GX[i], .09, GZ[j], city, false);
  // Kreisel
  var ring = mesh(new THREE.RingGeometry(RB.r - 4, RB.r + 4, 40), roadM, RBX, .13, RBZ, city); ring.rotation.x = -Math.PI / 2; ring.castShadow = false;
  var isl = cyl(RB.r - 4, RB.r - 4, .5, '#8fd46a', RBX, .3, RBZ, city, 30); isl.castShadow = false;
  tree(city, RBX, RBZ, 1.2, '#3f8a3f'); [0, 1, 2, 3, 4, 5].forEach(function (k) { mesh(new THREE.SphereGeometry(.4, 8, 6), ['#e0368a', '#f6c623', '#ffffff'][k % 3], RBX + Math.cos(k) * 2.6, .7, RBZ + Math.sin(k) * 2.6, city); });
  // Häuser und Orte
  LOTS.forEach(function (L) {
    var g = new THREE.Group(); g.position.set(L.x, 0, L.z); g.rotation.y = Math.atan2(L.fx, L.fz); city.add(g); L.g = g;
    if (L.place) placeBuild(L, g);
    else {
      var hh = L.h, ww = L.w - 1, dd = L.d - 1, tall = hh >= 14;
      house(ww, hh, dd, L.wall, tall ? 'office' : 'win', g);
      bx(ww + .3, 1.1, dd + .3, shade(L.wall, -.32), 0, .55, 0, g);                    // Sockel
      if (L.roof === 'dach') { roof(ww, dd, 3, ['#b5402f', '#8a4a2a', '#5a6a7a', '#a0522d'][Math.floor(R() * 4)], g, hh); bx(.9, 2.4, .9, '#8a5a4a', ww * .25, hh + 2, -dd * .15, g); }
      else {
        bx(ww + .4, .7, dd + .4, shade(L.wall, -.22), 0, hh + .35, 0, g);           // Dachrand
        bx(2.4, 1.6, 2.4, '#c8c8c8', (R() - .5) * 4, hh + 1.5, (R() - .5) * 4, g);
        if (tall && R() < .5) { cyl(1.1, 1.1, 2.4, '#9a8a7a', -ww * .25, hh + 1.9, dd * .2, g, 10); cyl(.08, .08, 4, '#555', ww * .3, hh + 2.7, -dd * .2, g, 4); }
      }
      if (tall && L.wall.charCodeAt(2) % 2 === 0) { g.updateMatrixWorld(true); for (var fy = 4.6; fy < hh - 1.5; fy += 3.6) [-1, 1].forEach(function (sx) { var bxp = sx * ww * .24;
        INS.balc.push(instM(g, bxp, fy, dd / 2 + .6, ww * .36, .25, 1.2)); INS.rail.push(instM(g, bxp, fy + .55, dd / 2 + 1.15, ww * .36, .9, .08)); }); }
      bx(1.8, 2.8, .3, '#6b4a2f', 0, 1.4, L.d / 2 - .4, g);
      bx(2.6, .25, 1.4, '#c9c3b8', 0, 3.1, L.d / 2 + .2, g);
    }
    var hgt = L.place ? 14 : L.h + 1, ex = L.place ? 3 : .5, bx0 = L.x - (L.fx ? L.d : L.w) / 2, bx1 = L.x + (L.fx ? L.d : L.w) / 2, bz0 = L.z - (L.fz ? L.d : L.w) / 2, bz1 = L.z + (L.fz ? L.d : L.w) / 2;
    if (L.fx > 0) bx1 += ex; if (L.fx < 0) bx0 -= ex; if (L.fz > 0) bz1 += ex; if (L.fz < 0) bz0 -= ex;
    w.boxes.push({ x0: bx0, x1: bx1, z0: bz0, z1: bz1, h: hgt });
  });
  // Bäume an den Nord–Süd-Strassen und am Fluss
  for (i = 0; i < GX.length; i++) for (j = 0; j < GZ.length - 1; j++) {
    if (i === 0 || i === GX.length - 1) continue;
    for (var tz = GZ[j] + 9; tz < GZ[j + 1] - 6; tz += 9) [-5.6, 5.6].forEach(function (o) {
      var x = GX[i] + o; if (x > RIV[0] - 3 && x < RIV[1] + 3) return; if (Math.hypot(x - RBX, tz - RBZ) < 14) return;
      if (i === 3 && o > 0) return; if (i === 4 && o < 0) return;
      tree(city, x, tz, .7 + R() * .2, R() < .6 ? 'laub' : 'nadel');
    });
  }
  for (var q = -40; q < 210; q += 10) { tree(city, RIV[0] - 7, q + 3, .9); tree(city, RIV[1] + 7, q, .9); }
  for (q = 0; q < 50; q++) { var ox = -90 + R() * 500, oz = -90 + R() * 360; if ((ox > -30 && ox < 310 && oz > -40 && oz < 200)) continue; tree(city, ox, oz, .8 + R() * .8); }
  // Instanzen bauen
  var GREENS = ['#4f9a4a', '#5fae52', '#3f8a3f', '#6cb85a', '#4a8f5a'];
  buildInst(new THREE.BoxGeometry(1, .02, 1), dashM, INS.dash, false); buildInst(new THREE.BoxGeometry(1, .02, 1), dashM, INS.zebra, false);
  buildInst(new THREE.CylinderGeometry(.11, .15, 5.8, 6), M('#4a4f57'), INS.pole);
  buildInst(new THREE.CylinderGeometry(.18, .42, .45, 8), M('#3a3f47'), INS.lamp.map(function (q) { return [q[0], q[1] + .2, q[2], 1, 1, 1]; }));
  buildInst(new THREE.SphereGeometry(.3, 8, 6), new THREE.MeshBasicMaterial({ color: '#fff1b8' }), INS.lamp.map(function (q) { return [q[0], q[1] - .05, q[2], 1, .6, 1]; }), false);
  buildInst(new THREE.CylinderGeometry(.25, .35, 2, 6), M('#8a5a3a'), INS.trunk);
  buildInst(new THREE.ConeGeometry(1.6, 3.6, 7), new THREE.MeshLambertMaterial({ color: '#ffffff' }), INS.cone, true, GREENS);
  buildInst(new THREE.IcosahedronGeometry(1, 1), new THREE.MeshLambertMaterial({ color: '#ffffff', flatShading: true }), INS.crown, true, GREENS);
  buildInst(new THREE.BoxGeometry(1, 1, 1), M('#d8d4cc'), INS.balc); buildInst(new THREE.BoxGeometry(1, 1, 1), new THREE.MeshLambertMaterial({ color: '#9fc4dc', transparent: true, opacity: .7 }), INS.rail, false);
  // Wolken
  w.clouds = [];
  for (q = 0; q < 9; q++) { var cl = new THREE.Group(); var ca = R() * Math.PI * 2, cr = 330 + R() * 90; cl.position.set(140 + Math.cos(ca) * cr, 55 + R() * 30, 80 + Math.sin(ca) * cr); cl.scale.setScalar(1.6); for (var cb = 0; cb < 5; cb++) { var sp = mesh(new THREE.SphereGeometry(5 + R() * 5, 10, 8), '#ffffff', cb * 6 - 12, R() * 3, R() * 6 - 3, cl, false); } sc.add(cl); w.clouds.push(cl); }
  // Autos, die um die Häuserblöcke fahren (Rechtsverkehr, Block auf der rechten Seite)
  w.cars = [];
  [[0, 0], [2, 0], [4, 0], [0, 2], [4, 2], [0, 3], [1, 3], [4, 3], [3, 1], [3, 1]].forEach(function (b, k) {
    var loop = b[0] === 3 ? [[3, 1], [4, 1], [4, 3], [3, 3]] : [[b[0], b[1]], [b[0] + 1, b[1]], [b[0] + 1, b[1] + 1], [b[0], b[1] + 1]];
    var pts2 = loop.map(function (q2) { return { x: GX[q2[0]], z: GZ[q2[1]] }; }), per = 0, legs = [];
    pts2.forEach(function (a, i2) { var c2 = pts2[(i2 + 1) % pts2.length], L2 = Math.hypot(c2.x - a.x, c2.z - a.z); legs.push({ a: a, b: c2, L: L2, s: per }); per += L2; });
    var cols = ['#d23a3a', '#2f6fd0', '#f4f4f4', '#3a3a3a', '#f3c623', '#3a9a5a', '#e8833a', '#8a5ad0', '#9aa8b8', '#c0392b'];
    var cg = car(city, 0, 0, 0, cols[k], k === 4 ? 'taxi' : k === 7 ? 'van' : 'car');
    w.cars.push({ g: cg, legs: legs, per: per, s: (k * 37) % per, v: 7 + (k % 3) * 1.5 });
  });
  // Ortsnamen hoch über den Gebäuden (Stufe Places/Jobs, freies Spazieren und Karte von oben)
  w.plabels = [];
  var TOP = { hospital: 26, space: 32, church: 29, police: 14, school: 15, airport: 24, site: 21, cinema: 12, bank: 12, museum: 13, court: 13, library: 12 };
  LOTS.forEach(function (L) { if (!L.place) return; var P = PLACES[L.place], sp2 = placeSprite(P.emo + ' ' + P.en); sp2.position.set(L.x, (TOP[L.place] || 10) + 4, L.z); city.add(sp2); w.plabels.push(sp2); });
  // Leute vor ihren Arbeitsorten
  var byPlace = {}; JOBS.forEach(function (J) { (byPlace[J[2]] = byPlace[J[2]] || []).push(J); });
  LOTS.forEach(function (L) {
    if (!L.place || !byPlace[L.place]) return;
    byPlace[L.place].forEach(function (J, k) {
      var p = person(J[4]); var off = byPlace[L.place].length > 1 ? (k ? 1 : -1) * 3.4 : 3.2;
      var lx = off, lz = L.d / 2 + 1.6;
      if (L.place === 'park') { lx = k ? 6 : -4; lz = L.d / 2 - 3; }
      if (L.place === 'space') lx = -6;
      if (L.place === 'farm') { lx = 4; lz = L.d / 2 - 3; }
      if (L.place === 'school') lz = L.d / 2 - 2;
      if (L.place === 'church') lz = L.d / 2 - .5;
      p.position.set(lx, .24, lz); L.g.add(p);
      if (J[0] === 'painter') { var ea = new THREE.Group(); ea.position.set(lx + 1.4, 0, lz - .6); L.g.add(ea); bx(.15, 2.6, .15, '#7a5a3a', 0, 1.3, 0, ea); bx(1.6, 1.3, .1, '#ffffff', 0, 2.1, .1, ea); }
      if (J[0] === 'musician') bx(.3, .9, .2, '#8a4a1a', .5, 2.1, .35, p);
      var lb = labelSprite(J[0]); lb.position.set(lx, 4.3, lz); L.g.add(lb);
      w.workers.push({ job: J[0], place: L.place, p: p, lb: lb, ph: Math.random() * 6 });
    });
  });
  // Die Eule
  w.owl = owlMesh(); sc.add(w.owl);
  // Markierungen (Start, Ziel)
  w.marks = new THREE.Group(); sc.add(w.marks);
  w.paths = new THREE.Group(); sc.add(w.paths);
  w.clock = new THREE.Clock();
  w.el = document.createElement('div'); w.el.className = 'ow';
  w.el.appendChild(ren.domElement);
  w.ro = new ResizeObserver(function () { resize(); }); w.ro.observe(w.el);
  buildMini();
}
function resize() {
  if (!WD) return; var r = WD.el.getBoundingClientRect(); if (!r.width || !r.height) return;
  WD.ren.setSize(r.width, r.height, false); WD.ren.domElement.style.width = '100%'; WD.ren.domElement.style.height = '100%';
  WD.cam.aspect = r.width / r.height; WD.cam.updateProjectionMatrix();
}

// ---------------------------------------------------------------------- Kleiner Stadtplan
var MINI = { x0: -40, x1: 320, z0: -40, z1: 200 };
function buildMini() {
  var cv = document.createElement('canvas'); cv.width = 360; cv.height = 240; cv.className = 'mini'; WD.mini = cv;
  var bg = document.createElement('canvas'); bg.width = 360; bg.height = 240; WD.miniBg = bg;
  var g = bg.getContext('2d'), k = 1;
  function X(x) { return (x - MINI.x0) * k; } function Zp(z) { return (z - MINI.z0) * k; }
  g.fillStyle = '#cfe9b8'; g.fillRect(0, 0, 360, 240);
  g.fillStyle = '#8cc8ee'; g.fillRect(X(RIV[0]), 0, RIV[1] - RIV[0], 240);
  g.fillStyle = '#e8e2d2'; LOTS.forEach(function (L) { var w = L.fx ? L.d : L.w, d = L.fz ? L.d : L.w; g.fillStyle = L.place ? '#f0c888' : '#ddd6c6'; g.fillRect(X(L.x - w / 2), Zp(L.z - d / 2), w, d); });
  g.strokeStyle = '#6a6e74'; g.lineWidth = 6; g.lineCap = 'square';
  SEGS.forEach(function (s) { var a = NODES[s.a], b = NODES[s.b]; g.beginPath(); g.moveTo(X(s.d === 'H' ? GX[s.i] : a.x), Zp(s.d === 'H' ? a.z : GZ[s.j])); g.lineTo(X(s.d === 'H' ? GX[s.i + 1] : b.x), Zp(s.d === 'H' ? b.z : GZ[s.j + 1])); g.stroke(); });
  g.beginPath(); g.arc(X(RBX), Zp(RBZ), RB.r, 0, 7); g.stroke(); g.fillStyle = '#8fd46a'; g.beginPath(); g.arc(X(RBX), Zp(RBZ), RB.r - 3, 0, 7); g.fill();
  g.fillStyle = '#1f2421'; g.font = 'bold 13px Arial'; g.fillText('N ⬆', 8, 18);
  WD.miniX = X; WD.miniZ = Zp;
}
function drawMini() {
  var cv = WD.mini, g = cv.getContext('2d'); g.drawImage(WD.miniBg, 0, 0);
  function line(list, col, wd) {
    if (!list || list.length < 2) return; g.strokeStyle = col; g.lineWidth = wd; g.lineJoin = 'round'; g.beginPath();
    list.forEach(function (id, k) { var n = NODES[id]; if (k) { var e = EMAP[list[k - 1] + '>' + id]; if (e && e.k === 'A') { for (var t = .25; t < 1; t += .25) { var p = epos(e, t); g.lineTo(WD.miniX(p.x), WD.miniZ(p.z)); } } g.lineTo(WD.miniX(n.x), WD.miniZ(n.z)); } else g.moveTo(WD.miniX(n.x), WD.miniZ(n.z)); });
    g.stroke();
  }
  if (WD.miniPaths) { line(WD.miniPaths.sol, '#e0362c', 5); line(WD.miniPaths.kid, '#2f6fd0', 3); }
  if (WD.miniStar) { g.fillStyle = '#d6ad45'; g.font = '20px Arial'; g.textAlign = 'center'; g.fillText('⭐', WD.miniX(WD.miniStar.x), WD.miniZ(WD.miniStar.z) + 7); g.textAlign = 'left'; }
  var o = WD.owl.position, h = OW.hd, x = WD.miniX(o.x), z = WD.miniZ(o.z);
  g.save(); g.translate(x, z); g.rotate(h); g.fillStyle = '#e0362c'; g.strokeStyle = '#fff'; g.lineWidth = 2;
  g.beginPath(); g.moveTo(9, 0); g.lineTo(-6, -6); g.lineTo(-3, 0); g.lineTo(-6, 6); g.closePath(); g.fill(); g.stroke(); g.restore();
}

// ---------------------------------------------------------------------- Bewegung der Eule
var SPEED = 15, OW = { node: null, hd: 0, mv: null, tr: null, trace: [], held: false, q: null, lock: true, bump: 0, onArrive: null, onBump: null };
function owlReset(id, hd) {
  OW.node = id; OW.hd = hd; OW.mv = OW.tr = OW.q = null; OW.trace = [id]; OW.lock = false; OW.bump = 0;
  var n = NODES[id]; WD.owl.position.set(n.x, 0, n.z); WD.owl.rotation.y = Math.PI / 2 - hd; CAM.snap = true;
}
function owlCmd(c) {
  if (OW.lock) return;
  if (OW.mv || OW.tr) { OW.q = c; return; }
  if (c === 'L' || c === 'R' || c === 'B') { OW.tr = { a: OW.hd, b: OW.hd + (c === 'R' ? Math.PI / 2 : c === 'L' ? -Math.PI / 2 : Math.PI), t: 0 }; tone(c === 'B' ? 380 : 470, .05, 'sine', .08); return; }
  if (c === 'U') {
    var e = straightEdge(OW.node, OW.hd);
    if (!e && ringEntry(OW.node, OW.hd)) e = ringArc(OW.node);
    if (!e) { OW.bump = 1; if (OW.onBump) OW.onBump(); tone(180, .12, 'triangle', .1); return; }
    OW.mv = { e: e, t: 0 };
  }
}
function owlStep(dt) {
  var o = WD.owl;
  if (OW.tr) {
    OW.tr.t = Math.min(1, OW.tr.t + dt * 4.5); var k = OW.tr.t, ease = k * k * (3 - 2 * k);
    OW.hd = OW.tr.a + (OW.tr.b - OW.tr.a) * ease;
    if (k >= 1) { OW.hd = Math.atan2(Math.sin(OW.tr.b), Math.cos(OW.tr.b)); OW.tr = null; if (OW.onArrive) OW.onArrive(OW.node); next(); }
  } else if (OW.mv) {
    var e = OW.mv.e; OW.mv.t = Math.min(1, OW.mv.t + dt * SPEED / e.len);
    var p = epos(e, OW.mv.t); o.position.x = p.x; o.position.z = p.z; OW.hd = p.h;
    o.position.y = e.bridge ? .7 : e.k === 'A' ? .1 : 0;
    o.userData.body.rotation.z = Math.sin(performance.now() / 90) * .12; o.userData.body.position.y = Math.abs(Math.sin(performance.now() / 90)) * .15;
    if (OW.mv.t >= 1) {
      OW.node = e.b; OW.hd = e.h1; OW.mv = null; OW.trace.push(OW.node); o.userData.body.rotation.z = 0; o.userData.body.position.y = 0;
      var n = NODES[OW.node];
      if (OW.onArrive) OW.onArrive(OW.node);
      if (OW.q) next();
      else if (OW.held && n.t === 'S' && straightEdge(OW.node, OW.hd)) { OW.mv = { e: straightEdge(OW.node, OW.hd), t: 0 }; }
    }
  } else if (OW.bump) {
    OW.bump = Math.max(0, OW.bump - dt * 3); o.userData.body.position.y = Math.sin(OW.bump * Math.PI) * .5;
  }
  o.rotation.y = Math.PI / 2 - OW.hd;
  function next() { var c = OW.q; OW.q = null; if (c) owlCmd(c); else if (OW.held) owlCmd('U'); }
}
var CAM = { mode: 'follow', snap: true, pos: null, look: null, view: null };
function camStep(dt) {
  var c = WD.cam, o = WD.owl.position, fx = Math.cos(OW.hd), fz = Math.sin(OW.hd), tp, tl;
  if (CAM.mode === 'view' && CAM.view) { tp = CAM.view.pos; tl = CAM.view.look; }
  else if (CAM.mode === 'top') { tp = new THREE.Vector3(o.x, 95, o.z + 38); tl = new THREE.Vector3(o.x, 0, o.z); }
  else {
    var dist = 13, H = 7.5;
    for (; dist > 3; dist -= .5) { var px = o.x - fx * dist, pz = o.z - fz * dist; if (!WD.boxes.some(function (b) { return px > b.x0 - .8 && px < b.x1 + .8 && pz > b.z0 - .8 && pz < b.z1 + .8 && H < b.h + 6; })) break; }
    var ahead = 6; if (dist < 8) { H = 7.5 + (8 - dist) * 2.4; ahead = 2.5; }
    tp = new THREE.Vector3(o.x - fx * dist, H, o.z - fz * dist); tl = new THREE.Vector3(o.x + fx * ahead, 1.2, o.z + fz * ahead);
  }
  if (CAM.snap || !CAM.pos) { CAM.pos = tp.clone(); CAM.look = tl.clone(); CAM.snap = false; }
  var k = 1 - Math.exp(-dt * (CAM.mode === 'follow' ? 5 : 2.2));
  CAM.pos.lerp(tp, k); CAM.look.lerp(tl, k); c.position.copy(CAM.pos); c.lookAt(CAM.look);
}
var LOOP = { on: false, last: 0 };
function loop() {
  if (!WD || !document.body.contains(WD.el)) { LOOP.on = false; return; }
  requestAnimationFrame(loop);
  var dt = Math.min(.05, WD.clock.getDelta());
  owlStep(dt); camStep(dt);
  var t = performance.now() / 1000;
  WD.spin.forEach(function (s) { s.rotation.y = t * 1.5; });
  WD.cars.forEach(function (c) {
    c.s = (c.s + dt * c.v) % c.per; var lg = c.legs.filter(function (l) { return c.s >= l.s && c.s < l.s + l.L; })[0] || c.legs[0], f = (c.s - lg.s) / lg.L;
    var dx = (lg.b.x - lg.a.x) / lg.L, dz = (lg.b.z - lg.a.z) / lg.L;
    c.g.position.set(lg.a.x + (lg.b.x - lg.a.x) * f - dz * 2, (lg.L > 58 && f > .2 && f < .8) ? .7 : 0, lg.a.z + (lg.b.z - lg.a.z) * f + dx * 2);
    var want = Math.atan2(dx, dz), cur = c.g.rotation.y; c.g.rotation.y = cur + angd(want, cur) * Math.min(1, dt * 8);
  });
  WD.clouds.forEach(function (c, k) { var a = Math.atan2(c.position.z - 80, c.position.x - 140) + dt * .004, r = Math.hypot(c.position.z - 80, c.position.x - 140); c.position.x = 140 + Math.cos(a) * r; c.position.z = 80 + Math.sin(a) * r; });
  var showP = LABELS === 'immer' || CAM.mode !== 'follow';
  var op = WD.owl.position, far = CAM.mode === 'follow' ? 75 : 1e9;
  WD.plabels.forEach(function (s2) { s2.visible = showP && Math.hypot(s2.position.x - op.x, s2.position.z - op.z) < far; });
  WD.workers.forEach(function (w) { w.p.rotation.y = Math.sin(t * .8 + w.ph) * .25; });
  WD.hl.forEach(function (m) { m.position.y = m.userData.y0 + Math.sin(t * 3) * .5; if (m.userData.spin) m.rotation.y = t * 2; });
  if (WD.grow) { var gr = WD.grow; gr.t = Math.min(1, gr.t + dt / gr.dur); gr.list.forEach(function (m) { m.geometry.setDrawRange(0, Math.floor(m.geometry.index.count * gr.t / 6) * 6); }); if (gr.t >= 1) WD.grow = null; }
  if (WD.mini.isConnected && (++LOOP.last % 3 === 0)) drawMini();
  WD.ren.render(WD.scene, WD.cam);
}
function startLoop() { if (!LOOP.on) { LOOP.on = true; WD.clock.getDelta(); requestAnimationFrame(loop); } }

// Tastatur (Pfeile, WASD, Leertaste = Ziel)
var KEYH = null;
window.addEventListener('keydown', function (e) {
  if (!KEYH) return; var k = e.key, c = null;
  if (k === 'ArrowUp' || k === 'w' || k === 'W') c = 'U'; else if (k === 'ArrowLeft' || k === 'a' || k === 'A') c = 'L';
  else if (k === 'ArrowRight' || k === 'd' || k === 'D') c = 'R'; else if (k === 'ArrowDown' || k === 's' || k === 'S') c = 'B';
  else if (k === ' ' || k === 'Enter') c = 'M';
  if (!c) return; e.preventDefault();
  if (c === 'U') { if (e.repeat) return; OW.held = true; }
  if (e.repeat) return;
  KEYH(c);
});
window.addEventListener('keyup', function (e) { if (e.key === 'ArrowUp' || e.key === 'w' || e.key === 'W') OW.held = false; });
window.addEventListener('blur', function () { OW.held = false; });

// ---------------------------------------------------------------------- Wege und Markierungen zeichnen
function clearMarks() {
  if (!WD) return;
  [WD.marks, WD.paths].forEach(function (gp) { while (gp.children.length) { var m = gp.children.pop(); m.traverse(function (x) { if (x.geometry) x.geometry.dispose(); }); } });
  WD.hl = []; WD.grow = null; WD.miniPaths = null; WD.miniStar = null;
  WD.workers.forEach(function (w) { w.lb.visible = MODE_LABELS; });
}
var MODE_LABELS = true, LABELS = 'immer';
function pts(list, y) {
  var a = [];
  list.forEach(function (id, k) {
    var n = NODES[id];
    if (k) { var e = EMAP[list[k - 1] + '>' + id]; if (e && e.k === 'A') for (var t = .2; t < 1; t += .2) { var p = epos(e, t); a.push(new THREE.Vector3(p.x, y, p.z)); } }
    var yy = y + (n.t === 'R' ? .1 : 0); a.push(new THREE.Vector3(n.x, yy, n.z));
  });
  var out = []; a.forEach(function (p) { if (!out.length || out[out.length - 1].distanceTo(p) > .3) out.push(p); }); return out;
}
function tube(list, col, y, r) {
  var p = pts(list, y); if (p.length < 2) return null;
  var cp = new THREE.CurvePath(), L = 0;
  for (var k = 0; k < p.length - 1; k++) { cp.add(new THREE.LineCurve3(p[k], p[k + 1])); L += p[k].distanceTo(p[k + 1]); }
  var m = new THREE.Mesh(new THREE.TubeGeometry(cp, Math.max(8, Math.round(L / .8)), r, 7, false), new THREE.MeshBasicMaterial({ color: col, depthTest: false, transparent: true, opacity: .92 }));
  m.renderOrder = col === '#2f6fd0' ? 9 : 8; WD.paths.add(m); return m;
}
function floatMark(x, z, y, emo, big) {
  var s = emoSprite(emo, big ? 7 : 4.5); s.position.set(x, y, z); s.userData.y0 = y;
  WD.marks.add(s); WD.hl.push(s); return s;
}
function ringMark(x, z, col) {
  var m = new THREE.Mesh(new THREE.TorusGeometry(3, .35, 8, 30), new THREE.MeshBasicMaterial({ color: col })); m.rotation.x = Math.PI / 2; m.position.set(x, .6, z); m.userData.y0 = .9; WD.marks.add(m); WD.hl.push(m); return m;
}
function viewFit(lists) {
  var x0 = 1e9, x1 = -1e9, z0 = 1e9, z1 = -1e9;
  lists.forEach(function (l) { (l || []).forEach(function (id) { var n = NODES[id]; x0 = Math.min(x0, n.x); x1 = Math.max(x1, n.x); z0 = Math.min(z0, n.z); z1 = Math.max(z1, n.z); }); });
  var cx = (x0 + x1) / 2, cz = (z0 + z1) / 2, asp = WD.cam.aspect || 1.5, ext = Math.max((x1 - x0 + 50) / asp, z1 - z0 + 60);
  var H = Math.max(60, ext * .95);
  CAM.view = { pos: new THREE.Vector3(cx - H * .06, H * 1.05, cz + H * .2), look: new THREE.Vector3(cx - H * .06, 0, cz + 2) }; CAM.mode = 'view';
}

// ---------------------------------------------------------------------- Bildschirm im Spiel
var UI = null;
function ui(api, lv) {
  var box = document.createElement('div'); box.className = 'owbox';
  box.innerHTML = '<div class="card" id="owCard"></div>' +
    '<div class="tools"><button class="pill" data-k="top" title="Von oben schauen">🗺 Karte</button><button class="pill" data-k="help" title="Little Helper">💡 Helper</button></div>' +
    '<div class="pad"><span></span><button data-c="U" aria-label="geradeaus">⬆</button><span></span><button data-c="L" aria-label="links drehen">⬅</button><button data-c="B" aria-label="umdrehen">⬇</button><button data-c="R" aria-label="rechts drehen">➡</button></div>' +
    '<button class="mark" data-c="M">📍 Hier ist das Ziel!</button><div class="near" id="owNear"></div><div class="pop" id="owPop" hidden></div><div class="toast" id="owToast"></div>';
  box.insertBefore(WD.el, box.firstChild); box.appendChild(WD.mini); WD.mini.classList.toggle('aus', lv.mini === false);
  api.stage.appendChild(box);
  var U = UI = { box: box, card: box.querySelector('#owCard'), near: box.querySelector('#owNear'), pop: box.querySelector('#owPop'), toast: box.querySelector('#owToast') };
  Array.prototype.forEach.call(box.querySelectorAll('[data-c]'), function (b) {
    var c = b.dataset.c;
    b.addEventListener('pointerdown', function (e) { e.preventDefault(); if (c === 'U') OW.held = true; if (KEYH) KEYH(c); });
    ['pointerup', 'pointerleave', 'pointercancel'].forEach(function (ev) { b.addEventListener(ev, function () { if (c === 'U') OW.held = false; }); });
  });
  box.querySelector('[data-k=top]').onclick = function (e) { if (CAM.mode === 'view') return; CAM.mode = CAM.mode === 'top' ? 'follow' : 'top'; e.currentTarget.classList.toggle('on', CAM.mode === 'top'); };
  box.querySelector('[data-k=help]').onclick = function () { helper(); };
  resize(); startLoop();
  try { window.focus(); } catch (e) {}
  return U;
}
function toast(t, ms) { if (!UI) return; UI.toast.innerHTML = t; UI.toast.classList.add('on'); clearTimeout(UI.tt); UI.tt = setTimeout(function () { if (UI) UI.toast.classList.remove('on'); }, ms || 2200); }
var HELP = [
  ['⬅', 'turn left', 'links abbiegen'], ['➡', 'turn right', 'rechts abbiegen'], ['⬆', 'walk straight on', 'geradeaus gehen'],
  ['✚', 'at the first / second crossing', 'bei der ersten / zweiten Kreuzung'], ['🔚', 'walk to the end of the street', 'bis zum Ende der Strasse gehen'],
  ['🌉', 'cross the bridge', 'über die Brücke gehen'], ['⭕', 'take the first / second / third exit', 'im Kreisel die 1. / 2. / 3. Ausfahrt nehmen'],
  ['🏠', 'walk past the …', 'am … vorbeigehen'], ['👀', 'on your left you can see the …', 'links siehst du …'],
  ['✋', 'stop at the second building on your right', 'beim zweiten Gebäude rechts anhalten']
];
function helper() {
  var o = '<div class="pp"><h3>Little Helper ✦</h3><table>';
  HELP.forEach(function (x) { o += '<tr><td class="ic">' + x[0] + '</td><td><b data-say="' + h(x[1]) + '">' + h(x[1]) + '</b></td><td>' + x[2] + '</td></tr>'; });
  var vs = enVoices();
  if (vs.length) { o += '</table><p class="kl">Stimme: <select id="owVoice">' + vs.map(function (v) { return '<option value="' + h(v.name) + '"' + (VOICE && VOICE.name === v.name ? ' selected' : '') + '>' + h(v.name.replace(/^(Microsoft|Google)\s+/, '')) + ' (' + h(v.lang) + ')</option>'; }).join('') + '</select> <button class="pill" data-x="vt">🔊 Probehören</button></p><table style="display:none">'; }
  o += '</table><p class="kl">Tasten: ⬆ gehen (gedrückt halten = weiterlaufen) · ⬅ ➡ drehen · ⬇ umdrehen · Leertaste = Ziel markieren<br>Am Anfang stehst du mit dem Rücken zum Gebäude.</p><button class="go" data-x="zu">OK</button></div>';
  popup(o, function (b) { if (b.dataset.x === 'vt') { say('Turn left at the second crossing. Then walk straight on.'); return false; } return b.dataset.x === 'zu'; });
  var sel = UI.pop.querySelector('#owVoice');
  if (sel) sel.onchange = function () { var v = enVoices().filter(function (x) { return x.name === sel.value; })[0]; if (v) { VOICE = v; try { localStorage.setItem(VKEY, v.name); } catch (e) {} say('Hello! This is my voice.'); } };
}
function popup(html, onClick) {
  var p = UI.pop; p.innerHTML = html; p.hidden = false; var was = OW.lock; OW.lock = true;
  p.onclick = function (e) {
    var s = e.target.closest('[data-say]'); if (s) { say(s.dataset.say); return; }
    var b = e.target.closest('button'); if (!b) return;
    if (onClick(b) !== false) { p.hidden = true; p.innerHTML = ''; OW.lock = was; }
  };
}
function nearInfo(id, speak) {
  var n = NODES[id]; if (!UI) return;
  if (n.t !== 'S' || !n.lots.length) {
    var tr = OW.trace, rc = 0; for (var q = tr.length - 1; q > 0 && NODES[tr[q - 1]].t === 'R' && NODES[tr[q]].t === 'R'; q--) rc++;
    UI.near.innerHTML = n.t === 'R' ? (rc ? '⭕ ' + ORD[rc - 1] + ' exit ➡' : '⭕ roundabout') : n.t === 'J' ? '✚ crossing' : '';
    UI.near.classList.toggle('on', !!UI.near.innerHTML); return;
  }
  var parts = [], words = [], AR = { L: '⬅', R: '➡', S: '⬆', B: '⬇' };
  n.lots.forEach(function (lt) {
    var d = angd(Math.atan2(lt.z - n.z, lt.x - n.x), OW.hd), w = Math.abs(d) < Math.PI / 4 ? 'S' : Math.abs(d) > 3 * Math.PI / 4 ? 'B' : d > 0 ? 'R' : 'L';
    parts.push(w === 'R' ? h(lotArt(lt)) + ' ' + AR[w] : AR[w] + ' ' + h(lotArt(lt))); if (lt.place) words.push('the ' + PLACES[lt.place].en);
  });
  UI.near.innerHTML = parts.join(' &nbsp;·&nbsp; ');
  UI.near.classList.add('on');
  if (speak && words.length) say(words.join(' and '));
}

// Ziel markieren: Welches Gebäude? (links / rechts)
function askMark(cb) {
  var n = NODES[OW.node];
  if (OW.mv || OW.tr) return;
  if (n.t !== 'S' || !n.lots.length) { toast('Stell dich vor ein Gebäude, nicht auf eine Kreuzung.'); bad(); return; }
  // Steht die Eule mit dem Gesicht zu einem Gebäude? Dann ist es dieses.
  var facing = n.lots.filter(function (L) { return Math.abs(angd(Math.atan2(L.z - n.z, L.x - n.x), OW.hd)) < .8; });
  if (facing.length === 1 || n.lots.length === 1) { cb(facing[0] || n.lots[0]); return; }
  var hd = OW.hd;
  // Richtung entlang der Strasse für links/rechts
  var segE = n.out[0], along = segE.h0; if (Math.abs(angd(along, hd)) > Math.PI / 2) along += Math.PI;
  var o = '<div class="pp"><h3>Welches Gebäude ist dein Ziel?</h3><div class="row">';
  var bySide = { L: [], R: [] }; n.lots.forEach(function (L) { bySide[sideOf(L, n.x, n.z, along)].push(L); });
  ['L', 'R'].forEach(function (sd) { bySide[sd].forEach(function (L) { o += '<button class="go ' + (sd === 'L' ? 'alt' : 'sun') + '" data-l="' + L.id + '">' + (sd === 'L' ? '⬅ links<br>' : 'rechts ➡<br>') + '<small>' + h(lotArt(L)) + '</small></button>'; }); });
  o += '</div><button class="pill" data-x="no" style="margin-top:12px">Doch nicht</button></div>';
  popup(o, function (b) { if (b.dataset.l) { var L = LOTS.filter(function (x) { return x.id === b.dataset.l; })[0]; setTimeout(function () { cb(L); }, 0); } return true; });
}

// ---------------------------------------------------------------------- Das Spiel
var GAME = { run: 0 };
G.play = function (lv, api, li) {
  var run = ++GAME.run;
  api.msg('<span class="em">🦉</span> Die Stadt wird gebaut …');
  loadThree(function (err) {
    if (run !== GAME.run) return;
    if (err) { api.msg('<span class="em">📡</span> Die 3D-Stadt braucht Internet. Bitte Seite neu laden.'); return; }
    try { document.fonts && document.fonts.load('40px "Patrick Hand"'); } catch (e) {}
    var go = function () { if (run !== GAME.run) return; if (!WD) buildWorld(); play(lv, api, li, run); };
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { setTimeout(go, 30); }); else go();
  });
};
function play(lv, api, li, run) {
  clearMarks(); CAM.mode = 'follow'; CAM.view = null;
  MODE_LABELS = lv.typ !== 'job'; WD.workers.forEach(function (w) { w.lb.visible = MODE_LABELS; });
  LABELS = lv.typ === 'weg' ? 'karte' : 'immer';
  var U = ui(api, lv), N = G.n, k = 0, task = null, used = {};
  var alive = function () { return run === GAME.run && document.body.contains(U.box); };
  OW.onBump = function () {
    if (ringEntry(OW.node, OW.hd + Math.PI / 2) || NODES[OW.node].t === 'R') toast('Im Kreisel geht es rechts herum ↺ – drück ⬆.');
    else toast('Hier geht es nicht weiter. Dreh dich mit ⬅ oder ➡.');
  };
  var lastSpoken = null;
  OW.onArrive = function (id) { var sp = lv.typ === 'frei' && !OW.mv && lastSpoken !== id; if (sp) lastSpoken = id; nearInfo(id, sp); };
  KEYH = function (c) { if (!alive()) { KEYH = null; return; } if (c === 'M') { if (lv.typ !== 'frei' && task && !task.done) askMark(check); return; } owlCmd(c); };

  if (lv.typ === 'frei') {
    var L0 = LOTS.filter(function (L) { return L.place === 'school'; })[0];
    owlReset(L0.stop, Math.atan2(L0.fz, L0.fx)); nearInfo(L0.stop);
    U.box.querySelector('.mark').hidden = true;
    U.card.innerHTML = '<div class="hd">🚶 Free walk</div><p class="de">Spaziere frei durch die Stadt. Bleib vor einem Gebäude stehen: Du siehst und hörst seinen englischen Namen.</p>' +
      '<p class="de">Wer arbeitet wo? Schau dir die Leute vor den Gebäuden an.</p>';
    api.msg('');
    return;
  }

  function nextTask() {
    if (!alive()) return;
    clearMarks(); CAM.mode = 'follow'; CAM.view = null; U.box.querySelector('[data-k=top]').classList.remove('on');
    U.box.classList.remove('review');
    if (lv.typ === 'weg') {
      var r = genRoute(lv); if (!r) { api.msg('Kein Weg gefunden 🤔'); return; }
      task = { typ: 'weg', r: r, done: false, heard: 0 };
      owlReset(r.start.stop, r.face);
      task.flag = [r.start.x, r.start.z];
    } else {
      var pool = lv.typ === 'job' ? JOBS.filter(function (J) { return !used[J[0]]; }) : Object.keys(PLACES).filter(function (p) { return !used[p]; });
      var pick1 = pool[Math.floor(Math.random() * pool.length)], place = lv.typ === 'job' ? pick1[2] : pick1;
      used[lv.typ === 'job' ? pick1[0] : pick1] = 1;
      var sl = LOTS.filter(function (L) { return L.place && L.place !== place && isBuilding(L) && NODES[L.stop].t === 'S'; });
      var s0 = sl[Math.floor(Math.random() * sl.length)];
      task = { typ: lv.typ, place: place, job: lv.typ === 'job' ? pick1 : null, start: s0, done: false };
      owlReset(s0.stop, Math.atan2(s0.fz, s0.fx));
    }
    G.task = task; // für Tests
    nearInfo(OW.node);
    showTask();
    var sl0 = task.typ === 'weg' ? task.r.start : task.start;
    setTimeout(function () { if (alive()) toast('🦉 Du stehst vor «' + h(lotArt(sl0)) + '»,<br>mit dem Rücken zum Gebäude.', 3200); }, 600);
    api.msg('<small>Aufgabe ' + (k + 1) + ' von ' + N + '</small>');
  }
  function showTask() {
    var o = '';
    if (task.typ === 'weg') {
      var st = task.r.steps, hide = lv.listen && !task.show;
      o = '<div class="hd">🧭 Route ' + (k + 1) + ' <small>of ' + N + '</small></div>';
      if (hide) o += '<p class="de">🎧 Hör gut zu und lauf den Weg. Du kannst so oft hören, wie du willst.</p>';
      else { o += '<ol class="steps">'; st.forEach(function (s, i) { o += '<li data-i="' + i + '">' + h(s.text) + '</li>'; }); o += '<li class="q">Now you are at the …?</li></ol>'; }
      o += '<div class="row"><button class="go sun" data-x="say">🔊 ' + (hide ? 'Anhören' : 'Vorlesen') + '</button>' + (lv.listen ? '<button class="go alt" data-x="show">' + (task.show ? 'Text verstecken' : '📄 Text zeigen') + '</button>' : '') + '</div>';
      o += '<p class="de">Lauf mit den Pfeiltasten. Am Ziel: <b>📍</b> drücken (oder Leertaste).</p>';
    } else if (task.typ === 'job') {
      var J = task.job;
      o = '<div class="hd">' + J[1] + ' Where does the <b>' + h(J[0]) + '</b> work?</div><p class="de">Finde den Ort, wo «' + h(J[0]) + '» arbeitet, und markiere ihn mit 📍.</p><div class="row"><button class="go sun" data-x="say">🔊 Anhören</button></div>';
    } else {
      var P = PLACES[task.place];
      o = '<div class="hd">' + P.emo + ' Walk to the <b>' + h(P.en) + '</b>.</div><p class="de">Lies die Schilder. Lauf zum Ort und markiere ihn mit 📍.</p><div class="row"><button class="go sun" data-x="say">🔊 Anhören</button><button class="go alt" data-x="tipp">💡 Tipp</button></div>';
    }
    U.card.innerHTML = o;
    U.card.onclick = function (e) {
      var b = e.target.closest('[data-x]'), li2 = e.target.closest('li[data-i]');
      if (li2 && task.typ === 'weg') { say(task.r.steps[+li2.dataset.i].text); return; }
      if (!b) return;
      if (b.dataset.x === 'say') sayTask();
      if (b.dataset.x === 'show') { task.show = !task.show; showTask(); }
      if (b.dataset.x === 'tipp') { var T = LOTS.filter(function (L) { return L.place === task.place; })[0]; WD.miniStar = { x: T.x, z: T.z }; WD.mini.classList.remove('aus'); toast('⭐ Schau auf den kleinen Plan unten rechts.'); }
      if (b.dataset.x === 'next') { if (!alive()) return; var more = api.answer(task.ok, true); k++; if (more) nextTask(); else { U.card.innerHTML = '<div class="hd">🏁 Fertig!</div>'; OW.lock = true; } }
      if (b.dataset.x === 'replay') replay();
    };
    if (task.typ === 'weg' && lv.listen && !task.heard) { task.heard = 1; setTimeout(function () { if (alive()) sayTask(); }, 500); }
  }
  function sayTask() {
    if (task.typ === 'weg') {
      var sent = task.r.steps.map(function (s) { return s.text; }).concat(['Where are you?']);
      if (!(lv.listen ? sayList(sent, .78, 1600) : sayList(sent, .88, 600))) { task.show = true; showTask(); toast('Vorlesen geht auf diesem Gerät nicht – lies den Text.'); }
    }
    else if (task.typ === 'job') say('Where does the ' + task.job[0] + ' work?');
    else say('Walk to the ' + PLACES[task.place].en + '.');
  }

  function check(L) {
    if (!alive() || task.done) return;
    task.done = true; OW.lock = true; OW.held = false;
    var ok, rv = { kid: OW.trace.slice() };
    if (task.typ === 'weg') { ok = L === task.r.target; rv.sol = task.r.nodes; rv.T = task.r.target; }
    else { ok = L.place === task.place; var T = LOTS.filter(function (x) { return x.place === task.place; })[0]; rv.T = T; var to = {}; to[T.stop] = 1; rv.sol = shortest(task.start.stop, to); }
    task.ok = ok; if (ok) good(); else bad();
    review(L, ok, rv);
  }
  function review(L, ok, rv) {
    U.box.classList.add('review');
    WD.workers.forEach(function (w) { w.lb.visible = true; });
    var T = rv.T, P = PLACES[T.place], o = '';
    var redM = tube(rv.sol, '#e0362c', 1, 1.1), blueM = tube(rv.kid, '#2f6fd0', 1.6, .6);
    if (task.flag) floatMark(task.flag[0], task.flag[1], 16, '🚩');
    WD.grow = { t: 0, dur: 2.2, list: [redM, blueM].filter(Boolean) }; WD.grow.list.forEach(function (m) { m.geometry.setDrawRange(0, 0); });
    WD.miniPaths = { sol: rv.sol, kid: rv.kid }; WD.miniStar = { x: T.x, z: T.z };
    floatMark(T.x, T.z, (T.place === 'hospital' ? 26 : T.place === 'space' ? 32 : 16), '⭐', true);
    if (!ok) { ringMark(L.x + L.fx * (L.d / 2 + 2), L.z + L.fz * (L.d / 2 + 2), '#2f6fd0'); }
    viewFit([rv.sol, rv.kid]);
    if (task.typ === 'weg') {
      var ex = explain(task.r, rv.kid, L);
      o = '<div class="hd">' + (ok ? '🎉 Right! You are at the <b>' + h(P.en) + '</b>.' : '🤔 Not quite. The goal was the <b>' + h(P.en) + '</b>.') + '</div>';
      o += '<p class="de">' + h(P.en) + ' = ' + h(P.de) + (ok ? '' : ' · Du warst bei: ' + h(lotArt(L))) + '</p>';
      o += '<ol class="steps rv">'; task.r.steps.forEach(function (s, i) { var c = ex.step == null ? 'ok' : i < ex.step ? 'ok' : i === ex.step ? 'no' : ''; o += '<li data-i="' + i + '" class="' + c + '">' + h(s.text) + (i === ex.step ? '<div class="why">' + ex.why + '</div>' : '') + '</li>'; }); o += '</ol>';
      if (!ok && ex.node) { var n = NODES[ex.node]; floatMark(n.x, n.z, 6, '❗'); ringMark(n.x, n.z, '#f6c623'); }
    } else {
      var J = task.job;
      if (ok) o = '<div class="hd">🎉 Yes! ' + (J ? 'The <b>' + h(J[0]) + '</b> works at the <b>' + h(P.en) + '</b>.' : 'This is the <b>' + h(P.en) + '</b>.') + '</div>';
      else o = '<div class="hd">🤔 This is ' + h(lotArt(L)) + '.</div><p class="de">' + (J ? 'The ' + h(J[0]) + ' (' + h(J[3]) + ') arbeitet hier: ' : 'Gesucht war ') + '<b>the ' + h(P.en) + '</b> ⭐</p>';
      o += '<p class="de">' + h(P.en) + ' = ' + h(P.de) + (J ? ' · ' + h(J[0]) + ' = ' + h(J[3]) : '') + '</p>';
      say(ok ? (J ? 'Yes! The ' + J[0] + ' works at the ' + P.en + '.' : 'Yes! This is the ' + P.en + '.') : 'This is ' + lotArt(L) + '. The ' + (J ? J[0] + ' works at the ' : '') + P.en + ' is here.');
    }
    o += '<p class="leg"><span class="r"></span> richtiger Weg &nbsp; <span class="b"></span> dein Weg</p>';
    o += '<div class="row"><button class="go alt" data-x="replay">▶ Nochmal zeigen</button><button class="go sun" data-x="next">' + (k + 1 < N ? 'Weiter →' : 'Fertig ✓') + '</button></div>';
    U.card.innerHTML = o; U.card.scrollTop = 0;
    if (task.typ === 'weg' && ok) say('Right! You are at the ' + P.en + '.');
  }
  function replay() { if (!WD.paths.children.length) return; WD.grow = { t: 0, dur: 2.2, list: WD.paths.children.slice() }; WD.paths.children.forEach(function (m) { m.geometry.setDrawRange(0, 0); }); }
  nextTask();
}

// Wo wurde der Weg falsch verstanden?  → { step: Satz-Nummer oder null, why: Erklärung, node }
function explain(r, kid, L) {
  var sol = r.nodes, d = 0;
  while (d < sol.length && d < kid.length && sol[d] === kid[d]) d++;
  if (L === r.target) return { step: null, why: '' };
  var last = r.steps.length - 1, fin = r.steps[last];
  if (d === sol.length && kid.length === sol.length) {
    // richtiger Haltepunkt, aber falsches Gebäude
    return { step: last, node: sol[sol.length - 1], why: 'Der Weg stimmt! Aber «on your ' + DIR[fin.side] + '» heisst ' + DIRDE[fin.side] + '. Du hast das Gebäude auf der anderen Seite gewählt.' };
  }
  if (d >= kid.length) {
    // zu früh stehen geblieben
    var s = r.stepOf[d] != null ? r.stepOf[d] : last;
    return { step: s, node: kid[kid.length - 1], why: 'Hier bist du stehen geblieben – das Ziel ist noch weiter. ' + (s === last ? 'Zähle die Gebäude auf der ' + (fin.side === 'L' ? 'linken' : 'rechten') + ' Seite: «the ' + ORD[fin.ord - 1] + ' building» = das ' + ORDDE[fin.ord - 1] + ' Gebäude.' : 'Lies den Satz nochmals genau.') };
  }
  if (d >= sol.length) {
    return { step: last, node: sol[sol.length - 1], why: 'Du bist zu weit gegangen. «the ' + ORD[fin.ord - 1] + ' building on your ' + DIR[fin.side] + '» = das ' + ORDDE[fin.ord - 1] + ' Gebäude ' + DIRDE[fin.side] + '.' };
  }
  var at = sol[d - 1], step = r.stepOf[d - 1], st = r.steps[step], n = NODES[at];
  var inH = d - 2 >= 0 ? hdOf(sol[d - 2], at, true) : r.face;
  var want = rel(inH, hdOf(at, sol[d])), did = rel(inH, hdOf(at, kid[d]));
  if (d - 1 === 0) {
    return { step: 0, node: at, why: 'Am Anfang stehst du mit dem Rücken zum Gebäude. «turn ' + DIR[st.turn] + '» heisst ' + DIRDE[st.turn] + '. Du bist ' + DIRDE[did] + ' gegangen.' };
  }
  if (n.t === 'R') {
    var entry = sol.indexOf(sol.filter(function (x) { return NODES[x].t === 'R'; })[0]), kEx = 0;
    for (var q = entry + 1; q < kid.length && NODES[kid[q]].t === 'R'; q++) kEx++;
    return { step: step, node: at, why: '«take the ' + ORD[st.exit - 1] + ' exit» heisst: die ' + ORDDE[st.exit - 1] + ' Ausfahrt aus dem Kreisel. ' + (kEx ? 'Du hast die ' + kEx + '. Ausfahrt genommen.' : 'Zähle die Ausfahrten.') };
  }
  if (n.t === 'S' || did === 'B') return { step: step, node: at, why: 'Hier bist du umgekehrt. Geh weiter in dieselbe Richtung.' };
  if (st.t === 'turn' && want === 'S') {
    return { step: step, node: at, why: 'Hier bist du schon abgebogen. Das war erst die ' + (r.crossNo[d - 1] || 1) + '. Kreuzung. «at the ' + ORD[st.n - 1] + ' crossing» = bei der ' + ORDDE[st.n - 1] + ' Kreuzung. Zähle die Kreuzungen!' };
  }
  if (want === 'S') return { step: step, node: at, why: 'Hier musst du geradeaus gehen («walk straight on»). Du bist ' + DIRDE[did] + ' gegangen.' };
  if (did === 'S') return { step: step, node: at, why: 'Hier musst du abbiegen: «turn ' + DIR[want] + '» heisst ' + DIRDE[want] + '. Du bist geradeaus gegangen.' + (st.t === 'turn' && st.n > 1 ? ' Das ist die ' + ORDDE[st.n - 1] + ' Kreuzung.' : '') };
  return { step: step, node: at, why: '«turn ' + DIR[want] + '» heisst ' + DIRDE[want] + '. Du bist ' + DIRDE[did] + ' gegangen. Tipp: Links ist, wo der Daumen der linken Hand ein «L» macht.' };
}
function hdOf(a, b, end) { var e = EMAP[a + '>' + b]; if (!e) { var A = NODES[a], B = NODES[b]; return Math.atan2(B.z - A.z, B.x - A.x); } return end ? e.h1 : e.h0; }

// Knopf «Frei spazieren» im Stufen-Menü
G.extra = function () {
  var lvs = app.querySelector('.lvs'); if (!lvs) return;
  var b = document.createElement('button'); b.className = 'lv frei'; b.innerHTML = '<span class="n" style="background:#fff">🚶</span><span class="tx"><b>Free walk</b><span>Frei durch die Stadt spazieren und Wörter hören</span></span>';
  b.onclick = function () { tone(520, .08); freeWalk(); };
  lvs.appendChild(b);
};
function freeWalk() {
  stopAll(); RUN++; CUR = -1; KN.level(null);
  app.innerHTML = '<div class="top"><button class="pill" data-back>← Stufen</button><span class="t">Free walk</span>' + sndBtn() + '</div><div class="msg" id="msg"></div><div class="stage" id="stage"></div>';
  app.querySelector('[data-back]').onclick = menu;
  var stage = document.getElementById('stage'), msgEl = document.getElementById('msg');
  G.play({ typ: 'frei' }, { stage: stage, msg: function (t) { msgEl.innerHTML = t; }, later: function (fn, ms) { setTimeout(fn, ms); }, answer: function () { return true; } }, -1);
}
