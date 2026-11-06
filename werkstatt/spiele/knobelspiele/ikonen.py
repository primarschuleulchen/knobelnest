# Gezeichnete Symbole statt Emojis (Wunsch der Lehrerin: keine Emojis in den Aufgaben).
# ICON_JS kommt in den Rahmen aller Knobelspiele: ik('haus', 40) gibt ein SVG (bzw. bei der Eule ein Bild) zurück.
import base64, os

HIER = os.path.dirname(os.path.abspath(__file__))
_eule = os.path.join(HIER, '..', '..', '..', 'bilder', 'eule.webp')
with open(_eule, 'rb') as f:
    EULE = 'data:image/webp;base64,' + base64.b64encode(f.read()).decode()

# viewBox jeweils 0 0 24 24; «c» = currentColor (Knöpfe), sonst feste Farben
SVG = {
    'laut': '<path d="M4 9h4l5-4v14l-5-4H4z" fill="currentColor"/><path d="M16 8.5a5 5 0 0 1 0 7M18.5 6a8.5 8.5 0 0 1 0 12" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>',
    'stumm': '<path d="M4 9h4l5-4v14l-5-4H4z" fill="currentColor"/><path d="M16.5 9.5l5 5M21.5 9.5l-5 5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>',
    'mikro': '<rect x="9" y="3" width="6" height="11" rx="3" fill="currentColor"/><path d="M6 11a6 6 0 0 0 12 0M12 17v4M8.5 21h7" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>',
    'pause': '<rect x="6" y="5" width="4" height="14" rx="1.5" fill="currentColor"/><rect x="14" y="5" width="4" height="14" rx="1.5" fill="currentColor"/>',
    'play': '<path d="M8 5l11 7-11 7z" fill="currentColor"/>',
    'uhr': '<circle cx="12" cy="13.5" r="7.5" fill="none" stroke="currentColor" stroke-width="2"/><path d="M12 13.5V9.5M10 3h4M18 7l1.5-1.5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>',
    'pokal': '<path d="M7 3h10v5a5 5 0 0 1-10 0z" fill="#f2c037" stroke="#c4952f" stroke-width="1.2"/><path d="M7 5H4a3 3 0 0 0 3 4M17 5h3a3 3 0 0 1-3 4" fill="none" stroke="#c4952f" stroke-width="1.5"/><path d="M11 13h2v4h-2z" fill="#d6ad45"/><rect x="7.5" y="17" width="9" height="3.5" rx="1" fill="#b98b4e"/>',
    'stern': '<path d="M12 2.5l2.9 6 6.6.8-4.9 4.5 1.3 6.5L12 17l-5.9 3.3 1.3-6.5L2.5 9.3l6.6-.8z" fill="#f2c037" stroke="#c4952f" stroke-width="1.2" stroke-linejoin="round"/>',
    'herz': '<path d="M12 20s-7.5-4.6-7.5-10A4.3 4.3 0 0 1 12 7.3 4.3 4.3 0 0 1 19.5 10C19.5 15.4 12 20 12 20z" fill="#e8574c" stroke="#b8392f" stroke-width="1"/>',
    'herzleer': '<path d="M12 20s-7.5-4.6-7.5-10A4.3 4.3 0 0 1 12 7.3 4.3 4.3 0 0 1 19.5 10C19.5 15.4 12 20 12 20z" fill="#fff" stroke="#c9ced6" stroke-width="1.6"/>',
    'haus': '<path d="M3 11.5L12 4l9 7.5" fill="none" stroke="#b8392f" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/><path d="M5.5 10.5V20h13v-9.5L12 5z" fill="#f6e3c2" stroke="#b98b4e" stroke-width="1.2"/><path d="M3.5 11.5L12 4.5l8.5 7" fill="none" stroke="#d6574c" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/><rect x="10" y="13.5" width="4" height="6.5" rx="1" fill="#b98b4e"/><rect x="15" y="12" width="2.6" height="2.6" fill="#8fc6ea"/>',
    'nuss': '<path d="M12 5c4.5 0 7 3.5 7 8s-3 7.5-7 7.5S5 17.5 5 13s2.5-8 7-8z" fill="#b5793f" stroke="#7d4f25" stroke-width="1.2"/><path d="M6 10.5c2-3.5 10-3.5 12 0-1-4-3.5-6-6-6s-5 2-6 6z" fill="#7d4f25"/><path d="M12 4.5V2.5" stroke="#5f3a18" stroke-width="1.6" stroke-linecap="round"/><ellipse cx="9.5" cy="14" rx="1.4" ry="2.4" fill="#d79a5e"/>',
    'baum': '<rect x="10.8" y="14" width="2.4" height="7" rx="1" fill="#8a5a2f"/><circle cx="12" cy="10" r="6.5" fill="#6fb04f"/><circle cx="9.5" cy="8.5" r="2.3" fill="#8cc96a"/>',
    'stein': '<path d="M4 18c-.5-4 2-8 6-9.5s8 .5 9.5 4.5S19 19 15 19H6c-1 0-1.8-.4-2-1z" fill="#a3abb5" stroke="#78818c" stroke-width="1.2"/><path d="M9 11.5c1.5-1 3.5-1.2 5-.5" fill="none" stroke="#c9ced6" stroke-width="1.4" stroke-linecap="round"/>',
    'hahn': '<rect x="2" y="7" width="9" height="5" rx="1.5" fill="#9aa8b4"/><path d="M11 8.5h4.5a3 3 0 0 1 3 3V14h-4v-1.5H11z" fill="#b6c2cc" stroke="#7d8a96" stroke-width="1"/><rect x="5" y="4" width="4" height="3" rx="1" fill="#7d8a96"/><path d="M16.5 16.5c0 1.5-1 2.5-2 2.5s-2-1-2-2.5 2-4 2-4 2 2.5 2 4z" fill="#5fb0e8"/>',
    'blume': '<path d="M12 13v8" stroke="#5f9a4a" stroke-width="2" stroke-linecap="round"/><path d="M12 18c2-2.5 4-2.5 5.5-2-1 2-3 3-5.5 2z" fill="#6fb04f"/><g fill="#f08aa0"><circle cx="12" cy="5.5" r="2.8"/><circle cx="15.5" cy="8.2" r="2.8"/><circle cx="14" cy="12" r="2.8"/><circle cx="10" cy="12" r="2.8"/><circle cx="8.5" cy="8.2" r="2.8"/></g><circle cx="12" cy="9" r="2.3" fill="#f2c037"/>',
    'welk': '<path d="M12 21v-7c0-3 2-4.5 4-5" fill="none" stroke="#9a9a6a" stroke-width="2" stroke-linecap="round"/><g fill="#c7a38a"><circle cx="17.5" cy="10" r="2.3"/><circle cx="18" cy="13.5" r="2.3"/><circle cx="15" cy="12.5" r="2.3"/></g><circle cx="16.8" cy="12" r="1.6" fill="#b59a52"/><path d="M12 18c-2-2-3.5-2-5-1.5 1 1.8 3 2.6 5 1.5z" fill="#a8a878"/>',
    'rakete': '<path d="M12 2c3 2.5 4.5 6 4.5 10v4h-9v-4c0-4 1.5-7.5 4.5-10z" fill="#f4f6f9" stroke="#7d8a96" stroke-width="1.2"/><circle cx="12" cy="9.5" r="2.2" fill="#8fc6ea" stroke="#3f8fdc" stroke-width="1"/><path d="M7.5 12.5L4.5 17v2l3-2M16.5 12.5l3 4.5v2l-3-2" fill="#e8574c"/><path d="M9.5 16h5l-1 3h-3z" fill="#e8574c"/><path d="M10.5 19h3l-1.5 3.5z" fill="#f2a63a"/>',
    'mond': '<circle cx="12" cy="12" r="9" fill="#f6dc7a" stroke="#d6ad45" stroke-width="1.2"/><circle cx="9" cy="9" r="1.8" fill="#e7c55a"/><circle cx="14.5" cy="14.5" r="2.4" fill="#e7c55a"/><circle cx="15" cy="7.5" r="1.1" fill="#e7c55a"/>',
    'nadel': '<path d="M12 22s-6.5-7-6.5-12a6.5 6.5 0 0 1 13 0c0 5-6.5 12-6.5 12z" fill="#e8574c" stroke="#b8392f" stroke-width="1"/><circle cx="12" cy="10" r="2.5" fill="#fff"/>',
}


def svg(name, size=24, attr=''):
    # Für Python-Bauskripte (fester Text)
    return '<svg width="%s" height="%s" viewBox="0 0 24 24" aria-hidden="true" %s>%s</svg>' % (size, size, attr, SVG[name])


ICON_JS = ('var IK = %s, IK_EULE = "%s";\n' % (str({k: v for k, v in SVG.items()}).replace("': '", "':'"), EULE) +
           r"""function ik(n, s, cls) {
  s = s || 24;
  if (n === 'eule') return '<img class="ik' + (cls ? ' ' + cls : '') + '" src="' + IK_EULE + '" alt="" width="' + s + '" height="' + s + '" style="width:' + s + 'px;height:' + s + 'px;object-fit:contain;vertical-align:middle">';
  return '<svg class="ik' + (cls ? ' ' + cls : '') + '" width="' + s + '" height="' + s + '" viewBox="0 0 24 24" aria-hidden="true" style="vertical-align:middle">' + IK[n] + '</svg>';
}
""")
