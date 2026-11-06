# 17) Klassenkiste-Stil (wie die Lehrpersonen-Seite im Stil der Eulenkiste, body.lp in style.css):
#     Schrift Patrick Hand (eingebettet), helles Blau, weisse Karten mit weichem blauem Schatten, Knöpfe mit dunklem Rand,
#     Gold-Akzente und ✦ ✧ ✦, Eulen-Marke. Bewusst nur hell (wie das Portal und für den Beamer).
#     Schrift und Eule werden als data:-Adressen eingebettet, damit die Seite auch als claude.ai-Artefakt ohne fremde Dateien läuft.
#     «Drucken» fällt weg: im Artefakt kann die Seite keinen Druckdialog öffnen.
#     Wird als letzter Abschnitt von standalone.py ausgeführt.
import base64
_root = os.path.abspath(os.path.join(here, '..', '..', '..'))
_font = base64.b64encode(open(os.path.join(_root, 'schriften', 'patrick-hand.woff2'), 'rb').read()).decode()
_eule = base64.b64encode(open(os.path.join(_root, 'bilder', 'eule.webp'), 'rb').read()).decode()

# Keine Schriften von Google mehr: Patrick Hand ist eingebettet
rep('<link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Patrick+Hand&family=Nunito:wght@400;600;700;800&family=Fredoka:wght@500;600;700&display=swap">\n', '')

# Marke oben links: Eule im Goldring, Name in Handschrift
rep('    <h1>Klassen-Pinnwand</h1>', '''    <h1 class="marke"><span class="marke-bild"><img src="data:image/webp;base64,''' + _eule + '''" alt=""></span><span class="marke-text"><b>Klassen<em>-</em>Pinnwand<i>✦</i></b><small>Ideen sammeln · ordnen · abstimmen</small></span></h1>''')

# Standard-Hintergrund heisst jetzt wie das Portal
rep('const BGS = [["", "Aquarell"],', 'const BGS = [["", "Klassenkiste"],')
# Kein Drucken im Artefakt
rep('      <div class="row"><button class="btn ghost small" type="button" data-act="print">🖨️ Drucken</button></div>\n', '')

rep('</style>\n\n<div class="wrap">', '''/* ===== Klassenkiste-Stil ===== */
@font-face{font-family:"Patrick Hand";src:url(data:font/woff2;base64,''' + _font + ''') format("woff2");font-weight:400;font-display:swap}
:root{
  --paper:#f4f9fd; --card:#ffffff; --ink:#1f2421; --muted:#5f6963; --line:#dbe7f1; --line2:#c5d8e8; --edge:#e1edf7;
  --gold:#d6ad45; --gold-d:#c4952f; --sky-soft:#dcf0fd; --sky-mid:#c9e7fb; --sky-deep:#3f78a8; --sun-soft:#fbf3dc;
  --sky:#8fc3ea; --rose:#3f78a8; --rose-soft:#dcf0fd; --leaf:#7ea56a; --leaf-deep:#4f7d3c; --leaf-soft:#e9f1e3;
  --ui:"Patrick Hand","Segoe Print","Comic Sans MS",cursive; --hand:var(--ui); --bubble:var(--ui);
  --shadow:0 10px 26px rgba(63,120,168,.18),0 2px 6px rgba(63,120,168,.10);
  --shadow-hi:0 16px 34px rgba(63,120,168,.26),0 3px 8px rgba(63,120,168,.14);
  --note-shadow:0 1px 0 rgba(0,0,0,.04),0 8px 18px -6px rgba(63,120,168,.32);
}
html{font-size:18px;background:var(--paper)}
body{font-size:1.05rem;line-height:1.4;background:radial-gradient(ellipse 70% 32% at 50% -6%,#dcf0fd 0,transparent 70%),radial-gradient(ellipse 40% 30% at 100% 100%,rgba(214,173,69,.10),transparent 70%),var(--paper);background-attachment:fixed}
body,body *{font-weight:400!important}
:focus-visible{outline:3px solid #9fd0f3;outline-offset:2px}
h2,h3{font-size:1.75rem;line-height:1.1}
/* Kopf und Marke */
header.top{padding-block:4px 10px;border-bottom:1.5px dashed rgba(214,173,69,.45);margin-bottom:4px}
header.top h1.marke{all:unset;flex:1 1 auto;display:flex;align-items:center;gap:12px;min-width:0}
.marke-bild{flex:none;width:58px;height:58px;border-radius:50%;background:#fff;padding:3px;box-shadow:0 0 0 2px var(--gold),0 6px 18px rgba(63,120,168,.25);transform:rotate(-6deg);transition:transform .3s}
.marke-bild img{width:100%;height:100%;display:block;border-radius:50%}
.marke:hover .marke-bild{transform:rotate(4deg) scale(1.05)}
.marke-text{display:flex;flex-direction:column;min-width:0}
.marke-text b{font-family:var(--ui);font-size:2.05rem;line-height:.95;color:var(--ink)}
.marke-text em{font-style:normal;color:var(--gold-d)}
.marke-text i{font-style:normal;color:var(--gold);font-size:.55em;vertical-align:super;margin-left:3px}
.marke-text small{align-self:flex-start;margin-top:3px;font-size:.9rem;color:var(--muted);border-top:1.5px dashed var(--gold);padding-top:1px}
.status{background:#fff;border:1.5px solid var(--edge);font-size:.85rem;color:var(--muted)}
#roleSeg{background:#fff;border:1.5px solid var(--edge);border-radius:999px;padding:4px;box-shadow:var(--shadow);gap:2px}
#roleSeg button{border:0;box-shadow:none;background:transparent}
#roleSeg button[aria-pressed="true"]{background:var(--sky-soft);border:0;box-shadow:none}
.pres-title{all:unset;flex:1 1 auto;font-family:var(--ui);font-size:clamp(30px,4.4vw,48px);line-height:1;color:var(--ink)}
.pres-title::after{content:" ✦";color:var(--gold);font-size:.45em;vertical-align:super}
/* Karten */
.panel,.empty,.baro,.bcard{border:1.5px solid var(--edge);border-radius:28px;box-shadow:var(--shadow);background:linear-gradient(180deg,#fff 0%,#fff 70%,#f7fbfe 100%)}
.panel>h2,.panel>div>h2,.panel summary h2,.baro>div>h2{display:inline-flex;align-items:center;gap:10px;flex-wrap:wrap}
.panel>h2::after,.panel>div>h2::after,.panel summary h2::after,.baro>div>h2::after{content:"✦ ✧ ✦";font-size:12px;letter-spacing:.3em;color:var(--gold)}
.empty{border:2px dashed #b9d6ec;box-shadow:none;background:rgba(255,255,255,.7)}
.empty h3{color:var(--muted)}
.sub{color:var(--muted);font-size:.95rem}
.tool-l{color:var(--sky-deep);font-size:.78rem;letter-spacing:.1em}
.bhead h2::after{content:" ✦";color:var(--gold);font-size:.5em;vertical-align:super}
.bcard:hover,button.bcard:hover{transform:translateY(-3px);box-shadow:var(--shadow-hi)}
.bcard{transition:transform .15s,box-shadow .15s}
.bcard .foot{border-top:1.5px dashed rgba(214,173,69,.55)}
.btpl{background:var(--sun-soft);color:#6b5418}
.vis{font-size:.8rem}
.vis.on{background:var(--leaf-soft);color:#3f6b2e}
.badge{background:var(--sun-soft);color:#6b5418;border:1.5px solid var(--gold);font-family:var(--ui);font-size:.85rem}
/* Knöpfe */
.btn{border:2px solid var(--ink);border-radius:14px;background:var(--sky-soft);color:var(--ink);font-size:1.05rem;padding:6px 18px;box-shadow:var(--shadow);transition:transform .15s,box-shadow .15s,background .15s}
.btn:hover{background:var(--sky-mid);border-color:var(--ink);transform:translateY(-2px);box-shadow:var(--shadow-hi)}
.btn:active{transform:translateY(1px);box-shadow:var(--shadow)}
.btn.ghost{background:#fff;border-color:var(--ink);color:var(--ink)}
.btn.ghost:hover{background:var(--sky-soft);border-color:var(--ink)}
.btn.small{border-radius:11px;padding:3px 13px;font-size:.95rem;box-shadow:0 4px 12px rgba(63,120,168,.14)}
.btn:disabled{transform:none}
.linkbtn,.edit-btn{color:var(--sky-deep);font-family:var(--ui);font-size:.95rem}
.del{font-size:.92rem;color:#9a3b33}
.del.arm{background:#b5524a}
/* Umschalter, Reiter, Felder */
.seg button,.tabs button{border:1.5px solid transparent;background:transparent;border-radius:999px;color:var(--ink);font-size:1.05rem;padding:5px 16px;transition:background .15s}
.tabs button{font-size:1.15rem;padding:6px 18px;min-height:42px}
.seg button:hover,.tabs button:hover{background:var(--sky-soft);border-color:transparent}
.seg button[aria-pressed="true"],.tabs button[aria-selected="true"]{background:#fff;border-color:var(--ink);color:var(--ink);box-shadow:var(--shadow)}
.tabs{gap:6px}
.field{border:1.5px solid var(--line2);border-radius:14px;background:#fff;font-size:1.05rem;padding:8px 14px}
.field:focus{border-color:var(--sky-deep);outline:3px solid #9fd0f3;box-shadow:none}
textarea.field{background:#fff;font-size:1.3rem}
select,button,input,textarea{font-family:inherit}
select.field{min-height:42px;font-family:var(--ui)}
.tg{border:1.5px solid var(--line2);border-radius:14px;background:#f7fbfe;font-size:.98rem;padding:4px 12px}
.tg input{accent-color:#7ea56a}
.tg:has(input:checked){background:var(--leaf-soft);border-color:#7ea56a;color:#3f6b2e}
.note .tg{font-size:.88rem}
.qitem{background:var(--sun-soft);border:1.5px dashed var(--gold);border-radius:20px}
/* Zettel */
.note::before{background:rgba(214,173,69,.30);border-left:1px dashed rgba(196,149,47,.35);border-right:1px dashed rgba(196,149,47,.35)}
.tool{border-top:1.5px dashed rgba(214,173,69,.45)}
.scale button,.agree button{font-size:.95rem}
.scale button[aria-pressed="true"]{background:var(--sky-deep);color:#fff}
.sbar-mark span{background:var(--sky-deep)}
.sbar-fill,.pr-r .pt i,.pc-track i{background:linear-gradient(90deg,#9fd0f3,var(--sky-deep))}
.cm b{font-family:var(--ui);font-size:.9rem}
.lpc .lpc-t{border-left-color:var(--gold)}
/* Vorlagen */
.tpl{border:1.5px solid var(--edge);border-radius:22px;box-shadow:0 4px 12px rgba(63,120,168,.10);transition:transform .15s,box-shadow .15s}
.tpl:hover{border-color:var(--edge);transform:translateY(-3px);box-shadow:var(--shadow-hi)}
.tpl[aria-pressed="true"]{border:2px solid var(--ink);background:#fff;box-shadow:0 0 0 3px #fff,0 0 0 5px var(--gold),var(--shadow)}
.tpl-top b{font-size:1.1rem}
.tpl-d{font-size:.9rem}
.bprompt{border:1.5px dashed var(--gold);border-left:1.5px dashed var(--gold);background:#fff;font-size:1.6rem}
/* Seitenleiste, Spalten, Mindmap, Leinwand */
.side-top{color:var(--sky-deep);font-size:.85rem;letter-spacing:.1em}
.lpside .panel{border-radius:22px}
.col{border-radius:24px;border:1.5px solid var(--edge);border-top:10px solid var(--mc,#c5d8e8);background:rgba(255,255,255,.75)}
.colhead{font-size:1.5rem}
.mm-center{border-color:var(--ink);color:var(--ink);box-shadow:0 0 0 4px #fff,0 0 0 6px var(--gold),var(--shadow)}
.mm-node{font-size:1.2rem}
.cv{border:1.5px solid var(--edge);border-radius:28px;box-shadow:var(--shadow);background:#fff}
.cv-lt{font-family:var(--ui)}
.tl-dot{background:var(--sky-deep);box-shadow:0 0 0 4px #fff,0 0 0 6px var(--gold)}
.tl-it::before{background:var(--sky-deep)}
.one-nav{border:2px solid var(--ink);box-shadow:var(--shadow)}
.pc-title{font-family:var(--ui);border-bottom:3px dashed var(--gold)}
.pc-chip{border:1.5px solid var(--line2)}
.pc-chip.cur{background:var(--sky-soft);border-color:var(--ink);color:var(--ink)}
.cathead{font-family:var(--ui);border-bottom:2px dashed var(--gold)}
.catnote{border-left:6px solid var(--gold);border-radius:18px}
.toast{background:var(--ink);border-radius:14px;font-size:1rem;box-shadow:var(--shadow-hi)}
@media (max-width:640px){.marke-bild{width:46px;height:46px}.marke-text b{font-size:1.65rem}.marke-text small{display:none}}
@media (prefers-reduced-motion:reduce){*{transition:none!important}}
</style>

<div class="wrap">''')

# Hinweis auf die Klassenkiste: dort lassen sich Vorlagen bearbeiten, löschen und eigene erstellen
rep('esc(t.icon) + " Erstellen"}</button></div></section>`;', '''esc(t.icon) + " Erstellen"}</button></div>
    <div class="kk-hint"><span class="kk-stern" aria-hidden="true">✦</span><p><b>Eigene Vorlagen?</b> In der Klassenkiste können Sie Vorlagen bearbeiten, löschen und eigene erstellen, dazu viele weitere Werkzeuge für Ihre Klasse.</p><a class="btn kk-btn" href="https://primarschuleulchen.github.io/knobelnest/" target="_blank" rel="noopener">✦ Hol dir jetzt den Zugang</a></div></section>`;''')
rep('/* ===== Klassenkiste-Stil ===== */', '''/* ===== Klassenkiste-Stil ===== */
.kk-hint{display:flex;flex-wrap:wrap;align-items:center;gap:10px 16px;background:var(--sun-soft, #fbf3dc);border:1.5px dashed var(--gold, #d6ad45);border-radius:20px;padding:12px 18px;color:#4a3d1a}
.kk-hint p{flex:1 1 300px;margin:0;font-size:1.05rem;line-height:1.35;min-width:0}
.kk-hint b{color:#6b5418}
.kk-stern{font-size:1.6rem;color:var(--gold, #d6ad45);line-height:1}
.kk-btn{text-decoration:none;background:#fff;white-space:nowrap}
.kk-btn:hover{background:#fff6dc}''')
