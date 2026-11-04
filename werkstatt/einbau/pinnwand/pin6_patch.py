# Klassen-Pinnwand (Version 6 der Lehrerin) -> Knobelnest (pinnwand.html)
# Das Original enthält schon alle früheren Erweiterungen (Abschnitte 5–12 der alten pin_patch.py).
# Hier kommt nur noch die Anbindung ans Knobelnest dazu, plus die Korrekturen aus pin_fixes.py.
import sys, os
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    assert c == n, ('Anzahl %d statt %d: ' % (c, n)) + a[:90]
    s = s.replace(a, b)

# 1) Verbindung zum Knobelnest: Speicher, Kinder und Rolle kommen aus dem Portal. Kinder sehen nie Namen.
rep('(() => {\nconst $ = (s, r = document) => r.querySelector(s);', '''(() => {
const $ = (s, r = document) => r.querySelector(s);
const KN = (() => { try { return window.parent !== window && window.parent.knPin || null; } catch { return null; } })();
if (KN) window.claude = KN.claude;''')
rep('  my: { name: ls.get("pw-name", ""), r: {} }, peek: "",', '  my: { name: KN ? KN.name : ls.get("pw-name", ""), r: {} }, peek: "",')

# 2) Kein Namensfeld: das Knobelnest kennt den Namen. Lehrperson: Kind wählen und dessen Ansicht sehen.
rep('  const nameBlock = isTeacher ? peekHTML() : !name || S.editName', '  const nameBlock = KN ? (isTeacher ? peekHTML() : "") : isTeacher ? peekHTML() : !name || S.editName')

# 3) Kind-Ansicht mit der Klassenliste aus dem Knobelnest (statt nur der Namen aus den Stimmen)
rep('function peekHTML() {\n', '''function peekHTML() {
  if (KN) {
    const voted = new Set([...S.votes.keys()]);
    return `<div class="row peekrow"><label class="grow"><span class="sub">Ansicht von</span><select class="field" id="peekSel">
    <option value="">Vorschau (ohne Kind)</option>${KN.roster.map(k => `<option value="${esc(k.id)}" ${S.peek === k.id ? "selected" : ""}>${esc(k.name)}${voted.has(k.id) ? " ✓" : ""}</option>`).join("")}</select></label></div>
    ${S.peek ? `<p class="sub peeknote">So sieht ${esc((KN.roster.find(k => k.id === S.peek) || {}).name || "")} die Pinnwand: mit den eigenen Stimmen und Kommentaren. Hier kann nichts geändert werden.</p>` : ""}`;
  }
''')
rep('function setPeek(id) {\n', '''function setPeek(id) {
  if (KN) {
    S.peek = id || "";
    const k = KN.roster.find(x => x.id === S.peek), v = S.peek ? S.votes.get(S.peek) : null;
    S.my = S.peek ? { name: k ? k.name : "", r: JSON.parse(JSON.stringify((v && v.r) || {})) } : { name: KN.name, r: {} };
    document.body.classList.toggle("peeking", !!S.peek);
    return;
  }
''')

# 4) Zurück in die Klassenkiste
rep('''    <h1>Klassen-Pinnwand</h1>''', '''    <button class="btn ghost small" type="button" id="knBack" hidden>← Klassenkiste</button>
    <h1>Klassen-Pinnwand</h1>''')
rep('/* ---------- Start ---------- */', '''if (KN) { const kb = $("#knBack"); kb.hidden = false; if (KN.mode === "kid") kb.textContent = "← Zurück"; kb.onclick = () => KN.back(); }
/* ---------- Start ---------- */''')
rep('/* Erweiterungen */', '/* Erweiterungen */\n#knBack{margin-right:4px}')

# 5) Korrekturen (gleich wie in der Eulenkiste)
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pin_fixes.py'), encoding='utf-8').read())

open(dst, 'w', encoding='utf-8').write(s)
print('ok', len(s))
