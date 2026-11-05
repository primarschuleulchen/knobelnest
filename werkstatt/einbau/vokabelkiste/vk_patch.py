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

# 2) Wortlisten der Klasse aus der Klassenkiste (sonst die eingebauten)
rep("let EMBED=null;try{EMBED=JSON.parse($('#vk-content').textContent)}catch(e){}",
    "let EMBED=null;try{EMBED=JSON.parse($('#vk-content').textContent)}catch(e){}\n"
    "const KN=!!KNI;\n"
    "if(KN&&KNI.settings&&KNI.settings.content&&Array.isArray(KNI.settings.content.subjects))EMBED=KNI.settings.content;")
rep("const EMBED_JSON=JSON.stringify(EMBED),EMBED_HASH=hashStr(EMBED_JSON);",
    "let EMBED_JSON=JSON.stringify(EMBED),EMBED_HASH=hashStr(EMBED_JSON);")

# 3) Fortschritt des Kindes in der Klassenkiste speichern (statt nur auf dem Gerät)
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

# 5) Start: Lehrperson mit Bearbeiten-Recht (aus «Wörter & Freigaben» in der Klassenkiste)
rep("  if(!window.claude||!window.claude.use)return;",
    "  if(KN){if(KNI.teacher&&KNI.edit){CAN_EDIT=true;ART={};T=true;renderTop();renderBanner();renderPub();if(nav.view!=='session')rerender()}return}\n"
    "  if(!window.claude||!window.claude.use)return;")

# 6) Hinweis für die Kinder: der Fortschritt bleibt in der Klassenkiste (auf jedem Gerät gleich)
rep("wird auf diesem Gerät gespeichert.</p>`;",
    "wird ${KN?'in der Klassenkiste gespeichert – auf jedem Gerät gleich':'auf diesem Gerät gespeichert'}.</p>`;")

# 7) Tagesstern, Serie und Abzeichen (nur in der Klassenkiste)
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
const starOf=(p,k)=>(((p&&p.sec)||{})[k]||0)>=STAR_SEC,starOn=k=>starOf(P,k);
function knStreak(p=P){let n=0;const d=noon(new Date());
  for(let i=0;i<500;i++){if(schoolDay(d)){if(starOf(p,isoOf(d)))n++;else if(i>0)break}d.setDate(d.getDate()-1)}return n}
function knWeeks(p=P){const ks=Object.keys((p&&p.sec)||{}).sort();if(!ks.length)return 0;const d=noon(ks[0]+'T12:00:00');d.setDate(d.getDate()-((d.getDay()+6)%7));
  const end=new Date();let n=0;
  while(d<=end){let sd=0,ok=true;for(let i=0;i<5;i++){const x=new Date(d);x.setDate(d.getDate()+i);if(schoolDay(x)){sd++;if(!starOf(p,isoOf(x)))ok=false}}
    if(sd&&ok)n++;d.setDate(d.getDate()+7)}return n}
function knFach5(p=P){const ids=new Set();Object.values((p&&p.boxes)||{}).forEach(o=>Object.values(o||{}).forEach(b=>Object.entries((b&&b.map)||{}).forEach(([id,f])=>{if(f>=5)ids.add(id)})));return ids.size}
const knStars=(p=P)=>Object.keys((p&&p.sec)||{}).filter(k=>starOf(p,k)).length;
function knAward(){if(!KN)return;const sec={},d=noon(new Date());for(let i=0;i<35;i++){const k=isoOf(d);if((P.sec||{})[k])sec[k]=P.sec[k];d.setDate(d.getDate()-1)}
  knSend({type:'award',award:{stars:knStars(),vk:{streak:knStreak(),weeks:knWeeks(),fach5:knFach5(),sec}}})}
function knTick(){if(!KN||!session||document.hidden||Date.now()-knAct>30000)return;
  P.sec=P.sec||{};const k=dayKey(),b=P.sec[k]||0;P.sec[k]=b+1;const lg=knLog();if(lg)lg.s=(lg.s||0)+1;
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

# 8) Lehrperson: Klassen-Übersicht und «So wurde geübt» pro Portion
#    Die Vokabelkiste merkt sich pro Portion und Übung: Anzahl Starts (n), Antworten (a), davon richtig (c), Sekunden (s), zuletzt (t)
#    in P.log[Portion][Übung] und pro Wort richtig/falsch in P.wc. Das Portal gibt der Lehrperson KNI.kids = [{id,name,p}] mit.
rep("function rec(id,ok){const w=WD(id);if(!w)return;knRec(ok);", r"""/* ---------- Knobelnest: Was wurde wo geübt (für die Lehrperson) ---------- */
let knMode=null;
function knLog(){if(!KN||!knMode)return null;P.log=P.log||{};const a=P.log[knMode.key]=P.log[knMode.key]||{};return a[knMode.mode]=a[knMode.mode]||{n:0,a:0,c:0,s:0}}
function knStart(key,mode){knMode={key:String(key||'?'),mode};const lg=knLog();if(lg){lg.n++;lg.t=Date.now();saveP()}}
function knWord(id,ok){if(!KN)return;P.wc=P.wc||{};const x=P.wc[id]=P.wc[id]||[0,0];x[ok?0:1]++;const lg=knLog();if(lg){lg.a++;if(ok)lg.c++;lg.t=Date.now()}}
const KIDS=KN&&KNI.settings&&Array.isArray(KNI.settings.kids)?KNI.settings.kids:[];
const MODE_NAMES={karte:'Kärtchen',drei:'3er',merken:'Merken',salat:'Salat',schreiben:'Schreiben',hoeren:'Hören',luecke:'Lücke',pairs:'Paare',regen:'Wortregen'};
const minTxt=x=>x?(x<60?'<1':Math.round(x/60))+' Min.':'–';
const pct=v=>v&&v.a?Math.round(v.c/v.a*100)+' %':'';
const dShort=t=>new Date(t).toLocaleDateString('de-CH',{day:'numeric',month:'numeric'});
function weekDays(back=0){const d=noon(new Date());d.setDate(d.getDate()-((d.getDay()+6)%7)-7*back);
  return ['Mo','Di','Mi','Do','Fr'].map((n,i)=>{const x=new Date(d);x.setDate(d.getDate()+i);return{n,k:isoOf(x),d:x}})}
function lastInfo(p){let best=null;Object.entries((p&&p.log)||{}).forEach(([key,m])=>Object.entries(m||{}).forEach(([mode,v])=>{if(v&&v.t&&(!best||v.t>best.t))best={t:v.t,key,mode}}));return best}
function keyName(key){if(key==='box')return'Karteikasten';if(key==='nuts')return'Knacknüsse';const id=String(key).split(':')[0],i=NODES.get(id);
  return i?i.node.name+(String(key).endsWith(':all')?' · Gesamt':''):'(gelöscht)'}
const sicherOf=(p,id)=>{const s=((p&&p.stats)||{})[id];if(s&&s.st>=2)return true;return Object.values((p&&p.boxes)||{}).some(o=>Object.values(o||{}).some(b=>((b&&b.map)||{})[id]>=3))};
const dayCell=(p,x)=>{const sec=(p&&p.sec)||{};return FREI.has(x.k)?'<td class="fr">frei</td>':`<td class="${starOf(p,x.k)?'ok':sec[x.k]?'part':''}">${sec[x.k]?Math.max(1,Math.round(sec[x.k]/60))+(starOf(p,x.k)?' ⭐':''):'–'}</td>`};
function goClass(){
  stopSession();nav={view:'class'};const wd=weekDays(),today=dayKey(),s=SUB();
  let h=crumbs(null,'Klasse')+`<div class="phead"><h1 class="big">Klasse</h1></div><p class="hand">So üben die Kinder. Tippe auf ein Kind für alle Einzelheiten oder unten auf eine Portion.</p>`;
  if(!KIDS.length)h+=`<div class="empty">Noch keine Kinder in dieser Klasse.</div>`;
  else h+=`<div class="ctab"><table><thead><tr><th class="l">Kind</th><th>Heute</th>${wd.map(x=>`<th>${x.n} ${x.d.getDate()}.</th>`).join('')}<th>🔥 Serie</th><th>⭐ Sterne</th><th>🏅 Wochenheld</th><th>📦 Fach 5</th><th>Knacknüsse</th><th class="l">Zuletzt geübt</th></tr></thead><tbody>`+
    KIDS.map(k=>{const p=k.p||{},sec=p.sec||{},st=knStreak(p),wk=knWeeks(p),f5=knFach5(p),nuts=Object.values(p.stats||{}).filter(x=>(x.w||0)>=NUT_AT).length,li=lastInfo(p);
      return `<tr><th class="l"><button class="kidb" data-kid="${esc(k.id)}">${esc(k.name)}</button></th><td class="${starOf(p,today)?'ok':sec[today]?'part':''}">${minTxt(sec[today]||0)}</td>${wd.map(x=>dayCell(p,x)).join('')}
        <td>${st?st+' '+'🔥'.repeat(Math.min(st,5)):'–'}</td><td>${knStars(p)||'–'}</td><td>${wk?(wk>1?wk+'×':'✓'):'–'}</td><td class="${f5>=PROFI?'ok':''}">${f5}/${PROFI}</td><td>${nuts||'–'}</td>
        <td class="l sm">${li?dShort(li.t)+' · '+esc(keyName(li.key))+' · '+esc(MODE_NAMES[li.mode]||(String(li.mode).startsWith('kasten')?'Karteikasten':li.mode)):'–'}</td></tr>`}).join('')+`</tbody></table></div>
    <p class="note">Minuten = echte Übungszeit (nur während einer Übung). Grün mit ⭐ = Tagesstern (7 Minuten), gelb = geübt, aber weniger als 7 Minuten. «frei» = Ferien oder schulfrei im Hausaufgabenheft.</p>`;
  h+=`<div class="sh"><h2 class="lbl">Portion anschauen</h2><p class="hand">${esc(s.name)} · Sprache oben wechseln</p></div>${portionPicker(s)}`;
  stage.innerHTML=h;bindClass();
}
function portionPicker(s){
  const grp=(n,depth)=>{const ps=(n.kids||[]).filter(x=>x.words),fs=(n.kids||[]).filter(x=>!x.words);
    return `<div class="cpg" style="margin-left:${depth*16}px"><b>${esc(n.name)}</b>${ps.length?`<div class="cpr">${ps.map(pb).join('')}</div>`:''}${fs.map(f=>grp(f,depth+1)).join('')}</div>`};
  const pb=n=>`<button class="pill sm ${isOpen(n)?'':'offp'}" data-cp="${n.id}">${esc(n.name)}${isOpen(n)?'':' 🔒'}</button>`;
  const loose=s.tree.filter(x=>x.words);
  return `<div class="cpick">${s.tree.filter(x=>!x.words).map(n=>grp(n,0)).join('')}${loose.length?`<div class="cpr">${loose.map(pb).join('')}</div>`:''}</div>`;
}
function bindClass(){$$('[data-kid]').forEach(b=>b.onclick=()=>goClassKid(b.dataset.kid));$$('[data-cp]').forEach(b=>b.onclick=()=>goClassPortion(b.dataset.cp));bindNodes(stage);window.scrollTo(0,0)}
function goClassPortion(id){
  const info=NODES.get(id);if(!info||!info.node.words)return goClass();
  if(info.sub!==SUB()){P.sub=info.sub.id;renderTop()}
  stopSession();nav={view:'classp',node:id};const node=info.node,ws=node.words.filter(valid),modes=Object.keys(MODE_NAMES).filter(m=>!(m==='luecke'&&noSent()));
  const path=info.path.slice(0,-1).map(n=>n.name).join(' › ');
  let h=crumbs(null,'Klasse')+`<div class="phead"><h1 class="big">${esc(node.name)}</h1><div class="hact"><button class="pill" id="toClass">← Klasse</button><button class="pill" data-node="${id}">Portion öffnen</button></div></div>
    <p class="hand">${esc(path)} · ${ws.length} Wörter${isOpen(node)?'':' · nicht freigegeben'}. Pro Übung: wie oft gestartet und wie viele Antworten richtig waren.</p>`;
  h+=`<div class="ctab"><table><thead><tr><th class="l">Kind</th><th>Zeit</th>${modes.map(m=>`<th>${MODE_NAMES[m]}</th>`).join('')}<th>Kann sicher</th><th class="l">Am meisten falsch</th></tr></thead><tbody>`+
    KIDS.map(k=>{const p=k.p||{},lg=((p.log||{})[id])||{},wc=p.wc||{};let tot=0;Object.values(lg).forEach(v=>tot+=(v&&v.s)||0);
      const sich=ws.filter(w=>sicherOf(p,w.id)).length,hard=ws.map(w=>({w,f:(wc[w.id]||[0,0])[1]})).filter(x=>x.f>0).sort((a,b)=>b.f-a.f).slice(0,3);
      return `<tr><th class="l"><button class="kidb" data-kid="${esc(k.id)}">${esc(k.name)}</button></th><td>${minTxt(tot)}</td>${modes.map(m=>{const v=lg[m];
        return v&&v.n?`<td class="${v.a&&v.c/v.a>=.8?'ok':'part'}"><b>${v.n}×</b>${v.a?`<small>${pct(v)} richtig</small>`:''}</td>`:'<td class="no">–</td>'}).join('')}
        <td class="${ws.length&&sich===ws.length?'ok':''}">${sich}/${ws.length}</td><td class="l sm">${hard.map(x=>`${esc(Q(x.w))} <span class="mut">${x.f}×</span>`).join(', ')||'–'}</td></tr>`}).join('')+`</tbody></table></div>`;
  const rows=ws.map(w=>{let r=0,f=0,k=0;KIDS.forEach(kd=>{const x=((kd.p||{}).wc||{})[w.id];if(x){r+=x[0];f+=x[1]}if(sicherOf(kd.p,w.id))k++});return{w,r,f,k}}).sort((a,b)=>b.f-a.f||a.k-b.k);
  h+=`<div class="sh"><h2 class="lbl">Wörter</h2><p class="hand">Die schwierigsten zuerst</p></div><div class="ctab"><table><thead><tr><th class="l">Deutsch</th><th class="l">${esc(SUB().name)}</th><th>Richtig</th><th>Falsch</th><th>Kinder, die es sicher können</th></tr></thead><tbody>`+
    rows.map(x=>`<tr><td class="l">${esc(x.w.de)}</td><td class="l"><b>${esc(x.w.f)}</b></td><td>${x.r||'–'}</td><td class="${x.f?'bad':''}">${x.f||'–'}</td><td>${x.k}/${KIDS.length}</td></tr>`).join('')+`</tbody></table></div>
    <p class="note">«Kann sicher» = zuletzt mindestens 2× hintereinander richtig oder im Karteikasten ab Fach 3. Gezählt wird ab dem Tag, an dem diese Ansicht eingebaut wurde.</p>`;
  stage.innerHTML=h;$('#toClass').onclick=goClass;bindClass();
}
function goClassKid(kid){
  const k=KIDS.find(x=>x.id===kid);if(!k)return goClass();
  stopSession();nav={view:'classk',kid};const p=k.p||{},st=knStreak(p),wk=knWeeks(p),f5=knFach5(p);
  let h=crumbs(null,'Klasse')+`<div class="phead"><h1 class="big">${esc(k.name)}</h1><div class="hact"><button class="pill" id="toClass">← Klasse</button></div></div>
    <div class="kntoday"><div class="kt kt-fire ${st?'on':''}"><b class="ktn">${st}</b><div class="ktx"><span class="ktf">${st?'🔥'.repeat(Math.min(st,10)):'Keine Serie'}</span><small>Schultage hintereinander mit Tagesstern</small></div></div>
      <div class="kt kt-day ${knStars(p)?'on':''}"><span class="kts">⭐</span><div class="ktx"><b>${knStars(p)} Tagessterne</b><small>insgesamt</small></div></div>
      <div class="kt kt-badges"><div class="kb ${wk?'on':''}"><span class="kbi">🏅</span><span><b>Wochenheld</b><small>${wk?wk+'× geschafft':'noch nicht'}</small></span></div>
        <div class="kb ${f5>=PROFI?'on':''}"><span class="kbi">📦</span><span><b>Kistenprofi</b><small>${f5} von ${PROFI} Wörtern im letzten Fach</small></span></div></div></div>`;
  h+=`<div class="sh"><h2 class="lbl">Übungszeit</h2><p class="hand">Minuten pro Schultag, die letzten 4 Wochen</p></div><div class="ctab"><table><thead><tr><th class="l">Woche</th><th>Mo</th><th>Di</th><th>Mi</th><th>Do</th><th>Fr</th><th>Total</th></tr></thead><tbody>`+
    [0,1,2,3].map(b=>{const wd=weekDays(b);let t=0;wd.forEach(x=>t+=((p.sec||{})[x.k]||0));return `<tr><th class="l">${b?dShort(wd[0].d)+' – '+dShort(wd[4].d):'Diese Woche'}</th>${wd.map(x=>dayCell(p,x)).join('')}<td><b>${minTxt(t)}</b></td></tr>`}).join('')+`</tbody></table></div>`;
  const lg=p.log||{},keys=Object.keys(lg).sort((a,b)=>Math.max(0,...Object.values(lg[b]).map(v=>v.t||0))-Math.max(0,...Object.values(lg[a]).map(v=>v.t||0)));
  h+=`<div class="sh"><h2 class="lbl">Geübte Portionen</h2><p class="hand">zuletzt geübt zuerst</p></div>`+(keys.length?`<div class="ctab"><table><thead><tr><th class="l">Portion</th><th>Zeit</th><th class="l">Übungen</th><th>Zuletzt</th></tr></thead><tbody>`+
    keys.map(key=>{const m=lg[key];let t=0,last=0;Object.values(m).forEach(v=>{t+=v.s||0;last=Math.max(last,v.t||0)});const id=String(key).split(':')[0];
      return `<tr><th class="l">${NODES.has(id)&&NODES.get(id).node.words?`<button class="kidb" data-cp="${id}">${esc(keyName(key))}</button>`:esc(keyName(key))}</th><td>${minTxt(t)}</td>
        <td class="l sm">${Object.entries(m).map(([mo,v])=>`${esc(MODE_NAMES[mo]||(mo==='kasten-karte'?'Kasten Kärtchen':mo==='kasten-schreiben'?'Kasten Schreiben':mo))} ${v.n}×${v.a?' ('+pct(v)+')':''}`).join(' · ')}</td><td>${last?dShort(last):'–'}</td></tr>`}).join('')+`</tbody></table></div>`
    :`<div class="empty">Noch keine Übungen aufgezeichnet.</div>`);
  const nuts=Object.entries(p.stats||{}).filter(([id,x])=>(x.w||0)>=NUT_AT&&WD(id)).map(([id])=>WD(id));
  const wc=p.wc||{},hard=Object.keys(wc).filter(id=>WD(id)&&wc[id][1]).sort((a,b)=>wc[b][1]-wc[a][1]).slice(0,15);
  h+=`<div class="sh"><h2 class="lbl">Knifflige Wörter</h2></div><p>${nuts.length?'<b>Knacknüsse:</b> '+nuts.map(w=>`${esc(w.de)} = ${esc(w.f)}`).join(' · '):'Zurzeit keine Knacknüsse.'}</p>`+
    (hard.length?`<p><b>Am meisten falsch:</b> ${hard.map(id=>`${esc(WD(id).de)} = ${esc(WD(id).f)} <span class="mut">(${wc[id][1]}× falsch, ${wc[id][0]}× richtig)</span>`).join(' · ')}</p>`:'');
  stage.innerHTML=h;$('#toClass').onclick=goClass;bindClass();
}
function rec(id,ok){const w=WD(id);if(!w)return;knRec(ok);knWord(id,ok);""")
rep("  MODE_FN()[b.dataset.mode]()})}", "  knStart(SET.key,b.dataset.mode);MODE_FN()[b.dataset.mode]()})}")
rep("  SET={key:'box',label:'Karteikasten',words:list.map(WD)};", "  SET={key:'box',label:'Karteikasten',words:list.map(WD)};knStart('box','kasten-'+kind);")
rep("function rerender(){if(nav.view==='all')", "function rerender(){if(nav.view==='class')return goClass();if(nav.view==='classp')return goClassPortion(nav.node);if(nav.view==='classk')return goClassKid(nav.kid);if(nav.view==='all')")
rep("    ${CAN_EDIT?`<button class=\"pill ${T?'rose':''}\" id=\"tbtn\">", "    ${CAN_EDIT&&KN?`<button class=\"pill\" id=\"clsbtn\">📊 Klasse</button>`:''}${CAN_EDIT?`<button class=\"pill ${T?'rose':''}\" id=\"tbtn\">")
rep("  const tb=$('#tbtn');if(tb)tb.onclick=", "  const cb=$('#clsbtn');if(cb)cb.onclick=goClass;\n  const tb=$('#tbtn');if(tb)tb.onclick=")
rep("<div class=\"hact\"><button class=\"pill ${isOpen(node)?'go':'rose'}\" id=\"relNode\">", "<div class=\"hact\">${KN&&isPortion?'<button class=\"pill\" id=\"cpBtn\">📊 So wurde geübt</button>':''}<button class=\"pill ${isOpen(node)?'go':'rose'}\" id=\"relNode\">")
rep("    $('#relNode').onclick=()=>toggleRelease(id);", "    $('#relNode').onclick=()=>toggleRelease(id);const cpb=$('#cpBtn');if(cpb)cpb.onclick=()=>goClassPortion(id);")
rep("@media (prefers-reduced-motion:reduce)", r"""/* Knobelnest: Klassen-Übersicht der Lehrperson */
.ctab{background:#fff;border-radius:18px;box-shadow:var(--shadow);overflow:auto;margin-top:8px}
.ctab table{border-collapse:collapse;width:100%;font-size:14px}
.ctab th,.ctab td{padding:8px 10px;border-bottom:1px solid var(--line);text-align:center;white-space:nowrap;vertical-align:middle}
.ctab thead th{font-size:12px;font-weight:800;color:var(--muted);text-transform:uppercase;letter-spacing:.04em;background:var(--paper);position:sticky;top:0}
.ctab .l{text-align:left}
.ctab .sm{font-size:13px;white-space:normal;min-width:180px}
.ctab td.ok{background:var(--leaf-soft);color:var(--leaf-deep);font-weight:800}
.ctab td.part{background:#fff6dc}
.ctab td.fr,.ctab td.no{color:var(--rule)}
.ctab td.bad{color:var(--rose-ink);font-weight:800}
.ctab td small{display:block;font-size:11.5px;font-weight:700;color:var(--muted)}
.ctab .mut{color:var(--muted);font-size:12px}
.kidb{border:0;background:none;padding:0;font-weight:800;color:var(--navy);text-align:left;text-decoration:underline;text-decoration-color:var(--rule);text-underline-offset:3px}
.kidb:hover{color:var(--rose-ink)}
.cpick{display:flex;flex-direction:column;gap:10px;margin-top:6px}
.cpg>b{font-family:var(--hand);font-size:22px;font-weight:400;color:var(--navy)}
.cpr{display:flex;flex-wrap:wrap;gap:6px;margin-top:4px}
.pill.offp{opacity:.6}
@media (prefers-reduced-motion:reduce)""")


# 9) iPad/Safari: Beim Umdrehen schimmerte die Vorderseite gespiegelt durch die Rückseite.
#    Darum wird zusätzlich zur 3D-Drehung die verdeckte Seite in der Mitte der Drehung unsichtbar geschaltet.
rep("@media (prefers-reduced-motion:reduce)", r"""/* Knobelnest: Kärtchen-Rückseite auf iPad sauber (verdeckte Seite ausblenden) */
.inner>.face{transform:rotateY(0deg) translateZ(1px);transition:visibility 0s linear .27s}
.inner>.face.back,.inner>.face.open{transform:rotateY(180deg) translateZ(1px);visibility:hidden}
.flipped>.inner>.face{visibility:hidden}
.flipped>.inner>.face.back,.flipped>.inner>.face.open{visibility:visible}
@media (prefers-reduced-motion:reduce)""")

# 10) Im Knobelnest gibt es keinen dunklen Balken mehr (wie beim Hausaufgabenheft): Die Vokabelkiste hat
#     links oben selbst einen Knopf «← Klassenkiste», der das Portal bittet, sie zu schliessen.
rep("  $('#top').innerHTML=`<button class=\"brand\" id=\"brand\"", "  $('#top').innerHTML=`${KN?'<button class=\"pill\" id=\"knBack\">← Klassenkiste</button>':''}<button class=\"brand\" id=\"brand\"")
rep("  $('#brand').onclick=()=>goNode(null);", "  $('#brand').onclick=()=>goNode(null);\n  const kb=$('#knBack');if(kb)kb.onclick=()=>{saveP();knAward();knSend({type:'close'})};")

# 11) Vorlagen: Die Admin-Lehrperson gibt Portionen oder ganze Ordner «als Vorlage» frei (n.tpl; ein Ordner gilt für alles darin).
#     Das Portal speichert daraus shared_store «vokabelkiste-vorlage». Bei anderen Lehrpersonen werden neue Vorlage-Portionen
#     beim Öffnen von «Wörter & Freigaben» als Kopie eingefügt (für Kinder gesperrt). C.tplSeen merkt sich, was schon kam,
#     damit Gelöschtes nicht wiederkommt und Änderungen der Lehrperson bleiben.
rep("/* ---------- Knobelnest: Was wurde wo geübt (für die Lehrperson) ---------- */", r"""/* ---------- Knobelnest: Vorlagen für andere Lehrpersonen ---------- */
const KN_ADMIN=KN&&!!KNI.admin,TPL=KN&&KNI.settings&&KNI.settings.tpl&&Array.isArray(KNI.settings.tpl.subjects)?KNI.settings.tpl:null;
let knFresh=false;
const tplOf=id=>{const i=NODES.get(id);return !i?0:i.node.tpl?1:i.path.some(n=>n.tpl)?2:0};
function toggleTpl(id){const i=NODES.get(id);if(!i)return;if(i.node.tpl)delete i.node.tpl;else i.node.tpl=true;
  touch();rerender();toast(i.node.tpl?'Als Vorlage für Lehrpersonen freigegeben. Wird gespeichert …':'Keine Vorlage mehr. Wird gespeichert …');publishContent(null)}
function findDeep(arr,id){for(const n of arr){if(n.id===id)return n;if(n.kids){const f=findDeep(n.kids,id);if(f)return f}}return null}
function mergeTpl(){
  if(KN_ADMIN)return [];
  /* Klasse ohne eigene Listen: nur mit den zugeteilten Vorlagen beginnen (nicht mit den eingebauten Listen) */
  if(KNI.settings&&KNI.settings.tplOn&&!KNI.settings.content&&!C.tplSeen){C.subjects.forEach(x=>{x.tree=[];x.excl=[]});C.tplSeen=[];knFresh=true}
  if(!TPL)return [];
  const seen=new Set(C.tplSeen||[]),added=[];
  TPL.subjects.forEach(ts=>{let sub=C.subjects.find(s=>s.id===ts.id);
    if(!sub){sub={id:ts.id,name:ts.name,lang:ts.lang,excl:[],tree:[]};C.subjects.push(sub)}
    const walk=(tarr,getArr)=>(tarr||[]).forEach(tn=>{
      if(tn.words){if(seen.has(tn.id))return;seen.add(tn.id);if(findDeep(sub.tree,tn.id))return;
        const cp=JSON.parse(JSON.stringify(tn));delete cp.tpl;cp.open=false;getArr().push(cp);added.push(cp.name);
        (ts.excl||[]).forEach(x=>{if(cp.words.some(w=>w.id===x)&&!sub.excl.includes(x))sub.excl.push(x)})}
      else{let f=null;walk(tn.kids,()=>{if(f)return f.kids;f=findDeep(sub.tree,tn.id);if(!f){f={id:tn.id,name:tn.name,kids:[],open:false};getArr().push(f)}f.kids=f.kids||[];return f.kids})}});
    walk(ts.tree,()=>sub.tree)});
  C.tplSeen=[...seen];return added;
}
/* ---------- Knobelnest: Was wurde wo geübt (für die Lehrperson) ---------- */""")
rep("CAN_EDIT=true;ART={};T=true;renderTop();", "CAN_EDIT=true;ART={};T=true;{const ad=mergeTpl();if(ad.length||knFresh){touch();publishContent(null);}if(ad.length){setTimeout(()=>toast('Neu von '+(TPL.by||'der Admin-Lehrperson')+': '+ad.join(', ')+'. Für die Kinder noch gesperrt.'),900)}}renderTop();")
rep("<div class=\"hact\">${KN&&isPortion?", "<div class=\"hact\">${KN_ADMIN?(()=>{const t=tplOf(id);return t===2?'<span class=\"pill\" style=\"cursor:default\">📤 Vorlage (ganzer Ordner)</span>':`<button class=\"pill ${t?'go':''}\" id=\"tplNode\">${t?'✓ Vorlage für Lehrpersonen':'📤 Als Vorlage freigeben'}</button>`})():''}${KN&&isPortion?")
rep("    $('#relNode').onclick=()=>toggleRelease(id);", "    $('#relNode').onclick=()=>toggleRelease(id);const tpb=$('#tplNode');if(tpb)tpb.onclick=()=>toggleTpl(id);")
rep("${T&&!op?' · <span class=\"lock\">nicht freigegeben</span>':''}</span>", "${T&&!op?' · <span class=\"lock\">nicht freigegeben</span>':''}${KN_ADMIN&&tplOf(n.id)?' · 📤 Vorlage':''}</span>")

# 12) Karteikasten: Ein Kärtchen rutscht erst nach 2× «Gewusst» weiter. Damit der Zähler nicht scheinbar bei 0 stehen bleibt,
#     zeigt er auch die Kärtchen, die schon 1× gewusst wurden, und der Balken wächst schon beim ersten Mal.
rep("  const next=()=>{setProg(`${doneN} von ${total} fertig · ${up} weiter, ${down} zurück`,doneN/total);",
    "  const next=()=>{const once=queue.filter(id=>(b.hits[id]||0)===1).length;setProg(`${doneN} von ${total} fertig · ${once} schon 1× gewusst · ${up} weiter, ${down} zurück<br><small>Ein Kärtchen rutscht ins nächste Fach, wenn du es 2× gewusst hast.</small>`,(doneN+once/2)/total);")


# 13) Ausbau (November 2026): Bilder zu den Wörtern, Übungen «Bild & Wort» und «Sprechen», Stil der Eulenkiste.
#     Der Code steht in eigenen Dateien neben diesem Skript:
#       vk_ausbau.js  = Bilder (w.img: Emoji, eigenes Bild als data:image oder '-' = kein Bild; sonst automatisch aus vk_emoji.txt),
#                       Bild-Auswahl im Editor (picDialog), modeBild, modeTalk (Spracherkennung, sonst aufnehmen, sonst selbst prüfen)
#       vk_eule.css   = Gestaltung der neuen Teile und Stil der Eulenkiste (Patrick Hand lokal, Gold, Blau)
#       vk_emoji.txt  = Wörter -> Emoji (de: = nur deutsches Wort, fl: = nur Fremdwort)
import os, json
HIER = os.path.dirname(os.path.abspath(__file__))
def datei(n): return open(os.path.join(HIER, n), encoding='utf-8').read()
emo, schon = [], set()
for z in datei('vk_emoji.txt').splitlines():
    z = z.strip()
    if not z or z.startswith('#') or '=' not in z: continue
    e, ks = z.split('=', 1)
    for k in ks.split('|'):
        k = k.strip().lower()
        if k and k not in schon: schon.add(k); emo.append([k, e.strip()])
js = datei('vk_ausbau.js').replace('__EMOJI__', json.dumps(emo, ensure_ascii=False))
rep("/* ---------- Karteikasten (pro Sprache) ---------- */", js + "\n/* ---------- Karteikasten (pro Sprache) ---------- */")
rep("@media (prefers-reduced-motion:reduce)", datei('vk_eule.css') + "@media (prefers-reduced-motion:reduce)")
# Keine Schriften von Google (Patrick Hand kommt aus schriften/)
rep('<link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Patrick+Hand&family=Amatic+SC:wght@700&family=Nunito:wght@400;600;700;800&family=Fredoka:wght@500;600;700&display=swap">\n', '')
# Logo der Vokabelkiste (rund mit Goldrand) statt der gezeichneten Kiste
rep('id="brand" aria-label="Zur Übersicht">${BOX_SVG}', 'id="brand" aria-label="Zur Übersicht">${KN?\'<img src="../bilder/kacheln/vokabelkiste.webp" alt="">\':BOX_SVG}')
# Im Knobelnest hat das Fenster Zugriff auf den Speicher der Klassenkiste (wegen des Mikrofons). Die Vokabelkiste soll dort
# nichts ablegen (Entwürfe, Navigation): alles bleibt wie vorher in der Klassenkiste gespeichert.
for a in ("const lsGet=k=>{try{", "const ssGet=k=>{try{"): rep(a, a + "if(window.parent!==window)return null;")
for a in ("const lsSet=(k,v)=>{try{", "const lsDel=k=>{try{", "const ssSet=(k,v)=>{try{"): rep(a, a + "if(window.parent!==window)return;")
# Neue Übungen in der Auswahl, im Start und in der Klassen-Übersicht
rep("].filter(m=>!(m[0]==='luecke'&&noSent()));", "].filter(m=>!(m[0]==='luecke'&&noSent()));knMoreModes(MODES,ws);")
rep("regen:modeRain});", "regen:modeRain,bild:modeBild,sprechen:modeTalk});")
rep("regen:'Wortregen'};", "regen:'Wortregen',bild:'Bild',sprechen:'Sprechen'};")
# Kärtchen: Bild klein auf der Rückseite
rep("<div class=\"face back\"><div class=\"lang\"><span>${esc(aLang())}</span>${!qIsF?spkBtn(w.f):''}</div>",
    "<div class=\"face back\"><div class=\"lang\"><span>${esc(aLang())}</span>${!qIsF?spkBtn(w.f):''}</div>${picOf(w)?`<div class=\"cpic\">${picHTML(picOf(w))}</div>`:''}")
rep("${qIsF?spkBtn(w.f):''}</div>", "${qIsF?spkBtn(w.f):''}</div>${!qIsF&&picOf(w)?`<div class=\"cpic\">${picHTML(picOf(w))}</div>`:''}")
# Editor: Bild-Spalte vorne
rep('<span class="th">Deutsch</span>', '<span class="th">Bild</span><span class="th">Deutsch</span>')
rep("      `<input class=\"inp\" data-id=\"${w.id}\" data-f=\"de\"", "      `${picCell(w)}<input class=\"inp\" data-id=\"${w.id}\" data-f=\"de\"")
rep("$$('#etab [data-del]').forEach(b=>b.onclick=()=>{node.words=node.words.filter(x=>x.id!==b.dataset.del);touch();table()});",
    "$$('#etab [data-del]').forEach(b=>b.onclick=()=>{node.words=node.words.filter(x=>x.id!==b.dataset.del);touch();table()});bindPics(node,table);")
rep('«Kasten» weg = ', 'Tippe auf das runde Bild, um es zu ändern (gestrichelt = automatisch gewählt). «Kasten» weg = ')


# 14) Anzeige «geschafft» (vk_ausbau.js: vkReq, vkMark, vkHead, vkTileMark, vkCardMark): Am Ende einer Übung (Schluss-Seite) wird sie
#     für die Portion abgehakt. Über den Übungen steht «6 von 9 Übungen geschafft» mit Punkten, die Kacheln zeigen «✓ geschafft»,
#     die Portions-Karten «6/9 Übungen» bzw. «✓ geschafft».
rep("function summary(body,{title,lines,actions}){", "function summary(body,{title,lines,actions}){vkMark(lines);")
rep('Am besten der Reihe nach, von 1 bis ${MODES.length}.</p>', 'Am besten der Reihe nach, von 1 bis ${MODES.length}.</p>${vkHead()}')
rep('<span class="go">Starten →</span></button>`;', '${vkTileMark(m)}<span class="go">Starten →</span></button>`;')
rep('<span class="fmeta">${meta}', '<span class="fmeta">${meta}${vkCardMark(n)?\' · \'+vkCardMark(n):\'\'}')


# 15) Mein Heft, Sticker, Abzeichen, Urkunden, Klassen-Ziel und Bilder in der Datenbank (Version 30, Code in vk_heft.js,
#     Bilder-Speicher in vk_ausbau.js: w.img = 'vk:<id>', geholt über das Portal mit knAsk('vkBilder')).
rep("/* ---------- Karteikasten (pro Sprache) ---------- */", datei('vk_heft.js') + "\n/* ---------- Karteikasten (pro Sprache) ---------- */")
# Knopf «Mein Heft» oben und Ansicht im Navigations-Verteiler
rep("${CAN_EDIT&&KN?`<button class=\"pill\" id=\"clsbtn\">📊 Klasse</button>`:''}", "${CAN_EDIT&&KN?`<button class=\"pill\" id=\"clsbtn\">📊 Klasse</button>`:''}")
rep("const cb=$('#clsbtn');if(cb)cb.onclick=goClass;", "const cb=$('#clsbtn');if(cb)cb.onclick=goClass;const hb=$('#heftBtn');if(hb)hb.onclick=()=>goHeft();")
rep("function rerender(){if(nav.view==='class')", "function rerender(){if(nav.view==='heft')return goHeft(nav.tab);if(nav.view==='class')")
# Klassen-Ziel auf der Startseite der Sprache
rep("  return `${KN?knTodayHTML():''}<div class=\"feat\">", "  return `${KN?knTodayHTML()+vkZielHTML(T):''}<div class=\"feat\">")
# Lehrperson: Belohnungen und Sticker-Spalte in der Klassen-Übersicht
rep("h+=`<div class=\"sh\"><h2 class=\"lbl\">Portion anschauen</h2>", "h+=vkClassRewards();h+=`<div class=\"sh\"><h2 class=\"lbl\">Portion anschauen</h2>")
rep("stage.innerHTML=h;bindClass();", "stage.innerHTML=h;bindClass();bindClassRewards();")
rep("<th>Knacknüsse</th>", "<th>Knacknüsse</th><th>🧩 Sticker</th>")
rep("<td>${nuts||'–'}</td>", "<td>${nuts||'–'}</td><td>${vkStkN(p)||'–'}</td>")
# Editor: viele Bilder auf einmal (Dateiname = Wort, auch ZIP)
rep('<details class="import"><summary>Viele Wörter auf einmal einfügen</summary>',
    '<div class="bulk"><label class="pill"><input type="file" accept="image/*,.zip" multiple hidden id="bulkPic">🖼 Viele Bilder hochladen</label><span class="note">Bilder oder eine ZIP-Datei. Der Dateiname ist das Wort, z. B. «lifejacket.png» oder «Rettungsweste.png».</span></div><details class="import"><summary>Viele Wörter auf einmal einfügen</summary>')
rep("$('#impBtn').onclick=", "bindBulk(node,table);$('#impBtn').onclick=")
# Start: Sticker, Urkunden und Abzeichen nachführen
rep("  if(KN){setInterval(knTick,1000);knAward();}", "  if(KN){setInterval(knTick,1000);knAward();vkCheckAll(false);vkBadgeReady=true;}")


# 16) Abzeichen «Regenmeister»: jedes Mal, wenn das Kind im Wortregen seinen eigenen Rekord knackt (ab 10 Punkten)
rep("if(isRec){P.rain[key]=score;", "if(isRec){P.rain[key]=score;if(score>=10){vkCount('regen');vkBadgeCheck()}")


# 17) «Mein Heft» als Kachel auf der Startseite der Sprache (statt Wochenheld/Kistenprofi; die sind jetzt Abzeichen im Heft)
rep("""    <div class="kt kt-badges">${bd('🏅','Wochenheld',wk>0,wk?(wk>1?wk+'× geschafft':'geschafft!'):'jeden Schultag einer Woche einen Tagesstern')}
      ${bd('📦','Kistenprofi',f5>=PROFI,f5>=PROFI?'100 Wörter im letzten Fach!':f5+' von '+PROFI+' Wörtern im letzten Fach')}</div></div>`}""",
    """    ${vkHeftCard()}</div>`}""")

open(dst, 'w', encoding='utf-8').write(s)
print('ok', len(s))
