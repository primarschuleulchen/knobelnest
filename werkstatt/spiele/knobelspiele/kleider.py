# Kleiderschrank (Englisch: clothes): Kleider im Schrank entdecken, benennen, schreiben, sprechen,
# my/your/his/her/our/their und Sätze «This is my dress.» / «These are my ties.».
# Wird von bauen.py aufgerufen: kleider.alle(spiel)
import base64, io, os
#
# Bilder: Schrankbild der Lehrerin (kleider_bilder/schrank-original.webp). Die Kleider schneidet
# kleider_ausschneiden.py aus (kleider_bilder/<id>.webp); im Spiel liegen sie genau auf dem Schrank.
# Mia und Noah sind hier als SVG gezeichnet.

K = 'stroke="#2b2f2c" stroke-width="2.6" stroke-linejoin="round" stroke-linecap="round"'
L = 'fill="none" stroke="#2b2f2c" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"'
W = 'fill="none" stroke="#fff" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" opacity=".75"'


# Wörter: en = Wort im Wortschatz, sg/pl = Einzahl/Mehrzahl auf Englisch (sg None = immer Mehrzahl),
# de = deutsches Wort mit Artikel, dg = Geschlecht (m/f/n, p = Mehrzahl), dn/dpl = Nomen ohne Artikel Einzahl/Mehrzahl
WORT = [
    dict(id='jumper', en='jumper', sg='jumper', pl='jumpers', de='der Pullover', dg='m', dn='Pullover', dpl='Pullover'),
    dict(id='tshirt', en='T-shirt', sg='T-shirt', pl='T-shirts', de='das T-Shirt', dg='n', dn='T-Shirt', dpl='T-Shirts'),
    dict(id='shirt', en='shirt', sg='shirt', pl='shirts', de='das Hemd', dg='n', dn='Hemd', dpl='Hemden'),
    dict(id='dress', en='dress', sg='dress', pl='dresses', de='das Kleid', dg='n', dn='Kleid', dpl='Kleider'),
    dict(id='skirt', en='skirt', sg='skirt', pl='skirts', de='der Rock', dg='m', dn='Rock', dpl='Röcke'),
    dict(id='trousers', en='trousers', sg=None, pl='trousers', de='die Hose', dg='f', dn='Hose', dpl='Hosen'),
    dict(id='shorts', en='shorts', sg=None, pl='shorts', de='die kurze Hose', dg='f', dn='kurze Hose', dpl='kurzen Hosen'),
    dict(id='jacket', en='jacket', sg='jacket', pl='jackets', de='die Jacke', dg='f', dn='Jacke', dpl='Jacken'),
    dict(id='coat', en='coat', sg='coat', pl='coats', de='der Mantel', dg='m', dn='Mantel', dpl='Mäntel'),
    dict(id='scarf', en='scarf', sg='scarf', pl='scarves', de='der Schal', dg='m', dn='Schal', dpl='Schals'),
    dict(id='hat', en='hat', sg='hat', pl='hats', de='der Hut', dg='m', dn='Hut', dpl='Hüte'),
    dict(id='cap', en='cap', sg='cap', pl='caps', de='die Kappe', dg='f', dn='Kappe', dpl='Kappen'),
    dict(id='tie', en='tie', sg='tie', pl='ties', de='die Krawatte', dg='f', dn='Krawatte', dpl='Krawatten'),
    dict(id='socks', en='socks', sg=None, pl='socks', de='die Socken', dg='p', dn='Socken', dpl='Socken'),
    dict(id='shoes', en='shoes', sg=None, pl='shoes', de='die Schuhe', dg='p', dn='Schuhe', dpl='Schuhe'),
    dict(id='boots', en='boots', sg=None, pl='boots', de='die Stiefel', dg='p', dn='Stiefel', dpl='Stiefel'),
    dict(id='gloves', en='gloves', sg=None, pl='gloves', de='die Handschuhe', dg='p', dn='Handschuhe', dpl='Handschuhe'),
]
# Was die Spracherkennung statt des Worts auch hören darf (gleich klingende Wörter)
AEHNLICH = {'tie': ['thai', 'tai', 'tye', 'ty', 'tied', 'tight'], 'tshirt': ['tshirt', 't shirt', 'tee shirt', 'teeshirt', 't-shirts', 'tshirts'],
            'socks': ['sox', 'sock'], 'hat': ['hats'], 'cap': ['caps', 'cup'], 'coat': ['coats', 'code'], 'scarf': ['scarves'],
            'shoes': ['shoe', 'shoos'], 'boots': ['boot'], 'gloves': ['glove'], 'jumper': ['jumpers', 'jump her'], 'shirt': ['shirts'],
            'dress': ['dresses'], 'skirt': ['skirts'], 'jacket': ['jackets'], 'trousers': ['trouser'], 'shorts': ['short']}


# ------------------------------------------------------------------ Bild der Lehrerin (kleider_bilder/schrank-original.webp, 1254 × 1254)
# Kasten jedes Kleidungsstücks im Bild (links, oben, rechts, unten); kleider_ausschneiden.py schneidet damit die Einzelbilder aus
BOX = {'hat': (285, 235, 492, 362), 'cap': (545, 235, 735, 340), 'scarf': (108, 320, 208, 642), 'tie': (1060, 320, 1142, 618),
       'jumper': (248, 452, 404, 624), 'tshirt': (380, 452, 504, 618), 'shirt': (480, 452, 624, 622), 'jacket': (598, 452, 738, 622),
       'dress': (752, 452, 880, 675), 'coat': (860, 452, 1004, 680), 'skirt': (258, 690, 420, 848), 'trousers': (428, 690, 555, 870),
       'shorts': (572, 690, 720, 826), 'boots': (798, 712, 990, 870), 'shoes': (282, 912, 450, 1032), 'socks': (522, 902, 675, 1032),
       'gloves': (772, 908, 962, 1032)}

# ------------------------------------------------------------------ Bilder einbetten (damit das Spiel auch als einzelne Datei läuft)
BILDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'kleider_bilder')


def data_url(name):
    with open(os.path.join(BILDER, name), 'rb') as f: return 'data:image/webp;base64,' + base64.b64encode(f.read()).decode()


def bilder():
    from PIL import Image
    s = Image.open(os.path.join(BILDER, 'schrank.webp')); x0, y0, x1, y1 = s.getbbox()
    w, h = x1 - x0, y1 - y0
    buf = io.BytesIO(); s.crop((x0, y0, x1, y1)).save(buf, 'WEBP', quality=80, method=6)
    bg = 'data:image/webp;base64,' + base64.b64encode(buf.getvalue()).decode()
    # Plätze in Prozent des zugeschnittenen Schranks
    platz = {}
    for k, (a, b, c, d) in BOX.items():
        it = Image.open(os.path.join(BILDER, k + '.webp')); bx = it.getbbox()
        a2, b2, c2, d2 = a + bx[0], b + bx[1], a + bx[2], b + bx[3]
        platz[k] = [round((a2 - x0) / w * 100, 3), round((b2 - y0) / h * 100, 3), round((c2 - a2) / w * 100, 3), round((d2 - b2) / h * 100, 3)]
    return platz, w, h, bg


def schrank():
    platz, w, h, bg = bilder()
    o = [f'<div class="schrank" style="aspect-ratio:{w}/{h}" role="group" aria-label="Kleiderschrank"><img class="bg" src="{bg}" alt="">']
    for w0 in WORT:
        k = w0['id']; a, b, c, d = platz[k]
        o.append(f'<button class="it" data-id="{k}" aria-label="{w0["en"]}" style="left:{a}%;top:{b}%;width:{c}%;height:{d}%"><img alt=""></button>')
    return ''.join(o) + '</div>'


# ------------------------------------------------------------------ Mia und Noah (Bild der Lehrerin kinder-original.webp, ausgeschnitten in kleider_ausschneiden.py)
def kind_bild(k):
    return f'<img class="kind-bild" alt="" src="{data_url(k + ".webp")}">'


def logo():
    # Logo des Spiels (rund, Goldrand im Bild), eingebettet wie bei «Im Museum»
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logos', 'kleiderschrank.webp'), 'rb') as f:
        return '<img class="logo" alt="" src="data:image/webp;base64,' + base64.b64encode(f.read()).decode() + '">'


def alle(spiel):
    items = [dict(w) for w in WORT]
    spiel(id='kleiderschrank', titel='Kleiderschrank', icon=logo(), fach='Englisch', thema='Clothes', stufe='3.–6. Klasse', sort=1, n=10,
          sterne={'modus': 'runde', 'n': 10},
          kurz='Kleider auf Englisch: anschauen, hören, schreiben, sprechen und «This is my dress.»',
          intro='Im Schrank hängen viele Kleider. Wie heissen sie auf Englisch? Hör gut zu und sprich nach!',
          levels=[dict(name='Entdecken', info='Antippen, hören und finden', t=0),
                  dict(name='Auswählen', info='Wie heisst es auf Englisch?', t=1),
                  dict(name='Schreiben', info='Das englische Wort schreiben', t=2),
                  dict(name='Sprechen', info='Das Wort laut sagen 🎤', t=3),
                  dict(name='my, your, his, her', info='Wem gehört es?', t=4),
                  dict(name='Sätze', info='This is my … / These are my …', t=5)],
          daten={'items': items, 'png': {w['id']: data_url('karte-' + w['id'] + '.webp') for w in WORT}, 'sp': {w['id']: data_url(w['id'] + '.webp') for w in WORT}, 'schrank': schrank(), 'mia': kind_bild('mia'), 'eule': kind_bild('eule').replace('kind-bild', 'eule-bild'), 'noah': kind_bild('noah'), 'aehnlich': AEHNLICH},
          css=CSS, js=JS)


CSS = r"""
.ks{display:flex;flex-direction:column;align-items:center;gap:12px;width:100%}
.schrank{position:relative;width:min(100%,640px,calc((100vh - 250px) * 1.13))}
.schrank .bg{display:block;width:100%;height:100%;pointer-events:none}
.schrank .it{position:absolute;padding:0;border:0;background:none;cursor:pointer;transform-origin:center;transition:transform .15s,filter .15s;outline:none}
.schrank .it img{display:block;width:100%;height:100%;pointer-events:none}
.schrank .it:hover,.schrank .it:focus-visible{transform:scale(1.06)}
.schrank .it.an{filter:drop-shadow(0 0 10px #f0c24b) drop-shadow(0 0 4px #f0c24b);transform:scale(1.08)}
.schrank .it.no{animation:wk2 .4s}
@keyframes wk2{25%{transform:rotate(-4deg)}75%{transform:rotate(4deg)}}
.schrank .it.seen{filter:drop-shadow(0 0 3px rgba(240,194,75,.9))}
.schrank .it.seen.an{filter:drop-shadow(0 0 10px #f0c24b) drop-shadow(0 0 4px #f0c24b)}
.wortkarte{min-height:64px;display:flex;align-items:center;gap:16px;background:#fff;border:2px solid var(--line);border-radius:20px;padding:6px 18px;box-shadow:var(--sch-k)}
.wortkarte b{font-size:clamp(30px,6.6vw,42px);color:var(--sky-d);font-weight:400}
.wortkarte span{color:var(--soft);font-size:22px}
.wortkarte .wk{display:flex;align-items:center}
.wortkarte .de2{border-left:2px solid var(--line2);padding-left:16px;margin-left:6px}
.laut{display:inline-grid;place-items:center;width:52px;height:52px;border-radius:50%;background:var(--sky);border:2px solid var(--ink);font-size:24px;box-shadow:var(--sch-k);flex:none}
.laut:active{transform:scale(.94)}
.bild{width:min(56vw,230px);aspect-ratio:1;display:grid;place-items:center;background:#fff;border:3px solid var(--gold);border-radius:30px;box-shadow:inset 0 0 0 6px #fff,var(--sch);padding:16px;position:relative}
.bild .art{width:100%;height:100%;display:flex;align-items:center;justify-content:center}
.bild .art img{max-width:100%;max-height:100%;object-fit:contain;display:block;filter:drop-shadow(0 3px 4px rgba(63,120,168,.18))}
.bild .art.zwei img{max-width:62%}.bild .art.zwei img+img{margin-left:-14%;margin-top:-18%}
.bild .laut{position:absolute;right:-14px;bottom:-14px}
.wahl{display:grid;grid-template-columns:1fr 1fr;gap:12px;width:min(100%,560px)}
.wahl button{background:#fff;border:2px solid var(--ink);border-radius:20px;box-shadow:var(--sch-k);min-height:70px;padding:8px;font-size:clamp(26px,5.6vw,34px);transition:transform .12s}
.wahl button:active{transform:scale(.96)}
.wahl button.ok{background:#e7f3df;border-color:var(--ok)}.wahl button.no{background:#fbe5e2;border-color:var(--no)}.wahl button.hint{background:var(--sun);border-color:var(--gold)}
.schreib{display:flex;gap:10px;width:min(100%,480px)}
.schreib input{flex:1;min-width:0;font-family:inherit;font-size:32px;padding:6px 16px;border-radius:18px;border:2px solid var(--ink);background:#fff;color:var(--ink);text-align:center;box-shadow:var(--sch-k)}
.schreib input:focus{outline:3px solid var(--gold);outline-offset:2px}
.schreib input.ok{background:#e7f3df;border-color:var(--ok)}.schreib input.no{background:#fbe5e2;border-color:var(--no)}
.luecke{font-size:32px;letter-spacing:.18em;color:var(--sky-d)}
.mik{width:118px;height:118px;border-radius:50%;background:var(--rose);border:3px solid var(--ink);font-size:52px;box-shadow:var(--sch);display:grid;place-items:center}
.mik.hoert{background:#fbe5e2;animation:puls 1s infinite}
@keyframes puls{50%{box-shadow:0 0 0 14px rgba(200,87,78,.18),var(--sch)}}
.gehoert{color:var(--soft);font-size:20px;min-height:26px;text-align:center}
.buehne{width:min(100%,620px);display:grid;grid-template-columns:1fr 1.15fr 1fr;grid-template-rows:auto auto;align-items:end;column-gap:6px;row-gap:6px}
.buehne .sprech{grid-row:1;grid-column:1/4;height:92px;display:flex;align-items:flex-end;justify-content:flex-start}
.blase{position:relative;background:#fff;border:2px solid var(--ink);border-radius:18px;padding:8px 12px;font-size:clamp(19px,4.4vw,24px);box-shadow:var(--sch-k);line-height:1.2}
.blase::after{content:"";position:absolute;bottom:-11px;left:30px;width:18px;height:18px;background:#fff;border-right:2px solid var(--ink);border-bottom:2px solid var(--ink);transform:rotate(45deg)}
.blase.r::after{left:auto;right:30px}
.sprech .blase{width:max-content;max-width:100%;margin-bottom:12px;text-align:center}
.sprech .blase::after{left:calc(var(--t1,30px) - 10px)}
.sprech .blase.zwei::before{content:"";position:absolute;bottom:-11px;left:calc(var(--t2,60px) - 10px);width:18px;height:18px;background:#fff;border-right:2px solid var(--ink);border-bottom:2px solid var(--ink);transform:rotate(45deg)}
.rueck{min-height:44px;font-size:24px;text-align:center;margin:-6px 0 8px;max-width:760px;line-height:1.3}
.rueck .em{font-size:32px;vertical-align:middle;margin:0 4px;line-height:1}
.erzaehl{grid-row:1;grid-column:1/4;height:92px;display:flex;align-items:center;gap:22px;justify-content:flex-start;padding-left:calc(50% - 110px)}
.eule-bild{width:auto;height:78px;display:block;flex:none}
.erzaehl .blase::after{left:-11px;top:50%;bottom:auto;transform:translateY(-50%) rotate(135deg)}
.kind{grid-row:2;display:flex;flex-direction:column;align-items:center;position:relative}
.kind-bild{height:min(30vh,230px);width:auto;max-width:100%;display:block;object-fit:contain}
.ring{width:150px;height:150px;background:none;border:0;padding:0;box-shadow:0 8px 18px rgba(63,120,168,.18)}.ring .logo{width:100%;height:100%;display:block;border-radius:50%}
.kind .nm2{background:var(--sun);border-radius:10px;padding:0 10px;font-size:20px;margin-top:2px}
.ding{grid-row:2;grid-column:2;display:flex;align-items:center;padding-bottom:34px}
.ding .bild{width:min(30vw,150px);padding:10px;border-width:3px}
.ding.l{justify-content:flex-start}.ding.r{justify-content:flex-end}.ding.m{justify-content:center}
.ding.l .bild::before,.ding.r .bild::before{content:"";position:absolute;top:50%;width:16px;height:16px;background:#fff;border:3px solid var(--gold);border-right:0;border-top:0;transform:translateY(-50%) rotate(45deg)}
.ding.l .bild::before{left:-10px}.ding.r .bild::before{right:-10px;transform:translateY(-50%) rotate(-135deg)}
.wer{grid-column:1/4;text-align:center;color:var(--soft);font-size:19px;margin-top:-4px}
.satz{min-height:66px;width:min(100%,600px);display:flex;flex-wrap:wrap;gap:8px;justify-content:center;align-items:center;background:#fff;border:2px dashed var(--line2);border-radius:20px;padding:8px}
.satz.ok{border:2px solid var(--ok);background:#f1f7ec}.satz.no{border-color:var(--no)}
.kaertli{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;width:min(100%,600px)}
.kaertli button,.satz button{background:#fff;border:2px solid var(--ink);border-radius:14px;padding:6px 14px;min-height:50px;font-size:clamp(24px,5.2vw,30px);box-shadow:var(--sch-k)}
.satz button{background:var(--sky)}
.kaertli button.weg{visibility:hidden}
.satz .pkt{font-size:26px}
.de{font-size:clamp(22px,5vw,28px);text-align:center}
@media (max-height:700px){.bild{width:min(44vw,170px)}.mik{width:92px;height:92px;font-size:40px}}
/* Stufe 1: Wortkarte oben, Schrank, Knopf unten (hochkant); im Querformat Schrank links, Rest rechts */
.ks.quer .seite{display:contents}.ks.quer .wortkarte{order:1}.ks.quer .schrank{order:2}.ks.quer .seite .go{order:3}
.ks.quer .schrank{width:min(100%,640px,calc((100vh - 330px) * 1.13))}
/* iPad und Laptop quer: alles auf einen Bildschirm ohne Scrollen */
@media (orientation:landscape) and (min-width:820px) and (max-height:920px){
  .ring{width:112px;height:112px}.kopf h1{font-size:36px;margin-top:6px}.kopf p{font-size:19px}
  .lvs{grid-template-columns:1fr 1fr;max-width:920px;gap:10px}.lv{min-height:70px;padding:8px 16px}
  .msg{min-height:0;margin-bottom:4px}.rueck{min-height:34px;margin:0 0 4px}
  .ks.quer{flex-direction:row;align-items:center;justify-content:center;gap:30px}
  .ks.quer .seite{display:flex;flex-direction:column;align-items:center;gap:18px;width:300px;flex:none}
  .ks.quer .schrank{order:0;width:min(60vw,calc((100vh - 195px) * 1.13))}
  .ks.zs{display:grid;grid-template-columns:minmax(0,1.05fr) minmax(0,1fr);align-items:center;align-content:center;column-gap:30px;row-gap:12px;max-width:1120px}
  .ks.zs .buehne{grid-column:1;grid-row:1 / span 4;width:100%}
  .ks.zs > :not(.buehne){grid-column:2;justify-self:center}
  .ks.zs .wahl{grid-template-columns:1fr}.ks.zs .wahl button{min-height:58px;width:100%}
  .ks.zs .wahl{width:min(100%,400px)}
  .kind-bild{height:min(40vh,260px)}
}
@media (max-width:520px){.kind-bild{height:min(26vh,170px)}.ding .bild{width:min(32vw,118px)}.buehne .sprech,.erzaehl{height:84px}.kaertli button,.satz button{min-height:44px;padding:4px 12px}}
"""

JS = r"""
var IT = D.items, ITM = {}; IT.forEach(function (x) { ITM[x.id] = x; });
var BOTH = 'Mia und Noah';
// ---------- Bilder
function art(id, zwei) {
  var im = '<img src="' + D.png[id] + '" alt="">';
  return '<div class="art' + (zwei ? ' zwei' : '') + '" data-k="' + id + '">' + im + (zwei ? im : '') + '</div>';
}
// ---------- Sprechen (Vorlesen auf Englisch)
var VOICE = null;
function voices() {
  try {
    var v = speechSynthesis.getVoices(), gb = v.filter(function (x) { return /^en[-_]GB/i.test(x.lang); });
    var pref = gb.filter(function (x) { return /female|kate|serena|libby|sonia|martha|google uk english female/i.test(x.name); });
    VOICE = pref[0] || gb[0] || v.filter(function (x) { return /^en[-_]/i.test(x.lang); })[0] || null;
  } catch (e) {}
}
try { voices(); speechSynthesis.onvoiceschanged = voices; } catch (e) {}
function say(t, rate) {
  try {
    speechSynthesis.cancel();
    var u = new SpeechSynthesisUtterance(t); u.lang = 'en-GB'; if (VOICE) u.voice = VOICE; u.rate = rate || 0.82; u.pitch = 1.05;
    speechSynthesis.speak(u);
  } catch (e) {}
}
function lautBtn(t) { var b = document.createElement('button'); b.className = 'laut'; b.setAttribute('aria-label', 'Anhören'); b.textContent = '🔊'; b.onclick = function (e) { e.stopPropagation(); say(t); }; return b; }
function norm(s) { return String(s || '').toLowerCase().replace(/[’']/g, '').replace(/[^a-z\- ]/g, ' ').replace(/\s+/g, ' ').trim(); }
function klein(s) { return norm(s).replace(/-/g, '').replace(/ /g, ''); }
function abstand(a, b) {
  var d = [], i, j; for (i = 0; i <= a.length; i++) { d[i] = [i]; } for (j = 0; j <= b.length; j++) d[0][j] = j;
  for (i = 1; i <= a.length; i++) for (j = 1; j <= b.length; j++) d[i][j] = Math.min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1));
  return d[a.length][b.length];
}
// Abwechslung: jedes Stück kommt, bevor eines doppelt kommt
function reihe(n, filt) { var a = [], src = IT.filter(filt || function () { return true; }); while (a.length < n) a = a.concat(shuffle(src)); return a.slice(0, n); }
// Rückmeldung («Richtig!») unter der Aufgabe; die Aufgabe selbst bleibt stehen
function fb(t) {
  var r = document.getElementById('rueck'), m = document.getElementById('msg');
  if (!r && m) { r = document.createElement('div'); r.id = 'rueck'; r.className = 'rueck'; m.parentNode.insertBefore(r, m.nextSibling); }
  if (r) r.innerHTML = t || '';
}
function neu(c, html) { var e = document.createElement('div'); if (c) e.className = c; if (html != null) e.innerHTML = html; return e; }

// ---------- Stufe 1: Schrank entdecken, dann finden
function stufeSchrank(api) {
  var w = neu('ks quer'); api.stage.appendChild(w);
  var karte = neu('wortkarte', '<span>Tippe auf ein Kleidungsstück im Schrank.</span>');
  var holder = neu('', D.schrank); var sv = holder.firstChild;
  Array.prototype.forEach.call(sv.querySelectorAll('.it'), function (g) { g.querySelector('img').src = D.sp[g.getAttribute('data-id')]; });
  var los = document.createElement('button'); los.className = 'go sun'; los.textContent = 'Finde die Kleider! →';
  var seite = neu('seite'); seite.appendChild(karte); seite.appendChild(los); w.appendChild(sv); w.appendChild(seite);
  var seen = {}, phase = 'schau', liste = reihe(G.n), k = 0, ziel = null, lock = false;
  api.msg('Schau in den Schrank! Tippe auf die Kleider und hör gut zu.');
  function itEl(id) { return sv.querySelector('[data-id="' + id + '"]'); }
  function zeig(id) {
    var x = ITM[id]; karte.innerHTML = ''; karte.appendChild(lautBtn(x.en));
    karte.appendChild(neu('wk', '<b>' + h(x.en) + '</b><span class="de2">' + h(x.de) + '</span>'));
  }
  function frage() {
    ziel = liste[k]; lock = false; fb('');
    var t = 'Find the ' + ziel.en + '!';
    karte.innerHTML = ''; karte.appendChild(lautBtn(t)); karte.appendChild(neu('', '<b>Find the ' + h(ziel.en) + '!</b>'));
    api.msg('Hör zu und tippe auf das richtige Kleidungsstück.');
    say(t);
  }
  Array.prototype.forEach.call(sv.querySelectorAll('.it'), function (g) {
    function tap() {
      var id = g.getAttribute('data-id');
      if (phase === 'schau') {
        Array.prototype.forEach.call(sv.querySelectorAll('.it.an'), function (e) { e.classList.remove('an'); });
        g.classList.add('an', 'seen'); seen[id] = 1; zeig(id); say(ITM[id].en);
        var n = Object.keys(seen).length;
        if (n >= 6) los.classList.add('pop');
        fb((n >= IT.length ? 'Du hast alles angeschaut! Jetzt «Finde die Kleider!»' : n + ' von ' + IT.length + ' angeschaut.'));
        return;
      }
      if (lock || !ziel) return; lock = true;
      var ok = id === ziel.id, rich = itEl(ziel.id);
      Array.prototype.forEach.call(sv.querySelectorAll('.it.an'), function (e) { e.classList.remove('an'); });
      rich.classList.add('an');
      if (!ok) { g.classList.remove('no'); void g.offsetWidth; g.classList.add('no'); }
      say(ok ? ziel.en : 'This is the ' + ziel.en + '.');
      fb(ok ? '<span class="em">✨</span> Yes! <b>' + h(ziel.en) + '</b> = ' + h(ziel.de) : '<span class="em">💡</span> Das ist <b>' + h(ITM[id].en) + '</b>. Gesucht war <b>' + h(ziel.en) + '</b> (leuchtet).');
      k++;
      if (!api.answer(ok)) return;
      api.later(function () { rich.classList.remove('an'); g.classList.remove('no'); frage(); }, ok ? 1300 : 2400);
    }
    g.addEventListener('click', tap);
    g.addEventListener('keydown', function (e) { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); tap(); } });
  });
  los.onclick = function () {
    phase = 'finden'; los.remove();
    Array.prototype.forEach.call(sv.querySelectorAll('.it'), function (e) { e.classList.remove('an', 'seen'); });
    frage();
  };
}

// ---------- Stufe 2: Auswählen
function stufeWahl(api) {
  var w = neu('ks'); api.stage.appendChild(w); var liste = reihe(G.n), k = 0;
  function frage() {
    var x = liste[k], lock = false; w.innerHTML = ''; fb('');
    var b = neu('bild', art(x.id)); w.appendChild(b);
    var opts = [x].concat(pick(IT.filter(function (y) { return y.id !== x.id; }), 3));
    var wahl = neu('wahl'); w.appendChild(wahl);
    api.msg('Wie heisst das auf Englisch?');
    shuffle(opts).forEach(function (o) {
      var bt = document.createElement('button'); bt.textContent = o.en;
      bt.onclick = function () {
        if (lock) return; lock = true; var ok = o.id === x.id;
        bt.classList.add(ok ? 'ok' : 'no');
        if (!ok) Array.prototype.forEach.call(wahl.children, function (c) { if (c.textContent === x.en) c.classList.add('hint'); });
        say(x.en); b.appendChild(lautBtn(x.en));
        fb(ok ? '<span class="em">' + pick(['✨', '🌟', '👏'], 1)[0] + '</span> Richtig! <b>' + h(x.en) + '</b> = ' + h(x.de) : '<span class="em">💡</span> Das ist <b>' + h(x.en) + '</b> (' + h(x.de) + ').');
        k++; if (!api.answer(ok)) return;
        api.later(frage, ok ? 1300 : 2300);
      };
      wahl.appendChild(bt);
    });
  }
  frage();
}

// ---------- Stufe 3: Schreiben
function stimmt(x, s) {
  var a = klein(s).replace(/^(a|an|the)(?=[a-z])/, ''); if (/^(a|an|the) /.test(norm(s))) a = klein(norm(s).replace(/^(a|an|the) /, ''));
  var gut = [x.en, x.pl, x.sg].filter(Boolean).map(klein);
  return gut.indexOf(a) >= 0;
}
function stufeSchreiben(api) {
  var w = neu('ks'); api.stage.appendChild(w); var liste = reihe(G.n), k = 0;
  function frage() {
    var x = liste[k], vers = 0, lock = false; w.innerHTML = ''; fb('');
    var b = neu('bild', art(x.id)); w.appendChild(b);
    var lu = neu('luecke', ''); w.appendChild(lu);
    var f = neu('schreib', '<input type="text" autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false" enterkeyhint="done" aria-label="Englisches Wort"><button class="go">Prüfen</button>');
    w.appendChild(f);
    var inp = f.querySelector('input'), btn = f.querySelector('button');
    api.msg('<span class="em">✏️</span> Schreib das englische Wort. <small>(' + h(x.de) + ')</small>');
    setTimeout(function () { try { inp.focus(); } catch (e) {} }, 60);
    function pruef() {
      if (lock) return; if (!inp.value.trim()) { inp.focus(); return; }
      var ok = stimmt(x, inp.value);
      if (!ok && vers === 0) {
        vers = 1; inp.classList.add('no'); f.classList.remove('shake'); void f.offsetWidth; f.classList.add('shake'); bad();
        lu.textContent = x.en.split('').map(function (c, i) { return i === 0 || c === '-' ? c : '_'; }).join(' ');
        b.appendChild(lautBtn(x.en)); say(x.en);
        fb('<span class="em">💡</span> Noch nicht. Tipp: So viele Buchstaben hat das Wort. Hör nochmal zu!');
        api.later(function () { inp.classList.remove('no'); inp.select(); }, 600);
        return;
      }
      lock = true; inp.classList.add(ok ? 'ok' : 'no'); inp.disabled = true;
      if (!ok) { lu.textContent = x.en; }
      if (vers === 0 || !ok) b.appendChild(lautBtn(x.en));
      say(x.en);
      fb(ok ? '<span class="em">🌟</span> Richtig geschrieben: <b>' + h(x.en) + '</b>!' : '<span class="em">📝</span> So schreibt man es: <b>' + h(x.en) + '</b>');
      k++; if (!api.answer(ok)) return;
      api.later(frage, ok ? 1400 : 2800);
    }
    btn.onclick = pruef;
    inp.addEventListener('keydown', function (e) { if (e.key === 'Enter') { e.preventDefault(); pruef(); } });
  }
  frage();
}

// ---------- Stufe 4: Sprechen (Spracherkennung des Geräts; sonst aufnehmen und selber vergleichen)
var SR = window.SpeechRecognition || window.webkitSpeechRecognition, SR_AUS = false;
function gehoertOk(x, alts) {
  var ziele = [x.en, x.pl, x.sg].filter(Boolean).map(klein).concat((D.aehnlich[x.id] || []).map(klein));
  for (var i = 0; i < alts.length; i++) {
    var t = norm(alts[i]), ganz = klein(t), woerter = t.split(' ');
    for (var j = 0; j < ziele.length; j++) {
      var z = ziele[j];
      if (ganz === z || ganz.indexOf(z) >= 0 && z.length >= 4) return true;
      for (var m = 0; m < woerter.length; m++) {
        var wd = klein(woerter[m]), wd2 = m + 1 < woerter.length ? wd + klein(woerter[m + 1]) : '';
        if (wd === z || wd2 === z || (z.length >= 5 && abstand(wd, z) <= 1)) return true;
      }
    }
  }
  return false;
}
function stufeSprechen(api) {
  var w = neu('ks'); api.stage.appendChild(w); var liste = reihe(G.n), k = 0, rec = null;
  function frage() {
    var x = liste[k], vers = 0, lock = false; w.innerHTML = ''; fb('');
    var b = neu('bild', art(x.id)); b.appendChild(lautBtn(x.en)); w.appendChild(b);
    var mik = document.createElement('button'); mik.className = 'mik'; mik.setAttribute('aria-label', 'Sprechen'); mik.textContent = '🎤';
    var info = neu('gehoert', ''); w.appendChild(mik); w.appendChild(info);
    var selbst = !SR || SR_AUS;
    api.msg(selbst ? '<span class="em">🗣️</span> Sag das Wort laut auf Englisch! <small>Tippe auf 🔊 zum Vorhören, dann auf 🎤.</small>'
                   : '<span class="em">🗣️</span> Tippe auf 🎤 und sag das Wort auf Englisch! <small>(🔊 = vorhören)</small>');
    function fertig(ok) {
      if (lock) return; lock = true; mik.disabled = true; mik.classList.remove('hoert');
      say(x.en);
      fb(ok ? '<span class="em">🌟</span> Super ausgesprochen: <b>' + h(x.en) + '</b>!' : '<span class="em">👂</span> Hör nochmal gut zu: <b>' + h(x.en) + '</b>');
      k++; if (!api.answer(ok)) return;
      api.later(frage, ok ? 1500 : 2600);
    }
    function selbstPruefen() {
      // Ohne Spracherkennung: aufnehmen, anhören und selber vergleichen
      info.innerHTML = '';
      var r = neu('row', '<button class="go alt" data-x="ja">👍 Klang gleich</button><button class="go alt" data-x="nochmal">🔁 Nochmal</button>');
      function wahl() { w.appendChild(r); r.querySelector('[data-x="ja"]').onclick = function () { r.remove(); fertig(true); }; r.querySelector('[data-x="nochmal"]').onclick = function () { r.remove(); info.textContent = ''; }; }
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia || !window.MediaRecorder) { info.textContent = 'Sag das Wort laut. Klang es wie bei 🔊?'; wahl(); return; }
      navigator.mediaDevices.getUserMedia({ audio: true }).then(function (st) {
        var mr = new MediaRecorder(st), teile = [];
        mr.ondataavailable = function (e) { if (e.data && e.data.size) teile.push(e.data); };
        mr.onstop = function () {
          st.getTracks().forEach(function (t) { t.stop(); }); mik.classList.remove('hoert');
          var url = URL.createObjectURL(new Blob(teile, { type: mr.mimeType || 'audio/webm' })), a = new Audio(url);
          info.innerHTML = 'So klingst du: '; var p = document.createElement('button'); p.className = 'laut'; p.textContent = '▶️'; p.onclick = function () { a.play(); }; info.appendChild(p);
          a.play().catch(function () {}); wahl();
        };
        mik.classList.add('hoert'); info.textContent = 'Ich nehme auf … sprich jetzt!'; mr.start();
        api.later(function () { if (mr.state !== 'inactive') mr.stop(); }, 2600);
      }).catch(function () { info.textContent = 'Sag das Wort laut. Klang es wie bei 🔊?'; wahl(); });
    }
    mik.onclick = function () {
      if (lock || mik.classList.contains('hoert')) return;
      try { speechSynthesis.cancel(); } catch (e) {}
      if (!SR || SR_AUS) { selbstPruefen(); return; }
      var r; try { r = new SR(); } catch (e) { SR_AUS = true; selbstPruefen(); return; }
      rec = r; r.lang = 'en-GB'; r.interimResults = false; r.maxAlternatives = 6; r.continuous = false;
      var bekommen = false, stopp = setTimeout(function () { try { r.stop(); } catch (e) {} }, 6000);
      r.onresult = function (e) {
        bekommen = true; var alts = [];
        for (var i = 0; i < e.results.length; i++) for (var j = 0; j < e.results[i].length; j++) alts.push(e.results[i][j].transcript);
        if (gehoertOk(x, alts)) { info.textContent = 'Ich habe gehört: «' + alts[0] + '» ✓'; fertig(true); return; }
        vers++; info.textContent = 'Ich habe gehört: «' + (alts[0] || '…') + '»';
        if (vers >= 3) { fertig(false); return; }
        bad(); fb('<span class="em">🔁</span> Fast! Hör mit 🔊 zu und versuch es nochmal.');
      };
      r.onerror = function (e) {
        if (e.error === 'not-allowed' || e.error === 'service-not-allowed' || e.error === 'audio-capture') {
          SR_AUS = true; info.textContent = 'Das Mikrofon ist hier gesperrt. Du kannst trotzdem üben:'; mik.classList.remove('hoert'); api.later(selbstPruefen, 900); return;
        }
        if (e.error === 'no-speech') { info.textContent = 'Ich habe nichts gehört. Tippe auf 🎤 und sprich etwas lauter.'; return; }
        if (e.error === 'aborted') return;
        // z. B. «network»: Die Spracherkennung geht hier nicht, also selber vergleichen
        SR_AUS = true; mik.classList.remove('hoert'); info.textContent = 'Zuhören geht gerade nicht. Du kannst trotzdem üben:'; api.later(selbstPruefen, 900);
      };
      r.onend = function () { clearTimeout(stopp); mik.classList.remove('hoert'); if (!bekommen && info.textContent === 'Ich höre zu …') info.textContent = 'Ich habe nichts gehört. Nochmal!'; };
      try { r.start(); mik.classList.add('hoert'); info.textContent = 'Ich höre zu …'; } catch (e) { SR_AUS = true; selbstPruefen(); }
    };
  }
  frage();
}

// ---------- Stufe 5 und 6: Mia und Noah
// Besitzer und wer spricht: self = das Kind über sich, other = ein Kind zum anderen, beide-self = beide Kinder zusammen (our),
// eule = die Eule erzählt (his, her, their), eule-zu-beiden = die Eule spricht mit beiden (your für mehrere, «euer»)
var PR = {
  my: { de: 'mein', wer: 'self' }, your: { de: 'dein', wer: 'other' }, his: { de: 'sein', wer: 'noah' },
  her: { de: 'ihr', wer: 'mia' }, our: { de: 'unser', wer: 'beide-self' }, their: { de: 'ihr', wer: 'beide' },
  your2: { de: 'euer', wer: 'eule-zu-beiden' }
};
var PAAR = { my: 'your', your: 'my', his: 'her', her: 'his', our: 'their', their: 'our' };
function aufgabe(x, mehrErlaubt) {
  var key = pick(['my', 'my', 'your', 'your', 'his', 'his', 'her', 'her', 'our', 'our', 'their', 'their', 'your2'], 1)[0], spr = 'eule', own, mit = null;
  var c = PR[key].wer, p = key === 'your2' ? 'your' : key;
  if (c === 'self') { own = pick(['mia', 'noah'], 1)[0]; spr = own; }
  else if (c === 'other') { own = pick(['mia', 'noah'], 1)[0]; spr = own === 'mia' ? 'noah' : 'mia'; mit = own; }
  else if (c === 'beide-self') { own = 'beide'; spr = 'beide'; }
  else if (c === 'eule-zu-beiden') { own = 'beide'; mit = 'beide'; }
  else own = c;
  var enPl = !x.sg || (mehrErlaubt && Math.random() < 0.45);
  var dePl = x.dg === 'p' || (x.sg && enPl);
  var g = dePl ? 'p' : x.dg, noun = dePl && x.sg ? x.dpl : x.dn, fe = g === 'f' || g === 'p';
  var poss = key === 'your2' ? (fe ? 'eure' : 'euer') : PR[key].de + (fe ? 'e' : '');
  return { x: x, key: key, p: p, own: own, spr: spr, mit: mit, enPl: enPl, zwei: !!(x.sg && enPl),
    deP: poss + ' ' + noun, deS: (dePl ? 'Das sind ' : 'Das ist ') + poss + ' ' + noun + '.',
    word: enPl ? x.pl : x.sg, enP: p + ' ' + (enPl ? x.pl : x.sg),
    enS: (enPl ? 'These are ' : 'This is ') + p + ' ' + (enPl ? x.pl : x.sg) };
}
var NAME = { mia: 'Mia', noah: 'Noah', beide: 'Mia und Noah' };
function buehne(a, text) {
  var b = neu('buehne');
  // obere Zeile hat immer dieselbe Höhe (Kinder und Bild springen nicht)
  if (a.spr !== 'eule') { var bl = neu('sprech', '<div class="blase">' + text + '</div>'); bl.dataset.wer = a.spr; b.appendChild(bl); }
  else b.appendChild(neu('erzaehl', D.eule + '<div class="blase">' + text + '</div>'));
  var m = neu('kind' + (a.own === 'mia' || a.own === 'beide' ? ' own' : ''), D.mia + '<span class="nm2">Mia</span>'); m.style.gridColumn = '1';
  var n = neu('kind' + (a.own === 'noah' || a.own === 'beide' ? ' own' : ''), D.noah + '<span class="nm2">Noah</span>'); n.style.gridColumn = '3';
  var d = neu('ding ' + (a.own === 'mia' ? 'l' : a.own === 'noah' ? 'r' : 'm'), '<div class="bild">' + art(a.x.id, a.zwei) + '</div>');
  b.appendChild(m); b.appendChild(d); b.appendChild(n);
  var t = a.spr === 'eule' ? (a.mit ? 'Die Eule spricht mit Mia und Noah.' : 'Die Eule erzählt über ' + NAME[a.own] + '.')
    : a.spr === 'beide' ? 'Mia und Noah sprechen über sich.'
    : NAME[a.spr] + ' spricht' + (a.mit ? ' mit ' + NAME[a.mit] : ' über sich') + '.';
  b.appendChild(neu('wer', h(t)));
  return b;
}
// Sprechblase so breit wie der Text, Spitze genau über dem Kind (bei «beide» zwei Spitzen)
function richte(b) {
  var s = b.querySelector('.sprech'); if (!s) return;
  var bl = s.querySelector('.blase'), sr = s.getBoundingClientRect(), ks = b.querySelectorAll('.kind'); if (!sr.width) return;
  function cx(el) { var q = el.getBoundingClientRect(); return q.left + q.width / 2 - sr.left; }
  var wer = s.dataset.wer, z = wer === 'mia' ? [cx(ks[0])] : wer === 'noah' ? [cx(ks[1])] : [cx(ks[0]), cx(ks[1])];
  bl.style.minWidth = z.length > 1 ? (z[1] - z[0] + 56) + 'px' : '';
  var bw = bl.offsetWidth, mitte = (z[0] + z[z.length - 1]) / 2, left = Math.max(0, Math.min(sr.width - bw, mitte - bw / 2));
  bl.style.marginLeft = left + 'px';
  bl.style.setProperty('--t1', Math.max(18, Math.min(bw - 18, z[0] - left)) + 'px');
  if (z.length > 1) bl.style.setProperty('--t2', Math.max(18, Math.min(bw - 18, z[1] - left)) + 'px');
  bl.classList.toggle('zwei', z.length > 1);
}
window.addEventListener('resize', function () { Array.prototype.forEach.call(document.querySelectorAll('.buehne'), richte); });
function buehneRein(w, a, text) { var b = buehne(a, text); w.appendChild(b); richte(b); requestAnimationFrame(function () { richte(b); }); return b; }
function tippPr(a) {
  return { my: '«mein» = my', your: '«dein» = your', your2: '«euer» = your (auch für mehrere Personen)', his: 'Es gehört Noah (einem Jungen) → his',
    her: 'Es gehört Mia (einem Mädchen) → her', our: '«unser» = our', their: 'Es gehört Mia und Noah → their' }[a.key];
}
function stufeBegleiter(api) {
  var w = neu('ks zs'); api.stage.appendChild(w); var liste = reihe(G.n), k = 0;
  function frage() {
    var a = aufgabe(liste[k], false), lock = false; w.innerHTML = ''; fb('');
    buehneRein(w, a, '<b>' + h(a.deP) + '</b>');
    api.msg('<span class="em">🧺</span> Wem gehört es? Wie sagt man das auf Englisch?');
    var opts = [a.p, PAAR[a.p]], rest = shuffle(['my', 'your', 'his', 'her', 'our', 'their'].filter(function (q) { return opts.indexOf(q) < 0; }));
    opts = shuffle(opts.concat(rest.slice(0, 2)));
    var wahl = neu('wahl'); w.appendChild(wahl);
    opts.forEach(function (q) {
      var bt = document.createElement('button'), t = q + ' ' + a.word; bt.textContent = t;
      bt.onclick = function () {
        if (lock) return; lock = true; var ok = q === a.p;
        bt.classList.add(ok ? 'ok' : 'no');
        if (!ok) Array.prototype.forEach.call(wahl.children, function (c) { if (c.textContent === a.enP) c.classList.add('hint'); });
        say(a.enP);
        fb(ok ? '<span class="em">✨</span> Richtig: <b>' + h(a.enP) + '</b>' : '<span class="em">💡</span> ' + h(tippPr(a)) + ': <b>' + h(a.enP) + '</b>');
        k++; if (!api.answer(ok)) return;
        api.later(frage, ok ? 1500 : 3000);
      };
      wahl.appendChild(bt);
    });
  }
  frage();
}
function stufeSaetze(api) {
  var w = neu('ks zs'); api.stage.appendChild(w); var liste = reihe(G.n), k = 0;
  function frage() {
    var a = aufgabe(liste[k], true), vers = 0, lock = false; w.innerHTML = ''; fb('');
    buehneRein(w, a, '<b>' + h(a.deS) + '</b>');
    var ziel = a.enS.split(' ');
    var dazu = [a.enPl ? 'This' : 'These', a.enPl ? 'is' : 'are', PAAR[a.p]];
    if (a.x.sg) dazu.push(a.enPl ? a.x.sg : a.x.pl);
    var satz = neu('satz'), kae = neu('kaertli'); w.appendChild(satz); w.appendChild(kae);
    var go = document.createElement('button'); go.className = 'go'; go.textContent = 'Prüfen'; w.appendChild(go);
    api.msg('Bau den Satz auf Englisch! Tippe die Wörter der Reihe nach an.');
    var gewaehlt = [];
    function zeichnen() {
      satz.innerHTML = '';
      gewaehlt.forEach(function (btn, i) {
        var s = document.createElement('button'); s.textContent = btn.textContent;
        s.onclick = function () { if (lock) return; gewaehlt.splice(i, 1); btn.classList.remove('weg'); zeichnen(); };
        satz.appendChild(s);
      });
      if (gewaehlt.length) satz.appendChild(neu('pkt', '.'));
      go.disabled = gewaehlt.length < ziel.length; go.style.opacity = go.disabled ? .5 : 1;
    }
    shuffle(ziel.concat(dazu)).forEach(function (t) {
      var b = document.createElement('button'); b.textContent = t;
      b.onclick = function () { if (lock || b.classList.contains('weg')) return; b.classList.add('weg'); gewaehlt.push(b); zeichnen(); };
      kae.appendChild(b);
    });
    zeichnen();
    go.onclick = function () {
      if (lock || go.disabled) return;
      var s = gewaehlt.map(function (b) { return b.textContent; }).join(' '), ok = s === a.enS;
      if (!ok && vers === 0) {
        vers = 1; satz.classList.add('no', 'shake'); bad();
        var g = s.split(' '), tipp = g[0] !== ziel[0] || g[1] !== ziel[1] ? (a.enPl ? 'Mehrere Dinge (oder trousers, socks …) → These are' : 'Ein Ding → This is') : g[2] !== ziel[2] ? tippPr(a) : 'Schau das Bild genau an: eins oder zwei?';
        if (!a.x.sg && (g[0] !== ziel[0] || g[1] !== ziel[1])) tipp = '«' + a.x.pl + '» ist auf Englisch immer Mehrzahl → These are';
        fb('<span class="em">💡</span> Noch nicht ganz. ' + h(tipp));
        api.later(function () { satz.classList.remove('no', 'shake'); gewaehlt.forEach(function (b) { b.classList.remove('weg'); }); gewaehlt = []; zeichnen(); }, 1500);
        return;
      }
      lock = true; go.remove();
      if (!ok) { satz.innerHTML = ''; ziel.forEach(function (t) { var e = document.createElement('button'); e.textContent = t; satz.appendChild(e); }); satz.appendChild(neu('pkt', '.')); }
      satz.classList.add(ok ? 'ok' : 'no'); satz.appendChild(lautBtn(a.enS + '.'));
      say(a.enS + '.');
      fb(ok ? '<span class="em">🌟</span> Super! <b>' + h(a.enS) + '.</b>' : '<span class="em">📝</span> So heisst der Satz: <b>' + h(a.enS) + '.</b>');
      k++; if (!api.answer(ok)) return;
      api.later(frage, ok ? 2000 : 3400);
    };
  }
  frage();
}

G.play = function (lv, api) {
  try { speechSynthesis.cancel(); } catch (e) {}
  [stufeSchrank, stufeWahl, stufeSchreiben, stufeSprechen, stufeBegleiter, stufeSaetze][lv.t](api);
};
"""
