# Mein Wochenziel -> Klassenkiste (wochenziel.html). Aufruf: python3 wz_patch.py <Original> <Ziel>
# Version 2 (SQL Version 33): Das Portal stellt die Brücke window.knWochenziel bereit (wzBridge in app.js):
#   mode 'teacher' = Lehrperson: kommt direkt in die Übersicht (ohne PIN), Kinder = Kinderliste der Klassenkiste,
#                    «Kinderansicht» zeigt die Seite eines Kindes, «Zur Übersicht» führt zurück.
#   mode 'kid'     = Kind, in der Klassenkiste angemeldet: kommt direkt zu seinen Zielen (ohne Namen/Bildpasswort),
#                    gespeichert über kid_wz_set (nur eigene Ziele, nur Kinder-Felder).
# Ohne Portal (Datei allein geöffnet) läuft alles wie im Original.
import sys
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    assert c == n, ('Anzahl %d statt %d: ' % (c, n)) + a[:90]
    s = s.replace(a, b)

# 1) Brücke der Klassenkiste (ganz oben im Skript, damit alle Teile sie kennen)
rep("(() => {\n'use strict';", """(() => {
'use strict';
const KNW = (() => { try { return window.parent !== window && window.parent.knWochenziel; } catch (e) { return null; } })();
const KNT = !!(KNW && KNW.mode === 'teacher'), KNK = !!(KNW && KNW.mode === 'kid');
if (KNW) document.documentElement.classList.add('knw', KNK ? 'knw-kid' : 'knw-lp');""")

# 2) Speicher: im Portal die Brücke nehmen, sonst wie bisher claude.ai bzw. nur dieses Gerät
rep('''    if (window.claude && typeof window.claude.use === 'function')
      db = await Promise.race([window.claude.use('db'), new Promise(r => setTimeout(() => r(null), 10000))]);''',
    '''    if (KNW && KNW.claude) db = await KNW.claude.use('db');
    else if (window.claude && typeof window.claude.use === 'function')
      db = await Promise.race([window.claude.use('db'), new Promise(r => setTimeout(() => r(null), 10000))]);''')

# 3) Nach dem Laden: Lehrperson direkt in die Übersicht, Kind direkt zu seinen Zielen
rep("if (got.size === 3 && S.screen === 'loading') { clearTimeout(timer); S.screen = 'start'; } render(); };",
    "if (got.size === 3 && S.screen === 'loading') { clearTimeout(timer); S.screen = knStart(); } render(); };")
rep("const onErr = () => { if (S.screen === 'loading')",
    "const onErr = () => { if (KNW) { clearTimeout(timer); S.screen = 'knaus'; render(); return; } if (S.screen === 'loading')")
rep("/* ================= Abfragen ================= */", """function knStart() {
  if (KNT) { S.lpOk = true; return 'lp'; }
  if (KNK) { S.kidId = KNW.kidId; return 'kid'; }
  return 'start';
}
/* ================= Abfragen ================= */""")
rep("    case 'loading': h += `<p class=\"boot\">Mein Wochenziel wird geladen …</p>`; break;",
    """    case 'loading': h += `<p class="boot">Mein Wochenziel wird geladen …</p>`; break;
    case 'knaus': h += `<div class="kid"><div class="kid-in"><div class="kid-card narrow"><h2>Mein Wochenziel ist gerade zu.</h2><p class="lead">Frag deine Lehrperson.</p></div></div></div>`; break;""")

# 4) Lehrperson in der Kinderansicht: Leiste oben mit dem Weg zurück zur Übersicht
rep("  $app.innerHTML = h;", """  if (KNT && (S.screen === 'kidpick' || S.screen === 'kid'))
    h = `<div class="knlpbar"><span>👁 Kinderansicht${S.screen === 'kid' && kidById(S.kidId) ? ' · so sieht es ' + esc(kidById(S.kidId).name) : ' · wähle ein Kind'}</span><button class="btn sm" data-a="knLp">Zur Übersicht</button></div>` + h;
  $app.innerHTML = h;""")

# 5) Name der Klasse kommt aus der Klassenkiste
rep("  const k = D().set.klasse;\n  return `<div class=\"marke\">", "  const k = KNW && KNW.className ? KNW.className : D().set.klasse;\n  return `<div class=\"marke\">")
rep('<div class="topbar">${D().set.klasse ? `<span class="cls">${esc(D().set.klasse)}</span>` : \'\'}<button class="btn sm" data-a="goKid">Kinderansicht</button><button class="btn sm" data-a="lpLogout">Abmelden</button></div>',
    '<div class="topbar">${KNW && KNW.className ? `<span class="cls">${esc(KNW.className)}</span>` : D().set.klasse ? `<span class="cls">${esc(D().set.klasse)}</span>` : \'\'}<button class="btn sm" data-a="goKid">👁 Kinderansicht</button><button class="btn sm knw-weg" data-a="lpLogout">Abmelden</button></div>')
rep("    <div class=\"kid-top\"><button class=\"kid-btn\" data-a=\"home\">‹ Zurück</button>${D().set.klasse ? `<span class=\"who\">${esc(D().set.klasse)}</span>` : ''}</div>\n    <h1>Wer bist du?</h1>",
    "    <div class=\"kid-top\"><button class=\"kid-btn\" data-a=\"home\">‹ Zurück</button>${KNW && KNW.className ? `<span class=\"who\">${esc(KNW.className)}</span>` : D().set.klasse ? `<span class=\"who\">${esc(D().set.klasse)}</span>` : ''}</div>\n    <h1>${KNT ? 'Wessen Seite möchten Sie ansehen?' : 'Wer bist du?'}</h1>")

# 6) Kinderliste, PIN, Bildpasswort und Klassenname verwaltet die Klassenkiste: hier ausblenden
rep("const tabs = [['klasse', 'Klasse'], ['kinder', 'Kinder'], ['einst', 'Beurteilung & Einstellungen']];",
    "const tabs = [['klasse', 'Klasse'], ['kinder', 'Kinder'], ['einst', 'Beurteilung & Einstellungen']].filter(t => !(KNW && t[0] === 'kinder'));")
rep('''<p>Tragen Sie zuerst die Vornamen Ihrer Klasse ein. Danach können die Kinder ihr Wochenziel setzen.</p>
    <button class="btn primary" data-a="tab" data-t="kinder">Kinder eintragen</button></div>`;''',
    '''<p>${KNW ? 'Tragen Sie die Kinder in der Klassenkiste unter «Kinder» ein. Sie erscheinen dann automatisch hier.' : 'Tragen Sie zuerst die Vornamen Ihrer Klasse ein. Danach können die Kinder ihr Wochenziel setzen.'}</p>
    ${KNW ? '' : '<button class="btn primary" data-a="tab" data-t="kinder">Kinder eintragen</button>'}</div>`;''')
rep('<button class="switch" role="switch" data-a="tgl" data-k="bildpw"', '<button class="switch knw-weg" role="switch" data-a="tgl" data-k="bildpw"')
rep('<div class="card"><h3>Klasse</h3>', '<div class="card knw-weg"><h3>Klasse</h3>')
rep("? `<p class=\"storenote db\"><i></i>Gespeichert für die ganze Klasse</p>`",
    "? `<p class=\"storenote db\"><i></i>${KNW ? 'In der Klassenkiste gespeichert' : 'Gespeichert für die ganze Klasse'}</p>`")

# 7) Aktionen: Wege in der Klassenkiste
rep("    case 'home': kidReset(); S.lpOk = false; go('start'); break;",
    """    case 'home': if (KNK) { try { KNW.back(); } catch (e) {} break; }
      if (KNT) { kidReset(); go('lp'); break; }
      kidReset(); S.lpOk = false; go('start'); break;
    case 'knLp': kidReset(); go('lp'); break;""")
rep("    case 'goKid': kidReset(); S.openKid = null; if (!S.demo) S.lpOk = false; go('kidpick'); break;",
    "    case 'goKid': kidReset(); S.openKid = null; if (!S.demo && !KNT) S.lpOk = false; go('kidpick'); break;")
rep("      go(D().set.bildpw && k && (k.pw || []).length === 3 ? 'kidpw' : 'kid'); break;",
    "      go(!KNW && D().set.bildpw && k && (k.pw || []).length === 3 ? 'kidpw' : 'kid'); break;")
rep("    case 'kidDone': kidReset(); go('kidpick'); break;",
    "    case 'kidDone': if (KNK) { try { KNW.back(); } catch (e) {} break; } kidReset(); go('kidpick'); break;")
rep('<button class="kid-btn" data-a="kidDone">Fertig</button>',
    '<button class="kid-btn" data-a="kidDone">${KNT ? \'‹ Anderes Kind\' : \'Fertig\'}</button>')
rep("Super, alles erledigt! Du kannst jetzt auf «Fertig» tippen.", "Super, alles erledigt!${KNT ? '' : ' Du kannst jetzt auf «Fertig» tippen.'}")

# 8) Zurück-Knopf zur Klassenkiste (oben links, nur im Portal sichtbar)
i = s.find('</body>')
assert i > 0
s = s[:i] + '''<button class="knback" id="knBack" type="button" hidden aria-label="Zurück zur Klassenkiste"><span>←</span><img src="bilder/eule.webp" alt=""></button>
<script>(() => { let K = null; try { K = window.parent !== window && window.parent.knWochenziel; } catch (e) {}
  if (!K) return; const b = document.getElementById('knBack'); b.hidden = false; document.body.classList.add('inkn');
  b.addEventListener('click', () => { try { K.back(); } catch (e) {} }); })();</script>
''' + s[i:]

# 9) Startseite: die Regel für die Kinderansicht (.kid = ganze Bildschirmhöhe) traf auch den Knopf «Ich bin ein Kind»
j = s.index('<div id="app"'); j = s.rindex('</style>', 0, j)   # Ende des grossen Stilblocks
s = s[:j] + '.door.kid{min-height:0;padding:16px 18px}\n' + s[j:]

# 10) Schöner im Stil der Klassenkiste: Patrick Hand, Aquarell-Hintergrund, weisse Karten mit Goldrand und weichem
#     blauem Schatten, goldene Hauptknöpfe (wie «Los geht's» bei der Anmeldung der Kinder). Gilt auch ohne Portal.
STIL = r'''
/* ===== Klassenkiste-Stil (wz_patch.py Abschnitt 10) ===== */
:root{--hand:"Patrick Hand","Segoe Print","Comic Sans MS",cursive;--h:var(--hand);--gold-l:#f3e2b3;--paper:#fffdf7}
html,body{background:#eef6fc}
body{background:radial-gradient(1100px 520px at 8% -8%,#d9ecfb 0,rgba(217,236,251,0) 60%),radial-gradient(900px 480px at 100% 0,#fbf0d6 0,rgba(251,240,214,0) 55%),
  radial-gradient(800px 600px at 50% 110%,#e3f0e0 0,rgba(227,240,224,0) 60%),#f4f9fd;background-attachment:fixed}
.lp,.kid{background:transparent!important}
.knw-weg{display:none!important}
/* Kopf */
.top{background:rgba(255,255,255,.82);box-shadow:0 1px 0 rgba(214,173,69,.45),0 6px 18px rgba(63,120,168,.08)}
.marke-bild{background:#fff;box-shadow:0 0 0 3px var(--gold),0 6px 18px rgba(63,120,168,.25)}
.topbar .btn{font-size:19px}
.tab[aria-selected="true"]{border-color:var(--gold);background:#fffdf5;box-shadow:0 4px 14px rgba(214,173,69,.25)}
.h2{color:var(--ink)}
/* Lehrperson: Karten der Kinder */
.kc{border:1.5px solid #ecdcae;border-radius:24px;background:linear-gradient(180deg,#fff,#fffdf8)}
.kc:hover{border-color:var(--gold)}
.kc-top b{font-size:24px}
.kc-goal{background:var(--paper);border:1.5px dashed #e4c978;border-radius:16px;font-size:21px}
.kc-goal.none{background:#f6f9fc;border:1.5px dashed #cfdceb}
.sumbox{border-color:#ecdcae}
.sumbox b{font-family:var(--hand);font-weight:400;font-size:28px;color:var(--gold-d)}
.chip[aria-pressed="true"]{background:#fff6dc;border-color:var(--gold);box-shadow:0 3px 10px rgba(214,173,69,.25)}
.weeknav{border-color:#ecdcae}
.weeknav button{background:#fff3cf;color:#7a5a12}
.card{border-color:#ecdcae}
.mode[aria-pressed="true"]{border-color:var(--gold);background:#fffaea}
.sheet-head h2{font-family:var(--hand)}
.vg{border-color:#ecdcae}
.lprate button[aria-pressed="true"]{border-color:var(--gold);background:#fff6dc;box-shadow:0 0 0 3px rgba(214,173,69,.25)}
/* Kinder: weich statt schwarzer Ränder */
.kid{font-family:"Andika","Trebuchet MS",system-ui,sans-serif}
.kid h1,.kid h2,.kid h3,.kid-top .who,.kid-btn,.kid-name b,.kid-go,.rate button span.t,.klbl,.goalbox .wk,.goalbox .gp b,.hitem .wk,.feedback small,.strip figcaption,.hitem .rs figcaption{font-family:var(--hand)!important;font-weight:400!important;letter-spacing:0;text-transform:none}
.kid h1{font-size:clamp(36px,6vw,52px)}
.kid h1::after,.kid-card h2::after{content:" ✦";color:var(--gold);font-size:.5em;vertical-align:super}
.kid .party+h2::after,.kid-card.narrow h2::after{content:""}
.kid-top .who{font-size:28px}
.kid-top .who .ini{box-shadow:0 0 0 3px var(--gold)}
.kid-btn{border:1.5px solid #d9c38a;border-radius:999px;background:#fff;font-size:20px;box-shadow:0 4px 12px rgba(63,120,168,.14);padding:0 20px}
.kid-btn:hover{background:#fffaea}
.kid-card{border:2px solid #ecdcae;border-radius:30px;box-shadow:var(--schatten);background:linear-gradient(180deg,#fff 0,#fff 75%,#fffdf6 100%)}
.kid-card h2{font-size:clamp(28px,4.6vw,38px)}
.kid-name{border:2px solid #ecdcae;box-shadow:0 6px 16px rgba(63,120,168,.14);border-radius:22px}
.kid-name:hover{border-color:var(--gold);transform:translateY(-2px)}
.kid-name:active{transform:translateY(1px);box-shadow:0 2px 6px rgba(63,120,168,.14)}
.kid-name b{font-size:25px}
.kid-go{border-radius:999px;color:#3d2c05;background:linear-gradient(180deg,#ffd873,#f2be3c);box-shadow:0 5px 0 #c99a2e,0 14px 24px rgba(214,173,69,.32);font-size:27px;transition:transform .12s,box-shadow .12s}
.kid-go:hover{background:linear-gradient(180deg,#ffdd85,#f4c44a);transform:translateY(-2px)}
.kid-go:active{transform:translateY(4px);box-shadow:0 1px 0 #c99a2e,0 6px 12px rgba(214,173,69,.3)}
.kid-go[disabled]{background:#e9edf0;color:#8a948e;box-shadow:none;transform:none}
.kid-go.alt{background:#fff;color:var(--ink);border:2px dashed var(--gold);box-shadow:none;font-size:22px;line-height:1.2;padding:12px 22px}
.kid-go.alt:hover{background:#fffaea}
.goalbox{background:var(--paper);border:2px dashed var(--gold);border-radius:24px;box-shadow:inset 0 0 0 6px #fff9e8}
.goalbox .wk{font-size:19px}
.goalbox .gt{font-size:clamp(30px,5vw,44px)}
.goalbox .gp b{font-size:18px}
.rate button{border:2px solid #e2e8ee;box-shadow:0 5px 14px rgba(63,120,168,.13);border-radius:22px}
.rate button:hover{border-color:#e4c978}
.rate button span.t{font-size:20px}
.rate button[aria-pressed="true"]{background:#fff6dc;border-color:var(--gold);outline:0;transform:translateY(2px);box-shadow:0 0 0 4px rgba(214,173,69,.35)}
.ktext{border:2px solid #dfe8f0;border-radius:20px;background:#fff;font-size:27px;box-shadow:inset 0 2px 6px rgba(63,120,168,.06)}
.ktext:focus{outline:0;border-color:var(--gold);box-shadow:0 0 0 4px rgba(214,173,69,.25)}
.klbl{font-size:22px}
.idea{border:1.5px solid #e4c978;background:#fffdf5;font-size:20px}
.idea:hover{background:#fff3cf}
.feedback{background:#f1f7ec;border:2px solid #cfe2c2;border-radius:24px}
.feedback small{font-size:17px}
.hitem{border:1.5px solid #ecdcae;box-shadow:0 4px 12px rgba(63,120,168,.1);border-radius:22px}
.hitem .wk{font-size:17px}
.strip figure{background:#fff;border-radius:16px;padding:6px 2px 4px;box-shadow:0 3px 10px rgba(63,120,168,.1)}
.symbtn,.pwslots span{border-width:2px}
.symbtn{border-color:#e2e8ee;box-shadow:0 5px 14px rgba(63,120,168,.13)}
.pwslots span.on{border-color:var(--gold)}
.door{border:2px solid #ecdcae}
.door:hover{border-color:var(--gold)}
.login-hero{background:linear-gradient(160deg,#d9ecfb,#eaf5fd 60%,#fdf3dc)}
/* Klassenkiste: Zurück-Knopf wie überall (weisse Pille mit Pfeil und Eule) */
.knback{position:fixed;left:12px;top:10px;z-index:60;display:flex;align-items:center;gap:6px;height:48px;padding:0 8px 0 16px;border:0;border-radius:999px;background:#fff;
  box-shadow:0 6px 18px rgba(63,120,168,.22),0 0 0 1.5px #ecdcae;font:24px/1 var(--hand);color:var(--ink);cursor:pointer}
.knback img{width:36px;height:36px;border-radius:50%}
.knback:hover{transform:translateY(-1px)}
body.inkn .top-in{padding-left:max(110px,env(safe-area-inset-left,0px))}
body.inkn .kid{padding-top:72px}
.knlpbar{position:sticky;top:0;z-index:30;display:flex;align-items:center;justify-content:center;gap:14px;flex-wrap:wrap;padding:8px 16px 8px 110px;background:#fff6dc;
  border-bottom:1.5px dashed var(--gold);font:20px/1.2 var(--hand);color:#5b4a1e}
body.inkn .knlpbar+.kid{padding-top:22px}
'''
j = s.index('<div id="app"'); j = s.rindex('</style>', 0, j)
s = s[:j] + STIL + s[j:]
open(dst, 'w', encoding='utf-8').write(s)
