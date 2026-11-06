"""Rechenoperationen (Mathe, Lernziele 5.5): Übungen und Merkblätter.

Quelle: vorlage.html (eigene Spiele, Merkblätter, Rahmen) + quellen/*.html (vier Übungen der Lehrerin,
laufen je in einem Shadow DOM, angepasst durch die Abschnitte unten).

  python3 werkstatt/spiele/rechenoperationen/bauen.py                 Klassenkiste: rechenoperationen/ (6 Spiele + Spielpaket)
  python3 werkstatt/spiele/rechenoperationen/bauen.py --eulenkiste P  zusätzlich die Eulenkiste-Fassung (ohne Sterne) nach P
  python3 werkstatt/spiele/rechenoperationen/bauen.py --artifact P    zusätzlich alles auf einer Seite (mit Sternen im Browser) nach P
"""
import json, re, os, sys, base64, hashlib
H = os.path.dirname(os.path.abspath(__file__))
def lies(n): return open(os.path.join(H, n), encoding='utf-8').read()

def teile(name):
    t = lies('quellen/' + name + '.html')
    css = t.split('<style>')[2].split('</style>')[0]
    html = t.split('</style>', 2)[2].split('<script>')[0].strip()
    js = t.split('<script>')[1].split('</script>')[0]
    return css, html, js

def css_um(css):
    css = re.sub(r'@media \(prefers-color-scheme:dark\)\{:root:not\(\[data-theme="light"\]\)[^{]*\{[^}]*\}\}', '', css)
    css = re.sub(r':root\[data-theme="dark"\][^{]*\{[^}]*\}', '', css)
    css = css.replace(':root', ':host').replace('body{', '.app{')
    return css

PRE = {
 'durch': [
  ("""    el.addEventListener('input', () => {
      el.value = el.value.replace(/\\D/g,'').slice(-1);
      el.classList.remove('bad');
      const f = S.F[S.fi]; if(!f) return;
      const k = f.ids.indexOf(el.id);
      if(el.value!=='' && k>0) document.getElementById(f.ids[k-1]).focus();
    });
    el.addEventListener('keydown', e => {
      const f = S.F[S.fi]; const k = f ? f.ids.indexOf(el.id) : -1;
      if(e.key==='Enter'){ e.preventDefault(); sNext(); }
      else if(k<0) return;
      else if(e.key==='Backspace' && el.value==='' && k<f.ids.length-1){ e.preventDefault(); const nx = document.getElementById(f.ids[k+1]); nx.value=''; nx.focus(); }
      else if(e.key==='ArrowLeft' && k>0){ e.preventDefault(); document.getElementById(f.ids[k-1]).focus(); }
      else if(e.key==='ArrowRight' && k<f.ids.length-1){ e.preventDefault(); document.getElementById(f.ids[k+1]).focus(); }
    });""",
   """    // Zahlen wie gewohnt eintippen: die Ziffern rutschen von rechts nach links (wie beim Taschenrechner)
    el.addEventListener('beforeinput', e => {
      const f = S.F[S.fi]; if(!f || !f.ids.includes(el.id)) return;
      const cur = () => f.ids.map(id => document.getElementById(id).value).join('');
      const fill = s => f.ids.forEach((id,c) => { const x = document.getElementById(id), k = c - (f.ids.length - s.length); x.value = k>=0 ? s[k] : ''; x.classList.remove('bad'); });
      const t = e.inputType || '';
      if(t.indexOf('insert')===0){
        e.preventDefault();
        const d = String(e.data||'').replace(/\\D/g,''); if(!d) return;
        let s = cur() + d; if(s.length > f.ids.length) s = s.slice(-f.ids.length);
        fill(s); document.getElementById(f.ids[f.ids.length-1]).focus();
      } else if(t.indexOf('delete')===0){ e.preventDefault(); fill(cur().slice(0,-1)); }
    });
    el.addEventListener('input', () => { el.value = el.value.replace(/\\D/g,'').slice(-1); el.classList.remove('bad'); });
    el.addEventListener('keydown', e => { if(e.key==='Enter'){ e.preventDefault(); sNext(); } });"""),
 ],
 'mal': [
  ("  b.onclick = kStep; btns.appendChild(b);\n", """  b.onclick = kStep; btns.appendChild(b);
  const tb = document.createElement('button'); tb.className='btn'; tb.id='k-tip'; tb.textContent='Tipp';
  tb.onclick = () => { const ca = core(t.a), cb = core(t.b), z = zerosOf(t.a)+zerosOf(t.b);
    setMsg($('#k-msg'), `Lass zuerst alle Nullen weg und rechne ${ca} · ${cb}. Dann hängst du ${nullen(z)} an.` + ((ca*cb)%10===0 ? ` Achtung: ${ca} · ${cb} gibt selbst schon eine Null, die bleibt auch stehen.` : ''), 'info'); $('#k-in').focus(); };
  btns.appendChild(tb);
"""),
  ("  K.results[K.i] = ok; K.answered = true;\n", "  K.results[K.i] = ok; K.answered = true; $('#k-tip')?.remove();\n"),
 ],
 'flex': [
  ("""const ORDER = ['t2','t4','t5','t1','t3'];
TRICKS.sort((a,b) => ORDER.indexOf(a.key) - ORDER.indexOf(b.key));
const META = { t2:['Trick 1','w1'], t4:['Trick 2','w2'], t5:['Trick 3','w4'], t1:['Gesetz 1','w3'], t3:['Gesetz 2','w3'] };""",
   """// Mal und Durch zusammengelegt: 5/50/500 und Verteilungsgesetz, Rechenart wählbar
const BY = k => TRICKS.find(t => t.key===k);
function merge(key, title, subs, extra){
  const o = Object.assign({ key, title, op:0, lv:1, sel:0, ops:[['mal','Mal'],['durch','Durch']], subs,
    preview: subs.mal.preview, blurb: subs.mal.blurb, merke: subs.mal.merke,
    sub(op){ const s = this.subs[op]; s.lv = this.lv; s.sel = this.sel; return s; },
    rand(){ const op = this.op || pick(['mal','durch']); return Object.assign({_op:op}, this.sub(op).rand()); },
    steps(x){ const s = this.sub(x._op); this.merke = s.merke; this.align = s.align; return s.steps(x); },
    practice(){ return this.sub(this.op || pick(['mal','durch'])).practice(); }
  }, extra);
  Object.defineProperty(o, 'ex', { get(){ const op = this.op || 'mal'; return Object.assign({_op:op}, this.subs[op].ex); } });
  return o;
}
const T2 = BY('t2');
const T45 = merge('t45', 'Trick mit 5 / 50 / 500', {mal:BY('t4'), durch:BY('t5')}, {choices:[5,50,500]});
const TV = merge('tv', 'Verteilungsgesetz', {mal:BY('t1'), durch:BY('t3')}, {});
TRICKS.length = 0; TRICKS.push(T2, T45, TV);
const META = { t2:['Trick 1','w1'], t45:['Trick 2','w2'], tv:['Gesetz','w3'] };"""),
  ("""  $('#v-lv').innerHTML = [[1,'Leicht'],[2,'Mittel'],[3,'Schwer']].map(([v,l]) => `<button data-v="${v}" aria-pressed="${t.lv===v}">${l}</button>`).join('');
""", """  $('#v-lv').innerHTML = [[1,'Leicht'],[2,'Mittel'],[3,'Schwer']].map(([v,l]) => `<button data-v="${v}" aria-pressed="${t.lv===v}">${l}</button>`).join('');
  $('#v-opg').hidden = !t.ops;
  if(t.ops) $('#v-op').innerHTML = [...t.ops, [0,'Gemischt']].map(([v,l]) => `<button data-v="${v}" aria-pressed="${t.op===v}">${l}</button>`).join('');
"""),
  ("// ---------- Navigation ----------", """$('#v-op').addEventListener('click', e => {
  const b = e.target.closest('button'); if(!b) return;
  const t = V.t; t.op = b.dataset.v==='0' ? 0 : b.dataset.v;
  renderChoose(t); V.steps = t.steps(t.rand()); V.i = 0; renderStep(); newPractice();
});
// ---------- Navigation ----------"""),
 ],
}
STERNE = {
 'werkstatt': [("  if(!S.solved){ S.solved = true; S.score++;", "  if(!S.solved){ SOLVED('strich-' + S.diff); S.solved = true; S.score++;"),
               ("    if(!W.solved && !W.shown){ W.solved = true; W.score++;", "    if(!W.solved && !W.shown){ SOLVED('schrift-' + W.len); W.solved = true; W.score++;")],
 'mal': [("    if(!W.solved && !W.shown){ W.solved = true; W.score++;", "    if(!W.solved && !W.shown){ SOLVED('schrift-' + W.len); W.solved = true; W.score++;")],
 'durch': [("    S.score++; $('#s-score')", "    SOLVED('schrift-' + S.lv); S.score++; $('#s-score')")],
 'flex': [("    if(!P.solved){ P.score++; P.solved = true;", "    if(!P.solved){ SOLVED(V.t.key + '-' + V.t.lv); P.score++; P.solved = true;")],
}
KOPF_ENDE = ("    const n = K.results.filter(Boolean).length;\n    body.innerHTML = `<div class=\"task\">${n} von 10 richtig</div>`;",
             "    const n = K.results.filter(Boolean).length;\n    body.innerHTML = `<div class=\"task\">${n} von 10 richtig</div>` + STAR('kopf-' + K.lv, n>=9 ? 3 : n>=6 ? 2 : 1);")
def js_um(js, name):
    for a, b in STERNE.get(name, []) + ([KOPF_ENDE] if name in ('werkstatt', 'mal', 'durch') else []):
        assert js.count(a) == 1, (name, a[:60])
        js = js.replace(a, b)
    for a, b in PRE.get(name, []):
        assert js.count(a) == 1, (name, a[:60])
        js = js.replace(a, b)
    if name in ('werkstatt', 'mal', 'durch'):  # jede Kopfrechen-Antwort ans Portal melden
        a = 'K.results[K.i] = ok; K.answered = true;'
        assert js.count(a) == 1, (name, a)
        js = js.replace(a, a + ' ANS(ok);')
    def rep(a, b, n=None):
        nonlocal js
        c = js.count(a)
        assert c and (n is None or c == n), (name, c, a)
        js = js.replace(a, b)
    for a in ['document.querySelectorAll', 'document.querySelector', 'document.getElementById', 'document.activeElement']:
        if a in js: js = js.replace(a, 'KR.' + a.split('.', 1)[1])
    js = re.sub(r"\n\s*if\(location\.hash\.slice\(1\)!==id\) location\.hash = id==='home' \? '' : id;( else show\(id\);)?", '', js)
    js = re.sub(r"\nwindow\.addEventListener\('hashchange'[^\n]*", '', js)
    js = re.sub(r"\nshow\(location\.hash\.slice\(1\) \|\| 'home'\);", '', js)
    if name == 'flex':
        rep("""function go(id){
  const h = id==='home' ? '' : id;
  if(location.hash.slice(1) !== h){ location.hash = h; } else show(id);
}""", "function go(id){ if(id==='home'){ EXIT(); return; } show(id); }")
        rep("document.addEventListener('keydown'", "KR.addEventListener('keydown'")
        rep("document.addEventListener('click'", "KR.addEventListener('click'")
    if name == 'durch':
        # zusätzliche Stufen: mit Rest, dreistelliger Divisor (erweiterte Anforderung)
        rep("const S = { lv:'1', score:0, firsts:{'1':[846,3],'R':[847,3],'2':[966,23]} };",
            "const S = { lv:'1', score:0, firsts:{'1':[846,3],'R':[847,3],'2':[966,23],'3':[79500,150]} };")
        rep("    else { do{ d = rnd(12,48); }while(d%10===0 || d%11===0); a = d * rnd(12,349); }",
            "    else if(lv==='3'){ d = Math.random()<.4 ? pick([125,150,240,250]) : rnd(101,399); a = d * rnd(21,249) + (Math.random()<.5 ? rnd(1,d-1) : 0); }\n"
            "    else { do{ d = rnd(12,48); }while(d%10===0 || d%11===0); a = d * rnd(12,349); }")
        rep("$('#s-note').textContent = S.lv==='2'", "$('#s-note').textContent = (S.lv==='2' || S.lv==='3')")
    assert 'location.hash' not in js, name
    assert 'document.addEventListener' not in js.replace("document.addEventListener('fullscreenchange'", ''), name
    return 'function (KR, EXIT, STAR, SOLVED, ANS) {\n' + js + '\nreturn show;\n}'

def html_um(html, name):
    if name == 'durch':
        a = '<button data-v="1" aria-pressed="true">Durch 1-stellig</button><button data-v="2">Durch 2-stellig</button>'
        assert html.count(a) == 1
        html = html.replace(a, '<button data-v="1" aria-pressed="true">Durch 1-stellig</button><button data-v="R">Mit Rest</button>'
                               '<button data-v="2">Durch 2-stellig</button><button data-v="3">Durch 3-stellig</button>')
    if name == 'durch':
        a = 'Mehrstellige Zahlen von rechts nach links tippen'
        assert html.count(a) == 1
        html = html.replace(a, 'Zahlen ganz normal eintippen')
    if name == 'flex':
        a = '<span class="cgroup" id="v-choose" hidden>'
        assert html.count(a) == 1
        html = html.replace(a, '<span class="cgroup" id="v-opg" hidden><span class="kicker">Rechenart</span><span class="seg" id="v-op"></span></span>' + a)
    return html

# Stil der Eulenkiste über die Übungen legen
EULE_CSS = """
:host{display:block;--ink:#1f2421;--ink-soft:#5f6963;--pen:#3f78a8;--green:#5f9a4a;--red:#c8574e;--mark:#ffdf5e;
  --wash1:#fbf3dc;--wash2:#e4f2fd;--wash3:#e9f1e3;--wash4:#efe7f7;--card:#fff;--line:#c5d8e8;--paper:#fbfdff;--paper2:#fbfdff;
  --sky1:transparent;--sky2:transparent;--bg:transparent;--bg2:transparent;--tile:#fff;--tile1:#fbf3dc;--tile2:#e9f1e3;
  --pe:#2f8f3a;--pz:#1d63c4;--ph:#9a3fc9;--we:#e3f4e1;--wz:#e2edfb;--wh:#f3e6fb;--c1:#3f78a8;--c2:#5f9a4a;
  --display:"Patrick Hand","Segoe Print","Comic Sans MS",cursive;--body:var(--display);--title:var(--display)}
[hidden]{display:none!important}
.app{background:none!important;font-family:var(--display);font-size:20px;line-height:1.35;color:var(--ink);min-height:0!important}
.wrap{max-width:none!important;padding:0!important}
h1,h2,h3,.task,.ptask,.board,.prow,.preview,.preview .big,.tile h3,.say .nr,.step .nr,.merke b.t,.dgrid .op,.dgrid .mi,.wgrid .opc,.row .op,.tag,.btn.you{font-weight:400!important}
h2{font-size:clamp(30px,5.4vw,40px)}
h2::after{content:" ✦";color:#d6ad45;font-size:.5em;vertical-align:super}
.back{all:unset;box-sizing:border-box;cursor:pointer;display:inline-flex!important;align-items:center;gap:8px;background:#fff;border:2px solid var(--ink);border-radius:999px;
  padding:3px 16px 3px 6px;box-shadow:0 4px 12px rgba(63,120,168,.14);font-size:22px;min-height:46px;margin-bottom:16px;color:var(--ink)!important}
.back img{width:36px;height:36px;border-radius:50%;object-fit:cover}
.sheet{border:1.5px solid #e1edf7!important;border-radius:28px!important;box-shadow:0 10px 26px rgba(63,120,168,.18),0 2px 6px rgba(63,120,168,.10)!important;background:#fff}
.btn{border-radius:14px!important;border:2px solid var(--ink)!important;background:#fff!important;color:var(--ink)!important;box-shadow:0 4px 12px rgba(63,120,168,.14);font-weight:400!important;font-size:21px;padding:6px 18px!important}
.btn.primary{background:#dcf0fd!important}
.btn.you{background:#fbf3dc!important;border-color:#d6ad45!important;color:var(--ink)!important}
.btn.ghost{border-color:var(--line)!important}
.seg{border:2px solid var(--ink);border-radius:14px}
.seg button{font-weight:400!important;font-size:18px!important}
.seg button[aria-pressed="true"]{background:#fbf3dc!important;color:var(--ink)!important;box-shadow:inset 0 -3px 0 #d6ad45}
.bar label,.kicker,.choose .kicker{font-weight:400!important;font-size:15px!important;color:var(--ink-soft)}
.score,.pill{font-weight:400!important;border-color:#efdca6!important;background:#fbf3dc!important;color:#a87c1f}
.msg{font-weight:400!important;font-size:20px;border-radius:16px}
.note,.lead{font-size:17px}
.dot{border-color:#c5d8e8}
.dot.now{border-color:#d6ad45!important;background:#fbf3dc!important}
.dot.ok{background:#5f9a4a!important;border-color:#5f9a4a!important}
.dot.bad{background:#d6ad45!important;border-color:#d6ad45!important}
.say{background:#fbf3dc;border:1.5px solid #efdca6}
.say .nr,.step .nr{background:#d6ad45!important;color:#fff!important}
.step{font-weight:400!important;background:#fbf3dc!important;border:1.5px solid #efdca6}
.step.done{background:#e9f1e3!important;border-color:#cfe1c4}
.merke{border-color:#d6ad45!important;background:#fffaf0!important}
.merke b.t{color:#a87c1f!important}
input.cell,input.field,input.cc{font-family:var(--display)!important;font-weight:400!important}
input:focus{border-color:#d6ad45!important;box-shadow:0 0 0 4px #fbf3dc!important}
.res{color:#a87c1f!important;border-bottom-color:#d6ad45!important}
.board .hot{background:#fbf3dc!important}
.legend{font-size:15px}
/* Schriftlich: kariertes Heftblatt wie auf den Merkblättern */
.written{overflow-x:auto;padding:6px 0 10px}
.dgrid,.wgrid{--k:2.7rem;background-color:#fff;background-image:linear-gradient(#d9e7f5 1px,transparent 1px),linear-gradient(90deg,#d9e7f5 1px,transparent 1px);
  background-size:var(--k) var(--k);padding:var(--k);border-radius:20px;border:1.5px solid #d9e7f5;font-size:1.8rem!important;box-shadow:inset 0 0 0 6px #fff}
.dgrid{grid-auto-rows:var(--k)!important}
.dgrid > div,.wgrid > div{width:var(--k)!important;height:var(--k)!important;padding:0!important}
.dgrid .ex,.wgrid .ex{font-weight:400!important}
.dgrid .op,.wgrid .opc{color:#5f6963}
.dgrid input.cell,.wgrid input.cell{width:calc(var(--k) - 8px)!important;height:calc(var(--k) - 8px)!important;font-size:1.7rem!important;background:rgba(255,255,255,.7)!important;
  border:2px dashed #b4cde4!important;border-radius:10px!important;box-shadow:none!important}
.dgrid input.cell[readonly]{border-color:transparent!important;background:transparent!important}
.dgrid input.tq{color:#2f8f3a!important}.dgrid input.tp{color:#1d63c4!important}.dgrid input.td{color:#9a3fc9!important}.dgrid input.tr{color:#d0453a!important}
.dgrid input.cell.tq:not([readonly]){background:#e3f4e1!important;border-color:#7cc27f!important}.dgrid input.cell.tp:not([readonly]){background:#e2edfb!important;border-color:#7ea6e3!important}.dgrid input.cell.td:not([readonly]){background:#f3e6fb!important;border-color:#c18fe0!important}
.dgrid input.cell.cur.cur:not([readonly]){border:3px solid #e07a2e!important;box-shadow:0 0 0 4px #fde3cc!important}
.dgrid input.cell.bad,.wgrid input.cell.bad,.wgrid input.cc.bad{border:2.5px solid #c8574e!important;background:#fcefed!important}
.dgrid input.cell.shown,.wgrid input.shown{color:#a87c1f!important}
.dgrid .hl,.dgrid input.cell.hl,.wgrid .now{background:#ffdf5e!important;border-radius:9px}
.dgrid .ul,.wgrid .carry{border-bottom:2.5px solid #1f2421!important}
.dgrid .mi{color:#1d63c4!important}
.wgrid .p0,.wgrid input.t0{color:#2f8f3a!important}.wgrid .p1,.wgrid input.t1{color:#1d63c4!important}.wgrid .p2,.wgrid input.t2{color:#9a3fc9!important}
.sw{width:1em!important;height:1em!important}
.dgrid .rlab{color:#c8574e!important;font-weight:400!important}
.wgrid input.cc{width:1.5rem!important;height:1.5rem!important;font-size:1rem!important;border:1.5px dashed #e3b1aa!important;background:transparent!important;color:#c8574e!important}
.wgrid input.cell.ok,.wgrid input.cc.ok{border-style:solid!important;border-color:#a8cc98!important;background:#f3f8ef!important}
.wgrid input.cell:focus,.dgrid input.cell:focus{border-style:solid!important}
.wgrid .head{font-size:.75rem!important;color:#a87c1f}
.tag{transform:scale(.85)}
/* Tipp hinter der Glühbirne, Merkblatt-Knopf */
.note{display:none!important}
section{position:relative}
.sheet{position:relative}
.birne{position:absolute;top:-18px;right:18px;z-index:3;display:inline-flex;align-items:center;gap:4px;background:#fff;border:2px solid #d6ad45;border-radius:999px;padding:3px 12px 3px 6px;
  font:inherit;font-size:17px;color:#a87c1f;cursor:pointer;box-shadow:0 4px 12px rgba(63,120,168,.16)}
.birne[aria-expanded="true"]{background:#fff6cf}
.birnbox{background:#fffbea;border:2px solid #f0d97a;border-radius:18px;padding:10px 16px;margin:4px 0 14px;font-size:18px;line-height:1.35}
.birnbox p{margin:0 0 6px}
.birnbox .mbl{all:unset;cursor:pointer;color:#1d63c4;text-decoration:underline}
.theo{all:unset;box-sizing:border-box;cursor:pointer;display:inline-flex;align-items:center;gap:6px;margin:0 0 16px 10px;background:#fff;border:2px solid #d6ad45;border-radius:999px;
  padding:3px 16px;min-height:46px;font-size:20px;color:#a87c1f;box-shadow:0 4px 12px rgba(63,120,168,.14);vertical-align:top}
#k-tip::before,#s-tip::before{content:"";display:inline-block;width:20px;height:20px;margin-right:6px;vertical-align:-3px;background:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M9 18h6M10 21h4M12 3a6 6 0 0 0-3.6 10.8c.7.6 1.1 1.3 1.1 2.2h5c0-.9.4-1.6 1.1-2.2A6 6 0 0 0 12 3z' fill='%23fbe7a1' stroke='%23a87c1f' stroke-width='1.6' stroke-linejoin='round'/%3E%3C/svg%3E") center/contain no-repeat}
@media (max-width:480px){.dgrid,.wgrid{--k:2.2rem;font-size:1.4rem!important}.dgrid input.cell,.wgrid input.cell{font-size:1.35rem!important}}
"""

css, html, js = {}, {}, {}
for n in ['werkstatt', 'mal', 'durch', 'flex']:
    c, h, j = teile(n)
    css[n], html[n], js[n] = css_um(c), html_um(h, n), js_um(j, n)

apps = ('var APP_CSS = ' + json.dumps(css, ensure_ascii=False) + ';\nvar APP_HTML = ' + json.dumps(html, ensure_ascii=False) +
        ';\nvar APP_EULE = ' + json.dumps(EULE_CSS, ensure_ascii=False) + ';\nvar APPS = {\n' +
        ',\n'.join(json.dumps(n) + ': ' + js[n] for n in js) + '\n};')
apps = apps.replace('</script', '<\\/script')
REPO = os.path.normpath(os.path.join(H, '..', '..', '..'))
FONT = base64.b64encode(open(os.path.join(REPO, 'schriften', 'patrick-hand.woff2'), 'rb').read()).decode()
EULE = base64.b64encode(open(os.path.join(REPO, 'bilder', 'eule.webp'), 'rb').read()).decode()
V = lies('vorlage.html').replace('__APPS__', apps)

def ganz(modus):
    """Alles in einer Datei (Schrift und Eule eingebettet)."""
    s = V.replace('__FONT__', FONT).replace('__EULE__', EULE)
    s = s.replace("<script>\n'use strict';", '<script>\nwindow.RK_MODUS = ' + json.dumps(modus) + ";\n'use strict';", 1)
    return s

def kopf(titel, rest):
    return ('<!doctype html>\n<html lang="de-CH">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            '<title>' + titel + '</title>\n' + rest + '</head>\n<body>\n')

# ---- Klassenkiste: gemeinsames stil.css und spiel.js, pro Bereich eine kleine Seite
stil = V.split('<style>', 1)[1].split('</style>', 1)[0].replace('__FONT__', FONT)
skript = V.split('<script>', 1)[1].rsplit('</script>', 1)[0].replace("'data:image/webp;base64,__EULE__'", "'../bilder/eule.webp'")
assert '__EULE__' not in skript and '__FONT__' not in stil
ZIEL = os.path.join(REPO, 'rechenoperationen')
os.makedirs(ZIEL, exist_ok=True)
open(os.path.join(ZIEL, 'stil.css'), 'w', encoding='utf-8').write(stil)
open(os.path.join(ZIEL, 'spiel.js'), 'w', encoding='utf-8').write(skript)
VER = hashlib.sha1((stil + skript).encode()).hexdigest()[:10]

# Datei, Bereich (id in BEREICHE), Titel, Beschreibung, Sterne
SEITEN = [
    ('im-kopf', 'kopf', 'Im Kopf', 'Runde Zahlen und Nullen schnell im Kopf rechnen.', 'eigene'),
    ('halbschriftlich', 'halb', 'Halbschriftlich', 'In Teilschritten rechnen: Rechenstrich und Teilprodukte.', 'eigene'),
    ('schriftlich', 'schrift', 'Schriftlich', 'Untereinander rechnen: Plus, Minus, Mal und Durch.', 'eigene'),
    ('flexibel-rechnen', 'flex', 'Flexibel rechnen', 'Rechentricks und Verteilungsgesetze mit Erklärung.', 'eigene'),
    ('fachwoerter', 'woerter', 'Fachwörter', 'Summand, Produkt, Quotient, Quersumme.', 'eigene'),
    ('merkblaetter', 'merk', 'Merkblätter', 'Theorie: So rechnest du, mit Beispielen zum Aufdecken.', 'aus'),
]
paket = []
for nr, (datei, bid, titel, text, sterne) in enumerate(SEITEN):
    seite = kopf('Rechenoperationen · ' + titel, '<link rel="stylesheet" href="stil.css?v=' + VER + '">\n') + \
        '<div id="app"></div>\n<script>window.RK_MODUS = ' + json.dumps({'ziel': 'klassenkiste', 'bereich': bid}) + ';</script>\n' + \
        '<script src="spiel.js?v=' + VER + '"></script>\n</body>\n</html>\n'
    open(os.path.join(ZIEL, datei + '.html'), 'w', encoding='utf-8').write(seite)
    meta = json.dumps({'modus': sterne}).replace('"', '&quot;')
    paket.append({'title': titel, 'description': text, 'fach': 'Mathematik', 'thema': 'Rechenoperationen', 'stufe': '5. Klasse', 'sort': nr + 1,
                  'html': '<!doctype html><html lang="de-CH"><head><meta charset="utf-8">'
                          '<meta name="knobelnest-url" content="rechenoperationen/' + datei + '.html">'
                          '<meta name="knobelnest-sterne" content="' + meta + '"><title>' + titel + '</title></head>'
                          '<body><p>' + titel + ': Dieses Spiel liegt in der Klassenkiste im Ordner rechenoperationen/.</p></body></html>'})
open(os.path.join(ZIEL, 'rechenoperationen-spielpaket.json'), 'w', encoding='utf-8').write(
    json.dumps({'format': 'knobelnest-spielpaket', 'games': paket}, ensure_ascii=False, indent=1) + '\n')
print('Klassenkiste: rechenoperationen/ (' + str(len(SEITEN)) + ' Spiele, Version ' + VER + ')')

def arg(n):
    return sys.argv[sys.argv.index(n) + 1] if n in sys.argv else None
if arg('--eulenkiste'):
    eu = ganz({'ziel': 'eulenkiste'}).replace('<title>Rechenoperationen 5.5</title>', '', 1)
    eu = kopf('Rechenoperationen', '<meta name="referrer" content="no-referrer">\n<link rel="icon" type="image/png" href="../eulenkiste-icon.png?v=2">\n') + eu + '\n</body>\n</html>\n'
    open(arg('--eulenkiste'), 'w', encoding='utf-8').write(eu)
    print('Eulenkiste:', arg('--eulenkiste'))
if arg('--artifact'):
    open(arg('--artifact'), 'w', encoding='utf-8').write(ganz({'ziel': 'artifact'}))
    print('Artifact:', arg('--artifact'))
