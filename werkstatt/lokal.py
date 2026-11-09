# Schriften und Programmteile vom eigenen Server statt von Google, jsDelivr oder cdnjs (Datenschutz: keine Aufrufe an Dritte).
# lokal(html, p) biegt die Adressen in einer gebauten Seite um; p = Weg zum Hauptordner ('' oder '../').
# Aufruf: python3 werkstatt/lokal.py  -> bearbeitet alle betroffenen Seiten im Hauptordner (mehrmals ausführbar)
#         python3 werkstatt/lokal.py --pruefen -> meldet nur, ob noch fremde Adressen vorkommen
import os, re, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
FREMD = re.compile(r'https://(fonts\.googleapis\.com|fonts\.gstatic\.com|cdn\.jsdelivr\.net|cdnjs\.cloudflare\.com|unpkg\.com)')

def lokal(h, p=''):
    # Google-Schriften: Vorverbindungen weg, Stylesheet -> schriften/schriften.css (dieselben Schriften liegen lokal)
    h = re.sub(r'<link rel="preconnect" href="https://fonts\.(googleapis|gstatic)\.com"( crossorigin)?>\n?', '', h)
    h = re.sub(r'<link rel="stylesheet" href="https://fonts\.googleapis\.com/css2\?[^"]*">', '<link rel="stylesheet" href="' + p + 'schriften/schriften.css">', h)
    h = h.replace('https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.105.0/dist/umd/supabase.js', p + 'bibliothek/supabase/supabase.js')
    h = h.replace('https://cdn.jsdelivr.net/npm/three@0.160.0/', p + 'bibliothek/three/')
    h = h.replace('https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js', p + 'bibliothek/jspdf/jspdf.umd.min.js')
    return h

# Seiten, die nicht über einen Einbau gebaut werden (bzw. deren Bau-Skript hier nicht läuft)
SEITEN = ['index.html', 'zeitreise/index.html', 'zeitreise/altsteinzeit.html', 'zeitreise/jungsteinzeit.html', 'englisch/owl-town.html',
          'hausaufgaben.html', 'atelier.html']
# Ausnahme: vokabelkiste/index.html enthält Google-Schriften nur im Text für den Export nach claude.ai (wird im Portal nicht geladen)
AUSNAHMEN = {'vokabelkiste/index.html'}

def fremde():
    out = []
    for d, _, fs in os.walk(ROOT):
        rel = os.path.relpath(d, ROOT)
        if rel.split(os.sep)[0] in ('werkstatt', 'spieleregal', '.git', 'bibliothek', 'supabase'): continue
        for f in fs:
            if not f.endswith(('.html', '.js', '.css')): continue
            r = os.path.normpath(os.path.join(rel, f))
            if r in AUSNAHMEN: continue
            s = open(os.path.join(d, f), encoding='utf-8', errors='ignore').read()
            for m in FREMD.finditer(s): out.append(r + ': ' + s[m.start():m.start() + 80].split('"')[0])
    return out

if __name__ == '__main__':
    if '--pruefen' not in sys.argv:
        for s in SEITEN:
            f = os.path.join(ROOT, s); h = open(f, encoding='utf-8').read()
            n = lokal(h, '../' if '/' in s else '')
            if n != h: open(f, 'w', encoding='utf-8').write(n); print('umgestellt', s)
    rest = fremde()
    print('\n'.join(rest) if rest else 'keine fremden Adressen mehr')
    sys.exit(1 if rest else 0)
