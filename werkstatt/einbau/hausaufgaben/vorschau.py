# Vorschau des Hausaufgabenhefts als eine Seite (Artefakt zum gemeinsamen Überarbeiten), ohne Klassenkiste und ohne Speichern.
# Erfundene Kinder und Beispiel-Einträge; oben umschalten zwischen Lehrperson und Kind.
# Aufruf: python3 werkstatt/einbau/hausaufgaben/vorschau.py <ziel.html>
import json, os, sys, datetime as dt
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
heft = open(os.path.join(ROOT, 'hausaufgaben.html'), encoding='utf-8').read()
schrift = open(os.path.join(ROOT, 'rechenoperationen', 'stil.css'), encoding='utf-8').read()
import re
FONT = re.search(r'@font-face\{[^}]*\}', schrift).group(0)
# Schriften im Heft: lokale Datei der Klassenkiste geht im Artefakt nicht, darum eingebettet
heft = heft.replace('<head>', '<head><style>' + FONT + '</style>', 1)
import base64
EULE = 'data:image/webp;base64,' + base64.b64encode(open(os.path.join(ROOT, 'bilder', 'eule.webp'), 'rb').read()).decode()
heft = heft.replace('bilder/eule.webp', EULE)
KIDS = ['Lena', 'David', 'Mia', 'Noah', 'Emma', 'Luca', 'Sofia', 'Ben']
heute = dt.date.today(); mo = heute - dt.timedelta(days=heute.weekday())
d = lambda n: (mo + dt.timedelta(days=n)).isoformat()
E = [
 dict(id='e1', date=d(0), type='aufgabe', fach='Mathematik', title='Arbeitsheft S. 24, Nr. 1–5', details='Mit Bleistift lösen', order=0),
 dict(id='e2', date=d(0), type='aufgabe', fach='Deutsch', title='Lesetext «Der Fuchs» zweimal lesen', order=1),
 dict(id='e3', date=d(1), type='aufgabe', fach='Englisch', title='Wörter Unit 2 in der Vokabelkiste üben', order=0),
 dict(id='e4', date=d(2), type='lernkontrolle', fach='Mathematik', title='Lernkontrolle Einmaleins', order=0),
 dict(id='e5', date=d(2), type='notiz', title='Turnsachen mitnehmen', order=1),
 dict(id='e6', date=d(3), type='aufgabe', fach='NMG', title='Blatt «Wasserkreislauf» fertig malen', order=0),
 dict(id='e7', date=d(4), type='aufgabe', fach='Deutsch', title='Diktat üben: Wörter mit ie', details='Eltern diktieren lassen', order=0),
]
for e in E: e.update(dict(status={}, notes={}, first={}, neuAuf={}, selbst={}, **({'for': []})))
DATA = dict(klasse='Klasse 5b', sus=[], settings=dict(lines=8, font='Patrick Hand', cover='eule'), entries=E)
seite = '''<title>Hausaufgabenheft Vorschau</title><meta name="claude:viewport-fit-sides" content="cover">
<style>''' + FONT + '''
:root{color-scheme:light;--ink:#1f2421;--gold:#d6ad45;--sky:#dcf0fd;--bg:#f4f9fd}
html,body{height:100%}body{margin:0;background:var(--bg);color:var(--ink);font-family:"Patrick Hand","Segoe Print",cursive;display:flex;flex-direction:column}
.leiste{display:flex;align-items:center;gap:10px;flex-wrap:wrap;padding-block:8px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));background:#fff;border-bottom:1.5px solid #e1edf7;font-size:17px}
.leiste b{font-weight:400;font-size:19px}.leiste b::after{content:" ✦";color:var(--gold);font-size:.6em;vertical-align:super}
.leiste button{font:inherit;font-size:17px;border:2px solid #c5d8e8;background:#fff;color:var(--ink);border-radius:999px;padding:3px 16px;cursor:pointer}
.leiste button[aria-pressed="true"]{background:var(--sky);border-color:var(--ink)}
.leiste span{color:#5f6963;font-size:15px}
iframe{flex:1;width:100%;border:0;min-height:0}
</style>
<div class="leiste"><b>Hausaufgabenheft</b><button id="lp" aria-pressed="true">Lehrperson</button><button id="kind" aria-pressed="false">Kind (Lena)</button><span>Vorschau mit erfundenen Namen, nichts wird gespeichert.</span></div>
<iframe id="f" title="Hausaufgabenheft"></iframe>
<script>
var HEFT=''' + json.dumps(heft, ensure_ascii=False).replace('</', '<\\/') + ''';
var START=''' + json.dumps(DATA, ensure_ascii=False) + ''', KIDS=''' + json.dumps(KIDS) + ''';
var daten=JSON.parse(JSON.stringify(START)), roster=KIDS.map(function(n,i){return {id:'k'+i,name:n};});
function doc(){return {get:async function(){return {exists:true,data:function(){return JSON.parse(JSON.stringify(daten));}};},
  set:async function(v){daten=JSON.parse(JSON.stringify(v));}, onSnapshot:function(){return function(){};}};}
function ansicht(kind){
  document.getElementById('lp').setAttribute('aria-pressed',!kind); document.getElementById('kind').setAttribute('aria-pressed',kind);
  window.knHeft = kind ? {mode:'kid',key:'v-kind',kidId:'k0',className:'',roster:[],own:function(e,del){daten.entries=daten.entries.filter(function(x){return x.id!==e.id;}); if(!del){e.by='k0'; e.type='aufgabe'; daten.entries.push(e);} },
      tick:function(id,on){var e=daten.entries.filter(function(x){return x.id===id;})[0]; if(e){e.selbst=e.selbst||{}; if(on)e.selbst.k0=true; else delete e.selbst.k0;}}, back:function(){},
      claude:{use:async function(n){return n==='db'?{doc:doc}:null;}}}
    : {mode:'teacher',key:'v-lp',className:'Klasse 5b',embed:false,roster:roster,back:function(){},
      claude:{use:async function(n){return n==='db'?{doc:doc,collection:function(){return {doc:doc};}}:null;}}};
  document.getElementById('f').srcdoc=HEFT;
}
document.getElementById('lp').onclick=function(){ansicht(false);}; document.getElementById('kind').onclick=function(){ansicht(true);};
ansicht(false);
</script>'''
open(sys.argv[1], 'w', encoding='utf-8').write(seite)
print('ok', sys.argv[1])
