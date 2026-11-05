# Baut die Englisch-Spiele der Klassenkiste. Zurzeit: «Owl Town» (3D-Stadt: Orte, Berufe, Wegbeschreibungen).
# Aufruf im Repo-Hauptordner:  python3 werkstatt/spiele/englisch/bauen.py
#
# Ergebnis:
#   englisch/owl-town.html               das Spiel (liegt auf GitHub Pages)
#   englisch/englisch-spielpaket.json    Paket zum Importieren (Verwaltung → «Spielpaket importieren», nur ein kurzer Verweis)
#
# Wie die Knobelspiele: In der Tabelle «games» steht nur ein Verweis (<meta name="knobelnest-url" content="englisch/…">).
# Verbesserungen kommen also über GitHub (dann EN_VER in app.js erhöhen), ohne neues Hochladen.
# Rahmen (Stufen-Menü, Sterne, Ton, Meldungen an das Portal) und Stil kommen aus werkstatt/spiele/gedaechtnis/bauen.py.
# Das eigentliche Spiel steht in owl-town.js und owl-town.css (gleicher Ordner).
import base64, importlib.util, json, os, sys
sys.dont_write_bytecode = True

HIER = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HIER, '..', '..', '..'))
ZIEL = os.path.join(REPO, 'englisch')

_spec = importlib.util.spec_from_file_location('gd_bauen', os.path.join(REPO, 'werkstatt', 'spiele', 'gedaechtnis', 'bauen.py'))
GD = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(GD)


def rep(s, alt, neu, n=1):
    c = s.count(alt)
    if c != n: raise SystemExit(f'Anzahl {c} statt {n}: {alt[:70]}')
    return s.replace(alt, neu)


# Spielstand unter eigenem Namen («en»), sechste Stufenfarbe, Knopf «Free walk» im Menü
FRAME = GD.FRAME
FRAME = rep(FRAME, "data: { gd: s }", "data: { en: s }")
FRAME = rep(FRAME, "localStorage.setItem('gd', s)", "localStorage.setItem('en', s)")
FRAME = rep(FRAME, "x.store && x.store.gd", "x.store && x.store.en")
FRAME = rep(FRAME, "localStorage.getItem('gd')", "localStorage.getItem('en')")
FRAME = rep(FRAME, "var LV_COL = ['#e9f1e3', '#dcf0fd', '#fbf3dc', '#fcefed', '#efe7f7'];", "var LV_COL = ['#e9f1e3', '#dcf0fd', '#fbf3dc', '#fcefed', '#efe7f7', '#e3f4f1'];")
FRAME = rep(FRAME, "function stopAll() { TM.forEach(clearTimeout); TM = []; }", "function stopAll() { TM.forEach(clearTimeout); TM = []; if (typeof stopSay === 'function') stopSay(); }")  # Vorlesen stoppen bei Stufen, Ende, Zurück
FRAME = rep(FRAME, "app.innerHTML = o + '</div>';", "app.innerHTML = o + '</div>'; if (G.extra) G.extra();")

def logo(name):
    # Logo des Spiels (rund, durchsichtige Ecken, eigener Goldrand) direkt eingebettet, damit es auch als Artefakt läuft
    with open(os.path.join(HIER, 'logos', name + '.webp'), 'rb') as f:
        return '<img class="logo" alt="" src="data:image/webp;base64,' + base64.b64encode(f.read()).decode() + '">'


SPIELE = [dict(
    id='owl-town', titel='Owl Town', icon=logo('owl-town'), fach='Englisch', thema='Town, jobs & directions', stufe='4.–6. Klasse', sort=1, n=5,
    sterne={'modus': 'sammeln', 'pro': 10, 'max': 10, 'proLevel': True, 'proTag': False},  # je 10 richtige Aufgaben 1 Stern, pro Stufe bis 10
    kurz='3D-Stadt: Gebäude und Berufe finden, Wegbeschreibungen laufen.',
    intro='Lauf mit der Eule durch die Stadt! Mit den Pfeiltasten ⬆ ⬅ ➡ ⬇ gehst und drehst du dich. Am Ziel drückst du 📍.',
    levels=[
        dict(name='Places', info='Finde die Orte: bakery, church, library …', typ='ort'),
        dict(name='Jobs', info='Wo arbeitet the vet, the baker, the pilot …?', typ='job'),
        dict(name='Short routes', info='turn left · turn right · walk straight on', typ='weg', ev=[1, 2], round='no', bridge='no', straight=.3),
        dict(name='Long routes', info='at the second crossing · cross the bridge · walk past', typ='weg', ev=[2, 3], round='no', bridge='any', lm=True, straight=.45),
        dict(name='Roundabout', info='take the first / second / third exit', typ='weg', ev=[2, 4], round='need', bridge='any', lm=True, straight=.35),
        dict(name='Listening', info='Nur hören – wie wenn dir jemand den Weg erklärt', typ='weg', ev=[2, 3], round='any', bridge='any', lm=True, listen=True, straight=.35),
    ])]


def lies(name):
    with open(os.path.join(HIER, name), encoding='utf-8') as f: return f.read()


def randfarbe(im):
    # Durchsichtige Pixel bekommen die Farbe der nächsten sichtbaren (sonst helle Säume am Rand der 3D-Figur)
    import numpy as np
    from PIL import Image, ImageFilter
    a = np.asarray(im).astype(np.float32); rgb, al = a[..., :3], a[..., 3:] / 255.0
    acc = rgb * al; w = al * 255; res = rgb.copy(); done = al[..., 0] > .6
    for r in (1, 2, 4, 8, 16):
        k = ImageFilter.GaussianBlur(r)
        def bl(x): return np.stack([np.asarray(Image.fromarray(np.clip(x[..., i], 0, 255).astype(np.uint8)).filter(k)).astype(np.float32) for i in range(x.shape[-1])], -1)
        A2 = bl(acc); W2 = bl(w); m = (~done) & (W2[..., 0] > 2)
        res[m] = A2[m] / (W2[m] / 255); done = done | m
    out = np.concatenate([np.clip(res, 0, 255), a[..., 3:]], -1).astype(np.uint8)
    return Image.fromarray(out, 'RGBA')


def leute():
    # Gezeichnete Figuren: leute/<Beruf>.webp (Beruf wie in JOBS, Leerzeichen als «-», z. B. police-officer.webp)
    from PIL import Image
    out, ordner = {}, os.path.join(HIER, 'leute')
    for n in sorted(os.listdir(ordner)) if os.path.isdir(ordner) else []:
        if not n.endswith('.webp'): continue
        im = randfarbe(Image.open(os.path.join(ordner, n)).convert('RGBA')); w, h = im.size
        import io; buf = io.BytesIO(); im.save(buf, 'WEBP', quality=90)
        out[n[:-5].replace('-', ' ')] = {'url': 'data:image/webp;base64,' + base64.b64encode(buf.getvalue()).decode(), 'w': w, 'h': h}
    return out


def modelle():
    # 3D-Figuren der Lehrerin: modelle/<Beruf>.glb (Name wie in JOBS, Leerzeichen als «-»), eingebettet als Base64
    out, ordner = {}, os.path.join(HIER, 'modelle')
    for n in sorted(os.listdir(ordner)) if os.path.isdir(ordner) else []:
        if n.endswith('.glb'):
            with open(os.path.join(ordner, n), 'rb') as f: out[n[:-4].replace('-', ' ')] = base64.b64encode(f.read()).decode()
    return out


def game_html(s):
    meta = json.dumps(s['sterne'], ensure_ascii=False).replace('"', '&quot;')
    g = {'title': s['titel'], 'icon': s['icon'], 'intro': s['intro'], 'n': s['n'], 'levels': s['levels']}
    return ('<!doctype html>\n<html lang="de-CH">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
            f'<meta name="knobelnest-sterne" content="{meta}">\n'
            '<script type="importmap">{"imports":{"three":"https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.min.js","three/addons/":"https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"}}</script>\n'
            f'<title>{s["titel"]}</title>\n<style>{GD.CSS.replace("__SCHRIFT__", GD.schrift())}{lies(s["id"] + ".css")}</style>\n</head>\n<body>\n<div id="app"></div>\n'
            f'<script>\nvar G = {json.dumps(g, ensure_ascii=False)};\nvar LEUTE = {json.dumps(leute(), ensure_ascii=False)};\nvar MODELLE = {json.dumps(modelle(), ensure_ascii=False)};\n{lies(s["id"] + ".js")}\n{FRAME}\n</script>\n</body>\n</html>\n')


def stub_html(s):
    meta = json.dumps(s['sterne'], ensure_ascii=False).replace('"', '&quot;')
    return ('<!doctype html><html lang="de-CH"><head><meta charset="utf-8">'
            f'<meta name="knobelnest-url" content="englisch/{s["id"]}.html">'
            f'<meta name="knobelnest-sterne" content="{meta}">'
            f'<title>{s["titel"]}</title></head><body><p>{s["titel"]}: Dieses Spiel liegt in der Klassenkiste im Ordner englisch/.</p></body></html>')


if __name__ == '__main__':
    os.makedirs(ZIEL, exist_ok=True)
    for s in SPIELE:
        with open(os.path.join(ZIEL, s['id'] + '.html'), 'w', encoding='utf-8') as f: f.write(game_html(s))
    paket = {'format': 'knobelnest-spielpaket', 'games': [
        {'title': s['titel'], 'description': s['kurz'], 'fach': s['fach'], 'thema': s['thema'], 'stufe': s['stufe'], 'sort': s['sort'], 'html': stub_html(s)} for s in SPIELE]}
    with open(os.path.join(ZIEL, 'englisch-spielpaket.json'), 'w', encoding='utf-8') as f: json.dump(paket, f, ensure_ascii=False, indent=1)
    print(len(SPIELE), 'Englisch-Spiel(e) gebaut (Ordner englisch/)')
