# Tagesfolie im Stil der Eulenkiste / Klassenkiste
# Diese Datei gibt es zweimal, gleich: im Knobelnest (werkstatt/einbau/tagesfolie/eulenstil.py)
# und in der Eulenkiste (werkstatt/eulenstil_tagesfolie.py). Bei Änderungen beide anpassen.
#
# Nur die Bedienung bekommt den neuen Stil (obere Leiste, Leiste unten, Menüs, Fenster, Meldungen,
# Rahmen der Bausteine). Was die Lehrperson auf die Folie schreibt (Schrift, Farben), bleibt wie es ist.
#   - Schrift Patrick Hand in einer Stärke, etwas grösser
#   - weisse Knöpfe mit weichem blauem Schatten statt grauer Linien
#   - Gold als Akzent: aktueller Bildschirm, Auswahl, ✦ als Trenner, ✦ ✧ ✦ in den Fenstertiteln
#   - Knöpfe in Fenstern wie in der Klassenkiste (dunkler Rand, hellblau = wichtig)
#   - Bausteine mit blauem Schatten wie die Karten der Eulenkiste
#   - im Ruhemodus (Vollbild, Maus still) verschwindet auch der Mauszeiger

CSS = r'''
/* ===== Stil der Eulenkiste / Klassenkiste (eulenstil.py) ===== */
:root{--gold:#d6ad45;--gold-dark:#b58a24;--sun-soft:#fbf3dc;--sky-soft:#dcf0fd;--sky-deep:#3f78a8;--eline:#dbe7f1;
  --eui:"Patrick Hand","Segoe Print","Comic Sans MS",cursive;
  --eschatten:0 4px 14px rgba(63,120,168,.2);--eschatten-hoch:0 7px 20px rgba(63,120,168,.3)}
.top,.dock,.sheet,.dd,.menu,.chrome,.toast,.kn-tip{font-family:var(--eui)}
.top button,.dock button,.sheet button,.dd button,.menu button,.chrome button,.toast,.status{font-weight:400}
.app.idle,.app.idle *{cursor:none!important}

/* Obere Leiste */
.top{padding-block:12px 4px}
.pill,.tabs .navb{border:0;background:#fff;box-shadow:var(--eschatten);font-size:18px;padding:5px 16px;min-height:38px;transition:box-shadow .15s,transform .15s}
.tabs .navb{width:38px;height:38px;padding:0;font-size:18px}
.pill:hover,.tabs .navb:hover{box-shadow:var(--eschatten-hoch);transform:translateY(-1px)}
.pill:disabled:hover{box-shadow:var(--eschatten);transform:none}
.scrbtn{background:#fff;color:#1f2421;border:0;box-shadow:0 0 0 2px var(--gold),var(--eschatten);font-size:21px;padding:4px 18px;min-height:38px;transition:box-shadow .15s}
.scrbtn::before{content:"✦";color:var(--gold);font-size:.8em}
.scrbtn b{color:var(--gold-dark);font-weight:400;font-size:.8em}
.scrbtn small{background:var(--sky-soft);color:var(--sky-deep);font-size:14px;font-weight:400}
.scrbtn:hover{box-shadow:0 0 0 2px var(--gold),var(--eschatten-hoch)}
.status{background:none;font-size:16px;color:#6c766f}

/* Leiste unten */
.dock{background:rgba(255,255,255,.97);border:0;border-radius:24px;padding:6px 8px;box-shadow:0 10px 28px rgba(63,120,168,.2),0 2px 6px rgba(63,120,168,.1),inset 0 -2px 0 rgba(214,173,69,.45)}
.dock button{font-size:15px;line-height:1.1;border-radius:16px;padding:7px 6px 5px;transition:background .15s,transform .15s}
.dock button:hover{background:var(--sky-soft);transform:translateY(-2px)}
.dock button:active{transform:translateY(0)}
.dock .sep{width:16px;background:none;margin:0;display:flex;align-items:center;justify-content:center}
.dock .sep::before{content:"✦";color:var(--gold);font-size:13px}
@media (max-width:640px){.dock button{font-size:13px}}

/* Bausteine */
.w .card{border-radius:24px;box-shadow:0 8px 24px rgba(63,120,168,.13),0 2px 6px rgba(63,120,168,.08)}
.cal-sheet{box-shadow:0 8px 24px rgba(63,120,168,.13),0 2px 6px rgba(63,120,168,.08)}
.w.sel .card{outline:2px dashed var(--gold);outline-offset:5px}
.w .rse::after,.w .rsb::after{background:var(--gold)}
.w .rs::after{border-color:var(--gold)}
.w .chrome{border:0;box-shadow:var(--eschatten);padding:3px 4px}
.chrome button{font-size:15px;color:#4d5751}
.chrome .grip{font-weight:400}
.chrome button:hover{background:var(--sky-soft);color:#1f2421}
.lfoot,.addrow{font-family:var(--eui)}
.lfoot{border-top:1.5px dashed rgba(214,173,69,.5)}
.lfoot input,.addrow input[type=text]{font-size:16px;border:1.5px solid var(--eline);background:#fff}
.lfoot select{font-size:15px;font-weight:400;border:1.5px solid var(--eline)}

/* Menüs */
.dd,.menu{border:0;border-radius:20px;box-shadow:0 16px 40px rgba(63,120,168,.26),0 2px 8px rgba(63,120,168,.12)}
.ddhead{font-size:15px;font-weight:400;color:var(--sky-deep);letter-spacing:.08em}
.ddhead em{font-weight:400;background:var(--sky-soft)}
.ddrow{font-size:18px;font-weight:400;border-radius:12px}
.ddrow:hover,.menu button:hover,.ddic:hover,.ddfold:hover{background:var(--sky-soft)}
.ddrow.on{background:var(--sun-soft);color:#1f2421;font-weight:400;box-shadow:inset 0 0 0 1.5px var(--gold)}
.ddrow.on::before{content:"✦ ";color:var(--gold)}
.ddempty{font-size:15px}
.ddfoot{border-top:1.5px dashed rgba(214,173,69,.55)}
.menu button{font-size:17px}

/* Fenster */
.sheet-bg{background:rgba(31,52,70,.28)}
.sheet{border-radius:28px;box-shadow:0 24px 60px rgba(63,120,168,.32),0 0 0 1.5px #e1edf7}
.sheet header{padding:20px 22px 8px}
.sheet h2{font-size:34px}
.sheet h2::after{content:"✦ ✧ ✦";font-size:15px;color:var(--gold);letter-spacing:.2em;margin-left:14px;vertical-align:middle}
.sheet .body{padding:4px 22px 22px;font-size:17px}
.sheet p.hint{font-size:16px}
.sheet .body h3{font-weight:400;font-size:21px!important}
.sbtn{border:2px solid #1f2421;border-radius:12px;padding:4px 13px;font-size:16px;font-weight:400;box-shadow:0 3px 10px rgba(63,120,168,.14);transition:transform .15s,box-shadow .15s,background .15s}
.sbtn:hover{border-color:#1f2421;background:var(--sky-soft);transform:translateY(-1px);box-shadow:0 6px 14px rgba(63,120,168,.22)}
.sbtn.rose{background:var(--sky-soft);border-color:#1f2421;color:#1f2421}
.sbtn.rose:hover{background:#c9e7fb}
.chip{border:1.5px solid var(--eline);background:#fff;font-size:16px}
.chip:hover{border-color:var(--sky-deep);background:var(--sky-soft)}
.chip.added{background:var(--sun-soft);color:#1f2421;border-color:var(--gold)}
.sheet textarea,.sheet input[type=text],.sheet input[type=time],.sheet input[type=number],.sheet select{border:1.5px solid var(--eline);border-radius:12px}
.fonts button{border-width:1.5px;border-color:var(--eline);background:#fff}
.fonts button.on{border-color:var(--gold);background:var(--sun-soft);box-shadow:0 0 0 1.5px var(--gold)}
.fonts .fn{font-family:var(--eui);font-size:15px;font-weight:400}
.bgtiles button.on{border-color:var(--gold)}
.bgtiles button,.bgtiles .lab{font-family:var(--eui);font-weight:400}
.bgtiles .lab{font-size:16px}
.tiles button.on{border-color:var(--gold);background:var(--sun-soft)}
.tiles button.on::after{color:var(--gold-dark);font-family:var(--eui);font-weight:400}
.tiles .del{font-family:var(--eui)}
.sheet textarea:focus,.sheet input:focus,.sheet select:focus{outline:2px solid var(--sky-deep);outline-offset:1px}

/* Musik-Knopf */
.music-chip{font-family:var(--eui);border:0;box-shadow:var(--eschatten)}
.music-chip button{background:var(--sky-deep)}
:focus-visible{outline-color:var(--sky-deep)}

/* Meldung */
.toast{background:#fff;color:#1f2421;font-size:18px;padding:8px 20px;box-shadow:0 0 0 2px var(--gold),0 10px 26px rgba(63,120,168,.28)}
.toast::before{content:"✦ ";color:var(--gold)}
'''

ANKER = '@media (prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important}}\n</style>'


def eulenstil(rep):
    """rep(alt, neu) = Ersetzen mit Prüfung, wie im jeweiligen Bau-Skript."""
    rep(ANKER, CSS.lstrip('\n') + ANKER)
