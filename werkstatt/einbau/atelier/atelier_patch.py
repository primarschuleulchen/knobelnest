# Atelier -> Knobelnest (atelier.html). Aufruf: python3 atelier_patch.py <Atelier/index.html> <ziel/atelier.html>
import sys
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    assert c == n, ('Anzahl %d statt %d: ' % (c, n)) + a[:90]
    s = s.replace(a, b)

# 1) Bilder mit eindeutigen Namen (liegen in der Klassenkiste neben den anderen Dateien)
rep('url(plan-full.webp)', 'url(atelier-plan.webp)')
rep('url(bike-halo.png)', 'url(atelier-bike-halo.png)', 2)
rep('url(bike-lines.png)', 'url(atelier-bike-lines.png)', 2)

# 2) Leiste: Zurück, Riegel für die Kinder, Hinweis; «+ Kind» entfällt (Namen kommen aus der Klassenkiste)
rep('''  <div class="top">
    <div class="sp"></div>''', '''  <div class="top">
    <button class="pill" id="knBack" type="button" hidden>← Klassenkiste</button>
    <span class="khint" id="kHint" hidden></span>
    <div class="sp"></div>''')
rep('''    <button class="pill" id="btnPaste" type="button">Liste einfügen</button>''',
    '''    <button class="toggle" id="tgOpen" type="button" role="switch" aria-checked="false" hidden title="Wenn offen, können die Kinder Thema und Umsetzungsart selbst ändern">Kinder dürfen Text ändern<span class="track"></span></button>
    <button class="pill" id="btnPaste" type="button">Liste einfügen</button>''')
rep('.sp{flex:1}\n.status{', r'''.sp{flex:1}
.khint{font-size:14px;font-weight:700;color:#4f7a3c;background:rgba(255,255,255,.85);border:1px solid var(--line);border-radius:999px;padding:7px 14px}
.kid.me{box-shadow:0 0 0 3px var(--c);background:color-mix(in srgb,var(--c) 7%,#fff)}
.kidmode .f-stufe{display:none}
.kidmode .bike.locked{cursor:default}
.kidmode .kid.other{cursor:default}
.kidmode .kid.other:hover{background:none}
.dlg input[readonly]{background:#f1f2ee;color:var(--muted)}
.dlg input:disabled{opacity:.55}
.dlg .lockmsg{font-size:13px;color:var(--muted);margin:-4px 0 0;text-align:center}
.status{''')

# 3) Speicher über das Knobelnest (Lehrperson: einzelne Kinder; Kind: nur das eigene Velo)
rep('''let kids=[]; // {id,name,thema,umsetzung,stufe,farbe,x,y,order}
let store=null;''', r'''let kids=[]; // {id,name,thema,umsetzung,stufe,farbe,x,y,order}
let store=null;
// Knobelnest: Kinder der Klasse und Speicher kommen aus dem Portal
const KN=(()=>{try{return window.parent!==window&&window.parent.knAtelier||null}catch(e){return null}})();
const KID=!!(KN&&KN.mode==='kid');
let knOpen=false, dragging=false, lastWrite=0;''')
rep('''function setStatus(t){statusEl.textContent=t}''', r'''function makeKnStore(){
  let cb=null, timer=null; const fixed={};
  const pull=async()=>{
    if(dragging||Date.now()-lastWrite<2500||modal.innerHTML) return;
    try{
      const d=await KN.load(); if(!d) return;
      knOpen=!!d.open; applyOpen();
      // Startfarbe nach Namen (überall gleich); die Lehrperson speichert sie einmal fest
      const byName=[...(d.kids||[])].map(k=>k.name).sort((x,y)=>String(x).localeCompare(String(y),'de'));
      const list=(d.kids||[]).map((k,i)=>({...k,farbe:k.farbe||PALETTE[byName.indexOf(k.name)%PALETTE.length],order:i}));
      if(!KID) list.forEach((k,i)=>{if(!d.kids[i].farbe&&!fixed[k.id]){fixed[k.id]=1;KN.put(k.id,{farbe:k.farbe}).catch(()=>{})}});
      cb&&cb(list);
      setStatus('');
    }catch(e){setStatus('Die Daten sind gerade nicht erreichbar.')}
  };
  return {
    kind:'kn',
    subscribe(f){cb=f;pull();timer=setInterval(()=>{if(!document.hidden)pull()},4000)},
    async set(id,data){lastWrite=Date.now();await KN.put(id,data)},
    async update(id,patch){lastWrite=Date.now();await KN.put(id,patch)},
    async remove(id){},
    newId(){return 'k'+Date.now().toString(36)}
  };
}
function applyOpen(){
  const t=document.getElementById('tgOpen'); if(t) t.setAttribute('aria-checked',knOpen);
  const h=document.getElementById('kHint');
  if(KID&&h){h.hidden=false;h.textContent=knOpen?'Tippe auf deine Karte: Thema, Umsetzungsart und Velofarbe ändern.':'Zieh dein Velo an den Ort, wo du gerade stehst. Auf deiner Karte änderst du die Farbe.'}
}
function setStatus(t){statusEl.textContent=t}''')

# 4) Sortierung: Präsentation (oben links) – Produkt – Recherche – Thema – Parkplatz; Kinder sehen keine Lernerstufe
rep('''  const sorted=[...kids].sort((a,b)=>(a.order??0)-(b.order??0)||String(a.name).localeCompare(b.name));''',
    r'''  const RANK={'Präsentation':0,'Produkt':1,'Recherche':2,'Thema':3};
  const rk=k=>{const st=station(k);return st?RANK[st]:4};
  const sorted=[...kids].sort((a,b)=>(KN?rk(a)-rk(b):0)||(a.order??0)-(b.order??0)||String(a.name).localeCompare(b.name));''')
rep('''      const c=document.createElement('button');c.type='button';c.className='kid';c.dataset.id=k.id;''',
    '''      const c=document.createElement('button');c.type='button';c.className='kid'+(KID?(k.id===KN.me?' me':' other'):'');c.dataset.id=k.id;''')
rep('''        <div class="facts"><div><i>Thema</i>${f(k.thema)}</div><div><i>Umsetzungsart</i>${f(k.umsetzung)}</div><div class="f-stufe"><i>Lernerstufe</i>${f(k.stufe)}</div></div>`;''',
    '''        <div class="facts"${KID?' style="--cols:2"':''}><div><i>Thema</i>${f(k.thema)}</div><div><i>Umsetzungsart</i>${f(k.umsetzung)}</div>${KID?'':`<div class="f-stufe"><i>Lernerstufe</i>${f(k.stufe)}</div>`}</div>`;''')
rep('''      c.addEventListener('click',()=>{flashBike(k.id);openEdit(k)});''',
    '''      c.addEventListener('click',()=>{flashBike(k.id);if(!KID||k.id===KN.me)openEdit(k)});''')
rep('''    b.style.left=k.x+'%';b.style.top=k.y+'%';plan.appendChild(b);wireDrag(b,k);''',
    '''    b.style.left=k.x+'%';b.style.top=k.y+'%';plan.appendChild(b);wireDrag(b,k);if(KID&&k.id!==KN.me)b.classList.add('locked');''')
rep('''    park.appendChild(b);wireDrag(b,k);''', '''    park.appendChild(b);wireDrag(b,k);if(KID&&k.id!==KN.me)b.classList.add('locked');''')

# 5) Ziehen: Kinder nur das eigene Velo; während des Ziehens kein Nachladen
rep('''    if(ev.button!==0)return;
    ev.preventDefault();''', '''    if(ev.button!==0)return;
    if(KID&&k.id!==KN.me){flashCard(k.id);return}
    ev.preventDefault(); dragging=true;''')
rep('''      document.removeEventListener('pointermove',move);document.removeEventListener('pointerup',up);document.removeEventListener('pointercancel',up);
      park.classList.remove('over');''', '''      document.removeEventListener('pointermove',move);document.removeEventListener('pointerup',up);document.removeEventListener('pointercancel',up);
      park.classList.remove('over'); dragging=false;''')
rep('''  el.addEventListener('keydown',e=>{if(e.key==='Enter'){flashCard(k.id);openEdit(k)}});''',
    '''  el.addEventListener('keydown',e=>{if(e.key==='Enter'){flashCard(k.id);if(!KID||k.id===KN.me)openEdit(k)}});''')

# 6) Bearbeiten: Name kommt aus der Klassenkiste; Kinder ohne Lernerstufe, Text nur mit offenem Riegel
rep('''    <h3>${isNew?'Neues Kind':'Kind bearbeiten'}</h3>''', '''    <h3>${isNew?'Neues Kind':KID?'Mein Velo':'Kind bearbeiten'}</h3>''')
rep('''    <div class="grid2"><label>Umsetzungsart<input type="text" id="f-umsetzung" list="dl-ums"></label>
    <label>Lernerstufe<input type="text" id="f-stufe" list="dl-stufe"></label></div>''',
    '''    ${KID?`<label>Umsetzungsart<input type="text" id="f-umsetzung" list="dl-ums"></label>${knOpen?'':'<p class="lockmsg">Thema und Umsetzungsart kann gerade nur deine Lehrperson ändern.</p>'}`:`<div class="grid2"><label>Umsetzungsart<input type="text" id="f-umsetzung" list="dl-ums"></label>
    <label>Lernerstufe<input type="text" id="f-stufe" list="dl-stufe"></label></div>`}''')
rep('''    <div class="row">${isNew?'':'<button type="button" class="pill ghostbtn" id="del">Löschen</button>'}<span class="sp"></span>''',
    '''    <div class="row">${isNew||KN?'':'<button type="button" class="pill ghostbtn" id="del">Löschen</button>'}<span class="sp"></span>''')
rep('''  const fields=['name','thema','umsetzung','stufe'];
  fields.forEach(n=>$('#f-'+n).value=d[n]||'');''', '''  const fields=KID?['name','thema','umsetzung']:['name','thema','umsetzung','stufe'];
  fields.forEach(n=>$('#f-'+n).value=d[n]||'');
  if(KN){$('#f-name').readOnly=true;}
  if(KID&&!knOpen){$('#f-thema').disabled=true;$('#f-umsetzung').disabled=true;}''')
rep('''    const data={name:$('#f-name').value.trim(),thema:$('#f-thema').value.trim(),umsetzung:$('#f-umsetzung').value.trim(),stufe:$('#f-stufe').value.trim(),farbe:d.farbe};''',
    '''    const data=KID?(knOpen?{name:k.name,thema:$('#f-thema').value.trim(),umsetzung:$('#f-umsetzung').value.trim(),farbe:d.farbe}:{name:k.name,farbe:d.farbe})
      :{name:$('#f-name').value.trim(),thema:$('#f-thema').value.trim(),umsetzung:$('#f-umsetzung').value.trim(),stufe:$('#f-stufe').value.trim(),farbe:d.farbe};''')
rep('''      Object.assign(k,data);render();safe(()=>store.update(k.id,data));''',
    '''      Object.assign(k,data);render();
      if(KN){const {name:_n,...p}=data;safe(()=>store.update(k.id,p));} else safe(()=>store.update(k.id,data));''')
rep('''  setTimeout(()=>$('#f-name').focus(),30);
}''', '''  setTimeout(()=>{const n=KN?(KID&&!knOpen?null:$('#f-thema')):$('#f-name');n&&n.focus()},30);
}''')

# 7) Liste einfügen: in der Klassenkiste nach Namen zuordnen (nur Thema, Umsetzungsart, Lernerstufe)
rep('''    e.preventDefault();const rows=parse();if(!rows.length)return;closeModal();
    const base=Date.now();''', r'''    e.preventDefault();const rows=parse();if(!rows.length)return;closeModal();
    if(KN){
      const norm=v=>String(v||'').trim().toLowerCase();let miss=[];
      for(const r of rows){
        const k=kids.find(x=>norm(x.name)===norm(r.name))||kids.find(x=>norm(x.name).split(' ')[0]===norm(r.name).split(' ')[0]);
        if(!k){miss.push(r.name);continue}
        const p={thema:r.thema,umsetzung:r.umsetzung,stufe:r.stufe};Object.assign(k,p);
        await safe(()=>store.update(k.id,p));
      }
      render(); if(miss.length) setStatus('Nicht gefunden: '+miss.join(', '));
      return;
    }
    const base=Date.now();''')
rep('''    <p class="hint">Eine Zeile pro Kind, in dieser Reihenfolge: <b>Name Kind, Thema, Umsetzungsart, Lernerstufe</b>. Du kannst die Spalten direkt aus Excel kopieren oder mit Strichpunkt trennen. Jedes Kind bekommt automatisch eine Velofarbe, die du nachher ändern kannst.</p>''',
    '''    <p class="hint">Eine Zeile pro Kind, in dieser Reihenfolge: <b>Name Kind, Thema, Umsetzungsart, Lernerstufe</b>. Du kannst die Spalten direkt aus Excel kopieren oder mit Strichpunkt trennen. ${KN?'Die Zeilen werden den Kindern der Klasse über den Namen zugeordnet.':'Jedes Kind bekommt automatisch eine Velofarbe, die du nachher ändern kannst.'}</p>''')

# 8) Start: Leiste je nach Rolle, Speicher aus der Klassenkiste
rep('''$('#btnAdd').onclick=()=>openEdit(null);''', r'''$('#btnAdd').onclick=()=>openEdit(null);
if(KN){
  $('#btnAdd').hidden=true;
  const kb=$('#knBack');kb.hidden=false;kb.onclick=()=>KN.back();
  if(KID){$('#btnPaste').hidden=true;$('#tgStufe').hidden=true;document.body.classList.add('kidmode')}
  else{const to=$('#tgOpen');to.hidden=false;to.onclick=async()=>{knOpen=!knOpen;applyOpen();lastWrite=Date.now();
    try{await KN.setOpen(knOpen);setStatus(knOpen?'Die Kinder können jetzt Thema und Umsetzungsart ändern.':'Gesperrt: Die Kinder können nur noch ihr Velo verschieben und die Farbe ändern.');setTimeout(()=>setStatus(''),4000)}
    catch(e){knOpen=!knOpen;applyOpen();setStatus('Speichern hat nicht geklappt.')}}}
  if(KN.className) document.querySelector('.ptitle').textContent='Atelier';
}''')
rep('''setStufe(stufeOn);''', '''setStufe(KID?false:stufeOn);''')
rep('''  store=db?makeDbStore(db):makeLocalStore();''', '''  store=KN?makeKnStore():db?makeDbStore(db):makeLocalStore();''')
rep('''  try{db=window.claude&&window.claude.use?await window.claude.use('db'):null}catch(e){db=null}''',
    '''  try{db=!KN&&window.claude&&window.claude.use?await window.claude.use('db'):null}catch(e){db=null}''')

exec(open(__file__.rsplit('/',1)[0]+'/sec9.py',encoding='utf-8').read())
exec(open(__file__.rsplit('/',1)[0]+'/sec10.py',encoding='utf-8').read())
exec(open(__file__.rsplit('/',1)[0]+'/sec11.py',encoding='utf-8').read())
exec(open(__file__.rsplit('/',1)[0]+'/sec12.py',encoding='utf-8').read())
open(dst, 'w', encoding='utf-8').write(s)
print('ok', len(s))
