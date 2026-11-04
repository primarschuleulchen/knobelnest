# Kleiderschrank (Englisch: clothes): Kleider im Schrank entdecken, benennen, schreiben, sprechen,
# my/your/his/her/our/their und Sätze «This is my dress.» / «These are my ties.».
# Wird von bauen.py aufgerufen: kleider.alle(spiel)
#
# Alle Bilder sind hier als SVG gezeichnet (kein Bild von aussen). Jedes Kleidungsstück hat eine eigene
# Zeichenfläche (viewBox), der Schrank setzt sie an feste Plätze.

K = 'stroke="#2b2f2c" stroke-width="2.6" stroke-linejoin="round" stroke-linecap="round"'
L = 'fill="none" stroke="#2b2f2c" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"'
W = 'fill="none" stroke="#fff" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" opacity=".75"'


def sock(dx, dy, c):
    return (f'<g transform="translate({dx},{dy})"><path {K} fill="{c}" d="M14 6 L34 6 L34 52 Q34 68 22 74 L10 76 Q0 76 2 66 Q4 60 12 58 L14 54 Z"/>'
            f'<path {K} fill="#fff" d="M14 6 L34 6 L34 18 L14 18 Z"/><path {W} stroke="#e8c56a" opacity="1" d="M15 30 L33 30 M15 40 L33 40"/>'
            f'<path {L} d="M4 64 Q10 62 12 70"/></g>')


def shoe(dx, dy, s=1):
    return (f'<g transform="translate({dx},{dy}) scale({s})"><path {K} fill="#e46a5e" d="M2 40 L2 18 Q2 10 12 10 L22 10 Q30 20 44 22 Q58 24 60 34 L60 40 Z"/>'
            f'<path {K} fill="#fff" d="M2 40 L60 40 L60 46 Q60 48 58 48 L4 48 Q2 48 2 46 Z"/>'
            f'<path {L} stroke="#fff" d="M20 14 L28 22 M16 18 L26 26 M12 22 L22 30"/><circle cx="10" cy="26" r="2.4" fill="#fff"/></g>')


def boot(dx, dy):
    return (f'<g transform="translate({dx},{dy})"><path {K} fill="#f0c24b" d="M6 4 L30 4 L30 50 Q50 52 56 64 L56 74 L6 74 Z"/>'
            f'<path {K} fill="#3f78a8" d="M6 68 L56 68 L56 76 Q56 78 54 78 L8 78 Q6 78 6 76 Z"/>'
            f'<path {K} fill="#e2ad2f" d="M4 2 L32 2 L32 12 L4 12 Z"/><path {W} d="M12 22 L12 52"/></g>')


def glove(dx, dy, flip=False):
    t = f'translate({dx},{dy})' + (' translate(46,0) scale(-1,1)' if flip else '')
    f = '#b893dd'
    return (f'<g transform="{t}"><rect {K} fill="{f}" x="6" y="12" width="9" height="30" rx="4.5"/><rect {K} fill="{f}" x="15" y="4" width="9" height="36" rx="4.5"/>'
            f'<rect {K} fill="{f}" x="24" y="6" width="9" height="34" rx="4.5"/><rect {K} fill="{f}" x="33" y="14" width="8.5" height="28" rx="4.25"/>'
            f'<path {K} fill="{f}" d="M4 36 Q-6 30 -4 24 Q0 20 6 28 Z"/>'
            f'<path {K} fill="{f}" d="M4 30 L42 30 L42 52 Q42 62 30 62 L16 62 Q4 62 4 50 Z"/>'
            f'<path {K} fill="#8f68b8" d="M8 60 L38 60 L38 72 L8 72 Z"/><path {L} stroke="#fff" opacity=".6" d="M13 64 L13 70 M19 64 L19 70 M25 64 L25 70 M31 64 L31 70"/></g>')


def tie_art():
    return (f'<path {K} fill="#d4574e" d="M17 6 L33 6 L30 18 L20 18 Z"/>'
            f'<path {K} fill="#d4574e" d="M20 18 L30 18 L38 92 L25 108 L12 92 Z"/>'
            '<g fill="#f6d5cf"><circle cx="25" cy="34" r="2.6"/><circle cx="21" cy="52" r="2.6"/><circle cx="29" cy="58" r="2.6"/>'
            '<circle cx="24" cy="74" r="2.6"/><circle cx="31" cy="84" r="2.6"/><circle cx="18" cy="88" r="2.6"/></g>')


# id, viewBox, Zeichnung
ART = {
    'jumper': ('0 0 100 100',
               f'<path {K} fill="#e88a80" d="M30 20 Q50 30 70 20 L88 32 L95 70 L82 73 L77 46 L76 88 L24 88 L23 46 L18 73 L5 70 L12 32 Z"/>'
               f'<path {K} fill="#d46f66" d="M24 80 L76 80 L76 88 L24 88 Z M6 63 L19 66 L18 73 L5 70 Z M94 63 L81 66 L82 73 L95 70 Z"/>'
               f'<path {K} fill="#d46f66" d="M36 21 Q50 33 64 21 Q50 27 36 21 Z"/>'
               f'<path {W} d="M30 50 l5 6 l5 -6 l5 6 l5 -6 l5 6 l5 -6 l5 6 l5 -6 M30 62 l5 6 l5 -6 l5 6 l5 -6 l5 6 l5 -6 l5 6 l5 -6"/>'),
    'tshirt': ('0 0 100 100',
               f'<path {K} fill="#8fc3ea" d="M33 20 Q50 30 67 20 L90 32 L82 48 L72 43 L72 88 L28 88 L28 43 L18 48 L10 32 Z"/>'
               f'<path {L} d="M38 22 Q50 32 62 22"/>'
               '<path fill="#f6d36b" stroke="#c4952f" stroke-width="1.6" stroke-linejoin="round" d="M50 46 L54 55 L64 56 L57 63 L59 73 L50 68 L41 73 L43 63 L36 56 L46 55 Z"/>'),
    'shirt': ('0 0 100 100',
              f'<path {K} fill="#e2eef9" d="M32 18 L68 18 L88 30 L93 72 L80 74 L76 46 L76 90 L24 90 L24 46 L20 74 L7 72 L12 30 Z"/>'
              f'<path {L} stroke="#9cc3e3" d="M36 40 L36 90 M64 40 L64 90 M18 40 L16 70 M82 40 L84 70"/>'
              f'<path {L} d="M50 30 L50 90"/>'
              f'<path {K} fill="#fff" d="M36 16 L50 30 L42 38 L33 22 Z M64 16 L50 30 L58 38 L67 22 Z"/>'
              '<g fill="#2b2f2c"><circle cx="50" cy="46" r="2"/><circle cx="50" cy="60" r="2"/><circle cx="50" cy="74" r="2"/></g>'
              f'<path {L} d="M56 50 L66 50 L66 60 L56 60 Z"/>'),
    'dress': ('0 0 100 150',
              f'<path {K} fill="#c4a2e3" d="M36 22 L42 22 Q50 34 58 22 L64 22 L66 58 L90 138 Q50 146 10 138 L34 58 Z"/>'
              f'<path {L} d="M38 22 L36 8 M62 22 L64 8"/>'
              f'<path {K} fill="#f0c24b" d="M33 56 L67 56 L67 64 L33 64 Z"/>'
              '<g fill="#fff" opacity=".8"><circle cx="40" cy="84" r="3"/><circle cx="58" cy="80" r="3"/><circle cx="50" cy="100" r="3"/><circle cx="32" cy="110" r="3"/>'
              '<circle cx="66" cy="108" r="3"/><circle cx="44" cy="124" r="3"/><circle cx="74" cy="128" r="3"/><circle cx="24" cy="130" r="3"/><circle cx="58" cy="128" r="3"/></g>'
              f'<path {L} d="M10 138 Q50 146 90 138"/>'),
    'skirt': ('0 0 100 100',
              f'<path {K} fill="#ecc35e" d="M28 20 L72 20 L73 32 L92 82 Q50 90 8 82 L27 32 Z"/>'
              f'<path {K} fill="#d6ad45" d="M28 20 L72 20 L73 32 L27 32 Z"/>'
              f'<path {L} d="M40 32 L30 86 M50 32 L50 88 M60 32 L70 86"/>'),
    'trousers': ('0 0 100 100',
                 f'<path {K} fill="#5d8cc0" d="M28 8 L72 8 L77 94 L57 94 L50 38 L43 94 L23 94 Z"/>'
                 f'<path {K} fill="#4a77a8" d="M28 8 L72 8 L72.6 17 L27.4 17 Z"/>'
                 f'<path {L} stroke="#cfe2f3" d="M50 17 L50 32 M30 22 Q38 26 40 18 M70 22 Q62 26 60 18"/>'),
    'shorts': ('0 0 100 100',
               f'<path {K} fill="#9ccb87" d="M22 24 L78 24 L86 70 L58 74 L50 46 L42 74 L14 70 Z"/>'
               f'<path {K} fill="#7fb069" d="M22 24 L78 24 L79.6 34 L20.4 34 Z"/>'
               f'<path {L} stroke="#fff" d="M50 34 L50 44 M17 62 L42 66 M83 62 L58 66"/>'),
    'jacket': ('0 0 100 100',
               f'<path {K} fill="#f2a65a" d="M34 14 L66 14 L86 28 L93 74 L80 76 L77 46 L76 90 L24 90 L23 46 L20 76 L7 74 L14 28 Z"/>'
               f'<path {K} fill="#e08d3c" d="M34 14 L50 28 L66 14 L60 10 L40 10 Z"/>'
               f'<path {L} d="M50 28 L50 90"/><path {L} stroke-dasharray="1 4" d="M53 30 L53 88"/>'
               f'<path {L} d="M28 66 L40 60 M72 66 L60 60"/><circle cx="50" cy="34" r="2.4" fill="#d6ad45" stroke="#2b2f2c" stroke-width="1.5"/>'),
    'coat': ('0 0 100 150',
             f'<path {K} fill="#b98c62" d="M34 10 L66 10 L86 26 L92 92 L79 94 L76 50 L82 142 L18 142 L24 50 L21 94 L8 92 L14 26 Z"/>'
             f'<path {K} fill="#a2764d" d="M40 10 L50 40 L60 10 Z"/>'
             f'<path {K} fill="#8a6440" d="M23 68 L77 68 L77.6 76 L22.4 76 Z"/>'
             '<g fill="#f0c24b" stroke="#2b2f2c" stroke-width="1.5"><circle cx="43" cy="52" r="3"/><circle cx="57" cy="52" r="3"/><circle cx="43" cy="92" r="3"/><circle cx="57" cy="92" r="3"/><circle cx="43" cy="112" r="3"/><circle cx="57" cy="112" r="3"/></g>'
             f'<path {L} d="M50 40 L50 142"/>'),
    'scarf': ('0 0 60 140',
              f'<path {K} fill="#d9645a" d="M12 18 Q30 -4 48 18 L48 30 Q30 14 12 30 Z"/>'
              f'<path {K} fill="#d9645a" d="M12 22 L28 22 L28 120 L12 120 Z"/>'
              f'<path {K} fill="#d9645a" d="M32 22 L48 22 L50 104 L34 104 Z"/>'
              '<g fill="#fff"><rect x="13.3" y="44" width="13.4" height="8"/><rect x="13.3" y="66" width="13.4" height="8"/><rect x="13.3" y="88" width="13.4" height="8"/>'
              '<rect x="33.3" y="40" width="15" height="8"/><rect x="33.6" y="62" width="15.2" height="8"/><rect x="34" y="84" width="15.4" height="8"/></g>'
              f'<path {L} d="M14 120 L14 130 M18 120 L18 130 M22 120 L22 130 M26 120 L26 130 M36 104 L36 114 M40 104 L40 114 M44 104 L44 114 M48 104 L48 114"/>'),
    'hat': ('0 0 100 100',
            f'<path {K} fill="#e7c873" d="M28 64 Q28 26 50 26 Q72 26 72 64 Z"/>'
            f'<path {K} fill="#c8574e" d="M28.6 52 Q50 58 71.4 52 L71.8 62 Q50 68 28.2 62 Z"/>'
            f'<ellipse {K} fill="#e7c873" cx="50" cy="66" rx="46" ry="12"/>'
            f'<path {K} fill="#e7c873" d="M28 64 Q50 70 72 64 L72 60 Q50 66 28 60 Z" stroke="none"/>'
            f'<path {L} d="M28 63 Q50 70 72 63"/><path {L} stroke="#c4952f" d="M38 40 Q50 34 62 40"/>'),
    'cap': ('0 0 100 100',
            f'<path {K} fill="#3d6797" d="M50 58 L96 62 Q98 72 88 74 L50 70 Z"/>'
            f'<path {K} fill="#4f7fb5" d="M14 66 Q12 28 50 26 Q80 26 84 62 Q50 56 14 66 Z"/>'
            f'<path {L} stroke="#cfe2f3" d="M50 28 Q42 44 44 60 M50 28 Q64 42 66 58"/><circle cx="50" cy="26" r="3.4" fill="#3d6797" stroke="#2b2f2c" stroke-width="2"/>'
            '<path fill="#f6d36b" stroke="#c4952f" stroke-width="1.4" d="M28 46 L31 51 L37 52 L33 56 L34 62 L28 59 L22 62 L23 56 L19 52 L25 51 Z"/>'),
    'tie': ('0 0 50 112', tie_art()),
    'socks': ('0 0 80 86', sock(2, 4, '#8fc3ea') + sock(38, 0, '#8fc3ea')),
    'shoes': ('0 0 100 80', shoe(28, 6, .95) + shoe(4, 28)),
    'boots': ('0 0 100 84', boot(2, 4) + boot(40, 0)),
    'gloves': ('0 0 100 80', glove(8, 6) + glove(50, 2, True)),
}

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


# ------------------------------------------------------------------ Der Schrank (viewBox 0 0 1000 780)
# Plätze: id -> (x, y, Breite, Höhe); die Zeichnung wird in diesen Kasten eingepasst
PLATZ = {
    'hat': (200, 48, 160, 128), 'cap': (410, 50, 150, 124),
    'jumper': (166, 236, 116, 150), 'tshirt': (272, 236, 116, 150), 'shirt': (378, 236, 116, 150), 'jacket': (484, 236, 116, 150),
    'skirt': (184, 420, 124, 136), 'trousers': (322, 414, 132, 152), 'shorts': (466, 420, 124, 124),
    'dress': (612, 228, 120, 186), 'coat': (720, 228, 120, 186),
    'boots': (642, 446, 168, 116),
    'shoes': (180, 600, 180, 112), 'socks': (420, 588, 120, 126), 'gloves': (598, 596, 210, 112),
    'scarf': (48, 140, 86, 230), 'tie': (870, 140, 80, 210),
}
assert set(PLATZ) == set(ART) == set(w['id'] for w in WORT)


def schrank():
    holz, dunkel, innen = '#dcaa70', '#b07c45', '#f8ecd8'
    o = ['<svg class="schrank" viewBox="0 0 1000 780" role="group" aria-label="Kleiderschrank">',
         '<ellipse cx="500" cy="764" rx="470" ry="14" fill="#c5d8e8" opacity=".55"/>',
         # Türen (offen)
         f'<path {K} fill="{holz}" d="M30 40 L142 18 L142 752 L30 728 Z"/><path {L} stroke="{dunkel}" d="M48 70 L124 54 L124 716 L48 700 Z"/>',
         f'<path {K} fill="{holz}" d="M858 18 L970 40 L970 728 L858 752 Z"/><path {L} stroke="{dunkel}" d="M876 54 L952 70 L952 700 L876 716 Z"/>',
         '<circle cx="128" cy="400" r="7" fill="#f0c24b" stroke="#2b2f2c" stroke-width="2"/><circle cx="872" cy="400" r="7" fill="#f0c24b" stroke="#2b2f2c" stroke-width="2"/>',
         # Haken an den Türen
         f'<path {L} stroke-width="4" d="M88 136 L88 150 Q88 158 96 156 M910 136 L910 150 Q910 158 902 156"/>',
         # Kasten
         f'<rect {K} fill="{holz}" x="142" y="18" width="716" height="734" rx="14"/>',
         f'<rect {K} fill="{innen}" x="160" y="36" width="680" height="682" rx="6"/>',
         f'<rect {K} fill="{holz}" x="126" y="4" width="748" height="26" rx="9"/>',
         f'<rect {K} fill="{holz}" x="160" y="186" width="680" height="14"/>',
         f'<rect {K} fill="{holz}" x="160" y="570" width="680" height="14"/>',
         f'<rect {K} fill="{holz}" x="600" y="200" width="12" height="370"/>',
         '<g fill="#f0c24b" stroke="#2b2f2c" stroke-width="2"><circle cx="300" cy="122" r="0" /></g>',
         # Stangen
         '<path d="M168 232 L594 232 M168 418 L594 418 M618 226 L834 226" stroke="#8a97a3" stroke-width="7" stroke-linecap="round"/>',
         # Füsse
         f'<path {K} fill="{dunkel}" d="M170 752 L200 752 L196 770 L174 770 Z M800 752 L830 752 L826 770 L804 770 Z"/>',
         '<text x="786" y="114" font-size="30" fill="#d6ad45" text-anchor="middle">✦ ✧ ✦</text>']
    # Bügel
    for i in ('jumper', 'tshirt', 'shirt', 'jacket', 'dress', 'coat'):
        x, y, w, hh = PLATZ[i]; cx = x + w / 2; ry = 232 if i not in ('dress', 'coat') else 226
        o.append(f'<path {L} stroke-width="3" d="M{cx} {ry + 14} L{cx} {ry - 2} Q{cx} {ry - 12} {cx + 8} {ry - 8} M{cx - 40} {ry + 30} L{cx} {ry + 14} L{cx + 40} {ry + 30}"/>')
    for i in ('skirt', 'trousers', 'shorts'):
        x, y, w, hh = PLATZ[i]; cx = x + w / 2
        o.append(f'<path {L} stroke-width="3" d="M{cx} {430} L{cx} 416 Q{cx} 406 {cx + 8} 410 M{cx - 34} 430 L{cx + 34} 430"/>')
    for i, (x, y, w, hh) in PLATZ.items():
        vb = ART[i][0]
        o.append(f'<g class="it" data-id="{i}" tabindex="0" role="button" aria-label="{i}"><rect class="hit" x="{x}" y="{y}" width="{w}" height="{hh}" rx="16"/>'
                 f'<svg x="{x}" y="{y}" width="{w}" height="{hh}" viewBox="{vb}" overflow="visible">{ART[i][1]}</svg></g>')
    o.append('</svg>')
    return ''.join(o).replace('<g fill="#f0c24b" stroke="#2b2f2c" stroke-width="2"><circle cx="300" cy="122" r="0" /></g>', '')


# ------------------------------------------------------------------ Mia und Noah
def kind(haar, oben, unten, zopf):
    haut = '#f7d5b8'
    o = (f'<svg viewBox="0 0 100 180" class="kind-svg">'
         f'<path {K} fill="{unten}" d="M36 126 L48 126 L48 164 L36 164 Z M52 126 L64 126 L64 164 L52 164 Z"/>'
         f'<path {K} fill="#5f6963" d="M32 164 L49 164 L49 172 L30 172 Q30 166 32 164 Z M51 164 L68 164 Q70 166 70 172 L51 172 Z"/>'
         f'<path d="M30 86 Q16 106 22 126 M70 86 Q84 106 78 126" fill="none" stroke="#2b2f2c" stroke-width="12" stroke-linecap="round"/>'
         f'<path d="M30 86 Q16 106 22 126 M70 86 Q84 106 78 126" fill="none" stroke="{haut}" stroke-width="7" stroke-linecap="round"/>'
         f'<path {K} fill="{oben}" d="M30 82 Q50 72 70 82 L74 134 L26 134 Z"/>'
         f'<rect {K} fill="{haut}" x="44" y="68" width="12" height="10"/>')
    if zopf:
        o += f'<circle {K} fill="{haar}" cx="22" cy="54" r="9"/><circle {K} fill="{haar}" cx="78" cy="54" r="9"/>'
    o += f'<circle {K} fill="{haut}" cx="50" cy="48" r="24"/>'
    if zopf:
        o += f'<path {K} fill="{haar}" d="M26 50 Q22 20 50 20 Q78 20 74 50 Q70 34 56 34 Q52 40 44 34 Q30 34 26 50 Z"/>'
    else:
        o += f'<path {K} fill="{haar}" d="M26 46 Q24 20 50 20 Q76 20 74 46 Q70 36 62 36 L60 30 L54 36 L48 29 L42 36 L36 31 Q30 36 26 46 Z"/>'
    o += ('<circle cx="41" cy="50" r="2.8" fill="#2b2f2c"/><circle cx="59" cy="50" r="2.8" fill="#2b2f2c"/>'
          '<circle cx="36" cy="58" r="4" fill="#f3a6a0" opacity=".6"/><circle cx="64" cy="58" r="4" fill="#f3a6a0" opacity=".6"/>'
          f'<path {L} d="M43 60 Q50 66 57 60"/></svg>')
    return o


MIA = kind('#8a5a33', '#f2a0a8', '#5d6f8a', True)
NOAH = kind('#3b2b22', '#7fb069', '#4a77a8', False)


def alle(spiel):
    items = [dict(w, vb=ART[w['id']][0]) for w in WORT]
    spiel(id='kleiderschrank', titel='Kleiderschrank', icon='👚', fach='Englisch', thema='Clothes', stufe='3.–6. Klasse', sort=1, n=10,
          sterne={'modus': 'runde', 'n': 10},
          kurz='Kleider auf Englisch: anschauen, hören, schreiben, sprechen und «This is my dress.»',
          intro='Im Schrank hängen viele Kleider. Wie heissen sie auf Englisch? Hör gut zu und sprich nach!',
          levels=[dict(name='Entdecken', info='Antippen, hören und finden', t=0),
                  dict(name='Auswählen', info='Wie heisst es auf Englisch?', t=1),
                  dict(name='Schreiben', info='Das englische Wort schreiben', t=2),
                  dict(name='Sprechen', info='Das Wort laut sagen 🎤', t=3),
                  dict(name='my, your, his, her', info='Wem gehört es?', t=4),
                  dict(name='Sätze', info='This is my … / These are my …', t=5)],
          daten={'items': items, 'svg': {k: v[1] for k, v in ART.items()}, 'schrank': schrank(), 'mia': MIA, 'noah': NOAH, 'aehnlich': AEHNLICH},
          css=CSS, js=JS)


CSS = r"""
.ks{display:flex;flex-direction:column;align-items:center;gap:12px;width:100%}
.schrank{display:block;width:min(100%,640px,calc((100vh - 250px) * 1.28));height:auto}
.schrank .hit{fill:transparent}
.schrank .it{cursor:pointer;transform-box:fill-box;transform-origin:center;transition:transform .15s,filter .15s;outline:none}
.schrank .it:hover,.schrank .it:focus-visible{transform:scale(1.06)}
.schrank .it.an{filter:drop-shadow(0 0 10px #f0c24b) drop-shadow(0 0 4px #f0c24b);transform:scale(1.08)}
.schrank .it.no{animation:wk2 .4s}
@keyframes wk2{25%{transform:rotate(-4deg)}75%{transform:rotate(4deg)}}
.schrank .it.seen .hit{fill:rgba(240,194,75,.13)}
.wortkarte{min-height:64px;display:flex;align-items:center;gap:12px;background:#fff;border:2px solid var(--line);border-radius:20px;padding:6px 18px;box-shadow:var(--sch-k)}
.wortkarte b{font:700 clamp(26px,6vw,38px) system-ui,-apple-system,sans-serif;color:var(--sky-d)}
.wortkarte span{color:var(--soft);font-size:20px}
.laut{display:inline-grid;place-items:center;width:52px;height:52px;border-radius:50%;background:var(--sky);border:2px solid var(--ink);font-size:24px;box-shadow:var(--sch-k);flex:none}
.laut:active{transform:scale(.94)}
.bild{width:min(56vw,230px);aspect-ratio:1;display:grid;place-items:center;background:#fff;border:3px solid var(--gold);border-radius:30px;box-shadow:inset 0 0 0 6px #fff,var(--sch);padding:16px;position:relative}
.bild svg{width:100%;height:100%;display:block}
.bild .laut{position:absolute;right:-14px;bottom:-14px}
.wahl{display:grid;grid-template-columns:1fr 1fr;gap:12px;width:min(100%,560px)}
.wahl button{background:#fff;border:2px solid var(--ink);border-radius:20px;box-shadow:var(--sch-k);min-height:70px;padding:8px;font:700 clamp(22px,5vw,30px) system-ui,-apple-system,sans-serif;transition:transform .12s}
.wahl button:active{transform:scale(.96)}
.wahl button.ok{background:#e7f3df;border-color:var(--ok)}.wahl button.no{background:#fbe5e2;border-color:var(--no)}.wahl button.hint{background:var(--sun);border-color:var(--gold)}
.schreib{display:flex;gap:10px;width:min(100%,480px)}
.schreib input{flex:1;min-width:0;font:700 30px system-ui,-apple-system,sans-serif;padding:8px 16px;border-radius:18px;border:2px solid var(--ink);background:#fff;color:var(--ink);text-align:center;box-shadow:var(--sch-k)}
.schreib input:focus{outline:3px solid var(--gold);outline-offset:2px}
.schreib input.ok{background:#e7f3df;border-color:var(--ok)}.schreib input.no{background:#fbe5e2;border-color:var(--no)}
.luecke{font:700 28px system-ui,-apple-system,sans-serif;letter-spacing:.18em;color:var(--sky-d)}
.mik{width:118px;height:118px;border-radius:50%;background:var(--rose);border:3px solid var(--ink);font-size:52px;box-shadow:var(--sch);display:grid;place-items:center}
.mik.hoert{background:#fbe5e2;animation:puls 1s infinite}
@keyframes puls{50%{box-shadow:0 0 0 14px rgba(200,87,78,.18),var(--sch)}}
.gehoert{color:var(--soft);font-size:20px;min-height:26px;text-align:center}
.buehne{width:min(100%,620px);display:grid;grid-template-columns:1fr 1.15fr 1fr;grid-template-rows:auto auto;align-items:end;column-gap:6px;row-gap:6px}
.buehne .sprech{grid-row:1;min-height:70px;display:flex;align-items:flex-end}
.blase{position:relative;background:#fff;border:2px solid var(--ink);border-radius:18px;padding:8px 12px;font-size:clamp(19px,4.4vw,24px);box-shadow:var(--sch-k);line-height:1.2}
.blase::after{content:"";position:absolute;bottom:-11px;left:30px;width:18px;height:18px;background:#fff;border-right:2px solid var(--ink);border-bottom:2px solid var(--ink);transform:rotate(45deg)}
.blase.r::after{left:auto;right:30px}
.erzaehl{grid-column:1/4;display:flex;align-items:center;gap:10px;justify-content:center}
.erzaehl img{width:54px;height:54px;object-fit:contain}
.erzaehl .blase::after{display:none}
.kind{grid-row:2;display:flex;flex-direction:column;align-items:center;position:relative}
.kind-svg{width:min(100%,120px);height:auto;display:block}
.kind .nm2{background:var(--sun);border-radius:10px;padding:0 10px;font-size:20px;margin-top:2px}
.kind.own::before{content:"";position:absolute;left:8%;right:8%;bottom:20px;height:22px;border-radius:50%;background:radial-gradient(#f0c24b 0%,rgba(240,194,75,0) 70%)}
.ding{grid-row:2;grid-column:2;display:flex;align-items:center;padding-bottom:34px}
.ding .bild{width:min(30vw,150px);padding:10px;border-width:3px}
.ding.l{justify-content:flex-start}.ding.r{justify-content:flex-end}.ding.m{justify-content:center}
.ding.l .bild::before,.ding.r .bild::before{content:"";position:absolute;top:50%;width:16px;height:16px;background:#fff;border:3px solid var(--gold);border-right:0;border-top:0;transform:translateY(-50%) rotate(45deg)}
.ding.l .bild::before{left:-10px}.ding.r .bild::before{right:-10px;transform:translateY(-50%) rotate(-135deg)}
.wer{grid-column:1/4;text-align:center;color:var(--soft);font-size:19px;margin-top:-4px}
.satz{min-height:66px;width:min(100%,600px);display:flex;flex-wrap:wrap;gap:8px;justify-content:center;align-items:center;background:#fff;border:2px dashed var(--line2);border-radius:20px;padding:8px}
.satz.ok{border:2px solid var(--ok);background:#f1f7ec}.satz.no{border-color:var(--no)}
.kaertli{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;width:min(100%,600px)}
.kaertli button,.satz button{background:#fff;border:2px solid var(--ink);border-radius:14px;padding:6px 14px;min-height:50px;font:700 clamp(20px,4.6vw,26px) system-ui,-apple-system,sans-serif;box-shadow:var(--sch-k)}
.satz button{background:var(--sky)}
.kaertli button.weg{visibility:hidden}
.satz .pkt{font:700 26px system-ui,sans-serif}
.de{font-size:clamp(22px,5vw,28px);text-align:center}
@media (max-height:700px){.bild{width:min(44vw,170px)}.mik{width:92px;height:92px;font-size:40px}}
@media (max-width:520px){.kind-svg{max-width:88px}.ding .bild{width:min(32vw,118px)}.buehne .sprech{min-height:56px}.kaertli button,.satz button{min-height:44px;padding:4px 12px}}
"""

JS = r"""
var IT = D.items, ITM = {}; IT.forEach(function (x) { ITM[x.id] = x; });
var BOTH = 'Mia und Noah';
// ---------- Bilder
function art(id, zwei) {
  var x = ITM[id], s = D.svg[id];
  if (!zwei) return '<svg viewBox="' + x.vb + '" aria-hidden="true" data-k="' + id + '">' + s + '</svg>';
  var v = x.vb.split(' ').map(Number), w = v[2], hh = v[3];
  return '<svg viewBox="0 0 ' + (w * 1.6) + ' ' + (hh * 1.12) + '" aria-hidden="true" data-k="' + id + '"><g transform="translate(0,' + (hh * .12) + ') scale(.95)">' + s + '</g><g transform="translate(' + (w * .62) + ',0) scale(.95)">' + s + '</g></svg>';
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
function neu(c, html) { var e = document.createElement('div'); if (c) e.className = c; if (html != null) e.innerHTML = html; return e; }

// ---------- Stufe 1: Schrank entdecken, dann finden
function stufeSchrank(api) {
  var w = neu('ks'); api.stage.appendChild(w);
  var karte = neu('wortkarte', '<span>Tippe auf ein Kleidungsstück im Schrank.</span>');
  var holder = neu('', D.schrank); var sv = holder.firstChild;
  var los = document.createElement('button'); los.className = 'go sun'; los.textContent = 'Finde die Kleider! →';
  w.appendChild(karte); w.appendChild(sv); w.appendChild(los);
  var seen = {}, phase = 'schau', liste = reihe(G.n), k = 0, ziel = null, lock = false;
  api.msg('<span class="em">👀</span> Schau in den Schrank! Tippe auf die Kleider und hör gut zu.');
  function itEl(id) { return sv.querySelector('[data-id="' + id + '"]'); }
  function zeig(id) {
    var x = ITM[id]; karte.innerHTML = ''; karte.appendChild(lautBtn(x.en));
    karte.appendChild(neu('', '<b>' + h(x.en) + '</b> <span>' + h(x.de) + '</span>'));
  }
  function frage() {
    ziel = liste[k]; lock = false;
    var t = 'Find the ' + ziel.en + '!';
    karte.innerHTML = ''; karte.appendChild(lautBtn(t)); karte.appendChild(neu('', '<b>Find the ' + h(ziel.en) + '!</b>'));
    api.msg('<span class="em">🔎</span> Hör zu und tippe auf das richtige Kleidungsstück.');
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
        api.msg('<span class="em">' + (n >= IT.length ? '🌟' : '👆') + '</span> ' + (n >= IT.length ? 'Du hast alles angeschaut! Jetzt «Finde die Kleider!»' : n + ' von ' + IT.length + ' angeschaut.'));
        return;
      }
      if (lock || !ziel) return; lock = true;
      var ok = id === ziel.id, rich = itEl(ziel.id);
      Array.prototype.forEach.call(sv.querySelectorAll('.it.an'), function (e) { e.classList.remove('an'); });
      rich.classList.add('an');
      if (!ok) { g.classList.remove('no'); void g.getBBox(); g.classList.add('no'); }
      say(ok ? ziel.en : 'This is the ' + ziel.en + '.');
      api.msg(ok ? '<span class="em">✨</span> Yes! <b>' + h(ziel.en) + '</b> = ' + h(ziel.de) : '<span class="em">💡</span> Das ist <b>' + h(ITM[id].en) + '</b>. Gesucht war <b>' + h(ziel.en) + '</b> (leuchtet).');
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
    var x = liste[k], lock = false; w.innerHTML = '';
    var b = neu('bild', art(x.id)); w.appendChild(b);
    var opts = [x].concat(pick(IT.filter(function (y) { return y.id !== x.id; }), 3));
    var wahl = neu('wahl'); w.appendChild(wahl);
    api.msg('<span class="em">🤔</span> Wie heisst das auf Englisch?');
    shuffle(opts).forEach(function (o) {
      var bt = document.createElement('button'); bt.textContent = o.en;
      bt.onclick = function () {
        if (lock) return; lock = true; var ok = o.id === x.id;
        bt.classList.add(ok ? 'ok' : 'no');
        if (!ok) Array.prototype.forEach.call(wahl.children, function (c) { if (c.textContent === x.en) c.classList.add('hint'); });
        say(x.en); b.appendChild(lautBtn(x.en));
        api.msg(ok ? '<span class="em">' + pick(['✨', '🌟', '👏'], 1)[0] + '</span> Richtig! <b>' + h(x.en) + '</b> = ' + h(x.de) : '<span class="em">💡</span> Das ist <b>' + h(x.en) + '</b> (' + h(x.de) + ').');
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
    var x = liste[k], vers = 0, lock = false; w.innerHTML = '';
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
        api.msg('<span class="em">💡</span> Noch nicht. Tipp: So viele Buchstaben hat das Wort. Hör nochmal zu!');
        api.later(function () { inp.classList.remove('no'); inp.select(); }, 600);
        return;
      }
      lock = true; inp.classList.add(ok ? 'ok' : 'no'); inp.disabled = true;
      if (!ok) { lu.textContent = x.en; }
      if (vers === 0 || !ok) b.appendChild(lautBtn(x.en));
      say(x.en);
      api.msg(ok ? '<span class="em">🌟</span> Richtig geschrieben: <b>' + h(x.en) + '</b>!' : '<span class="em">📝</span> So schreibt man es: <b>' + h(x.en) + '</b>');
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
    var x = liste[k], vers = 0, lock = false; w.innerHTML = '';
    var b = neu('bild', art(x.id)); b.appendChild(lautBtn(x.en)); w.appendChild(b);
    var mik = document.createElement('button'); mik.className = 'mik'; mik.setAttribute('aria-label', 'Sprechen'); mik.textContent = '🎤';
    var info = neu('gehoert', ''); w.appendChild(mik); w.appendChild(info);
    var selbst = !SR || SR_AUS;
    api.msg(selbst ? '<span class="em">🗣️</span> Sag das Wort laut auf Englisch! <small>Tippe auf 🔊 zum Vorhören, dann auf 🎤.</small>'
                   : '<span class="em">🗣️</span> Tippe auf 🎤 und sag das Wort auf Englisch! <small>(🔊 = vorhören)</small>');
    function fertig(ok) {
      if (lock) return; lock = true; mik.disabled = true; mik.classList.remove('hoert');
      say(x.en);
      api.msg(ok ? '<span class="em">🌟</span> Super ausgesprochen: <b>' + h(x.en) + '</b>!' : '<span class="em">👂</span> Hör nochmal gut zu: <b>' + h(x.en) + '</b>');
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
        bad(); api.msg('<span class="em">🔁</span> Fast! Hör mit 🔊 zu und versuch es nochmal.');
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
var PR = {
  my: { de: 'mein', wer: 'self' }, your: { de: 'dein', wer: 'other' }, his: { de: 'sein', wer: 'noah' },
  her: { de: 'ihr', wer: 'mia' }, our: { de: 'unser', wer: 'beide-self' }, their: { de: 'ihr', wer: 'beide' }
};
var PAAR = { my: 'your', your: 'my', his: 'her', her: 'his', our: 'their', their: 'our' };
function aufgabe(x, mehrErlaubt) {
  var p = pick(['my', 'your', 'his', 'her', 'my', 'your', 'his', 'her', 'our', 'their'], 1)[0], spr = null, own;
  var c = PR[p].wer;
  if (c === 'self') { own = pick(['mia', 'noah'], 1)[0]; spr = own; }
  else if (c === 'other') { own = pick(['mia', 'noah'], 1)[0]; spr = own === 'mia' ? 'noah' : 'mia'; }
  else if (c === 'beide-self') { own = 'beide'; spr = pick(['mia', 'noah'], 1)[0]; }
  else own = c;
  var enPl = !x.sg || (mehrErlaubt && Math.random() < 0.45);
  var dePl = x.dg === 'p' || (x.sg && enPl);
  var g = dePl ? 'p' : x.dg, noun = dePl && x.sg ? x.dpl : x.dn;
  var poss = PR[p].de + (g === 'f' || g === 'p' ? 'e' : '');
  return { x: x, p: p, own: own, spr: spr, enPl: enPl, zwei: !!(x.sg && enPl),
    deP: poss + ' ' + noun, deS: (dePl ? 'Das sind ' : 'Das ist ') + poss + ' ' + noun + '.',
    word: enPl ? x.pl : x.sg, enP: p + ' ' + (enPl ? x.pl : x.sg),
    enS: (enPl ? 'These are ' : 'This is ') + p + ' ' + (enPl ? x.pl : x.sg) };
}
function buehne(a, text) {
  var b = neu('buehne');
  if (a.spr) {
    var bl = neu('sprech', '<div class="blase' + (a.spr === 'noah' ? ' r' : '') + '">' + text + '</div>');
    bl.style.gridColumn = a.spr === 'mia' ? '1/3' : '2/4'; if (a.spr === 'noah') bl.style.justifyContent = 'flex-end';
    b.appendChild(bl);
  } else b.appendChild(neu('erzaehl', '<img src="../bilder/eule.webp" alt="" onerror="this.replaceWith(\'🦉\')"><div class="blase">' + text + '</div>'));
  var m = neu('kind' + (a.own === 'mia' || a.own === 'beide' ? ' own' : ''), D.mia + '<span class="nm2">Mia</span>'); m.style.gridColumn = '1';
  var n = neu('kind' + (a.own === 'noah' || a.own === 'beide' ? ' own' : ''), D.noah + '<span class="nm2">Noah</span>'); n.style.gridColumn = '3';
  var d = neu('ding ' + (a.own === 'mia' ? 'l' : a.own === 'noah' ? 'r' : 'm'), '<div class="bild">' + art(a.x.id, a.zwei) + '</div>');
  b.appendChild(m); b.appendChild(d); b.appendChild(n);
  b.appendChild(neu('wer', a.spr ? (a.spr === 'mia' ? 'Mia' : 'Noah') + ' sagt:' : ''));
  if (!a.spr) b.lastChild.textContent = '🦉 erzählt über ' + (a.own === 'beide' ? 'Mia und Noah' : a.own === 'mia' ? 'Mia' : 'Noah') + '.';
  else if (a.spr) b.lastChild.textContent = (a.spr === 'mia' ? 'Mia' : 'Noah') + ' spricht' + (a.p === 'your' ? ' mit ' + (a.spr === 'mia' ? 'Noah' : 'Mia') : a.p === 'our' ? ' über sich und ' + (a.spr === 'mia' ? 'Noah' : 'Mia') : ' über sich') + '.';
  return b;
}
function tippPr(a) {
  return { my: '«mein» = my', your: '«dein» = your', his: 'Es gehört Noah (einem Jungen) → his', her: 'Es gehört Mia (einem Mädchen) → her',
    our: '«unser» = our', their: 'Es gehört Mia und Noah → their' }[a.p];
}
function stufeBegleiter(api) {
  var w = neu('ks'); api.stage.appendChild(w); var liste = reihe(G.n), k = 0;
  function frage() {
    var a = aufgabe(liste[k], false), lock = false; w.innerHTML = '';
    w.appendChild(buehne(a, '<b>' + h(a.deP) + '</b>'));
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
        api.msg(ok ? '<span class="em">✨</span> Richtig: <b>' + h(a.enP) + '</b>' : '<span class="em">💡</span> ' + h(tippPr(a)) + ': <b>' + h(a.enP) + '</b>');
        k++; if (!api.answer(ok)) return;
        api.later(frage, ok ? 1500 : 3000);
      };
      wahl.appendChild(bt);
    });
  }
  frage();
}
function stufeSaetze(api) {
  var w = neu('ks'); api.stage.appendChild(w); var liste = reihe(G.n), k = 0;
  function frage() {
    var a = aufgabe(liste[k], true), vers = 0, lock = false; w.innerHTML = '';
    w.appendChild(buehne(a, '<b>' + h(a.deS) + '</b>'));
    var ziel = a.enS.split(' ');
    var dazu = [a.enPl ? 'This' : 'These', a.enPl ? 'is' : 'are', PAAR[a.p]];
    if (a.x.sg) dazu.push(a.enPl ? a.x.sg : a.x.pl);
    var satz = neu('satz'), kae = neu('kaertli'); w.appendChild(satz); w.appendChild(kae);
    var go = document.createElement('button'); go.className = 'go'; go.textContent = 'Prüfen'; w.appendChild(go);
    api.msg('<span class="em">🧩</span> Bau den Satz auf Englisch! Tippe die Wörter der Reihe nach an.');
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
        api.msg('<span class="em">💡</span> Noch nicht ganz. ' + h(tipp));
        api.later(function () { satz.classList.remove('no', 'shake'); gewaehlt.forEach(function (b) { b.classList.remove('weg'); }); gewaehlt = []; zeichnen(); }, 1500);
        return;
      }
      lock = true; go.remove();
      if (!ok) { satz.innerHTML = ''; ziel.forEach(function (t) { var e = document.createElement('button'); e.textContent = t; satz.appendChild(e); }); satz.appendChild(neu('pkt', '.')); }
      satz.classList.add(ok ? 'ok' : 'no'); satz.appendChild(lautBtn(a.enS + '.'));
      say(a.enS + '.');
      api.msg(ok ? '<span class="em">🌟</span> Super! <b>' + h(a.enS) + '.</b>' : '<span class="em">📝</span> So heisst der Satz: <b>' + h(a.enS) + '.</b>');
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
