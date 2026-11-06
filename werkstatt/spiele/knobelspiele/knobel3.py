# Vierte Lieferung: Laternen (alle Laternen anzünden), Schiebe-Bild (Bildteile zurückschieben), Zahlenmauer (Mathematik).
# Eigene Spiele im Stil der Klassenkiste. Wird von bauen.py aufgerufen: knobel3.alle(spiel, logo, LOGO_CSS, HIER)
import base64, os


def bilder(hier):
    # Bilder fürs Schiebe-Bild: die gemalten Logos der Lehrerin (rund, 320 px)
    out = []
    for n in ['rechen-rakete', 'eulen-weg', 'kiosk', 'wasser-weg', 'uhr-lesen', 'bilder-sudoku', 'der-die-das']:
        with open(os.path.join(hier, 'logos', n + '.webp'), 'rb') as f:
            out.append('data:image/webp;base64,' + base64.b64encode(f.read()).decode())
    return out


def alle(spiel, logo, LOGO_CSS, hier):
    # ================================================================== Laternen
    spiel(id='laternen', titel='Laternen', icon=logo('laternen'), fach='Knobelkiste', thema='Logik', stufe='2.–6. Klasse', sort=7, n=0,
          sterne={'modus': 'sammeln', 'pro': 10, 'max': 3, 'proLevel': True, 'proTag': False},
          kurz='Ein Tipp schaltet eine Laterne und ihre Nachbarn um. Zünde alle an!',
          intro='Jede Laterne ist ein Schalter. Tippst du auf eine, wechselt sie selbst und die Laternen direkt daneben (oben, unten, links, rechts) – wie ein Kreuz. Aus wird an, an wird aus. Ziel: Alle Laternen leuchten!',
          levels=[dict(name='Ein Tipp', info='Ein einziger Tipp genügt. Finde das dunkle Kreuz!', n=3, k=1, ziel=5),
                  dict(name='Zwei Tipps', info='Mit 2 Tipps lösbar', n=3, k=2, ziel=5),
                  dict(name='3 × 3', info='Mit 3 bis 4 Tipps lösbar', n=3, k=4, ziel=5),
                  dict(name='4 × 4', info='Mit 3 bis 4 Tipps lösbar', n=4, k=4, ziel=5),
                  dict(name='5 × 5', info='Mit 5 bis 6 Tipps lösbar', n=5, k=6, ziel=5)],
          css=LOGO_CSS + r"""
.la{display:flex;flex-direction:column;align-items:center;gap:16px;width:100%}
.la-nacht{display:grid;gap:12px;padding:18px;border-radius:26px;background:radial-gradient(circle at 30% 20%,#3a5f8f,#1d3557 70%);box-shadow:var(--sch);border:3px solid var(--gold)}
.la-nacht button{border-radius:50%;border:0;padding:0;position:relative;background:radial-gradient(circle at 40% 35%,#53698a,#2c3e5a);box-shadow:inset 0 -4px 0 rgba(0,0,0,.25);transition:background .25s,box-shadow .25s,transform .1s}
.la-nacht button::after{content:"";position:absolute;inset:26%;border-radius:50%;background:#46597a;transition:background .25s}
.la-nacht button.an{background:radial-gradient(circle at 40% 35%,#fff5c4,#f3c64e 55%,#d99a2b);box-shadow:0 0 22px 6px rgba(255,214,102,.65),inset 0 -4px 0 rgba(0,0,0,.15)}
.la-nacht button.an::after{background:#fffbe8}
.la-nacht button:active{transform:scale(.94)}
.la-nacht button.nb{outline:4px solid rgba(255,255,255,.75);outline-offset:3px}
.la-nacht button.blitz{animation:laBlitz .45s ease-out}
@keyframes laBlitz{0%{transform:scale(.8)}60%{transform:scale(1.08)}100%{transform:scale(1)}}
.la-nacht button.tipp{outline:5px solid #ffd666;outline-offset:4px;animation:laTipp 1s ease-in-out infinite}
@keyframes laTipp{50%{outline-color:rgba(255,214,102,.25)}}
.la-regel{display:flex;align-items:center;gap:12px;background:#fff;border:2px solid var(--line);border-radius:16px;padding:8px 16px;font-size:19px;box-shadow:var(--sch-k);max-width:560px}
.la-regel svg{flex:none}
.la-info{display:flex;gap:10px;flex-wrap:wrap;justify-content:center}
.la-info span{background:#fff;border:2px solid var(--line);border-radius:14px;padding:4px 14px;font-size:20px;box-shadow:var(--sch-k)}
.la-info b{font-weight:400;color:var(--sky-d);font-size:24px}
""",
          js=r"""
G.play = function (lv, api) {
  var N = lv.n, geloest = 0, myRun = RUN;
  var wrap = document.createElement('div'); wrap.className = 'la'; api.stage.appendChild(wrap);
  function raetsel() {
    var feld = [], start, zuege = 0, fertig = false;
    for (var i = 0; i < N * N; i++) feld.push(1);
    function kipp(f, k) { var y = Math.floor(k / N), x = k % N; [[0,0],[1,0],[-1,0],[0,1],[0,-1]].forEach(function (d) { var yy = y + d[0], xx = x + d[1]; if (yy >= 0 && xx >= 0 && yy < N && xx < N) f[yy * N + xx] ^= 1; }); }
    // aus dem Ziel (alle an) rückwärts: lv.k verschiedene Felder umschalten, dann ist es sicher lösbar
    var k = lv.k > 2 ? rnd(lv.k - 1, lv.k) : lv.k, loes = pick(range(N * N), k), startLoes;
    loes.forEach(function (t) { kipp(feld, t); });
    startLoes = loes.slice();
    if (feld.every(function (v) { return v; })) return raetsel();
    start = feld.slice();
    var s = Math.floor(Math.min(84, (Math.min(window.innerWidth, 640) - 80) / N - 12, (window.innerHeight - 300) / N - 12)); s = Math.max(40, s);
    // kleines Bild der Regel: Tipp in der Mitte schaltet das Kreuz um
    var regel = '<div class="la-regel"><svg width="58" height="58" viewBox="0 0 30 30" aria-hidden="true">' + [0,1,2].map(function (y) { return [0,1,2].map(function (x) {
      var kreuz = (x === 1 || y === 1); return '<circle cx="' + (5 + x * 10) + '" cy="' + (5 + y * 10) + '" r="4" fill="' + (kreuz ? '#f3c64e' : '#46597a') + '"/>'; }).join(''); }).join('') +
      '<circle cx="15" cy="15" r="2.2" fill="#fff" stroke="#c4952f" stroke-width="1"/></svg><span>Ein Tipp schaltet die Laterne <b>und</b> ihre Nachbarn im Kreuz um.</span></div>';
    wrap.innerHTML = regel + '<div class="la-info"><span>Tipps <b class="zz">0</b></span></div>' +
      '<div class="la-nacht" style="grid-template-columns:repeat(' + N + ',' + s + 'px);grid-auto-rows:' + s + 'px"></div>' +
      '<div class="row"><button class="go alt" data-x="hilfe">Hilfe</button><button class="go alt" data-x="neu">↺ Nochmal von vorn</button></div>';
    var nacht = wrap.querySelector('.la-nacht'), zz = wrap.querySelector('.zz');
    for (i = 0; i < N * N; i++) nacht.insertAdjacentHTML('beforeend', '<button data-k="' + i + '" aria-label="Laterne ' + (i + 1) + '"></button>');
    function male() { Array.prototype.forEach.call(nacht.children, function (b, i) { b.classList.toggle('an', !!feld[i]); b.setAttribute('aria-pressed', String(!!feld[i])); }); zz.textContent = zuege; }
    function kreuz(k) { var y = Math.floor(k / N), x = k % N, r = []; [[0,0],[1,0],[-1,0],[0,1],[0,-1]].forEach(function (d) { var yy = y + d[0], xx = x + d[1]; if (yy >= 0 && xx >= 0 && yy < N && xx < N) r.push(yy * N + xx); }); return r; }
    function zeig(k) { Array.prototype.forEach.call(nacht.children, function (b) { b.classList.remove('nb'); }); if (k != null) kreuz(k).forEach(function (j) { nacht.children[j].classList.add('nb'); }); }
    male();
    api.msg('Zünde alle Laternen an!');
    // Mit der Maus: beim Darüberfahren zeigen, welche Laternen mitwechseln
    nacht.onpointerover = function (e) { var b = e.target.closest('button'); if (e.pointerType === 'mouse' && b) zeig(+b.dataset.k); };
    nacht.onpointerleave = function () { zeig(null); };
    nacht.onclick = function (e) {
      var b = e.target.closest('button'); if (!b || fertig || RUN !== myRun) return;
      var t = +b.dataset.k; kipp(feld, t); zuege++; tone(500 + feld.filter(Boolean).length * 25, 0.06, 'sine', 0.08); male();
      var li = loes.indexOf(t); if (li >= 0) loes.splice(li, 1); else loes.push(t);
      Array.prototype.forEach.call(nacht.children, function (x) { x.classList.remove('tipp'); });
      kreuz(t).forEach(function (j) { var x = nacht.children[j]; x.classList.remove('blitz'); void x.offsetWidth; x.classList.add('blitz'); });
      if (feld.every(function (v) { return v; })) {
        fertig = true; geloest++; good();
        api.msg('Alle Laternen leuchten!' + (zuege <= k ? ' Mit nur ' + zuege + ' Tipps!' : ''));
        api.answer(true, true);
        if (geloest >= lv.ziel) { api.later(function () { api.done('Du hast ' + geloest + ' Rätsel gelöst!', 1); }, 1300); return; }
        api.later(raetsel, 1500);
      }
    };
    wrap.querySelector('[data-x="neu"]').onclick = function () { if (fertig) return; feld = start.slice(); loes = startLoes.slice(); zuege = 0; male(); api.msg('Nochmal von vorn!'); };
    // Hilfe: eine Laterne golden umranden, die zur Lösung gehört
    wrap.querySelector('[data-x="hilfe"]').onclick = function () {
      if (fertig || !loes.length) return;
      Array.prototype.forEach.call(nacht.children, function (x) { x.classList.remove('tipp'); });
      nacht.children[loes[0]].classList.add('tipp'); api.msg('Tippe auf die Laterne mit dem goldenen Ring!');
    };
  }
  raetsel();
};
""")

    # ================================================================== Schiebe-Bild
    spiel(id='schiebe-bild', titel='Schiebe-Bild', icon=logo('schiebe-bild'), fach='Knobelkiste', thema='Logik', stufe='1.–6. Klasse', sort=8, n=0,
          sterne={'modus': 'sammeln', 'pro': 10, 'max': 3, 'proLevel': True, 'proTag': False},
          kurz='Die Teile eines Bildes zurückschieben, bis es wieder stimmt.',
          intro='Ein Bild ist durcheinander geraten. Tippe auf ein Teil neben dem leeren Platz, dann rutscht es hinüber. Schiebe so lange, bis das Bild wieder ganz ist!',
          levels=[dict(name='3 × 3, wenig gemischt', info='Mit Zahlen als Hilfe', n=3, misch=12, zahlen=True, ziel=3),
                  dict(name='3 × 3', info='Mit Zahlen als Hilfe', n=3, misch=60, zahlen=True, ziel=3),
                  dict(name='3 × 3 ohne Zahlen', info='Nur das Bild hilft', n=3, misch=60, zahlen=False, ziel=3),
                  dict(name='4 × 4', info='Mit Zahlen als Hilfe', n=4, misch=40, zahlen=True, ziel=3),
                  dict(name='4 × 4 ohne Zahlen', info='Das grosse Schiebe-Bild', n=4, misch=120, zahlen=False, ziel=3)],
          daten={'BILDER': bilder(hier)},
          css=LOGO_CSS + r"""
.sb{display:flex;flex-direction:column;align-items:center;gap:14px;width:100%}
.sb-rahmen{position:relative;background:#e9d2a6;border:5px solid #b98b4e;border-radius:20px;padding:5px;box-shadow:var(--sch)}
.sb-teil{position:absolute;border-radius:10px;background-repeat:no-repeat;box-shadow:inset 0 0 0 2px rgba(255,255,255,.7),0 2px 4px rgba(0,0,0,.15);transition:left .15s ease,top .15s ease;padding:0;border:0;cursor:pointer}
.sb-teil i{position:absolute;left:5px;top:3px;font:700 15px system-ui,sans-serif;color:#1f2421;background:rgba(255,255,255,.85);border-radius:8px;padding:0 6px;font-style:normal}
.sb-fertig .sb-teil{box-shadow:none;border-radius:0}
.sb-vorlage{display:flex;align-items:center;gap:10px;color:var(--soft);font-size:18px}
.sb-vorlage img{width:64px;height:64px;border-radius:50%;box-shadow:var(--sch-k)}
.sb-info{background:#fff;border:2px solid var(--line);border-radius:14px;padding:4px 14px;font-size:20px;box-shadow:var(--sch-k)}
.sb-info b{font-weight:400;color:var(--sky-d);font-size:24px}
""",
          js=r"""
G.play = function (lv, api) {
  var N = lv.n, geloest = 0, myRun = RUN, bilderLeft = shuffle(D.BILDER.slice());
  var wrap = document.createElement('div'); wrap.className = 'sb'; api.stage.appendChild(wrap);
  function raetsel() {
    var bild = bilderLeft[geloest % bilderLeft.length], pos = range(N * N), leer = N * N - 1, zuege = 0, fertig = false;
    // pos[Platz] = Teil; vom fertigen Bild aus mit erlaubten Zügen mischen (darum immer lösbar)
    var vor = -1;
    for (var m = 0; m < lv.misch || pos.every(function (t, i) { return t === i; }); m++) {
      var nb = nachbarn(leer).filter(function (x) { return x !== vor; }), w = nb[rnd(0, nb.length - 1)];
      pos[leer] = pos[w]; pos[w] = N * N - 1; vor = leer; leer = w;
    }
    function nachbarn(p) { var y = Math.floor(p / N), x = p % N, o = []; if (y > 0) o.push(p - N); if (y < N - 1) o.push(p + N); if (x > 0) o.push(p - 1); if (x < N - 1) o.push(p + 1); return o; }
    var gr = Math.floor(Math.min(420, Math.min(window.innerWidth, 640) - 60, window.innerHeight - 320)), t = Math.floor((gr - (N - 1) * 4) / N);
    gr = t * N + (N - 1) * 4;
    wrap.innerHTML = '<div class="row" style="align-items:center"><span class="sb-vorlage"><img src="' + bild + '" alt="">So soll es aussehen</span></div>' +
      '<div class="sb-rahmen" style="width:' + (gr + 10) + 'px;height:' + (gr + 10) + 'px"></div>';
    var rahmen = wrap.querySelector('.sb-rahmen'), teile = [];
    for (var k = 0; k < N * N - 1; k++) {
      var b = document.createElement('button'), ty = Math.floor(k / N), tx = k % N;
      b.className = 'sb-teil'; b.style.width = t + 'px'; b.style.height = t + 'px';
      b.style.backgroundImage = 'url(' + bild + ')'; b.style.backgroundSize = gr + 'px ' + gr + 'px'; b.style.backgroundPosition = (-tx * (t + 4)) + 'px ' + (-ty * (t + 4)) + 'px';
      b.innerHTML = lv.zahlen ? '<i>' + (k + 1) + '</i>' : ''; b.dataset.t = k; b.setAttribute('aria-label', 'Teil ' + (k + 1));
      rahmen.appendChild(b); teile[k] = b;
    }
    function setz() { pos.forEach(function (tt, p) { if (tt === N * N - 1) return; var b = teile[tt]; b.style.left = (5 + (p % N) * (t + 4)) + 'px'; b.style.top = (5 + Math.floor(p / N) * (t + 4)) + 'px'; }); }
    setz();
    api.msg('Schiebe die Teile, bis das Bild stimmt!');
    rahmen.onclick = function (e) {
      var b = e.target.closest('.sb-teil'); if (!b || fertig || RUN !== myRun) return;
      var p = pos.indexOf(+b.dataset.t), ly = Math.floor(leer / N), lx = leer % N, py = Math.floor(p / N), px = p % N;
      if (py !== ly && px !== lx) { tone(200, 0.08, 'triangle', 0.06); return; }
      // ganze Reihe bis zum leeren Platz schieben
      var schritt = py === ly ? (px < lx ? -1 : 1) : (py < ly ? -N : N);
      while (leer !== p) { var w = leer + schritt; pos[leer] = pos[w]; pos[w] = N * N - 1; leer = w; zuege++; }
      tone(520, 0.05, 'sine', 0.07); setz();
      if (pos.every(function (tt, i) { return tt === i; })) {
        fertig = true; geloest++; good(); rahmen.classList.add('sb-fertig');
        api.msg('Das Bild ist wieder ganz!');
        api.answer(true, true);
        if (geloest >= lv.ziel) { api.later(function () { api.done('Du hast ' + geloest + ' Bilder geschafft!', 1); }, 1600); return; }
        api.later(raetsel, 1800);
      }
    };
  }
  raetsel();
};
""")

    # ================================================================== Zahlenmauer
    spiel(id='zahlenmauer', titel='Zahlenmauer', icon=logo('zahlenmauer'), fach='Mathematik', thema='Rechnen', stufe='1.–6. Klasse', sort=4, n=0,
          sterne={'modus': 'sammeln', 'pro': 10, 'max': 3, 'proLevel': True, 'proTag': False},
          kurz='Jeder Stein ist die Summe der zwei Steine darunter. Fülle die Lücken!',
          intro='In der Zahlenmauer ist jeder Stein so gross wie die zwei Steine darunter zusammen. Tippe auf einen leeren Stein und gib die Zahl ein.',
          levels=[dict(name='3 Reihen bis 20', info='Nur nach oben rechnen', r=3, max=5, weg=3, unten=False, ziel=3),
                  dict(name='3 Reihen bis 40', info='Manchmal auch rückwärts rechnen', r=3, max=10, weg=3, unten=True, ziel=3),
                  dict(name='4 Reihen bis 100', info='Plus und Minus', r=4, max=12, weg=5, unten=True, ziel=3),
                  dict(name='4 Reihen bis 200', info='Grössere Zahlen', r=4, max=25, weg=6, unten=True, ziel=3),
                  dict(name='5 Reihen', info='Die grosse Mauer', r=5, max=12, weg=9, unten=True, ziel=3)],
          css=LOGO_CSS + r"""
.zm{display:flex;flex-direction:column;align-items:center;gap:14px;width:100%}
.zm-mauer{display:flex;flex-direction:column;align-items:center;gap:6px}
.zm-reihe{display:flex;gap:6px}
.zm-stein{display:grid;place-items:center;border-radius:10px;background:linear-gradient(180deg,#f3d9b5,#e2b98a);border:2px solid #b98b4e;box-shadow:inset 0 -3px 0 rgba(0,0,0,.12);font:700 26px system-ui,sans-serif;color:#4a3518;padding:0}
.zm-stein.leer{background:#fff;border-style:dashed;color:var(--sky-d);cursor:pointer}
.zm-stein.sel{background:var(--sun);border:3px solid var(--gold-d);box-shadow:0 0 0 3px rgba(214,173,69,.35)}
.zm-stein.ok{background:linear-gradient(180deg,#d9efcf,#b9dca6);border-color:#5f9a4a;color:#2d5a1f}
.zm-stein.falsch{animation:sh .35s;background:#fbe5e2;border-color:var(--no)}
.zm-tasten{display:grid;grid-template-columns:repeat(6,58px);gap:8px}
.zm-tasten button{height:56px;border-radius:14px;background:#fff;border:2px solid var(--ink);box-shadow:0 3px 0 var(--line2);font:700 24px system-ui,sans-serif;padding:0}
.zm-tasten button:active{transform:translateY(2px);box-shadow:none}
.zm-tasten .ok{background:#e7f3df;border-color:#3f6b2e;grid-column:span 2}
.zm-info{background:#fff;border:2px solid var(--line);border-radius:14px;padding:4px 14px;font-size:20px;box-shadow:var(--sch-k)}
.zm-info b{font-weight:400;color:var(--sky-d);font-size:24px}
@media (max-width:420px){.zm-tasten{grid-template-columns:repeat(6,1fr);width:100%}}
""",
          js=r"""
// Mauer als Reihen von unten (0) nach oben: wert[r][i] = wert[r-1][i] + wert[r-1][i+1]
function zmBau(R, max) { var w = [[]]; for (var i = 0; i < R; i++) w[0].push(rnd(1, max)); for (var r = 1; r < R; r++) { w.push([]); for (i = 0; i < R - r; i++) w[r].push(w[r - 1][i] + w[r - 1][i + 1]); } return w; }
function zmLoesbar(w, auf) { // auf[r][i] = bekannt? Schritt für Schritt erschliessen
  var k = auf.map(function (z) { return z.slice(); }), neu = true, R = w.length;
  while (neu) { neu = false;
    for (var r = 1; r < R; r++) for (var i = 0; i < R - r; i++) {
      var a = k[r - 1][i], b = k[r - 1][i + 1], c = k[r][i], n = (a ? 1 : 0) + (b ? 1 : 0) + (c ? 1 : 0);
      if (n === 2) { k[r - 1][i] = k[r - 1][i + 1] = k[r][i] = true; neu = true; }
    } }
  return k.every(function (z) { return z.every(Boolean); });
}
G.play = function (lv, api) {
  var geloest = 0, myRun = RUN;
  var wrap = document.createElement('div'); wrap.className = 'zm'; api.stage.appendChild(wrap);
  function mauer() {
    var R = lv.r, w = zmBau(R, lv.max), auf = w.map(function (z) { return z.map(function () { return true; }); }), plaetze = [];
    for (var r = 0; r < R; r++) for (var i = 0; i < R - r; i++) if (lv.unten || r > 0) plaetze.push([r, i]);
    var weg = 0; shuffle(plaetze).forEach(function (p) { if (weg >= lv.weg) return; auf[p[0]][p[1]] = false; if (zmLoesbar(w, auf)) weg++; else auf[p[0]][p[1]] = true; });
    var sel = null, eingabe = '', offen = weg;
    var s = Math.floor(Math.min(86, (Math.min(window.innerWidth, 700) - 40) / R - 6)); s = Math.max(48, s);
    wrap.innerHTML = '<div class="zm-mauer"></div><div class="zm-tasten">' +
      [1,2,3,4,5,'⌫',6,7,8,9,0].map(function (x) { return '<button data-z="' + x + '">' + x + '</button>'; }).join('') + '<button class="ok" data-z="ok">✓ Prüfen</button></div>';
    var m = wrap.querySelector('.zm-mauer');
    for (r = R - 1; r >= 0; r--) {
      var reihe = document.createElement('div'); reihe.className = 'zm-reihe';
      for (i = 0; i < R - r; i++) {
        var b = document.createElement('button'); b.className = 'zm-stein' + (auf[r][i] ? '' : ' leer'); b.style.width = (s * 1.3) + 'px'; b.style.height = s * .8 + 'px';
        b.dataset.r = r; b.dataset.i = i; b.textContent = auf[r][i] ? w[r][i] : ''; reihe.appendChild(b);
      }
      m.appendChild(reihe);
    }
    function stein(r, i) { return m.querySelector('[data-r="' + r + '"][data-i="' + i + '"]'); }
    function waehle(b) { if (sel) sel.classList.remove('sel'); sel = b; eingabe = ''; if (b) { b.classList.add('sel'); b.textContent = '?'; } }
    function naechster() { var l = m.querySelector('.zm-stein.leer'); waehle(l); }
    naechster();
    api.msg('Welche Zahl fehlt? <small>Unten zwei Steine zusammen = der Stein darüber.</small>');
    m.onclick = function (e) { var b = e.target.closest('.zm-stein.leer'); if (!b || RUN !== myRun) return; if (sel && sel !== b) sel.textContent = ''; waehle(b); };
    wrap.querySelector('.zm-tasten').onclick = function (e) {
      var t = e.target.closest('[data-z]'); if (!t || !sel || RUN !== myRun) return;
      var z = t.dataset.z;
      if (z === '⌫') { eingabe = eingabe.slice(0, -1); sel.textContent = eingabe || '?'; return; }
      if (z !== 'ok') { if (eingabe.length < 4) eingabe += z; sel.textContent = eingabe; tone(560, 0.04, 'sine', 0.06); return; }
      if (!eingabe) return;
      var r2 = +sel.dataset.r, i2 = +sel.dataset.i, ok = +eingabe === w[r2][i2];
      if (ok) {
        sel.classList.remove('leer', 'sel'); sel.classList.add('ok'); sel.textContent = w[r2][i2]; auf[r2][i2] = true; sel = null; offen--;
        api.answer(true);
        if (!offen) {
          geloest++; api.msg('Die Mauer steht!');
          if (geloest >= lv.ziel) { api.later(function () { api.done('Du hast ' + geloest + ' Mauern gebaut!', 1); }, 1400); return; }
          api.later(mauer, 1600); return;
        }
        api.msg('Richtig!'); naechster();
      } else {
        api.answer(false); var b2 = sel; b2.classList.remove('falsch'); void b2.offsetWidth; b2.classList.add('falsch');
        eingabe = ''; b2.textContent = '?';
        var hilf = r2 > 0 && auf[r2 - 1][i2] && auf[r2 - 1][i2 + 1] ? 'Rechne die zwei Steine darunter zusammen.' : 'Tipp: Stein oben minus der Nachbar unten.';
        api.msg('Das stimmt noch nicht. <small>' + hilf + '</small>');
      }
    };
  }
  mauer();
};
""")
