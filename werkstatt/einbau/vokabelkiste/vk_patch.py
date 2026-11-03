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

open(dst, 'w', encoding='utf-8').write(s)
print('ok', len(s))
