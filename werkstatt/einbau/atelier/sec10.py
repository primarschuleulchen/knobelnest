# 10) Titel grösser, keine «Kinder»-Überschrift, Station nach Höhe auf dem Weg, Stationsfarben, Umsetzungsarten zum Auswählen
rep('''  --ptH:clamp(30px,3.4vh,42px);''', '''  --ptH:clamp(42px,5.2vh,64px);''')
rep('''<div class="lhead" id="headL">Kinder</div>''', '')
rep('''<div class="lhead" id="headR">Kinder</div>''', '')
rep('''  .lbody{container-type:size;padding:2px 8px 8px;gap:0;overflow:auto}''', '''  .lbody{container-type:size;padding:8px 8px 8px;gap:0;overflow:auto}''')
# Wer auf dem Weg (von unten nach oben) auf der Höhe eines Schildes vorbei ist, gehört zur nächsten Station
rep('''  // nächstes Schild (Fuss des Pfostens, in % des Plans; Höhe zählt wegen Seitenverhältnis 1.41x)
  const S=[['Präsentation',13,25],['Produkt',70,44],['Recherche',22,60],['Thema',85,80]];
  let best=S[0],bd=1e9;S.forEach(s=>{const d=(s[1]-k.x)**2+((s[2]-k.y)*1.41)**2;if(d<bd){bd=d;best=s}});
  return best[0];''', '''  // Höhe der Schildmitte in % des Plans: Thema 66.8, Recherche 45.6, Produkt 29.3
  if(k.y>66.8) return 'Thema';
  if(k.y>45.6) return 'Recherche';
  if(k.y>29.3) return 'Produkt';
  return 'Präsentation';''')
rep('''.st.Thema{background:var(--leaf-soft);color:#4f7a3c}
.st.Recherche{background:var(--sky-soft);color:#456f97}
.st.Produkt{background:var(--sun-soft);color:#9a6a12}
.st.Präsentation{background:var(--rose-soft);color:#b5524a}''', '''.st.Thema{background:#e6e8ea;color:#4f575e}
.st.Recherche{background:#fbeeb8;color:#7d5f00}
.st.Produkt{background:#dcefd3;color:#336e24}
.st.Präsentation{background:#dbe6fb;color:#2a58b0}''')
rep('''  .kname .st{flex:none;font-size:clamp(8.5px,calc(var(--r) * .15),11px);padding:1px 7px 0}''',
    '''  .kname .st{flex:none;font-size:clamp(9.5px,calc(var(--r) * .17),12.5px);padding:2px 9px 1px}''')
# Umsetzungsarten: Lehrperson legt sie fest, beim Bearbeiten wird ausgewählt
rep('''let knOpen=false, dragging=false, lastWrite=0;''', '''let knOpen=false, dragging=false, lastWrite=0, knArten=[];''')
rep('''      knOpen=!!d.open; applyOpen();''', '''      knOpen=!!d.open; knArten=Array.isArray(d.arten)?d.arten:[]; applyOpen();''')
rep('''    <button class="pill" id="btnPaste" type="button">Liste einfügen</button>''',
    '''    <button class="pill" id="btnArten" type="button" hidden>Umsetzungsarten</button>
    <button class="pill" id="btnPaste" type="button">Liste einfügen</button>''')
rep('''.dlg .lockmsg{''', '''.dlg select{font-size:16px;font-weight:600;text-transform:none;letter-spacing:0;color:var(--ink);padding:8px 14px;border:1px solid var(--line);border-radius:999px;background:var(--paper);width:100%}
.dlg select:disabled{opacity:.55}
.dlg .lockmsg{''')
rep('''  if(KID&&!knOpen){$('#f-thema').disabled=true;$('#f-umsetzung').disabled=true;}''', r'''  if(KN&&knArten.length){ // Auswahl statt Freitext
    const inp=$('#f-umsetzung'), cur=inp.value, sel=document.createElement('select'); sel.id='f-umsetzung';
    const opts=[...knArten]; if(cur&&!opts.includes(cur)) opts.push(cur);
    sel.innerHTML='<option value="">– bitte wählen –</option>'+opts.map(a=>`<option>${esc(a)}</option>`).join('');
    sel.value=cur; inp.replaceWith(sel);
  }
  if(KID&&!knOpen){$('#f-thema').disabled=true;$('#f-umsetzung').disabled=true;}''')
rep('''$('#btnPaste').onclick=openPaste;''', r'''$('#btnPaste').onclick=openPaste;
function openArten(){
  modal.innerHTML=`<div class="overlay"><form class="dlg" id="af">
    <h3>Umsetzungsarten</h3>
    <p class="hint">Eine Art pro Zeile. Die Kinder wählen ihre Umsetzungsart dann aus dieser Liste (wenn der Riegel «Kinder dürfen Text ändern» offen ist).</p>
    <textarea id="at" placeholder="Plakat&#10;Modell&#10;Film&#10;Präsentation mit Folien"></textarea>
    <div class="row"><button type="button" class="pill" id="acancel">Abbrechen</button><button type="submit" class="pill rose">Speichern</button></div>
  </form></div>`;
  $('#at').value=knArten.join('\n');
  $('#acancel').onclick=closeModal;
  $('#af').addEventListener('submit',async e=>{
    e.preventDefault();
    const list=[...new Set($('#at').value.split(/\r?\n/).map(x=>x.trim()).filter(Boolean))].slice(0,30);
    closeModal(); knArten=list; lastWrite=Date.now();
    try{await KN.setArten(list);setStatus('Umsetzungsarten gespeichert.');setTimeout(()=>setStatus(''),3000)}catch(err){setStatus('Speichern hat nicht geklappt.')}
  });
  setTimeout(()=>$('#at').focus(),30);
}
$('#btnArten').onclick=openArten;''')
rep('''  else{const to=$('#tgOpen');to.hidden=false;''', '''  else{$('#btnArten').hidden=false;const to=$('#tgOpen');to.hidden=false;''')
rep('''.st.Präsentation{background:#dbe6fb;color:#2a58b0}''', '''.st.Präsentation{background:#dbe6fb;color:#2a58b0}
.st:not(.Thema):not(.Recherche):not(.Produkt):not(.Präsentation){background:#fff;color:#8a928c;box-shadow:inset 0 0 0 1px #cfd6cd}''')
