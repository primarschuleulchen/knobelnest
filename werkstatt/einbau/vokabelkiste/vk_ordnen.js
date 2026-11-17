/* ---------- Knobelnest: Portionen/Ordner duplizieren und verschieben (Lehrperson) ---------- */
const vkArr=id=>{const i=NODES.get(id);return !i?null:i.parent?(i.parent.kids=i.parent.kids||[]):i.sub.tree};
/* Kopie gleich hinter dem Original, mit neuen IDs (eigener Fortschritt), für die Kinder zuerst gesperrt */
function vkDup(id){const i=NODES.get(id);if(!i)return;const s=i.sub,ex=new Set(s.excl),arr=vkArr(id);
  const cp=JSON.parse(JSON.stringify(i.node));
  const neu=n=>{n.id=uid();delete n.tpl;(n.words||[]).forEach(w=>{const old=w.id;w.id=uid();delete w.imgT;if(ex.has(old))s.excl.push(w.id)});(n.kids||[]).forEach(neu)};
  neu(cp);cp.name=i.node.name+' (Kopie)';cp.open=false;arr.splice(arr.indexOf(i.node)+1,0,cp);
  touch();toast('Kopie erstellt. Sie ist für die Kinder noch gesperrt.');goNode(cp.id)}
/* In einen anderen Ordner (oder ganz nach oben) verschieben; nie in sich selbst. Unten: neuen Ordner erstellen und gleich hinein.
   back = was danach angezeigt wird (aus der Ordner-Ansicht: dort bleiben), sonst die verschobene Portion. */
function vkMove(id,back){const i=NODES.get(id);if(!i)return;const s=i.sub,L=$('#layer');
  const rows=[];const walk=(arr,d)=>arr.forEach(n=>{if(n.words||n.id===id)return;rows.push({n,d});walk(n.kids||[],d+1)});walk(s.tree,0);
  const cur=i.parent?i.parent.id:'';
  L.innerHTML=`<div class="scrim"></div><div class="dlg mvdlg" role="dialog" aria-label="Verschieben"><h2 class="lbl">«${esc(i.node.name)}» verschieben</h2>
    <p class="note" style="margin:0">Wähl den Ordner, in den ${i.node.words?'die Portion':'der Ordner'} kommen soll.</p>
    <div class="mvlist"><button class="mvo ${cur===''?'cur':''}" data-to="">🏠 ${esc(s.name)} (ganz oben)</button>${rows.map(r=>`<button class="mvo ${r.n.id===cur?'cur':''}" data-to="${r.n.id}" style="padding-left:${14+r.d*22}px">📁 ${esc(r.n.name)}</button>`).join('')}</div>
    <div class="mvnew"><b>Oder neuer Ordner:</b><input class="inp" id="mvName" placeholder="Name, z. B. Unit 3" maxlength="60">
      <label>in <select class="inp" id="mvIn"><option value="">${esc(s.name)} (ganz oben)</option>${rows.map(r=>`<option value="${r.n.id}" ${r.n.id===cur?'selected':''}>${'– '.repeat(r.d+1)}${esc(r.n.name)}</option>`).join('')}</select></label>
      <button class="pill go" id="mvNew">Erstellen und verschieben</button></div>
    <div class="dact"><button class="pill" id="mvX">Abbrechen</button></div></div>`;
  const zu=()=>{L.innerHTML=''};$('#mvX',L).onclick=zu;$('.scrim',L).onclick=zu;
  const done=ziel=>{zu();touch();toast('Verschoben nach «'+(ziel?ziel.name:s.name)+'»');if(back)back();else goNode(id)};
  const take=()=>{const from=vkArr(id);from.splice(from.indexOf(i.node),1)};
  $$('[data-to]',L).forEach(b=>b.onclick=()=>{const to=b.dataset.to;if(to===cur){zu();return}
    const ziel=to?NODES.get(to).node:null;take();(ziel?(ziel.kids=ziel.kids||[]):s.tree).push(i.node);done(ziel)});
  $('#mvName',L).onkeydown=e=>{if(e.key==='Enter')$('#mvNew',L).click()};
  $('#mvNew',L).onclick=()=>{const nm=$('#mvName',L).value.trim();if(!nm){toast('Bitte zuerst einen Namen für den neuen Ordner eingeben.');$('#mvName',L).focus();return}
    const pid=$('#mvIn',L).value,par=pid?NODES.get(pid).node:null,arr=par?(par.kids=par.kids||[]):s.tree;
    const f={id:uid(),name:nm,kids:[],open:isOpen(i.node)};arr.push(f);take();f.kids.push(i.node);done(f)}}
/* Ordnerfarbe (Lehrperson): n.farbe = Schlüssel aus FFARBEN; ohne eigene Farbe gilt die des nächsten oberen Ordners */
const FFARBEN=[['blau','#dcf0fd','Hellblau'],['gruen','#e4f1da','Grün'],['mint','#d8f1ea','Mint'],['gelb','#fbf0cc','Gelb'],['orange','#fde3cc','Orange'],['rosa','#fbe0e5','Rosa'],['lila','#e9e0f7','Lila'],['grau','#ebebe8','Grau']];
function vkFc(n){let i=NODES.get(n.id);while(i){const f=i.node.farbe&&FFARBEN.find(x=>x[0]===i.node.farbe);if(f)return f[1];i=i.parent?NODES.get(i.parent.id):null}return ''}
const vkFcStyle=n=>{const c=vkFc(n);return c?` style="--fc:${c}"`:''};
function vkFarbe(id,back){const i=NODES.get(id);if(!i)return;const n=i.node,L=$('#layer');
  L.innerHTML=`<div class="scrim"></div><div class="dlg fcdlg" role="dialog" aria-label="Farbe"><h2 class="lbl">Farbe für «${esc(n.name)}»</h2>
    <p class="note" style="margin:0">Ordner darin ohne eigene Farbe bekommen dieselbe Farbe.</p>
    <div class="fcwahl">${FFARBEN.map(([k,c,t])=>`<button class="fcs ${n.farbe===k?'on':''}" data-fc="${k}" style="--fc:${c}" title="${t}"><span></span>${t}</button>`).join('')}
      <button class="fcs auto ${n.farbe?'':'on'}" data-fc=""><span></span>Automatisch</button></div>
    <div class="dact"><button class="pill" id="fcX">Abbrechen</button></div></div>`;
  const zu=()=>{L.innerHTML=''};$('#fcX',L).onclick=zu;$('.scrim',L).onclick=zu;
  $$('[data-fc]',L).forEach(b=>b.onclick=()=>{const k=b.dataset.fc;if(k)n.farbe=k;else delete n.farbe;zu();touch();toast('Farbe gespeichert');if(back)back()})}
