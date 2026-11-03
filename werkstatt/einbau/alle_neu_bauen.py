# Baut die eingebetteten Werkzeuge aus den Originalen neu und vergleicht sie mit den veröffentlichten Dateien.
# Aufruf (im Repo-Hauptordner):  python3 werkstatt/einbau/alle_neu_bauen.py            -> nur prüfen
#                                python3 werkstatt/einbau/alle_neu_bauen.py --schreiben -> Dateien im Hauptordner ersetzen
import os, subprocess, sys, filecmp, tempfile
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
W = os.path.join(ROOT, 'werkstatt')
JOBS = [  # (Einbau-Skript, Original, Ziel im Hauptordner)
    ('einbau/hausaufgaben/heft_patch.py',  'originale/hausaufgabentafel.html', 'hausaufgaben.html'),
    ('einbau/pinnwand/pin_patch.py',       'originale/klassen-pinnwand.html',  'pinnwand.html'),
    ('einbau/tagesfolie/patch.py',         'originale/tagesfolien.html',       'tagesfolie.html'),
    ('einbau/otterteich/otter2_patch.py',  'originale/otterteich.html',        'otterteich.html'),
    ('einbau/atelier/atelier_patch.py',    'originale/atelier/index.html',     'atelier.html'),
    ('einbau/vokabelkiste/vk_patch.py',    'originale/vokabelkiste.html',      'vokabelkiste/index.html'),
]
write = '--schreiben' in sys.argv
ok = True
with tempfile.TemporaryDirectory() as tmp:
    for script, src, dst in JOBS:
        out = os.path.join(tmp, dst.replace('/', '_'))
        r = subprocess.run([sys.executable, os.path.join(W, script), os.path.join(W, src), out], capture_output=True, text=True)
        if r.returncode:
            ok = False; print('FEHLER  ', dst, '\n', r.stderr.strip()[-800:]); continue
        same = filecmp.cmp(out, os.path.join(ROOT, dst), shallow=False) if os.path.exists(os.path.join(ROOT, dst)) else False
        print(('gleich  ' if same else 'anders  ') + dst)
        if write and not same:
            open(os.path.join(ROOT, dst), 'wb').write(open(out, 'rb').read()); print('         -> ersetzt')
sys.exit(0 if ok else 1)
