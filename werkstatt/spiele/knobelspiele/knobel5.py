# Sechste Lieferung: Spiegelbild (Muster spiegeln), Waage (Gewichte, Mathematik), Zahlen-Pfad (Weg von 1 bis zum Ende).
# Eigene Spiele im Stil der Klassenkiste, ohne Emojis. Wird von bauen.py aufgerufen: knobel5.alle(spiel, logo, LOGO_CSS)


def alle(spiel, logo, LOGO_CSS):
    # ================================================================== Spiegelbild
    spiel(id='spiegelbild', titel='Spiegelbild', icon=logo('spiegelbild'), fach='Knobelkiste', thema='Geometrie', stufe='1.–6. Klasse', sort=11, n=0,
          sterne={'modus': 'sammeln', 'pro': 10, 'max': 3, 'proLevel': True, 'proTag': False},
          kurz='Ein Muster an der goldenen Linie spiegeln.',
          intro='Auf einer Seite der goldenen Linie ist ein Muster. Male auf der anderen Seite das Spiegelbild – so, als ob die Linie ein Spiegel wäre. Dann tippe auf «Prüfen».',
          levels=[dict(name='Spiegel senkrecht', info='Kleines Feld, eine Farbe', n=4, dir='v', farben=1, k=4, ziel=5),
                  dict(name='Grösseres Muster', info='Senkrechter Spiegel, eine Farbe', n=6, dir='v', farben=1, k=7, ziel=5),
                  dict(name='Spiegel waagrecht', info='Oben und unten spiegeln', n=6, dir='h', farben=1, k=7, ziel=5),
                  dict(name='Zwei Farben', info='Achte auch auf die Farben', n=6, dir='mix', farben=2, k=8, ziel=5),
                  dict(name='Profi-Spiegel', info='Grosses Feld, zwei Farben', n=8, dir='mix', farben=2, k=12, ziel=5)],
          css=LOGO_CSS + r"""
.sp{display:flex;flex-direction:column;align-items:center;gap:14px;width:100%}
.sp-feld{position:relative;display:grid;gap:3px;padding:8px;background:#fff;border:3px solid var(--line);border-radius:18px;box-shadow:var(--sch)}
.sp-feld button{border:0;border-radius:7px;background:#eef3f7;padding:0;transition:background .15s,transform .1s}
.sp-feld button.vor{cursor:default}
.sp-feld button.c1{background:#3f8fdc}.sp-feld button.c2{background:#e8574c}
.sp-feld button.vor.c1{background:#3f8fdc}.sp-feld button.vor.c2{background:#e8574c}
.sp-feld button.vor:not(.c1):not(.c2){background:#f5f1e8}
.sp-feld button:not(.vor):active{transform:scale(.9)}
.sp-feld button.falsch{box-shadow:inset 0 0 0 3px #e8574c;animation:spWack .4s}
@keyframes spWack{25%{transform:translateX(-3px)}75%{transform:translateX(3px)}}
.sp-linie{position:absolute;background:var(--gold);border-radius:4px;box-shadow:0 0 0 2px #fff,0 0 10px rgba(214,173,69,.7);pointer-events:none}
.sp-wahl{display:flex;gap:12px;align-items:center}
.sp-wahl button{width:52px;height:52px;border-radius:50%;border:3px solid #fff;box-shadow:0 3px 8px rgba(0,0,0,.2)}
.sp-wahl button.an{outline:4px solid var(--ink);outline-offset:2px}
""",
          js=r"""
G.play = function (lv, api) {
  var N = lv.n, geloest = 0, myRun = RUN;
  var wrap = document.createElement('div'); wrap.className = 'sp'; api.stage.appendChild(wrap);
  function bild() {
    var dir = lv.dir === 'mix' ? pick(['v', 'h'], 1)[0] : lv.dir, H = N / 2, feld = [], soll = [], farbe = 1, fertig = false, fehler = 0;
    // Vorlage: Seite links (senkrecht) oder oben (waagrecht), Spiegelbild auf der anderen Seite
    var vorlage = function (y, x) { return dir === 'v' ? x < H : y < H; };
    var spiegel = function (y, x) { return dir === 'v' ? y * N + (N - 1 - x) : (N - 1 - y) * N + x; };
    for (var i = 0; i < N * N; i++) { feld.push(0); soll.push(0); }
    var frei = []; for (var y = 0; y < N; y++) for (var x = 0; x < N; x++) if (vorlage(y, x)) frei.push(y * N + x);
    pick(frei, lv.k).forEach(function (k) { var c = lv.farben > 1 ? rnd(1, 2) : 1; feld[k] = c; soll[spiegel(Math.floor(k / N), k % N)] = c; });
    var s = Math.floor(Math.min(58, (Math.min(window.innerWidth, 700) - 60) / N - 3, (window.innerHeight - 340) / N - 3)); s = Math.max(28, s);
    wrap.innerHTML = '<div class="sp-feld" style="grid-template-columns:repeat(' + N + ',' + s + 'px);grid-auto-rows:' + s + 'px"></div>' +
      (lv.farben > 1 ? '<div class="sp-wahl"><span>Farbe:</span><button class="an" data-c="1" style="background:#3f8fdc" aria-label="blau"></button><button data-c="2" style="background:#e8574c" aria-label="rot"></button></div>' : '') +
      '<div class="row"><button class="go alt" data-x="leer">Alles löschen</button><button class="go sun" data-x="pruef">✓ Prüfen</button></div>';
    var f = wrap.querySelector('.sp-feld');
    for (i = 0; i < N * N; i++) {
      var yy = Math.floor(i / N), xx = i % N, v = vorlage(yy, xx);
      f.insertAdjacentHTML('beforeend', '<button data-k="' + i + '" class="' + (v ? 'vor' : '') + (v && feld[i] ? ' c' + feld[i] : '') + '"' + (v ? ' disabled aria-hidden="true"' : ' aria-label="Feld"') + '></button>');
    }
    var mitte = 8 + H * (s + 3) - 3;
    f.insertAdjacentHTML('beforeend', dir === 'v' ? '<div class="sp-linie" style="left:' + (mitte - 1) + 'px;top:4px;bottom:4px;width:5px"></div>' : '<div class="sp-linie" style="top:' + (mitte - 1) + 'px;left:4px;right:4px;height:5px"></div>');
    api.msg(dir === 'v' ? 'Male das Spiegelbild auf der rechten Seite.' : 'Male das Spiegelbild auf der unteren Seite.');
    function eigen() { var o = []; for (var i = 0; i < N * N; i++) if (!vorlage(Math.floor(i / N), i % N)) o.push(i); return o; }
    f.onclick = function (e) {
      var b = e.target.closest('button'); if (!b || b.disabled || fertig || RUN !== myRun) return;
      var k = +b.dataset.k; b.classList.remove('falsch');
      feld[k] = feld[k] === farbe ? 0 : farbe; b.classList.remove('c1', 'c2'); if (feld[k]) b.classList.add('c' + feld[k]);
      tone(feld[k] ? 600 : 420, 0.05, 'sine', 0.06);
    };
    var wahl = wrap.querySelector('.sp-wahl');
    if (wahl) wahl.onclick = function (e) { var b = e.target.closest('[data-c]'); if (!b) return; farbe = +b.dataset.c; Array.prototype.forEach.call(wahl.querySelectorAll('[data-c]'), function (x) { x.classList.toggle('an', x === b); }); };
    wrap.querySelector('[data-x="leer"]').onclick = function () { if (fertig) return; eigen().forEach(function (k) { feld[k] = 0; var b = f.children[k]; b.classList.remove('c1', 'c2', 'falsch'); }); };
    wrap.querySelector('[data-x="pruef"]').onclick = function () {
      if (fertig || RUN !== myRun) return;
      var falsch = eigen().filter(function (k) { return feld[k] !== soll[k]; });
      if (!falsch.length) {
        fertig = true; geloest++; good(); api.answer(true, true);
        api.msg(fehler ? 'Geschafft! Das Spiegelbild stimmt.' : 'Perfekt gespiegelt!');
        if (geloest >= lv.ziel) { api.later(function () { api.done('Du hast ' + geloest + ' Spiegelbilder gemalt!', 1); }, 1400); return; }
        api.later(bild, 1500); return;
      }
      fehler++; bad(); api.answer(false, true);
      falsch.forEach(function (k) { var b = f.children[k]; b.classList.remove('falsch'); void b.offsetWidth; b.classList.add('falsch'); });
      api.msg('Noch nicht ganz. Die rot umrandeten Felder stimmen noch nicht.');
    };
  }
  bild();
};
""")

    # ================================================================== Waage
    spiel(id='waage', titel='Waage', icon=logo('waage'), fach='Mathematik', thema='Rechnen', stufe='1.–6. Klasse', sort=12, n=0,
          sterne={'modus': 'sammeln', 'pro': 10, 'max': 3, 'proLevel': True, 'proTag': False},
          kurz='Gewichte auflegen, bis die Waage gerade ist.',
          intro='Die Waage ist schief! Lege Gewichte auf die rechte Schale, bis beide Seiten gleich schwer sind. In den höheren Stufen findest du heraus, wie schwer eine Kugel oder ein Würfel ist.',
          levels=[dict(name='Gleich schwer bis 10', info='Gewichte auflegen', art='auf', max=10, ziel=8),
                  dict(name='Gleich schwer bis 20', info='Gewichte auflegen', art='auf', max=20, ziel=8),
                  dict(name='Gleich schwer bis 100', info='Grosse Gewichte', art='auf', max=100, ziel=8),
                  dict(name='Wie schwer ist die Kugel?', info='Eine Waage, die gerade ist', art='kugel', ziel=8),
                  dict(name='Zwei Waagen', info='Zuerst die eine, dann die andere Waage lesen', art='zwei', ziel=8)],
          css=LOGO_CSS + r"""
.wg{display:flex;flex-direction:column;align-items:center;gap:12px;width:100%}
.wg-waagen{display:flex;gap:10px;flex-wrap:wrap;justify-content:center}
.wg svg{max-width:100%;height:auto;overflow:visible}
.wg-balken{transition:transform .6s cubic-bezier(.3,1.4,.5,1)}
.wg-schale{transition:transform .6s cubic-bezier(.3,1.4,.5,1)}
.wg-vorrat{display:flex;gap:10px;flex-wrap:wrap;justify-content:center;min-height:62px;background:#f3e3c4;border:3px solid #b98b4e;border-radius:18px;padding:10px 14px;box-shadow:var(--sch-k)}
.wg-vorrat button{border:0;padding:0;background:none;transition:transform .12s,opacity .2s}
.wg-vorrat button:active{transform:scale(.92)}
.wg-vorrat button.weg{opacity:.18;pointer-events:none}
.wg-wahl{display:flex;gap:12px;flex-wrap:wrap;justify-content:center}
.wg-wahl button{min-width:76px;height:60px;font-size:30px;border-radius:16px;border:3px solid var(--ink);background:#fff;box-shadow:var(--sch-k)}
.wg-wahl button.ok{background:#e3f1dc;border-color:#5f9a4a}.wg-wahl button.nein{background:#fbe5e2;border-color:#c8574e}
.wg-zahl{font-size:20px;color:var(--soft)}
""",
          js=r"""
// Gewicht als Messing-Klotz mit Zahl; Kugel (orange) und Würfel (violett) mit Fragezeichen
function wgKlotz(w, x, y) { var b = 24 + String(w).length * 9, h = 26; return '<g transform="translate(' + (x - b / 2) + ' ' + (y - h) + ')"><path d="M3 ' + h + 'L7 4h' + (b - 14) + 'L' + (b - 3) + ' ' + h + 'z" fill="#d9b25a" stroke="#9c7428" stroke-width="2" stroke-linejoin="round"/><rect x="' + (b / 2 - 5) + '" y="0" width="10" height="5" rx="2" fill="#9c7428"/><text x="' + b / 2 + '" y="' + (h - 6) + '" font-size="15" text-anchor="middle" fill="#3a2a0e">' + w + '</text></g>'; }
function wgBreit(w) { return 26 + String(w).length * 9; }
function wgKugel(x, y) { return '<g><circle cx="' + x + '" cy="' + (y - 14) + '" r="14" fill="#f08a2c" stroke="#b5631c" stroke-width="2"/><circle cx="' + (x - 5) + '" cy="' + (y - 19) + '" r="4" fill="#ffc68a"/><text x="' + x + '" y="' + (y - 8) + '" font-size="15" text-anchor="middle" fill="#fff">?</text></g>'; }
function wgWuerfel(x, y) { return '<g><rect x="' + (x - 13) + '" y="' + (y - 26) + '" width="26" height="26" rx="4" fill="#a874d6" stroke="#71489a" stroke-width="2"/><text x="' + x + '" y="' + (y - 7) + '" font-size="15" text-anchor="middle" fill="#fff">?</text></g>'; }
// Dinge in einer Schale nebeneinander (zwei Reihen, wenn es viele sind)
function wgInhalt(dinge, cx, by) {
  var breit = dinge.map(function (d) { return d.t === 'w' ? wgBreit(d.w) : 30; }), reihen = [[]], rb = [0];
  dinge.forEach(function (d, i) { if (rb[rb.length - 1] + breit[i] > 120 && reihen[reihen.length - 1].length) { reihen.push([]); rb.push(0); } reihen[reihen.length - 1].push(i); rb[rb.length - 1] += breit[i] + 3; });
  var o = '';
  reihen.forEach(function (r, ri) { var x = cx - rb[ri] / 2, y = by - ri * 29; r.forEach(function (i) { var d = dinge[i], m = x + breit[i] / 2; o += d.t === 'w' ? wgKlotz(d.w, m, y) : d.t === 'k' ? wgKugel(m, y) : wgWuerfel(m, y); x += breit[i] + 3; }); });
  return o;
}
function wgWert(dinge, kugel, wuerfel) { return dinge.reduce(function (s, d) { return s + (d.t === 'w' ? d.w : d.t === 'k' ? kugel : wuerfel); }, 0); }
// Waage zeichnen: links/rechts = Listen von Dingen; neig = Winkel in Grad (positiv = rechts tiefer)
function wgSvg(links, rechts, neig, breite) {
  var W = breite || 380, cx = W / 2, arm = W / 2 - 70, z = WG_ZOOM, o = '<svg viewBox="0 0 ' + W + ' 250" width="' + Math.round(W * z) + '" height="' + Math.round(250 * z) + '" aria-hidden="true">';
  o += '<path d="M' + (cx - 46) + ' 240h92l-14-12h-64z" fill="#b98b4e"/><rect x="' + (cx - 6) + '" y="60" width="12" height="172" rx="4" fill="#c99d5c" stroke="#9c7428" stroke-width="2"/>';
  o += '<g class="wg-balken" style="transform-origin:' + cx + 'px 62px;transform:rotate(' + neig + 'deg)"><rect x="' + (cx - arm - 8) + '" y="56" width="' + (2 * arm + 16) + '" height="12" rx="6" fill="#d9b25a" stroke="#9c7428" stroke-width="2"/></g>';
  o += '<circle cx="' + cx + '" cy="62" r="9" fill="#f2c037" stroke="#9c7428" stroke-width="2"/>';
  [[-1, links], [1, rechts]].forEach(function (p) {
    var r = neig * Math.PI / 180, ex = cx + p[0] * arm * Math.cos(r), ey = 62 + p[0] * arm * Math.sin(r);
    o += '<g class="wg-schale" style="transform:translate(' + (ex - (cx + p[0] * arm)) + 'px,' + (ey - 62) + 'px)">' +
      '<path d="M' + (cx + p[0] * arm) + ' 62L' + (cx + p[0] * arm - 62) + ' 170M' + (cx + p[0] * arm) + ' 62L' + (cx + p[0] * arm + 62) + ' 170" stroke="#9c7428" stroke-width="2"/>' +
      wgInhalt(p[1], cx + p[0] * arm, 168) +
      '<path d="M' + (cx + p[0] * arm - 70) + ' 168h140c-6 16-28 24-70 24s-64-8-70-24z" fill="#e8c77a" stroke="#9c7428" stroke-width="2"/></g>';
  });
  return o + '</svg>';
}
var WG_ZOOM = 1;
function wgNeig(l, r) { var d = r - l; return d === 0 ? 0 : Math.max(-14, Math.min(14, d * 1.6 + (d > 0 ? 3 : -3))); }

G.play = function (lv, api) {
  var geschafft = 0, runden = 0, myRun = RUN;
  var wrap = document.createElement('div'); wrap.className = 'wg'; api.stage.appendChild(wrap);
  // Waage so gross wie möglich zeichnen (WG_ZOOM vergrössert die ganze Zeichnung)
  var W = 380; WG_ZOOM = Math.max(.8, Math.min(1.6, (window.innerWidth - 40) / W, (window.innerHeight - (lv.art === 'auf' ? 380 : 330)) / 250));
  function weiter(ok) {
    runden++; if (ok) geschafft++;
    if (geschafft >= lv.ziel) { api.later(function () { api.done('Du hast ' + geschafft + ' Waagen geschafft!', runden ? geschafft / runden : 1); }, 1400); return; }
    api.later(aufgabe, ok ? 1500 : 2800);
  }
  function auflegen() {
    // Vorrat: eine passende Auswahl plus Ablenker; links ein oder zwei Gewichte
    var grosse = lv.max <= 10 ? [1, 2, 3, 4, 5] : lv.max <= 20 ? [1, 2, 3, 4, 5, 6, 8, 10] : [1, 2, 5, 10, 20, 25, 50];
    var vorrat, ziel, tries = 0;
    do {
      vorrat = []; for (var i = 0; i < (lv.max <= 10 ? 4 : 6); i++) vorrat.push(pick(grosse, 1)[0]);
      var teil = pick(range(vorrat.length), rnd(2, Math.min(3, vorrat.length)));
      ziel = teil.reduce(function (s, i) { return s + vorrat[i]; }, 0); tries++;
    } while ((ziel > lv.max || ziel < (lv.max <= 10 ? 3 : lv.max <= 20 ? 8 : 25)) && tries < 200);
    vorrat.sort(function (a, b) { return a - b; });
    var links = [], rest = ziel;
    if (ziel > 6 && Math.random() < .6) { var a = rnd(1, ziel - 1); links = [{ t: 'w', w: a }, { t: 'w', w: ziel - a }]; } else links = [{ t: 'w', w: ziel }];
    var rechts = [], fertig = false;
    wrap.innerHTML = '<div class="wg-waagen"></div><div class="wg-vorrat">' + vorrat.map(function (w, i) { return '<button data-i="' + i + '" aria-label="Gewicht ' + w + '"><svg width="' + Math.round((wgBreit(w) + 4) * 1.6) + '" height="48" viewBox="' + (-wgBreit(w) / 2 - 2) + ' -28 ' + (wgBreit(w) + 4) + ' 30">' + wgKlotz(w, 0, 0) + '</svg></button>'; }).join('') + '</div>' +
      '<div class="wg-zahl">Tippe auf ein Gewicht, um es auf die Waage zu legen. Tippe auf die Schale, um es wieder wegzunehmen.</div>';
    var waagen = wrap.querySelector('.wg-waagen'), vr = wrap.querySelector('.wg-vorrat');
    function male() {
      var l = wgWert(links), r = rechts.reduce(function (s, i) { return s + vorrat[i]; }, 0);
      waagen.innerHTML = wgSvg(links, rechts.map(function (i) { return { t: 'w', w: vorrat[i] }; }), wgNeig(l, r), W);
      Array.prototype.forEach.call(vr.children, function (b, i) { b.classList.toggle('weg', rechts.indexOf(i) >= 0); });
      return [l, r];
    }
    male();
    api.msg('Mach die Waage gerade!');
    vr.onclick = function (e) {
      var b = e.target.closest('[data-i]'); if (!b || fertig || RUN !== myRun) return;
      rechts.push(+b.dataset.i); tone(480, 0.06, 'triangle', 0.08);
      var lr = male();
      if (lr[0] === lr[1]) { fertig = true; good(); api.answer(true, true); api.msg('Gerade! Links und rechts sind je ' + lr[0] + ' schwer.'); weiter(true); }
      else api.msg(lr[1] < lr[0] ? 'Rechts ist noch zu leicht.' : 'Jetzt ist rechts zu schwer. Nimm etwas weg.');
    };
    waagen.onclick = function () { if (fertig || !rechts.length) return; rechts.pop(); tone(360, 0.06, 'triangle', 0.08); var lr = male(); api.msg(lr[1] < lr[0] ? 'Rechts ist zu leicht.' : 'Rechts ist zu schwer.'); };
  }
  function wahlKnoepfe(loes, frage, erklaer) {
    var opts = [loes]; while (opts.length < 4) { var x = loes + rnd(-4, 4); if (x > 0 && opts.indexOf(x) < 0) opts.push(x); }
    var w = document.createElement('div'); w.className = 'wg-wahl';
    w.innerHTML = shuffle(opts).map(function (x) { return '<button data-w="' + x + '">' + x + '</button>'; }).join('');
    wrap.appendChild(w); api.msg(frage);
    var fertig = false;
    w.onclick = function (e) {
      var b = e.target.closest('[data-w]'); if (!b || fertig || RUN !== myRun) return; fertig = true;
      var ok = +b.dataset.w === loes; b.classList.add(ok ? 'ok' : 'nein');
      if (!ok) Array.prototype.forEach.call(w.children, function (x) { if (+x.dataset.w === loes) x.classList.add('ok'); });
      if (ok) good(); else bad(); api.answer(ok, true);
      api.msg(ok ? 'Richtig! ' + erklaer : 'Es ist ' + loes + '. ' + erklaer);
      weiter(ok);
    };
  }
  function kugel() {
    // m Kugeln (+ Gewicht a) = Gewichte b, die Waage ist gerade
    var x = rnd(2, 9), m = rnd(1, 3), a = m === 1 ? rnd(0, 6) : rnd(0, 4), b = m * x + a;
    var links = range(m).map(function () { return { t: 'k' }; }); if (a) links.push({ t: 'w', w: a });
    var rechts = [], rest = b; while (rest > 0) { var g = Math.min(rest, pick([2, 3, 4, 5, 10], 1)[0]); rechts.push({ t: 'w', w: g }); rest -= g; }
    wrap.innerHTML = '<div class="wg-waagen">' + wgSvg(links, rechts, 0, W) + '</div>';
    wahlKnoepfe(x, 'Die Waage ist gerade. Wie schwer ist eine Kugel?',
      (m > 1 ? m + ' Kugeln' : 'Die Kugel') + (a ? ' und ' + a : '') + ' sind zusammen ' + b + ' schwer' + (a ? ', also ' + (m > 1 ? 'die Kugeln ' : 'die Kugel ') + (b - a) : '') + (m > 1 ? ', eine Kugel ' + x : '') + '.');
  }
  function zwei() {
    // Waage 1: Kugel = k Würfel. Waage 2: Kugel + Würfel = Gewicht. Gesucht: der Würfel
    var c = rnd(1, 6), k = rnd(2, 3), ball = k * c, s2 = ball + c;
    var w1r = range(k).map(function () { return { t: 'q' }; });
    var w2r = [], rest = s2; while (rest > 0) { var g = Math.min(rest, pick([2, 3, 5, 10], 1)[0]); w2r.push({ t: 'w', w: g }); rest -= g; }
    var B = 330, nz = window.innerWidth > 760 ? 2 : 1; WG_ZOOM = Math.max(.7, Math.min(1.3, (window.innerWidth - 50) / nz / B, (window.innerHeight - 330) / nz / 250 * (nz === 1 ? 1 : 2)));
    wrap.innerHTML = '<div class="wg-waagen">' + wgSvg([{ t: 'k' }], w1r, 0, B) + wgSvg([{ t: 'k' }, { t: 'q' }], w2r, 0, B) + '</div>';
    wahlKnoepfe(c, 'Beide Waagen sind gerade. Wie schwer ist ein Würfel?',
      'Eine Kugel ist so schwer wie ' + k + ' Würfel. Kugel und Würfel sind also ' + (k + 1) + ' Würfel = ' + s2 + '. Ein Würfel ist ' + c + '.');
  }
  function aufgabe() { if (RUN !== myRun) return; if (lv.art === 'auf') auflegen(); else if (lv.art === 'kugel') kugel(); else zwei(); }
  aufgabe();
};
""")

    # ================================================================== Zahlen-Pfad
    spiel(id='zahlen-pfad', titel='Zahlen-Pfad', icon=logo('zahlen-pfad'), fach='Knobelkiste', thema='Logik', stufe='1.–6. Klasse', sort=13, n=0,
          sterne={'modus': 'sammeln', 'pro': 10, 'max': 3, 'proLevel': True, 'proTag': False},
          kurz='Einen Weg von 1 bis zur letzten Zahl durch alle Felder ziehen.',
          intro='Ziehe mit dem Finger einen Weg von der 1 bis zur grössten Zahl. Der Weg geht nur nach oben, unten, links oder rechts und muss durch jedes Feld genau einmal. Die Zahlen, die schon stehen, müssen am richtigen Platz auf dem Weg liegen.',
          levels=[dict(name='3 × 3', info='Von 1 bis 9', r=3, h=1, ziel=4),
                  dict(name='4 × 4 mit Hilfen', info='Von 1 bis 16, viele Zahlen stehen schon', r=4, h=4, ziel=3),
                  dict(name='4 × 4', info='Von 1 bis 16, wenige Hilfen', r=4, h=1, ziel=3),
                  dict(name='5 × 5', info='Von 1 bis 25', r=5, h=4, ziel=3),
                  dict(name='6 × 6', info='Von 1 bis 36, für Profis', r=6, h=5, ziel=3)],
          css=LOGO_CSS + r"""
.zp{display:flex;flex-direction:column;align-items:center;gap:14px;width:100%}
.zp-feld{position:relative;display:grid;gap:4px;padding:8px;background:#fff;border:3px solid var(--line);border-radius:18px;box-shadow:var(--sch);touch-action:none;user-select:none;-webkit-user-select:none}
.zp-feld .z{position:relative;z-index:2;display:grid;place-items:center;border-radius:10px;background:#eef3f7;font-size:22px;color:var(--soft);transition:background .15s}
.zp-feld .z.fest{background:#fbf3dc;color:var(--ink);box-shadow:inset 0 0 0 2px var(--gold)}
.zp-feld .z.weg{background:rgba(220,240,253,.45);color:#2c5a82}
.zp-feld .z.fest.weg{background:rgba(246,227,168,.6);color:var(--ink)}
.zp-feld .z.ende{box-shadow:inset 0 0 0 3px #3f8fdc}
.zp-feld .z.wack{animation:spWack2 .35s}
@keyframes spWack2{25%{transform:translateX(-4px)}75%{transform:translateX(4px)}}
.zp-feld svg{position:absolute;inset:0;z-index:1;pointer-events:none}
""",
          js=r"""
// Weg durch alle Felder (zufällig, mit Vorliebe für Felder mit wenig freien Nachbarn)
function zpWeg(R) {
  for (var v = 0; v < 400; v++) {
    var start = rnd(0, R * R - 1), weg = [start], drin = {}; drin[start] = 1;
    var nb = function (k) { var y = Math.floor(k / R), x = k % R, o = []; if (y > 0) o.push(k - R); if (y < R - 1) o.push(k + R); if (x > 0) o.push(k - 1); if (x < R - 1) o.push(k + 1); return o; };
    while (weg.length < R * R) {
      var frei = nb(weg[weg.length - 1]).filter(function (k) { return !drin[k]; }); if (!frei.length) break;
      var gr = frei.map(function (k) { return nb(k).filter(function (j) { return !drin[j]; }).length; }), m = Math.min.apply(null, gr);
      var w = shuffle(frei.filter(function (k, i) { return gr[i] === m || Math.random() < .15; }))[0];
      weg.push(w); drin[w] = 1;
    }
    if (weg.length === R * R) return weg;
  }
  return null;
}
G.play = function (lv, api) {
  var R = lv.r, N = R * R, geloest = 0, myRun = RUN;
  var wrap = document.createElement('div'); wrap.className = 'zp'; api.stage.appendChild(wrap);
  function raetsel() {
    var loes = zpWeg(R), fest = {}, pfad = [], fertig = false;
    fest[loes[0]] = 1; fest[loes[N - 1]] = N;
    pick(range(N - 2).map(function (i) { return i + 1; }), lv.h).forEach(function (i) { fest[loes[i]] = i + 1; });
    var feldVon = {}; Object.keys(fest).forEach(function (k) { feldVon[fest[k]] = +k; });
    pfad = [loes[0]];
    var s = Math.floor(Math.min(72, (Math.min(window.innerWidth, 640) - 50) / R - 4, (window.innerHeight - 300) / R - 4)); s = Math.max(40, s);
    wrap.innerHTML = '<div class="zp-feld" style="grid-template-columns:repeat(' + R + ',' + s + 'px);grid-auto-rows:' + s + 'px"></div>' +
      '<div class="row"><button class="go alt" data-x="zur">Einen Schritt zurück</button><button class="go alt" data-x="neu">Nochmal von vorn</button></div>';
    var f = wrap.querySelector('.zp-feld');
    for (var k = 0; k < N; k++) f.insertAdjacentHTML('beforeend', '<div class="z' + (fest[k] ? ' fest' : '') + '" data-k="' + k + '"></div>');
    f.insertAdjacentHTML('beforeend', '<svg width="100%" height="100%"></svg>');
    var svg = f.querySelector('svg');
    function mitte(k) { return [8 + (k % R) * (s + 4) + s / 2, 8 + Math.floor(k / R) * (s + 4) + s / 2]; }
    function male() {
      var ist = {}; pfad.forEach(function (k, i) { ist[k] = i + 1; });
      Array.prototype.forEach.call(f.querySelectorAll('.z'), function (z) { var k = +z.dataset.k; z.textContent = fest[k] || ist[k] || ''; z.classList.toggle('weg', !!ist[k]); z.classList.toggle('ende', k === pfad[pfad.length - 1] && !fertig); });
      svg.innerHTML = pfad.length > 1 ? '<polyline points="' + pfad.map(function (k) { return mitte(k).join(','); }).join(' ') + '" fill="none" stroke="#7cb8e6" stroke-width="' + Math.round(s * .3) + '" stroke-linecap="round" stroke-linejoin="round" opacity=".8"/>' : '';
    }
    function nachbar(a, b) { var ya = Math.floor(a / R), xa = a % R, yb = Math.floor(b / R), xb = b % R; return Math.abs(ya - yb) + Math.abs(xa - xb) === 1; }
    function wack(k, t) { var z = f.children[k]; z.classList.remove('wack'); void z.offsetWidth; z.classList.add('wack'); if (t) api.msg(t); }
    function tippe(k) {
      if (fertig || RUN !== myRun) return;
      var i = pfad.indexOf(k);
      if (i >= 0) { if (i < pfad.length - 1) { pfad = pfad.slice(0, Math.max(1, i + 1)); male(); } return; }
      var ende = pfad[pfad.length - 1], nr = pfad.length + 1;
      if (!nachbar(ende, k)) return;
      if (fest[k] && fest[k] !== nr) { wack(k, 'Hier muss die ' + fest[k] + ' stehen, nicht die ' + nr + '.'); return; }
      if (!fest[k] && feldVon[nr] != null) { wack(feldVon[nr], 'Die ' + nr + ' steht schon an einem anderen Platz.'); return; }
      pfad.push(k); tone(420 + nr * 12, 0.05, 'sine', 0.06); male();
      if (pfad.length === N) {
        fertig = true; geloest++; good(); api.answer(true, true); male();
        api.msg('Der Weg ist fertig!');
        if (geloest >= lv.ziel) { api.later(function () { api.done('Du hast ' + geloest + ' Zahlen-Pfade gefunden!', 1); }, 1400); return; }
        api.later(raetsel, 1500);
      } else api.msg('Weiter mit der ' + (nr + 1) + '.');
    }
    // Ziehen mit Finger oder Maus, Tippen geht auch
    var zieht = false;
    function unter(e) { var el = document.elementFromPoint(e.clientX, e.clientY); el = el && el.closest ? el.closest('.z') : null; return el && f.contains(el) ? +el.dataset.k : null; }
    f.onpointerdown = function (e) { var k = unter(e); if (k == null) return; zieht = true; tippe(k); e.preventDefault(); };
    f.onpointermove = function (e) { if (!zieht) return; var k = unter(e); if (k != null && k !== pfad[pfad.length - 1] && pfad.indexOf(k) < 0) tippe(k); };
    window.addEventListener('pointerup', function () { zieht = false; });
    wrap.querySelector('[data-x="zur"]').onclick = function () { if (fertig || pfad.length < 2) return; pfad.pop(); male(); };
    wrap.querySelector('[data-x="neu"]').onclick = function () { if (fertig) return; pfad = [loes[0]]; male(); api.msg('Nochmal von vorn. Starte bei der 1.'); };
    male();
    api.msg('Ziehe den Weg von der 1 bis zur ' + N + '.');
  }
  raetsel();
};
""")
