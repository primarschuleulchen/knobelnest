# Siebte Lieferung: Muster-Reihe (was kommt als Nächstes?), Brüche (Mathematik), Lichtstrahl (Spiegel drehen).
# Eigene Spiele im Stil der Klassenkiste, ohne Emojis. Wird von bauen.py aufgerufen: knobel6.alle(spiel, logo, LOGO_CSS)


def alle(spiel, logo, LOGO_CSS):
    # ================================================================== Muster-Reihe
    spiel(id='muster-reihe', titel='Muster-Reihe', icon=logo('muster-reihe'), fach='Knobelkiste', thema='Logik', stufe='1.–6. Klasse', sort=14, n=0,
          sterne={'modus': 'sammeln', 'pro': 10, 'max': 3, 'proLevel': True, 'proTag': False},
          kurz='Erkennen, wie das Muster weitergeht.',
          intro='Schau dir die Reihe genau an. Welche Regel steckt dahinter? Tippe auf das Bild, das an den leeren Platz gehört.',
          levels=[dict(name='Farben-Muster', info='Die Farben wiederholen sich', art='farbe', ziel=10),
                  dict(name='Formen-Muster', info='Die Formen wiederholen sich', art='form', ziel=10),
                  dict(name='Form und Farbe', info='Beides ändert sich', art='beides', ziel=10),
                  dict(name='Drehen', info='Die Form dreht sich weiter', art='drehen', ziel=10),
                  dict(name='Lücke finden', info='Alles gemischt, die Lücke ist irgendwo', art='mix', ziel=10)],
          css=LOGO_CSS + r"""
.mr{display:flex;flex-direction:column;align-items:center;gap:18px;width:100%}
.mr-reihe{display:flex;gap:8px;flex-wrap:wrap;justify-content:center;background:#fff;border:3px solid var(--line);border-radius:20px;padding:14px;box-shadow:var(--sch)}
.mr-reihe .f{display:grid;place-items:center;border-radius:14px;background:#f4f7fa}
.mr-reihe .f.luecke{background:#fbf3dc;box-shadow:inset 0 0 0 3px var(--gold);border-radius:14px}
.mr-reihe .f.luecke b{font-weight:400;font-size:34px;color:var(--gold)}
.mr-wahl{display:flex;gap:14px;flex-wrap:wrap;justify-content:center}
.mr-wahl button{display:grid;place-items:center;background:#fff;border:3px solid var(--ink);border-radius:18px;box-shadow:var(--sch-k);padding:6px;transition:transform .12s}
.mr-wahl button:active{transform:scale(.94)}
.mr-wahl button.ok{background:#e3f1dc;border-color:#5f9a4a}.mr-wahl button.nein{background:#fbe5e2;border-color:#c8574e}
""",
          js=r"""
var MR_FARBEN = ['#e8574c', '#3f8fdc', '#f2c037', '#5fb34a', '#a874d6'];
var MR_FORMEN = ['kreis', 'quadrat', 'dreieck', 'stern', 'herz', 'raute'];
function mrForm(d, s) {
  var c = MR_FARBEN[d.c], o = '<svg width="' + s + '" height="' + s + '" viewBox="0 0 40 40" aria-hidden="true"><g transform="rotate(' + (d.r || 0) + ' 20 20)">';
  var st = ' fill="' + c + '" stroke="rgba(0,0,0,.25)" stroke-width="1.5" stroke-linejoin="round"';
  if (d.f === 'kreis') o += '<circle cx="20" cy="20" r="14"' + st + '/>';
  else if (d.f === 'quadrat') o += '<rect x="7" y="7" width="26" height="26" rx="4"' + st + '/>';
  else if (d.f === 'dreieck') o += '<path d="M20 5L35 33H5z"' + st + '/>';
  else if (d.f === 'stern') o += '<path d="M20 4l4.4 9.6 10.4 1.1-7.8 7 2.2 10.3L20 26.8 10.8 32l2.2-10.3-7.8-7 10.4-1.1z"' + st + '/>';
  else if (d.f === 'herz') o += '<path d="M20 34S6 25.5 6 15.5A7.5 7.5 0 0 1 20 11a7.5 7.5 0 0 1 14 4.5C34 25.5 20 34 20 34z"' + st + '/>';
  else if (d.f === 'raute') o += '<path d="M20 4l14 16-14 16L6 20z"' + st + '/>';
  else if (d.f === 'pfeil') o += '<path d="M20 5l11 12h-7v17h-8V17H9z"' + st + '/>';
  return o + '</g></svg>';
}
function mrKey(d) { return d.f + '|' + d.c + '|' + ((d.r || 0) % 360); }
// Ein Muster-Block (z. B. AB, ABC, AAB, ABB) für eine Eigenschaft
function mrBlock(werte) { var t = pick(['AB', 'ABC', 'AAB', 'ABB', 'AABB', 'ABCD'].filter(function (x) { return new Set(x).size <= werte.length; }), 1)[0], m = {}, w = shuffle(werte.slice()); return t.split('').map(function (ch) { if (m[ch] == null) m[ch] = w[Object.keys(m).length]; return m[ch]; }); }
function mrReihe(art) {
  var L = 8, r = [], i;
  if (art === 'mix') art = pick(['farbe', 'form', 'beides', 'drehen'], 1)[0];
  if (art === 'farbe') { var bf = mrBlock(range(5)), f = pick(MR_FORMEN, 1)[0]; for (i = 0; i < L; i++) r.push({ f: f, c: bf[i % bf.length] }); }
  else if (art === 'form') { var bo = mrBlock(MR_FORMEN), c = rnd(0, 4); for (i = 0; i < L; i++) r.push({ f: bo[i % bo.length], c: c }); }
  else if (art === 'beides') {
    var b1, b2; do { b1 = mrBlock(MR_FORMEN); b2 = mrBlock(range(5)); } while (b1.length === b2.length);
    L = 9; for (i = 0; i < L; i++) r.push({ f: b1[i % b1.length], c: b2[i % b2.length] });
  } else {
    var schritt = pick([45, 90, -90, 135], 1)[0], fo = pick(['pfeil', 'dreieck'], 1)[0], cc = mrBlock(range(5)).slice(0, pick([1, 2], 1)[0]), r0 = pick([0, 90, 180, 270], 1)[0];
    for (i = 0; i < L; i++) r.push({ f: fo, c: cc[i % cc.length], r: ((r0 + i * schritt) % 360 + 360) % 360 });
  }
  return r;
}
G.play = function (lv, api) {
  var richtig = 0, runden = 0, myRun = RUN;
  var wrap = document.createElement('div'); wrap.className = 'mr'; api.stage.appendChild(wrap);
  function aufgabe() {
    if (RUN !== myRun) return;
    var r = mrReihe(lv.art), L = r.length, lk = lv.art === 'mix' ? rnd(2, L - 1) : L - 1, loes = r[lk], fertig = false;
    // Ablenker: eine Eigenschaft anders als die Lösung
    var opts = [loes], tries = 0;
    while (opts.length < 4 && tries++ < 100) {
      var d = { f: loes.f, c: loes.c, r: loes.r || 0 }, w = rnd(0, 2);
      var dreht = loes.f === 'pfeil' || loes.f === 'dreieck';
      if (w === 0 && !dreht) d.f = pick(MR_FORMEN, 1)[0]; else if (w === 1 || (w === 2 && !dreht)) d.c = rnd(0, 4); else d.r = ((d.r + pick([45, 90, 180, 270], 1)[0]) % 360);
      if (!dreht) d.r = 0;
      if (opts.every(function (o) { return mrKey(o) !== mrKey(d); })) opts.push(d);
    }
    var s = Math.max(40, Math.min(64, Math.floor((Math.min(window.innerWidth, 860) - 60) / L) - 8));
    wrap.innerHTML = '<div class="mr-reihe">' + r.map(function (d, i) { return i === lk ? '<span class="f luecke" style="width:' + s + 'px;height:' + s + 'px"><b>?</b></span>' : '<span class="f" style="width:' + s + 'px;height:' + s + 'px">' + mrForm(d, s - 8) + '</span>'; }).join('') + '</div>' +
      '<div class="mr-wahl">' + shuffle(opts).map(function (d) { return '<button data-k="' + mrKey(d) + '" aria-label="Antwort">' + mrForm(d, 66) + '</button>'; }).join('') + '</div>';
    api.msg(lk === L - 1 ? 'Was kommt als Nächstes?' : 'Was gehört in die Lücke?');
    wrap.querySelector('.mr-wahl').onclick = function (e) {
      var b = e.target.closest('[data-k]'); if (!b || fertig || RUN !== myRun) return; fertig = true;
      var ok = b.dataset.k === mrKey(loes); runden++; if (ok) richtig++;
      b.classList.add(ok ? 'ok' : 'nein');
      if (!ok) Array.prototype.forEach.call(this.children, function (x) { if (x.dataset.k === mrKey(loes)) x.classList.add('ok'); });
      var lu = wrap.querySelector('.luecke'); lu.innerHTML = mrForm(loes, s - 8); lu.classList.remove('luecke');
      if (ok) good(); else bad(); api.answer(ok, true);
      api.msg(ok ? pick(['Richtig!', 'Genau!', 'Super!'], 1)[0] : 'Schau nochmal: Das grün umrandete Bild passt.');
      if (runden >= lv.ziel) { api.later(function () { api.done('Du hast ' + richtig + ' von ' + runden + ' Mustern erkannt!', richtig / runden); }, 1400); return; }
      api.later(aufgabe, ok ? 1200 : 2400);
    };
  }
  aufgabe();
};
""")

    # ================================================================== Brüche
    spiel(id='brueche', titel='Brüche', icon=logo('brueche'), fach='Mathematik', thema='Brüche', stufe='3.–6. Klasse', sort=15, n=0,
          sterne={'modus': 'sammeln', 'pro': 10, 'max': 3, 'proLevel': True, 'proTag': False},
          kurz='Brüche an Pizza und Streifen erkennen, malen und vergleichen.',
          intro='Ein Bruch zeigt, wie viele gleich grosse Teile von einem Ganzen gemeint sind. Unten steht, in wie viele Teile das Ganze geteilt ist, oben, wie viele davon gefärbt sind.',
          levels=[dict(name='Brüche erkennen', info='Welcher Bruch ist gefärbt?', art='lesen', ziel=10),
                  dict(name='Brüche malen', info='Färbe den Bruch ein', art='malen', ziel=10),
                  dict(name='Brüche vergleichen', info='Mit Bildern: grösser, kleiner oder gleich?', art='vergl', ziel=10),
                  dict(name='Gleich viel', info='Welche Brüche sind gleich gross?', art='gleich', ziel=10),
                  dict(name='Profi-Vergleich', info='Ohne Bilder vergleichen', art='profi', ziel=10)],
          css=LOGO_CSS + r"""
.br{display:flex;flex-direction:column;align-items:center;gap:16px;width:100%}
.br-bilder{display:flex;gap:22px;flex-wrap:wrap;justify-content:center;align-items:center}
.br-bilder svg{overflow:visible}
.br-bilder path,.br-bilder rect{transition:fill .2s}
.br-bilder [data-t]{cursor:pointer}
.bz{display:inline-flex;flex-direction:column;align-items:center;line-height:1;font-size:32px;vertical-align:middle;margin:0 4px}
.bz i{font-style:normal;padding:0 4px}.bz i:first-child{border-bottom:3px solid currentColor;padding-bottom:3px;margin-bottom:3px}
.br-gross .bz{font-size:44px}
.br-wahl{display:flex;gap:14px;flex-wrap:wrap;justify-content:center}
.br-wahl button{min-width:88px;min-height:84px;background:#fff;border:3px solid var(--ink);border-radius:18px;box-shadow:var(--sch-k);font-size:30px;padding:6px 12px}
.br-wahl button.ok{background:#e3f1dc;border-color:#5f9a4a}.br-wahl button.nein{background:#fbe5e2;border-color:#c8574e}
.br-wahl .zeichen{font-size:44px;min-width:96px}
.br-paar{display:flex;align-items:center;gap:18px;font-size:30px}
.br-paar .platz{width:64px;height:64px;border:3px dashed var(--gold);border-radius:14px;display:grid;place-items:center;font-size:40px;color:var(--gold)}
""",
          js=r"""
function brBz(z, n) { return '<span class="bz"><i>' + z + '</i><i>' + n + '</i></span>'; }
function ggt(a, b) { return b ? ggt(b, a % b) : a; }
// Pizza (Kreis in n Stücke) oder Streifen; voll = Anzahl gefärbter Teile; malen = Teile antippbar
function brBild(n, voll, s, malen, farbe) {
  var o = '<svg width="' + s + '" height="' + s + '" viewBox="0 0 100 100" aria-hidden="true">', f = farbe || '#f2a63a', i;
  {
    o += '<circle cx="50" cy="50" r="46" fill="#fbf3dc" stroke="#b98b4e" stroke-width="3"/>';
    for (i = 0; i < n; i++) {
      var a0 = (i / n) * 2 * Math.PI - Math.PI / 2, a1 = ((i + 1) / n) * 2 * Math.PI - Math.PI / 2, gr = (a1 - a0) > Math.PI ? 1 : 0;
      var d = n === 1 ? 'M50 4a46 46 0 1 1 -.1 0z' : 'M50 50L' + (50 + 44 * Math.cos(a0)).toFixed(2) + ' ' + (50 + 44 * Math.sin(a0)).toFixed(2) + 'A44 44 0 ' + gr + ' 1 ' + (50 + 44 * Math.cos(a1)).toFixed(2) + ' ' + (50 + 44 * Math.sin(a1)).toFixed(2) + 'z';
      o += '<path d="' + d + '" fill="' + (i < voll ? f : '#fff8e8') + '" stroke="#b98b4e" stroke-width="2.5" stroke-linejoin="round"' + (malen ? ' data-t="' + i + '"' : '') + '/>';
    }
  }
  return o + '</svg>';
}
function brStreifen(n, voll, w, malen, farbe) {
  var f = farbe || '#3f8fdc', h = 56, o = '<svg width="' + w + '" height="' + h + '" viewBox="0 0 ' + w + ' ' + h + '" aria-hidden="true">', tw = (w - 6) / n;
  for (var i = 0; i < n; i++) o += '<rect x="' + (3 + i * tw) + '" y="3" width="' + tw + '" height="' + (h - 6) + '" fill="' + (i < voll ? f : '#eef5fb') + '" stroke="#2c5a82" stroke-width="2.5"' + (malen ? ' data-t="' + i + '"' : '') + '/>';
  return o + '</svg>';
}
function brZeig(n, voll, s, malen, farbe, streifen) { return streifen ? brStreifen(n, voll, Math.round(s * 2.4), malen, farbe) : brBild(n, voll, s, malen, farbe); }
G.play = function (lv, api) {
  var richtig = 0, runden = 0, myRun = RUN;
  var wrap = document.createElement('div'); wrap.className = 'br'; api.stage.appendChild(wrap);
  var S = Math.max(120, Math.min(200, window.innerHeight - 440, (window.innerWidth - 80) / 2.6));
  function fertig(ok, text) {
    runden++; if (ok) richtig++; if (ok) good(); else bad(); api.answer(ok, true); api.msg(text);
    if (runden >= lv.ziel) { api.later(function () { api.done('Du hast ' + richtig + ' von ' + runden + ' Aufgaben richtig!', richtig / runden); }, 1500); return; }
    api.later(aufgabe, ok ? 1300 : 2600);
  }
  function wahl(opts, loes, cls, erkl) {
    var w = document.createElement('div'); w.className = 'br-wahl'; var zu = false;
    w.innerHTML = opts.map(function (o) { return '<button class="' + (cls || '') + '" data-w="' + o[0] + '">' + o[1] + '</button>'; }).join('');
    wrap.appendChild(w);
    w.onclick = function (e) {
      var b = e.target.closest('[data-w]'); if (!b || zu || RUN !== myRun) return; zu = true;
      var ok = b.dataset.w === String(loes); b.classList.add(ok ? 'ok' : 'nein');
      if (!ok) Array.prototype.forEach.call(w.children, function (x) { if (x.dataset.w === String(loes)) x.classList.add('ok'); });
      fertig(ok, ok ? pick(['Richtig!', 'Genau!', 'Super!'], 1)[0] + (erkl ? ' ' + erkl : '') : (erkl || 'Schau dir die Lösung an.'));
    };
  }
  function lesen() {
    var n = pick([2, 3, 4, 5, 6, 8, 10], 1)[0], z = rnd(1, n - 1), str = n > 8 || Math.random() < .35;
    wrap.innerHTML = '<div class="br-bilder">' + brZeig(n, z, S, false, null, str) + '</div>';
    var opts = [[z + '/' + n, brBz(z, n)]], k = 0;
    var kand = [[n - z, n], [z, n + 1], [z + 1, n], [z, n - 1], [n, z], [z - 1, n]].filter(function (x) { return x[0] > 0 && x[1] > 1 && x[0] < x[1]; });
    shuffle(kand).forEach(function (x) { var key = x[0] + '/' + x[1]; if (opts.length < 4 && opts.every(function (o) { return o[0] !== key; })) opts.push([key, brBz(x[0], x[1])]); });
    api.msg('Welcher Bruch ist gefärbt?');
    wahl(shuffle(opts), z + '/' + n, '', 'Es sind ' + z + ' von ' + n + ' gleichen Teilen gefärbt.');
  }
  function malen() {
    var n = pick([2, 3, 4, 5, 6, 8, 10], 1)[0], z = rnd(1, n - 1), str = n > 8 || Math.random() < .4, an = [], zu = false;
    for (var i = 0; i < n; i++) an.push(false);
    api.msg('Färbe ' + brBz(z, n) + ' ein. Tippe auf die Teile.');
    function male() {
      var box = wrap.querySelector('.br-bilder'); box.innerHTML = brZeig(n, 0, S, true, null, str);
      Array.prototype.forEach.call(box.querySelectorAll('[data-t]'), function (t) { if (an[+t.dataset.t]) t.setAttribute('fill', str ? '#3f8fdc' : '#f2a63a'); });
    }
    wrap.innerHTML = '<div class="br-bilder"></div><div class="row"><button class="go sun" data-x="pruef">✓ Prüfen</button></div>';
    male();
    wrap.querySelector('.br-bilder').onclick = function (e) { var t = e.target.closest('[data-t]'); if (!t || zu) return; an[+t.dataset.t] = !an[+t.dataset.t]; tone(an[+t.dataset.t] ? 600 : 420, 0.05, 'sine', 0.06); male(); };
    wrap.querySelector('[data-x="pruef"]').onclick = function () {
      if (zu || RUN !== myRun) return; var k = an.filter(Boolean).length; zu = true;
      fertig(k === z, k === z ? 'Richtig! ' + z + ' von ' + n + ' Teilen sind gefärbt.' : 'Du hast ' + k + ' Teile gefärbt. Für ' + z + '/' + n + ' braucht es ' + z + ' von ' + n + ' Teilen.');
    };
  }
  function vergl(bilder) {
    var a, b, c, d, t;
    do {
      t = rnd(0, 2);
      if (t === 0) { b = d = pick([3, 4, 5, 6, 8, 10], 1)[0]; a = rnd(1, b - 1); c = rnd(1, d - 1); }
      else if (t === 1) { a = c = rnd(1, 3); b = rnd(a + 1, 10); d = rnd(c + 1, 10); }
      else { b = pick([2, 3, 4, 5, 6], 1)[0]; var m = pick([2, 3], 1)[0]; d = b * m; a = rnd(1, b - 1); c = Math.random() < .4 ? a * m : rnd(1, d - 1); }
    } while (!bilder && t === 0 && Math.random() < .5);
    var l = a / b, r = c / d, loes = Math.abs(l - r) < 1e-9 ? '=' : l > r ? '>' : '<';
    wrap.innerHTML = '<div class="br-bilder br-gross">' + (bilder ? '<div>' + brZeig(b, a, S * .8, false, '#f2a63a', false) + '</div>' : '') + brBz(a, b) + '<span style="font-size:40px;color:var(--gold)">?</span>' + brBz(c, d) + (bilder ? '<div>' + brZeig(d, c, S * .8, false, '#3f8fdc', false) + '</div>' : '') + '</div>';
    api.msg('Welches Zeichen passt?');
    wahl([['<', '&lt;'], ['=', '='], ['>', '&gt;']], loes, 'zeichen', a + '/' + b + ' ' + (loes === '<' ? 'ist kleiner als' : loes === '>' ? 'ist grösser als' : 'ist gleich gross wie') + ' ' + c + '/' + d + '.');
  }
  function gleich() {
    var b = pick([2, 3, 4, 5], 1)[0], a = rnd(1, b - 1), m = pick([2, 3, 4], 1)[0], d = b * m, loes = a * m;
    wrap.innerHTML = '<div class="br-bilder">' + brZeig(b, a, S * .85, false, '#f2a63a', true) + brZeig(d, loes, S * .85, false, '#3f8fdc', true) + '</div>' +
      '<div class="br-paar">' + brBz(a, b) + '<span>=</span><span class="bz"><i><span class="platz">?</span></i><i>' + d + '</i></span></div>';
    var opts = [loes]; shuffle(range(d + 1).slice(1)).forEach(function (x) { if (opts.length < 4 && opts.indexOf(x) < 0) opts.push(x); });
    var NAME = { 4: 'Viertel', 6: 'Sechstel', 8: 'Achtel', 9: 'Neuntel', 10: 'Zehntel', 12: 'Zwölftel', 15: 'Fünfzehntel', 16: 'Sechzehntel', 20: 'Zwanzigstel' };
    api.msg('Wie viele ' + (NAME[d] || d + '-tel') + ' sind gleich viel wie ' + brBz(a, b) + '?');
    wahl(shuffle(opts).map(function (x) { return [x, x]; }), loes, '', a + '/' + b + ' = ' + loes + '/' + d + ': Jeder Teil wird in ' + m + ' kleinere Teile geschnitten.');
  }
  function aufgabe() {
    if (RUN !== myRun) return;
    if (lv.art === 'lesen') lesen(); else if (lv.art === 'malen') malen(); else if (lv.art === 'vergl') vergl(true); else if (lv.art === 'gleich') gleich(); else vergl(false);
  }
  aufgabe();
};
""")

    # ================================================================== Lichtstrahl
    spiel(id='lichtstrahl', titel='Lichtstrahl', icon=logo('lichtstrahl'), fach='Knobelkiste', thema='Logik', stufe='2.–6. Klasse', sort=16, n=0,
          sterne={'modus': 'sammeln', 'pro': 10, 'max': 3, 'proLevel': True, 'proTag': False},
          kurz='Spiegel drehen, bis das Licht den Kristall trifft.',
          intro='Die Lampe leuchtet nach rechts. Tippe auf einen Spiegel, dann dreht er sich und lenkt das Licht in eine andere Richtung. Bringst du den Lichtstrahl zum Kristall?',
          levels=[dict(name='Zwei Spiegel', info='Kleines Feld', n=4, m=3, min=2, waende=0, ziel=5),
                  dict(name='Drei Spiegel', info='Etwas grösser', n=5, m=5, min=3, waende=0, ziel=5),
                  dict(name='Mit Steinen', info='Steine halten das Licht auf', n=5, m=6, min=3, waende=3, ziel=4),
                  dict(name='Viele Spiegel', info='Nicht jeder Spiegel wird gebraucht', n=6, m=9, min=4, waende=3, ziel=4),
                  dict(name='Profi-Licht', info='Grosses Feld, langer Weg', n=7, m=12, min=6, waende=5, ziel=3)],
          css=LOGO_CSS + r"""
.ls{display:flex;flex-direction:column;align-items:center;gap:12px;width:100%}
.ls svg{max-width:100%;height:auto;touch-action:manipulation}
.ls [data-k]{cursor:pointer}
.ls .spg{transition:transform .25s}
.ls-info{font-size:20px;color:var(--soft)}
""",
          js=r"""
// Lichtweg berechnen: Start links in Zeile r, nach rechts; '/' und '\' lenken um, 'w' hält auf
function lsWeg(N, feld, r) {
  var y = r, x = -1, dy = 0, dx = 1, pfad = [[y, x]], spg = [], guard = 0;
  while (guard++ < 400) {
    y += dy; x += dx;
    if (y < 0 || x < 0 || y >= N || x >= N) { pfad.push([y, x]); return { pfad: pfad, aus: [y, x], spg: spg }; }
    pfad.push([y, x]);
    var c = feld[y * N + x];
    if (c === 'w') return { pfad: pfad, aus: null, spg: spg };
    if (c === '/') { var t = dy; dy = -dx; dx = -t; spg.push(y * N + x); }
    else if (c === '\\') { var u = dy; dy = dx; dx = u; spg.push(y * N + x); }
  }
  return { pfad: pfad, aus: null, spg: spg };
}
function lsBau(lv) {
  var N = lv.n;
  for (var v = 0; v < 3000; v++) {
    var feld = [], r = rnd(0, N - 1), i;
    for (i = 0; i < N * N; i++) feld.push('');
    var frei = range(N * N).filter(function (k) { return !(Math.floor(k / N) === r && k % N === 0); });
    var sp = pick(frei, lv.m); sp.forEach(function (k) { feld[k] = Math.random() < .5 ? '/' : '\\'; });
    pick(frei.filter(function (k) { return !feld[k]; }), lv.waende).forEach(function (k) { feld[k] = 'w'; });
    var w = lsWeg(N, feld, r);
    if (!w.aus || w.spg.length < lv.min) continue;
    if (w.aus[1] < 0 && w.aus[0] === r) continue;
    // Spiegel auf dem Weg zum Teil verdrehen, so dass das Rätsel nicht schon gelöst ist
    var loes = feld.slice(), start = feld.slice();
    var drehen = pick(w.spg, Math.max(1, Math.ceil(w.spg.length * .6)));
    drehen.forEach(function (k) { start[k] = start[k] === '/' ? '\\' : '/'; });
    pick(sp.filter(function (k) { return w.spg.indexOf(k) < 0; }), Math.floor(sp.length / 3)).forEach(function (k) { start[k] = start[k] === '/' ? '\\' : '/'; });
    var w2 = lsWeg(N, start, r);
    if (w2.aus && w2.aus[0] === w.aus[0] && w2.aus[1] === w.aus[1]) continue;
    return { N: N, r: r, feld: start, ziel: w.aus };
  }
  return null;
}
G.play = function (lv, api) {
  var geloest = 0, myRun = RUN;
  var wrap = document.createElement('div'); wrap.className = 'ls'; api.stage.appendChild(wrap);
  function raetsel() {
    if (RUN !== myRun) return;
    var P = lsBau(lv), N = P.N, feld = P.feld, zuege = 0, fertig = false;
    var s = Math.floor(Math.min(76, (Math.min(window.innerWidth, 760) - 40) / (N + 2), (window.innerHeight - 290) / (N + 2))); s = Math.max(36, s);
    var W = (N + 2) * s;
    wrap.innerHTML = '<svg width="' + W + '" height="' + W + '" viewBox="0 0 ' + W + ' ' + W + '"></svg><div class="ls-info">Drehungen: <b class="zz">0</b></div><div class="row"><button class="go alt" data-x="neu">Nochmal von vorn</button></div>';
    var svg = wrap.querySelector('svg'), zz = wrap.querySelector('.zz'), start = feld.slice();
    function mx(x) { return (x + 1) * s + s / 2; }
    function male() {
      var w = lsWeg(N, feld, P.r), getroffen = w.aus && w.aus[0] === P.ziel[0] && w.aus[1] === P.ziel[1];
      var o = '<rect x="' + (s - 6) + '" y="' + (s - 6) + '" width="' + (N * s + 12) + '" height="' + (N * s + 12) + '" rx="16" fill="#1d3557"/>';
      for (var y = 0; y < N; y++) for (var x = 0; x < N; x++) {
        var k = y * N + x, c = feld[k], X = (x + 1) * s, Y = (y + 1) * s;
        o += '<rect x="' + (X + 2) + '" y="' + (Y + 2) + '" width="' + (s - 4) + '" height="' + (s - 4) + '" rx="8" fill="#26456e"' + (c === '/' || c === '\\' ? ' data-k="' + k + '"' : '') + '/>';
        if (c === 'w') o += '<path d="M' + (X + s * .18) + ' ' + (Y + s * .78) + 'c-1-' + (s * .3) + ' ' + (s * .12) + '-' + (s * .5) + ' ' + (s * .36) + '-' + (s * .56) + 's' + (s * .42) + ' ' + (s * .08) + ' ' + (s * .46) + ' ' + (s * .34) + 's-' + (s * .06) + ' ' + (s * .22) + '-' + (s * .3) + ' ' + (s * .22) + 'z" fill="#8a96a3" stroke="#5f6b78" stroke-width="2"/>';
        if (c === '/' || c === '\\') {
          var a = c === '/' ? [X + s * .2, Y + s * .8, X + s * .8, Y + s * .2] : [X + s * .2, Y + s * .2, X + s * .8, Y + s * .8];
          o += '<line x1="' + a[0] + '" y1="' + a[1] + '" x2="' + a[2] + '" y2="' + a[3] + '" stroke="#dfe8f1" stroke-width="' + Math.round(s * .14) + '" stroke-linecap="round" data-k="' + k + '"/>' +
               '<line x1="' + a[0] + '" y1="' + a[1] + '" x2="' + a[2] + '" y2="' + a[3] + '" stroke="#9fb3c6" stroke-width="' + Math.round(s * .05) + '" stroke-linecap="round" pointer-events="none"/>';
        }
      }
      // Lichtstrahl
      var pts = w.pfad.map(function (p, i) { var px = mx(p[1]), py = mx(p[0]); if (i === 0) px = s * .75; if (i === w.pfad.length - 1 && w.aus) { px = mx(Math.max(-1, Math.min(N, p[1]))); py = mx(Math.max(-1, Math.min(N, p[0]))); } return px + ',' + py; });
      if (!w.aus) { var l = w.pfad[w.pfad.length - 1], v = w.pfad[w.pfad.length - 2]; pts[pts.length - 1] = ((mx(l[1]) + mx(v[1])) / 2 + (mx(l[1]) - mx(v[1])) * .1) + ',' + ((mx(l[0]) + mx(v[0])) / 2 + (mx(l[0]) - mx(v[0])) * .1); }
      o += '<polyline points="' + pts.join(' ') + '" fill="none" stroke="#ffd666" stroke-width="' + Math.round(s * .26) + '" stroke-opacity=".35" stroke-linejoin="round" stroke-linecap="round" pointer-events="none"/>' +
           '<polyline points="' + pts.join(' ') + '" fill="none" stroke="#fff3c0" stroke-width="' + Math.round(s * .08) + '" stroke-linejoin="round" stroke-linecap="round" pointer-events="none"/>';
      // Lampe links und Kristall am Ziel
      var ly = mx(P.r);
      o += '<g pointer-events="none"><circle cx="' + s * .5 + '" cy="' + ly + '" r="' + s * .34 + '" fill="#f2c037" stroke="#c4952f" stroke-width="3"/><circle cx="' + s * .5 + '" cy="' + ly + '" r="' + s * .16 + '" fill="#fff8d8"/></g>';
      var zx = mx(P.ziel[1]), zy = mx(P.ziel[0]), r2 = s * .32;
      o += '<g pointer-events="none">' + (getroffen ? '<circle cx="' + zx + '" cy="' + zy + '" r="' + s * .48 + '" fill="#ffd666" opacity=".45"/>' : '') +
        '<path d="M' + zx + ' ' + (zy - r2) + 'L' + (zx + r2 * .75) + ' ' + zy + 'L' + zx + ' ' + (zy + r2) + 'L' + (zx - r2 * .75) + ' ' + zy + 'z" fill="' + (getroffen ? '#8fe0f0' : '#5fb0c8') + '" stroke="#2c7f95" stroke-width="2.5"/>' +
        '<path d="M' + (zx - r2 * .75) + ' ' + zy + 'L' + (zx + r2 * .75) + ' ' + zy + 'M' + zx + ' ' + (zy - r2) + 'L' + (zx - r2 * .2) + ' ' + zy + 'L' + zx + ' ' + (zy + r2) + '" stroke="#2c7f95" stroke-width="1.5" fill="none"/></g>';
      svg.innerHTML = o; zz.textContent = zuege;
      return getroffen;
    }
    male();
    api.msg('Lenke das Licht zum Kristall!');
    svg.onclick = function (e) {
      var t = e.target.closest('[data-k]'); if (!t || fertig || RUN !== myRun) return;
      var k = +t.dataset.k; feld[k] = feld[k] === '/' ? '\\' : '/'; zuege++; tone(520, 0.05, 'triangle', 0.07);
      if (male()) {
        fertig = true; geloest++; good(); api.answer(true, true);
        api.msg('Der Kristall leuchtet!');
        if (geloest >= lv.ziel) { api.later(function () { api.done('Du hast ' + geloest + ' Lichträtsel gelöst!', 1); }, 1500); return; }
        api.later(raetsel, 1700);
      }
    };
    wrap.querySelector('[data-x="neu"]').onclick = function () { if (fertig) return; feld = start.slice(); zuege = 0; male(); };
  }
  raetsel();
};
""")
