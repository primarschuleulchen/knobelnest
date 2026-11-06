/* ---------- Knobelnest: Arbeitsblatt- und Test-Generator (nur Lehrperson) ----------
   Aus den Wörtern der Portion (SET.words) entsteht ein A4-Blatt zum Drucken: Arbeitsblatt oder Test, Aufgaben wählbar,
   mit oder ohne Bilder, Version A/B (anders gemischt), auf Wunsch mit Lösungsblatt. Nichts wird gespeichert. */
const WSA=[ /* [Schlüssel, Name, Aufgabentext] */
  ['de','Übersetzen Deutsch → Fremdsprache','Schreib auf {S}.'],
  ['fl','Übersetzen Fremdsprache → Deutsch','Schreib auf Deutsch.'],
  ['bild','Bilder beschriften','Schreib das Wort auf {S} unter das Bild.'],
  ['verb','Verbinden','Verbinde, was zusammengehört.'],
  ['salat','Buchstabensalat','Ordne die Buchstaben. Schreib das Wort richtig.'],
  ['luecke','Lückensätze','Setz das passende Wort ein.'],
  ['suche','Wörter-Suchrätsel','Such die Wörter auf {S}. Sie stehen waagrecht oder senkrecht.']];
let WS=null;
const vkPage=sz=>{let st=document.getElementById('pgsz');if(!st){st=document.createElement('style');st.id='pgsz';document.head.appendChild(st)}st.textContent='@page{size:A4 '+sz+';margin:'+(sz==='landscape'?'12mm':'14mm')+'}'};

function wsRng(seed){let a=seed>>>0;return()=>{a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}}
const wsMix=(arr,r)=>{const a=arr.slice();for(let i=a.length-1;i>0;i--){const j=Math.floor(r()*(i+1));[a[i],a[j]]=[a[j],a[i]]}return a};
const wsF=w=>String(w.f||'').replace(/\s*\[|\]\s*/g,' ').trim();
function wsTools(){return '<button class="pill tool" id="wsBtn">🖨 Arbeitsblatt / Test</button>'+(noSent()?'':'<button class="pill tool" id="gapReview">✏️ Lückensätze prüfen</button>')}
function goWs(){
  const ws=SET.words.filter(valid);if(!ws.length){toast('Hier gibt es keine Wörter.');return}
  if(!WS||WS.key!==SET.key)WS={key:SET.key,typ:'blatt',titel:SET.label||'',bilder:ws.some(bildOK),ver:'A',n:10,loes:true,seed:Math.random()*1e9|0,
    tasks:{de:true,fl:false,bild:ws.filter(bildOK).length>=3,verb:true,salat:false,luecke:ws.some(gapOK),suche:false}};
  if(nav.view!=='ws')lastBack=makeBack(nav);
  stopSession();nav={view:'ws'};wsRender();window.scrollTo(0,0)}
function wsRender(){const ws=SET.words.filter(valid),s=SUB(),W=WS;
  const opt=(k,label,dis,hint)=>`<label class="kbx ${dis?'off':''}"><input type="checkbox" data-wt="${k}" ${W.tasks[k]&&!dis?'checked':''} ${dis?'disabled':''}> ${label}${hint?` <small>${hint}</small>`:''}</label>`;
  const nB=ws.filter(bildOK).length,nG=ws.filter(gapOK).length,nS=ws.filter(w=>salatOf(wsF(w))).length;
  stage.innerHTML=`<div class="stop"><button class="pill" id="wsBack">← Zurück</button><div class="t"><div class="eyebrow">${esc(s.name)} · ${esc(SET.label)}</div><h1 class="big mid">Arbeitsblatt &amp; Test</h1></div></div>
  <div class="wsg"><aside class="wsset">
    <div class="seg ws-typ" role="group"><button data-wtyp="blatt" aria-pressed="${W.typ==='blatt'}">📝 Arbeitsblatt</button><button data-wtyp="test" aria-pressed="${W.typ==='test'}">✅ Test</button></div>
    <label class="wsl">Titel<input class="inp" id="wsTitel" value="${esc(W.titel)}" maxlength="80"></label>
    <div class="wsl">Aufgaben</div>
    <div class="wsopts">${opt('de','Deutsch → '+esc(s.name))}${opt('fl',esc(s.name)+' → Deutsch')}${opt('bild','Bilder beschriften',nB<2,nB<2?'(zu wenige Bilder)':'')}${opt('verb','Verbinden')}
      ${opt('salat','Buchstabensalat',!nS)}${opt('luecke','Lückensätze',!nG||noSent(),!nG?'(keine Sätze)':'')}${opt('suche','Wörter-Suchrätsel')}</div>
    <label class="wsl">Wörter pro Aufgabe<select class="inp" id="wsN">${[5,8,10,12,15,99].map(n=>`<option value="${n}" ${W.n===n?'selected':''}>${n===99?'alle ('+ws.length+')':n}</option>`).join('')}</select></label>
    <label class="kbx"><input type="checkbox" id="wsBild" ${W.bilder?'checked':''}> Bilder neben die Wörter</label>
    <label class="kbx"><input type="checkbox" id="wsLoes" ${W.loes?'checked':''}> Lösungsblatt dazu</label>
    <div class="wsl">Version</div>
    <div class="seg" role="group"><button data-wver="A" aria-pressed="${W.ver==='A'}">A</button><button data-wver="B" aria-pressed="${W.ver==='B'}">B</button></div>
    <p class="note" style="margin:0">Version B hat dieselben Aufgaben, aber anders gemischt. So schreiben Banknachbarn nicht ab.</p>
    <div class="actions" style="justify-content:flex-start"><button class="pill" id="wsMix">🔀 Neu mischen</button><button class="pill go" id="wsPrint">🖨 Drucken / PDF</button></div>
    <p class="note" style="margin:0">Im Druckfenster kannst du auch «Als PDF sichern» wählen.</p>
  </aside><div class="wsprev" id="wsPrev">${wsPages(false)}${W.loes?wsPages(true):''}</div></div>`;
  $('#wsBack').onclick=()=>lastBack();
  $$('[data-wtyp]').forEach(b=>b.onclick=()=>{W.typ=b.dataset.wtyp;if(W.typ==='test')W.tasks.suche=false;wsRender()});
  $$('[data-wver]').forEach(b=>b.onclick=()=>{W.ver=b.dataset.wver;wsRender()});
  $$('[data-wt]').forEach(c=>c.onchange=()=>{W.tasks[c.dataset.wt]=c.checked;wsRender()});
  $('#wsTitel').oninput=e=>{W.titel=e.target.value;$$('.wsp-t').forEach(x=>x.textContent=W.titel)};
  $('#wsN').onchange=e=>{W.n=+e.target.value;wsRender()};
  $('#wsBild').onchange=e=>{W.bilder=e.target.checked;wsRender()};
  $('#wsLoes').onchange=e=>{W.loes=e.target.checked;wsRender()};
  $('#wsMix').onclick=()=>{W.seed=Math.random()*1e9|0;wsRender()};
  $('#wsPrint').onclick=()=>{vkPage('portrait');document.body.classList.add('wsdruck');setTimeout(()=>{try{window.print()}catch(e){}setTimeout(()=>document.body.classList.remove('wsdruck'),600)},120)};
  wsZoom()}
function wsZoom(){const p=$('#wsPrev');if(!p)return;const z=Math.min(1,(p.clientWidth-8)/794);$$('.wsp',p).forEach(x=>x.style.zoom=z)}
addEventListener('resize',()=>{if(nav.view==='ws')wsZoom()});
/* Ein Blatt (oder das Lösungsblatt) */
function wsPages(L){const W=WS,s=SUB(),all=SET.words.filter(valid),r=wsRng(W.seed+(W.ver==='B'?7919:0));
  const pick=list=>wsMix(list,r).slice(0,W.n);
  const bild=w=>W.bilder&&picOf(w)?`<span class="wsb">${picHTML(picOf(w))}</span>`:'';
  const line=ans=>`<span class="wsline">${L?`<em>${esc(ans)}</em>`:''}</span>`;
  const pts=n=>W.typ==='test'?`<span class="wspt">___ / ${n}</span>`:'';
  let nr=0,tot=0;const blocks=[];
  const task=(k,body,n)=>{nr++;tot+=n;const t=WSA.find(x=>x[0]===k);blocks.push(`<section class="wst"><h3><b>${nr}</b> ${esc(t[2].replace('{S}',s.name))}${pts(n)}</h3>${body}</section>`)};
  if(W.tasks.de){const l=pick(all);task('de',`<div class="wsrows">${l.map(w=>`<div class="wsr">${bild(w)}<span class="wsq">${esc(w.de)}</span>${line(wsF(w))}</div>`).join('')}</div>`,l.length)}
  if(W.tasks.fl){const l=pick(all);task('fl',`<div class="wsrows">${l.map(w=>`<div class="wsr">${bild(w)}<span class="wsq">${esc(wsF(w))}</span>${line(w.de)}</div>`).join('')}</div>`,l.length)}
  if(W.tasks.bild){const l=pick(all.filter(bildOK));if(l.length>=2)task('bild',`<div class="wsbg">${l.map(w=>`<div class="wsbc"><span class="wsbb">${picHTML(picOf(w))}</span>${line(wsF(w))}</div>`).join('')}</div>`,l.length)}
  if(W.tasks.verb){const l=pick(all).slice(0,Math.min(W.n,10)),rr=wsMix(l,r);
    task('verb',`<div class="wsv"><div>${l.map((w,i)=>`<div class="wsvr"><span>${esc(wsF(w))}</span><i class="dot"></i></div>`).join('')}</div>
      <div>${rr.map(w=>`<div class="wsvr r"><i class="dot"></i><span>${esc(w.de)}${L?` <em>(${l.indexOf(w)+1})</em>`:''}</span></div>`).join('')}</div></div>
      ${L?`<p class="wsnote">Lösung: Die Zahl zeigt, zu welchem Wort links (von oben gezählt) es gehört.</p>`:''}`,l.length)}
  if(W.tasks.salat){const l=pick(all.filter(w=>salatOf(wsF(w))));if(l.length)task('salat',`<div class="wsrows">${l.map(w=>{const t=salatOf(wsF(w)),ch=[...t.replace(/\s+/g,'')];let m=wsMix(ch,r);for(let i=0;i<5&&m.join('')===ch.join('');i++)m=wsMix(ch,r);
      return `<div class="wsr">${bild(w)}<span class="wsq salat">${esc(m.join(' ').toLowerCase())}</span>${line(t)}</div>`}).join('')}</div>`,l.length)}
  if(W.tasks.luecke&&!noSent()){const l=pick(all.filter(gapOK));if(l.length){const bank=wsMix(l.map(w=>gapOf(w).word),r);
    task('luecke',`${W.typ==='blatt'?`<div class="wsbank">${bank.map(x=>`<span>${esc(x)}</span>`).join('')}</div>`:''}<div class="wsgaps">${l.map((w,i)=>{const g=gapOf(w);
      return `<p>${i+1}. ${esc(cleanS(g.before))}<span class="wsgap">${L?`<em>${esc(g.word)}</em>`:''}</span>${esc(cleanS(g.after))}</p>`}).join('')}</div>`,l.length)}}
  if(W.tasks.suche&&W.typ==='blatt'){const z=wsSuche(all,r);if(z.words.length)task('suche',`<div class="wss"><table class="wsgrid">${z.grid.map((row,y)=>`<tr>${row.map((c,x)=>`<td class="${L&&z.hit[y][x]?'hit':''}">${c}</td>`).join('')}</tr>`).join('')}</table>
      <div class="wssl"><b>Finde:</b>${z.words.map(w=>`<span>${esc(w.de)}${L?` = <em>${esc(w.f2)}</em>`:''}</span>`).join('')}</div></div>`,0)}
  const kopf=`<header class="wsh"><div><span class="wsp-k">${esc(s.name)} · ${W.typ==='test'?'Test':'Arbeitsblatt'}${W.ver==='B'?' · Version B':''}${L?' · Lösung':''}</span><h2 class="wsp-t">${esc(W.titel)}</h2></div>
    <div class="wsf"><span>Name: <i></i></span><span>Datum: <i></i></span>${W.typ==='test'?`<span>Punkte: <i class="k"></i> / ${tot}</span>`:''}</div></header>`;
  return `<div class="wsp ${L?'loes':''}">${kopf}${blocks.join('')||'<p class="note">Wähl links mindestens eine Aufgabe.</p>'}<footer class="wsfoot">Klassenkiste · Vokabelkiste</footer></div>`}
/* Wörter-Suchrätsel: nur Wörter aus Buchstaben (ohne Leerzeichen), höchstens 12 lang; waagrecht und senkrecht */
function wsSuche(all,r){const N=12,g=[...Array(N)].map(()=>Array(N).fill('')),hit=[...Array(N)].map(()=>Array(N).fill(false)),words=[];
  const cand=wsMix(all,r).map(w=>{const t=String(w.f||'').replace(/\([^)]*\)/g,'').split(/[\/,;]/)[0].trim().replace(ARTRE,'').replace(/^to\s+/i,'').trim();
    return {w,t:t.toUpperCase().normalize('NFC')}}).filter(x=>/^[\p{L}]{3,12}$/u.test(x.t));
  for(const c of cand){if(words.length>=10)break;let ok=false;
    for(let tries=0;tries<80&&!ok;tries++){const d=r()<.5?[1,0]:[0,1],L=c.t.length,x0=Math.floor(r()*((d[0]?N-L:N-1)+1)),y0=Math.floor(r()*((d[1]?N-L:N-1)+1));
      if(x0+(d[0]?L-1:0)>=N||y0+(d[1]?L-1:0)>=N)continue;let fit=true;
      for(let i=0;i<L;i++){const ch=g[y0+d[1]*i][x0+d[0]*i];if(ch&&ch!==c.t[i]){fit=false;break}}
      if(!fit)continue;for(let i=0;i<L;i++){g[y0+d[1]*i][x0+d[0]*i]=c.t[i];hit[y0+d[1]*i][x0+d[0]*i]=true}ok=true}
    if(ok)words.push({de:c.w.de,f2:c.t.toLowerCase()})}
  const AB='ABCDEFGHIJKLMNOPRSTUVWY';for(let y=0;y<N;y++)for(let x=0;x<N;x++)if(!g[y][x])g[y][x]=AB[Math.floor(r()*AB.length)];
  return {grid:g,hit,words}}
