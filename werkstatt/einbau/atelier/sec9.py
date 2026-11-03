# 9) Platz für 12 Kinder pro Liste, grösserer (in die Breite gezogener) Weg, Vollbild ohne Leiste
rep('''  --planW:min(44vw, calc((100dvh - 236px) * .7071 / 1.06));''', '''  --planW:min(44vw, calc((100dvh - 236px) * .7071 / 1.06));
  --ptH:clamp(30px,3.4vh,42px); --parkH:clamp(64px,8.5vh,84px);''')
CSS = r'''
/* ===== Knobelnest: 12 Kinder pro Liste, grosser Weg ===== */
@media (min-width:901px){
  .stage{grid-template-columns:minmax(290px,1fr) minmax(0,1.7fr) minmax(290px,1fr)}
  .facts:not([style]){grid-template-columns:minmax(0,1.25fr) minmax(0,1.25fr) minmax(0,.8fr)}
  .facts i{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .lhead{font-size:clamp(20px,1.6vw,26px);padding:8px 14px 2px}
  .lbody{container-type:size;padding:2px 8px 8px;gap:0;overflow:auto}
  .kid{--r:max(46px,calc((100cqh - 10px) / 12));flex:none;height:var(--r);grid-template-columns:calc(var(--r) * 1.3) minmax(0,1fr);gap:0 10px;padding:calc(var(--r) * .05) 8px;overflow:hidden}
  .kside{gap:0}
  .kinfo{gap:calc(var(--r) * .04)}
  .kname{font-size:clamp(15px,calc(var(--r) * .36),27px);flex-wrap:nowrap;align-items:center}
  .kname .n{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .kname .st{flex:none;font-size:clamp(8.5px,calc(var(--r) * .15),11px);padding:1px 7px 0}
  .facts i{font-size:clamp(8px,calc(var(--r) * .14),10px);line-height:1.15}
  .facts b{font-size:clamp(10.5px,calc(var(--r) * .21),13.5px);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;line-height:1.2}
  .planwrap{container-type:size;height:100%;gap:6px}
  .ptitle{font-size:var(--ptH);line-height:1;height:var(--ptH);flex:none}
  .plan{--H:calc((100cqh - var(--ptH) - var(--parkH) - 12px) / 1.1);height:var(--H);width:min(100cqw,calc(var(--H) * 1.15));aspect-ratio:auto;margin:calc(var(--H) * .035) 0 calc(var(--H) * .05)}
  .park{flex:none;height:var(--parkH);min-height:0}
  .park{overflow:hidden;align-content:center;gap:2px 6px;padding:4px 10px}
  .park .bike{width:var(--pb,calc(var(--parkH) * 1.05));--bw:var(--pb,calc(var(--parkH) * 1.05))}
  .park.tight .lbl{font-size:15px}
  .plan .bike{width:min(19cqw,calc(var(--H) * .14))}
}
/* Vollbild: Leiste oben verschwindet, nur ein dezenter Knopf zum Beenden */
.fsx{position:fixed;top:10px;right:12px;z-index:40;display:none;opacity:0;transition:opacity .2s}
:root:fullscreen .top{display:none}
:root:fullscreen .stage{padding-top:14px}
:root:fullscreen .fsx{display:inline-flex}
:root:fullscreen .fsx:hover,:root:fullscreen .fsx:focus-visible{opacity:1}
'''
rep('''@media (max-width:900px){''', CSS + '''@media (max-width:900px){''')
# Stations-Etikett neben den Namen statt unter das Velo (spart Höhe)
rep('''      const pill=document.createElement('span');pill.className='st '+(st||'');pill.textContent=st||'Parkplatz';side.appendChild(pill);''',
    '''      const pill=document.createElement('span');pill.className='st '+(st||'');pill.textContent=st||'Parkplatz';''')
rep('''      info.querySelector('.n').textContent=k.name;''', '''      info.querySelector('.n').textContent=k.name;info.querySelector('.kname').appendChild(pill);''')
# Vollbild-Knopf
rep('''    <button class="pill" id="btnPaste" type="button">Liste einfügen</button>''',
    '''    <button class="pill" id="btnPaste" type="button">Liste einfügen</button>
    <button class="pill" id="btnFs" type="button">⛶ Vollbild</button>''')
rep('''<div id="modal"></div>''', '''<button class="pill fsx" id="fsx" type="button">✕ Vollbild beenden</button>
<div id="modal"></div>''')
rep('''$('#btnPaste').onclick=openPaste;''', '''$('#btnPaste').onclick=openPaste;
$('#btnFs').onclick=()=>{try{document.documentElement.requestFullscreen().catch(()=>setStatus('Vollbild geht hier nicht.'))}catch(e){}};
$('#fsx').onclick=()=>{try{document.exitFullscreen().catch(()=>{})}catch(e){}};
document.addEventListener('fullscreenchange',()=>setTimeout(fitSigns,60));
window.addEventListener('resize',()=>{clearTimeout(window.__fs);window.__fs=setTimeout(fitSigns,80)});''')

# Parkplatz: Velos so gross, dass alle Platz haben
rep('''function flashBike(id){''', r'''function fitPark(){
  if(innerWidth<=900){park.style.removeProperty('--pb');return}
  const bs=[...park.querySelectorAll('.bike')], n=bs.length; if(!n){park.style.removeProperty('--pb');park.classList.remove('tight');return}
  const W=park.clientWidth-20, H=park.clientHeight-8, lbl=park.querySelector('.lbl');
  let best=30;
  for(let w=Math.round(H*1.6);w>=30;w-=2){
    const bh=w*396/640, lw=(lbl?lbl.offsetWidth+8:0), cols=Math.max(1,Math.floor((W+6)/(w+6))), rows=Math.ceil((n+(lbl?Math.ceil(lw/(w+6)):0))/cols);
    if(rows*(bh+2)<=H){best=w;break}
  }
  park.style.setProperty('--pb',best+'px'); park.classList.toggle('tight',best<60);
}
function flashBike(id){''')
rep('''    park.appendChild(b);wireDrag(b,k);if(KID&&k.id!==KN.me)b.classList.add('locked');
  });''', '''    park.appendChild(b);wireDrag(b,k);if(KID&&k.id!==KN.me)b.classList.add('locked');
  });
  fitPark();''')
rep("window.addEventListener('resize',()=>{clearTimeout(window.__fs);window.__fs=setTimeout(fitSigns,80)});",
    "window.addEventListener('resize',()=>{clearTimeout(window.__fs);window.__fs=setTimeout(()=>{fitSigns();fitPark()},80)});")
# Kürzere Spaltentitel, damit sie in den schmalen Zeilen ganz lesbar sind
rep('''<div><i>Umsetzungsart</i>${f(k.umsetzung)}</div>${KID?'':`<div class="f-stufe"><i>Lernerstufe</i>${f(k.stufe)}</div>`}''',
    '''<div><i>Umsetzung</i>${f(k.umsetzung)}</div>${KID?'':`<div class="f-stufe"><i>Stufe</i>${f(k.stufe)}</div>`}''')
