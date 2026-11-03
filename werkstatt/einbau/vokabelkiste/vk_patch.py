# Vokabelkiste (Artifact aus claude.ai) -> Knobelnest (vokabelkiste/index.html)
# Aufruf: python3 vk_patch.py <vokabelkiste.html> <ziel/vokabelkiste/index.html>
#
# Im Knobelnest läuft die Vokabelkiste wie ein Spiel (wie die Zeitreise): Die Spiel-Datei in der Verwaltung
# zeigt auf diese Seite. Das Portal schickt beim Start {store, settings, teacher, edit}:
#   settings.content = Wortlisten und Freigaben der Klasse (game_settings), sonst die eingebauten Listen
#   store.p          = Fortschritt des Kindes (Karteikasten, Knacknüsse, Übungstage), gespeichert mit kid_save
# Die Seite meldet: 'answer' (richtig/falsch), 'level' (Sprache), 'store' (Fortschritt), 'vkContent' (Lehrperson speichert).
import sys
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    assert c == n, ('Anzahl %d statt %d: ' % (c, n)) + a[:90]
    s = s.replace(a, b)

# 1) Die App startet erst, wenn das Knobelnest geantwortet hat (oder sofort, wenn die Seite allein offen ist)
rep("<script id=\"vk-app\">\n(function(){\n'use strict';", "<script id=\"vk-app\">\nwindow.__vkMain=function(KNI){\n'use strict';")
rep("\n})();\n</script>", r"""
};
</script>
<script>
// Knobelnest: zuerst «hallo» sagen und auf Wortlisten und Fortschritt warten
(function(){
  var started=false; function go(i){ if(started) return; started=true; window.__vkMain(i||null); }
  if(window.parent===window){ go(null); return; }
  addEventListener('message',function(e){ if(e.source!==parent||!e.data||!e.data.knobelnestInit) return; go(e.data.knobelnestInit); });
  try{ parent.postMessage({knobelnest:1,type:'hello'},'*'); }catch(e){}
  setTimeout(function(){ go(null); },5000);
})();
</script>""")

# 2) Wortlisten der Klasse aus dem Knobelnest (sonst die eingebauten)
rep("let EMBED=null;try{EMBED=JSON.parse($('#vk-content').textContent)}catch(e){}",
    "let EMBED=null;try{EMBED=JSON.parse($('#vk-content').textContent)}catch(e){}\n"
    "const KN=!!KNI;\n"
    "if(KN&&KNI.settings&&KNI.settings.content&&Array.isArray(KNI.settings.content.subjects))EMBED=KNI.settings.content;")
rep("const EMBED_JSON=JSON.stringify(EMBED),EMBED_HASH=hashStr(EMBED_JSON);",
    "let EMBED_JSON=JSON.stringify(EMBED),EMBED_HASH=hashStr(EMBED_JSON);")

# 3) Fortschritt des Kindes im Knobelnest speichern (statt nur auf dem Gerät)
rep("const P=lsGet(PKEY)||{};", "const P=(KN?(KNI.store&&KNI.store.p):lsGet(PKEY))||{};")
rep("const saveP=()=>lsSet(PKEY,P);", r"""const knSend=m=>{if(!KN)return;try{m.knobelnest=1;parent.postMessage(m,'*')}catch(e){}};
const saveP=()=>{if(!KN)return lsSet(PKEY,P);knSend({type:'store',data:{p:P}})};
/* Knobelnest: Übungstage zählen (für Sterne und Abzeichen) und Antworten für die Fortschritts-Übersicht melden */
const dayKey=()=>{const d=new Date();return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0')};
let knLv;
function knRec(ok){
  P.days=P.days||{};const t=dayKey();P.days[t]=(P.days[t]||0)+1;
  const ks=Object.keys(P.days).sort();while(ks.length>120)delete P.days[ks.shift()];
  const lv=(C.subjects.find(x=>x.id===P.sub)||C.subjects[0]||{}).name||null;
  if(lv!==knLv){knLv=lv;knSend({type:'level',level:lv})}
  knSend({type:'answer',ok:!!ok});
}
/* Knobelnest: Wortlisten der Lehrperson für die Klasse speichern */
let knSeq=0;const knWait={};
addEventListener('message',e=>{if(e.source!==parent||!e.data||e.data.vkAck==null)return;const f=knWait[e.data.vkAck];if(f){delete knWait[e.data.vkAck];f(e.data)}});
function knSave(c){return new Promise((res,rej)=>{const id=++knSeq,t=setTimeout(()=>{delete knWait[id];rej(new Error('timeout'))},15000);
  knWait[id]=d=>{clearTimeout(t);d.ok?res():rej(new Error(d.err||'fehler'))};knSend({type:'vkContent',id,content:JSON.parse(JSON.stringify(c))})})}""")
rep("function rec(id,ok){const w=WD(id);if(!w)return;", "function rec(id,ok){const w=WD(id);if(!w)return;knRec(ok);")

# 4) Speichern der Lehrperson geht ans Knobelnest (statt an claude.ai)
rep("  try{await ART.publish(buildHTML(C));", r"""  if(KN){const fin=()=>{if(btn){btn.disabled=false;btn.textContent='Für die Klasse veröffentlichen'}};
    try{await knSave(C);EMBED_JSON=JSON.stringify(C);dirty=false;renderPub();fin();toast('Gespeichert. Die Kinder sehen es beim nächsten Öffnen.')}
    catch(e){fin();toast('Speichern hat nicht geklappt. Bitte nochmals versuchen.')}
    return}
  try{await ART.publish(buildHTML(C));""")

# 5) Start: Lehrperson mit Bearbeiten-Recht (aus «Wörter & Freigaben» im Knobelnest)
rep("  if(!window.claude||!window.claude.use)return;",
    "  if(KN){if(KNI.teacher&&KNI.edit){CAN_EDIT=true;ART={};T=true;renderTop();renderBanner();renderPub();if(nav.view!=='session')rerender()}return}\n"
    "  if(!window.claude||!window.claude.use)return;")

# 6) Hinweis für die Kinder: der Fortschritt bleibt im Knobelnest (auf jedem Gerät gleich)
rep("wird auf diesem Gerät gespeichert.</p>`;",
    "wird ${KN?'im Knobelnest gespeichert – auf jedem Gerät gleich':'auf diesem Gerät gespeichert'}.</p>`;")

# 7) Tagesstern, Serie und Abzeichen (nur im Knobelnest)
#    Übungszeit zählt nur, solange eine Übung läuft und das Kind in den letzten 30 Sekunden etwas getippt hat.
#    Tagesstern ab 7 Minuten. Serie = Schultage hintereinander mit Tagesstern; Samstag, Sonntag und Tage mit
#    «Ferien» oder «schulfrei» im Hausaufgabenheft (settings.frei) zählen nicht und unterbrechen nicht.
#    Wochenheld = an allen Schultagen einer Woche einen Tagesstern. Kistenprofi = 100 Wörter im letzten Fach.
rep("function rec(id,ok){const w=WD(id);if(!w)return;knRec(ok);", r"""/* ---------- Knobelnest: Übungszeit, Tagesstern, Serie und Abzeichen ---------- */
const STAR_SEC=420,PROFI=100,FREI=new Set(KN&&KNI.settings&&Array.isArray(KNI.settings.frei)?KNI.settings.frei:[]);
let knAct=0;['pointerdown','keydown','input'].forEach(t=>addEventListener(t,()=>{knAct=Date.now()},true));
const isoOf=d=>d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');
const noon=d=>{d=new Date(d);d.setHours(12,0,0,0);return d};
const schoolDay=d=>{const w=d.getDay();return w>0&&w<6&&!FREI.has(isoOf(d))};
const starOn=k=>((P.sec||{})[k]||0)>=STAR_SEC;
function knStreak(){let n=0;const d=noon(new Date());
  for(let i=0;i<500;i++){if(schoolDay(d)){if(starOn(isoOf(d)))n++;else if(i>0)break}d.setDate(d.getDate()-1)}return n}
function knWeeks(){const ks=Object.keys(P.sec||{}).sort();if(!ks.length)return 0;const d=noon(ks[0]+'T12:00:00');d.setDate(d.getDate()-((d.getDay()+6)%7));
  const end=new Date();let n=0;
  while(d<=end){let sd=0,ok=true;for(let i=0;i<5;i++){const x=new Date(d);x.setDate(d.getDate()+i);if(schoolDay(x)){sd++;if(!starOn(isoOf(x)))ok=false}}
    if(sd&&ok)n++;d.setDate(d.getDate()+7)}return n}
function knFach5(){const ids=new Set();Object.values(P.boxes||{}).forEach(o=>Object.values(o||{}).forEach(b=>Object.entries((b&&b.map)||{}).forEach(([id,f])=>{if(f>=5)ids.add(id)})));return ids.size}
const knStars=()=>Object.keys(P.sec||{}).filter(starOn).length;
function knAward(){if(!KN)return;const sec={},d=noon(new Date());for(let i=0;i<35;i++){const k=isoOf(d);if((P.sec||{})[k])sec[k]=P.sec[k];d.setDate(d.getDate()-1)}
  knSend({type:'award',award:{stars:knStars(),vk:{streak:knStreak(),weeks:knWeeks(),fach5:knFach5(),sec}}})}
function knTick(){if(!KN||!session||document.hidden||Date.now()-knAct>30000)return;
  P.sec=P.sec||{};const k=dayKey(),b=P.sec[k]||0;P.sec[k]=b+1;
  if(b<STAR_SEC&&b+1>=STAR_SEC){toast('⭐ Tagesstern! Du hast heute 7 Minuten geübt.');saveP();knAward()}
  else if((b+1)%20===0){saveP();knAward()}}
const mmss=x=>Math.floor(x/60)+':'+String(x%60).padStart(2,'0');
function knTodayHTML(){
  const sec=(P.sec||{})[dayKey()]||0,ok=sec>=STAR_SEC,st=knStreak(),wk=knWeeks(),f5=knFach5();
  const fl=st?'🔥'.repeat(Math.min(st,10))+(st>10?' …':''):'';
  const bd=(ic,name,on,txt)=>`<div class="kb ${on?'on':''}"><span class="kbi">${ic}</span><span><b>${name}</b><small>${txt}</small></span></div>`;
  return `<div class="kntoday">
    <div class="kt kt-day ${ok?'on':''}"><span class="kts">⭐</span><div class="ktx"><b>${ok?'Tagesstern geschafft!':'Heute: '+mmss(sec)+' von 7 Minuten'}</b>
      <div class="bar"><i style="width:${Math.min(100,Math.round(sec/STAR_SEC*100))}%"></i></div><small>Es zählt nur die Zeit, in der du wirklich übst.</small></div></div>
    <div class="kt kt-fire ${st?'on':''}"><b class="ktn">${st}</b><div class="ktx"><span class="ktf">${fl||'Noch keine Flamme'}</span><small>${st===1?'Schultag':'Schultage'} hintereinander mit Tagesstern</small></div></div>
    <div class="kt kt-badges">${bd('🏅','Wochenheld',wk>0,wk?(wk>1?wk+'× geschafft':'geschafft!'):'jeden Schultag einer Woche einen Tagesstern')}
      ${bd('📦','Kistenprofi',f5>=PROFI,f5>=PROFI?'100 Wörter im letzten Fach!':f5+' von '+PROFI+' Wörtern im letzten Fach')}</div></div>`}
function rec(id,ok){const w=WD(id);if(!w)return;knRec(ok);""")
rep("  return `<div class=\"feat\">${boxTile('karte')}", "  return `${KN?knTodayHTML():''}<div class=\"feat\">${boxTile('karte')}")
rep("  if(KN){if(KNI.teacher&&KNI.edit)", "  if(KN){setInterval(knTick,1000);knAward();}\n  if(KN){if(KNI.teacher&&KNI.edit)")
rep("@media (prefers-reduced-motion:reduce)", r"""/* Knobelnest: Tagesstern, Serie, Abzeichen */
.kntoday{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:14px;margin-top:6px;margin-bottom:14px}
.kt{display:flex;align-items:center;gap:14px;background:#fff;border-radius:22px;box-shadow:var(--shadow);padding:14px 18px;min-width:0}
.kt small{display:block;color:var(--muted);font-size:13px;margin-top:3px}
.ktx{flex:1;min-width:0}
.kts{font-size:38px;filter:grayscale(1);opacity:.35}
.kt-day.on .kts{filter:none;opacity:1}
.kt-day.on{background:#fff8e1}
.kt .bar{max-width:none;margin-top:6px}
.kt-day.on .bar i{background:#e0a92a}
.ktn{font-family:var(--bub);font-size:44px;line-height:1;color:var(--muted);min-width:1.1em;text-align:center}
.kt-fire.on .ktn{color:#e0662a}
.ktf{font-size:22px;letter-spacing:-2px;word-break:break-all}
.kt-fire:not(.on) .ktf{font-size:15px;letter-spacing:0;color:var(--muted);font-weight:700}
.kt-badges{flex-direction:column;align-items:stretch;gap:8px}
.kb{display:flex;align-items:center;gap:10px;opacity:.55}
.kb.on{opacity:1}
.kbi{font-size:26px;filter:grayscale(1)}
.kb.on .kbi{filter:none}
@media (prefers-reduced-motion:reduce)""")

open(dst, 'w', encoding='utf-8').write(s)
print('ok', len(s))
