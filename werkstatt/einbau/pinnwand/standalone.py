# Klassen-Pinnwand eigenständig (claude.ai-Artefakt mit window.claude.use('db')), ohne Klassenkiste-Anbindung.
# Aufruf: python3 werkstatt/einbau/pinnwand/standalone.py werkstatt/originale/klassen-pinnwand.html <Ziel.html>
# Grundlage ist dasselbe Original (Version 6) wie in der Klassenkiste, dazu:
#   - die gemeinsamen Korrekturen (pin_fixes.py) und der Klassenkiste-Stil (pin_stil.py),
#   - Schrift und Eule als data:-Adressen (ein Artefakt darf keine fremden Dateien laden),
#   - kein «Drucken» (ein Artefakt kann keinen Druckdialog öffnen),
#   - Hinweis: eigene Vorlagen gibt es in der Klassenkiste.
# Für das Artefakt: alles zwischen <body> und </body> veröffentlichen, mit capabilities db (Regeln siehe CLAUDE.md) und user.
import sys, os, base64
src, dst = sys.argv[1], sys.argv[2]
here = os.path.dirname(os.path.abspath(__file__))
root = os.path.abspath(os.path.join(here, '..', '..', '..'))
s = open(src, encoding='utf-8').read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    assert c == n, ('Anzahl %d statt %d: ' % (c, n)) + a[:90]
    s = s.replace(a, b)

exec(open(os.path.join(here, 'pin_fixes.py'), encoding='utf-8').read())

rep('<link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Patrick+Hand&family=Nunito:wght@400;600;700;800&family=Fredoka:wght@500;600;700&display=swap">\n', '')
EULE = 'data:image/webp;base64,' + base64.b64encode(open(os.path.join(root, 'bilder', 'eule.webp'), 'rb').read()).decode()
SCHRIFT = ('@font-face{font-family:"Patrick Hand";src:url(data:font/woff2;base64,'
           + base64.b64encode(open(os.path.join(root, 'schriften', 'patrick-hand.woff2'), 'rb').read()).decode()
           + ') format("woff2");font-weight:400;font-display:swap}\n')
exec(open(os.path.join(here, 'pin_stil.py'), encoding='utf-8').read())

# Kein Drucken im Artefakt
rep('      <div class="row"><button class="btn ghost small" type="button" data-act="print">🖨️ Drucken</button></div>\n', '')
# Hinweis auf die Klassenkiste: dort lassen sich Vorlagen bearbeiten, löschen und eigene erstellen
rep('esc(t.icon) + " Erstellen"}</button></div></section>`;', '''esc(t.icon) + " Erstellen"}</button></div>
    <div class="vl-hint"><span class="vl-stern" aria-hidden="true">✦</span><p><b>Eigene Vorlagen?</b> In der Klassenkiste können Sie Vorlagen bearbeiten, löschen und eigene erstellen, dazu viele weitere Werkzeuge für Ihre Klasse.</p><a class="btn vl-btn" href="https://klassenkiste.primarschuleulchen.com/" target="_blank" rel="noopener">✦ Hol dir jetzt den Zugang</a></div></section>`;''')

open(dst, 'w', encoding='utf-8').write(s)
print('ok', len(s))
