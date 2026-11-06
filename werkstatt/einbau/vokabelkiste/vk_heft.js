/* ---------- Knobelnest: Mein Heft (Sticker, Abzeichen, Urkunden) und Klassen-Ziel ----------
   Sticker: für jede geschaffte Portion einer (P.stk = {Sticker-ID: {n, g, t}}, P.stkFor = {Portion: Sticker-ID}).
     Welche Übungen zählen, stellt die Lehrperson pro Klasse ein (C.belohnung.modes, siehe vkReq).
     Goldrand (selten): jeder 5. Sticker und jeder Sticker, solange die Serie 5 Schultage oder mehr hat.
     Die Bilder lädt die Admin-Lehrperson hoch (shared_store «vokabelkiste-sticker» = {list:[{id,name}]}, Bilder in vk_bilder).
     Ohne eigene Sticker: Tier-Emojis als Ersatz.
   Abzeichen: zählen mit (P.cnt und vorhandene Zahlen), werden ab 5, 10 und 25 grösser (vkTier).
   Urkunden: für jeden Ordner mit Portionen (z. B. «Unit 1»), wenn alle Portionen darin geschafft sind (P.urk = {Ordner: Zeit}).
   Klassen-Ziel: C.ziel = {anzahl, belohnung, ab}; gezählt werden die Tagessterne aller Kinder seit «ab» (kid_vk_extra). */
const EXTRA=KN&&KNI.settings&&KNI.settings.extra||{};
const KIDNAME=KN&&KNI.name?String(KNI.name):'',KIDNAME_=KIDNAME;
let STK=((EXTRA.sticker&&Array.isArray(EXTRA.sticker.list))?EXTRA.sticker.list:[]).filter(x=>x&&x.id);
/* Feste Sticker-Tiere der Lehrerin (vokabelkiste/sticker/<name>.webp), dazu die in «Belohnungen» hochgeladenen */
const TIERE=['fuchs','baer','biene','delfin','eichhoernchen','eisbaer','esel','frosch','giraffe','hund','igel','katze'];
const stkList=()=>TIERE.map(n=>({id:'t-'+n,img:'sticker/'+n+'.webp?v=1',name:n})).concat(STK.map(x=>({id:x.id,img:'vk:'+x.id,name:x.name||''})));
const vkCount=(k,n=1)=>{P.cnt=P.cnt||{};P.cnt[k]=(P.cnt[k]||0)+n};
/* richtig geschrieben / gesagt zählen (rec wird hier ergänzt) */
{const r0=rec;rec=function(id,ok){r0(id,ok);if(!ok||!knMode)return;
  if(['schreiben','hoeren','luecke','merken','salat'].includes(knMode.mode))vkCount('schreib');
  if(knMode.mode==='sprechen')vkCount('sag')}}

function vkGold(){const n=Object.values(P.stk||{}).reduce((a,e)=>a+(e.n||0),0)+1;return n%5===0||knStreak()>=5}
function vkGiveSticker(key){
  const list=stkList();P.stk=P.stk||{};P.stkFor=P.stkFor||{};if(P.stkFor[key])return null;
  const neu=list.filter(s=>!P.stk[s.id]),pool=neu.length?neu:list,s=pool[Math.random()*pool.length|0],gold=vkGold();
  const e=P.stk[s.id]=P.stk[s.id]||{n:0,g:0,t:0};e.n++;if(gold)e.g++;e.t=Date.now();P.stkFor[key]=s.id;
  return {s,gold,first:e.n===1}}
/* Alle Portionen prüfen (auch nach einer neuen Einstellung der Lehrperson) und Sticker und Urkunden vergeben */
function vkCheckAll(show){if(!KN||T)return;
  const got=[];P.done=P.done||{};P.ganz=P.ganz||{};
  NODES.forEach((inf,id)=>{const n=inf.node;if(inf.sub!==SUB()||!n.words||!pathOpen(id))return;const ws=wordsOf(n),req=vkReq(ws),d=P.done[id]||{};
    if(req.length&&req.every(m=>d[m])){if(!P.ganz[id])P.ganz[id]=Date.now();const r=vkGiveSticker(id);if(r)got.push(r)}});
  const urk=[];P.urk=P.urk||{};
  vkUnits().forEach(u=>{if(!P.urk[u.id]&&u.total&&u.done>=u.total){P.urk[u.id]=Date.now();urk.push(u)}});
  vkBadgeCheck();
  if(got.length||urk.length){saveP();if(show)vkCelebrate(got,urk);else toast('Neu in deinem Heft: '+(got.length?got.length+' Sticker':'')+(got.length&&urk.length?' und ':'')+(urk.length?urk.length+' Urkunde':''))}}
/* Ordner mit Portionen = «Unit» */
function vkUnits(){const out=[];
  NODES.forEach((inf,id)=>{const n=inf.node;if(inf.sub!==SUB()||n.words||!(n.kids||[]).some(k=>k.words)||!pathOpen(id))return;
    const ps=[];const walk=x=>(x.kids||[]).forEach(k=>{if(!vis(k))return;if(k.words){if(wordsOf(k).length&&vkReq(wordsOf(k)).length)ps.push(k)}else walk(k)});walk(n);
    out.push({id,name:n.name,path:inf.path.map(x=>x.name),total:ps.length,done:ps.filter(k=>(P.ganz||{})[k.id]).length,words:wordsOf(n).length,sub:SUB().name})});
  return out}

/* Abzeichen: [id, Symbol, Name, wofür, Zahl]. Bild im Heft: vokabelkiste/abzeichen/<id>.webp (gezeichnet von der Lehrerin, rund) */
const BADGES=[
  ['stern','⭐','Tagesstern','7 Minuten an einem Tag geübt',()=>knStars()],
  ['serie','🔥','Dranbleiber','5 Schultage hintereinander geübt',()=>(P.cnt||{}).serie||0],
  ['woche','🏅','Wochenheld','jeden Schultag einer Woche einen Tagesstern',()=>knWeeks()],
  ['portion','🏁','Portion geschafft','alle Übungen einer Portion gemacht',()=>Object.keys(P.ganz||{}).length],
  ['perfekt','💯','Fehlerfrei','eine Übung ohne einen Fehler',()=>(P.cnt||{}).perfekt||0],
  ['sprech','🎤','Sprechprofi','je 20 Wörter richtig gesagt',()=>Math.floor(((P.cnt||{}).sag||0)/20)],
  ['schreib','✍️','Schreibprofi','je 50 Wörter richtig geschrieben',()=>Math.floor(((P.cnt||{}).schreib||0)/50)],
  ['ohr','👂','Gutes Ohr','«Hören & Schreiben» ohne Fehler',()=>(P.cnt||{}).ohr||0],
  ['regen','🌧️','Regenmeister','eigenen Rekord im Wortregen geknackt (ab 10 Punkten)',()=>(P.cnt||{}).regen||0],
  ['bild','🖼️','Bilderblick','«Bild & Wort» ganz durch',()=>(P.cnt||{}).bild||0],
  ['kiste','📦','Kistenprofi','je 100 Wörter im letzten Fach',()=>Math.floor(knFach5()/100)],
  ['unit','📜','Unit geschafft','alle Portionen einer Unit',()=>Object.keys(P.urk||{}).length]];
const vkTier=n=>n>=25?4:n>=10?3:n>=5?2:n>=1?1:0;
function vkBadgeCheck(){if(!KN||T)return;const st=knStreak(),today=dayKey();P.cnt=P.cnt||{};
  if(st>=5&&st%5===0&&P.cnt.serieTag!==today){P.cnt.serie=(P.cnt.serie||0)+1;P.cnt.serieTag=today}
  P.bdg=P.bdg||{};const up=[];BADGES.forEach(b=>{const n=b[4](),old=P.bdg[b[0]]||0;if(n>old){up.push([b,n]);P.bdg[b[0]]=n}});
  if(up.length&&vkBadgeReady){const b=up[0];later(()=>toast(`${b[0][1]} Abzeichen «${b[0][2]}»${b[1]>1?' ×'+b[1]:''}!`),900)}
  return up}
let vkBadgeReady=false;

/* Feier: neuer Sticker / neue Urkunde */
function vkCelebrate(got,urk){const L=$('#layer'),g=got[0];
  L.innerHTML=`<div class="scrim"></div><div class="dlg feier" role="dialog" aria-label="Geschafft">
    <p class="kick">${g?'Portion geschafft!':'Unit geschafft!'}</p>
    ${g?`<div class="stk big ${g.gold?'gold':''}">${picHTML(g.s.img)}</div><h2 class="lbl">${g.gold?'Ein goldener Sticker!':g.first?'Ein neuer Sticker!':'Den hast du jetzt doppelt!'}</h2>`:''}
    ${urk.length?`<p class="hand">📜 Neue Urkunde: «${esc(urk[0].name)}»</p>`:''}
    <div class="dact"><button class="pill" id="fzu">Weiter üben</button><button class="pill go" id="fheft">📒 Ins Heft</button></div></div>`;
  $('#fzu',L).onclick=()=>{L.innerHTML=''};$('.scrim',L).onclick=()=>{L.innerHTML=''};$('#fheft',L).onclick=()=>{L.innerHTML='';goHeft(urk.length&&!g?'urk':'stk')}}

/* Klassen-Ziel */
function vkZielHTML(teacher){const z=C.ziel;if(!z||!z.anzahl||!z.ab)return'';
  const n=teacher?KIDS.reduce((a,k)=>a+Object.entries((k.p&&k.p.sec)||{}).filter(([d,s])=>d>=z.ab&&s>=STAR_SEC).length,0):(((EXTRA.klasse||{}).sterne)||0);
  const pc=Math.min(100,Math.round(n/z.anzahl*100)),fertig=n>=z.anzahl;
  return `<div class="ziel ${fertig?'fertig':''}"><div class="zk"><span class="zt">${fertig?'🎉 Geschafft! ':''}Klassen-Ziel${z.belohnung?': '+esc(z.belohnung):''}</span><span class="zn">⭐ ${n} von ${z.anzahl}</span></div>
    <div class="zbar"><i style="width:${pc}%"></i></div><small>Alle Tagessterne der Klasse seit ${new Date(z.ab+'T12:00:00').toLocaleDateString('de-CH',{day:'numeric',month:'long'})} zählen zusammen.</small></div>`}

/* ---------- Heft ---------- */
/* Lehrperson: «Vorschau: so sieht ein volles Heft aus» (nichts wird gespeichert) */
let heftVor=false;
const FUNKEN=i=>`<i style="--x:${(i*29)%70+12}%;--y:${(i*47)%64+14}%;--d:${(i*0.37)%2.4}s"></i><i style="--x:${(i*53)%66+18}%;--y:${(i*31)%58+22}%;--d:${(i*0.61+1.1)%2.4}s"></i><i style="--x:${(i*17)%60+20}%;--y:${(i*71)%60+18}%;--d:${(i*0.23+0.6)%2.4}s"></i>`;
function goHeft(tab){stopSession();tab=tab||'stk';nav={view:'heft',tab};if(!heftVor)vkCheckAll(false);
  const list=stkList(),units=vkUnits(),V=heftVor;
  const stkOf=(s,i)=>V?{n:i%4===1?2:1,g:i%5===4?1:0}:(P.stk||{})[s.id];
  const bdgN=(b,i)=>V?[1,3,7,12,30,0,2,5,10,1,4,26][i%12]:b[4]();
  const urkT=u=>V?Date.now():(P.urk||{})[u.id];
  const own=list.filter((s,i)=>stkOf(s,i)),gold=list.reduce((a,s,i)=>a+((stkOf(s,i)||{}).g||0),0),bn=BADGES.filter((b,i)=>bdgN(b,i)>0).length;
  const prog=(n,m,txt)=>`<div class="hprog"><span>${txt}</span><div class="hpb"><i style="width:${m?Math.round(n/m*100):0}%"></i></div><b>${n} / ${m}</b></div>`;
  let body='';
  if(tab==='stk')body=`${prog(own.length,list.length,'Gesammelt'+(gold?' · <span class="gd">✦ '+gold+' mit Goldrand</span>':''))}
    <div class="album">${list.map((s,i)=>{const e=stkOf(s,i);
      return e?`<div class="stslot"><div class="stk ${e.g?'gold':''}" style="--r:${((i*37)%9)-4}deg">${picHTML(s.img)}</div>${e.n>1?`<span class="anz">×${e.n}</span>`:''}</div>`
        :`<div class="stslot zu" aria-label="Noch nicht gefunden"><div class="geheim">${FUNKEN(i+1)}<span class="fz">?</span></div></div>`}).join('')}</div>
    <p class="hfuss">Für jede geschaffte Portion klebst du einen neuen Sticker ein. Welcher es wird, ist eine Überraschung.</p>`;
  else if(tab==='bdg')body=`${prog(bn,BADGES.length,'Abzeichen')}
    <div class="badges">${BADGES.map((b,i)=>{const n=bdgN(b,i),t=vkTier(n);return `<div class="bdg t${t}"><div class="bi"><img src="abzeichen/${b[0]}.webp?v=2" alt="" draggable="false">${n>0?`<b class="bz">${n}</b>`:''}</div><span class="bn">${b[2]}</span><small>${b[3]}</small></div>`}).join('')}</div>
    <p class="hfuss">Viele Abzeichen bekommst du mehrmals. Ab 5, 10 und 25 werden sie grösser.</p>`;
  else body=`${prog(units.filter(u=>urkT(u)).length,units.length,'Urkunden')}
    <div class="urks">${units.length?units.map(u=>{const t=urkT(u);return `<button class="urk ${t?'':'leer'}" data-urk="${u.id}" ${t?'':'disabled'}>
      <span class="mini"><span class="mt">Urkunde</span><span class="ml"></span><span class="ml k"></span><span class="ms">${t?'✦':'🔒'}</span></span>
      <b>${esc(u.name)}</b><small>${t?new Date(t).toLocaleDateString('de-CH'):u.done+' von '+u.total+' Portionen'}</small></button>`}).join(''):'<p class="note">Noch keine Units.</p>'}</div>
    <p class="hfuss">Hast du in einer Unit alle Portionen geschafft, bekommst du eine Urkunde zum Ausdrucken.</p>`;
  const name=V?'Lena':KIDNAME;
  stage.innerHTML=`<div class="heft">
    ${CAN_EDIT?`<div class="hvor"><span>${V?'👁 Vorschau: So sieht ein volles Heft aus. Nichts davon wird gespeichert.':'Lehrperson: Möchtest du sehen, wie ein volles Heft aussieht?'}</span><button class="pill sm ${V?'rose':''}" id="hvorB">${V?'Vorschau beenden':'👁 Vorschau'}</button></div>`:''}
    <div class="hcover"><i class="hstich"></i><div class="hband"><i></i></div><i class="hribbon"></i>
      <span class="hdoo d1">✦</span><span class="hdoo d2">✧</span><span class="hdoo d3">♡</span><span class="hdoo d4">✦</span><span class="hdoo d5">☆</span><span class="hdoo d6">✧</span>
      <div class="hlabel"><i class="htape l"></i><i class="htape r"></i><span class="hk">✦ Vokabelkiste · ${esc(SUB().name)} ✦</span><span class="hn">${name?'Heft von '+esc(name):'Mein Heft'}</span><span class="hz"></span></div>
</div>
    ${vkZielHTML(false)}
    <div class="hbook"><div class="htabs" role="tablist">${[['stk','Sticker','sticker'],['bdg','Abzeichen','abzeichen'],['urk','Urkunden','urkunden']].map(([k,t,e])=>`<button class="htab h-${k} ${k===tab?'on':''}" data-ht="${k}" role="tab" aria-selected="${k===tab}"><img class="rt" src="abzeichen/reiter-${e}.webp?v=2" alt="" draggable="false">${t}</button>`).join('')}</div>
    <div class="hpage">${body}</div></div></div>`;
  $$('[data-ht]').forEach(b=>b.onclick=()=>goHeft(b.dataset.ht));
  const vb=$('#hvorB');if(vb)vb.onclick=()=>{heftVor=!heftVor;goHeft(tab)};
  $$('[data-urk]').forEach(b=>b.onclick=()=>vkUrkunde(units.find(u=>u.id===b.dataset.urk),V?'Lena':null));
  window.scrollTo(0,0)}

/* Urkunde (edel, zum Ausdrucken) */
function vkUrkunde(u,nameVor){if(!u)return;const t=(P.urk||{})[u.id]||Date.now(),L=$('#layer'),KIDNAME=nameVor||KIDNAME_;
  L.innerHTML=`<div class="scrim"></div><div class="urkwrap" role="dialog" aria-label="Urkunde"><div class="cert" id="cert">
    <div class="cr"><i></i><i></i><i></i><i></i></div>
    <img class="ceule" src="../bilder/eule.webp" alt="">
    <p class="ck">✦ Klassenkiste · Vokabelkiste ✦</p>
    <h2 class="ct">Urkunde</h2>
    <p class="cv">verliehen an</p>
    <p class="cn">${esc(KIDNAME||'…')}</p>
    <p class="cf">für das Lernen aller Wörter von</p>
    <p class="cu">«${esc(u.name)}»</p>
    <p class="cs">${esc(u.sub)} · ${u.total} Portionen · ${u.words} Wörter</p>
    <div class="cfoot"><span>${new Date(t).toLocaleDateString('de-CH',{day:'numeric',month:'long',year:'numeric'})}</span><span class="siegel">✦</span><span>Unterschrift</span></div>
  </div><div class="dact"><button class="pill" id="uzu">Schliessen</button><button class="pill go" id="udr">🖨 Drucken</button></div></div>`;
  const zu=()=>{L.innerHTML='';document.body.classList.remove('drucke')};
  $('#uzu',L).onclick=zu;$('.scrim',L).onclick=zu;
  $('#udr',L).onclick=()=>{vkPage('landscape');document.body.classList.add('drucke');setTimeout(()=>{try{window.print()}catch(e){}setTimeout(()=>document.body.classList.remove('drucke'),500)},50)}}

/* ---------- Lehrperson: Belohnungen in der Klassen-Übersicht ---------- */
function vkClassRewards(){const m=stkModes(),z=C.ziel||{};
  return `<div class="sh"><h2 class="lbl">Belohnungen</h2><p class="hand">Gilt für diese Klasse.</p></div>
  <div class="rewards">
    <div class="rw"><h3>Klassen-Ziel</h3>${vkZielHTML(true)||'<p class="note">Noch kein Ziel.</p>'}
      <div class="rwf"><label>Tagessterne<input class="inp" id="zAnz" type="number" min="1" max="99999" value="${esc(z.anzahl||'')}" placeholder="z. B. 200"></label>
      <label>Belohnung<input class="inp" id="zBel" maxlength="80" value="${esc(z.belohnung||'')}" placeholder="z. B. Filmnachmittag"></label>
      <label>Zählt ab<input class="inp" id="zAb" type="date" value="${esc(z.ab||dayKey())}"></label></div>
      <div class="actions" style="justify-content:flex-start"><button class="pill go" id="zSave">Ziel speichern</button>${z.anzahl?'<button class="pill" id="zDel">Ziel entfernen</button>':''}</div></div>
    <div class="rw"><h3>Welche Übungen zählen für die Sticker?</h3><p class="note" style="margin-top:0">Eine Portion ist geschafft, wenn die angekreuzten Übungen gemacht sind. Übt die Klasse z. B. nur mündlich, nimm die schriftlichen weg.</p>
      <div class="rwm">${ALL_MODES.map(k=>`<label class="kbx"><input type="checkbox" data-sm="${k}" ${m.includes(k)?'checked':''}> ${esc(MODE_NAMES[k]||k)}</label>`).join('')}</div>
      <div class="actions" style="justify-content:flex-start"><button class="pill go" id="smSave">Speichern</button></div></div>
    ${KN_ADMIN?`<div class="rw"><h3>Sticker (für alle Klassen)</h3><p class="note" style="margin-top:0">Nur du als Admin. Bilder oder eine ZIP-Datei hochladen. Sie liegen geschützt in der Klassenkiste.</p>
      <div class="stkadm">${STK.map(s=>`<div class="stka"><div class="stk">${picHTML('vk:'+s.id)}</div><button class="del" data-sdel="${esc(s.id)}" aria-label="Sticker entfernen">✕</button></div>`).join('')||'<p class="note">Noch keine eigenen Sticker (zurzeit Tier-Emojis).</p>'}</div>
      <div class="actions" style="justify-content:flex-start"><label class="pill go"><input type="file" accept="image/*,.zip" multiple hidden id="stkUp">🧩 Sticker hochladen</label></div></div>`:''}
  </div>`}
function bindClassRewards(){
  const zs=$('#zSave');if(zs)zs.onclick=()=>{const a=parseInt($('#zAnz').value,10);if(!(a>0)){toast('Bitte eine Zahl bei «Tagessterne» eingeben.');return}
    C.ziel={anzahl:a,belohnung:$('#zBel').value.trim().slice(0,80),ab:/^\d{4}-\d{2}-\d{2}$/.test($('#zAb').value)?$('#zAb').value:dayKey()};touch();publishContent(null);goClass()};
  const zd=$('#zDel');if(zd)zd.onclick=()=>{delete C.ziel;touch();publishContent(null);goClass()};
  const sm=$('#smSave');if(sm)sm.onclick=()=>{const m=$$('[data-sm]').filter(c=>c.checked).map(c=>c.dataset.sm);if(!m.length){toast('Mindestens eine Übung ankreuzen.');return}
    C.belohnung=Object.assign({},C.belohnung||{},{modes:m});touch();publishContent(null);toast('Gespeichert');goClass()};
  $$('[data-sdel]').forEach(b=>b.onclick=async()=>{const nl=STK.filter(s=>s.id!==b.dataset.sdel);try{await knAsk('vkSticker',{data:{list:nl}});STK=nl;goClass()}catch(e){toast(e.message)}});
  const up=$('#stkUp');if(up)up.onchange=async()=>{const fs=[...up.files];up.value='';const files=await vkReadFiles(fs);if(!files)return;let nl=STK.slice(),n=0;
    files.sort((a,b)=>a.name.localeCompare(b.name,'de',{numeric:true}));
    for(const x of files){try{const v=await vkStore(await picFromFile(x.blob,560));nl.push({id:v.slice(3),name:x.name.replace(/\.[^.]+$/,'')});n++;toast('Sticker '+n+' von '+files.length+' …')}catch(e){}}
    try{await knAsk('vkSticker',{data:{list:nl}});STK=nl;toast(n+' Sticker gespeichert');goClass()}catch(e){toast(e.message)}}}
const vkStkN=p=>Object.values((p&&p.stk)||{}).reduce((a,e)=>a+(e.n||0),0);

/* ---------- Viele Bilder auf einmal (auch als ZIP) ---------- */
async function unzipImgs(file){const buf=new Uint8Array(await file.arrayBuffer()),dv=new DataView(buf.buffer);let e=-1;
  for(let i=buf.length-22;i>=Math.max(0,buf.length-65557);i--){if(dv.getUint32(i,true)===0x06054b50){e=i;break}}
  if(e<0)throw new Error('zip');const cnt=dv.getUint16(e+10,true),td=new TextDecoder();let p=dv.getUint32(e+16,true);const out=[];
  for(let n=0;n<cnt;n++){if(dv.getUint32(p,true)!==0x02014b50)break;
    const meth=dv.getUint16(p+10,true),csz=dv.getUint32(p+20,true),nl=dv.getUint16(p+28,true),xl=dv.getUint16(p+30,true),cl=dv.getUint16(p+32,true),off=dv.getUint32(p+42,true);
    const name=td.decode(buf.subarray(p+46,p+46+nl));p+=46+nl+xl+cl;
    const base=name.replace(/^.*\//,''),ext=(base.match(/\.(png|jpe?g|webp|gif)$/i)||[])[1];
    if(!ext||/(^|\/)__MACOSX\//.test(name)||base.startsWith('.'))continue;
    const st=off+30+dv.getUint16(off+26,true)+dv.getUint16(off+28,true),raw=buf.subarray(st,st+csz),type='image/'+(ext.toLowerCase()==='jpg'?'jpeg':ext.toLowerCase());
    let blob;if(meth===0)blob=new Blob([raw],{type});
    else if(meth===8){if(!window.DecompressionStream)throw new Error('zip');blob=new Blob([await new Response(new Blob([raw]).stream().pipeThrough(new DecompressionStream('deflate-raw'))).arrayBuffer()],{type})}
    else continue;out.push({name:base,blob})}
  return out}
async function vkReadFiles(fs){let out=[];
  for(const f of fs){if(/\.zip$/i.test(f.name)||/zip/.test(f.type)){try{out=out.concat(await unzipImgs(f))}catch(e){toast('Die ZIP-Datei lässt sich auf diesem Gerät nicht öffnen. Wähl die Bilder direkt aus.');return null}}
    else if(/^image\//.test(f.type))out.push({name:f.name,blob:f})}
  if(!out.length){toast('Keine Bilder gefunden.');return null}return out}
const fileKey=t=>String(t||'').toLowerCase().normalize('NFC').replace(/[’‘ʼ`´]/g,"'").replace(/[^\p{L}\p{N}]/gu,'');
function bindBulk(node,redraw){const inp=$('#bulkPic');if(!inp)return;inp.onchange=async()=>{const fs=[...inp.files];inp.value='';if(!fs.length)return;
  toast('Bilder werden gelesen …');const files=await vkReadFiles(fs);if(!files)return;let ok=0;const miss=[];
  for(const x of files){const k=fileKey(x.name.replace(/\.[^.]+$/,''));
    const w=node.words.find(w=>fileKey(w.f)===k||fileKey(w.de)===k||String(w.f).split(/\s*[\/;,]\s*/).some(a=>fileKey(a)===k));
    if(!w){miss.push(x.name);continue}
    try{w.img=await vkStore(await picFromFile(x.blob));ok++;toast('Bild '+ok+' gespeichert …')}catch(e){miss.push(x.name+' (Fehler: '+e.message+')')}}
  if(ok){touch();redraw()}
  const L=$('#layer');L.innerHTML=`<div class="scrim"></div><div class="dlg"><h2 class="lbl">${ok} ${ok===1?'Bild':'Bilder'} eingefügt</h2><p class="note" style="margin:0">Gespeichert in hoher Qualität (800 px).</p>
    ${miss.length?`<p>Diese passen zu keinem Wort dieser Portion. Der Dateiname muss gleich heissen wie das Wort:</p><ul class="miss">${miss.map(m=>`<li>${esc(m)}</li>`).join('')}</ul>`:'<p>Alle Bilder haben ein Wort gefunden.</p>'}
    ${ok?'<p class="note">Vergiss nicht: unten «Für die Klasse veröffentlichen».</p>':''}<div class="dact"><button class="pill go" id="bok">OK</button></div></div>`;
  $('#bok',L).onclick=()=>{L.innerHTML=''};$('.scrim',L).onclick=()=>{L.innerHTML=''}}}

/* Kachel «Mein Heft» auf der Startseite der Sprache */
function vkHeftCard(){const list=stkList(),st=list.filter(s=>(P.stk||{})[s.id]).length,bd=BADGES.filter(b=>b[4]()>0).length,ur=Object.keys(P.urk||{}).length;
  return `<button type="button" class="kt kt-heft" id="heftCard"><span class="mh" aria-hidden="true"><i></i></span>
    <span class="ktx"><b>Mein Heft</b><span class="mhz"><span><img src="abzeichen/reiter-sticker.webp?v=2" alt="">${st}/${list.length}</span><span><img src="abzeichen/reiter-abzeichen.webp?v=2" alt="">${bd}</span><span><img src="abzeichen/reiter-urkunden.webp?v=2" alt="">${ur}</span></span><small>Sticker, Abzeichen und Urkunden anschauen →</small></span></button>`}
document.addEventListener('click',e=>{const b=e.target.closest&&e.target.closest('#heftCard');if(b)goHeft()});
