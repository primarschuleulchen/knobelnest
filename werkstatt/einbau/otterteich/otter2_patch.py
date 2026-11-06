# Otterteich (neue Vollbild-Version) -> Knobelnest (otterteich.html)
# Aufruf: python3 otter2_patch.py <otterteich.html> <ziel/otterteich.html>
import sys
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    assert c == n, ('Anzahl %d statt %d: ' % (c, n)) + a[:90]
    s = s.replace(a, b)

# 1) Verbindung zum Knobelnest (direkt oder in der Tagesfolie eingebettet)
rep("(()=>{\n'use strict';", r"""(()=>{
'use strict';
// Knobelnest: Klassenliste, Speicher und Zurück kommen aus dem Portal (auch eingebettet in der Tagesfolie)
const KN=(()=>{try{if(window.parent===window)return null;return window.parent.knOtter||(window.parent.parent!==window.parent&&window.parent.parent.knOtter)||null}catch(e){return null}})();
const EMBED=/[?&]embed\b/.test(location.search);
if(KN) document.documentElement.classList.add('kn');
if(EMBED) document.documentElement.classList.add('embed');
let knSaveSet=()=>{};""")

# 2) Einstellungen speichern, sobald sich etwas ändert
rep("  if(!S.captions) $('caption').classList.remove('show');\n  applyAudio(); applyWake();\n}",
    "  if(!S.captions) $('caption').classList.remove('show');\n  applyAudio(); applyWake();\n  knSaveSet();\n}")
rep("$('names').addEventListener('input',e=>{S.names=e.target.value;renameAll()});",
    "$('names').addEventListener('input',e=>{S.names=e.target.value;renameAll();knSaveSet()});")

# 3) Mikrofon: wenn der Browser den Ton erst nach einem Tippen erlaubt, erscheint «Weiter»
rep("    micCtx=new AC();", "    micCtx=new AC(); if(micCtx.state==='suspended') micCtx.resume().catch(()=>{});\n    setTimeout(knCheckAudio,400);")

# 4) CSS für Knobelnest und Einbettung
rep("</style>", r"""
/* ===== Knobelnest ===== */
#knResume{position:fixed;inset:0;z-index:31;display:grid;place-items:center;background:rgba(20,60,45,.28)}
#knResume button{font:700 1.25rem var(--display);border:0;border-radius:999px;padding:16px 30px;background:#fff;color:var(--fur);box-shadow:0 6px 22px rgba(0,0,0,.25);cursor:pointer}
html.embed .clock,html.embed #fsBtn,html.embed #knBack{display:none!important}
html.embed .drawer{top:6px;right:6px;bottom:6px;width:min(400px,calc(100vw - 12px))}
html.embed .br,html.embed .count,html.embed .pausebadge{zoom:.7}
html.embed .caption{zoom:.75}
html.embed .scard{zoom:.6}
html.embed .actions{opacity:0;transition:opacity .3s}
html.embed body:hover .actions{opacity:1}
html.embed #knResume button{font-size:1rem;padding:10px 20px}
</style>""")

# 5) Start: gespeicherte Einstellungen und den letzten Stand des Teichs holen
rep("syncUI(); micUI(); selectTab('szene');", r"""syncUI(); micUI(); selectTab('szene');
// ================= Knobelnest =================
function knCheckAudio(){
  if(!KN||!micCtx||micCtx.state==='running'||$('knResume')) return;
  const ov=document.createElement('div'); ov.id='knResume'; ov.innerHTML='<button type="button">▶ Weiter mit dem Otterteich</button>';
  ov.onclick=()=>{try{micCtx&&micCtx.resume();ensureOut();actx&&actx.resume&&actx.resume()}catch(e){} ov.remove()};
  document.body.appendChild(ov);
}
if(KN){
  const q=x=>document.querySelector(x);
  // Texte: in der Klassenkiste werden Namen und Einstellungen pro Klasse gespeichert
  q('.dhead p').textContent='Wird für diese Klasse in der Klassenkiste gespeichert';
  q('.scard h1').textContent='Otterteich';
  q('.scard p').textContent='Das Mikrofon misst nur live, wie laut es im Raum ist – es wird nichts aufgenommen. Namen und Einstellungen bleiben für eure Klasse in der Klassenkiste gespeichert.';
  const fines=[...document.querySelectorAll('.scard .fine')]; if(fines[1]) fines[1].hidden=true;
  const nh=$('names').parentElement.querySelector('.hint');
  if(nh) nh.textContent='Mit Komma oder Zeilenumbruch trennen. Die Namen bleiben für diese Klasse gespeichert, auch auf anderen Geräten.';
  q('.privacy').innerHTML='<p><b>Gespeichert in der Klassenkiste.</b> Namen und Einstellungen werden für diese Klasse gespeichert, damit sie überall gleich sind – auch in der Tagesfolie.</p><p>Das Mikrofon misst nur live, wie laut es ist. Es wird nichts aufgenommen.</p>';
  const lb=$('linkBtn'), lh=lb.previousElementSibling, ls=lh&&lh.previousElementSibling;
  lb.hidden=true; $('linkOut').hidden=true; if(lh) lh.hidden=true; if(ls&&ls.classList.contains('sec')) ls.hidden=true;
  // Namen der Klasse einsetzen
  if(KN.roster&&KN.roster.length){
    const b=document.createElement('button'); b.className='btn'; b.type='button'; b.textContent='Namen der Klasse einsetzen';
    b.onclick=()=>{S.names=KN.roster.join(', ');$('names').value=S.names;renameAll();knSaveSet()};
    $('names').parentElement.appendChild(b);
  }
  // Zurück ins Knobelnest
  if(!EMBED&&KN.back){
    const b=document.createElement('button'); b.className='ab'; b.id='knBack'; b.type='button'; b.textContent='← Klassenkiste'; b.style.padding='0 14px';
    b.onclick=()=>{try{if(isFs())(document.exitFullscreen||document.webkitExitFullscreen).call(document)}catch(e){} knKeep(); KN.back()};
    $('actions').insertBefore(b,$('actions').firstChild);
  }
  const KEYS=Object.keys(DEF); let ready=false, setT=null;
  knSaveSet=()=>{ if(!ready||!KN.save) return; clearTimeout(setT); setT=setTimeout(()=>{const o={};KEYS.forEach(k=>o[k]=S[k]);KN.save(o)},800) };
  // Stand des Teichs: wird laufend gemerkt; beim Verlassen bleibt er stehen und geht beim nächsten Öffnen weiter
  const runState=()=>({n:present().length,names:present().map(o=>o.name||''),quietT:Math.round(quietT*10)/10,paused,mic:analyser?'mic':(sim?'sim':''),at:Date.now()});
  function knKeep(){ if(ready&&KN.keepRun) KN.keepRun(runState()) }
  setInterval(knKeep,1000);
  addEventListener('pagehide',knKeep);
  document.addEventListener('visibilitychange',()=>{if(document.hidden)knKeep()});
  function restoreOtter(name){
    if(!spawn()) return; const o=otters[otters.length-1];
    if(name&&nameList().includes(name)&&!otters.some(x=>x!==o&&x.name===name)) o.name=name;
    const p=randInPond(.6); o.x=p.x; o.y=p.y; o.state='swim'; o.lift=0; pickActivity(o);
  }
  (async()=>{
    let d=null; try{d=KN.load?await KN.load():null}catch(e){}
    if(d&&typeof d==='object'){ for(const k of KEYS) if(k in d && typeof d[k]===typeof DEF[k]) S[k]=d[k]; }
    if(!d||!('showNext' in d)) S.showNext=false; // nur der Balken
    if(!String(S.names||'').trim()&&KN.roster&&KN.roster.length) S.names=KN.roster.join(', ');
    $('names').value=S.names; $('pondName').value=S.pond; syncUI(); renameAll();
    const r=d&&d.run;
    if(r&&typeof r==='object'){
      const cap=S.captions; S.captions=false;
      const n=Math.max(0,Math.min(S.max,r.n|0)), nm=Array.isArray(r.names)?r.names:[];
      for(let i=0;i<n;i++) restoreOtter(nm[i]);
      S.captions=cap; reached=present().length; updUnlocks();
      quietT=Math.max(0,+r.quietT||0);
      if(r.paused){paused=true;$('pauseBadge').hidden=false;$('pauseBtn').innerHTML=ICON.play;$('pauseBtn').setAttribute('aria-label','Weiter')}
      if(r.mic==='mic') startMic(); else if(r.mic==='sim') startSim();
    }
    ready=true; if(!d) knSaveSet();
  })();
}""")

open(dst, 'w', encoding='utf-8').write(s)
print('ok', len(s))
