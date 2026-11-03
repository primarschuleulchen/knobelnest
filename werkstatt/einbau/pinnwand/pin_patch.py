# Klassen-Pinnwand -> Knobelnest (pinnwand.html)
import sys
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    assert c == n, ('Anzahl %d statt %d: ' % (c, n)) + a[:90]
    s = s.replace(a, b)

# 1) Verbindung zum Knobelnest
rep('(() => {\nconst $ = (s, r = document) => r.querySelector(s);', '''(() => {
const $ = (s, r = document) => r.querySelector(s);
// Knobelnest: Speicher, Kinder und Rolle kommen aus dem Portal. Kinder sehen nie Namen.
const KN = (() => { try { return window.parent !== window && window.parent.knPin || null; } catch { return null; } })();
if (KN) window.claude = KN.claude;''')
rep('  my: { name: ls.get("pw-name", ""), r: {} },', '  my: { name: KN ? KN.name : ls.get("pw-name", ""), r: {} }, peek: "",')

# 2) Kein Namensfeld: das Knobelnest kennt den Namen
rep('  const nameBlock = !name || S.editName', '  const nameBlock = KN ? peekHTML() : !name || S.editName')
rep('i.status === "pending" && inBoard(i) && i.uid === myKey());', 'i.status === "pending" && inBoard(i) && i.uid === (S.peek || myKey()));')

# 3) Lehrperson: in der Kinder-Ansicht ein Kind wählen und sehen, wie es abgestimmt hat (nur ansehen)
rep('function myVote(id) { return (S.my.r[id] ||= {}); }', '''function myVote(id) { if (S.peek) return {}; return (S.my.r[id] ||= {}); }
function peekHTML() {
  if (!KN || !isTeacher) return "";
  const voted = new Set([...S.votes.keys()]);
  return `<div class="row peekrow"><label class="grow"><span class="sub">Ansicht von</span><select class="field" id="peekSel" data-act="peek">
    <option value="">Vorschau (ohne Kind)</option>${KN.roster.map(k => `<option value="${esc(k.id)}" ${S.peek === k.id ? "selected" : ""}>${esc(k.name)}${voted.has(k.id) ? " ✓" : ""}</option>`).join("")}</select></label></div>
    ${S.peek ? `<p class="sub peeknote">So sieht ${esc((KN.roster.find(k => k.id === S.peek) || {}).name || "")} die Pinnwand: mit den eigenen Stimmen und Kommentaren. Hier kann nichts geändert werden.</p>` : ""}`;
}
function setPeek(id) {
  S.peek = id || "";
  const k = KN.roster.find(x => x.id === S.peek), v = S.peek ? S.votes.get(S.peek) : null;
  S.my = S.peek ? { name: k ? k.name : "", r: JSON.parse(JSON.stringify((v && v.r) || {})) } : { name: KN.name, r: {} };
  document.body.classList.toggle("peeking", !!S.peek);
}''')
rep('''document.addEventListener("change", async e => {
  const el = e.target;''', '''document.addEventListener("change", async e => {
  const el = e.target;
  if (el.id === "peekSel") { setPeek(el.value); render(); return; }''')
rep('''  else if (act === "send") {''', '''  else if (act === "send" && S.peek) { toast("In der Ansicht eines Kindes kann nichts abgeschickt werden."); }
  else if (act === "send") {''')
rep('''  if (isTeacher) db.collection("votes").onSnapshot(snap => { S.votes = new Map(snap.docs.map(d => [d.id, d.data()]));''',
    '''  if (isTeacher) db.collection("votes").onSnapshot(snap => { S.votes = new Map(snap.docs.map(d => [d.id, d.data()])); if (KN && S.peek) setPeek(S.peek);''')
# Beim Wechsel der Rolle die Kind-Ansicht zurücksetzen
rep('''  if (act === "role") {''', '''  if (act === "role" && KN && S.peek) setPeek("");
  if (act === "role") {''')

# 4) Zurück ins Knobelnest
rep('''    <h1>Klassen-Pinnwand</h1>''', '''    <button class="btn ghost small" type="button" id="knBack" hidden>← Knobelnest</button>
    <h1>Klassen-Pinnwand</h1>''')
rep('/* ---------- Start ---------- */', '''if (KN) { const kb = $("#knBack"); kb.hidden = false; if (KN.mode === "kid") kb.textContent = "← Zurück"; kb.onclick = () => KN.back(); }
/* ---------- Start ---------- */''')

rep('</style>\n\n<div class="wrap">', '''/* Knobelnest */
.peekrow select{min-height:44px}
.peeknote{margin:0;color:var(--leaf-deep, #3f6b39)}
body.peeking .note .tool,body.peeking .baro .tray,body.peeking .baro .track .pin{pointer-events:none}
body.peeking #ideaIn,body.peeking [data-act="send"]{opacity:.5}
#knBack{margin-right:4px}
</style>

<div class="wrap">''')

exec(open(__file__.replace('pin_patch.py','sec5.py'), encoding='utf-8').read())
exec(open(__file__.replace('pin_patch.py','sec6.py'), encoding='utf-8').read())
exec(open(__file__.replace('pin_patch.py','sec7.py'), encoding='utf-8').read())
exec(open(__file__.replace('pin_patch.py','sec8.py'), encoding='utf-8').read())
exec(open(__file__.replace('pin_patch.py','sec9.py'), encoding='utf-8').read())
exec(open(__file__.replace('pin_patch.py','sec10.py'), encoding='utf-8').read())
exec(open(__file__.replace('pin_patch.py','sec11.py'), encoding='utf-8').read())
exec(open(__file__.replace('pin_patch.py','sec12.py'), encoding='utf-8').read())
open(dst, 'w', encoding='utf-8').write(s)
print('ok', len(s))
