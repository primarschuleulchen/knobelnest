/* ---------- Knobelnest: Bilder zu den Wörtern ---------- */
/* w.img = Emoji (Text) oder eigenes Bild (data:image/…), '-' = bewusst kein Bild. Ohne Eintrag sucht die Kiste ein Emoji
   aus EMO (Liste in werkstatt/einbau/vokabelkiste/vk_emoji.txt), zuerst mit dem deutschen Wort, dann mit dem Fremdwort. */
const EMO=new Map(__EMOJI__);
const EMO_PRE=/^(?:(?:am|im|um|in der|in the|at|on|to|der|die|das|den|dem|des|ein|eine|einen|the|a|an|le|la|les|un|une|des|du|el|il|lo)\s+)+/;
function emoKeys(t){t=String(t||'').toLowerCase().normalize('NFC').replace(/[’‘ʼ`´]/g,"'").replace(/\([^)]*\)/g,' ').replace(/\*(?:in|e|r)\b|\*/g,'');
  return t.split(/\s*[\/,;]\s*|\s+oder\s+|\s+or\s+|\s+ou\s+/).map(x=>x.replace(/[.!?…]+/g,' ').replace(/\s+/g,' ').trim().replace(EMO_PRE,'').replace(/^l'/,'').trim()).filter(Boolean)}
function autoEmo(w){for(const k of emoKeys(w.de)){const e=EMO.get('de:'+k)||EMO.get(k);if(e)return e}
  for(const k of emoKeys(w.f)){const e=EMO.get('fl:'+k)||EMO.get(k);if(e)return e}return null}
const isImgUrl=v=>/^data:image\//.test(v||'');
const picOf=w=>!w||w.img==='-'?null:(w.img||autoEmo(w));
const bildOK=w=>!!picOf(w);
const picHTML=(v,cls='')=>!v?'':isImgUrl(v)?`<img class="pic ${cls}" src="${esc(v)}" alt="" draggable="false">`:`<span class="pic emo ${cls}" aria-hidden="true">${esc(v)}</span>`;
/* Emoji-Suche für die Lehrperson: alle Bilder, deren Stichwort mit dem Suchwort beginnt */
function emoFind(q){q=String(q||'').toLowerCase().trim();const out=[];if(!q)return out;
  for(const [k,e] of EMO){const kk=k.replace(/^(de|fl):/,'');if((kk.startsWith(q)||kk.split(' ').some(x=>x.startsWith(q)))&&!out.includes(e))out.push(e);if(out.length>=40)break}return out}
const EMO_GRUND=['🍎','🐕','🐈','🏫','📕','✏️','🎒','👩','👨','👧','👦','👪','😊','😢','😠','😴','☀️','🌧️','❄️','🍂','🌷','🏠','🚲','⚽','🎵','🎨','🍕','🧀','🍞','🥛','👕','👖','👟','🧢','🎁','⭐','❤️','✅','❌','🗣️'];

/* Eigenes Bild: quadratisch zuschneiden, 200 px, als webp (sonst jpeg). Klein genug für die Klassenkiste. */
function picFromFile(file){return new Promise((res,rej)=>{
  if(!file||!/^image\//.test(file.type)){rej(new Error('Das ist kein Bild.'));return}
  const url=URL.createObjectURL(file),img=new Image();
  img.onload=()=>{try{const S=200,c=document.createElement('canvas');c.width=S;c.height=S;const g=c.getContext('2d');
      const m=Math.min(img.naturalWidth,img.naturalHeight),sx=(img.naturalWidth-m)/2,sy=(img.naturalHeight-m)/2;
      g.imageSmoothingQuality='high';g.drawImage(img,sx,sy,m,m,0,0,S,S);URL.revokeObjectURL(url);
      let d=c.toDataURL('image/webp',.78);
      if(!/^data:image\/webp/.test(d)){const c2=document.createElement('canvas');c2.width=S;c2.height=S;const g2=c2.getContext('2d');g2.fillStyle='#fff';g2.fillRect(0,0,S,S);g2.drawImage(c,0,0);d=c2.toDataURL('image/jpeg',.8)}
      res(d)}catch(e){rej(e)}};
  img.onerror=()=>{URL.revokeObjectURL(url);rej(new Error('Das Bild lässt sich nicht öffnen.'))};img.src=url})}

/* Bild-Auswahl für ein Wort (Lehrperson) */
function picDialog(w,onDone){
  const L=$('#layer');let cur=w.img;
  const now=()=>cur==='-'?null:(cur||autoEmo(w));
  const draw=()=>{const v=now(),auto=!cur&&!!v;
    L.innerHTML=`<div class="scrim"></div><div class="dlg picdlg" role="dialog" aria-label="Bild wählen">
      <h2 class="lbl">Bild für «${esc(w.de)} = ${esc(w.f)}»</h2>
      <div class="pdnow">${v?picHTML(v,'big'):'<span class="pic none big">–</span>'}<p>${auto?'Automatisch gewählt. Passt es nicht? Such unten ein anderes oder lade ein eigenes Bild hoch.':cur==='-'?'Dieses Wort hat kein Bild. Es kommt bei «Bild &amp; Wort» nicht vor.':v?'Dieses Bild hast du gewählt.':'Noch kein Bild gefunden. Such unten eines oder lade ein eigenes hoch.'}</p></div>
      <input class="inp" id="pdq" placeholder="Bild suchen (z. B. Hund, apple) oder Emoji einfügen" aria-label="Bild suchen" autocomplete="off">
      <div class="pdgrid" id="pdgrid"></div>
      <div class="dact pdact"><label class="pill"><input type="file" accept="image/*" id="pdfile" hidden>📷 Eigenes Bild</label>
        ${cur?'<button class="pill" id="pdauto">Automatisch</button>':''}${cur!=='-'?'<button class="pill" id="pdnone">Kein Bild</button>':''}<span class="sp"></span><button class="pill go" id="pdok">Fertig</button></div></div>`;
    const grid=$('#pdgrid',L),q=$('#pdq',L);
    const fill=()=>{const t=q.value.trim();let list=t?emoFind(t):[...new Set([...emoKeys(w.de).flatMap(emoFind),...EMO_GRUND])].slice(0,40);
      const own=t&&/\p{Extended_Pictographic}/u.test(t)?[t.replace(/[\p{L}\p{N}\s]/gu,'')].filter(Boolean):[];
      list=[...own,...list.filter(e=>!own.includes(e))];
      grid.innerHTML=list.length?list.map(e=>`<button class="pdo" data-e="${esc(e)}">${esc(e)}</button>`).join(''):'<p class="note">Nichts gefunden. Versuch ein anderes Wort oder lade ein eigenes Bild hoch.</p>';
      $$('[data-e]',grid).forEach(b=>b.onclick=()=>{cur=b.dataset.e;draw()})};
    q.oninput=fill;fill();
    const close=()=>{L.innerHTML='';onDone()};
    $('.scrim',L).onclick=close;$('#pdok',L).onclick=()=>{if(cur)w.img=cur;else delete w.img;close()};
    const pa=$('#pdauto',L);if(pa)pa.onclick=()=>{cur=undefined;draw()};
    const pn=$('#pdnone',L);if(pn)pn.onclick=()=>{cur='-';draw()};
    $('#pdfile',L).onchange=async e=>{const f=e.target.files&&e.target.files[0];if(!f)return;
      try{cur=await picFromFile(f);draw()}catch(x){toast(x.message||'Das Bild ging nicht.')}};
  };draw();
}
function bindPics(node,redraw){$$('#etab [data-pic]').forEach(b=>b.onclick=()=>{const w=node.words.find(x=>x.id===b.dataset.pic);if(!w)return;
  const before=w.img;picDialog(w,()=>{if(w.img!==before){touch();redraw()}})})}
const picCell=w=>{const v=picOf(w);return `<button type="button" class="picb ${v&&!w.img?'auto':''}" data-pic="${w.id}" title="Bild wählen" aria-label="Bild für ${esc(w.de)} wählen">${v?picHTML(v):'<span class="plus">+</span>'}</button>`};

/* ---------- Knobelnest: neue Übungen «Bild & Wort» und «Sprechen» ---------- */
ICONS.bild=I('<rect x="3" y="4" width="18" height="16" rx="2.5"/><circle cx="9" cy="10" r="2"/><path d="M21 16l-5-5-9 9"/>');
ICONS.sprechen=I('<rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5.5 11a6.5 6.5 0 0 0 13 0M12 17.5V21M8.5 21h7"/>');
const SR=window.SpeechRecognition||window.webkitSpeechRecognition||null;
const canRecord=!!(navigator.mediaDevices&&navigator.mediaDevices.getUserMedia&&window.MediaRecorder);
const sprechOK=w=>!w.x;
function knMoreModes(MODES,ws){
  const bilN=ws.filter(bildOK).length,spN=ws.filter(sprechOK).length;
  const bild=['bild','Bild & Wort',bilN>=2?`Zu jedem Bild das richtige Wort finden und umgekehrt. ${bilN} ${bilN===1?'Wort':'Wörter'} mit Bild.`:'Hier gibt es noch zu wenige Wörter mit Bild.',bilN>=2];
  const spr=['sprechen','Sprechen',`Deutsch wird angezeigt, du sagst es auf ${esc(SUB().name)}. ${SR?'Die Kiste hört zu.':'Du nimmst dich auf und vergleichst.'}`,spN];
  const ia=MODES.findIndex(m=>m[0]==='karte');if(bilN>=2||T)MODES.splice(ia+1,0,bild);
  const ib=MODES.findIndex(m=>m[0]==='hoeren');MODES.splice(ib+1,0,spr);
}

/* Bild & Wort: abwechselnd Bild -> Wort wählen und Wort (vorgelesen) -> Bild wählen */
function modeBild(subset){
  const all=SET.words.filter(bildOK);
  const list=subset?shuffle(subset):freshOrder(all.map(w=>w.id),(SET.key||'')+':bild'),total=list.length;
  const body=shell('Bild &amp; Wort');let queue=list.slice(),done=0,tries=0,turn=Math.random()<.5?0:1;const hard=new Set();
  const others=w=>{const inf=IDX.get(w.id),own=inf&&inf.portion&&inf.portion.words?inf.portion.words.filter(x=>valid(x)&&bildOK(x)):[];
    const out=[],sp=new Set([picOf(w)]),sw=new Set([norm(w.f)]);
    for(const src of [own,all,subWords(SUB()).filter(bildOK)]){for(const o of shuffle(src)){if(out.length>=3)break;if(o.id===w.id)continue;
      const p=picOf(o),k=norm(o.f);if(sp.has(p)||sw.has(k))continue;sp.add(p);sw.add(k);out.push(o)}if(out.length>=3)break}
    return out};
  const next=()=>{setProg(`${done} von ${total} richtig`,done/total);
    if(!queue.length)return summary(body,{title:'Alle Bilder erkannt!',lines:[`${total} Wörter, ${tries} Versuche.`,hard.size?`${hard.size} ${hard.size===1?'Wort war':'Wörter waren'} zuerst falsch.`:'Fehlerfrei!'],actions:endActions(hard,modeBild)});
    const id=queue.shift(),w=WD(id),opts=shuffle([w,...others(w)]),kind=turn++%2;
    body.innerHTML=(kind===0
      ?`<div class="bq"><div class="bbig">${picHTML(picOf(w))}</div><p class="hand">Welches Wort passt zum Bild?</p></div>
        <div class="opts">${opts.map((o,i)=>`<button class="opt" data-i="${i}"><kbd>${i+1}</kbd><span>${esc(o.f)}</span></button>`).join('')}</div>`
      :`<div class="bq"><div class="bword">${esc(w.f)}${spkBtn(w.f)}</div><p class="hand">Welches Bild passt?</p></div>
        <div class="bopts">${opts.map((o,i)=>`<button class="bopt" data-i="${i}" aria-label="Bild ${i+1}"><kbd>${i+1}</kbd>${picHTML(picOf(o))}</button>`).join('')}</div>`)
      +`<div class="fb" id="fb"></div><p class="keys">Tasten 1 – ${opts.length}</p>`;
    bindSpeak(body);if(kind===1)speak(w.f);
    let fin=false;
    const pick=i=>{if(fin||!opts[i])return;fin=true;const ok=opts[i].id===w.id;tries++;
      $$('[data-i]',body).forEach((b,j)=>{if(opts[j].id===w.id)b.classList.add('right');else if(j===i)b.classList.add('wrong')});
      $('#fb',body).innerHTML=ok?`<span class="ok">✓ Richtig!</span><span class="sub">${esc(w.f)} = ${esc(w.de)}</span>`:`<span class="no">✗ Leider falsch. Richtig ist:</span><span class="sub">${esc(w.f)} = ${esc(w.de)}</span>`;
      speak(w.f);rec(id,ok);if(ok)done++;else{hard.add(id);reins(queue,id)}
      later(next,ok?1300:2400)};
    $$('[data-i]',body).forEach(b=>b.onclick=()=>pick(+b.dataset.i));
    session.key=e=>{const n=parseInt(e.key,10);if(n>=1&&n<=opts.length){e.preventDefault();pick(n-1)}};
  };next();
}

/* Sprechen: Das Kind sieht das deutsche Wort und sagt es in der Fremdsprache.
   Mit Spracherkennung (Chrome, Edge, Safari) prüft die Kiste selbst (der Ton geht dafür an Google bzw. Apple).
   Sonst: aufnehmen, anhören, mit der Vorlese-Stimme vergleichen und selbst entscheiden. */
const SR_LANG={en:'en-GB',fr:'fr-FR',it:'it-IT',es:'es-ES',de:'de-CH'};
const CONTR=[[/\bit's\b/g,'it is'],[/\bthat's\b/g,'that is'],[/\bwhat's\b/g,'what is'],[/\bhe's\b/g,'he is'],[/\bshe's\b/g,'she is'],[/\bthere's\b/g,'there is'],
  [/\bi'm\b/g,'i am'],[/\byou're\b/g,'you are'],[/\bwe're\b/g,'we are'],[/\bthey're\b/g,'they are'],[/\bcan't\b/g,'cannot'],[/\bcan not\b/g,'cannot'],[/\bdon't\b/g,'do not'],
  [/\bdoesn't\b/g,'does not'],[/\bisn't\b/g,'is not'],[/\baren't\b/g,'are not'],[/\bi've\b/g,'i have'],[/\bwe've\b/g,'we have'],[/\blet's\b/g,'let us'],[/\bo'clock\b/g,'oclock'],[/\bo clock\b/g,'oclock']];
function spN(s){s=String(s||'').toLowerCase().normalize('NFC').replace(/[’‘ʼ`´]/g,"'");s=deacc(s);
  CONTR.forEach(([a,b])=>{s=s.replace(a,b)});
  return s.replace(/[-–]/g,' ').replace(/[^\p{L}\p{N}' ]/gu,' ').replace(/\s+/g,' ').trim()}
const SP_ART=/^(?:(?:the|a|an|to|le|la|les|un|une|des|du|il|lo|el|los|las|der|die|das)\s+|l')/;
function sayTargets(f){
  let t=String(f||'').replace(/[’‘ʼ`´]/g,"'").replace(NOTE_RE,'');
  const alts=t.split(/\s*[\/;]\s*|\s+or\s+|\s+ou\s+|\s*,\s*/).map(x=>x.trim()).filter(Boolean);if(!alts.length)alts.push(t);
  const out=new Set();
  alts.concat([t]).forEach(a=>{
    const forms=[a.replace(/[()]/g,''),a.replace(/\([^)]*\)/g,' ')];
    forms.forEach(x=>{x=x.replace(/…|\.\.\./g,' ');const n=spN(x);if(n){out.add(n);out.add(n.replace(SP_ART,''))}})});
  return [...out].filter(Boolean)}
/* «…» im Wort (z. B. «at … o'clock») = hier darf etwas Beliebiges stehen */
function sayRx(f){return String(f||'').replace(/[’‘ʼ`´]/g,"'").replace(NOTE_RE,'').split(/\s*[\/;]\s*/).filter(a=>/…|\.\.\./.test(a)).map(a=>{
  const parts=a.split(/…|\.\.\./).map(x=>spN(x.replace(/\([^)]*\)/g,' '))).filter(Boolean);
  return parts.length?new RegExp('^(?:.* )?'+parts.map(escRe).join(' (?:.* )?')+'(?: .*)?$'):null}).filter(Boolean)}
function sayMatch(heard,f){const T2=sayTargets(f),RX=sayRx(f);
  return heard.some(h=>{const a=spN(h),b=a.replace(SP_ART,'');if(!a)return false;if(RX.some(r=>r.test(a)))return true;
    return T2.some(t=>{if(t===a||t===b||t.replace(SP_ART,'')===b)return true;
      const tol=t.length>=10?2:t.length>=5?1:0;return tol&&(lev(a,t)<=tol||lev(b,t.replace(SP_ART,''))<=tol)})})}
const MIC_SVG='<svg width="46" height="46" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5.5 11a6.5 6.5 0 0 0 13 0M12 17.5V21M8.5 21h7"/></svg>';
let talkWay=null;/* 'sr' = Spracherkennung, 'rec' = aufnehmen, 'self' = laut sagen und selbst prüfen */
function modeTalk(subset){
  if(!talkWay)talkWay=SR?'sr':canRecord?'rec':'self';
  const list=subset?shuffle(subset):freshOrder(SET.words.filter(sprechOK).map(w=>w.id),(SET.key||'')+':sprechen'),total=list.length;
  const body=shell('Sprechen');let queue=list.slice(),done=0,tries=0;const hard=new Set();
  let rcg=null,mrec=null,stream=null,audio=null;
  const stopAll=()=>{try{if(rcg){rcg.onend=null;rcg.onresult=null;rcg.onerror=null;rcg.abort()}}catch(e){}rcg=null;
    try{if(mrec&&mrec.state!=='inactive')mrec.stop()}catch(e){}mrec=null;
    if(stream){stream.getTracks().forEach(t=>t.stop());stream=null}
    if(audio){try{audio.pause()}catch(e){}if(audio.src)URL.revokeObjectURL(audio.src);audio=null}};
  session.cleanup=stopAll;
  const lang=SUB().name;
  const next=()=>{stopAll();setProg(`${done} von ${total} richtig gesagt`,done/total);
    if(!queue.length)return summary(body,{title:'Super gesprochen!',lines:[`${total} Wörter, ${tries} Versuche.`,hard.size?`${hard.size} ${hard.size===1?'Wort brauchte':'Wörter brauchten'} mehrere Anläufe.`:'Alles beim ersten Mal!'],actions:endActions(hard,modeTalk)});
    const id=queue.shift(),w=WD(id),p=picOf(w);let fails=0,helped=false,fin=false,counted=false;
    body.innerHTML=`<div class="sheet talkq"><div class="lang"><span>Deutsch</span></div>${p?`<div class="tpic">${picHTML(p)}</div>`:''}<div class="word">${esc(w.de)}</div><div class="sub">Sag es auf ${esc(lang)}.</div></div>
      <div class="listen"><button type="button" class="play mic" id="mic" aria-label="${talkWay==='sr'?'Sprechen':talkWay==='rec'?'Aufnehmen':'Lösung zeigen'}">${talkWay==='self'?'👁':MIC_SVG}</button></div>
      <p class="hand" id="mict">${talkWay==='sr'?'Tippe aufs Mikrofon und sag das Wort.':talkWay==='rec'?'Tippe aufs Mikrofon, sag das Wort und tippe nochmals.':'Sag das Wort laut. Dann tippe auf das Auge.'}</p>
      <div class="fb" id="fb"></div>
      <div class="actions" id="tact"><button class="pill sm" id="hear">👂 Vorsagen</button><button class="pill sm" id="skip">Überspringen</button></div>
      <p class="keys">Leertaste: ${talkWay==='self'?'Lösung zeigen':'sprechen'}</p>`;
    const mic=$('#mic',body),mt=$('#mict',body),fb=$('#fb',body);
    const sol=()=>`<span class="sol">${esc(w.f)}</span>${spkBtn(w.f)}`;
    const finish=ok=>{if(fin)return;fin=true;stopAll();tries++;if(!counted){rec(id,ok);counted=true}
      if(ok)done++;else{hard.add(id);reins(queue,id)}};
    const right=heard=>{finish(!helped&&!fails);mic.classList.remove('on');mic.classList.add('okm');
      fb.innerHTML=`<span class="ok">✓ Richtig!${heard?` Ich habe gehört: «${esc(heard)}»`:''}</span><span class="sub">${sol()}</span>`;bindSpeak(fb);
      later(()=>speak(w.f),350);later(next,2000)};
    const wrong=heard=>{fails++;if(!counted){rec(id,false);counted=true}hard.add(id);mic.classList.remove('on');
      fb.innerHTML=heard?`<span class="no">Ich habe «${esc(heard)}» gehört.</span>`:`<span class="no">Ich habe nichts verstanden.</span>`;
      if(fails>=2)fb.innerHTML+=`<span class="sub">So heisst es: ${sol()}</span>`;
      fb.innerHTML+=`<span class="sub">Versuch es nochmal!</span>`;bindSpeak(fb);mt.textContent='Tippe aufs Mikrofon und versuch es nochmal.'};
    /* Spracherkennung */
    const listen=()=>{if(fin)return;if(rcg){try{rcg.stop()}catch(e){}return}
      let r;try{r=new SR()}catch(e){talkWay=canRecord?'rec':'self';return next0()}
      rcg=r;r.lang=SR_LANG[fl()]||fl();r.interimResults=true;r.maxAlternatives=5;r.continuous=false;
      let heard=[],shown='',errd=false;
      mic.classList.add('on');mt.textContent='Ich höre zu …';fb.innerHTML='';
      const tm=later(()=>{try{r.stop()}catch(e){}},8000);
      r.onresult=e=>{for(let i=e.resultIndex;i<e.results.length;i++){const res=e.results[i];shown=res[0].transcript;
          if(res.isFinal)for(let k=0;k<res.length;k++)heard.push(res[k].transcript)}
        mt.textContent='«'+shown.trim()+'»';
        if(heard.length&&sayMatch(heard,w.f)){try{r.stop()}catch(x){}}};
      r.onerror=e=>{errd=true;clearTimeout(tm);
        if(e.error==='not-allowed'||e.error==='service-not-allowed'||e.error==='network'||e.error==='audio-capture'){rcg=null;mic.classList.remove('on');
          talkWay=canRecord&&e.error!=='audio-capture'&&e.error!=='not-allowed'?'rec':'self';
          toast(e.error==='network'?'Die Spracherkennung ist nicht erreichbar. Du kannst dich stattdessen aufnehmen.':'Das Mikrofon ist gesperrt. Sag die Wörter laut und prüfe selbst.');
          later(next0,400)}};
      r.onend=()=>{clearTimeout(tm);if(rcg!==r)return;rcg=null;if(fin)return;
        if(!heard.length&&shown)heard.push(shown);
        if(heard.length&&sayMatch(heard,w.f))right(heard.find(h=>sayMatch([h],w.f))||heard[0]);
        else if(heard.length)wrong(heard[0]);
        else{mic.classList.remove('on');mt.textContent='Tippe aufs Mikrofon und sag das Wort.';if(!errd||!talkWay||talkWay==='sr')fb.innerHTML='<span class="no">Ich habe nichts gehört. Sprich etwas lauter und versuch es nochmal.</span>'}};
      try{r.start()}catch(e){rcg=null;mic.classList.remove('on')}
    };
    /* Aufnehmen und selbst vergleichen */
    const judge=()=>{$('#tact',body).innerHTML=`<div class="judge"><button class="no" id="tno">✗ Nochmal üben</button><button class="yes" id="tyes">✓ Klang gleich</button></div>`;
      $('#tno',body).onclick=()=>{if(fin)return;finish(false);next()};$('#tyes',body).onclick=()=>{if(fin)return;finish(!helped);next()}};
    const recStart=async()=>{if(fin)return;
      if(mrec&&mrec.state==='recording'){mrec.stop();return}
      try{stream=stream||await navigator.mediaDevices.getUserMedia({audio:true})}catch(e){talkWay='self';toast('Das Mikrofon ist gesperrt. Sag die Wörter laut und prüfe selbst.');return next0()}
      const chunks=[];mrec=new MediaRecorder(stream);mrec.ondataavailable=e=>{if(e.data&&e.data.size)chunks.push(e.data)};
      mrec.onstop=()=>{mic.classList.remove('on');if(stream){stream.getTracks().forEach(t=>t.stop());stream=null}
        if(audio&&audio.src)URL.revokeObjectURL(audio.src);
        audio=new Audio(URL.createObjectURL(new Blob(chunks,{type:chunks[0]&&chunks[0].type||'audio/webm'})));
        mt.textContent='Hör dich an und vergleiche mit der richtigen Aussprache.';
        fb.innerHTML=`<div class="actions"><button class="pill" id="me">▶ Ich</button><button class="pill" id="model">🔊 So klingt es richtig</button></div><span class="sub">${sol()}</span>`;bindSpeak(fb);
        $('#me',fb).onclick=()=>{try{audio.currentTime=0;audio.play()}catch(e){}};$('#model',fb).onclick=()=>speak(w.f);
        try{audio.play()}catch(e){}later(()=>speak(w.f),1600);judge()};
      mrec.start();mic.classList.add('on');mt.textContent='Ich nehme auf … Tippe nochmals, wenn du fertig bist.';fb.innerHTML='';
      later(()=>{if(mrec&&mrec.state==='recording')mrec.stop()},6000)};
    /* Ohne Mikrofon: Lösung zeigen und selbst entscheiden */
    const selfShow=()=>{if(fin)return;fb.innerHTML=`<span class="sub">${sol()}</span>`;bindSpeak(fb);speak(w.f);mic.disabled=true;mt.textContent='Hast du es richtig gesagt?';judge()};
    const go=()=>talkWay==='sr'?listen():talkWay==='rec'?recStart():selfShow();
    const next0=()=>{queue.unshift(id);next()};
    mic.onclick=go;
    $('#hear',body).onclick=()=>{helped=true;speak(w.f)};
    $('#skip',body).onclick=()=>{if(fin)return;fin=true;stopAll();if(!counted){rec(id,false);counted=true}hard.add(id);reins(queue,id);next()};
    session.key=e=>{if(e.code==='Space'){e.preventDefault();go()}};
  };next();
}

/* ---------- Knobelnest: Was habe ich in dieser Portion schon geschafft? ----------
   Eine Übung gilt als geschafft, wenn das Kind sie bis zur Schluss-Seite durchgemacht hat (summary).
   P.done[Portion] = {Übung: Zeit}. Die Portion ist geschafft, wenn alle Übungen geschafft sind, die es in ihr gibt
   (vkReq: ohne Lückensatz, wenn es keine Sätze gibt, ohne «Bild & Wort» bei weniger als 2 Bildern usw.); dann P.ganz[Portion] = Zeit.
   Die Spiele (Paare, Wortregen), der Karteikasten und die Knacknüsse zählen nicht. */
function vkReq(ws){ws=ws||[];if(!ws.length)return[];const nW=ws.filter(w=>!w.x).length;
  return [['karte',1],['bild',ws.filter(bildOK).length>=2],['drei',1],['merken',1],['salat',ws.some(salatOK)],['schreiben',1],
    ['hoeren',canSpeak&&nW],['sprechen',ws.some(sprechOK)],['luecke',!noSent()&&ws.some(gapOK)]].filter(x=>x[1]).map(x=>x[0])}
const vkDoneOf=key=>((P.done||{})[key])||{};
function vkMark(){
  if(!knMode||!knMode.key||knMode.key==='box'||knMode.key==='nuts'||knMode.key==='?')return;
  const key=knMode.key,mode=knMode.mode;if(!vkReq(SET.words).includes(mode))return;
  P.done=P.done||{};const d=P.done[key]=P.done[key]||{};const neu=!d[mode];d[mode]=Date.now();
  const req=vkReq(SET.words),n=req.filter(m=>d[m]).length;
  P.ganz=P.ganz||{};
  if(n>=req.length&&!P.ganz[key]){P.ganz[key]=Date.now();later(()=>toast('🎉 Portion geschafft! Du hast alle Übungen gemacht.'),400)}
  else if(neu)later(()=>toast('✓ '+(MODE_NAMES[mode]||mode)+' geschafft · '+n+' von '+req.length+' Übungen'),400);
  saveP()}
function vkHead(){if(!SET.key||SET.key==='box'||SET.key==='nuts')return'';const req=vkReq(SET.words),d=vkDoneOf(SET.key),n=req.filter(m=>d[m]).length;
  if(!req.length)return'';const ganz=n>=req.length;
  return `<div class="vkfort ${ganz?'ganz':''}"><span class="vkf-t">${ganz?'🎉 Portion geschafft!':n+' von '+req.length+' Übungen geschafft'}</span><span class="vkf-dots">${req.map(m=>`<i class="${d[m]?'on':''}" title="${esc(MODE_NAMES[m]||m)}"></i>`).join('')}</span></div>`}
const vkTileMark=m=>{const d=vkDoneOf(SET.key);return d[m]&&vkReq(SET.words).includes(m)?'<span class="vkok" title="geschafft">✓ geschafft</span>':''};
function vkCardMark(n){if(!n.words)return'';const ws=wordsOf(n),req=vkReq(ws),d=vkDoneOf(n.id),k=req.filter(m=>d[m]).length;
  if(!req.length||!k)return'';return k>=req.length?'<span class="vkcm ganz">✓ geschafft</span>':`<span class="vkcm">${k}/${req.length} Übungen</span>`}
