#!/usr/bin/env python3
"""Baut das Spiel «Wort des Tages» (spiele/wort-des-tages.html im Hauptordner) aus wort-des-tages.src.html und woerter.py.
Schrift (Patrick Hand) und Eule werden eingepackt, damit die Datei allein läuft.
Das Portal legt das Spiel beim Anmelden der Admin-Lehrperson selbst an bzw. aktualisiert es (wdtSync in app.js).
Bei jeder Änderung: wdt-version in wort-des-tages.src.html UND WDT_VER in app.js um 1 erhöhen."""
import base64, json, os, sys
HIER = os.path.dirname(os.path.abspath(__file__))
HAUPT = os.path.normpath(os.path.join(HIER, '..', '..'))
sys.path.insert(0, HIER)
import woerter

def b64(p):
    with open(os.path.join(HAUPT, p), 'rb') as f:
        return base64.b64encode(f.read()).decode()

L = woerter.liste(woerter.LOESUNGEN)
E = [w for w in woerter.liste(woerter.EXTRA) if w not in L]
for w in L + E:
    assert len(w) == 5 and w.isalpha() and w.isupper() and 'ß' not in w, w
src = open(os.path.join(HIER, 'wort-des-tages.src.html'), encoding='utf-8').read()
out = (src.replace('__FONT__', b64('schriften/patrick-hand.woff2'))
          .replace('__EULE__', b64('bilder/eule.webp'))
          .replace('__WOERTER__', json.dumps(L, ensure_ascii=False))
          .replace('__EXTRA__', json.dumps(E, ensure_ascii=False)))
os.makedirs(os.path.join(HAUPT, 'spiele'), exist_ok=True)
open(os.path.join(HAUPT, 'spiele', 'wort-des-tages.html'), 'w', encoding='utf-8').write(out)
print('spiele/wort-des-tages.html gebaut:', len(L), 'Lösungswörter,', len(E), 'weitere Wörter,', len(out) // 1024, 'KB')
