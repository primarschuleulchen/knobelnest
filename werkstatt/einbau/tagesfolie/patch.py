import sys
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    assert c >= 1, 'NOT FOUND: ' + a[:80]
    s = s.replace(a, b, n)

# 0) Titel
if '<title>' not in s:
    rep('<meta charset=utf8>', '<meta charset=utf8><title>Tagesfolie</title>')

# 1) Verbindung zu Knobelnest
rep('(() => {\n"use strict";', '''(() => {
"use strict";
// Knobelnest: Klassenliste, Speicher und Arbeitsstand-Tafel kommen aus dem Portal
const KN = (() => { try { return window.parent !== window && window.parent.knTagesfolie || null; } catch { return null; } })();
if (KN) window.claude = KN.claude;''')

# 2) Speicher pro Lehrperson auf diesem Gerät
rep('const LS = "tagesfolien2";', 'const LS = "tagesfolien2" + (KN ? "-" + KN.uid : "");')

# 3) Klassenliste immer aus der Klassenkiste
rep('  s.roster = s.roster || []; s.groupSets', '''  s.roster = KN && KN.roster.length ? KN.roster.slice() : (s.roster || []); s.groupSets''')
rep('  return s;\n', '''  if (KN && KN.roster.length) s.screens.forEach(sc => sc.widgets.forEach(w => { if (w.type === "random" && !(w.data.names || "").trim()) w.data.editing = false; }));
  return s;
''', 1)

# 4) Zufallsname: mit Klassenliste direkt bereit
rep('random:  { lab: "Zufallsname", w: 24, h: 30, d: () => ({ names: "", pick: "", editing: true }),',
    'random:  { lab: "Zufallsname", w: 24, h: 30, d: () => ({ names: "", pick: "", editing: !(KN && KN.roster.length) }),')
rep('<textarea id="names-${w.id}" placeholder="Namen eintragen, ein Name pro Zeile" aria-label="Namen">${esc(d.names)}</textarea>',
    '${KN && KN.roster.length && !(d.names || "").trim() ? `<p class="hint" style="margin:0 0 4px">Leer lassen = ganze Klasse ${esc(KN.className)}</p>` : ""}<textarea id="names-${w.id}" placeholder="${KN && KN.roster.length ? "Leer lassen für die ganze Klasse, oder eigene Namen, einer pro Zeile" : "Namen eintragen, ein Name pro Zeile"}" aria-label="Namen">${esc(d.names)}</textarea>')

# 5) Klassenliste-Dialog: Namen kommen aus der Klassenkiste
rep('''    return `<p class="hint">Ein Name pro Zeile. Die Liste gilt für alle Gruppen- und Zufallsname-Widgets.</p>
    <textarea id="rosterTxt" rows="9" aria-label="Klassenliste">${esc(S.roster.join("\\n"))}</textarea>
    <div style="margin-top:8px"><button class="sbtn rose" data-rsave>Klassenliste speichern</button></div>''',
'''    return (KN ? `<p class="hint">Die Namen kommen aus der Klassenkiste (Klasse ${esc(KN.className)}). Ändern können Sie sie im Portal unter «Kinder».</p>` : `<p class="hint">Ein Name pro Zeile. Die Liste gilt für alle Gruppen- und Zufallsname-Widgets.</p>
    <textarea id="rosterTxt" rows="9" aria-label="Klassenliste">${esc(S.roster.join("\\n"))}</textarea>
    <div style="margin-top:8px"><button class="sbtn rose" data-rsave>Klassenliste speichern</button></div>`) + `''')
# the original continued with "\n    <h3 ..." inside same template literal; we re-opened a template above
# 6) Neues Widget: Arbeitsstand-Tafel (live)
rep('  random:  { lab: "Zufallsname",', '''  stand:   { lab: "Arbeitsstand", w: 50, h: 60, d: () => ({}), icon: `<rect x="4" y="6" width="24" height="20" rx="3" fill="none" stroke="currentColor" stroke-width="2.4"/><path d="M4 13h24M12 6v20M20 6v20" stroke="currentColor" stroke-width="2"/><circle cx="8" cy="19" r="2" fill="currentColor"/><circle cx="24" cy="22" r="2" fill="currentColor"/>` },
  random:  { lab: "Zufallsname",''')
rep('const DOCK = ["title","date","clock","timer","|","list","check","plan","material","note","image","|","symbol","traffic","random","groups"];',
    'const DOCK = ["title","date","clock","timer","|","list","check","plan","material","note","image","|","symbol","traffic","random","groups"].concat(KN ? ["|","stand"] : []);')
rep('    case "image": return `<div class="t-img">',
    '''    case "stand": return KN ? `<div class="t-stand"><iframe src="${esc(KN.boardUrl)}" title="Arbeitsstand-Tafel" tabindex="-1"></iframe></div>` : `<div class="emptyhint">Die Arbeitsstand-Tafel gibt es nur in der Klassenkiste.</div>`;
    case "image": return `<div class="t-img">''')
rep('const DRAG_BODY = new Set(["title", "date", "clock", "symbol", "traffic", "image"]);',
    'const DRAG_BODY = new Set(["title", "date", "clock", "symbol", "traffic", "image", "stand"]);')
rep('.w.image .card{background:none;box-shadow:none}', '''.w.image .card{background:none;box-shadow:none}
.t-stand{position:absolute;inset:0}
.t-stand iframe{width:100%;height:100%;border:0;display:block;pointer-events:none}
.kn-back{font-weight:700}''')

# 7) Zurück ins Portal
rep('''    <div class="tabs" id="tabs" aria-label="Meine Bildschirme"></div>''', '''    <button class="pill kn-back" id="knBack" style="display:none">← Klassenkiste</button>
    <div class="tabs" id="tabs" aria-label="Meine Bildschirme"></div>''')
rep('$("#fsBtn").addEventListener("click", async () => {', '''if (KN) { const b = $("#knBack"); b.style.display = ""; b.addEventListener("click", () => KN.back()); }
$("#fsBtn").addEventListener("click", async () => {''')
exec(open(__file__.replace('patch.py','patch2.py'), encoding='utf-8').read())
exec(open(__file__.replace('patch.py','hintergruende.py'), encoding='utf-8').read())
exec(open(__file__.replace('patch.py','ausbau21.py'), encoding='utf-8').read())
exec(open(__file__.replace('patch.py','vorlage22.py'), encoding='utf-8').read())
exec(open(__file__.replace('patch.py','wunsch23.py'), encoding='utf-8').read())
exec(open(__file__.replace('patch.py','heft24.py'), encoding='utf-8').read())
exec(open(__file__.replace('patch.py','musik25.py'), encoding='utf-8').read())
exec(open(__file__.replace('patch.py','musik26.py'), encoding='utf-8').read())
exec(open(__file__.replace('patch.py','layout27.py'), encoding='utf-8').read())
exec(open(__file__.replace('patch.py','layout28.py'), encoding='utf-8').read())
exec(open(__file__.replace('patch.py','layout29.py'), encoding='utf-8').read())
exec(open(__file__.replace('patch.py','musik30.py'), encoding='utf-8').read())
# 19) Stil der Eulenkiste (gemeinsam mit der Eulenkiste, siehe eulenstil.py) und Schriften lokal statt von Google
import os as _os, re as _re
sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from eulenstil import eulenstil, farbkreis
eulenstil(rep)
farbkreis(rep)
rep('<link rel="preconnect" href="https://fonts.googleapis.com">\n', '')
_g = _re.findall(r'<link rel="stylesheet" href="https://fonts\.googleapis\.com/css2\?[^"]*">', s)
assert len(_g) == 1, 'Google-Schriften: ' + str(len(_g))
rep(_g[0], '<link rel="stylesheet" href="schriften/schriften.css">\n<meta name="referrer" content="no-referrer">')
open(dst, 'w', encoding='utf-8').write(s)
print('ok', len(s))
