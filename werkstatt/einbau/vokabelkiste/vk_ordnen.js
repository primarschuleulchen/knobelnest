/* ---------- Knobelnest: Portionen/Ordner duplizieren und verschieben (Lehrperson) ---------- */
const vkArr=id=>{const i=NODES.get(id);return !i?null:i.parent?(i.parent.kids=i.parent.kids||[]):i.sub.tree};
/* Kopie gleich hinter dem Original, mit neuen IDs (eigener Fortschritt), für die Kinder zuerst gesperrt */
function vkDup(id){const i=NODES.get(id);if(!i)return;const s=i.sub,ex=new Set(s.excl),arr=vkArr(id);
  const cp=JSON.parse(JSON.stringify(i.node));
  const neu=n=>{n.id=uid();delete n.tpl;(n.words||[]).forEach(w=>{const old=w.id;w.id=uid();delete w.imgT;if(ex.has(old))s.excl.push(w.id)});(n.kids||[]).forEach(neu)};
  neu(cp);cp.name=i.node.name+' (Kopie)';cp.open=false;arr.splice(arr.indexOf(i.node)+1,0,cp);
  touch();toast('Kopie erstellt. Sie ist für die Kinder noch gesperrt.');goNode(cp.id)}
/* In einen anderen Ordner (oder ganz nach oben) verschieben; nie in sich selbst */
function vkMove(id){const i=NODES.get(id);if(!i)return;const s=i.sub,L=$('#layer');
  const rows=[];const walk=(arr,d)=>arr.forEach(n=>{if(n.words||n.id===id)return;rows.push({n,d});walk(n.kids||[],d+1)});walk(s.tree,0);
  const cur=i.parent?i.parent.id:'';
  L.innerHTML=`<div class="scrim"></div><div class="dlg mvdlg" role="dialog" aria-label="Verschieben"><h2 class="lbl">«${esc(i.node.name)}» verschieben</h2>
    <p class="note" style="margin:0">Wähl den Ordner, in den ${i.node.words?'die Portion':'der Ordner'} kommen soll.</p>
    <div class="mvlist"><button class="mvo ${cur===''?'cur':''}" data-to="">🏠 ${esc(s.name)} (ganz oben)</button>${rows.map(r=>`<button class="mvo ${r.n.id===cur?'cur':''}" data-to="${r.n.id}" style="padding-left:${14+r.d*22}px">📁 ${esc(r.n.name)}</button>`).join('')}</div>
    <div class="dact"><button class="pill" id="mvX">Abbrechen</button></div></div>`;
  const zu=()=>{L.innerHTML=''};$('#mvX',L).onclick=zu;$('.scrim',L).onclick=zu;
  $$('[data-to]',L).forEach(b=>b.onclick=()=>{const to=b.dataset.to;if(to===cur){zu();return}
    const from=vkArr(id),ziel=to?NODES.get(to).node:null;from.splice(from.indexOf(i.node),1);
    (ziel?(ziel.kids=ziel.kids||[]):s.tree).push(i.node);
    zu();touch();toast('Verschoben nach «'+(ziel?ziel.name:s.name)+'»');goNode(id)})}
