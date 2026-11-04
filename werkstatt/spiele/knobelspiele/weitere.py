# Weitere Knobelspiele (zweite Lieferung): Wie spät ist es?, Kiosk, Der die das, Silben-Puzzle, Bilder-Sudoku, Wasser-Weg.
# Wird von bauen.py aufgerufen: weitere.alle(spiel)

# ------------------------------------------------------------------ Wörter für «Der, die, das»
DER_BILD = [('Hund','🐶'),('Apfel','🍎'),('Ball','⚽'),('Baum','🌳'),('Mond','🌙'),('Stern','⭐'),('Fisch','🐟'),('Vogel','🐦'),('Käse','🧀'),('Schuh','👟'),
            ('Stuhl','🪑'),('Igel','🦔'),('Fuchs','🦊'),('Löwe','🦁'),('Tiger','🐯'),('Affe','🐒'),('Bär','🐻'),('Hase','🐰'),('Pilz','🍄'),('Kuchen','🍰'),
            ('Regenschirm','☂️'),('Schlüssel','🔑'),('Zug','🚆'),('Bus','🚌'),('Brief','✉️'),('Schneemann','⛄'),('Ballon','🎈'),('Hut','🎩'),('Koffer','🧳'),
            ('Elefant','🐘'),('Frosch','🐸'),('Hahn','🐓'),('Pinguin','🐧'),('Kürbis','🎃'),('Mais','🌽'),('Daumen','👍')]
DIE_BILD = [('Katze','🐱'),('Maus','🐭'),('Sonne','☀️'),('Blume','🌸'),('Banane','🍌'),('Birne','🍐'),('Erdbeere','🍓'),('Tomate','🍅'),('Karotte','🥕'),
            ('Uhr','⏰'),('Brille','👓'),('Hose','👖'),('Jacke','🧥'),('Kerze','🕯️'),('Glocke','🔔'),('Lampe','💡'),('Tasse','☕'),('Pizza','🍕'),('Biene','🐝'),
            ('Eule','🦉'),('Kuh','🐮'),('Ente','🦆'),('Schnecke','🐌'),('Schildkröte','🐢'),('Rakete','🚀'),('Krone','👑'),('Wolke','☁️'),('Gitarre','🎸'),
            ('Trommel','🥁'),('Zitrone','🍋'),('Kirsche','🍒'),('Giraffe','🦒'),('Ameise','🐜'),('Hand','✋'),('Nase','👃'),('Tür','🚪'),('Schere','✂️'),('Torte','🎂')]
DAS_BILD = [('Haus','🏠'),('Auto','🚗'),('Schiff','🚢'),('Boot','⛵'),('Buch','📖'),('Ei','🥚'),('Brot','🍞'),('Herz','❤️'),('Pferd','🐴'),('Schaf','🐑'),
            ('Schwein','🐷'),('Huhn','🐔'),('Zebra','🦓'),('Kamel','🐫'),('Krokodil','🐊'),('Eis','🍦'),('Fahrrad','🚲'),('Flugzeug','✈️'),('Telefon','📞'),
            ('Geschenk','🎁'),('Bett','🛏️'),('Zelt','⛺'),('Blatt','🍃'),('Feuer','🔥'),('Kleid','👗'),('Hemd','👕'),('Ohr','👂'),('Messer','🔪'),('Schloss','🏰'),
            ('Paket','📦'),('Radio','📻'),('Klavier','🎹'),('Känguru','🦘'),('Nilpferd','🦛'),('Einhorn','🦄'),('Lama','🦙'),('Puzzle','🧩')]
DDD_WORT = {'der': ['Tisch','Stift','Garten','Lehrer','Sommer','Winter','Montag','Regen','Schnee','Wald','Berg','Fluss','Teller','Löffel','Rucksack','Pullover','Freund','Hagel'],
            'die': ['Schule','Tafel','Lehrerin','Woche','Strasse','Stadt','Wiese','Gabel','Pause','Farbe','Treppe','Klasse','Familie','Nacht','Freundin','Insel'],
            'das': ['Fenster','Zimmer','Heft','Wasser','Dorf','Spiel','Lied','Bild','Kind','Papier','Jahr','Wetter','Gras','Velo','Lineal','Turnier']}
DDD_SCHWER = {'der': ['Käse','Honig','Zucker','Pfeffer','Abend','Morgen','Mut','Fuss','Joker','Durst','Hunger','Frieden','Knopf','Spass'],
              'die': ['Butter','Milch','Gurke','Nudel','Angst','Freude','Leiter','Ruhe','Wut','Zeit','Hilfe','Idee','Musik','Luft'],
              'das': ['Mädchen','Knie','Salz','Obst','Gemüse','Ende','Glück','Gewitter','Mittagessen','Kissen','Märchen','Fräulein','Zuhause','Gold']}
DDD_SCHWER['das'].remove('Fräulein')
# Zusammengesetzte Nomen: [ganzes Wort, erster Teil, letzter Teil, Artikel]
DDD_ZUS = [('Haustür','Haus','tür','die'),('Apfelbaum','Apfel','baum','der'),('Fussball','Fuss','ball','der'),('Handschuh','Hand','schuh','der'),
           ('Sonnenbrille','Sonnen','brille','die'),('Kinderzimmer','Kinder','zimmer','das'),('Schulhaus','Schul','haus','das'),('Zahnbürste','Zahn','bürste','die'),
           ('Spielplatz','Spiel','platz','der'),('Bilderbuch','Bilder','buch','das'),('Tischbein','Tisch','bein','das'),('Gartenzaun','Garten','zaun','der'),
           ('Hosentasche','Hosen','tasche','die'),('Velohelm','Velo','helm','der'),('Schultasche','Schul','tasche','die'),('Blumenwiese','Blumen','wiese','die'),
           ('Baumhaus','Baum','haus','das'),('Holzpferd','Holz','pferd','das'),('Winterjacke','Winter','jacke','die'),('Pausenbrot','Pausen','brot','das'),
           ('Kuhglocke','Kuh','glocke','die'),('Vogelnest','Vogel','nest','das'),('Eisberg','Eis','berg','der'),('Butterbrot','Butter','brot','das'),
           ('Wasserglas','Wasser','glas','das'),('Schneeball','Schnee','ball','der'),('Mondrakete','Mond','rakete','die'),('Regenwolke','Regen','wolke','die'),
           ('Katzenfutter','Katzen','futter','das'),('Geburtstagskuchen','Geburtstags','kuchen','der')]

# ------------------------------------------------------------------ Wörter für das Silben-Puzzle (Silben mit «-» getrennt)
SIL2 = [('Ap-fel','🍎'),('Bir-ne','🍐'),('Ha-se','🐰'),('Kat-ze','🐱'),('Son-ne','☀️'),('Blu-me','🌸'),('Ti-ger','🐯'),('Ho-se','👖'),('Na-se','👃'),('Ro-se','🌹'),
        ('Bie-ne','🐝'),('Eu-le','🦉'),('Lö-we','🦁'),('I-gel','🦔'),('Bril-le','👓'),('Ker-ze','🕯️'),('Kro-ne','👑'),('Kä-se','🧀'),('Wol-ke','☁️'),('Tas-se','☕'),
        ('Gei-ge','🎻'),('Pan-da','🐼'),('Pin-sel','🖌️'),('Ga-bel','🍴'),('Lam-pe','💡'),('Gur-ke','🥒'),('En-te','🦆'),('Af-fe','🐒'),('Tor-te','🎂'),('Wür-fel','🎲'),
        ('Bal-lon','🎈'),('Ki-wi','🥝'),('Kür-bis','🎃'),('Ein-horn','🦄'),('Dra-che','🐉'),('Schnee-mann','⛄'),('Fuss-ball','⚽'),('Ge-schenk','🎁'),('Ze-bra','🦓'),('Zie-ge','🐐')]
SIL3 = [('Ba-na-ne','🍌'),('To-ma-te','🍅'),('Ra-ke-te','🚀'),('Gi-raf-fe','🦒'),('Ka-rot-te','🥕'),('Schmet-ter-ling','🦋'),('Te-le-fon','📞'),('Kro-ko-dil','🐊'),
        ('Pin-gu-in','🐧'),('Zi-tro-ne','🍋'),('Me-lo-ne','🍈'),('Ka-me-ra','📷'),('Ro-bo-ter','🤖'),('Schild-krö-te','🐢'),('Ham-bur-ger','🍔'),('Ka-nin-chen','🐇'),
        ('Erd-bee-re','🍓'),('Gi-tar-re','🎸'),('E-le-fant','🐘'),('Hub-schrau-ber','🚁'),('Schnee-flo-cke','❄️'),('Fle-der-maus','🦇'),('Re-gen-schirm','☂️'),('Sonnen-blu-me','🌻')]
SIL3 = [x for x in SIL3 if x[0] != 'Sonnen-blu-me'] + [('Son-nen-blu-me', '🌻')]
SIL4 = [('Re-gen-bo-gen','🌈'),('Scho-ko-la-de','🍫'),('Ba-de-wan-ne','🛁'),('Ta-schen-lam-pe','🔦'),('Ma-ri-en-kä-fer','🐞'),('Was-ser-me-lo-ne','🍉'),
        ('Lo-ko-mo-ti-ve','🚂'),('Ka-rus-sell','🎠'),('Ach-ter-bahn','🎢'),('Feu-er-wehr-au-to','🚒')]
SIL_WORT = ['Schu-le','Leh-re-rin','Pau-sen-platz','Fe-ri-en','Ge-burts-tag','Mon-tag','Diens-tag','Mitt-woch','Don-ners-tag','Frei-tag','Sams-tag','Ja-nu-ar',
            'Win-ter','Som-mer','Früh-ling','Fens-ter','Wan-der-tag','Tur-nen','Mu-sik','Zeich-nen','Haus-tür','Ku-schel-tier','Zau-ber-stab','Turn-hal-le',
            'Kin-der-gar-ten','Klas-sen-zim-mer','Haus-auf-ga-be','Pau-sen-glo-cke','Schnee-ball-schlacht','Fuss-ball-feld','Bus-hal-te-stel-le','Ge-spens-ter-schloss',
            'Scho-ko-la-den-ku-chen','Ge-burts-tags-fest','Re-gen-bo-gen-far-ben','Ta-schen-rech-ner']


def alle(spiel):
    # ================================================================== Wie spät ist es?
    spiel(id='uhr-lesen', titel='Wie spät ist es?', icon='⏰', fach='Mathematik', thema='Zeit', stufe='1.–4. Klasse', sort=2, n=10,
          sterne={'modus': 'runde', 'n': 10},
          kurz='Die Uhr lesen: volle Stunden bis genaue Minuten.',
          intro='Der kurze Zeiger zeigt die Stunde, der lange Zeiger die Minuten. Schau genau hin!',
          levels=[dict(name='Leicht', info='Volle Stunden', t=0),
                  dict(name='Gut', info='Halbe Stunden', t=1),
                  dict(name='Mittel', info='Viertelstunden', t=2),
                  dict(name='Schwer', info='Alle 5 Minuten', t=3),
                  dict(name='Profi', info='Genaue Minuten, auch am Nachmittag', t=4)],
          css=r"""
.uh{display:flex;flex-direction:column;align-items:center;gap:16px;width:100%}
.uh .frage{display:grid;place-items:center;background:#fff;border:2px solid var(--line);border-radius:28px;padding:12px 26px;box-shadow:var(--sch);min-height:120px}
.uh .frage .dig{font-family:system-ui,-apple-system,sans-serif;font-weight:700;font-size:clamp(48px,10vw,76px);color:var(--sky-d);letter-spacing:.02em}
.uh .frage .wort{font-size:clamp(34px,7vw,52px)}
.uh .wahl{display:grid;grid-template-columns:1fr 1fr;gap:14px;width:min(100%,560px)}
.uh .wahl button{background:#fff;border:2px solid var(--ink);border-radius:22px;box-shadow:var(--sch-k);min-height:80px;display:grid;place-items:center;padding:8px;transition:transform .12s}
.uh .wahl button:active{transform:scale(.96)}
.uh .wahl button.dig{font:700 clamp(30px,6vw,44px) system-ui,-apple-system,sans-serif}
.uh .wahl button.ok{background:#e7f3df;border-color:var(--ok)}.uh .wahl button.no{background:#fbe5e2;border-color:var(--no)}.uh .wahl button.hint{background:var(--sun);border-color:var(--gold)}
.uhr-svg{display:block}
""",
          js=r"""
var ZAHLW = ['zwölf', 'eins', 'zwei', 'drei', 'vier', 'fünf', 'sechs', 'sieben', 'acht', 'neun', 'zehn', 'elf', 'zwölf'];
function zw(h) { h = ((h - 1) % 12 + 12) % 12 + 1; return h === 1 ? 'eins' : ZAHLW[h]; }
function zeitWort(h, m) {
  var n = h % 12 || 12, nx = n % 12 + 1;
  if (m === 0) return (n === 1 ? 'ein' : zw(n)) + ' Uhr';
  if (m === 30) return 'halb ' + zw(nx);
  if (m === 15) return 'Viertel nach ' + zw(n);
  if (m === 45) return 'Viertel vor ' + zw(nx);
  return null;
}
function dig(h, m) { return h + ':' + ('0' + m).slice(-2); }
// Zufällige Zeit für die Stufe
function zeit(t) {
  var h = rnd(1, 12), m = t === 0 ? 0 : t === 1 ? pick([0, 30, 30], 1)[0] : t === 2 ? pick([0, 15, 30, 45, 15, 45], 1)[0] : t === 3 ? rnd(0, 11) * 5 : rnd(0, 59);
  return { h: h, m: m };
}
// Ähnliche, aber falsche Zeiten (gleich auf der Uhr = gleiche Stunde 1–12 und Minute)
function falsche(z, t) {
  var step = t <= 1 ? 30 : t === 2 ? 15 : t === 3 ? 5 : 1, c = [], o = [];
  var tausch = { h: Math.round(z.m / 5) || 12, m: (z.h % 12) * 5 };
  if (t >= 1) c.push(tausch);
  c.push({ h: z.h % 12 + 1, m: z.m }, { h: (z.h + 10) % 12 + 1, m: z.m });
  if (t >= 1) c.push({ h: z.h, m: (z.m + step) % 60 }, { h: z.h, m: (z.m + 60 - step) % 60 }, { h: z.h, m: (z.m + 30) % 60 });
  if (t === 0) c.push({ h: (z.h + 5) % 12 + 1, m: 0 }, { h: (z.h + 2) % 12 + 1, m: 0 });
  if (t === 1) c.push({ h: z.h % 12 + 1, m: (z.m + 30) % 60 });
  if (t >= 3) c.push({ h: z.h, m: (z.m + 10) % 60 }, { h: z.h % 12 + 1, m: (z.m + step) % 60 });
  c = shuffle(c.slice(0, 3)).concat(shuffle(c.slice(3)));
  c.forEach(function (x) { var k = x.h + ':' + x.m; if (o.length < 3 && k !== z.h + ':' + z.m && !o.some(function (y) { return y.h + ':' + y.m === k; })) o.push(x); });
  while (o.length < 3) { var r = zeit(t); if (r.h + ':' + r.m !== z.h + ':' + z.m && !o.some(function (y) { return y.h === r.h && y.m === r.m; })) o.push(r); }
  return o;
}
function uhrSvg(h, m, px) {
  var o = '<svg class="uhr-svg" viewBox="0 0 200 200" width="' + px + '" height="' + px + '" aria-hidden="true">' +
    '<circle cx="100" cy="100" r="94" fill="#fff" stroke="#d6ad45" stroke-width="7"/><circle cx="100" cy="100" r="86" fill="none" stroke="#e1edf7" stroke-width="2"/>';
  for (var i = 0; i < 60; i++) { var a = i * 6 * Math.PI / 180, r1 = i % 5 ? 80 : 74; o += '<line x1="' + (100 + Math.sin(a) * r1).toFixed(1) + '" y1="' + (100 - Math.cos(a) * r1).toFixed(1) + '" x2="' + (100 + Math.sin(a) * 85).toFixed(1) + '" y2="' + (100 - Math.cos(a) * 85).toFixed(1) + '" stroke="' + (i % 5 ? '#c5d8e8' : '#5f6963') + '" stroke-width="' + (i % 5 ? 1.5 : 3) + '"/>'; }
  for (i = 1; i <= 12; i++) { var b = i * 30 * Math.PI / 180; o += '<text x="' + (100 + Math.sin(b) * 60).toFixed(1) + '" y="' + (100 - Math.cos(b) * 60 + 8).toFixed(1) + '" text-anchor="middle" font-size="22" font-family="system-ui,sans-serif" font-weight="700" fill="#1f2421">' + i + '</text>'; }
  var ah = ((h % 12) + m / 60) * 30, am = m * 6;
  o += '<line x1="100" y1="100" x2="100" y2="52" stroke="#1f2421" stroke-width="9" stroke-linecap="round" transform="rotate(' + ah + ' 100 100)"/>';
  o += '<line x1="100" y1="100" x2="100" y2="24" stroke="#3f78a8" stroke-width="5" stroke-linecap="round" transform="rotate(' + am + ' 100 100)"/>';
  return o + '<circle cx="100" cy="100" r="7" fill="#d6ad45"/></svg>';
}
G.play = function (lv, api) {
  var t = lv.t, wrap = document.createElement('div'); wrap.className = 'uh'; api.stage.appendChild(wrap);
  var last = '';
  function next() {
    var z; do { z = zeit(t); } while (z.h + ':' + z.m === last); last = z.h + ':' + z.m;
    var art = Math.random() < .5 ? 'zeigen' : 'lesen', opts = shuffle([z].concat(falsche(z, t)));
    var nachm = t === 4 && Math.random() < .5, big = Math.min(240, window.innerHeight - 380, window.innerWidth - 60), small = Math.max(84, Math.min(150, (window.innerHeight - 330) / 2 - 20));
    var wort = t <= 2 && art === 'zeigen' && Math.random() < .6 ? zeitWort(z.h, z.m) : null;
    if (art === 'lesen') {
      api.msg('<span class="em">🕰️</span> Wie spät ist es?');
      wrap.innerHTML = '<div class="frage">' + uhrSvg(z.h, z.m, Math.max(150, big)) + '</div><div class="wahl"></div>';
    } else {
      api.msg('<span class="em">👆</span> Welche Uhr zeigt diese Zeit?' + (nachm ? ' <small>Am Nachmittag: 15 Uhr ist 3 Uhr.</small>' : ''));
      wrap.innerHTML = '<div class="frage">' + (wort ? '<span class="wort">' + h(wort) + '</span>' : '<span class="dig">' + dig(nachm ? z.h % 12 + 12 : z.h, z.m) + '</span>') + '</div><div class="wahl"></div>';
    }
    var wahl = wrap.querySelector('.wahl'), lock = false;
    opts.forEach(function (o) {
      var b = document.createElement('button'), ok = o.h === z.h && o.m === z.m;
      if (art === 'lesen') { b.className = 'dig'; b.textContent = dig(o.h, o.m); } else { b.innerHTML = uhrSvg(o.h, o.m, small); b.setAttribute('aria-label', 'Uhr ' + dig(o.h, o.m)); }
      b.onclick = function () {
        if (lock) return; lock = true;
        b.classList.add(ok ? 'ok' : 'no');
        if (!ok) Array.prototype.forEach.call(wahl.children, function (c, i) { if (opts[i].h === z.h && opts[i].m === z.m) c.classList.add('hint'); });
        var w = zeitWort(z.h, z.m);
        api.msg(ok ? '<span class="em">🎉</span> Richtig, es ist ' + dig(z.h, z.m) + (w ? ' (' + h(w) + ')' : '') + '.' : '<span class="em">💡</span> Es ist ' + dig(z.h, z.m) + (w ? ', also ' + h(w) : '') + '.');
        if (api.answer(ok)) api.later(next, ok ? 1100 : 2300);
      };
      wahl.appendChild(b);
    });
  }
  next();
};
""")

    # ================================================================== Kiosk (Geld)
    spiel(id='kiosk', titel='Kiosk', icon='🪙', fach='Mathematik', thema='Geld', stufe='1.–4. Klasse', sort=3, n=8,
          sterne={'modus': 'runde', 'n': 8},
          kurz='Mit Franken und Rappen genau bezahlen.',
          intro='Im Kiosk kostet alles etwas. Lege genau so viel Geld hin, wie es kostet. Tippe auf eine Münze, um sie hinzulegen, und auf eine Münze auf der Theke, um sie wieder wegzunehmen.',
          levels=[dict(name='Leicht', info='Bis 10 Franken', t=0),
                  dict(name='Gut', info='Bis 50 Franken, mit Noten', t=1),
                  dict(name='Mittel', info='Franken und 50 Rappen', t=2),
                  dict(name='Schwer', info='Mit 10 und 20 Rappen', t=3),
                  dict(name='Profi', info='Wie viel Rückgeld?', t=4)],
          css=r"""
.ki{display:flex;flex-direction:column;align-items:center;gap:14px;width:100%;max-width:860px}
.ki .ware{display:flex;align-items:center;gap:16px;background:#fff;border:2px solid var(--line);border-radius:26px;padding:10px 22px;box-shadow:var(--sch)}
.ki .ware .em2{font-size:64px;line-height:1}
.ki .schild{background:var(--sun);border:2px solid var(--gold);border-radius:14px;padding:4px 14px;font:700 clamp(28px,5vw,40px) system-ui,-apple-system,sans-serif;transform:rotate(-3deg)}
.ki .ware .wn{font-size:26px}
.theke{width:100%;min-height:118px;background:repeating-linear-gradient(90deg,#e9d2a6 0 38px,#e3c995 38px 76px);border:3px solid #c9a86a;border-radius:20px;padding:12px;display:flex;flex-wrap:wrap;gap:8px;align-content:flex-start;justify-content:center;box-shadow:inset 0 3px 8px rgba(0,0,0,.08)}
.theke:empty::before{content:"Hier liegt dein Geld";color:#8a6d3b;font-size:20px;align-self:center;margin:auto}
.summe{font-size:21px;color:var(--soft);min-height:28px}
.boerse{display:flex;flex-wrap:wrap;gap:10px;justify-content:center;align-items:center}
.mz{border-radius:50%;display:grid;place-items:center;font:700 15px/1 system-ui,-apple-system,sans-serif;color:#3a3f44;border:3px solid #9aa4ad;
  background:radial-gradient(circle at 35% 30%,#ffffff 0%,#e3e8ec 45%,#b9c2c9 100%);box-shadow:0 3px 6px rgba(0,0,0,.18);flex:none;text-align:center;padding:2px}
.nt{width:92px;height:52px;border-radius:8px;display:grid;place-items:center;font:700 22px system-ui,-apple-system,sans-serif;color:#2b2b2b;box-shadow:0 3px 6px rgba(0,0,0,.18);border:2px solid rgba(0,0,0,.18);flex:none}
.boerse button,.theke button{padding:0;transition:transform .12s}
.boerse button:active,.theke button:active{transform:scale(.92)}
.ki .knopf{display:flex;gap:10px;flex-wrap:wrap;justify-content:center}
.ki .wahl{display:grid;grid-template-columns:1fr 1fr;gap:12px;width:min(100%,520px)}
.ki .wahl button{background:#fff;border:2px solid var(--ink);border-radius:20px;min-height:74px;font:700 28px system-ui,-apple-system,sans-serif;box-shadow:var(--sch-k)}
.ki .wahl button.ok{background:#e7f3df;border-color:var(--ok)}.ki .wahl button.no{background:#fbe5e2;border-color:var(--no)}.ki .wahl button.hint{background:var(--sun);border-color:var(--gold)}
""",
          js=r"""
var WAREN = [['🍦', 'Glace'], ['🥨', 'Brezel'], ['📒', 'Heft'], ['🧃', 'Saft'], ['🍎', 'Apfel'], ['✏️', 'Stift'], ['🎈', 'Ballon'], ['🍫', 'Schoggi'],
  ['🧸', 'Teddy'], ['⚽', 'Ball'], ['🍪', 'Guetzli'], ['📚', 'Buch'], ['🧩', 'Puzzle'], ['🍌', 'Banane'], ['🥐', 'Gipfeli'], ['🖍️', 'Farbstifte'], ['🪁', 'Drachen'], ['🎲', 'Spiel']];
var GELD = { 10: ['10 Rp.', 46], 20: ['20 Rp.', 52], 50: ['50 Rp.', 42], 100: ['1 Fr.', 58], 200: ['2 Fr.', 66], 500: ['5 Fr.', 74], 1000: ['10', 0, '#f3cf55'], 2000: ['20', 0, '#ec8a7d'], 5000: ['50', 0, '#86c98b'] };
var SORTEN = [[100, 200, 500], [100, 200, 500, 1000, 2000], [50, 100, 200, 500, 1000], [10, 20, 50, 100, 200, 500], []];
function fr(rp) { return 'Fr. ' + Math.floor(rp / 100) + '.' + ('0' + rp % 100).slice(-2); }
function preis(t) {
  if (t === 0) return rnd(1, 10) * 100;
  if (t === 1) return rnd(6, 48) * 100;
  if (t === 2) return rnd(2, 19) * 50;
  if (t === 3) return rnd(15, 99) * 10;
  return Math.random() < .5 ? rnd(3, 18) * 50 : rnd(12, 95) * 10;
}
function stueck(v) {
  var g = GELD[v];
  if (v >= 1000) return '<span class="nt" style="background:' + g[2] + '">' + g[0] + '</span>';
  return '<span class="mz" style="width:' + g[1] + 'px;height:' + g[1] + 'px;font-size:' + (g[1] > 55 ? 16 : 13) + 'px">' + g[0] + '</span>';
}
G.play = function (lv, api) {
  var t = lv.t, letzte = '', wrap = document.createElement('div'); wrap.className = 'ki'; api.stage.appendChild(wrap);
  function next() {
    var w; do { w = pick(WAREN, 1)[0]; } while (w[1] === letzte); letzte = w[1];
    var p = preis(t), lock = false;
    if (t === 4) {
      var noten = [500, 1000, 2000, 5000].filter(function (n) { return n > p; }), bez = noten[0] === 500 && p < 400 ? 500 : noten[Math.min(noten.length - 1, rnd(0, 1))], rueck = bez - p;
      var c = [rueck + 10, rueck - 10, rueck + 50, rueck - 50, rueck + 100, rueck - 100], o = [rueck];
      shuffle(c).forEach(function (x) { if (o.length < 4 && x > 0 && o.indexOf(x) < 0) o.push(x); });
      o = shuffle(o);
      api.msg('<span class="em">🧾</span> Du bezahlst mit ' + (bez >= 1000 ? 'einer ' + (bez / 100) + '-Franken-Note' : 'einem 5-Fränkler') + '. Wie viel Rückgeld bekommst du?');
      wrap.innerHTML = '<div class="ware"><span class="em2">' + w[0] + '</span><span class="wn">' + h(w[1]) + '</span><span class="schild">' + fr(p) + '</span></div>' +
        '<div class="theke" aria-label="Bezahlt">' + stueck(bez) + '</div><div class="wahl"></div>';
      var wahl = wrap.querySelector('.wahl');
      o.forEach(function (x) {
        var b = document.createElement('button'); b.textContent = fr(x);
        b.onclick = function () {
          if (lock) return; lock = true; var ok = x === rueck;
          b.classList.add(ok ? 'ok' : 'no');
          if (!ok) Array.prototype.forEach.call(wahl.children, function (c2, i) { if (o[i] === rueck) c2.classList.add('hint'); });
          api.msg(ok ? '<span class="em">🎉</span> Genau! ' + fr(bez) + ' − ' + fr(p) + ' = ' + fr(rueck) : '<span class="em">💡</span> ' + fr(bez) + ' − ' + fr(p) + ' = <b>' + fr(rueck) + '</b>');
          if (api.answer(ok)) api.later(next, ok ? 1500 : 2800);
        };
        wahl.appendChild(b);
      });
      return;
    }
    var gelegt = [];
    api.msg('<span class="em">🛒</span> Bezahle genau ' + fr(p) + '.');
    wrap.innerHTML = '<div class="ware"><span class="em2">' + w[0] + '</span><span class="wn">' + h(w[1]) + '</span><span class="schild">' + fr(p) + '</span></div>' +
      '<div class="theke" aria-label="Theke"></div><div class="summe"></div><div class="boerse" aria-label="Portemonnaie">' +
      SORTEN[t].map(function (v) { return '<button data-v="' + v + '" aria-label="' + GELD[v][0] + (v >= 1000 ? ' Franken' : '') + ' hinlegen">' + stueck(v) + '</button>'; }).join('') +
      '</div><div class="knopf"><button class="go alt" data-x="weg">↺ Alles zurück</button><button class="go sun" data-x="zahl">✓ Bezahlen</button></div>';
    var theke = wrap.querySelector('.theke'), summe = wrap.querySelector('.summe');
    function zeig() {
      theke.innerHTML = gelegt.map(function (v, i) { return '<button data-i="' + i + '" aria-label="' + GELD[v][0] + ' wegnehmen">' + stueck(v) + '</button>'; }).join('');
      var s = gelegt.reduce(function (a, b) { return a + b; }, 0);
      summe.textContent = t === 0 && gelegt.length ? 'Du hast ' + fr(s) + ' hingelegt.' : '';
    }
    zeig();
    wrap.onclick = function (e) {
      var b = e.target.closest('button'); if (!b || lock) return;
      if (b.dataset.v) { if (gelegt.length >= 30) return; gelegt.push(+b.dataset.v); gelegt.sort(function (a, c) { return c - a; }); tone(900 + rnd(0, 4) * 60, 0.06, 'triangle', 0.08); zeig(); }
      else if (b.dataset.i != null) { gelegt.splice(+b.dataset.i, 1); zeig(); }
      else if (b.dataset.x === 'weg') { gelegt = []; zeig(); }
      else if (b.dataset.x === 'zahl') {
        if (!gelegt.length) { api.msg('<span class="em">👛</span> Lege zuerst Geld auf die Theke.'); return; }
        var s = gelegt.reduce(function (a, c) { return a + c; }, 0), ok = s === p; lock = true;
        api.msg(ok ? '<span class="em">🎉</span> Genau richtig! ' + w[0] + ' Danke für den Einkauf.' :
          '<span class="em">💡</span> Das sind ' + fr(s) + '. Es kostet aber ' + fr(p) + (s > p ? '. Das ist zu viel.' : '. Das ist zu wenig.'));
        if (api.answer(ok)) api.later(next, ok ? 1500 : 3000);
      }
    };
  }
  next();
};
""")

    # ================================================================== Der, die, das
    spiel(id='der-die-das', titel='Der, die, das', icon='🗂️', fach='Deutsch', thema='Wortarten', stufe='1.–5. Klasse', sort=2, n=10,
          sterne={'modus': 'runde', 'n': 10},
          kurz='Nomen in die richtige Artikel-Kiste legen.',
          intro='Heisst es <b style="color:#3f78a8">der</b>, <b style="color:#c8574e">die</b> oder <b style="color:#4c8a37">das</b>? Tippe auf die richtige Kiste.',
          levels=[dict(name='Leicht', info='Mit Bildern', t=0),
                  dict(name='Gut', info='Mit Bildern, mehr Wörter', t=1),
                  dict(name='Mittel', info='Ohne Bilder', t=2),
                  dict(name='Schwer', info='Knifflige Wörter', t=3),
                  dict(name='Profi', info='Zusammengesetzte Wörter', t=4)],
          daten={'DER': DER_BILD, 'DIE': DIE_BILD, 'DAS': DAS_BILD, 'WORT': DDD_WORT, 'SCHWER': DDD_SCHWER, 'ZUS': DDD_ZUS},
          css=r"""
.dd{display:flex;flex-direction:column;align-items:center;gap:18px;width:100%}
.dd .karte2{background:#fff;border:2px solid var(--line);border-radius:28px;padding:14px 30px;box-shadow:var(--sch);text-align:center;min-width:240px}
.dd .karte2 .em2{font-size:76px;line-height:1.1;display:block}
.dd .karte2 .wt{font-size:clamp(40px,8vw,58px);line-height:1.1}
.dd .karte2 .wt i{font-style:normal;color:var(--gold-d);text-decoration:underline;text-decoration-thickness:3px;text-underline-offset:6px}
.dd .kisten{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;width:min(100%,640px)}
.dd .kisten button{min-height:110px;border-radius:22px;border:3px solid;font-size:clamp(34px,7vw,46px);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:2px;box-shadow:var(--sch-k);transition:transform .12s}
.dd .kisten button small{font-size:28px;line-height:1}
.dd .kisten button:active{transform:scale(.96)}
.dd .k-der{background:#e3f0fb;border-color:#3f78a8;color:#2c5a82}
.dd .k-die{background:#fbe9e7;border-color:#c8574e;color:#9a3a32}
.dd .k-das{background:#e9f3e3;border-color:#5f9a4a;color:#3f6b2e}
.dd .kisten button.weg{opacity:.35}
.dd .kisten button.richtig{transform:scale(1.06);box-shadow:0 0 0 5px var(--gold)}
.dd .tipp{color:var(--soft);font-size:19px}
""",
          js=r"""
G.play = function (lv, api) {
  var t = lv.t, pool = [];
  function add(list, art, bild) { list.forEach(function (x) { pool.push(bild ? { w: x[0], e: x[1], a: art } : { w: x, e: '', a: art }); }); }
  if (t <= 1) { var k = t === 0 ? 14 : 99; add(D.DER.slice(0, k), 'der', 1); add(D.DIE.slice(0, k), 'die', 1); add(D.DAS.slice(0, k), 'das', 1); }
  else if (t === 2) { add(D.WORT.der, 'der'); add(D.WORT.die, 'die'); add(D.WORT.das, 'das'); }
  else if (t === 3) { add(D.SCHWER.der, 'der'); add(D.SCHWER.die, 'die'); add(D.SCHWER.das, 'das'); }
  else D.ZUS.forEach(function (z) { pool.push({ w: z[0], a: z[3], z: z }); });
  // möglichst gleich viele der, die, das
  var runde = [], arts = shuffle(['der', 'die', 'das']);
  for (var i = 0; i < G.n; i++) { var a = arts[i % 3], c = pool.filter(function (p) { return p.a === a && runde.indexOf(p) < 0; }); runde.push(pick(c, 1)[0]); }
  runde = shuffle(runde);
  var idx = 0, wrap = document.createElement('div'); wrap.className = 'dd'; api.stage.appendChild(wrap);
  function next() {
    var p = runde[idx++], lock = false;
    var wortHtml = p.z ? h(p.z[1]) + '<i>' + h(p.z[2]) + '</i>' : h(p.w);
    wrap.innerHTML = '<div class="karte2">' + (p.e ? '<span class="em2">' + p.e + '</span>' : '') + '<span class="wt">' + (p.z ? h(p.w) : wortHtml) + '</span></div>' +
      (t === 4 ? '<div class="tipp">Tipp: Das letzte Wort bestimmt den Artikel.</div>' : '') +
      '<div class="kisten">' + ['der', 'die', 'das'].map(function (a) { return '<button class="k-' + a + '" data-a="' + a + '">' + a + '<small>' + { der: '🔵', die: '🔴', das: '🟢' }[a] + '</small></button>'; }).join('') + '</div>';
    api.msg('<span class="em">🤔</span> Welcher Artikel passt?');
    wrap.querySelector('.kisten').onclick = function (e) {
      var b = e.target.closest('button'); if (!b || lock) return; lock = true;
      var ok = b.dataset.a === p.a;
      Array.prototype.forEach.call(this.children, function (c) { if (c.dataset.a === p.a) c.classList.add('richtig'); else c.classList.add('weg'); });
      if (!ok) b.classList.add('shake');
      if (p.z) wrap.querySelector('.wt').innerHTML = h(p.z[1]) + '<i>' + h(p.z[2]) + '</i>';
      api.msg((ok ? '<span class="em">🎉</span> Richtig: ' : '<span class="em">💡</span> Es heisst ') + '<b>' + p.a + ' ' + h(p.w) + '</b>' +
        (p.z ? ' <small>(wie ' + p.a + ' ' + h(p.z[2].charAt(0).toUpperCase() + p.z[2].slice(1)) + ')</small>' : ''));
      if (api.answer(ok)) api.later(next, ok ? 1200 : 2500);
    };
  }
  next();
};
""")

    # ================================================================== Silben-Puzzle
    spiel(id='silben-puzzle', titel='Silben-Puzzle', icon='🧩', fach='Deutsch', thema='Lesen', stufe='1.–4. Klasse', sort=3, n=8,
          sterne={'modus': 'runde', 'n': 8},
          kurz='Silben in die richtige Reihenfolge bringen.',
          intro='Die Silben sind durcheinander geraten. Tippe sie der Reihe nach an, damit das Wort entsteht. Klatsch die Silben dazu!',
          levels=[dict(name='Leicht', info='2 Silben, mit Bild', t=0),
                  dict(name='Gut', info='3 Silben, mit Bild', t=1),
                  dict(name='Mittel', info='3 bis 5 Silben, mit Bild', t=2),
                  dict(name='Schwer', info='Ohne Bild', t=3),
                  dict(name='Profi', info='Lange Wörter und eine Silbe zu viel', t=4)],
          daten={'S2': SIL2, 'S3': SIL3, 'S4': SIL4, 'SW': SIL_WORT},
          css=r"""
.si{display:flex;flex-direction:column;align-items:center;gap:18px;width:100%}
.si .em2{font-size:84px;line-height:1;background:#fff;border:3px solid var(--gold);border-radius:50%;width:130px;height:130px;display:grid;place-items:center;box-shadow:inset 0 0 0 6px #fff,var(--sch)}
.si .plaetze{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;min-height:76px}
.si .platz{min-width:70px;height:70px;border-radius:16px;border:2.5px dashed var(--line2);background:#fff;display:grid;place-items:center;padding:0 14px;font-size:clamp(28px,6vw,40px)}
.si .platz.voll{border-style:solid;border-color:var(--sky-d);background:var(--sky)}
.si .plaetze.gut .platz{border-color:var(--ok);background:#e7f3df}
.si .steine{display:flex;flex-wrap:wrap;gap:12px;justify-content:center;max-width:720px}
.si .stein{min-width:84px;height:76px;border-radius:18px;border:2px solid var(--ink);background:var(--sun);font-size:clamp(28px,6vw,40px);padding:0 16px;box-shadow:0 4px 0 #c9a43c;transition:transform .12s}
.si .stein:active{transform:translateY(3px);box-shadow:0 1px 0 #c9a43c}
.si .stein.weg{visibility:hidden}
.si .wort2{font-size:clamp(34px,7vw,50px);min-height:56px}
.si .wort2 span{display:inline-block;margin:0 2px}
.si .wort2 span:nth-child(odd){color:var(--sky-d)}.si .wort2 span:nth-child(even){color:#c8574e}
""",
          js=r"""
function sprich(w) {
  if (ST.mute) return;
  try { var u = new SpeechSynthesisUtterance(w); u.lang = 'de-CH'; u.rate = .8; var v = speechSynthesis.getVoices().filter(function (x) { return /^de/i.test(x.lang); }); if (v.length) u.voice = v.filter(function (x) { return /CH/i.test(x.lang); })[0] || v[0]; speechSynthesis.cancel(); speechSynthesis.speak(u); } catch (e) {}
}
G.play = function (lv, api) {
  var t = lv.t, pool;
  if (t === 0) pool = D.S2;
  else if (t === 1) pool = D.S3;
  else if (t === 2) pool = D.S3.concat(D.S4);
  else if (t === 3) pool = D.SW.filter(function (w) { return w.split('-').length <= 4; }).map(function (w) { return [w, '']; });
  else pool = D.SW.filter(function (w) { return w.split('-').length >= 3; }).concat(D.S4.map(function (x) { return x[0]; })).map(function (w) { return [w, '']; });
  var runde = pick(pool, G.n), idx = 0, wrap = document.createElement('div'); wrap.className = 'si'; api.stage.appendChild(wrap);
  function next() {
    var p = runde[idx++], sil = p[0].split('-'), wort = sil.join(''), gelegt = [], fehl = 0, lock = false, steine = sil.slice();
    if (t === 4) { var alle = [].concat.apply([], pool.map(function (x) { return x[0].split('-'); })).filter(function (s) { return sil.indexOf(s) < 0 && s.length > 1; }); steine.push(pick(alle, 1)[0]); }
    do { steine = shuffle(steine); } while (steine.join('') === sil.join('') && steine.length > 1);
    // Kleinschreibung der Teile wie im Wort, erste Silbe gross
    wrap.innerHTML = (p[1] ? '<div class="em2">' + p[1] + '</div>' : '') + '<div class="plaetze"></div><div class="steine"></div>';
    var plaetze = wrap.querySelector('.plaetze'), stEl = wrap.querySelector('.steine');
    for (var i = 0; i < sil.length; i++) plaetze.insertAdjacentHTML('beforeend', '<div class="platz"></div>');
    steine.forEach(function (s, i) { stEl.insertAdjacentHTML('beforeend', '<button class="stein" data-i="' + i + '">' + h(s) + '</button>'); });
    api.msg('<span class="em">👏</span> ' + (t === 4 ? 'Eine Silbe gehört nicht dazu. ' : '') + 'Welches Wort ist es?' + (sil.length > 2 ? ' <small>' + sil.length + ' Silben</small>' : ''));
    function zeig() { Array.prototype.forEach.call(plaetze.children, function (pl, i) { pl.textContent = gelegt[i] != null ? steine[gelegt[i]] : ''; pl.classList.toggle('voll', gelegt[i] != null); }); Array.prototype.forEach.call(stEl.children, function (b, i) { b.classList.toggle('weg', gelegt.indexOf(i) >= 0); }); }
    plaetze.onclick = function (e) { var pl = e.target.closest('.platz'); if (!pl || lock) return; var i = Array.prototype.indexOf.call(plaetze.children, pl); if (gelegt[i] != null) { gelegt = gelegt.slice(0, i); zeig(); } };
    stEl.onclick = function (e) {
      var b = e.target.closest('.stein'); if (!b || lock || b.classList.contains('weg')) return;
      gelegt.push(+b.dataset.i); tone(500 + gelegt.length * 80, 0.07, 'sine', 0.09); zeig();
      if (gelegt.length < sil.length) return;
      var gebaut = gelegt.map(function (k) { return steine[k]; }).join('');
      if (gebaut === wort) {
        lock = true; plaetze.classList.add('gut');
        api.msg('<span class="em">🎉</span> Super! <span class="wort2">' + sil.map(function (s) { return '<span>' + h(s) + '</span>'; }).join('·') + '</span>');
        sprich(wort);
        if (api.answer(fehl === 0)) api.later(next, 2000);
      } else {
        fehl++; bad(); plaetze.classList.remove('shake'); void plaetze.offsetWidth; plaetze.classList.add('shake');
        api.msg('<span class="em">🔁</span> Das ergibt kein Wort. Versuch es nochmal!' + (fehl >= 2 ? ' <small>Das Wort beginnt mit «' + h(sil[0]) + '».</small>' : ''));
        api.later(function () { gelegt = []; zeig(); }, 700);
      }
    };
  }
  next();
};
""")

    # ================================================================== Bilder-Sudoku
    spiel(id='bilder-sudoku', titel='Bilder-Sudoku', icon='🍓', fach='Knobeln', thema='Logik', stufe='1.–6. Klasse', sort=3, n=3,
          sterne={'modus': 'runde', 'n': 3},
          kurz='Jedes Bild nur einmal pro Zeile, Spalte und Kästchen.',
          intro='Fülle die leeren Felder. In jeder Zeile, jeder Spalte und jedem dicken Kästchen kommt jedes Bild genau einmal vor.',
          levels=[dict(name='Leicht', info='4 × 4 mit Früchten', n=4, weg=6, bild=True),
                  dict(name='Gut', info='4 × 4 mit Zahlen', n=4, weg=9, bild=False),
                  dict(name='Mittel', info='6 × 6 mit Tieren', n=6, weg=16, bild=True),
                  dict(name='Schwer', info='6 × 6 mit Zahlen', n=6, weg=22, bild=False),
                  dict(name='Profi', info='9 × 9 mit Zahlen', n=9, weg=44, bild=False)],
          css=r"""
.su{display:flex;gap:22px;align-items:center;justify-content:center;flex-wrap:wrap;width:100%}
.su .feld{display:grid;background:#1f2421;border:3px solid #1f2421;border-radius:14px;overflow:hidden;gap:1px;box-shadow:var(--sch)}
.su .z{background:#fff;display:grid;place-items:center;font-family:system-ui,-apple-system,sans-serif;font-weight:700;padding:0;border:0;line-height:1}
.su .z.fest{background:#eef3f7;color:#1f2421}
.su .z.neu{color:var(--sky-d);animation:pp .25s}
.su .z.mark{background:#f7f2e2}
.su .z.sel{background:var(--sun);box-shadow:inset 0 0 0 3px var(--gold)}
.su .z.falsch{background:#fbe5e2;animation:sh .35s}
.su .z.br{margin-right:2px}.su .z.bb{margin-bottom:2px}
.su .seite{display:flex;flex-direction:column;align-items:center;gap:12px}
.su .pad{display:grid;gap:8px}
.su .pad button{width:66px;height:66px;border-radius:16px;background:#fff;border:2px solid var(--ink);font:700 30px system-ui,-apple-system,sans-serif;box-shadow:var(--sch-k);padding:0}
.su .pad button:active{transform:scale(.94)}
.su .pad button.fertig{opacity:.3}
.herzen{font-size:26px;letter-spacing:2px}
""",
          js=r"""
var SU_BILD = { 4: ['🍎', '🍌', '🍇', '🍓'], 6: ['🐶', '🐱', '🐰', '🦊', '🐻', '🐸'] };
function boxMass(n) { return n === 4 ? [2, 2] : n === 6 ? [2, 3] : [3, 3]; }
function suOk(g, n, r, c, v) {
  var bm = boxMass(n), br = Math.floor(r / bm[0]) * bm[0], bc = Math.floor(c / bm[1]) * bm[1];
  for (var i = 0; i < n; i++) { if (g[r * n + i] === v || g[i * n + c] === v) return false; }
  for (var y = br; y < br + bm[0]; y++) for (var x = bc; x < bc + bm[1]; x++) if (g[y * n + x] === v) return false;
  return true;
}
function suFuell(g, n) {
  var k = g.indexOf(0); if (k < 0) return true;
  var vs = shuffle(range(n).map(function (x) { return x + 1; }));
  for (var i = 0; i < n; i++) { if (suOk(g, n, Math.floor(k / n), k % n, vs[i])) { g[k] = vs[i]; if (suFuell(g, n)) return true; g[k] = 0; } }
  return false;
}
// Anzahl Lösungen (höchstens 2 zählen)
function suZahl(g, n) {
  var best = -1, bestC = null;
  for (var k = 0; k < n * n; k++) if (!g[k]) {
    var c = []; for (var v = 1; v <= n; v++) if (suOk(g, n, Math.floor(k / n), k % n, v)) c.push(v);
    if (!c.length) return 0;
    if (!bestC || c.length < bestC.length) { best = k; bestC = c; if (c.length === 1) break; }
  }
  if (best < 0) return 1;
  var s = 0;
  for (var i = 0; i < bestC.length && s < 2; i++) { g[best] = bestC[i]; s += suZahl(g, n); }
  g[best] = 0; return s;
}
function suMach(n, weg) {
  var sol = range(n * n).map(function () { return 0; }); suFuell(sol, n);
  var g = sol.slice(), w = 0;
  shuffle(range(n * n)).forEach(function (k) { if (w >= weg) return; var v = g[k]; g[k] = 0; if (suZahl(g.slice(), n) === 1) w++; else g[k] = v; });
  return { sol: sol, start: g };
}
G.play = function (lv, api) {
  var idx = 0;
  function raetsel() {
    var n = lv.n, P = suMach(n, lv.weg), g = P.start.slice(), sel = -1, fehler = 0, fertig = false, bm = boxMass(n);
    var sym = function (v) { return lv.bild ? SU_BILD[n][v - 1] : String(v); };
    var breit = window.innerWidth > 760, avW = Math.min(window.innerWidth - 40, 900) - (breit ? 260 : 0), avH = window.innerHeight - (breit ? 200 : 330);
    var s = Math.floor(Math.min(84, avW / n, avH / n)); s = Math.max(34, s);
    api.stage.innerHTML = '';
    var box = document.createElement('div'); box.className = 'su';
    var o = '<div class="feld" style="grid-template-columns:repeat(' + n + ',' + s + 'px);grid-auto-rows:' + s + 'px;font-size:' + Math.round(s * (lv.bild ? .62 : .55)) + 'px">';
    for (var k = 0; k < n * n; k++) {
      var r = Math.floor(k / n), c = k % n;
      o += '<button class="z' + (g[k] ? ' fest' : '') + ((c + 1) % bm[1] === 0 && c < n - 1 ? ' br' : '') + ((r + 1) % bm[0] === 0 && r < n - 1 ? ' bb' : '') + '" data-k="' + k + '" aria-label="Zeile ' + (r + 1) + ', Spalte ' + (c + 1) + '">' + (g[k] ? sym(g[k]) : '') + '</button>';
    }
    o += '</div><div class="seite"><span class="herzen"></span><div class="pad" style="grid-template-columns:repeat(' + (n === 9 ? 3 : n === 6 ? 3 : 2) + ',66px)">';
    for (var v = 1; v <= n; v++) o += '<button data-v="' + v + '"' + (lv.bild ? ' style="font-size:36px"' : '') + '>' + sym(v) + '</button>';
    box.innerHTML = o + '</div></div>'; api.stage.appendChild(box);
    var feld = box.querySelector('.feld'), her = box.querySelector('.herzen');
    function herzen() { var x = ''; for (var i = 0; i < 3; i++) x += i < 3 - fehler ? '❤️' : '🤍'; her.textContent = x; }
    herzen();
    api.msg('<span class="em">🧩</span> Rätsel ' + (idx + 1) + ' von ' + G.n + ': Tippe auf ein leeres Feld und dann auf ' + (lv.bild ? 'ein Bild' : 'eine Zahl') + '.');
    function markiere() {
      var r = Math.floor(sel / n), c = sel % n, br = Math.floor(r / bm[0]), bc = Math.floor(c / bm[1]);
      Array.prototype.forEach.call(feld.children, function (z, k) {
        var r2 = Math.floor(k / n), c2 = k % n;
        z.classList.toggle('sel', k === sel);
        z.classList.toggle('mark', sel >= 0 && k !== sel && (r2 === r || c2 === c || (Math.floor(r2 / bm[0]) === br && Math.floor(c2 / bm[1]) === bc)));
      });
      Array.prototype.forEach.call(box.querySelectorAll('.pad button'), function (b) { var v = +b.dataset.v; b.classList.toggle('fertig', g.filter(function (x) { return x === v; }).length >= n); });
    }
    feld.onclick = function (e) { var z = e.target.closest('.z'); if (!z || fertig) return; var k = +z.dataset.k; if (g[k]) { sel = -1; markiere(); return; } sel = k; tone(520, 0.04, 'sine', 0.06); markiere(); };
    box.querySelector('.pad').onclick = function (e) {
      var b = e.target.closest('button'); if (!b || fertig) return;
      if (sel < 0) { api.msg('<span class="em">👆</span> Tippe zuerst auf ein leeres Feld.'); return; }
      var v = +b.dataset.v, z = feld.children[sel];
      if (P.sol[sel] === v) {
        g[sel] = v; z.textContent = sym(v); z.classList.remove('falsch'); z.classList.add('neu'); tone(660, 0.08, 'sine', 0.1);
        var leer = -1; for (var k = 0; k < n * n; k++) if (!g[k]) { leer = k; break; }
        sel = -1; markiere();
        if (leer < 0) {
          fertig = true;
          api.msg('<span class="em">🎉</span> Geschafft!' + (fehler === 0 ? ' Ganz ohne Fehler!' : ''));
          if (api.answer(fehler <= 2)) {
            var nb = document.createElement('button'); nb.className = 'go sun'; nb.textContent = 'Nächstes Rätsel →';
            nb.onclick = function () { idx++; raetsel(); };
            box.querySelector('.seite').innerHTML = ''; box.querySelector('.seite').appendChild(nb);
          }
        }
      } else {
        fehler++; herzen(); bad(); z.classList.remove('falsch'); void z.offsetWidth; z.classList.add('falsch');
        api.msg(fehler < 3 ? '<span class="em">🙈</span> Das passt hier nicht. Schau die Zeile, die Spalte und das Kästchen an.' : '<span class="em">💪</span> Keine Herzen mehr, aber mach das Rätsel trotzdem fertig!');
      }
    };
  }
  raetsel();
};
""")

    # ================================================================== Wasser-Weg
    spiel(id='wasser-weg', titel='Wasser-Weg', icon='🚰', fach='Knobeln', thema='Logik', stufe='1.–6. Klasse', sort=4, n=3,
          sterne={'modus': 'runde', 'n': 3},
          kurz='Röhren drehen, bis das Wasser zur Blume fliesst.',
          intro='Tippe auf eine Röhre, dann dreht sie sich. Baue einen Weg vom Wasserhahn bis zur Blume. Blaue Röhren haben schon Wasser.',
          levels=[dict(name='Leicht', info='4 × 4 Felder', s=4, min=5),
                  dict(name='Gut', info='5 × 5 Felder', s=5, min=7),
                  dict(name='Mittel', info='6 × 6 Felder', s=6, min=9),
                  dict(name='Schwer', info='7 × 7 Felder', s=7, min=12),
                  dict(name='Profi', info='8 × 8 Felder, langer Weg', s=8, min=16)],
          css=r"""
.ww{display:flex;flex-direction:column;align-items:center;gap:12px;width:100%}
.ww .rahmen{display:flex;align-items:stretch}
.ww .seitel,.ww .seiter{display:grid;flex:none}
.ww .seitel span,.ww .seiter span{display:grid;place-items:center;line-height:1}
.ww .netz{display:grid;background:#dfe9f1;border:3px solid #9cb7cc;border-radius:16px;padding:4px;gap:3px;box-shadow:var(--sch)}
.ww .ro{background:#fff;border-radius:10px;padding:0;border:0;display:block;transition:background .2s}
.ww .ro svg{display:block;width:100%;height:100%;transition:transform .18s ease}
.ww .ro .rohr{stroke:#b9c2c9}
.ww .ro.nass .rohr{stroke:#3f9be0}
.ww .ro.nass{background:#eaf5fd}
.ww .zaehler{color:var(--soft);font-size:19px}
.ww .bluehe{animation:pp .5s 2}
""",
          js=r"""
// Röhren: Bitmaske der offenen Seiten (1 oben, 2 rechts, 4 unten, 8 links)
var RX = [0, 1, 0, -1], RY = [-1, 0, 1, 0];
function dreh(m) { return ((m << 1) | (m >> 3)) & 15; }
function rohrSvg(m) {
  var o = '<svg viewBox="0 0 100 100" aria-hidden="true"><g class="rohr" stroke-width="22" stroke-linecap="round" fill="none">';
  [[50, 0], [100, 50], [50, 100], [0, 50]].forEach(function (p, i) { if (m & (1 << i)) o += '<line x1="50" y1="50" x2="' + p[0] + '" y2="' + p[1] + '"/>'; });
  return o + '</g></svg>';
}
function wegSuchen(N, min) {
  for (var t = 0; t < 4000; t++) {
    var sr = rnd(0, N - 1), tr = rnd(0, N - 1), weg = [[0, sr]], seen = {}; seen[0 + ',' + sr] = 1;
    var ok = (function geh() {
      var c = weg[weg.length - 1];
      if (c[0] === N - 1 && c[1] === tr) return weg.length >= min;
      if (weg.length > N * N) return false;
      var ds = shuffle([0, 1, 2, 3]);
      for (var i = 0; i < 4; i++) {
        var x = c[0] + RX[ds[i]], y = c[1] + RY[ds[i]];
        if (x < 0 || y < 0 || x >= N || y >= N || seen[x + ',' + y]) continue;
        seen[x + ',' + y] = 1; weg.push([x, y]);
        if (geh()) return true;
        weg.pop(); delete seen[x + ',' + y];
        if (Math.random() < .35) return false;
      }
      return false;
    })();
    if (ok) return { weg: weg, sr: sr, tr: tr };
  }
  return null;
}
function wasserMach(N, min) {
  var W = wegSuchen(N, min), soll = [], i, k;
  for (i = 0; i < N * N; i++) soll.push(0);
  W.weg.forEach(function (c, j) {
    var m = 0, k2 = c[1] * N + c[0];
    var vor = j === 0 ? [-1, c[1]] : W.weg[j - 1], nach = j === W.weg.length - 1 ? [N, c[1]] : W.weg[j + 1];
    [vor, nach].forEach(function (p) { for (var d = 0; d < 4; d++) if (c[0] + RX[d] === p[0] && c[1] + RY[d] === p[1]) m |= 1 << d; });
    soll[k2] = m;
  });
  var auf = {}; W.weg.forEach(function (c) { auf[c[1] * N + c[0]] = 1; });
  var formen = [5, 3, 5, 3, 7, 3];
  for (k = 0; k < N * N; k++) if (!auf[k]) { soll[k] = formen[rnd(0, formen.length - 1)]; for (var r = rnd(0, 3); r > 0; r--) soll[k] = dreh(soll[k]); }
  var ist = soll.map(function (m) { for (var r = rnd(0, 3); r > 0; r--) m = dreh(m); return m; });
  var mind = 0;
  W.weg.forEach(function (c) { var k3 = c[1] * N + c[0], m = ist[k3]; for (var r = 0; r < 4; r++) { if (m === soll[k3]) { mind += r; break; } m = dreh(m); } });
  return { N: N, ist: ist, sr: W.sr, tr: W.tr, mind: mind };
}
// Welche Felder bekommen Wasser? (vom Hahn links bei Zeile sr)
function nass(P) {
  var N = P.N, w = {}, q = [];
  var s = P.sr * N; if (P.ist[s] & 8) { w[s] = 1; q.push(s); }
  while (q.length) {
    var k = q.shift(), x = k % N, y = Math.floor(k / N);
    for (var d = 0; d < 4; d++) {
      if (!(P.ist[k] & (1 << d))) continue;
      var nx = x + RX[d], ny = y + RY[d]; if (nx < 0 || ny < 0 || nx >= N || ny >= N) continue;
      var n2 = ny * N + nx; if (w[n2] || !(P.ist[n2] & (1 << ((d + 2) % 4)))) continue;
      w[n2] = 1; q.push(n2);
    }
  }
  var z = P.tr * N + N - 1;
  return { w: w, ziel: !!(w[z] && (P.ist[z] & 2)) };
}
G.play = function (lv, api) {
  var idx = 0;
  function raetsel() {
    var P; do { P = wasserMach(lv.s, lv.min); } while (nass(P).ziel || P.mind < 2);
    var N = P.N, tipps = 0, fertig = false, rot = P.ist.map(function () { return 0; });
    var s = Math.floor(Math.min(84, (Math.min(window.innerWidth, 900) - 140) / N, (window.innerHeight - 300) / N)); s = Math.max(38, s);
    api.stage.innerHTML = '';
    var box = document.createElement('div'); box.className = 'ww';
    var side = function (cls, row, em) { var o = '<div class="' + cls + '" style="grid-template-rows:repeat(' + N + ',' + s + 'px);row-gap:3px;padding:7px 0;font-size:' + Math.round(s * .7) + 'px">'; for (var i = 0; i < N; i++) o += '<span>' + (i === row ? em : '') + '</span>'; return o + '</div>'; };
    var o = '<div class="zaehler"></div><div class="rahmen">' + side('seitel', P.sr, '🚰') + '<div class="netz" style="grid-template-columns:repeat(' + N + ',' + s + 'px);grid-auto-rows:' + s + 'px">';
    for (var k = 0; k < N * N; k++) o += '<button class="ro" data-k="' + k + '" aria-label="Röhre drehen">' + rohrSvg(P.ist[k]) + '</button>';
    box.innerHTML = o + '</div>' + side('seiter', P.tr, '🥀') + '</div>'; api.stage.appendChild(box);
    var netz = box.querySelector('.netz'), zl = box.querySelector('.zaehler'), blume = box.querySelectorAll('.seiter span')[P.tr];
    // Röhren in der Ausgangslage zeichnen und beim Drehen nur das Bild weiterdrehen
    function male() {
      var r = nass(P);
      Array.prototype.forEach.call(netz.children, function (b, k) { b.classList.toggle('nass', !!r.w[k]); b.firstChild.style.transform = 'rotate(' + (rot[k] * 90) + 'deg)'; });
      zl.textContent = 'Drehungen: ' + tipps;
      return r.ziel;
    }
    male();
    api.msg('<span class="em">💧</span> Rätsel ' + (idx + 1) + ' von ' + G.n + ': Bring das Wasser zur Blume!');
    netz.onclick = function (e) {
      var b = e.target.closest('.ro'); if (!b || fertig) return;
      var k = +b.dataset.k; P.ist[k] = dreh(P.ist[k]); rot[k]++; tipps++; tone(420 + rnd(0, 3) * 40, 0.04, 'square', 0.04);
      if (male()) {
        fertig = true; blume.textContent = '🌻'; blume.classList.add('bluehe'); good();
        var ok = tipps <= P.mind * 2 + 4;
        api.msg('<span class="em">🌻</span> Die Blume hat Wasser!' + (ok ? ' Mit ' + tipps + ' Drehungen.' : ' Versuch es nächstes Mal mit weniger Drehungen.'));
        if (api.answer(ok, true)) {
          var nb = document.createElement('button'); nb.className = 'go sun'; nb.textContent = 'Nächstes Rätsel →';
          nb.onclick = function () { idx++; raetsel(); };
          zl.textContent = ''; zl.appendChild(nb);
        }
      }
    };
  }
  raetsel();
};
""")
