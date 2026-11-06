# Mathe-Spiele der Lehrerin (Dezimalzahlen, Einmaleins, Raster & Koordinaten) im Klassenkiste-Stil.
# Die Übungen bleiben unverändert: es kommt nur eine Stil-Schicht dazu (Schrift Patrick Hand, Aquarell-Hintergrund,
# Gold-Akzente, runde Logos wie in der Übersicht der Rechenoperationen). Spielstände bleiben gleich.
# Aufruf: python3 werkstatt/spiele/mathematik/stil.py [Ausgabe-Ordner]
#   -> mathematik-spielpaket.json (in der Verwaltung importieren, «gleichen Titel ersetzen»)
#   -> vorschau.html (alle Spiele zum Ausprobieren)
import json, os, re, sys, html as H
HIER = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HIER, '..', '..', '..'))
QUELLE = os.path.join(HIER, 'quellen', 'spielpaket-mathematik.json')
AUS = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HIER, 'aus')
os.makedirs(AUS, exist_ok=True)

# Schrift Patrick Hand (eingebettet, wie in den Rechenoperationen)
stil = open(os.path.join(ROOT, 'rechenoperationen', 'stil.css'), encoding='utf-8').read()
FONT = re.search(r'@font-face\{[^}]*\}', stil).group(0)

BASIS = FONT + r'''
:root{--kn-ink:#1f2421;--kn-soft:#5f6963;--kn-line:#e1edf7;--kn-line2:#c5d8e8;--kn-gold:#d6ad45;--kn-gold-d:#a87c1f;--kn-sky:#dcf0fd;--kn-sun:#fbf3dc;
  --kn-sch:0 10px 26px rgba(63,120,168,.18),0 2px 6px rgba(63,120,168,.10);--kn-sch-k:0 4px 12px rgba(63,120,168,.14)}
html body{background:radial-gradient(1200px 600px at 10% -10%,#e3f1fc 0%,transparent 60%),radial-gradient(900px 500px at 110% 110%,#fbf3dc 0%,transparent 60%),#f4f9fd!important;background-attachment:fixed!important;color:var(--kn-ink)}
html body,html body *{font-family:"Patrick Hand","Segoe Print","Comic Sans MS",cursive!important}
html body h1,html body h2,html body h3,html body button{font-weight:400!important;letter-spacing:.01em}
.kn-logo{display:inline-grid;place-items:center;flex:none;width:84px;height:84px;border-radius:50%;background:radial-gradient(circle at 35% 30%,#fff 0%,#eaf5fe 70%);border:3px solid var(--kn-gold);
  box-shadow:inset 0 0 0 5px #fff,var(--kn-sch);font-size:24px;line-height:1;white-space:nowrap;color:var(--kn-ink);font-weight:400;letter-spacing:0;vertical-align:middle}
.kn-kopf{display:flex!important;align-items:center;gap:18px;text-align:left}
.kn-small{font-size:15px!important}
.kn-stern::after{content:" ✦";color:var(--kn-gold);font-size:.5em;vertical-align:super}
'''
KNOPF = '{background:var(--kn-sky)!important;border:2px solid var(--kn-ink)!important;color:var(--kn-ink)!important;border-radius:16px!important;box-shadow:var(--kn-sch-k)!important;font-weight:400!important;font-size:1.25rem!important}'
WAHL = '{background:var(--kn-sun)!important;border-color:var(--kn-gold)!important;color:var(--kn-ink)!important;box-shadow:0 0 0 2px var(--kn-gold) inset!important}'
KARTE = '{background:linear-gradient(180deg,#fff 0%,#fff 70%,#f7fbfe 100%)!important;border:1.5px solid var(--kn-line)!important;border-radius:28px!important;box-shadow:var(--kn-sch)!important}'

# 1×1-Spiele (gemeinsame Vorlage): Übersicht wie bei den Rechenoperationen, Karten mit rundem Bild
EINMALEINS_CSS = r'''
.wrap{max-width:980px!important}
.kn-kopf h1{font-size:clamp(40px,6vw,54px)!important;line-height:1!important}
.kn-kopf .lead{margin:6px 0 0!important;color:var(--kn-soft)!important;font-size:19px!important}
main.wrap>.kn-kopf{margin-bottom:22px}
main.wrap{padding-top:70px!important}
.levels{grid-template-columns:repeat(auto-fill,minmax(260px,1fr))!important;gap:18px!important}
.level{flex-direction:row!important;align-items:center!important;gap:14px!important;padding:14px 16px!important;border-radius:24px!important;border:1.5px solid var(--kn-line)!important;border-top:1.5px solid var(--kn-line)!important;
  background:linear-gradient(180deg,#fff 0%,#fff 70%,#f7fbfe 100%)!important;box-shadow:var(--kn-sch)!important;transition:transform .15s,box-shadow .15s}
.level:hover{transform:translateY(-3px);box-shadow:0 16px 34px rgba(63,120,168,.26)!important}
.level .kn-ic{flex:none;width:76px;height:76px;border-radius:50%;border:3px solid var(--kn-gold);box-shadow:inset 0 0 0 4px #fff;display:grid;place-items:center;font-size:20px;line-height:1;background:radial-gradient(circle at 35% 30%,#fff 0%,#eaf5fe 70%);white-space:nowrap}
.level .kn-t{display:flex;flex-direction:column;gap:2px;min-width:0}
.lname{font-size:25px!important;font-weight:400!important;line-height:1.05}
.lex{color:var(--kn-soft)!important;font-size:16px}
.st{color:var(--kn-gold)!important}.st.off{color:#e6dcc2!important}
.stat{background:#fff!important;border:1.5px solid var(--kn-line)!important;border-radius:20px!important;box-shadow:var(--kn-sch-k)}
.btn.primary,.key.go''' + KNOPF + r'''
.btn{border-radius:16px!important;border:2px solid var(--kn-ink)!important;box-shadow:var(--kn-sch-k)!important;font-weight:400!important}
.key,.ans{border:2px solid var(--kn-line2)!important;box-shadow:var(--kn-sch-k)!important;border-radius:18px!important;font-weight:400!important}
.key.go{border-color:var(--kn-ink)!important}
.ans.right{background:#5f9a4a!important;border-color:#5f9a4a!important;color:#fff!important}.ans.wrong{background:#c8574e!important;border-color:#c8574e!important;color:#fff!important}
.q{border-bottom-color:var(--kn-gold)!important;color:var(--kn-gold-d)!important}
.pbar span{background:var(--kn-gold)!important}
.task{font-weight:400!important}
.back{font-size:20px!important}
'''
EINMALEINS_JS = r'''<script>(function(){
var app=document.getElementById('app'); if(!app) return;
function ic(l){var ex=(l.querySelector('.lex')||{}).textContent||'',nm=(l.querySelector('.lname')||{}).textContent||'';
  var m=/z\.\s*B\.\s*(.+)/.exec(ex); if(m) return m[1].trim(); if(/[:·]/.test(ex)) return ex.split('=')[0].trim();
  var n=(nm+' '+ex).match(/\d+/g)||[]; if(/gemischt/i.test(nm)) return '1–10'; if(n.length>3) return n[0]+'–'+n[n.length-1]; return n.join(' ')||'1×1';}
function auf(){
  var h=app.querySelector('main.wrap>h1'); if(h&&!h.closest('.kn-kopf')&&(app.querySelector('.levels')||app.querySelector('#go'))){
    var k=document.createElement('div'); k.className='kn-kopf'; var lg=document.createElement('span'); lg.className='kn-logo'; lg.textContent=window.KN_LOGO||'1×1';
    var t=document.createElement('div'); h.parentNode.insertBefore(k,h); var p=h.nextElementSibling; t.appendChild(h); h.classList.add('kn-stern'); if(p&&p.classList.contains('lead')) t.appendChild(p); k.appendChild(lg); k.appendChild(t);}
  Array.prototype.forEach.call(app.querySelectorAll('.level'),function(l){ if(l.querySelector('.kn-ic')) return;
    var c=document.createElement('span'); c.className='kn-ic'; c.textContent=ic(l); if(c.textContent.length>7) c.classList.add('kn-small'); var t=document.createElement('span'); t.className='kn-t';
    while(l.firstChild) t.appendChild(l.firstChild); l.appendChild(c); l.appendChild(t); });
}
new MutationObserver(auf).observe(app,{childList:true}); auf();
})();</script>'''

# Pro Spiel: Logo-Text, Kopf (Selektor für das runde Logo), Hauptknöpfe, gewählte Knöpfe, Karten, zusätzliches CSS, Ersetzungen
SPIELE = {
 'Stellenwert benennen': dict(logo='3.45', kopf='#startScreen', titel='#startScreen .start-title', knopf='.start-btn', karte='.result-box',
   css='#startScreen .kn-kopf{flex-direction:column;text-align:center;gap:10px}#startScreen .start-title{display:block!important}#startScreen .chalk-icon,#endScreen .chalk-icon{display:none}#startScreen{gap:10px}.start-title{font-size:clamp(40px,6vw,54px)!important}.start-desc{color:var(--kn-soft)!important;font-size:19px!important}'),
 'Dezimalzahlen-Memory': dict(logo='0.2', titel='header h1', knopf='.level-complete-panel button', karte='.level-complete-panel',
   css='header{background:transparent!important;color:var(--kn-ink)!important;box-shadow:none!important;border:0!important}header{padding-left:120px!important}header h1{color:var(--kn-ink)!important;font-size:clamp(28px,4vw,40px)!important}header .kn-logo{width:60px;height:60px;font-size:18px}.level-badge,.timer{background:#fff!important;color:var(--kn-ink)!important;border:1.5px solid var(--kn-gold)!important;border-radius:999px!important}'),
 'Stellenwert-Spiel': dict(logo='+0.01', titel='.card h1', knopf='.card button', karte='.card', rep=[('<h1>🏁 ', '<h1>')]),
 'Punkt verschieben': dict(logo='× 10', titel='.modal-card h2', knopf='button.action.primary,.modal-card button', karte='.card,.modal-card', rep=[('🔢 ', ''), ('⏱️ ', '')],
   css='.topbar{padding-left:130px!important}.topbar{background:transparent!important;color:var(--kn-ink)!important}.topbar h1{color:var(--kn-ink)!important}'),
 'Zahlenstrahl': dict(logo='4.6', knopf='.check', wahl='.levels button[aria-pressed="true"]',
   css=':root{--btn:#dcf0fd!important;--chip-on:#fbf3dc!important}.levels button{border-radius:999px!important}.app{padding-top:56px!important}'),
 'Achterbahn Nachbarzahlen': dict(logo='24 | 25', wahl='.modes button[aria-pressed="true"]', css='.hud{padding-left:120px!important}.hud h1{color:var(--kn-ink)!important}'),
 '1×1-Duell': dict(logo='7 · 8', titel='.setup-card h1', knopf='#go,.go,.btn.primary,button.start', wahl='.chip.on,.chip[aria-pressed="true"]', karte='.setup-card'),
 'Punktgenau – Das Koordinaten-Spiel': dict(logo='(3|5)', titel='header h1', knopf='.btn:not(.quiet)', wahl='.choice[aria-pressed="true"],.pick[aria-pressed="true"]', karte='.sheet',
   css=':root,:root:not([data-theme="light"]),:root[data-theme="dark"]{--yellow:#dcf0fd!important;--yellow-ink:#1f2421!important}.choice{border-radius:18px!important;border:1.5px solid var(--kn-line2)!important;box-shadow:var(--kn-sch-k)!important}header h1{font-size:clamp(36px,5vw,50px)!important}header h1 small{color:var(--kn-soft)!important}.wrap{padding-top:70px!important}'),
 'Fläche und Umfang': dict(logo='4 × 3', titel='header h1', knopf='.btn.primary', wahl='.choice[aria-pressed="true"]', karte='.card',
   css=':root,:root:not([data-theme="light"]),:root[data-theme="dark"]{--yellow:#dcf0fd!important;--yellow-ink:#1f2421!important}.choice{border-radius:18px!important;border:1.5px solid var(--kn-line2)!important;box-shadow:var(--kn-sch-k)!important}header h1{font-size:clamp(36px,5vw,50px)!important}header h1 small{color:var(--kn-soft)!important}.wrap{padding-top:70px!important}'),
}
EINMALEINS_LOGO = {'1×1-Reihen': '3 · 7', '1×1-Blitz': '6 · 4', '1×1 gemischt': '8 · 7', '1×1-Detektiv': '□ · 6', 'Fehlende Zahl': '4 · □',
  '1×1-Achterbahn': '56 : 8', '1×1: alle 100 Aufgaben': '10 · 10', '1:1: alle 100 Aufgaben': '100 : 10'}

def kopf_js(sel, titel, logo):
    # rundes Logo links neben den Titel setzen (nur einmal)
    return '<script>(function(){function auf(){var t=document.querySelector(%s);if(!t||t.dataset.kn)return;t.dataset.kn=1;if(!t.querySelector("small"))t.classList.add("kn-stern");var lg=document.createElement("span");lg.className="kn-logo";lg.textContent=%s;var k=document.createElement("div");k.className="kn-kopf";t.parentNode.insertBefore(k,t);k.appendChild(lg);k.appendChild(t);}if(document.readyState!=="loading")auf();else document.addEventListener("DOMContentLoaded",auf);new MutationObserver(auf).observe(document.documentElement,{childList:true,subtree:true});})();</script>' % (json.dumps(titel), json.dumps(logo))

def umbauen(g):
    s = g['html']
    # alte Schrift-/Farbschicht und Google-Schriften entfernen
    s = re.sub(r'<style id="kn-fonts">.*?</style>', '', s, flags=re.S)
    s = re.sub(r'<style id="kn-look">.*?</style>', '', s, flags=re.S)
    s = re.sub(r'<link[^>]*fonts\.(googleapis|gstatic)\.com[^>]*>', '', s)
    t = g['title']; css = BASIS; js = ''
    if t in EINMALEINS_LOGO:
        css += EINMALEINS_CSS; js = '<script>window.KN_LOGO=%s</script>' % json.dumps(EINMALEINS_LOGO[t]) + EINMALEINS_JS
    else:
        c = SPIELE[t]
        for a, b in c.get('rep', []):
            assert a in s, (t, a); s = s.replace(a, b)
        if c.get('knopf'): css += c['knopf'] + KNOPF
        if c.get('wahl'): css += c['wahl'] + WAHL
        if c.get('karte'): css += c['karte'] + KARTE
        css += c.get('css', '')
        if c.get('titel'): js = kopf_js(None, c['titel'], c['logo'])
    lay = '<style id="kn-eule">' + css + '</style>'
    assert s.count('</head>') == 1, t
    s = s.replace('</head>', lay + '</head>')
    i = s.rfind('</body>'); s = s[:i] + js + s[i:] if i >= 0 else s + js
    return s

pak = json.load(open(QUELLE, encoding='utf-8'))
neu = dict(pak); neu['games'] = []
for g in pak['games']:
    n = dict(g); n['html'] = umbauen(g); neu['games'].append(n)
json.dump(neu, open(os.path.join(AUS, 'mathematik-spielpaket.json'), 'w', encoding='utf-8'), ensure_ascii=False)

# Vorschau-Seite: alle Spiele nach Thema, mit Spielfenster
themen = []
for g in neu['games']:
    if g['thema'] not in themen: themen.append(g['thema'])
logo = lambda t: EINMALEINS_LOGO.get(t) or SPIELE[t]['logo']
karten = ''.join('<section><h2>' + H.escape(th) + '</h2><div class="liste">' + ''.join(
    '<button class="sp" data-i="%d"><span class="ic">%s</span><span class="t"><b>%s</b><span>%s</span></span></button>' % (i, H.escape(logo(g['title'])), H.escape(g['title']), H.escape(g['description']))
    for i, g in enumerate(neu['games']) if g['thema'] == th) + '</div></section>' for th in themen)
daten = json.dumps([g['html'] for g in neu['games']], ensure_ascii=False).replace('</', '<\\/')
seite = '''<title>Mathe-Spiele Klassenkiste</title><meta name="claude:viewport-fit-sides" content="cover"><style>''' + FONT + '''
:root{--ink:#1f2421;--soft:#5f6963;--line:#e1edf7;--gold:#d6ad45;--sch:0 10px 26px rgba(63,120,168,.18),0 2px 6px rgba(63,120,168,.10)}
/* Bewusst nur hell: die Spiele selbst sind hell */
:root{color-scheme:light}
*{box-sizing:border-box}
body{font-family:"Patrick Hand","Segoe Print",cursive;color:var(--ink);background:radial-gradient(1200px 600px at 10% -10%,#e3f1fc 0%,transparent 60%),radial-gradient(900px 500px at 110% 110%,#fbf3dc 0%,transparent 60%),#f4f9fd;min-height:100vh}
.wrap{max-width:1040px;margin:0 auto;padding-block:24px 48px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
h1{font-weight:400;font-size:clamp(36px,6vw,52px);margin:0}h1::after{content:" ✦";color:var(--gold);font-size:.5em;vertical-align:super}
.lead{color:var(--soft);font-size:19px;margin:6px 0 18px}
h2{font-weight:400;font-size:30px;margin:26px 0 12px}
.liste{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:16px}
.sp{display:flex;gap:14px;align-items:center;text-align:left;font:inherit;color:inherit;cursor:pointer;background:linear-gradient(180deg,#fff 0%,#fff 70%,#f7fbfe 100%);border:1.5px solid var(--line);border-radius:24px;padding:14px 16px;box-shadow:var(--sch);min-width:0}
.sp:hover{transform:translateY(-3px)}
.ic{flex:none;width:76px;height:76px;border-radius:50%;border:3px solid var(--gold);box-shadow:inset 0 0 0 4px #fff;display:grid;place-items:center;font-size:20px;white-space:nowrap;background:radial-gradient(circle at 35% 30%,#fff 0%,#eaf5fe 70%)}
.t{display:flex;flex-direction:column;gap:2px;min-width:0}.t b{font-weight:400;font-size:24px;line-height:1.05}.t span{color:var(--soft);font-size:16px;line-height:1.2}
.fenster{position:fixed;inset:0;background:#f4f9fd;display:none;z-index:9}.fenster.offen{display:block}
.fenster iframe{position:absolute;inset:0;width:100%;height:100%;border:0}
.zu{position:absolute;top:calc(12px + env(safe-area-inset-top,0px));left:calc(12px + env(safe-area-inset-left,0px));z-index:2;font:inherit;font-size:22px;background:#fff;border:0;border-radius:999px;padding:6px 18px;cursor:pointer;box-shadow:0 4px 14px rgba(63,120,168,.25)}
.sp:focus-visible,.zu:focus-visible{outline:3px solid var(--gold);outline-offset:3px}
@media (prefers-reduced-motion:reduce){.sp:hover{transform:none}}
</style><div class="wrap"><h1>Mathe-Spiele im Klassenkiste-Stil</h1>
<p class="lead">Vorschau zum gemeinsamen Überarbeiten. Tippe auf ein Spiel, um es auszuprobieren. Hier wird nichts gespeichert.</p>''' + karten + '''</div>
<div class="fenster" id="f"><button class="zu" id="zu" title="Zurück zur Übersicht">← Zurück</button><iframe id="fr" title="Spiel" sandbox="allow-scripts allow-modals"></iframe></div>
<script>var SP=''' + daten + ''';
document.querySelectorAll('.sp').forEach(function(b){b.onclick=function(){document.getElementById('fr').srcdoc=SP[+b.dataset.i];document.getElementById('f').classList.add('offen');};});
document.getElementById('zu').onclick=function(){document.getElementById('f').classList.remove('offen');document.getElementById('fr').srcdoc='';};
</script>'''
open(os.path.join(AUS, 'vorschau.html'), 'w', encoding='utf-8').write(seite)
print('ok', len(neu['games']), 'Spiele ->', AUS)
