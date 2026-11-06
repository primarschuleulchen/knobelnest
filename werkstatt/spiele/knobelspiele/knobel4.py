# Fünfte Lieferung (Wunsch der Lehrerin): Geheimcode (Farbcode knacken) und Irrgarten (Labyrinth mit der Eule).
# Eigene Spiele im Stil der Klassenkiste. Wird von bauen.py aufgerufen: knobel4.alle(spiel, logo, LOGO_CSS)


def alle(spiel, logo, LOGO_CSS):
    # ================================================================== Geheimcode
    spiel(id='geheimcode', titel='Geheimcode', icon=logo('geheimcode'), fach='Knobelkiste', thema='Logik', stufe='2.–6. Klasse', sort=9, n=0,
          sterne={'modus': 'sammeln', 'pro': 10, 'max': 3, 'proLevel': True, 'proTag': False},
          kurz='Einen versteckten Farbcode aus Perlen knacken.',
          intro='Die Eule hat einen Geheimcode aus farbigen Perlen versteckt. Lege Perlen hin und tippe auf «Prüfen». Die Hinweise zeigen dir, was stimmt. Kannst du den Code knacken?',
          levels=[dict(name='3 Perlen, 4 Farben', info='Jede Perle zeigt, ob sie stimmt', l=3, f=4, dop=False, platz=True, versuche=8, ziel=3),
                  dict(name='3 Perlen, 5 Farben', info='Jede Perle zeigt, ob sie stimmt', l=3, f=5, dop=False, platz=True, versuche=8, ziel=3),
                  dict(name='4 Perlen, 5 Farben', info='Jede Perle zeigt, ob sie stimmt', l=4, f=5, dop=False, platz=True, versuche=8, ziel=3),
                  dict(name='4 Perlen mit Punkten', info='Nur Punkte verraten, wie viel stimmt', l=4, f=6, dop=False, platz=False, versuche=10, ziel=3),
                  dict(name='Profi-Code', info='Punkte, Farben können doppelt vorkommen', l=4, f=6, dop=True, platz=False, versuche=10, ziel=3)],
          css=LOGO_CSS + r"""
.gc{display:flex;flex-direction:column;align-items:center;gap:12px;width:100%}
.gc-info{background:#fff;border:2px solid var(--line);border-radius:14px;padding:4px 14px;font-size:20px;box-shadow:var(--sch-k)}
.gc-info b{font-weight:400;color:var(--sky-d);font-size:24px}
.gc-brett{display:flex;flex-direction:column;gap:6px;background:#f3e3c4;border:4px solid #b98b4e;border-radius:20px;padding:10px 12px;box-shadow:var(--sch);}
.gc-zeile{display:flex;align-items:center;gap:10px;padding:2px 6px;border-radius:12px}
.gc-zeile.jetzt{background:rgba(255,255,255,.75);box-shadow:inset 0 0 0 2px var(--gold)}
.gc-loch{border-radius:50%;background:rgba(120,85,40,.18);box-shadow:inset 0 2px 4px rgba(0,0,0,.2);display:grid;place-items:center;padding:0;border:0;position:relative}
.gc-loch.p::after{content:"";position:absolute;inset:0;border-radius:50%;box-shadow:inset -4px -6px 8px rgba(0,0,0,.18),inset 4px 4px 6px rgba(255,255,255,.55)}
.gc-loch.g{outline:4px solid #5f9a4a;outline-offset:2px}.gc-loch.y{outline:4px dashed #d6ad45;outline-offset:2px}
.gc-hinweis{display:grid;grid-template-columns:repeat(2,14px);gap:4px;margin-left:6px}
.gc-hinweis i{width:14px;height:14px;border-radius:50%;background:rgba(120,85,40,.18)}
.gc-hinweis i.s{background:#5f9a4a;box-shadow:0 0 0 1px #3f6b2e}.gc-hinweis i.f{background:#fff;box-shadow:0 0 0 2px #d6ad45}
.gc-wahl{display:flex;gap:10px;flex-wrap:wrap;justify-content:center}
.gc-wahl button{width:52px;height:52px;border-radius:50%;border:3px solid #fff;box-shadow:0 3px 8px rgba(0,0,0,.2);position:relative;padding:0}
.gc-wahl button::after{content:"";position:absolute;inset:0;border-radius:50%;box-shadow:inset -4px -6px 8px rgba(0,0,0,.18),inset 4px 4px 6px rgba(255,255,255,.55)}
.gc-legende{font-size:17px;color:var(--soft);text-align:center}
.gc-legende i{display:inline-block;width:13px;height:13px;border-radius:50%;vertical-align:-1px;margin:0 3px}
""",
          js=r"""
var GC_FARBEN = ['#e8574c', '#3f8fdc', '#f2c037', '#5fb34a', '#a874d6', '#f08a2c'];
var GC_NAMEN = ['rot', 'blau', 'gelb', 'grün', 'violett', 'orange'];
G.play = function (lv, api) {
  var geloest = 0, runden = 0, myRun = RUN;
  var wrap = document.createElement('div'); wrap.className = 'gc'; api.stage.appendChild(wrap);
  function code() {
    var c = [], farben = range(lv.f);
    for (var i = 0; i < lv.l; i++) { if (lv.dop) c.push(rnd(0, lv.f - 1)); else { var k = rnd(0, farben.length - 1); c.push(farben[k]); farben.splice(k, 1); } }
    return c;
  }
  function wertung(versuch, geheim) {
    var richtig = 0, farbe = 0, ra = [], rb = [], pro = [];
    for (var i = 0; i < geheim.length; i++) { if (versuch[i] === geheim[i]) { richtig++; pro[i] = 'g'; } else { ra.push(geheim[i]); rb.push(i); pro[i] = 'x'; } }
    rb.forEach(function (i) { var k = ra.indexOf(versuch[i]); if (k >= 0) { farbe++; ra.splice(k, 1); pro[i] = 'y'; } });
    return { richtig: richtig, farbe: farbe, pro: pro };
  }
  function runde() {
    var geheim = code(), zeile = 0, lage = [], fertig = false, s = Math.max(22, Math.min(46, Math.floor((window.innerWidth - 120) / (lv.l + 2)), Math.floor((window.innerHeight - 360) / lv.versuche) - 12));
    wrap.innerHTML = '<div class="gc-brett"></div>' +
      '<div class="gc-wahl">' + range(lv.f).map(function (f) { return '<button data-f="' + f + '" style="background:' + GC_FARBEN[f] + '" aria-label="' + GC_NAMEN[f] + '"></button>'; }).join('') + '</div>' +
      '<div class="row"><button class="go alt" data-x="weg">⌫ Zurück</button><button class="go sun" data-x="pruef">✓ Prüfen</button></div>' +
      '<div class="gc-legende">' + (lv.platz ? '<i style="outline:3px solid #5f9a4a"></i> richtige Farbe am richtigen Platz · <i style="outline:3px dashed #d6ad45"></i> Farbe kommt vor, anderer Platz'
        : '<i style="background:#5f9a4a"></i> richtige Farbe am richtigen Platz · <i style="background:#fff;box-shadow:0 0 0 2px #d6ad45"></i> Farbe kommt vor, anderer Platz') + '</div>';
    var brett = wrap.querySelector('.gc-brett');
    for (var z = 0; z < lv.versuche; z++) {
      var o = '<div class="gc-zeile" data-z="' + z + '">';
      for (var i = 0; i < lv.l; i++) o += '<span class="gc-loch" style="width:' + s + 'px;height:' + s + 'px"></span>';
      o += lv.platz ? '' : '<span class="gc-hinweis">' + range(lv.l).map(function () { return '<i></i>'; }).join('') + '</span>';
      brett.insertAdjacentHTML('beforeend', o + '</div>');
    }
    function zeig() {
      var zz = brett.children[zeile]; Array.prototype.forEach.call(brett.children, function (x, k) { x.classList.toggle('jetzt', k === zeile && !fertig); });
      if (!zz) return;
      Array.prototype.forEach.call(zz.querySelectorAll('.gc-loch'), function (l, i) { l.style.background = lage[i] != null ? GC_FARBEN[lage[i]] : ''; l.classList.toggle('p', lage[i] != null); });
    }
    zeig();
    api.msg('Welche Farben hat der Geheimcode?' + (lv.dop ? ' <small>Farben können doppelt vorkommen.</small>' : ''));
    wrap.querySelector('.gc-wahl').onclick = function (e) { var b = e.target.closest('[data-f]'); if (!b || fertig || RUN !== myRun || lage.length >= lv.l) return; lage.push(+b.dataset.f); tone(520 + lage.length * 60, 0.05, 'sine', 0.07); zeig(); };
    wrap.querySelector('[data-x="weg"]').onclick = function () { if (fertig) return; lage.pop(); zeig(); };
    wrap.querySelector('[data-x="pruef"]').onclick = function () {
      if (fertig || RUN !== myRun) return;
      if (lage.length < lv.l) { api.msg('Es braucht ' + lv.l + ' Perlen.'); return; }
      var w = wertung(lage, geheim), zz = brett.children[zeile];
      if (lv.platz) Array.prototype.forEach.call(zz.querySelectorAll('.gc-loch'), function (l, i) { if (w.pro[i] !== 'x') l.classList.add(w.pro[i]); });
      else { var punkte = []; for (var a = 0; a < w.richtig; a++) punkte.push('s'); for (a = 0; a < w.farbe; a++) punkte.push('f'); Array.prototype.forEach.call(zz.querySelectorAll('.gc-hinweis i'), function (p, i) { if (punkte[i]) p.className = punkte[i]; }); }
      tone(440, 0.08, 'triangle', 0.08);
      zeile++; lage = [];
      if (w.richtig === lv.l || zeile >= lv.versuche) {
        fertig = true; var ok = w.richtig === lv.l; runden++; if (ok) geloest++;
        api.answer(ok, true); if (ok) good(); else bad();
        api.msg(ok ? 'Geknackt in ' + zeile + (zeile === 1 ? ' Versuch!' : ' Versuchen!') : 'Der Code war: ' + geheim.map(function (f) { return '<span style="display:inline-block;width:22px;height:22px;border-radius:50%;vertical-align:middle;background:' + GC_FARBEN[f] + '"></span>'; }).join(' '));
        zeig();
        if (geloest >= lv.ziel) { api.later(function () { api.done('Du hast ' + geloest + ' Codes geknackt!', 1); }, 1600); return; }
        api.later(runde, ok ? 1800 : 3200); return;
      }
      zeig();
      api.msg('' + (lv.platz ? 'Schau dir die Ringe an und versuche es nochmal.' : w.richtig + ' am richtigen Platz, ' + w.farbe + ' am falschen Platz.'));
    };
  }
  runde();
};
""")

    # ================================================================== Irrgarten
    spiel(id='irrgarten', titel='Irrgarten', icon=logo('irrgarten'), fach='Knobelkiste', thema='Logik', stufe='1.–6. Klasse', sort=10, n=0,
          sterne={'modus': 'sammeln', 'pro': 10, 'max': 3, 'proLevel': True, 'proTag': False},
          kurz='Die Eule durch das Labyrinth nach Hause führen.',
          intro='Hilf der Eule durch den Irrgarten zu ihrem Haus. Wische in eine Richtung oder tippe auf die Pfeile, dann läuft sie bis zur nächsten Kreuzung.',
          levels=[dict(name='Kleiner Irrgarten', info='5 × 5 Wege', w=5, h=5, nuesse=0, dunkel=False, ziel=3),
                  dict(name='Mittlerer Irrgarten', info='8 × 8 Wege', w=8, h=8, nuesse=0, dunkel=False, ziel=3),
                  dict(name='Nüsse sammeln', info='10 × 10, zuerst 2 Nüsse holen', w=10, h=10, nuesse=2, dunkel=False, ziel=3),
                  dict(name='Grosser Irrgarten', info='12 × 12, 3 Nüsse', w=12, h=12, nuesse=3, dunkel=False, ziel=3),
                  dict(name='Im Dunkeln', info='Nur rund um die Eule ist es hell', w=10, h=10, nuesse=2, dunkel=True, ziel=3)],
          css=LOGO_CSS + r"""
.ig{display:flex;flex-direction:column;align-items:center;gap:12px;width:100%}
.ig-info{display:flex;gap:10px;flex-wrap:wrap;justify-content:center}
.ig-info span{background:#fff;border:2px solid var(--line);border-radius:14px;padding:4px 14px;font-size:20px;box-shadow:var(--sch-k)}
.ig-info b{font-weight:400;color:var(--sky-d);font-size:24px}
.ig-feld{position:relative;background:#e9f1e3;border:4px solid #9cc28a;border-radius:16px;box-shadow:var(--sch);touch-action:none}
.ig-feld svg{display:block}
.ig-eule,.ig-ding{position:absolute;display:grid;place-items:center;line-height:1}
.ig-eule{transition:transform .12s linear;z-index:3;filter:drop-shadow(0 3px 3px rgba(0,0,0,.25))}
.ig-ding{z-index:2}
.ig-ding.weg{opacity:0;transition:opacity .3s}
.ig-nacht{position:absolute;inset:0;border-radius:12px;pointer-events:none;z-index:4}
.ig-spiel{display:flex;gap:24px;align-items:center;justify-content:center;flex-wrap:wrap}
.ig-tasten{display:grid;grid-template-columns:repeat(3,64px);gap:8px}
.ig-tasten button{height:60px;border-radius:16px;background:#fff;border:2px solid var(--ink);box-shadow:0 4px 0 var(--line2);font:700 26px system-ui,sans-serif;padding:0;touch-action:manipulation}
.ig-tasten button:active{transform:translateY(3px);box-shadow:none}
""",
          js=r"""
// Wände: wand[y][x] = Bitmaske der offenen Seiten (1 oben, 2 rechts, 4 unten, 8 links)
var IG_D = [[0, -1, 1, 4], [1, 0, 2, 8], [0, 1, 4, 1], [-1, 0, 8, 2]]; // dx, dy, Bit hier, Bit dort
function igBau(W, H) {
  var o = [], gesehen = [], stapel = [[0, 0]];
  for (var y = 0; y < H; y++) { o.push([]); gesehen.push([]); for (var x = 0; x < W; x++) { o[y].push(0); gesehen[y].push(false); } }
  gesehen[0][0] = true;
  while (stapel.length) {
    var c = stapel[stapel.length - 1], frei = IG_D.filter(function (d) { var nx = c[0] + d[0], ny = c[1] + d[1]; return nx >= 0 && ny >= 0 && nx < W && ny < H && !gesehen[ny][nx]; });
    if (!frei.length) { stapel.pop(); continue; }
    var d = frei[rnd(0, frei.length - 1)], nx = c[0] + d[0], ny = c[1] + d[1];
    o[c[1]][c[0]] |= d[2]; o[ny][nx] |= d[3]; gesehen[ny][nx] = true; stapel.push([nx, ny]);
  }
  return o;
}
G.play = function (lv, api) {
  var geloest = 0, myRun = RUN;
  var wrap = document.createElement('div'); wrap.className = 'ig'; api.stage.appendChild(wrap);
  function runde() {
    var W = lv.w, H = lv.h, o = igBau(W, H), eu = { x: 0, y: 0 }, haus = { x: W - 1, y: H - 1 }, laeuft = false, fertig = false, schritte = 0;
    var freie = []; for (var y = 0; y < H; y++) for (var x = 0; x < W; x++) if ((x + y > 2) && !(x === haus.x && y === haus.y)) freie.push([x, y]);
    var nuesse = pick(freie, lv.nuesse).map(function (p) { return { x: p[0], y: p[1], da: true }; });
    var breit = window.innerWidth > 760, s = Math.floor(Math.min(58, (Math.min(window.innerWidth, 1000) - (breit ? 340 : 60)) / W, (window.innerHeight - (breit ? 250 : 400)) / H)); s = Math.max(20, s);
    var B = W * s, Hh = H * s;
    var svg = '<svg width="' + B + '" height="' + Hh + '" viewBox="0 0 ' + B + ' ' + Hh + '" aria-hidden="true"><g stroke="#7a5634" stroke-width="' + Math.max(3, Math.round(s / 8)) + '" stroke-linecap="round">';
    for (y = 0; y < H; y++) for (x = 0; x < W; x++) {
      var px = x * s, py = y * s;
      if (!(o[y][x] & 1)) svg += '<line x1="' + px + '" y1="' + py + '" x2="' + (px + s) + '" y2="' + py + '"/>';
      if (!(o[y][x] & 8)) svg += '<line x1="' + px + '" y1="' + py + '" x2="' + px + '" y2="' + (py + s) + '"/>';
      if (y === H - 1) svg += '<line x1="' + px + '" y1="' + (py + s) + '" x2="' + (px + s) + '" y2="' + (py + s) + '"/>';
      if (x === W - 1) svg += '<line x1="' + (px + s) + '" y1="' + py + '" x2="' + (px + s) + '" y2="' + (py + s) + '"/>';
    }
    svg += '</g></svg>';
    var fs = Math.round(s * .72);
    wrap.innerHTML = (lv.nuesse ? '<div class="ig-info"><span>Nüsse <b class="nz">0</b> von ' + lv.nuesse + '</span></div>' : '') +
      '<div class="ig-spiel"><div class="ig-feld" style="width:' + (B + 16) + 'px;height:' + (Hh + 16) + 'px;padding:4px">' + svg +
      nuesse.map(function (n, i) { return '<span class="ig-ding" data-n="' + i + '" style="left:' + (4 + n.x * s) + 'px;top:' + (4 + n.y * s) + 'px;width:' + s + 'px;height:' + s + 'px;font-size:' + fs + 'px">' + ik('nuss', fs) + '</span>'; }).join('') +
      '<span class="ig-ding haus" style="left:' + (4 + haus.x * s) + 'px;top:' + (4 + haus.y * s) + 'px;width:' + s + 'px;height:' + s + 'px;font-size:' + fs + 'px">' + ik('haus', fs) + '</span>' +
      '<span class="ig-eule" style="left:4px;top:4px;width:' + s + 'px;height:' + s + 'px;font-size:' + fs + 'px">' + ik('eule', fs) + '</span>' + (lv.dunkel ? '<div class="ig-nacht"></div>' : '') + '</div>' +
      '<div class="ig-tasten"><span></span><button data-r="0" aria-label="Nach oben">▲</button><span></span><button data-r="3" aria-label="Nach links">◀</button><button data-r="2" aria-label="Nach unten">▼</button><button data-r="1" aria-label="Nach rechts">▶</button></div></div>';
    var feld = wrap.querySelector('.ig-feld'), eule = wrap.querySelector('.ig-eule'), nacht = wrap.querySelector('.ig-nacht'), nz = wrap.querySelector('.nz');
    function zeig() {
      eule.style.transform = 'translate(' + eu.x * s + 'px,' + eu.y * s + 'px)';
      if (nacht) { var cx = 4 + eu.x * s + s / 2, cy = 4 + eu.y * s + s / 2, r = s * 2.3; nacht.style.background = 'radial-gradient(circle ' + r + 'px at ' + cx + 'px ' + cy + 'px,transparent 0,transparent ' + (r * .55) + 'px,rgba(20,30,50,.985) ' + r + 'px)'; }
    }
    zeig();
    api.msg('' + (lv.nuesse ? 'Hol zuerst alle Nüsse, dann geht es nach Hause!' : 'Bring die Eule nach Hause!'));
    function kann(r) { return !!(o[eu.y][eu.x] & IG_D[r][2]); }
    function geh(r) {
      if (laeuft || fertig || RUN !== myRun || !kann(r)) { if (!kann(r) && !laeuft && !fertig) tone(180, 0.08, 'triangle', 0.06); return; }
      laeuft = true;
      (function schritt() {
        if (RUN !== myRun) return;
        eu.x += IG_D[r][0]; eu.y += IG_D[r][1]; schritte++; zeig(); tone(600, 0.025, 'sine', 0.04);
        nuesse.forEach(function (n, i) { if (n.da && n.x === eu.x && n.y === eu.y) { n.da = false; feld.querySelector('[data-n="' + i + '"]').classList.add('weg'); tone(880, 0.1); if (nz) nz.textContent = nuesse.filter(function (q) { return !q.da; }).length; } });
        if (eu.x === haus.x && eu.y === haus.y) {
          if (nuesse.some(function (n) { return n.da; })) api.msg('Es fehlen noch Nüsse!');
          else { laeuft = false; ziel(); return; }
        }
        // weiterlaufen, solange es nur einen Weg nach vorn gibt (keine Kreuzung, keine Sackgasse)
        var rueck = (r + 2) % 4, wege = [0, 1, 2, 3].filter(function (q) { return q !== rueck && kann(q); });
        if (wege.length === 1 && wege[0] === r && !nuesse.some(function (n) { return n.da && n.x === eu.x && n.y === eu.y; })) { api.later(schritt, 110); return; }
        if (wege.length === 1) { r = wege[0]; api.later(schritt, 110); return; }
        laeuft = false;
      })();
    }
    function ziel() {
      fertig = true; geloest++; good(); api.answer(true, true);
      api.msg('Die Eule ist zu Hause!');
      if (geloest >= lv.ziel) { api.later(function () { api.done('Du hast ' + geloest + ' Irrgärten geschafft!', 1); }, 1400); return; }
      api.later(runde, 1600);
    }
    wrap.querySelector('.ig-tasten').addEventListener('pointerdown', function (e) { var b = e.target.closest('[data-r]'); if (!b) return; e.preventDefault(); geh(+b.dataset.r); });
    var wx = null, wy = null;
    feld.addEventListener('pointerdown', function (e) { wx = e.clientX; wy = e.clientY; });
    feld.addEventListener('pointerup', function (e) {
      if (wx == null) return; var dx = e.clientX - wx, dy = e.clientY - wy; wx = null;
      if (Math.max(Math.abs(dx), Math.abs(dy)) < 20) return;
      geh(Math.abs(dx) > Math.abs(dy) ? (dx > 0 ? 1 : 3) : (dy > 0 ? 2 : 0));
    });
    function taste(e) {
      if (RUN !== myRun) { document.removeEventListener('keydown', taste); return; }
      var m = { ArrowUp: 0, ArrowRight: 1, ArrowDown: 2, ArrowLeft: 3 }[e.key]; if (m != null) { e.preventDefault(); geh(m); }
    }
    document.removeEventListener('keydown', window.__igKey || function () {}); window.__igKey = taste;
    document.addEventListener('keydown', taste);
  }
  runde();
};
""")
