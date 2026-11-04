# Schneidet die Kleider aus dem Schrankbild (kleider_bilder/schrank-original.webp) aus.
# Aufruf: python3 werkstatt/spiele/knobelspiele/kleider_ausschneiden.py   (braucht Pillow)
# Ergebnis in kleider_bilder/: schrank.webp (ganzer Schrank, aufgeräumter Rand) und <id>.webp (Kleider aus dem Schrank, liegen im Spiel auf dem Schrank).
# Dazu karte-<id>.webp aus dem Einzelbild der Lehrerin (einzeln-original.webp): die Bilder auf den Karten (Stufe 2–6).
# Die Kästen (BOX) stehen auch in kleider.py, damit die Kleider im Spiel genau auf dem Schrank liegen.
import os, sys
from collections import deque
from PIL import Image
sys.dont_write_bytecode = True
HIER = os.path.dirname(os.path.abspath(__file__)); ORD = os.path.join(HIER, 'kleider_bilder')
sys.path.insert(0, HIER)
from kleider import BOX

def schrank():
    im = Image.open(os.path.join(ORD, 'schrank-original.webp')).convert('RGBA')
    px = im.load(); w, h = im.size
    for y in range(h):          # gelbe Krümel am Rand weg: halb durchsichtige Punkte ganz durchsichtig
        for x in range(w):
            r, g, b, a = px[x, y]
            if a < 170: px[x, y] = (r, g, b, 0)
    return im

# Nachbarn, die direkt anstossen: In diesem Streifen (Bild-Koordinaten) fällt weg, was eher die Farbe des Nachbarn hat
FREMD = {'jumper': [('tshirt', (372, 452, 404, 624))], 'tshirt': [('jumper', (380, 452, 412, 624)), ('shirt', (474, 452, 504, 624))],
         'shirt': [('tshirt', (480, 452, 510, 624)), ('jacket', (594, 452, 624, 624))], 'jacket': [('shirt', (598, 452, 630, 624))],
         'dress': [('coat', (852, 452, 880, 680))], 'coat': [('dress', (860, 452, 888, 680))]}

def kernfarbe(im, k):
    x0, y0, x1, y1 = BOX[k]; w, h = x1 - x0, y1 - y0
    # Stelle unten links von der Mitte (nicht der Stern oder das Muster in der Mitte)
    c = im.crop((x0 + w * 28 // 100, y0 + h * 72 // 100, x0 + w * 45 // 100, y0 + h * 86 // 100)).convert('RGB')
    ps = sorted(c.get_flattened_data(), key=sum); return ps[len(ps) // 2]

def frei(im, box, tol=46, k=None):
    c = im.crop(box); px = c.load(); w, h = c.size
    if k in FREMD:
        eigen = kernfarbe(im, k)
        for n, (a0, b0, a1, b1) in FREMD[k]:
            fr = kernfarbe(im, n)
            for x in range(max(a0, box[0]), min(a1, box[2])):
                for y in range(max(b0, box[1]), min(b1, box[3])):
                    p = px[x - box[0], y - box[1]]
                    if sum((p[i] - fr[i]) ** 2 for i in range(3)) < sum((p[i] - eigen[i]) ** 2 for i in range(3)): px[x - box[0], y - box[1]] = (0, 0, 0, 0)
    rand = [px[x, 0] for x in range(w)] + [px[x, h - 1] for x in range(w)] + [px[0, y] for y in range(h)] + [px[w - 1, y] for y in range(h)]
    def nah(p, q): return abs(p[0] - q[0]) + abs(p[1] - q[1]) + abs(p[2] - q[2]) < tol
    # Hintergrund = vom Rand aus erreichbare Punkte, die ihrem Nachbarn und einer häufigen Randfarbe ähnlich sind
    srt = sorted(rand, key=lambda p: (p[0] // 12, p[1] // 12, p[2] // 12))
    from collections import Counter
    cnt = Counter((p[0] // 12, p[1] // 12, p[2] // 12) for p in rand)
    haupt = [k for k, n in cnt.most_common(6) if n > len(rand) * 0.04]
    tuer = k in ('scarf', 'tie')  # an der orangen Tür: Orange/Gelbes am Rand (Tür, Schatten) gehört auch weg
    def orange(p): return tuer and p[0] > 140 and p[2] < 120 and p[1] > 0.56 * p[0]
    def bg(p): return p[3] < 40 or orange(p) or any(abs(p[0] // 12 - k[0]) + abs(p[1] // 12 - k[1]) + abs(p[2] // 12 - k[2]) <= 3 for k in haupt)
    weg = [[False] * h for _ in range(w)]; q = deque()
    for x in range(w):
        for y in (0, h - 1):
            if bg(px[x, y]): weg[x][y] = True; q.append((x, y))
    for y in range(h):
        for x in (0, w - 1):
            if bg(px[x, y]) and not weg[x][y]: weg[x][y] = True; q.append((x, y))
    while q:
        x, y = q.popleft()
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < w and 0 <= ny < h and not weg[nx][ny] and bg(px[nx, ny]) and (orange(px[nx, ny]) or nah(px[nx, ny], px[x, y])):
                weg[nx][ny] = True; q.append((nx, ny))
    # Dünne Verbindungen (Schatten, Brettkanten) trennen: Maske schrumpfen, grösstes Stück nehmen, wieder wachsen lassen
    from PIL import ImageFilter, ImageChops
    m = Image.new('L', (w, h), 0); mp = m.load()
    for x in range(w):
        for y in range(h):
            if not weg[x][y]: mp[x, y] = 255
    klein = m.filter(ImageFilter.MinFilter(7)); kp = klein.load()
    seen = [[False] * h for _ in range(w)]; teile = []
    for sx in range(w):
        for sy in range(h):
            if not kp[sx, sy] or seen[sx][sy]: continue
            t = []; q = deque([(sx, sy)]); seen[sx][sy] = True
            while q:
                x, y = q.popleft(); t.append((x, y))
                for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                    if 0 <= nx < w and 0 <= ny < h and kp[nx, ny] and not seen[nx][ny]: seen[nx][ny] = True; q.append((nx, ny))
            teile.append(t)
    teile.sort(key=len, reverse=True)
    g = Image.new('L', (w, h), 0); gp = g.load()
    for x, y in teile[0]: gp[x, y] = 255
    g = ImageChops.multiply(g.filter(ImageFilter.MaxFilter(11)), m); gp = g.load()
    behalten = set((x, y) for x in range(w) for y in range(h) if gp[x, y])
    out = Image.new('RGBA', (w, h), (0, 0, 0, 0)); op = out.load()
    for x, y in behalten: op[x, y] = px[x, y]
    # weicher Rand: Randpunkte halb durchsichtig
    for x, y in behalten:
        if any((nx, ny) not in behalten for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1))):
            r, g, b, a = op[x, y]; op[x, y] = (r, g, b, a // 2)
    bb = out.getbbox()
    return out, bb

# Kästen im Einzelbild (1402 × 1122, durchsichtiger Hintergrund)
EINZELN = {'hat': (40, 40, 370, 290), 'cap': (405, 40, 710, 290), 'scarf': (770, 20, 1000, 290), 'tie': (1120, 20, 1270, 290),
           'jumper': (40, 300, 360, 555), 'tshirt': (395, 300, 690, 555), 'shirt': (715, 300, 1025, 555), 'jacket': (1045, 300, 1355, 555),
           'dress': (60, 560, 335, 885), 'coat': (385, 560, 680, 885), 'skirt': (710, 590, 1025, 885), 'trousers': (1070, 570, 1320, 885),
           'shorts': (20, 900, 280, 1115), 'boots': (305, 895, 550, 1115), 'shoes': (555, 900, 825, 1115), 'socks': (835, 895, 1065, 1115),
           'gloves': (1090, 895, 1385, 1115)}

def karten():
    im = Image.open(os.path.join(ORD, 'einzeln-original.webp')).convert('RGBA')
    for k, box in EINZELN.items():
        c = im.crop(box); c = c.crop(c.split()[3].point(lambda a: 255 if a > 20 else 0).getbbox())
        c.thumbnail((280, 280), Image.LANCZOS)
        c.save(os.path.join(ORD, 'karte-' + k + '.webp'), quality=80, method=6)
        print('karte', k, c.size)

def kinder():
    # Mia (links) und Noah (rechts) aus kinder-original.webp, Logo rund aus logos/kleiderschrank-original.webp
    im = Image.open(os.path.join(ORD, 'kinder-original.webp')).convert('RGBA'); w, h = im.size
    for k, box in (('mia', (0, 0, w // 2, h)), ('noah', (w // 2, 0, w, h))):
        c = im.crop(box); c = c.crop(c.split()[3].point(lambda a: 255 if a > 20 else 0).getbbox()); c.thumbnail((400, 440), Image.LANCZOS)
        c.save(os.path.join(ORD, k + '.webp'), quality=82, method=6)
    from PIL import ImageDraw
    lg = Image.open(os.path.join(HIER, 'logos', 'kleiderschrank-original.webp')).convert('RGBA'); w, h = lg.size; px = lg.load()
    dunkel = lambda p: sum(p[:3]) < 700
    x0 = next(x for x in range(w) if dunkel(px[x, h // 2])); x1 = next(x for x in range(w - 1, 0, -1) if dunkel(px[x, h // 2]))
    y0 = next(y for y in range(h) if dunkel(px[w // 2, y])); y1 = next(y for y in range(h - 1, 0, -1) if dunkel(px[w // 2, y]))
    S = 1200; c = lg.crop((x0, y0, x1 + 1, y1 + 1)).resize((S, S), Image.LANCZOS)
    m = Image.new('L', (S * 2, S * 2), 0); ImageDraw.Draw(m).ellipse((0, 0, S * 2 - 1, S * 2 - 1), fill=255)
    c.putalpha(m.resize((S, S), Image.LANCZOS)); c.resize((320, 320), Image.LANCZOS).save(os.path.join(HIER, 'logos', 'kleiderschrank.webp'), quality=85, method=6)

if __name__ == '__main__':
    kinder()
    karten()
    im = schrank()
    im.save(os.path.join(ORD, 'schrank.webp'), quality=82, method=6)
    for k, box in BOX.items():
        out, bb = frei(im, box, k=k)
        out.save(os.path.join(ORD, k + '.webp'), quality=90, method=6)
        print(k, out.size, bb)
