# Klassen-Pinnwand eigenständig: alle Verbesserungen aus dem Knobelnest ohne Knobelnest-Anbindung
import sys, os
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
MAP = {
  '#knBack{margin-right:4px}': '/* Erweiterungen */',
  '  my: { name: KN ? KN.name': '  my: { name: ls.get("pw-name", "")',
}
def rep(a, b, n=1):
    global s
    if a in MAP: b = b.replace(a, MAP[a], 1); a = MAP[a]
    c = s.count(a)
    assert c == n, ('Anzahl %d statt %d: ' % (c, n)) + a[:90]
    s = s.replace(a, b)
s = s.replace('</style>\n\n<div class="wrap">', '/* Erweiterungen */\n</style>\n\n<div class="wrap">', 1)

# Kinder-Ansicht der Lehrperson: ein Kind wählen und seine Stimmen ansehen (Namen aus den Stimmen)
rep('  my: { name: ls.get("pw-name", ""), r: {} },', '  my: { name: ls.get("pw-name", ""), r: {} }, peek: "",')
rep('  const nameBlock = !name || S.editName', '  const nameBlock = isTeacher ? peekHTML() : !name || S.editName')
rep('i.status === "pending" && inBoard(i) && i.uid === myKey());', 'i.status === "pending" && inBoard(i) && i.uid === (S.peek || myKey()));')
rep('function myVote(id) { return (S.my.r[id] ||= {}); }', '''function myVote(id) { if (S.peek) return {}; return (S.my.r[id] ||= {}); }
let ownMy = null;
function peekHTML() {
  const kids = [...S.votes].filter(([vid]) => vid !== myKey()).map(([vid, v]) => ({ id: vid, name: (v && v.name) || "Ohne Namen" })).sort((a, b) => a.name.localeCompare(b.name, "de"));
  return `<div class="row peekrow"><label class="grow"><span class="sub">Ansicht von</span><select class="field" id="peekSel">
    <option value="">Meine eigene Ansicht</option>${kids.map(k => `<option value="${esc(k.id)}" ${S.peek === k.id ? "selected" : ""}>${esc(k.name)}</option>`).join("")}</select></label></div>
    ${S.peek ? `<p class="sub peeknote">So sieht ${esc((kids.find(k => k.id === S.peek) || {}).name || "")} die Pinnwand: mit den eigenen Stimmen und Kommentaren. Hier kann nichts geändert werden.</p>` : ""}`;
}
function setPeek(id) {
  if (!S.peek && id) ownMy = S.my;
  S.peek = id || "";
  const v = S.peek ? S.votes.get(S.peek) : null;
  S.my = S.peek ? { name: (v && v.name) || "", r: JSON.parse(JSON.stringify((v && v.r) || {})) } : (ownMy || S.my);
  if (!S.peek) ownMy = null;
  document.body.classList.toggle("peeking", !!S.peek);
}''')
rep('''document.addEventListener("change", async e => {
  const el = e.target;''', '''document.addEventListener("change", async e => {
  const el = e.target;
  if (el.id === "peekSel") { setPeek(el.value); render(); return; }''')
rep('''  else if (act === "send") {''', '''  else if (act === "send" && S.peek) { toast("In der Ansicht eines Kindes kann nichts abgeschickt werden."); }
  else if (act === "send") {''')
rep('''  if (isTeacher) db.collection("votes").onSnapshot(snap => { S.votes = new Map(snap.docs.map(d => [d.id, d.data()]));''',
    '''  if (isTeacher) db.collection("votes").onSnapshot(snap => { S.votes = new Map(snap.docs.map(d => [d.id, d.data()])); if (S.peek) setPeek(S.peek);''')
rep('''  if (act === "role") {''', '''  if (act === "role" && S.peek) setPeek("");
  if (act === "role") {''')
rep('/* Erweiterungen */', '''/* Erweiterungen */
.peekrow select{min-height:44px}
.peeknote{margin:0;color:var(--leaf-deep, #3f6b39)}
body.peeking .note .tool,body.peeking .baro .tray,body.peeking .baro .track .pin{pointer-events:none}
body.peeking #ideaIn,body.peeking [data-act="send"]{opacity:.5}''')
# Zeilenumbruch erhalten: die Erweiterungen setzen ihren CSS-Text vor diesen Anker
here = os.path.dirname(os.path.abspath(__file__))
for sec in ('sec5.py', 'sec6.py', 'sec7.py', 'sec8.py', 'sec9.py', 'sec10.py', 'sec11.py', 'sec12.py'):
    exec(open(os.path.join(here, sec), encoding='utf-8').read())
s = s.replace('/* Erweiterungen */', '/* Erweiterungen */', 1)
# Kinder-Ansicht der Lehrperson: eigene Stimmen bleiben unberührt, solange ein Kind angeschaut wird
rep('function touchMy(delay = 600) {\n', 'function touchMy(delay = 600) {\n  if (S.peek) return;\n')
rep('const all = new Map(S.votes); all.set(myKey(), S.my);', 'const all = new Map(S.votes); all.set(myKey(), S.peek ? (ownMy || { r: {} }) : S.my);')
rep('const v = S.votes.get(b.dataset.uid), txt =', 'const v = b.dataset.uid === myKey() ? (S.peek ? ownMy : S.my) : S.votes.get(b.dataset.uid), txt =')
rep('S.ideas = new Map(snap.docs.map(d => [d.id, d.data()]));', 'S.ideas = new Map(snap.docs.map(d => [d.id, JSON.parse(JSON.stringify(d.data()))]));')
rep('    if (data) { S.my = { name: data.name || S.my.name, r: data.r || {} };', '    if (data && S.peek) { ownMy = { name: data.name || (ownMy && ownMy.name) || "", r: data.r || {} }; render(); return; }\n    if (data) { S.my = { name: data.name || S.my.name, r: data.r || {} };')
# Vorlagen und Darstellungen
exec(open(os.path.join(here, 'vorlagen.py'), encoding='utf-8').read())
exec(open(os.path.join(here, 'vorlagen2.py'), encoding='utf-8').read())
exec(open(os.path.join(here, 'vorlagen3.py'), encoding='utf-8').read())
open(dst, 'w', encoding='utf-8').write(s)
print('ok', len(s))
