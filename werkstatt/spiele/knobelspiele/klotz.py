# Klötzli-Spiele (dritte Lieferung): Klötzli-Turm (fallende Klötze) und Kisten-Packen (Teile in die Kiste legen).
# Eigene Spiele im Stil der Klassenkiste (Holzklötze, Eule), keine Nachbildung eines bestimmten Spiels.
# Wird von bauen.py aufgerufen: klotz.alle(spiel, logo, LOGO_CSS)

HOLZ_CSS = r"""
.kl{--z:#8a5a2b}
.klotz{border-radius:22%;box-shadow:inset 0 -3px 0 rgba(0,0,0,.18),inset 0 2px 0 rgba(255,255,255,.45)}
.k1,.z.klotz.k1{background:linear-gradient(160deg,#f6c65b,#e3a63a)}.k2,.z.klotz.k2{background:linear-gradient(160deg,#7cc2ef,#4c9bd4)}
.k3,.z.klotz.k3{background:linear-gradient(160deg,#f29a8f,#de6f62)}.k4,.z.klotz.k4{background:linear-gradient(160deg,#9fd08a,#6fae58)}
.k5,.z.klotz.k5{background:linear-gradient(160deg,#c6a6e6,#9a77c8)}.k6,.z.klotz.k6{background:linear-gradient(160deg,#f7b77a,#e48c42)}
.k7,.z.klotz.k7{background:linear-gradient(160deg,#8fd6cf,#4fb3a8)}
.stein,.z.stein{background:repeating-linear-gradient(135deg,#a9b1b8 0 6px,#98a1a9 6px 12px);border-radius:22%;box-shadow:inset 0 -3px 0 rgba(0,0,0,.2)}
.kl-info{display:flex;gap:10px;flex-wrap:wrap;justify-content:center;align-items:center}
.kl-info span{background:#fff;border:2px solid var(--line);border-radius:14px;padding:4px 14px;font-size:20px;box-shadow:var(--sch-k)}
.kl-info b{font-weight:400;color:var(--sky-d);font-size:24px}
"""


def alle(spiel, logo, LOGO_CSS):
    # ================================================================== Klötzli-Turm
    spiel(id='kloetzli-turm', titel='Klötzli-Turm', icon=logo('kloetzli-turm'), fach='Knobeln', thema='Logik', stufe='2.–6. Klasse', sort=5, n=0,
          sterne={'modus': 'sammeln', 'pro': 10, 'max': 3, 'proLevel': True, 'proTag': False},  # je 10 richtige 1 Stern, pro Stufe bis 3
          kurz='Fallende Klötzli drehen und schieben, bis Reihen voll sind.',
          intro='Die Klötzli fallen von oben. Schiebe und drehe sie so, dass eine Reihe ganz voll wird. Volle Reihen verschwinden!',
          levels=[dict(name='Drei Reihen', info='Langsam, einfache Klötzli', ziel=3, ms=950, teile='leicht'),
                  dict(name='Fünf Reihen', info='Alle Klötzli, langsam', ziel=5, ms=850, teile='alle'),
                  dict(name='Acht Reihen', info='Etwas schneller', ziel=8, ms=700, teile='alle'),
                  dict(name='Zehn Reihen', info='Schnell', ziel=10, ms=550, teile='alle'),
                  dict(name='Fünfzehn Reihen', info='Sehr schnell', ziel=15, ms=420, teile='alle')],
          css=LOGO_CSS + HOLZ_CSS + r"""
.kt{display:flex;gap:22px;align-items:flex-start;justify-content:center;flex-wrap:wrap;width:100%}
.kt-schacht{position:relative;display:grid;background:#fdf8ee;border:4px solid #c9a46a;border-radius:16px;padding:4px;gap:2px;box-shadow:var(--sch);touch-action:none}
.kt-schacht .z{border-radius:22%;background:rgba(201,164,106,.12)}
.kt-schacht .z.geist{background:transparent;outline:2px dashed rgba(63,120,168,.45);outline-offset:-3px}
.kt-schacht .z.weg{animation:weg .35s forwards}
@keyframes weg{to{transform:scale(.2);opacity:0}}
.kt-seite{display:flex;flex-direction:column;gap:14px;align-items:center;min-width:170px}
.kt-naechst{background:#fff;border:2px solid var(--line);border-radius:18px;padding:10px 14px;box-shadow:var(--sch-k);text-align:center;font-size:18px;color:var(--soft)}
.kt-naechst .mini{display:grid;gap:2px;margin:6px auto 0;justify-content:center}
.kt-tasten{display:grid;grid-template-columns:repeat(3,72px);gap:10px}
.kt-tasten button{height:72px;border-radius:18px;background:#fff;border:2px solid var(--ink);box-shadow:0 4px 0 var(--line2);font:700 30px system-ui,sans-serif;padding:0;touch-action:manipulation}
.kt-tasten button:active{transform:translateY(3px);box-shadow:none}
.kt-tasten .breit{grid-column:span 3;height:58px;font:400 22px "Patrick Hand",cursive;background:var(--sun)}
.kt-pause{position:absolute;inset:0;display:grid;place-items:center;background:rgba(253,248,238,.85);border-radius:12px;font-size:26px;text-align:center;padding:10px}
@media (max-width:700px){.kt{gap:10px}.kt-seite{min-width:0;width:100%;flex-direction:row;flex-wrap:wrap;justify-content:center;gap:10px}.kt-naechst{padding:6px 10px;font-size:15px}.kt-tasten{grid-template-columns:repeat(6,1fr);width:100%}.kt-tasten button{height:58px;font-size:24px}}
""",
          js=r"""
// Klötze: Felder als [Zeile, Spalte] in einem 4×4-Raster, Farbe 1–7
var KT_FORMEN = [
  { f: [[0,1],[0,2],[1,1],[1,2]], k: 1 },        // Quadrat
  { f: [[1,0],[1,1],[1,2],[1,3]], k: 2 },        // Stange
  { f: [[0,0],[1,0],[1,1],[1,2]], k: 3 },        // Haken links
  { f: [[0,2],[1,0],[1,1],[1,2]], k: 6 },        // Haken rechts
  { f: [[0,1],[1,0],[1,1],[1,2]], k: 5 },        // Dach
  { f: [[0,1],[0,2],[1,0],[1,1]], k: 4 },        // Treppe
  { f: [[0,0],[0,1],[1,1],[1,2]], k: 7 }];       // Treppe andersrum
var KT_LEICHT = [0, 1, 2, 3];
G.play = function (lv, api) {
  var B = 10, H = 16, feld = [], linien = 0, myRun = RUN, lauf = true, pause = false;
  for (var y = 0; y < H; y++) { feld.push([]); for (var x = 0; x < B; x++) feld[y].push(0); }
  var avW = Math.min(window.innerWidth - 40, 900), avH = window.innerHeight - (avW > 700 ? 190 : 400);
  var s = Math.floor(Math.min(36, (avH - 12) / H - 2, (avW > 700 ? 420 : avW - 12) / B - 2)); s = Math.max(18, s);
  var wrap = document.createElement('div'); wrap.className = 'kt';
  wrap.innerHTML = '<div class="kt-schacht" style="grid-template-columns:repeat(' + B + ',' + s + 'px);grid-auto-rows:' + s + 'px"></div>' +
    '<div class="kt-seite"><div class="kl-info"><span>Reihen <b class="lz">0</b> von ' + lv.ziel + '</span></div>' +
    '<div class="kt-naechst">Als Nächstes<div class="mini"></div></div>' +
    '<div class="kt-tasten"><button data-t="l" aria-label="Nach links">◀</button><button data-t="d" aria-label="Drehen">⟳</button><button data-t="r" aria-label="Nach rechts">▶</button>' +
    '<button data-t="u" aria-label="Schneller nach unten">▼</button><button data-t="f" aria-label="Ganz nach unten fallen lassen">⤓</button><button data-t="p" aria-label="Pause">⏸</button>' +
    '</div></div>';
  api.stage.appendChild(wrap);
  var schacht = wrap.querySelector('.kt-schacht'), zellen = [], lz = wrap.querySelector('.lz'), mini = wrap.querySelector('.mini');
  for (var i = 0; i < B * H; i++) { var z = document.createElement('div'); z.className = 'z'; schacht.appendChild(z); zellen.push(z); }
  api.msg('<span class="em">🧱</span> Mach volle Reihen!' + (avW > 700 ? ' <small>◀ ▶ schieben, ⟳ drehen, ⤓ fallen lassen</small>' : ''));
  var pool = lv.teile === 'leicht' ? KT_LEICHT : [0, 1, 2, 3, 4, 5, 6], beutel = [];
  function zieh() { if (!beutel.length) beutel = shuffle(pool.slice()); return beutel.pop(); }
  var akt = null, naechst = zieh();
  function felder(t) { return t.f.map(function (p) { return [t.y + p[0], t.x + p[1]]; }); }
  function passt(t) { return felder(t).every(function (p) { return p[1] >= 0 && p[1] < B && p[0] < H && (p[0] < 0 || !feld[p[0]][p[1]]); }); }
  function dreh(f) { // im Uhrzeigersinn um die Mitte des Klotzes
    var my = 0, mx = 0; f.forEach(function (p) { my = Math.max(my, p[0]); mx = Math.max(mx, p[1]); });
    var r = f.map(function (p) { return [p[1], my - p[0]]; }), oy = Math.min.apply(null, r.map(function (p) { return p[0]; })), ox = Math.min.apply(null, r.map(function (p) { return p[1]; }));
    var oy0 = Math.min.apply(null, f.map(function (p) { return p[0]; })), ox0 = Math.min.apply(null, f.map(function (p) { return p[1]; }));
    return r.map(function (p) { return [p[0] - oy + oy0, p[1] - ox + ox0]; });
  }
  function neu() {
    var f = KT_FORMEN[naechst]; naechst = zieh();
    akt = { f: f.f.map(function (p) { return p.slice(); }), k: f.k, x: 3, y: -1 };
    zeigNaechst();
    if (!passt(akt)) { voll(); return; }
    male();
  }
  function zeigNaechst() {
    var f = KT_FORMEN[naechst], ms = Math.round(s * .7), o = '';
    for (var y = 0; y < 2; y++) for (var x = 0; x < 4; x++) { var drin = f.f.some(function (p) { return p[0] === y && p[1] === x; }); o += '<i class="' + (drin ? 'klotz k' + f.k : '') + '" style="width:' + ms + 'px;height:' + ms + 'px;display:block"></i>'; }
    mini.style.gridTemplateColumns = 'repeat(4,' + ms + 'px)'; mini.innerHTML = o;
  }
  function geist() { var g = { f: akt.f, x: akt.x, y: akt.y }; while (passt({ f: g.f, x: g.x, y: g.y + 1 })) g.y++; return g; }
  function male() {
    var g = akt ? felder(geist()) : [], a = akt ? felder(akt) : [];
    for (var y = 0; y < H; y++) for (var x = 0; x < B; x++) { var z = zellen[y * B + x], k = feld[y][x]; z.className = 'z' + (k ? ' klotz k' + k : ''); }
    g.forEach(function (p) { if (p[0] >= 0 && !feld[p[0]][p[1]]) zellen[p[0] * B + p[1]].className = 'z geist'; });
    a.forEach(function (p) { if (p[0] >= 0) zellen[p[0] * B + p[1]].className = 'z klotz k' + akt.k; });
  }
  function fest() {
    felder(akt).forEach(function (p) { if (p[0] >= 0) feld[p[0]][p[1]] = akt.k; });
    akt = null; tone(330, 0.06, 'triangle', 0.08);
    var volle = []; for (var y = 0; y < H; y++) if (feld[y].every(function (v) { return v; })) volle.push(y);
    if (!volle.length) { neu(); return; }
    male(); volle.forEach(function (y) { for (var x = 0; x < B; x++) zellen[y * B + x].classList.add('weg'); });
    volle.forEach(function (y, n) { tone(660 + n * 110, 0.12); });
    lauf = false;
    api.later(function () {
      volle.forEach(function (y) { feld.splice(y, 1); var r = []; for (var x = 0; x < B; x++) r.push(0); feld.unshift(r); });
      for (var n = 0; n < volle.length; n++) { linien++; api.answer(true, true); }
      lz.textContent = Math.min(linien, lv.ziel);
      if (linien >= lv.ziel) { ende(); return; }
      api.msg('<span class="em">' + (volle.length > 1 ? '🎉' : '✨') + '</span> ' + (volle.length > 1 ? volle.length + ' Reihen auf einmal!' : 'Eine Reihe weg!'));
      lauf = true; neu(); takt();
    }, 380);
  }
  function voll() {
    lauf = false; bad();
    api.msg('<span class="em">🙈</span> Der Turm ist zu hoch! Wir räumen auf und machen weiter.');
    api.later(function () { for (var y = 0; y < H; y++) for (var x = 0; x < B; x++) feld[y][x] = 0; lauf = true; neu(); takt(); }, 1600);
  }
  function ende() { lauf = false; document.removeEventListener('keydown', taste); api.done('Du hast ' + linien + (linien === 1 ? ' Reihe' : ' Reihen') + ' geschafft!', 1); }
  function schritt() {
    if (!akt) return;
    var t = { f: akt.f, x: akt.x, y: akt.y + 1 };
    if (passt(t)) { akt.y++; male(); } else fest();
  }
  function takt() { if (RUN !== myRun || !lauf) return; api.later(function () { if (!lauf || pause) { if (pause) takt(); return; } schritt(); takt(); }, lv.ms); }
  function tu(t) {
    if (!akt || !lauf || RUN !== myRun) return;
    if (t === 'p') { pause = !pause; var p = schacht.querySelector('.kt-pause'); if (pause && !p) schacht.insertAdjacentHTML('beforeend', '<div class="kt-pause">Pause<br>Tippe ⏸ zum Weiterspielen</div>'); if (!pause && p) p.remove(); return; }
    if (pause) return;
    if (t === 'l' || t === 'r') { var n = { f: akt.f, x: akt.x + (t === 'l' ? -1 : 1), y: akt.y }; if (passt(n)) { akt.x = n.x; male(); tone(520, 0.03, 'sine', 0.05); } }
    else if (t === 'd') {
      var f = dreh(akt.f);
      for (var k = 0; k < 3; k++) { var dx = [0, -1, 1][k], n2 = { f: f, x: akt.x + dx, y: akt.y }; if (passt(n2)) { akt.f = f; akt.x = n2.x; male(); tone(600, 0.04, 'sine', 0.06); break; } }
    }
    else if (t === 'u') schritt();
    else if (t === 'f') { var g = geist(); akt.y = g.y; male(); fest(); }
  }
  wrap.querySelector('.kt-tasten').addEventListener('pointerdown', function (e) {
    var b = e.target.closest('[data-t]'); if (!b) return; e.preventDefault(); tu(b.dataset.t);
    if (b.dataset.t === 'l' || b.dataset.t === 'r' || b.dataset.t === 'u') { // gedrückt halten = weiter
      var t = b.dataset.t, iv = setInterval(function () { if (RUN !== myRun) return clearInterval(iv); tu(t); }, 110), wart = setTimeout(function () {}, 0);
      var stopp = function () { clearInterval(iv); b.removeEventListener('pointerup', stopp); b.removeEventListener('pointerleave', stopp); };
      clearInterval(iv); iv = null;
      var start = setTimeout(function () { iv = setInterval(function () { if (RUN !== myRun) return clearInterval(iv); tu(t); }, 90); }, 260);
      stopp = function () { clearTimeout(start); clearInterval(iv); b.removeEventListener('pointerup', stopp); b.removeEventListener('pointerleave', stopp); b.removeEventListener('pointercancel', stopp); };
      b.addEventListener('pointerup', stopp); b.addEventListener('pointerleave', stopp); b.addEventListener('pointercancel', stopp);
    }
  });
  // Wischen im Schacht: links/rechts schieben, nach unten fallen lassen, Tippen = drehen
  var wx = null, wy = null, wt = 0;
  schacht.addEventListener('pointerdown', function (e) { wx = e.clientX; wy = e.clientY; wt = Date.now(); });
  schacht.addEventListener('pointerup', function (e) {
    if (wx == null) return; var dx = e.clientX - wx, dy = e.clientY - wy; wx = null;
    if (Math.abs(dx) < 12 && Math.abs(dy) < 12) { tu('d'); return; }
    if (Math.abs(dx) > Math.abs(dy)) { var n = Math.max(1, Math.round(Math.abs(dx) / s)); for (var i = 0; i < n; i++) tu(dx < 0 ? 'l' : 'r'); }
    else if (dy > 40) tu('f');
  });
  function taste(e) {
    if (RUN !== myRun) { document.removeEventListener('keydown', taste); return; }
    var m = { ArrowLeft: 'l', ArrowRight: 'r', ArrowUp: 'd', ArrowDown: 'u', ' ': 'f', p: 'p' }[e.key]; if (m) { e.preventDefault(); tu(m); }
  }
  document.addEventListener('keydown', taste);
  neu(); takt();
};
""")

    # ================================================================== Kisten-Packen
    spiel(id='kisten-packen', titel='Kisten-Packen', icon=logo('kisten-packen'), fach='Knobeln', thema='Logik', stufe='1.–6. Klasse', sort=6, n=0,
          sterne={'modus': 'sammeln', 'pro': 10, 'max': 3, 'proLevel': True, 'proTag': False},  # je 10 richtige 1 Stern, pro Stufe bis 3
          kurz='Klötzli in die Kiste legen. Volle Reihen und Spalten verschwinden.',
          intro='Zieh die Klötzli in die Kiste. Ist eine Reihe oder eine Spalte ganz voll, verschwindet sie. Überlege gut, wohin jedes Teil passt!',
          levels=[dict(name='Kleine Kiste', info='6 × 6 Felder, kleine Teile, 5 Reihen', n=6, ziel=5, teile='klein', steine=0),
                  dict(name='Grosse Kiste', info='8 × 8 Felder, 10 Reihen', n=8, ziel=10, teile='mittel', steine=0),
                  dict(name='Grosse Teile', info='Auch lange und breite Teile, 15 Reihen', n=8, ziel=15, teile='alle', steine=0),
                  dict(name='Mit Steinen', info='Graue Steine bleiben liegen, 15 Reihen', n=8, ziel=15, teile='alle', steine=5),
                  dict(name='Profi-Kiste', info='Alle Teile, 25 Reihen', n=8, ziel=25, teile='alle', steine=0)],
          css=LOGO_CSS + HOLZ_CSS + r"""
.kp{display:flex;gap:24px;align-items:center;justify-content:center;flex-wrap:wrap;width:100%}
.kp-kiste{display:grid;background:#e9d2a6;border:5px solid #b98b4e;border-radius:18px;padding:5px;gap:3px;box-shadow:var(--sch),inset 0 2px 6px rgba(0,0,0,.12);touch-action:none}
.kp-kiste .z{border-radius:22%;background:rgba(255,255,255,.35)}
.kp-kiste .z.vor{outline:3px solid #5f9a4a;outline-offset:-3px;background:rgba(95,154,74,.25)}
.kp-kiste .z.nein{outline:3px solid #c8574e;outline-offset:-3px;background:rgba(200,87,78,.2)}
.kp-kiste .z.weg{animation:weg .35s forwards}
@keyframes weg{to{transform:scale(.2);opacity:0}}
.kp-seite{display:flex;flex-direction:column;gap:16px;align-items:center}
.kp-ablage{display:flex;gap:18px;align-items:center;justify-content:center;flex-wrap:wrap;min-height:130px;background:#fff;border:2px dashed var(--line2);border-radius:20px;padding:14px 18px}
.kp-teil{display:grid;gap:3px;cursor:grab;touch-action:none;padding:4px;border-radius:10px;transition:transform .12s}
.kp-teil:hover{transform:scale(1.05)}
.kp-teil.leer{visibility:hidden}
.kp-teil.passt-nicht{opacity:.35}
.kp-teil i{display:block}
.kp-zieh{position:fixed;z-index:50;display:grid;gap:3px;pointer-events:none;filter:drop-shadow(0 10px 14px rgba(0,0,0,.25))}
@media (max-width:760px){.kp{flex-direction:column;gap:14px}}
""",
          js=r"""
// Teile als Liste von [Zeile, Spalte]
var KP_KLEIN = [[[0,0]], [[0,0],[0,1]], [[0,0],[1,0]], [[0,0],[0,1],[0,2]], [[0,0],[1,0],[2,0]], [[0,0],[0,1],[1,0],[1,1]],
  [[0,0],[1,0],[1,1]], [[0,1],[1,0],[1,1]], [[0,0],[0,1],[1,0]], [[0,0],[0,1],[1,1]]];
var KP_GROSS = [[[0,0],[0,1],[0,2],[0,3]], [[0,0],[1,0],[2,0],[3,0]], [[0,0],[0,1],[0,2],[1,0],[1,1],[1,2],[2,0],[2,1],[2,2]],
  [[0,0],[1,0],[2,0],[2,1],[2,2]], [[0,2],[1,2],[2,0],[2,1],[2,2]], [[0,0],[0,1],[0,2],[1,1]], [[0,1],[1,0],[1,1],[1,2]],
  [[0,0],[0,1],[1,1],[1,2]], [[0,1],[0,2],[1,0],[1,1]], [[0,0],[0,1],[0,2],[0,3],[0,4]], [[0,0],[1,0],[2,0],[1,1]], [[0,0],[0,1],[0,2],[1,0],[1,1],[1,2]]];
G.play = function (lv, api) {
  var N = lv.n, kiste = [], reihen = 0, myRun = RUN;
  var teile = lv.teile === 'klein' ? KP_KLEIN : lv.teile === 'mittel' ? KP_KLEIN.concat(KP_GROSS.slice(0, 2), KP_GROSS.slice(5, 9)) : KP_KLEIN.concat(KP_GROSS);
  for (var y = 0; y < N; y++) { kiste.push([]); for (var x = 0; x < N; x++) kiste[y].push(0); }
  function steine() { shuffle(range(N * N)).slice(0, lv.steine).forEach(function (k) { kiste[Math.floor(k / N)][k % N] = 's'; }); }
  steine();
  var breit = window.innerWidth > 760, avH = window.innerHeight - (breit ? 200 : 380), avW = Math.min(window.innerWidth - 40, 1000) - (breit ? 360 : 0);
  var s = Math.floor(Math.min(58, (avH - 16) / N - 3, (avW - 16) / N - 3)); s = Math.max(28, s);
  var ts = Math.max(18, Math.round(s * .55));
  var wrap = document.createElement('div'); wrap.className = 'kp';
  wrap.innerHTML = '<div class="kp-kiste" style="grid-template-columns:repeat(' + N + ',' + s + 'px);grid-auto-rows:' + s + 'px"></div>' +
    '<div class="kp-seite"><div class="kl-info"><span>Reihen <b class="lz">0</b> von ' + lv.ziel + '</span></div><div class="kp-ablage"></div></div>';
  api.stage.appendChild(wrap);
  var box = wrap.querySelector('.kp-kiste'), ablage = wrap.querySelector('.kp-ablage'), lz = wrap.querySelector('.lz'), zellen = [];
  for (var i = 0; i < N * N; i++) { var z = document.createElement('div'); z.className = 'z'; box.appendChild(z); zellen.push(z); }
  api.msg('<span class="em">📦</span> Zieh ein Klötzli in die Kiste!');
  var hand = [];
  function maxDim(t) { var h = 0, w = 0; t.forEach(function (p) { h = Math.max(h, p[0] + 1); w = Math.max(w, p[1] + 1); }); return [h, w]; }
  function teilHtml(t, k, gr) { var d = maxDim(t), o = ''; for (var y = 0; y < d[0]; y++) for (var x = 0; x < d[1]; x++) { var drin = t.some(function (p) { return p[0] === y && p[1] === x; }); o += '<i class="' + (drin ? 'klotz k' + k : '') + '" style="width:' + gr + 'px;height:' + gr + 'px"></i>'; } return { html: o, cols: d[1] }; }
  function passtBei(t, r, c) { return t.every(function (p) { var y = r + p[0], x = c + p[1]; return y >= 0 && x >= 0 && y < N && x < N && !kiste[y][x]; }); }
  function passtIrgendwo(t) { for (var r = 0; r < N; r++) for (var c = 0; c < N; c++) if (passtBei(t, r, c)) return true; return false; }
  function nachfuellen() { hand = [0, 1, 2].map(function () { return { t: pick(teile, 1)[0], k: rnd(1, 7) }; }); }
  function male() {
    for (var y = 0; y < N; y++) for (var x = 0; x < N; x++) { var v = kiste[y][x]; zellen[y * N + x].className = 'z' + (v === 's' ? ' stein' : v ? ' klotz k' + v : ''); }
    ablage.innerHTML = '';
    hand.forEach(function (h, i) {
      var d = document.createElement('div'); d.className = 'kp-teil' + (h ? '' : ' leer'); d.dataset.i = i;
      if (h) { var th = teilHtml(h.t, h.k, ts); d.style.gridTemplateColumns = 'repeat(' + th.cols + ',' + ts + 'px)'; d.innerHTML = th.html; if (!passtIrgendwo(h.t)) d.classList.add('passt-nicht'); }
      else d.style.width = (ts * 2) + 'px';
      ablage.appendChild(d);
    });
  }
  nachfuellen(); male();
  // Ziehen: das Teil schwebt etwas über dem Finger, die Kiste zeigt, wo es hinkommt
  var zug = null;
  function zielZelle(px, py) {
    var r = box.getBoundingClientRect(), d = maxDim(zug.h.t), st = s + 3;
    var lx = px - zug.dx - r.left - 5, ly = py - zug.dy - r.top - 5;
    return [Math.round(ly / st), Math.round(lx / st)];
  }
  function vorschau(rc) {
    zellen.forEach(function (z) { z.classList.remove('vor', 'nein'); });
    if (!rc) return;
    var ok = passtBei(zug.h.t, rc[0], rc[1]);
    zug.h.t.forEach(function (p) { var y = rc[0] + p[0], x = rc[1] + p[1]; if (y >= 0 && x >= 0 && y < N && x < N) zellen[y * N + x].classList.add(ok ? 'vor' : 'nein'); });
  }
  ablage.addEventListener('pointerdown', function (e) {
    var el = e.target.closest('.kp-teil'); if (!el || el.classList.contains('leer') || RUN !== myRun) return;
    e.preventDefault();
    var h = hand[+el.dataset.i], th = teilHtml(h.t, h.k, s), g = document.createElement('div'); g.className = 'kp-zieh';
    g.style.gridTemplateColumns = 'repeat(' + th.cols + ',' + s + 'px)'; g.style.gap = '3px'; g.innerHTML = th.html; document.body.appendChild(g);
    var d = maxDim(h.t), st = s + 3, hoch = e.pointerType === 'mouse' ? 0 : 70;
    zug = { el: el, h: h, i: +el.dataset.i, g: g, dx: d[1] * st / 2, dy: d[0] * st / 2 + hoch, rc: null };
    el.style.visibility = 'hidden';
    bewegen(e);
  });
  function bewegen(e) {
    if (!zug) return;
    zug.g.style.left = (e.clientX - zug.dx) + 'px'; zug.g.style.top = (e.clientY - zug.dy) + 'px';
    var rc = zielZelle(e.clientX, e.clientY); zug.rc = rc; vorschau(rc);
  }
  window.addEventListener('pointermove', bewegen);
  function los(e) {
    if (!zug) return; var z = zug; zug = null; z.g.remove(); vorschau(null);
    if (RUN !== myRun) return;
    var rc = z.rc;
    if (rc && passtBei(z.h.t, rc[0], rc[1])) {
      z.h.t.forEach(function (p) { kiste[rc[0] + p[0]][rc[1] + p[1]] = z.h.k; });
      hand[z.i] = null; tone(440 + z.h.t.length * 40, 0.06, 'triangle', 0.09);
      if (hand.every(function (x) { return !x; })) nachfuellen();
      raeumen();
    } else { z.el.style.visibility = ''; if (rc) tone(200, 0.12, 'triangle', 0.08); }
  }
  window.addEventListener('pointerup', los); window.addEventListener('pointercancel', los);
  function raeumen() {
    var voll = [], y, x;
    for (y = 0; y < N; y++) if (kiste[y].every(function (v) { return v; })) voll.push(['r', y]);
    for (x = 0; x < N; x++) { var ok = true; for (y = 0; y < N; y++) if (!kiste[y][x]) ok = false; if (ok) voll.push(['s', x]); }
    male();
    if (!voll.length) return pruefen();
    var weg = {};
    voll.forEach(function (v) { for (var k = 0; k < N; k++) { var yy = v[0] === 'r' ? v[1] : k, xx = v[0] === 'r' ? k : v[1]; if (kiste[yy][xx] !== 's') { weg[yy * N + xx] = 1; zellen[yy * N + xx].classList.add('weg'); } } });
    voll.forEach(function (v, n) { tone(660 + n * 110, 0.12); });
    api.later(function () {
      Object.keys(weg).forEach(function (k) { kiste[Math.floor(k / N)][k % N] = 0; });
      for (var n = 0; n < voll.length; n++) { reihen++; api.answer(true, true); }
      lz.textContent = Math.min(reihen, lv.ziel);
      if (reihen >= lv.ziel) { api.done('Du hast ' + reihen + ' Reihen geschafft!', 1); return; }
      api.msg('<span class="em">' + (voll.length > 1 ? '🎉' : '✨') + '</span> ' + (voll.length > 1 ? voll.length + ' Reihen auf einmal!' : 'Eine Reihe weg!'));
      male(); pruefen();
    }, 380);
  }
  function pruefen() {
    if (hand.some(function (h) { return h && passtIrgendwo(h.t); })) return;
    api.msg('<span class="em">🙈</span> Kein Teil passt mehr. Wir leeren die Kiste und machen weiter!'); bad();
    api.later(function () { for (var y = 0; y < N; y++) for (var x = 0; x < N; x++) kiste[y][x] = 0; steine(); nachfuellen(); male(); api.msg('<span class="em">📦</span> Weiter geht es!'); }, 1800);
  }
};
""")
