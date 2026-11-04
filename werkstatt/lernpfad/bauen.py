#!/usr/bin/env python3
"""Baut das Lernpfad-Werkzeug (Entwurf, noch nicht im Portal).

quelle.html  -> lernpfad.html (eigenständige Seite, Schrift und Eule eingebettet)
Mit --artifact PFAD zusätzlich eine Fassung ohne <html>-Gerüst (für claude.ai).
"""
import base64, pathlib, sys

hier = pathlib.Path(__file__).resolve().parent
haupt = hier.parent.parent
quelle = (hier / 'quelle.html').read_text(encoding='utf-8')
font = base64.b64encode((haupt / 'schriften/patrick-hand.woff2').read_bytes()).decode()
eule = base64.b64encode((haupt / 'bilder/eule.webp').read_bytes()).decode()
inhalt = quelle.replace('%%FONT%%', font).replace('%%EULE%%', eule)
assert '%%' not in inhalt

seite = ('<!doctype html>\n<html lang="de">\n<head>\n<meta charset="utf-8">\n'
         '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
         + inhalt + '\n</html>\n')
(hier / 'lernpfad.html').write_text(seite, encoding='utf-8')
print('geschrieben: lernpfad.html')
if '--artifact' in sys.argv:
    ziel = pathlib.Path(sys.argv[sys.argv.index('--artifact') + 1])
    ziel.write_text(inhalt, encoding='utf-8')
    print('geschrieben:', ziel)
